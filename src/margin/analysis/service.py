"""Versioned local calculation catalog shared by Python and interface adapters."""

from __future__ import annotations

import copy
from decimal import DecimalException

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from margin.analysis import calculations, ratios
from margin.analysis.facts import FACT_SCHEMA, MONEY_UNITS, check_compatibility, convert_units
from margin.core.contracts import DomainError
from margin.finance import dcf

NUMBER = {"type": ["number", "string"], "maxLength": 64}


def obj(properties, required=None):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties) if required is None else required,
    }


MODEL_SCHEMA = obj(
    {
        "forecast_fcff": {"type": "array", "items": NUMBER, "minItems": 1, "maxItems": 20},
        "wacc": NUMBER,
        "terminal_growth": NUMBER,
        "debt": NUMBER,
        "cash": NUMBER,
        "other_equity_adjustments": NUMBER,
        "diluted_shares": {"anyOf": [NUMBER, {"type": "null"}]},
        "amount_unit": {"enum": list(MONEY_UNITS)},
        "valuation_date": {"type": "string", "format": "date"},
        "company_type": {"enum": ["non_financial"]},
    }
)
PAIR = {"previous": FACT_SCHEMA, "current": FACT_SCHEMA}
SPECS = {
    **{
        "finance." + name: (
            getattr(ratios, name),
            obj({"facts": {"type": "array", "items": FACT_SCHEMA, "minItems": 1, "maxItems": 60}}),
        )
        for name in [
            "calculate_balance_sheet_metrics",
            "calculate_cash_conversion",
            "calculate_profitability",
        ]
    },
    "finance.reconcile_facts": (
        ratios.reconcile_facts,
        obj({"left": FACT_SCHEMA, "right": FACT_SCHEMA}),
    ),
    "facts.check_compatibility": (
        check_compatibility,
        obj(
            {
                "facts": {"type": "array", "items": FACT_SCHEMA, "minItems": 2, "maxItems": 4},
                "purpose": {"enum": ["comparison", "ratio", "ttm"]},
            },
            ["facts"],
        ),
    ),
    "facts.convert_units": (
        convert_units,
        obj({"value": FACT_SCHEMA, "target_unit": {"enum": list(MONEY_UNITS)}}),
    ),
    "finance.compare_periods": (calculations.compare_periods, obj(PAIR)),
    "finance.calculate_margins": (
        calculations.calculate_margins,
        obj({"profit": FACT_SCHEMA, "revenue": FACT_SCHEMA}),
    ),
    "finance.calculate_cashflow_metrics": (
        calculations.calculate_cashflow_metrics,
        obj({"cfo": FACT_SCHEMA, "capex": FACT_SCHEMA}),
    ),
    "finance.calculate_cagr": (calculations.calculate_cagr, obj(PAIR | {"years": NUMBER})),
    "finance.calculate_ttm": (
        calculations.calculate_ttm,
        obj({"facts": {"type": "array", "items": FACT_SCHEMA, "minItems": 4, "maxItems": 4}}),
    ),
    "finance.calculate_fcff": (
        dcf.calculate_fcff,
        obj(
            {
                "ebit": NUMBER,
                "tax_rate": NUMBER,
                "depreciation": NUMBER,
                "capex": NUMBER,
                "change_in_working_capital": NUMBER,
                "amount_unit": {"enum": list(MONEY_UNITS)},
            }
        ),
    ),
    "finance.calculate_dcf": (dcf.calculate_dcf, MODEL_SCHEMA),
    "finance.dcf_sensitivity": (
        dcf.dcf_sensitivity,
        obj(
            {
                "model": MODEL_SCHEMA,
                "discount_rates": {"type": "array", "items": NUMBER, "minItems": 1, "maxItems": 9},
                "terminal_growth_rates": {
                    "type": "array",
                    "items": NUMBER,
                    "minItems": 1,
                    "maxItems": 9,
                },
            }
        ),
    ),
    "finance.run_scenarios": (
        dcf.run_scenarios,
        obj(
            {
                "model": MODEL_SCHEMA,
                "scenarios": {
                    "type": "object",
                    "minProperties": 1,
                    "maxProperties": 5,
                    "propertyNames": {"minLength": 1, "maxLength": 40},
                    "additionalProperties": obj(MODEL_SCHEMA["properties"], []),
                },
            }
        ),
    ),
}


def capabilities():
    return [
        {
            "function": name,
            "function_version": "1.0",
            "schema": copy.deepcopy(schema),
            "network": False,
            "provider_credits": 0,
            "note": "Explicit inputs; validation/arithmetic is not source verification.",
        }
        for name, (_, schema) in SPECS.items()
    ]


def calculate(operation, arguments):
    if not isinstance(operation, str) or operation not in SPECS:
        raise DomainError("unknown_function", "Choose an enabled local analysis function.")
    fn, schema = SPECS[operation]
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(arguments)
    except ValidationError:
        raise DomainError(
            "invalid_input",
            "Arguments do not match the local function schema; no coercion or default assumptions.",
        ) from None
    try:
        return fn(**copy.deepcopy(arguments))
    except (DecimalException, OverflowError):
        raise DomainError(
            "numeric_range", "The supplied calculation exceeds the supported numerical range."
        ) from None
