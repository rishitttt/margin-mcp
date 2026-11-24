"""Independent fictional software references; real-company checks stay private."""

from copy import deepcopy
from decimal import Decimal

import httpx
import pytest

from margin.analysis.calculations import calculate_ttm
from margin.analysis.company import FUNCTIONS, calculate_company
from margin.analysis.facts import prepare_financial_facts
from margin.analysis.service import calculate
from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest
from margin.core.registry import DRISHTI, Registry
from margin.core.service import ResearchService
from margin.evidence.results import inspect_result


def record(rows=None):
    return {
        "operation": "bharatstock.get_financials",
        "operation_id": "software-example",
        "status": "success",
        "mode": "live",
        "payload_kind": "rest_json",
        "receipt": {
            "arguments": {"ticker": "EXAMPLE", "exchange": "NSE", "period_type": "annual"},
            "retrieved_at": "2026-11-24T00:00:00Z",
        },
        "payload": {
            "data": rows
            or [
                {
                    "period_type": "annual",
                    "period_end_date": "2026-03-31",
                    "consolidation_type": "consolidated",
                    "revenue": 200,
                    "net_profit": 25,
                    "profit_from_continuing_operations": 25,
                    "net_profit_attributable_to_owners": 20,
                    "operating_profit": 40,
                    "ebitda": 50,
                    "cash_flow_operating": 50,
                    "capex": 10,
                    "eps": 2,
                    "current_assets": 200,
                    "current_liabilities": 100,
                    "inventories": 50,
                    "cash_and_cash_equivalents": 30,
                    "borrowings_current": 10,
                    "borrowings_non_current": 20,
                    "total_equity": 100,
                    "total_assets": 500,
                    "total_liabilities": 400,
                }
            ]
        },
    }


def facts_for(metrics):
    return [f for f in prepare_financial_facts(record())["facts"] if f["metric"] in metrics]


def test_documented_units_stocks_and_explicit_unknown_preserve_source():
    source = record()
    before = deepcopy(source)
    facts = {f["metric"]: f for f in prepare_financial_facts(source)["facts"]}
    assert facts["revenue"]["unit"] == "INR"
    assert facts["eps"]["unit"] == "INR_per_share"
    assert facts["revenue"]["unit_origin"] == "provider_documentation"
    assert facts["revenue"]["source"]["unit_evidence"]["policy_version"]
    assert facts["current_assets"]["period_type"] == "instant"
    assert source == before
    assert all(f["unit"] is None for f in prepare_financial_facts(source, None)["facts"])
    assert all(f["unit"] is None for f in prepare_financial_facts(source, "unknown")["facts"])
    with pytest.raises(DomainError, match="documented in INR"):
        prepare_financial_facts(source, "INR_crore")


def test_ttm_documented_quarters_are_traceable_and_sum_correctly():
    ends = ["2025-12-31", "2026-03-31", "2026-06-30", "2026-09-30"]
    rows = [
        {
            "period_type": "quarterly",
            "period_end_date": end,
            "revenue": 25,
            "consolidation_type": "consolidated",
            "reported_period_days": None,
            "filed_period_days": None,
        }
        for end in ends
    ]
    source = record(rows)
    facts = prepare_financial_facts(source)["facts"]
    assert [f["period_start"] for f in facts] == [
        "2025-10-01",
        "2026-01-01",
        "2026-04-01",
        "2026-07-01",
    ]
    assert all(f["source"]["period_start_origin"] == "provider_documentation" for f in facts)
    output = calculate_ttm(facts)
    assert output["status"] == "success" and output["values"]["total"] == "100"


@pytest.mark.parametrize(
    "change",
    [
        {"reported_period_days": 182},
        {"filed_period_days": 183},
        {"period_end_date": "2026-09-29"},
        {"reported_period_days": "absent"},
    ],
)
def test_quarter_start_not_guessed_for_ambiguous_rows(change):
    row = {
        "period_type": "quarterly",
        "period_end_date": "2026-09-30",
        "revenue": 25,
        "consolidation_type": "consolidated",
        "reported_period_days": None,
        "filed_period_days": None,
    } | change
    if row["reported_period_days"] == "absent":
        del row["reported_period_days"]
    assert prepare_financial_facts(record([row]))["facts"][0]["period_start"] is None


def test_basis_change_and_longer_period_cannot_be_bypassed_with_supplied_starts():
    f = prepare_financial_facts(record())["facts"][0]
    f.update(period_type="quarterly", period_start="2026-07-01", period_end="2026-09-30")
    f["source"].update(basis_changed=True, reported_period_days=182)
    output = calculate_ttm([deepcopy(f) for _ in range(4)])
    assert output["status"] == "incomplete"
    assert any("basis change" in issue for issue in output["issues"])
    assert any("Longer" in issue for issue in output["issues"])


