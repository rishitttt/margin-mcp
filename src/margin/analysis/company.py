"""Bounded company calculations over one explicit retained financial response."""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal, localcontext

from jsonschema import Draft202012Validator, ValidationError

from margin.analysis.facts import (
    FIELDS,
    MONEY_UNITS,
    STOCK_FIELDS,
    TTM_FLOW_METRICS,
    prepare_financial_facts,
)
from margin.analysis.service import calculate, obj
from margin.core.contracts import DomainError

FUNCTIONS = {
    "finance.company_data_readiness": "Which fields support profitability, cash-conversion and liquidity across groups in ONE financial response; no forecast assumptions or numeric report rows",
    "finance.company_balance_sheet_metrics": "Liquidity and borrowings; current-assets-less-inventories ratio is not a fully adjusted quick ratio",
    "finance.company_cash_conversion": "CFO ratios and capex intensity; not days-based cash-conversion-cycle metrics",
    "finance.company_profitability": "Defined group/owners/operating/EBITDA margins",
    "finance.company_margins": "Latest-period continuing-profit margin when supplied, otherwise reported group-profit margin with scope caveat",
    "finance.company_cashflow_metrics": "Latest-period operating cash flow minus capex and coverage",
    "finance.company_growth": "Absolute and percentage change between the latest two returned periods; not a TTM sum",
    "finance.company_cagr": "CAGR between two returned annual endpoints",
    "finance.company_ttm": "Sum of four eligible quarterly flows, not growth or balance-sheet stocks; requires continuity",
}
SCHEMA = obj(
    {
        "ticker": {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9&_.-]{0,39}$"},
        "exchange": {"enum": ["NSE", "BSE"]},
        "period_type": {"enum": ["annual", "quarterly"]},
        "basis": {"enum": ["consolidated", "standalone"]},
        "money_unit": {"enum": ["auto", None, *MONEY_UNITS]},
        "metric": {"enum": list(FIELDS)},
        "source_operation_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "source_run_id": {"type": ["string", "null"], "maxLength": 100},
    }
)


def default_period(function):
    return "quarterly" if function == "finance.company_ttm" else "annual"


def function_constraints():
    return [
        {
            "if": {"properties": {"function": {"const": name}}, "required": ["function"]},
            "then": {"properties": properties},
        }
        for name, properties in [
            (
                "finance.company_ttm",
                {
                    "period_type": {"const": "quarterly"},
                    "metric": {"enum": [m for m in FIELDS if m in TTM_FLOW_METRICS]},
                },
            ),
            ("finance.company_cagr", {"period_type": {"const": "annual"}}),
        ]
    ]


def planning_capabilities():
    properties = {
        k: copy.deepcopy(v)
        for k, v in SCHEMA["properties"].items()
        if k not in {"source_run_id", "source_operation_id"}
    }
    properties.update(
        source=obj(
            {
                "run_id": {"type": "string", "minLength": 1, "maxLength": 100},
                "operation_id": {"type": "string", "minLength": 1, "maxLength": 100},
            }
        ),
        fetch_missing={"type": "boolean", "default": False},
    )
    rows = []
    for name, description in FUNCTIONS.items():
        inputs = copy.deepcopy(properties)
        inputs["period_type"]["default"] = default_period(name)
        if name in {"finance.company_ttm", "finance.company_cagr"}:
            inputs["period_type"]["enum"] = [default_period(name)]
        if name == "finance.company_ttm":
            inputs["metric"]["enum"] = [m for m in FIELDS if m in TTM_FLOW_METRICS]
        rows.append(
            {
                "function": name,
                "description": description,
                "planning_schema": obj(
                    inputs | {"function": {"const": name}}, ["function", "ticker", "exchange"]
                ),
                "defaults": {
                    "period_type": default_period(name),
                    "basis": "consolidated",
                    "money_unit": "auto",
                    "metric": "revenue",
                    "fetch_missing": False,
                },
                "note": "Reuse a matching retained source or explicitly preview one missing financials request.",
            }
        )
    return rows


def validate(function, arguments):
    if not isinstance(function, str) or function not in FUNCTIONS:
        raise DomainError("unknown_function", "Choose a supported company financial function.")
    try:
        Draft202012Validator(SCHEMA).validate(arguments)
    except ValidationError:
        raise DomainError(
            "invalid_input", "Check the company financial function arguments."
        ) from None
    if function == "finance.company_cagr" and arguments["period_type"] != "annual":
        raise DomainError("invalid_input", "Company CAGR requires annual financials.")
    if function == "finance.company_ttm" and arguments["period_type"] != "quarterly":
        raise DomainError("invalid_input", "Company TTM requires quarterly financials.")
    if (
        function == "finance.company_ttm"
        and arguments.get("metric", "revenue") not in TTM_FLOW_METRICS
    ):
        raise DomainError(
            "invalid_input",
            "TTM requires monetary quarterly flows, not EPS, ratios or balance-sheet stocks.",
        )


