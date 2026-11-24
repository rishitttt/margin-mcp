"""All retrieval and local calculation contracts through real orchestration, fictional fixtures."""

from decimal import Decimal

import pytest

from margin.core.config import Settings
from margin.core.service import ResearchService

B = {"ticker": "SYNTHA", "exchange": "NSE"}
Q = {
    "query": {
        "symbols": ["SYNTHA"],
        "from": "2026-10-01",
        "to": "2026-10-19",
        "limit": 1,
        "page": 1,
    }
}
RETRIEVAL = [
    ("bharatstock.search_stocks", {"q": "SYNTHA", "limit": 3}),
    ("bharatstock.get_stock_quote", B),
    ("bharatstock.get_stock_fundamentals", B),
    ("bharatstock.get_financials", B | {"period_type": "annual", "page": 1, "page_size": 2}),
    (
        "bharatstock.get_stock_prices",
        B | {"from": "2026-10-01", "to": "2026-10-10", "page": 1, "page_size": 5},
    ),
    (
        "bharatstock.get_corporate_actions",
        B | {"action_type": "dividend", "page": 1, "page_size": 5},
    ),
    ("drishti.get_symbols", {"query": {"symbols": ["SYNTHA"]}}),
    ("drishti.resolve_symbols", {"queries": ["Synthetic Alpha"]}),
    ("drishti.get_news", Q),
    ("drishti.get_announcements", Q),
    ("drishti.get_announcement_categories", {}),
    ("drishti.list_earnings", Q),
    ("drishti.get_earnings_filing", {"symbol": "SYNTHA", "quarter": "q1_27", "detailed": True}),
]


def observation(value, **changes):
    return {
        "issuer": "NSE:EXAMPLE",
        "metric": "revenue",
        "definition": "Fictional revenue",
        "value": value,
        "unit": "INR",
        "period_type": "annual",
        "period_start": "2024-04-01",
        "period_end": "2025-03-31",
        "basis": "consolidated",
        **changes,
    }


def calculations():
    previous = observation("100")
    current = observation("121", period_start="2025-04-01", period_end="2026-03-31")
    profit = current | {
        "metric": "net_profit",
        "definition": "Fictional group profit",
        "value": "24.2",
    }
    cfo = current | {"metric": "cash_flow_operating", "definition": "Fictional CFO", "value": "100"}
    capex = current | {
        "metric": "capex",
        "definition": "Fictional positive cash outflow",
        "value": "40",
    }
    periods = [
        ("2025-01-01", "2025-03-31"),
        ("2025-04-01", "2025-06-30"),
        ("2025-07-01", "2025-09-30"),
        ("2025-10-01", "2025-12-31"),
    ]
    model = {
        "forecast_fcff": ["10", "10", "10"],
        "wacc": "0.1",
        "terminal_growth": "0",
        "debt": "20",
        "cash": "5",
        "other_equity_adjustments": "-2",
        "diluted_shares": "10",
        "amount_unit": "INR",
        "valuation_date": "2026-11-24",
        "company_type": "non_financial",
    }
    return [
        ("facts.check_compatibility", {"facts": [profit, current], "purpose": "ratio"}, None, None),
        ("facts.convert_units", {"value": current, "target_unit": "INR_crore"}, None, None),
        (
            "finance.compare_periods",
            {"previous": previous, "current": current},
            "percentage_change",
            "21",
        ),
        (
            "finance.calculate_margins",
            {"profit": profit, "revenue": current},
            "margin_percent",
            "20",
        ),
        (
            "finance.calculate_cashflow_metrics",
            {"cfo": cfo, "capex": capex},
            "cfo_minus_capex",
            "60",
        ),
        (
            "finance.calculate_cagr",
            {"previous": previous, "current": current, "years": "1"},
            "cagr_percent",
            "21",
        ),
        (
            "finance.calculate_ttm",
            {
                "facts": [
                    observation(
                        str((i + 1) * 10),
                        period_type="quarterly",
                        period_start=start,
                        period_end=end,
                    )
                    for i, (start, end) in enumerate(periods)
                ]
            },
            "total",
            "100",
        ),
        (
            "finance.calculate_fcff",
            {
                "ebit": "100",
                "tax_rate": "0.25",
                "depreciation": "10",
                "capex": "20",
                "change_in_working_capital": "5",
                "amount_unit": "INR",
            },
            "fcff",
            "60",
        ),
        ("finance.calculate_dcf", model, "enterprise_value", "100"),
        (
            "finance.dcf_sensitivity",
            {"model": model, "discount_rates": ["0.1"], "terminal_growth_rates": ["0"]},
            None,
            None,
        ),
        ("finance.run_scenarios", {"model": model, "scenarios": {"same": {}}}, None, None),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation,arguments", RETRIEVAL, ids=[op for op, _ in RETRIEVAL])
async def test_every_retrieval_contract_through_core(operation, arguments):
    service = ResearchService(Settings())
    try:
        plan = service.create_plan([{"operation": operation, "arguments": arguments}])
        run = await service.start_run(plan["plan_id"], "matrix-retrieval-test")
        await service._tasks[run["run_id"]]
        result = service.get_result(run["run_id"], run["operations"][0]["operation_id"])
        assert result["status"] in {"success", "empty"}, result.get("error")
        assert result["receipt"]["http_attempts"] == 1
        assert result["mode"] == "synthetic"
        expected = arguments
        if operation == "drishti.get_announcements":
            expected = {"query": arguments["query"] | {"include_extracted_information": False}}
        assert result["receipt"]["arguments"] == expected
    finally:
        await service.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation,arguments,field,expected", calculations(), ids=[c[0] for c in calculations()]
)
async def test_every_calculation_contract_through_core(operation, arguments, field, expected):
    service = ResearchService(Settings())
    try:
        plan = service.create_plan([{"operation": operation, "arguments": arguments}])
        assert plan["data_operations"] == {"bharatstock": 0, "drishti": 0}
        run = await service.start_run(plan["plan_id"], "matrix-calculation-test")
        await service._tasks[run["run_id"]]
        result = service.get_result(run["run_id"], run["operations"][0]["operation_id"])
        assert result["status"] == "success", result.get("error")
        if field:
            assert abs(Decimal(result["payload"]["values"][field]) - Decimal(expected)) < Decimal(
                "1e-25"
            )
        if operation == "facts.check_compatibility":
            assert result["payload"]["compatible"]
        if operation == "facts.convert_units":
            assert Decimal(result["payload"]["fact"]["value"]) == Decimal("0.0000121")
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    finally:
        await service.close()