def test_balance_sheet_reference_math_and_missing_components():
    metrics = {
        "current_assets",
        "current_liabilities",
        "inventories",
        "cash_and_cash_equivalents",
        "borrowings_current",
        "borrowings_non_current",
        "total_equity",
        "total_assets",
        "total_liabilities",
    }
    facts = facts_for(metrics)
    output = calculate("finance.calculate_balance_sheet_metrics", {"facts": facts})
    assert output["status"] == "success"
    expected = {
        "working_capital": "100",
        "current_ratio": "2",
        "current_assets_less_inventory_ratio": "1.5",
        "cash_ratio": "0.3",
        "gross_borrowings": "30",
        "net_borrowings": "0",
        "borrowings_to_total_equity": "0.3",
        "liabilities_to_assets": "0.8",
    }
    assert {k: Decimal(v) for k, v in output["values"].items()} == {
        k: Decimal(v) for k, v in expected.items()
    }
    for f in facts:
        if f["metric"] == "current_liabilities":
            f["value"] = None
    output = calculate("finance.calculate_balance_sheet_metrics", {"facts": facts})
    assert output["status"] == "partial"
    assert "current_ratio" not in output["values"] and "net_borrowings" in output["values"]
    assert output["components"]["current_ratio"]["missing_fields"] == ["current_liabilities"]


@pytest.mark.parametrize(
    "change",
    [
        {"unit": "INR_crore"},
        {"issuer": "NSE:OTHER"},
        {"basis": "standalone"},
        {"period_end": "2025-03-31"},
        {"period_type": "annual"},
    ],
)
def test_balance_sheet_rejects_context_mixing(change):
    facts = facts_for({"current_assets", "current_liabilities"})
    facts[0].update(change)
    assert (
        calculate("finance.calculate_balance_sheet_metrics", {"facts": facts})["status"]
        == "incomplete"
    )


def test_cash_conversion_and_profitability_reference_math():
    output = calculate(
        "finance.calculate_cash_conversion",
        {"facts": facts_for({"cash_flow_operating", "capex", "net_profit", "revenue"})},
    )
    assert output["status"] == "success"
    assert {k: Decimal(v) for k, v in output["values"].items()} == {
        "cfo_margin_percent": Decimal(25),
        "cfo_to_group_profit": Decimal(2),
        "capex_to_revenue_percent": Decimal(5),
        "cfo_less_capex_margin_percent": Decimal(20),
    }
    output = calculate(
        "finance.calculate_profitability",
        {
            "facts": facts_for(
                {
                    "net_profit",
                    "profit_from_continuing_operations",
                    "net_profit_attributable_to_owners",
                    "operating_profit",
                    "ebitda",
                    "revenue",
                }
            )
        },
    )
    assert output["status"] == "success"
    assert Decimal(output["values"]["net_profit_margin_percent"]) == Decimal("12.5")
    assert Decimal(output["values"]["net_profit_attributable_to_owners_margin_percent"]) == 10
    assert Decimal(output["values"]["operating_profit_margin_percent"]) == 20
    assert Decimal(output["values"]["ebitda_margin_percent"]) == 25


def test_discontinued_profit_is_not_silently_used_as_continuing_margin():
    source = record()
    source["payload"]["data"][0]["profit_from_continuing_operations"] = 10
    args = {
        "ticker": "EXAMPLE",
        "exchange": "NSE",
        "period_type": "annual",
        "basis": "consolidated",
        "money_unit": "auto",
        "metric": "revenue",
        "source_operation_id": source["operation_id"],
        "source_run_id": "saved-example",
    }
    output = calculate_company("finance.company_margins", args, source)
    assert output["status"] == "success"
    assert output["inputs"][0]["metric"] == "profit_from_continuing_operations"
    assert Decimal(output["values"]["margin_percent"]) == 5
    group = calculate_company("finance.company_profitability", args, source)
    assert group["status"] == "partial"
    assert "net_profit_margin_percent" not in group["values"]
    assert group["components"]["net_profit_margin_percent"]["status"] == "needs_scope_review"
    facts = {f["metric"]: f for f in prepare_financial_facts(source)["facts"]}
    direct = calculate(
        "finance.calculate_margins", {"profit": facts["net_profit"], "revenue": facts["revenue"]}
    )
    assert direct["status"] == "incomplete"


def test_zero_negative_and_missing_denominators_are_not_fabricated():
    facts = facts_for({"cash_flow_operating", "capex", "net_profit", "revenue"})
    for f in facts:
        if f["metric"] == "net_profit":
            f["value"] = "0"
    output = calculate("finance.calculate_cash_conversion", {"facts": facts})
    assert output["status"] == "partial" and "cfo_to_group_profit" not in output["values"]
    for f in facts:
        if f["metric"] == "capex":
            f["value"] = "-10"
    with pytest.raises(DomainError):
        calculate("finance.calculate_cash_conversion", {"facts": facts})


