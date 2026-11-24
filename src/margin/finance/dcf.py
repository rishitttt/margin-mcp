"""Two-stage, annual end-of-year FCFF model with an explicit equity bridge."""

from __future__ import annotations

import copy
from datetime import date
from decimal import localcontext

from margin.analysis.calculations import result
from margin.analysis.facts import MONEY_UNITS, decimal
from margin.core.contracts import DomainError


def calculate_fcff(ebit, tax_rate, depreciation, capex, change_in_working_capital, amount_unit):
    e, tax, da, investment, wc = [
        decimal(v, label)
        for v, label in zip(
            [ebit, tax_rate, depreciation, capex, change_in_working_capital],
            ["ebit", "tax_rate", "depreciation", "capex", "change_in_working_capital"],
            strict=True,
        )
    ]
    if amount_unit not in MONEY_UNITS or not 0 <= tax <= 1 or da < 0 or investment < 0:
        raise DomainError(
            "invalid_input",
            "FCFF needs a known INR scale, decimal tax rate in [0, 1], and nonnegative depreciation/capex.",
        )
    with localcontext() as ctx:
        ctx.prec = 34
        fcff = e * (1 - tax) + da - investment - wc
    return result(
        "finance.calculate_fcff",
        {
            "ebit": e,
            "tax_rate": tax,
            "depreciation": da,
            "capex": investment,
            "change_in_working_capital": wc,
            "amount_unit": amount_unit,
        },
        {
            "fcff": fcff,
            "unit": amount_unit,
            "formula": "EBIT * (1 - tax_rate) + depreciation - capex - increase_in_noncash_operating_working_capital",
        },
    )


def calculate_dcf(
    forecast_fcff,
    wacc,
    terminal_growth,
    debt,
    cash,
    other_equity_adjustments,
    diluted_shares,
    amount_unit,
    valuation_date,
    company_type,
):
    if company_type != "non_financial":
        raise DomainError(
            "unsupported_model", "The initial FCFF template is for non-financial companies only."
        )
    if (
        amount_unit not in MONEY_UNITS
        or not isinstance(forecast_fcff, list)
        or not 1 <= len(forecast_fcff) <= 20
    ):
        raise DomainError(
            "invalid_input",
            "DCF requires a known INR scale and one to twenty annual forecast cash flows.",
        )
    try:
        if not isinstance(valuation_date, str):
            raise ValueError
        date.fromisoformat(valuation_date)
    except ValueError:
        raise DomainError("invalid_input", "Supply a valid ISO valuation date.") from None
    flows = [decimal(v, "forecast_fcff") for v in forecast_fcff]
    rate, growth, borrowings, cash_value, adjustment = [
        decimal(v, label)
        for v, label in zip(
            [wacc, terminal_growth, debt, cash, other_equity_adjustments],
            ["wacc", "terminal_growth", "debt", "cash", "other_equity_adjustments"],
            strict=True,
        )
    ]
    shares = None if diluted_shares is None else decimal(diluted_shares, "diluted_shares")
    if not 0 < rate <= 1 or not -1 < growth < rate:
        raise DomainError(
            "invalid_input", "Use decimal rates: 0 < WACC <= 1 and -1 < terminal growth < WACC."
        )
    if borrowings < 0 or cash_value < 0 or shares is not None and shares <= 0:
        raise DomainError(
            "invalid_input",
            "Debt/cash must be nonnegative; supplied diluted share count must be positive.",
        )
    if flows[-1] <= 0:
        raise DomainError(
            "unsupported_terminal",
            "A nonpositive terminal-year FCFF needs another model; no positive terminal value is fabricated.",
        )
    with localcontext() as ctx:
        ctx.prec = 34
        rows = [
            {
                "year": t,
                "fcff": value,
                "discount_factor": (1 + rate) ** t,
                "present_value": value / (1 + rate) ** t,
            }
            for t, value in enumerate(flows, 1)
        ]
        explicit_pv = sum(r["present_value"] for r in rows)
        terminal_cashflow = flows[-1] * (1 + growth)
        terminal_value = terminal_cashflow / (rate - growth)
        terminal_pv = terminal_value / (1 + rate) ** len(flows)
        enterprise = explicit_pv + terminal_pv
        equity = enterprise - borrowings + cash_value + adjustment
        values = {
            "forecast": rows,
            "forecast_present_value": explicit_pv,
            "terminal_cashflow": terminal_cashflow,
            "terminal_value": terminal_value,
            "terminal_present_value": terminal_pv,
            "terminal_contribution_percent": terminal_pv / enterprise * 100 if enterprise else None,
            "enterprise_value": enterprise,
            "equity_value": equity,
            "amount_unit": amount_unit,
            "value_per_share_inr": equity * MONEY_UNITS[amount_unit] / shares if shares else None,
            "equity_bridge": "enterprise_value - debt + cash + other_equity_adjustments",
            "discount_convention": "annual_end_of_year; first supplied cash flow at year 1",
            "terminal_formula": "final_forecast_fcff * (1 + terminal_growth) / (wacc - terminal_growth)",
        }
    inputs = {
        "forecast_fcff": flows,
        "wacc": rate,
        "terminal_growth": growth,
        "debt": borrowings,
        "cash": cash_value,
        "other_equity_adjustments": adjustment,
        "diluted_shares": shares,
        "amount_unit": amount_unit,
        "valuation_date": valuation_date,
        "company_type": company_type,
        "input_origin": "explicit caller-supplied forecasts and assumptions; no automatic provider population",
    }
    out = result("finance.calculate_dcf", inputs, values)
    if shares is None:
        out["warnings"].append("Per-share value unavailable: no diluted share count supplied.")
    if equity < 0:
        out["warnings"].append(
            "The supplied bridge produces negative equity; the result has not been floored to zero."
        )
    out["warnings"].append(
        "Assumption-dependent valuation, not an observed price or independently verified company valuation."
    )
    return out


