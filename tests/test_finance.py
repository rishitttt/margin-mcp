"""Independent arithmetic and rejection cases; numbers are software examples, not company data."""

from copy import deepcopy
from decimal import Decimal

import pytest

from margin.analysis.calculations import (
    calculate_cagr,
    calculate_cashflow_metrics,
    calculate_margins,
    calculate_ttm,
    compare_periods,
)
from margin.analysis.facts import (
    check_compatibility,
    convert_units,
    decimal,
    prepare_financial_facts,
)
from margin.analysis.service import calculate
from margin.core.contracts import DomainError
from margin.finance.dcf import calculate_dcf, calculate_fcff, dcf_sensitivity, run_scenarios


def observation(value="100", **changes):
    return {
        "issuer": "NSE:EXAMPLE",
        "metric": "revenue",
        "definition": "Revenue from operations",
        "value": value,
        "unit": "INR",
        "basis": "consolidated",
        "period_type": "annual",
        "period_start": "2024-04-01",
        "period_end": "2025-03-31",
        **changes,
    }


def model(**changes):
    return {
        "forecast_fcff": ["10", "10", "10"],
        "wacc": "0.1",
        "terminal_growth": "0",
        "debt": "20",
        "cash": "5",
        "other_equity_adjustments": "-2",
        "diluted_shares": "10",
        "amount_unit": "INR",
        "valuation_date": "2026-11-15",
        "company_type": "non_financial",
        **changes,
    }


def assert_close(actual, expected):
    assert abs(Decimal(actual) - Decimal(expected)) < Decimal("1e-27")


def test_constant_cashflow_reference_is_a_perpetuity_and_bridge_is_explicit():
    # A perpetual 10 at 10% is 100 regardless of where the explicit period ends.
    output = calculate_dcf(**model())
    assert_close(output["values"]["enterprise_value"], "100")
    assert_close(output["values"]["equity_value"], "83")
    assert_close(output["values"]["value_per_share_inr"], "8.3")
    assert len(output["values"]["forecast"]) == 3
    assert output["inputs"]["input_origin"].startswith("explicit caller")


def test_dcf_preserves_crore_amounts_but_uses_actual_share_count():
    output = calculate_dcf(**model(amount_unit="INR_crore", diluted_shares="10000000"))
    assert_close(output["values"]["equity_value"], "83")
    assert_close(output["values"]["value_per_share_inr"], "83")
    no_shares = calculate_dcf(**model(diluted_shares=None))
    assert no_shares["values"]["value_per_share_inr"] is None


def test_negative_early_cashflows_and_negative_equity_are_not_silently_floored():
    output = calculate_dcf(
        **model(forecast_fcff=["-10", "20"], debt="0", cash="0", other_equity_adjustments="0")
    )
    assert_close(
        output["values"]["enterprise_value"], "172.7272727272727272727272727272727272727273"
    )
    output = calculate_dcf(**model(debt="1000"))
    assert Decimal(output["values"]["equity_value"]) < 0


@pytest.mark.parametrize(
    "changes",
    [
        {"wacc": "10"},
        {"terminal_growth": "0.1"},
        {"terminal_growth": "-1"},
        {"diluted_shares": "0"},
        {"debt": "-1"},
        {"company_type": "bank"},
        {"forecast_fcff": []},
        {"forecast_fcff": ["1"] * 21},
        {"forecast_fcff": ["0"]},
        {"forecast_fcff": ["NaN"]},
        {"cash": True},
        {"valuation_date": "2026-02-30"},
    ],
)
def test_invalid_valuation_inputs_are_rejected(changes):
    with pytest.raises(DomainError):
        calculate_dcf(**model(**changes))


def test_fcff_reference_uses_ebit_not_net_profit_or_cfo():
    output = calculate_fcff("100", "0.30", "20", "30", "10", "INR_crore")
    assert output["values"]["fcff"] == "50.00"
    assert "EBIT" in output["values"]["formula"]


