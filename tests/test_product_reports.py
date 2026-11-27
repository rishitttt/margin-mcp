"""Product reports preserve exact calculation values and distinguish budget semantics."""

import copy
import json
from decimal import Decimal

import pytest

from margin.analysis.product_reports import input_contract, render_report
from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.finance.dcf import calculate_dcf
from margin.interfaces.mcp.profiles import ToolView
from margin.interfaces.mcp.server import MarginMCP


def model(**more):
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
        **more,
    }


@pytest.mark.parametrize("profile", ["all", "finance", "review", "review-simple"])
async def test_status_has_unambiguous_default_report_and_opt_in_diagnostics(profile):
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        view = ToolView(MarginMCP(service), profile)
        before = service.ledger.snapshot()
        result = await view.call("margin_status", {})
        assert not result.is_error
        data = result.structured_content["data"]
        report = data["report"]
        assert json.loads(result.content[0].text)["data"]["report"] == report
        rows = {r["metric"]: r for r in report["rows"]}
        for provider in ("bharatstock", "drishti"):
            r = rows[provider + "_local_http_allowance"]
            assert r["value"] == r["used"] == r["limit"] == 0
            assert r["unit"] == "HTTP_attempts" and r["scope"] == "local_process"
        assert rows["provider_account_balance"]["value"] is None
        assert rows["provider_account_balance"]["status"] == "unknown"
        assert "diagnostics" not in data and "company_finance_requests" not in data
        assert "last_historical_balance" not in data and "receipt_count" not in data
        detailed = (
            await view.call("margin_status", {"include_diagnostics": True})
        ).structured_content["data"]
        assert detailed["diagnostics"]["company_finance_requests"]["limit"] == 200
        assert detailed["report"] == report
        assert service.status()["company_finance_requests"]["limit"] == 200  # core compatibility
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


async def test_status_remaining_and_credit_reservations_are_local_not_account_balance():
    service = ResearchService(
        Settings(bharatstock_requests=2, drishti_requests=16, drishti_credits=8)
    )
    try:
        await service.ledger.http_attempt("bharatstock", seconds=0)
        await service.ledger.reserve("drishti", 3)
        data = (await MarginMCP(service).call("margin_status", {})).structured_content["data"]
        rows = {r["metric"]: r for r in data["report"]["rows"]}
        assert rows["bharatstock_local_http_allowance"]["value"] == 1
        assert rows["drishti_local_http_allowance"]["value"] == 16
        assert rows["drishti_local_estimated_credit_allowance"]["value"] == 5
        assert rows["provider_account_balance"]["value"] is None
        await service.ledger.settle(3, dispatched=False)
    finally:
        await service.close()


@pytest.mark.parametrize("unit", ["INR", "INR_thousand", "INR_lakh", "INR_crore"])
def test_dcf_report_preserves_amount_scale_and_distinguishes_terminal_timing(unit):
    output = calculate_dcf(**model(amount_unit=unit))
    values, report = output["values"], output["report"]
    rows = {r["metric"]: r for r in report["rows"]}
    assert Decimal(rows["terminal_value"]["value"]) == 100
    assert abs(
        Decimal(rows["terminal_present_value"]["value"])
        - Decimal("75.1314800901577761081893313298272")
    ) < Decimal("1e-27")
    assert "undiscounted" in rows["terminal_value"]["label"]
    assert "discounted" in rows["terminal_present_value"]["label"]
    assert rows["terminal_value"]["unit"] == unit
    for metric, row in rows.items():
        assert row["value"] == values[metric]
    assert rows["value_per_share_inr"]["unit"] == "INR_per_share"
    assert report["markdown"] == render_report(report)
    assert "explicit caller" in report["input_origin"]


def test_dcf_report_missing_shares_negative_equity_and_contract_are_not_repaired():
    no_shares = calculate_dcf(**model(diluted_shares=None))
    assert no_shares["report"]["rows"][-1]["status"] == "unavailable"
    assert no_shares["report"]["rows"][-1]["value"] is None
    negative = calculate_dcf(**model(debt="1000"))
    assert Decimal(negative["report"]["rows"][-2]["value"]) < 0
    contract = input_contract()
    assert "cash_flow_operating" in contract["forecast_fcff"]["not_equivalent_to"]
    assert "total_liabilities" in contract["debt"]["not_equivalent_to"]
    snapshot = copy.deepcopy(contract)
    contract["debt"]["definition"] = "wrong"
    assert input_contract() == snapshot


def test_report_renderer_escapes_table_control_markup_and_bounds_output():
    report = {
        "title": "Test",
        "rows": [{"label": "[source](url)|<tag>`\n", "display": "value"}] * 80,
        "warnings": ["Warning"] * 40,
    }
    rendered = render_report(report)
    assert "\\|" in rendered and "\\[" in rendered and "\\<" in rendered
    assert rendered.count("| value |") == 60
    assert rendered.count("Warning") == 20
