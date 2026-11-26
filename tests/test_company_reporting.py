"""Reporting regressions use fictional values; no providers, models or issuer gold."""

import copy
from decimal import Decimal

import pytest

from margin.analysis.reporting import company_report, formatted_value


def test_complete_checked_fields_do_not_authenticate_source_facts():
    report = company_report(
        output("data_readiness"),
        {
            "values": {
                "periods_returned": ["2026-03-31"],
                "null_fields_latest_period": [],
                "calculation_readiness": {
                    "finance.company_growth": {"status": "success", "issues": []}
                },
                "valuation_readiness": {"status": "needs_explicit_inputs"},
            },
            "inputs": [],
        },
    )
    assert report["null_fields_latest_period"] == []
    assert report["readiness_scope"]["source_facts_verified"] is False
    assert report["readiness_scope"]["numeric_rows_expected"] is False
    assert report["readiness_scope"]["checked_calculations"] == 1
    assert report["readiness_scope"]["assessment_status"] == "success"


@pytest.mark.parametrize(
    "raw,unit,value,display",
    [
        ("10000000", "INR", "1", "₹1.00 crore"),
        ("10000", "INR_thousand", "1", "₹1.00 crore"),
        ("100", "INR_lakh", "1", "₹1.00 crore"),
        ("1", "INR_crore", "1", "₹1.00 crore"),
        ("1234567000000", "INR", "123456.7", "₹123,456.70 crore"),
        ("-150000000", "INR", "-15", "₹-15.00 crore"),
        ("0", "INR", "0", "₹0.00 crore"),
        ("42.5", "INR_per_share", "42.5", "₹42.50 per share"),
        ("9.607951", "percent", "9.607951", "9.61%"),
        ("0.1251", "ratio", "0.1251", "0.13×"),
        ("1.125", "years", "1.125", "1.125000 years"),
    ],
)
def test_exact_value_unit_and_display_agree(raw, unit, value, display):
    actual, target, formatted, status = formatted_value(raw, unit)
    assert Decimal(actual) == Decimal(value)
    assert target == ("INR_crore" if unit.startswith("INR") and unit != "INR_per_share" else unit)
    assert formatted == display and status == "success"


@pytest.mark.parametrize(
    "raw,unit",
    [
        (None, "INR"),
        ("123", None),
        ("123", "USD"),
        (True, "INR"),
        ("NaN", "percent"),
        ("Infinity", "ratio"),
        ("1e10000000", "INR"),
    ],
)
def test_unknown_missing_and_invalid_do_not_become_zero(raw, unit):
    value, _, display, status = formatted_value(raw, unit)
    assert value is None and status == "unavailable"
    assert "0.00" not in display


def source_input(metric, value, end="2026-03-31", unit="INR", **extra):
    return {
        "metric": metric,
        "definition": "Fictional " + metric,
        "value": value,
        "unit": unit,
        "period_type": "annual",
        "period_start": None,
        "period_end": end,
        **extra,
    }


def output(function="growth", **extra):
    return {
        "function": "finance.company_" + function,
        "status": "success",
        "selection": {
            "ticker": "SYNTHA",
            "exchange": "NSE",
            "basis": "consolidated",
            "period_type": "annual",
            "metric": "revenue",
        },
        "issues": [],
        **extra,
    }


def test_growth_report_scales_absolute_change_and_preserves_comparison_dates():
    technical = {
        "inputs": [
            source_input("revenue", "1000000000000", "2025-03-31"),
            source_input("revenue", "1100000000000"),
        ],
        "values": {
            "absolute_change": "100000000000",
            "percentage_change": "10",
            "unit": "INR",
            "formula": "(current - previous) / previous * 100",
        },
    }
    before = copy.deepcopy(technical)
    report = company_report(output(), technical)
    indexed = {r["metric"]: r for r in report["rows"] if r["kind"] == "result"}
    change = indexed["absolute_change"]
    assert Decimal(change["value"]) == Decimal("10000") and change["unit"] == "INR_crore"
    assert change["display"] == "₹10,000.00 crore"
    assert change["formula"] == "current - previous"
    assert indexed["percentage_change"]["formula"] == "(current - previous) / previous * 100"
    assert change["comparison_period_ends"] == ["2025-03-31", "2026-03-31"]
    assert change["period_start"] is None and change["period_end"] is None
    assert indexed["percentage_change"]["display"] == "10.00%"
    assert "summary" not in report and "table_markdown" not in report
    assert technical == before


def test_margin_row_keeps_continuing_profit_scope():
    report = company_report(
        output("margins"),
        {
            "inputs": [
                source_input("profit_from_continuing_operations", "150000000"),
                source_input("revenue", "1000000000"),
            ],
            "values": {
                "margin_percent": "15",
                "profit_definition": "Reported group profit from continuing operations",
                "formula": "profit / revenue * 100",
            },
        },
    )
    result = next(row for row in report["rows"] if row["kind"] == "result")
    assert result["profit_definition"] == "Reported group profit from continuing operations"
    assert result["display"] == "15.00%"
    assert [row["display"] for row in report["rows"] if row["kind"] == "input"] == [
        "₹15.00 crore",
        "₹100.00 crore",
    ]
    assert "summary" not in report and "table_markdown" not in report