def test_sensitivity_invalid_cells_are_visible_and_scenarios_do_not_mutate_base():
    base = model()
    before = deepcopy(base)
    grid = dcf_sensitivity(base, ["0.05", "0.15"], ["0", "0.1"])
    assert grid["values"]["cells"][0][1]["status"] == "invalid"
    assert Decimal(grid["values"]["cells"][0][0]["enterprise_value"]) > Decimal(
        grid["values"]["cells"][1][0]["enterprise_value"]
    )
    scenarios = run_scenarios(
        base, {"base": {}, "lower_cashflows": {"forecast_fcff": ["5", "5", "5"]}}
    )
    assert Decimal(scenarios["values"]["base"]["values"]["enterprise_value"]) > Decimal(
        scenarios["values"]["lower_cashflows"]["values"]["enterprise_value"]
    )
    assert base == before


def test_comparison_null_zero_units_basis_and_profit_definitions():
    previous = observation("100")
    current = observation("110", period_start="2025-04-01", period_end="2026-03-31")
    output = compare_periods(previous, current)
    assert output["values"]["percentage_change"] == "10.0"
    assert compare_periods(previous | {"value": None}, current)["status"] == "incomplete"
    assert compare_periods(previous | {"value": "0"}, current)["status"] == "not_meaningful"
    for change in (
        {"unit": None},
        {"unit": "INR_crore"},
        {"basis": "standalone"},
        {"metric": "net_profit_attributable_to_owners"},
        {"definition": "Different revenue definition"},
    ):
        assert compare_periods(previous, current | change)["status"] == "incomplete"


def test_reported_and_adjusted_eps_are_never_combined_or_adjusted_twice():
    a = observation(
        "40", metric="eps", definition="Basic EPS", unit="INR_per_share", adjustment="as_reported"
    )
    b = a | {"value": "22", "period_start": "2025-04-01", "period_end": "2026-03-31"}
    assert compare_periods(a, b)["status"] == "incomplete"
    a = a | {
        "value": "20",
        "metric": "eps_adjusted",
        "adjustment": "provider_adjusted",
        "adjustment_reference": "same snapshot",
    }
    b = b | {
        "metric": "eps_adjusted",
        "adjustment": "provider_adjusted",
        "adjustment_reference": "same snapshot",
    }
    assert compare_periods(a, b)["values"]["percentage_change"] == "10.0"
    assert (
        compare_periods(a, b | {"adjustment_reference": "another snapshot"})["status"]
        == "incomplete"
    )


def test_margin_cashflow_reference_and_missing_start_do_not_become_zero():
    revenue = observation("100")
    profit = observation("20", metric="net_profit", definition="Group net profit")
    assert calculate_margins(profit, revenue)["values"]["margin_percent"] == "20.0"
    cfo = observation("100", metric="cash_flow_operating", definition="Net CFO")
    capex = observation(
        "60", metric="capex", definition="Positive cash purchase of PPE and intangibles"
    )
    output = calculate_cashflow_metrics(cfo, capex)
    assert output["values"]["cfo_minus_capex"] == "40"
    assert "not automatically FCFF" in output["values"]["definition"]
    assert calculate_cashflow_metrics(cfo, capex | {"value": None})["status"] == "incomplete"
    assert calculate_margins(profit | {"period_start": None}, revenue)["status"] == "incomplete"


def test_comparison_formulas_are_specific_to_their_output_metric():
    previous = observation("100", period_end="2025-03-31", period_start="2024-04-01")
    current = observation("125", period_end="2026-03-31", period_start="2025-04-01")
    values = compare_periods(previous, current)["values"]
    assert values["absolute_change"] == "25"
    assert values["percentage_change"] == "25.00"
    assert values["formulas"] == {
        "absolute_change": "current - previous",
        "percentage_change": "(current - previous) / previous * 100",
    }
    assert values["formula"] == values["formulas"]["percentage_change"]


def test_cagr_and_ttm_reference_and_overlap_rejection():
    a = observation("100", period_end="2024-03-31", period_start="2023-04-01")
    b = observation("121", period_end="2026-03-31", period_start="2025-04-01")
    assert_close(calculate_cagr(a, b, "2")["values"]["cagr_percent"], "10")
    assert calculate_cagr(a, b, "5")["status"] == "incomplete"
    dates = [
        ("2025-01-01", "2025-03-31"),
        ("2025-04-01", "2025-06-30"),
        ("2025-07-01", "2025-09-30"),
        ("2025-10-01", "2025-12-31"),
    ]
    quarters = [
        observation(str(10 * (i + 1)), period_type="quarterly", period_start=start, period_end=end)
        for i, (start, end) in enumerate(dates)
    ]
    assert calculate_ttm(quarters)["values"]["total"] == "100"
    quarters[1]["period_start"] = "2025-03-30"
    assert calculate_ttm(quarters)["status"] == "incomplete"