def calculate_company(function, arguments, source):
    validate(function, arguments)
    selectors = source.get("receipt", {}).get("arguments", {})
    if any(selectors.get(k) != arguments[k] for k in ("ticker", "exchange", "period_type")):
        raise DomainError(
            "incompatible_source", "Financial source belongs to a different listing or period type."
        )
    prepared = prepare_financial_facts(source, arguments["money_unit"])
    facts = [
        f
        for f in prepared["facts"]
        if f["basis"] == arguments["basis"]
        and f["source"]["reported_period_type"] == arguments["period_type"]
    ]
    dates = sorted({f["period_end"] for f in facts if f["period_end"]}, reverse=True)
    issues = []

    def pick(metric, end):
        matches = [f for f in facts if f["metric"] == metric and f["period_end"] == end]
        if len(matches) != 1:
            issues.append(
                f"Need one unambiguous {metric} observation for {end} / {arguments['basis']}."
            )
            return None
        return matches[0]

    needed = 4 if function.endswith("_ttm") else 2 if function.endswith(("_growth", "_cagr")) else 1
    if len(dates) < needed:
        issues.append(
            f"Need {needed} returned {arguments['basis']} {arguments['period_type']} periods; found {len(dates)}. No extra pages were fetched."
        )
    inputs = {}
    target = None
    if not issues and function.endswith("_data_readiness"):
        checks = {}
        for name in FUNCTIONS:
            if (
                name == function
                or (name.endswith("_ttm") and arguments["period_type"] != "quarterly")
                or (name.endswith("_cagr") and arguments["period_type"] != "annual")
            ):
                continue
            try:
                assessed = calculate_company(name, arguments, source)
            except DomainError as exc:
                if exc.code != "invalid_input":
                    raise
                checks[name] = {"status": "incomplete", "issues": [exc.message]}
                continue
            checks[name] = {
                k: assessed[k] for k in ["status", "issues", "components"] if k in assessed
            }
        missing = sorted(
            {f["metric"] for f in facts if f["period_end"] == dates[0] and f["value"] is None}
        )
        output = {
            "status": "success",
            "issues": [],
            "values": {
                "periods_returned": dates,
                "null_fields_latest_period": missing,
                "calculation_readiness": checks,
                "valuation_readiness": {
                    "status": "needs_explicit_inputs",
                    "required": [
                        "reviewed EBIT definition",
                        "tax rate",
                        "noncash operating working-capital changes",
                        "FCFF forecasts",
                        "WACC",
                        "terminal growth",
                        "debt/cash/equity bridge",
                        "diluted share count for per-share output",
                    ],
                    "note": "Reported operating profit is not automatically EBIT; historical cash flow is not a forecast.",
                },
            },
        }
    elif not issues:
        if function.endswith(("_balance_sheet_metrics", "_cash_conversion", "_profitability")):
            target = "finance.calculate_" + function.removeprefix("finance.company_")
            metrics = (
                set(STOCK_FIELDS)
                if function.endswith("_balance_sheet_metrics")
                else {"revenue", "net_profit", "cash_flow_operating", "capex"}
                if function.endswith("_cash_conversion")
                else {
                    "revenue",
                    "net_profit",
                    "profit_from_continuing_operations",
                    "net_profit_attributable_to_owners",
                    "operating_profit",
                    "ebitda",
                }
            )
            inputs = {
                "facts": [
                    f for f in facts if f["period_end"] == dates[0] and f["metric"] in metrics
                ]
            }
            if not inputs["facts"]:
                issues.append("No eligible fields returned for this metric group.")
        elif function.endswith("_margins"):
            target = "finance.calculate_margins"
            continuing = [
                f
                for f in facts
                if f["metric"] == "profit_from_continuing_operations"
                and f["period_end"] == dates[0]
                and f["value"] is not None
            ]
            inputs = {
                "profit": pick(
                    "profit_from_continuing_operations" if continuing else "net_profit", dates[0]
                ),
                "revenue": pick("revenue", dates[0]),
            }
        elif function.endswith("_cashflow_metrics"):
            target = "finance.calculate_cashflow_metrics"
            inputs = {
                "cfo": pick("cash_flow_operating", dates[0]),
                "capex": pick("capex", dates[0]),
            }
        elif function.endswith("_ttm"):
            target = "finance.calculate_ttm"
            inputs = {"facts": [pick(arguments["metric"], end) for end in dates[:4]]}
        else:
            target = (
                "finance.calculate_cagr"
                if function.endswith("_cagr")
                else "finance.compare_periods"
            )
            inputs = {
                "previous": pick(arguments["metric"], dates[1]),
                "current": pick(arguments["metric"], dates[0]),
            }
            if function.endswith("_cagr"):
                current, previous = date.fromisoformat(dates[0]), date.fromisoformat(dates[1])
                anniversary = (current.month, current.day) == (previous.month, previous.day)
                with localcontext() as context:
                    context.prec = 34
                    inputs["years"] = str(
                        Decimal(current.year - previous.year)
                        if anniversary
                        else Decimal((current - previous).days) / Decimal("365.25")
                    )
    if not function.endswith("_data_readiness") or issues:
        output = (
            calculate(target, inputs)
            if not issues
            else {"status": "incomplete", "issues": issues, "values": {}}
        )
    output["calculation_function"] = target
    output["function"] = function
    output["function_version"] = "1.0"
    output["selection"] = {
        k: arguments[k]
        for k in ("ticker", "exchange", "period_type", "basis", "metric", "money_unit")
    }
    output["source"] = {
        "run_id": arguments["source_run_id"],
        "operation_id": source["operation_id"],
        "retrieved_at": source["receipt"].get("retrieved_at"),
        "verification": "unverified",
    }
    output["warnings"] = [
        *output.get("warnings", []),
        *prepared["warnings"],
        "Latest means latest within this bounded response; not independently established as the latest filing.",
    ]
    if function.endswith("_cagr"):
        output["warnings"].append(
            "CAGR duration uses exact calendar-anniversary years when endpoints share month/day; otherwise actual days / 365.25, explicitly a day-count convention."
        )
    if function.endswith("_cagr"):
        output["warnings"].append(
            "Elapsed years are derived from returned endpoint dates / 365.25; two annual endpoints are not a long-term growth history."
        )
    return output
