"""Finance projection removes competing routes without changing the state owner."""

import copy
import json

import pytest
from jsonschema import Draft202012Validator
from mcp.shared.exceptions import MCPError

from margin.analysis.company import FUNCTIONS
from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import FINANCE_INSTRUCTIONS, FINANCE_TOOLS, ToolView
from margin.interfaces.mcp.server import MarginMCP


@pytest.fixture
async def owner():
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key="fictional-only",
            bharatstock_requests=0,
            drishti_requests=0,
            drishti_credits=0,
        )
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def call(view, name, args=None):
    args = args or {}
    Draft202012Validator(view.tools[name].input_schema).validate(args)
    response = await view.call(name, args)
    body = response.structured_content
    Draft202012Validator(view.tools[name].output_schema).validate(body)
    assert json.loads(response.content[0].text) == body
    assert not response.is_error, body
    return body


async def test_profile_is_small_and_owner_config_is_unchanged(owner):
    baseline = owner.service.ledger.snapshot()
    original = copy.deepcopy(owner.tools)
    full, finance = ToolView(owner), ToolView(owner, "finance")
    assert set(finance.tools) == FINANCE_TOOLS and len(finance.tools) == 6
    assert len(full.tools) == 39
    status = (await call(finance, "margin_status"))["data"]
    assert status["tool_profile"] == "finance" and status["advertised_tools"] == 6
    assert status["ledger"]["http_limits"] == {"bharatstock": 0, "drishti": 0}
    assert owner.service.ledger.snapshot() == baseline
    assert owner.tools == original
    assert (await call(full, "margin_status"))["data"]["tool_profile"] == "all"


@pytest.mark.parametrize("function", sorted(FUNCTIONS))
@pytest.mark.parametrize("key", [None, "explicit-caller-key"])
async def test_compact_summary_matches_binding_for_every_workflow(owner, function, key):
    finance = ToolView(owner, "finance")
    args = {"function": function, "ticker": "INFY", "execute": False}
    if key:
        args["idempotency_key"] = key
    baseline = owner.service.ledger.snapshot()
    body = await call(finance, "margin_company_finance", args)
    data = body["data"]
    summary, step = data["preview_summary"], data["next_steps"][0]
    assert (
        summary["next_tool_for_execution"]
        == step["mcp_execution"]["tool"]
        == "margin_company_finance"
    )
    assert summary["missing_fields_for_preview"] == []
    assert summary["data_fetched"] is False
    assert summary["financial_readiness_assessed"] is False
    assert summary["result_fields_after_execution"] == (
        ["report.readiness", "report.valuation_readiness"]
        if function == "finance.company_data_readiness"
        else ["report.rows"]
    )
    assert (
        summary["missing_fields_for_execution"]
        == step["required_host_fields"]
        == ([] if key else ["idempotency_key"])
    )
    assert summary["execution_input_complete"] is bool(key)
    assert summary["preview_authorizes_execution"] is False
    assert summary["provider_requests_made"] == {"bharatstock": 0, "drishti": 0}
    assert summary["planned_execution_maximum_provider_requests"] == {
        "bharatstock": 1,
        "drishti": 0,
    }
    assert not data["creates_plan_id"] and "margin_run" in step["do_not_use_tools"]
    assert "session_id" not in body and "call_id" not in body
    assert "company_execution_contract" not in data
    assert "maximum_provider_requests" not in data  # ambiguous on its own
    bound = step["bound_arguments"] | {"idempotency_key": key or "future-host-key"}
    Draft202012Validator(finance.tools["margin_company_finance"].input_schema).validate(bound)
    assert owner.service.ledger.snapshot() == baseline
    assert owner.service.company_finance_workflow.requests == {} and owner.service.plans == {}
    full = (await owner.call("margin_company_finance", args)).structured_content
    assert full["data"]["preview_summary"] == summary
    assert len(json.dumps(body)) < len(json.dumps(full)) * 0.75


@pytest.mark.parametrize("group", [None, "company", "calculations", "all"])
async def test_catalog_only_returns_callable_routes_and_exact_schemas(owner, group):
    view = ToolView(owner, "finance")
    args = {"include_schemas": True}
    if group:
        args["group"] = group
    data = (await call(view, "margin_catalog", args))["data"]
    assert set(data["groups"]) <= {"company", "calculations"}
    assert bool(data["groups"])
    for kind, rows in data["groups"].items():
        for row in rows:
            route = row["mcp_execution"]
            assert route["tool"] in view.tools
            assert route["tool"] == (
                (
                    "margin_company_data_readiness"
                    if row["function"] == "finance.company_data_readiness"
                    else "margin_company_finance"
                )
                if kind == "company"
                else (
                    "margin_calculate_dcf"
                    if row["function"] == "finance.calculate_dcf"
                    else "margin_calculate"
                )
            )
            if route["bind"]:
                assert route["bind"]["function"] == row["function"]
            if kind == "company":
                assert "planning_schema" not in row and "legacy_mcp_execution" not in row
                assert "fetch_missing" not in row["defaults"]
                assert row["defaults"]["execute"] is False
                assert "legacy_note" not in row and "legacy_defaults" not in row
                assert row["schema"] == view.tools[route["tool"]].input_schema
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