def test_unit_conversion_has_trace_and_no_source_mutation():
    original = observation("12", unit="INR_crore")
    out = convert_units(original, "INR")
    assert out["fact"]["value"] == "120000000"
    assert out["fact"]["transformations"][0]["source_unit"] == "INR_crore"
    assert original["unit"] == "INR_crore"
    with pytest.raises(DomainError):
        convert_units(original | {"unit": None}, "INR")


@pytest.mark.parametrize(
    "value", [True, "NaN", "Infinity", "1e99999", "1e-99999", "0e-99999", "0." + "1" * 40]
)
def test_number_bounds_do_not_allow_nonfinite_or_unbounded_decimal_expansion(value):
    if value == "0e-99999":
        assert decimal(value) == 0
    else:
        with pytest.raises(DomainError):
            decimal(value)


def test_fact_mapping_preserves_original_fields_and_declares_unknown_context():
    record = {
        "operation": "bharatstock.get_financials",
        "operation_id": "fixture-result",
        "mode": "synthetic",
        "status": "success",
        "payload_kind": "rest_json",
        "receipt": {
            "arguments": {"ticker": "EXAMPLE", "exchange": "NSE"},
            "retrieved_at": "2026-11-15T10:00:00Z",
        },
        "payload": {
            "data": [
                {
                    "period_type": "annual",
                    "period_end_date": "2026-03-31",
                    "consolidation_type": "consolidated",
                    "revenue": 100,
                    "net_profit": 20,
                    "net_profit_attributable_to_owners": 15,
                    "eps": 2,
                    "eps_adjusted": 1,
                    "eps_adjustment_factor": 2,
                    "cash_flow_operating": None,
                    "capex": None,
                }
            ]
        },
    }
    unknown = prepare_financial_facts(record, None)
    assert all(f["unit"] is None for f in unknown["facts"])
    assert all(f["period_start"] is None for f in unknown["facts"])
    declared = prepare_financial_facts(record, "INR")
    by_metric = {f["metric"]: f for f in declared["facts"]}
    assert by_metric["net_profit"]["value"] == "20"
    assert by_metric["net_profit_attributable_to_owners"]["value"] == "15"
    assert by_metric["cash_flow_operating"]["value"] is None
    assert by_metric["eps_adjusted"]["value"] == "1"  # No additional division by the factor.
    assert by_metric["eps_adjusted"]["source"]["eps_adjustment_factor"] == 2
    assert by_metric["revenue"]["unit_origin"] == "caller_declared"


def test_dispatcher_rejects_unknown_parameters_and_facts_compatibility_unknowns():
    with pytest.raises(DomainError):
        calculate("finance.calculate_dcf", model() | {"invent_missing_data": True})
    assert check_compatibility([observation(), observation(unit=None)])["status"] == "incomplete"


def test_missing_start_is_acceptable_only_for_ratios_from_the_same_retained_row():
    cfo = observation(
        "100",
        metric="cash_flow_operating",
        definition="Net CFO",
        period_start=None,
        source={"row_reference": "retained-run:data[0]"},
    )
    capex = observation(
        "60",
        metric="capex",
        definition="Cash purchase PPE/intangibles",
        period_start=None,
        source={"row_reference": "retained-run:data[0]"},
    )
    assert calculate_cashflow_metrics(cfo, capex)["status"] == "success"
    assert (
        calculate_cashflow_metrics(
            cfo, capex | {"source": {"row_reference": "another-run:data[0]"}}
        )["status"]
        == "incomplete"
    )


def test_stub_reporting_period_is_blocked_and_unknown_duration_is_qualified():
    previous = observation("100")
    stub = observation("110", period_start="2025-10-01", period_end="2026-03-31")
    assert compare_periods(previous, stub)["status"] == "incomplete"
    unknown = stub | {"period_start": None}
    out = compare_periods(previous, unknown)
    assert out["status"] == "success"
    assert any("Period starts are unknown" in message for message in out["warnings"])


def test_cagr_rejects_subday_duration_before_unbounded_exponentiation():
    with pytest.raises(DomainError, match="at least one day"):
        calculate_cagr(observation("1e-24"), observation("1e24", period_end="2026-03-31"), "1e-24")
