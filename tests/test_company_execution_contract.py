"""Advertised call bounds and controls must agree with actual company previews."""

import copy

import pytest

from margin.analysis.company import FUNCTIONS
from margin.core.company_finance import execution_contract
from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import ToolView
from margin.interfaces.mcp.server import MarginMCP


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


@pytest.mark.parametrize("function", sorted(FUNCTIONS))
async def test_company_contract_matches_local_preview_without_spending_allowance(owner, function):
    before = owner.service.ledger.snapshot()
    catalog = (
        await owner.call("margin_catalog", {"group": "company", "name": function})
    ).structured_content["data"]
    row = catalog["groups"]["company"][0]
    contract = catalog["company_execution_contract"]
    assert contract == execution_contract()
    assert row["fresh_mcp_execution"]["provider"] == contract["provider"] == "bharatstock"
    assert row["fresh_mcp_execution"]["maximum_provider_requests"] == {
        "bharatstock": 1,
        "drishti": 0,
    }
    assert row["fresh_mcp_execution"]["execution_contract_ref"] == "company_execution_contract"
    preview = (
        await owner.call("margin_company_finance", {"function": function, "ticker": "INFY"})
    ).structured_content["data"]
    assert preview["status"] == "preview"
    assert preview["company_execution_contract"] == contract
    query = preview["data_operation"]["arguments"]
    assert query["page"] == contract["bounds"]["page"]
    assert query["page_size"] == contract["bounds"]["rows"][query["period_type"]]
    assert contract["preview"]["maximum_provider_requests"] == {"bharatstock": 0, "drishti": 0}
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize("group", ["calculations", "retrieval", "review"])
async def test_company_contract_is_not_advertised_for_unrelated_catalog_groups(owner, group):
    result = (await owner.call("margin_catalog", {"group": group})).structured_content["data"]
    assert "company_execution_contract" not in result


async def test_no_key_catalog_still_explains_execution_and_returns_isolated_copy():
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        owner = MarginMCP(service)
        values = {"group": "company", "name": "finance.company_growth"}
        result = (await owner.call("margin_catalog", values)).structured_content["data"]
        contract = result["company_execution_contract"]
        assert (
            contract["execution"]["execute"] and contract["execution"]["idempotency_key_required"]
        )
        assert contract["execution"]["session_id_required"] is False
        assert contract["answer_fields"]["data_readiness"] == [
            "report.readiness",
            "report.valuation_readiness",
        ]
        baseline = copy.deepcopy(execution_contract())
        contract["execution"]["maximum_provider_requests"]["drishti"] = 100
        assert execution_contract() == baseline
        again = (await owner.call("margin_catalog", values)).structured_content["data"]
        assert again["company_execution_contract"] == baseline
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    finally:
        await service.close()


async def test_review_catalog_projection_does_not_leak_fresh_company_contract(owner):
    result = (await ToolView(owner, "review").call("margin_catalog", {})).structured_content["data"]
    assert set(result["groups"]) == {"review"}
    assert "company_execution_contract" not in result
