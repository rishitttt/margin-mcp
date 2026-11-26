"""Guidance stays explicit without claiming authenticated model inputs."""

import copy

import pytest

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.policy import DATA_INSTRUCTIONS, DATA_POLICY
from margin.interfaces.mcp.profiles import REVIEW_INSTRUCTIONS, SIMPLE_INSTRUCTIONS, ToolView
from margin.interfaces.mcp.server import INSTRUCTIONS, MarginMCP


@pytest.fixture
async def owner():
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


@pytest.mark.parametrize("instructions", [INSTRUCTIONS, REVIEW_INSTRUCTIONS, SIMPLE_INSTRUCTIONS])
def test_every_initialization_profile_leads_with_no_fabrication(instructions):
    assert instructions.startswith(DATA_INSTRUCTIONS)
    assert "user requests/supplies" in instructions
    assert "does not authenticate" in instructions


@pytest.mark.parametrize("profile", ["all", "review", "review-simple"])
async def test_status_preserves_policy_without_network_and_does_not_share_mutable_state(
    owner, profile
):
    view = ToolView(owner, profile)
    before = owner.service.ledger.snapshot()
    body = (await view.call("margin_status", {})).structured_content
    assert body["data"]["data_policy"] == DATA_POLICY
    body["data"]["data_policy"]["allowed_inputs"].append("fabricated")
    again = (await view.call("margin_status", {})).structured_content
    assert again["data"]["data_policy"] == DATA_POLICY
    assert owner.service.ledger.snapshot() == before


async def test_company_catalog_policy_preserves_both_routes_and_function_meanings(owner):
    before = owner.service.ledger.snapshot()
    response = await owner.call(
        "margin_catalog",
        {"group": "company", "name": "finance.company_growth", "include_schemas": True},
    )
    body = response.structured_content["data"]
    assert body["data_policy"] == DATA_POLICY
    row = body["groups"]["company"][0]
    assert row["mcp_execution"]["tool"] == "margin_company_preview"
    assert row["fresh_mcp_execution"]["tool"] == "margin_company_finance"
    hint = owner.tools["margin_company_finance"].input_schema["properties"]["function"][
        "description"
    ]
    assert "Annual growth is company_growth, not company_ttm" in hint
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize(
    "values,code",
    [
        (
            {"function": "finance.company_ttm", "ticker": "INFY", "period_type": "annual"},
            "invalid_input",
        ),
        (
            {"function": "finance.company_growth", "ticker": "INFY", "period_type": "annual"},
            "held_operation",
        ),
    ],
)
async def test_finance_errors_do_not_invite_invented_calculator_inputs(owner, values, code):
    before = owner.service.ledger.snapshot()
    response = await owner.call("margin_company_finance", values)
    assert response.is_error
    error = response.structured_content["error"]
    assert error["code"] == code
    assert "Never invent replacement values" in error["recovery_guidance"]
    assert "not growth" in error["recovery_guidance"]
    assert "data" not in response.structured_content
    assert owner.service.ledger.snapshot() == before


async def test_explicit_user_hypothetical_math_still_works_without_provider_auth(owner):
    context = {
        "issuer": "USER_EXAMPLE",
        "definition": "Explicit user-supplied hypothetical",
        "unit": "INR",
        "period_type": "annual",
        "period_start": "2025-04-01",
        "period_end": "2026-03-31",
        "basis": "standalone",
    }
    values = {
        "profit": context | {"metric": "net_profit", "value": "150"},
        "revenue": copy.deepcopy(context) | {"metric": "revenue", "value": "1000"},
        "why": "User-requested hypothetical arithmetic, not retrieved company data.",
    }
    before = owner.service.ledger.snapshot()
    response = await owner.call("margin_calculate_margins", values)
    assert not response.is_error
    assert response.structured_content["data"]["values"]["margin_percent"] == "15.00"
    assert owner.service.ledger.snapshot() == before