def test_reconciliation_distinguishes_scale_agreement_definition_conflict_and_value_conflict():
    left = facts_for({"revenue"})[0]
    right = deepcopy(left)
    right.update(value="0.00002", unit="INR_crore")
    output = calculate("finance.reconcile_facts", {"left": left, "right": right})
    assert output["status"] == "success" and output["values"]["numerically_equal"]
    right["definition"] = "Product sales only"
    output = calculate("finance.reconcile_facts", {"left": left, "right": right})
    assert output["status"] == "incomplete" and output["values"]["numerically_equal"]
    right["value"] = "0.000019"
    assert (
        calculate("finance.reconcile_facts", {"left": left, "right": right})["values"]["difference"]
        == "10.000000"
    )


def test_field_units_keep_market_cap_paths_separate():
    payload = {
        "market_cap": 20000000,
        "metrics": {"market_cap": 2},
        "mystery": 500,
        "latest_price": {"close": 3, "volume": 4},
    }
    _, _, coverage, _ = inspect_result(payload, "rest_json", "bharatstock.get_stock_quote")
    assert coverage["field_units"] == {
        "market_cap": "INR",
        "metrics.market_cap": "INR_crore",
        "latest_price.close": "INR_per_share",
        "latest_price.volume": "shares",
    }
    assert payload["market_cap"] == 20000000
    _, _, unknown, _ = inspect_result(
        {"unreviewed": {"market_cap": 2, "close": 3}}, "rest_json", "bharatstock.get_stock_quote"
    )
    assert "field_units" not in unknown


@pytest.mark.parametrize(
    "normalized,raw,unit,expected",
    [
        (100, 100, "Rs in crores", False),
        (100, 110, "Rs in crores", True),
        ("100.0", 100, "Rs in crores", False),
        (100, 100, "INR", False),
    ],
)
def test_nested_earnings_discrepancy_checks_respect_cells_units_and_numeric_types(
    normalized, raw, unit, expected
):
    payload = {
        "structuredContent": {
            "data": {
                "earnings_table": {
                    "consolidated": {
                        "revenue": {"current_period_value": normalized, "unit": "Rs in crores"},
                        "revenue_from_operations_raw": {"current_period_value": raw, "unit": unit},
                    }
                }
            }
        }
    }
    _, warnings, _, _ = inspect_result(payload, "mcp_result", "drishti.get_earnings_filing")
    assert any("differ in the same declared unit" in w for w in warnings) is expected
    assert any("units are missing or different" in w for w in warnings) is (unit != "Rs in crores")


@pytest.mark.asyncio
async def test_live_unit_conflict_is_rejected_before_data_plan_or_dispatch():
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        with pytest.raises(DomainError, match="documented INR"):
            service.plan_financial(
                "finance.company_margins",
                "EXAMPLE",
                "NSE",
                money_unit="INR_crore",
                fetch_missing=True,
            )
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
        assert not service.plans
    finally:
        await service.close()


def test_announcement_change_is_reviewed_but_extracted_branch_stays_held():
    registry = Registry(Settings())
    assert (
        DRISHTI["get_announcements"]["inputSchema"]["$defs"]["AnnouncementsQueryParams"][
            "properties"
        ]["include_extracted_information"]["default"]
        is True
    )
    args = {
        "query": {
            "symbols": ["EXAMPLE"],
            "lookback_days": 7,
            "page": 1,
            "limit": 1,
            "detailed": False,
        }
    }
    request = OperationRequest("drishti.get_announcements", args)
    registry.validate(request)
    assert args["query"]["include_extracted_information"] is False
    args["query"]["include_extracted_information"] = True
    with pytest.raises(DomainError):
        registry.validate(request)
    with pytest.raises(DomainError):
        registry.validate(OperationRequest("drishti.get_announcements", []))


@pytest.mark.asyncio
async def test_new_company_functions_reuse_one_source_and_readiness_has_no_hidden_fetch():
    async def handler(request):
        return httpx.Response(200, json=record()["payload"])

    service = ResearchService(Settings())
    await service.providers["bharatstock"].client.aclose()
    service.providers["bharatstock"].client = httpx.AsyncClient(
        base_url="https://bharatstockapi.com", transport=httpx.MockTransport(handler)
    )
    try:
        for index, name in enumerate(
            [
                "finance.company_data_readiness",
                "finance.company_profitability",
                "finance.company_cash_conversion",
                "finance.company_balance_sheet_metrics",
            ]
        ):
            plan = service.plan_financial(name, "EXAMPLE", "NSE", fetch_missing=index == 0)
            run = await service.start_run(plan["plan_id"], f"new-company-{index}")
            await service._tasks[run["run_id"]]
            state = service.get_run(run["run_id"])
            result = service.get_result(run["run_id"], state["operations"][-1]["operation_id"])
            assert result["status"] == "success", result
            if index == 0:
                assert (
                    result["payload"]["values"]["valuation_readiness"]["status"]
                    == "needs_explicit_inputs"
                )
                assert (
                    len(result["payload"]["values"]["calculation_readiness"]) == len(FUNCTIONS) - 2
                )  # excludes itself and quarterly TTM
        assert service.ledger.requests["bharatstock"] == 1
        assert service.ledger.requests["drishti"] == 0
    finally:
        await service.close()
