"""Typed aliases must preserve reviewed core math, validation and duplicate control."""

import copy
import json
from decimal import Decimal

import httpx
import pytest
from jsonschema import Draft202012Validator

from margin.analysis.service import SPECS
from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import ToolView
from margin.interfaces.mcp.server import MarginMCP
from margin.interfaces.mcp.tools import WHY


@pytest.fixture
async def owner():
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key="software-only",
            bharatstock_requests=0,
            drishti_requests=0,
            drishti_credits=0,
        )
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def call(view, name, values):
    response = await view.call(name, values)
    assert not response.is_error, response.structured_content
    body = response.structured_content
    assert json.loads(response.content[0].text) == body
    Draft202012Validator(view.tools[name].output_schema).validate(body)
    return body["data"]


@pytest.mark.parametrize("profile", ["all", "finance"])
@pytest.mark.parametrize("key", [None, "explicit-preview-key"])
async def test_typed_readiness_has_no_selector_and_binds_same_typed_tool(owner, profile, key):
    view = ToolView(owner, profile)
    values = {"ticker": "INFY", "execute": False}
    if key:
        values["idempotency_key"] = key
    before = owner.service.ledger.snapshot()
    output = await call(view, "margin_company_data_readiness", values)
    assert output["function"] == "finance.company_data_readiness"
    summary = output["preview_summary"]
    assert summary["workflow_function"] == output["function"]
    assert summary["cross_group_readiness_workflow"] is True
    assert summary["idempotency_key_is_authorization"] is False
    assert summary["preview_authorizes_execution"] is False
    assert summary["result_fields_after_execution"] == [
        "report.readiness",
        "report.valuation_readiness",
    ]
    assert summary["valuation_prerequisites"]["mcp_execution"] == {
        "tool": "margin_calculate_dcf",
        "bind": {},
        "inputs_at": "top_level",
    }
    assert not summary["valuation_prerequisites"]["assumptions_generated"]
    step = output["next_steps"][0]
    assert (
        step["mcp_execution"]["tool"]
        == summary["next_tool_for_execution"]
        == "margin_company_data_readiness"
    )
    assert "function" not in step["bound_arguments"]
    assert step["required_host_fields"] == ([] if key else ["idempotency_key"])
    complete = step["bound_arguments"] | {"idempotency_key": key or "future-host-key"}
    Draft202012Validator(view.tools["margin_company_data_readiness"].input_schema).validate(
        complete
    )
    assert owner.service.ledger.snapshot() == before
    assert not owner.service.company_finance_workflow.requests and not owner.service.plans


@pytest.mark.parametrize(
    "values",
    [
        {"ticker": "INFY", "function": "finance.company_profitability"},
        {"arguments": {"ticker": "INFY"}},
        {"ticker": "INFY", "execute": True},
        {"ticker": "INFY", "execute": "false"},
        {"ticker": "INFY", "idempotency_key": "bad"},
        {"ticker": "INFY", "forecast_fcff": [100]},
    ],
)
async def test_bad_alias_shape_and_missing_key_do_not_dispatch(owner, values):
    response = await owner.call("margin_company_data_readiness", values)
    assert response.is_error
    assert response.structured_content["error"]["code"] == "invalid_input"
    assert not owner.service.company_finance_workflow.requests
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


async def test_generic_readiness_still_binds_generic_tool_and_catalog_prefers_typed(owner):
    view = ToolView(owner)
    output = await call(
        view,
        "margin_company_finance",
        {"function": "finance.company_data_readiness", "ticker": "INFY"},
    )
    step = output["next_steps"][0]
    assert step["mcp_execution"]["tool"] == "margin_company_finance"
    assert step["bound_arguments"]["function"] == "finance.company_data_readiness"
    catalog = await call(
        view,
        "margin_catalog",
        {"group": "company", "name": "finance.company_data_readiness", "include_schemas": True},
    )
    row = catalog["groups"]["company"][0]
    assert row["mcp_execution"] == {
        "tool": "margin_company_data_readiness",
        "bind": {},
        "inputs_at": "top_level",
    }
    assert row["schema"] == owner.tools["margin_company_data_readiness"].input_schema
    assert "function" not in row["schema"]["properties"]


