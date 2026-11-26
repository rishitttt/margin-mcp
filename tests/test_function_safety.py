"""Adverse inputs across function families must never turn into provider work."""

import copy

import pytest
from jsonschema import Draft202012Validator

from margin.analysis.company import FUNCTIONS, default_period, planning_capabilities
from margin.analysis.service import SPECS
from margin.core.config import Settings
from margin.core.registry import build_specs
from margin.core.service import ResearchService
from margin.interfaces.mcp.server import MarginMCP
from margin.protocols.schemas import SCHEMAS


@pytest.fixture
async def owner():
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key="software-fixture-only",
            bharatstock_requests=0,
            drishti_requests=0,
            drishti_credits=0,
        )
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


@pytest.mark.parametrize("function", sorted(SPECS))
async def test_missing_calculation_facts_never_trigger_retrieval(owner, function):
    before = owner.service.ledger.snapshot()
    response = await owner.call("margin_calculate", {"function": function, "arguments": {}})
    assert response.is_error
    assert response.structured_content["error"]["code"] == "invalid_input"
    assert "Never invent" in response.structured_content["error"]["recovery_guidance"]
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize("operation", sorted(build_specs()))
async def test_missing_or_unavailable_retrieval_never_dispatch(owner, operation):
    before = owner.service.ledger.snapshot()
    response = await owner.call(
        "margin_preview", {"operations": [{"operation": operation, "arguments": {}}]}
    )
    assert response.is_error
    assert response.structured_content["error"]["code"] in {"invalid_input", "held_operation"}
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize("function", sorted(FUNCTIONS))
async def test_company_defaults_catalog_schema_and_request_agree(owner, function):
    before = owner.service.ledger.snapshot()
    metadata = next(r for r in planning_capabilities() if r["function"] == function)
    period = default_period(function)
    assert metadata["defaults"]["period_type"] == period
    fields = {"function": function, "ticker": "INFY", "exchange": "NSE", "fetch_missing": True}
    Draft202012Validator(metadata["planning_schema"]).validate(fields)
    args, request = owner.service.company_finance_workflow.prepare(
        {"function": function, "ticker": "INFY"}
    )
    assert args["period_type"] == request.arguments["period_type"] == period
    assert request.arguments["page_size"] == (8 if period == "quarterly" else 2)
    plan = owner.service.plan_financial(function, "INFY", "NSE", fetch_missing=True)
    assert plan["operations"][0]["arguments"]["period_type"] == period
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize("tool", ["margin_company_finance", "margin_company_preview"])
@pytest.mark.parametrize(
    "function,period,metric",
    [
        ("finance.company_ttm", "annual", "revenue"),
        ("finance.company_ttm", "quarterly", "eps"),
        ("finance.company_ttm", "quarterly", "total_assets"),
        ("finance.company_cagr", "quarterly", "revenue"),
    ],
)
async def test_host_schemas_reject_known_impossible_combinations(
    owner, tool, function, period, metric
):
    values = {
        "function": function,
        "ticker": "INFY",
        "exchange": "NSE",
        "period_type": period,
        "metric": metric,
    }
    assert not Draft202012Validator(owner.tools[tool].input_schema).is_valid(values)
    before = owner.service.ledger.snapshot()
    response = await owner.call(tool, values)
    assert response.is_error and owner.service.ledger.snapshot() == before


@pytest.mark.parametrize(
    "function", [name for name in SCHEMAS if name != "protocols.list_workflows"]
)
async def test_missing_review_inputs_do_not_create_fake_sources_or_packets(owner, function):
    before = copy.deepcopy(
        (
            owner.service.reviews.sources,
            owner.service.reviews.packets,
            owner.service.reviews.sessions,
        )
    )
    response = await owner.call("margin_review", {"function": function, "arguments": {}})
    assert response.is_error
    assert (
        owner.service.reviews.sources,
        owner.service.reviews.packets,
        owner.service.reviews.sessions,
    ) == before