def dcf_sensitivity(model, discount_rates, terminal_growth_rates):
    if not isinstance(model, dict) or not all(
        isinstance(v, list) and 1 <= len(v) <= 9 for v in (discount_rates, terminal_growth_rates)
    ):
        raise DomainError(
            "invalid_input",
            "Sensitivity grids require one to nine rates per axis (at most 81 cells).",
        )
    calculate_dcf(**model)
    rates = [decimal(v, "discount_rates") for v in discount_rates]
    growths = [decimal(v, "terminal_growth_rates") for v in terminal_growth_rates]
    cells = []
    for rate in rates:
        row = []
        for growth in growths:
            try:
                value = calculate_dcf(**(model | {"wacc": rate, "terminal_growth": growth}))[
                    "values"
                ]
                row.append(
                    {
                        "status": "success",
                        **{
                            k: value[k]
                            for k in ("enterprise_value", "equity_value", "value_per_share_inr")
                        },
                    }
                )
            except DomainError as e:
                row.append({"status": "invalid", "error": {"code": e.code, "message": e.message}})
        cells.append(row)
    return result(
        "finance.dcf_sensitivity",
        {"model": model, "discount_rates": rates, "terminal_growth_rates": growths},
        {"cells": cells, "amount_unit": model["amount_unit"]},
    )


def run_scenarios(model, scenarios):
    if not isinstance(scenarios, dict) or not 1 <= len(scenarios) <= 5:
        raise DomainError("invalid_input", "Supply one to five explicit named scenario overrides.")
    calculate_dcf(**model)
    outputs = {}
    for name, overrides in scenarios.items():
        if (
            not isinstance(name, str)
            or not 1 <= len(name) <= 40
            or not isinstance(overrides, dict)
            or set(overrides) - set(model)
        ):
            raise DomainError(
                "invalid_input", "Scenario names/overrides must match the explicit model contract."
            )
        try:
            outputs[name] = calculate_dcf(**(copy.deepcopy(model) | overrides))
        except DomainError as e:
            outputs[name] = {"status": "invalid", "error": {"code": e.code, "message": e.message}}
    return result("finance.run_scenarios", {"model": model, "scenarios": scenarios}, outputs)