async def test_profitability_preview_is_explicitly_not_cross_group_readiness(owner):
    output = await call(
        ToolView(owner),
        "margin_company_finance",
        {"function": "finance.company_profitability", "ticker": "INFY"},
    )
    summary = output["preview_summary"]
    assert summary["cross_group_readiness_workflow"] is False
    assert summary["workflow_function"] == "finance.company_profitability"
    assert summary["result_fields_after_execution"] == ["report.rows"]


async def test_typed_and_generic_share_one_execution_and_conflict_guard():
    service = ResearchService(
        Settings(bharatstock_requests=1, drishti_requests=0, drishti_credits=0)
    )
    try:
        view = ToolView(MarginMCP(service))
        values = {
            "ticker": "SYNTHA",
            "execute": True,
            "include_details": True,
            "idempotency_key": "one-readiness-intent",
        }
        typed = await call(view, "margin_company_data_readiness", values)
        generic = await call(
            view, "margin_company_finance", values | {"function": "finance.company_data_readiness"}
        )
        assert generic == typed
        assert typed["report"]["readiness_scope"]["source_facts_verified"] is False
        assert (
            typed["report"]["valuation_readiness"]["mcp_execution"]["tool"]
            == "margin_calculate_dcf"
        )
        conflict = await view.call("margin_company_data_readiness", values | {"ticker": "SYNTHB"})
        assert (
            conflict.is_error
            and conflict.structured_content["error"]["code"] == "idempotency_conflict"
        )
        assert service.ledger.requests == {"bharatstock": 1, "drishti": 0}
    finally:
        await service.close()


async def test_no_data_readiness_stays_unassessed_without_extra_fetch():
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key="software-only",
            bharatstock_requests=1,
            drishti_requests=0,
            drishti_credits=0,
        )
    )
    await service.providers["bharatstock"].client.aclose()
    service.providers["bharatstock"].client = httpx.AsyncClient(
        base_url="https://bharatstockapi.com",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"data": []})),
    )
    try:
        output = await call(
            ToolView(MarginMCP(service)),
            "margin_company_data_readiness",
            {"ticker": "EXAMPLE", "execute": True, "idempotency_key": "empty-software-response"},
        )
        assert output["status"] != "success"
        assert output["report"]["rows"] == [] and output["report"]["readiness"] == []
        assert output["report"]["valuation_readiness"]["status"] == "not_assessed"
        assert service.ledger.requests == {"bharatstock": 1, "drishti": 0}
    finally:
        await service.close()


def explicit_model():
    return {
        "forecast_fcff": ["10", "10", "10"],
        "wacc": "0.1",
        "terminal_growth": "0",
        "debt": "20",
        "cash": "5",
        "other_equity_adjustments": "-2",
        "diluted_shares": "10",
        "amount_unit": "INR",
        "valuation_date": "2026-11-27",
        "company_type": "non_financial",
    }


async def test_dcf_alias_matches_exact_core_schema_and_independent_perpetuity(owner):
    schema = copy.deepcopy(SPECS["finance.calculate_dcf"][1])
    schema["properties"]["why"] = WHY
    assert owner.tools["margin_calculate_dcf"].input_schema == schema
    view = ToolView(owner)
    values = explicit_model()
    output = await call(view, "margin_calculate_dcf", values)
    generic = await call(
        view, "margin_calculate", {"function": "finance.calculate_dcf", "arguments": values}
    )
    assert generic == output
    assert abs(Decimal(output["values"]["enterprise_value"]) - 100) < Decimal("1e-27")
    assert abs(Decimal(output["values"]["equity_value"]) - 83) < Decimal("1e-27")
    assert abs(Decimal(output["values"]["value_per_share_inr"]) - Decimal("8.3")) < Decimal("1e-27")
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"arguments": explicit_model()},
        explicit_model() | {"wacc": "0"},
        explicit_model() | {"terminal_growth": "0.2"},
    ],
)
async def test_dcf_missing_or_invalid_inputs_are_not_completed_with_invented_data(owner, values):
    response = await owner.call("margin_calculate_dcf", values)
    assert response.is_error
    assert "data" not in response.structured_content
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}