@pytest.mark.parametrize(
    "metric,unit,raw,expected",
    [
        ("working_capital", "INR", "-20000000", "₹-2.00 crore"),
        ("gross_borrowings", "INR", "0", "₹0.00 crore"),
        ("current_ratio", "ratio", "2.345", "2.34×"),
        ("cfo_margin_percent", "percent", "15.678", "15.68%"),
    ],
)
def test_component_units_and_rounding_are_explicit(metric, unit, raw, expected):
    report = company_report(
        output("balance_sheet_metrics"),
        {
            "inputs": [],
            "values": {metric: raw},
            "components": {
                metric: {"status": "success", "unit": unit, "formula": "fictional formula"}
            },
        },
    )
    row = report["rows"][0]
    assert row["display"] == expected
    assert row["formula"] == "fictional formula"


def test_scope_holds_stay_visible_and_withhold_any_numeric_result():
    report = company_report(
        output("profitability", status="partial"),
        {
            "inputs": [],
            "values": {"net_profit_margin_percent": "99"},
            "components": {
                "net_profit_margin_percent": {
                    "status": "needs_scope_review",
                    "unit": "percent",
                    "issue": "Different continuing and total profit scopes.",
                }
            },
        },
    )
    held = report["rows"][0]
    assert held["value"] is None and held["status"] == "needs_scope_review"
    assert "Different continuing and total profit scopes" in held["issue"]
    assert held["display"] == "Withheld (needs_scope_review)"


def test_cfo_minus_capex_is_an_amount_and_coverage_is_a_ratio():
    report = company_report(
        output("cashflow_metrics"),
        {
            "values": {
                "cfo_minus_capex": "120000000",
                "capex_coverage": None,
                "unit": "INR",
                "definition": "CFO minus cash capex; not FCFF.",
            },
        },
    )
    amount, coverage = report["rows"]
    assert amount["display"] == "₹12.00 crore" and amount["unit"] == "INR_crore"
    assert amount["formula"] == "cfo - capex"
    assert coverage["formula"] == "cfo / capex"
    assert "not FCFF" in amount["label"]
    assert coverage["value"] is None and coverage["unit"] == "ratio"


def test_cagr_formula_is_not_attached_to_its_elapsed_years_input():
    report = company_report(
        output("cagr"),
        {
            "values": {
                "cagr_percent": "10",
                "years": "2",
                "formula": "((current / previous) ** (1 / years) - 1) * 100",
            }
        },
    )
    indexed = {row["metric"]: row for row in report["rows"]}
    assert indexed["cagr_percent"]["formula"] == "((current / previous) ** (1 / years) - 1) * 100"
    assert "formula" not in indexed["years"]


def test_ttm_uses_only_the_core_established_interval_and_unit():
    report = company_report(
        output("ttm"),
        {
            "values": {
                "total": "1230000000",
                "unit": "INR",
                "period_start": "2025-04-01",
                "period_end": "2026-03-31",
            }
        },
    )
    row = report["rows"][0]
    assert row["period_type"] == "ttm" and row["period_start"] == "2025-04-01"
    assert row["display"] == "₹123.00 crore"


def test_readiness_and_forecast_requirements_are_not_invented_amounts():
    report = company_report(
        output("data_readiness"),
        {
            "values": {
                "periods_returned": ["2026-03-31"],
                "null_fields_latest_period": ["capex"],
                "calculation_readiness": {
                    "finance.company_cashflow_metrics": {
                        "status": "incomplete",
                        "issues": ["No capex returned."],
                    }
                },
                "valuation_readiness": {
                    "status": "needs_explicit_inputs",
                    "required": ["FCFF forecasts"],
                },
            }
        },
    )
    assert not report["rows"]
    assert report["readiness"][0]["issues"] == ["No capex returned."]
    assert report["valuation_readiness"]["required"] == ["FCFF forecasts"]
    assert report["null_fields_latest_period"] == ["capex"]


def test_unknown_numeric_output_unit_is_not_given_an_invented_value():
    report = company_report(
        output(),
        {
            "inputs": [
                source_input(
                    "revenue", "100", unit=None, definition="Fictional | label\nsecond line"
                )
            ],
            "values": {"future_metric": "1"},
        },
    )
    assert report["rows"][0]["value"] is None and report["rows"][0]["unit"] is None
    assert report["unmapped_fields"] == ["future_metric"]
    assert report["rows"][0]["label"] == "Fictional | label\nsecond line"
    assert "summary" not in report and "table_markdown" not in report