@pytest.mark.parametrize(
    "name,args",
    [
        ("margin_run", {}),
        ("margin_company_preview", {}),
        ("margin_sources", {}),
        ("margin_prepare_review", {}),
        ("finance.company_margins", {}),
        ("margin_catalog", {"group": "review"}),
        ("margin_catalog", {"group": "retrieval"}),
        ("margin_catalog", {"private-field": "private-value"}),
        ([], {}),
    ],
)
async def test_hidden_calls_do_not_forward(owner, monkeypatch, name, args):
    view = ToolView(owner, "finance")
    calls = []

    async def forbidden(*args):
        calls.append(args)

    monkeypatch.setattr(owner, "call", forbidden)
    with pytest.raises(MCPError) as err:
        await view.call(name, args)
    assert err.value.error.code == -32602 and not calls
    assert "private-value" not in err.value.error.message


async def test_hidden_name_cannot_leak_from_all_catalog(owner):
    view = ToolView(owner, "finance")
    with pytest.raises(MCPError, match="finance profile"):
        await view.call("margin_catalog", {"group": "all", "name": "evidence.register_sources"})


async def test_default_company_route_and_legacy_recovery_agree(owner):
    catalog = (await owner.call("margin_catalog", {"group": "company"})).structured_content["data"]
    for row in catalog["groups"]["company"]:
        assert row["mcp_execution"]["tool"] == (
            "margin_company_data_readiness"
            if row["function"] == "finance.company_data_readiness"
            else "margin_company_finance"
        )
        assert row["legacy_mcp_execution"]["tool"] == "margin_company_preview"
        assert owner.function_route(row["function"]) == row["mcp_execution"]
    error = await owner.call(
        "margin_company_preview",
        {"function": "finance.company_margins", "ticker": "INFY", "exchange": "NSE"},
    )
    assert error.is_error
    guidance = error.structured_content["error"]["recovery_guidance"]
    assert "execute=false" in guidance and "Do not fetch first" in guidance


async def test_local_zero_budget_blocks_and_replays_without_claiming_account_balance(owner):
    view = ToolView(owner, "finance")
    args = {
        "function": "finance.company_margins",
        "ticker": "INFY",
        "execute": True,
        "idempotency_key": "budget-test-only",
    }
    result = (await call(view, "margin_company_finance", args))["data"]
    assert result["status"] == "blocked"
    assert result["error"]["scope"] == "local_process_allowance"
    assert result["error"]["observed_account_balance"] is None
    assert result["usage"]["bharatstock_http_attempts"] == 0
    assert (await call(view, "margin_company_finance", args))["data"] == result
    preview = (
        await call(
            view,
            "margin_company_finance",
            {"function": "finance.company_margins", "ticker": "INFY"},
        )
    )["data"]
    assert preview["status"] == "preview"
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


async def test_missing_key_remains_a_configuration_hold_not_fabricated_preview():
    service = ResearchService(Settings(mode="live", bharatstock_requests=0))
    try:
        view = ToolView(MarginMCP(service), "finance")
        response = await view.call(
            "margin_company_finance", {"function": "finance.company_margins", "ticker": "INFY"}
        )
        assert (
            response.is_error and response.structured_content["error"]["code"] == "held_operation"
        )
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    finally:
        await service.close()


async def test_explicit_calculator_and_execution_projection_preserve_canonical_report():
    service = ResearchService(
        Settings(bharatstock_requests=1, drishti_requests=0, drishti_credits=0)
    )
    try:
        owner = MarginMCP(service)
        view = ToolView(owner, "finance")
        args = {
            "function": "finance.company_data_readiness",
            "ticker": "SYNTHA",
            "execute": True,
            "include_details": True,
            "idempotency_key": "fixture-only-readiness",
        }
        projected = (await call(view, "margin_company_finance", args))["data"]
        original = (await owner.call("margin_company_finance", args)).structured_content["data"]
        assert projected == original
        route = projected["report"]["valuation_readiness"]["mcp_execution"]
        assert route["tool"] == "margin_calculate_dcf"
        assert projected["report"]["readiness_scope"]["source_facts_verified"] is False
        assert service.ledger.requests == {"bharatstock": 1, "drishti": 0}
        fact = {
            "issuer": "EXAMPLE_ONLY",
            "metric": "revenue",
            "definition": "User hypothetical",
            "value": "1000",
            "unit": "INR",
            "period_type": "annual",
            "period_start": "2025-04-01",
            "period_end": "2026-03-31",
            "basis": "standalone",
        }
        result = await call(
            view,
            "margin_calculate",
            {
                "function": "finance.calculate_margins",
                "arguments": {
                    "revenue": fact,
                    "profit": fact | {"metric": "net_profit", "value": "150"},
                },
            },
        )
        assert result["data"]["values"]["margin_percent"] == "15.00"
        assert service.ledger.requests == {"bharatstock": 1, "drishti": 0}
    finally:
        await service.close()


def test_finance_instructions_are_short_and_do_not_include_review_or_legacy_flows():
    assert len(FINANCE_INSTRUCTIONS.encode()) < 3600
    assert "margin_prepare_review" not in FINANCE_INSTRUCTIONS
    assert "margin_company_preview" not in FINANCE_INSTRUCTIONS
