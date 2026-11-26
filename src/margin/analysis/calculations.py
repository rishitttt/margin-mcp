"""Pure financial comparisons. Decimal outputs are strings, not binary floats."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, localcontext

from margin.analysis.facts import (
    MONEY_UNITS,
    TTM_FLOW_METRICS,
    VERSION,
    check_compatibility,
    decimal,
    fact,
    wire,
)
from margin.core.contracts import DomainError


def result(name, inputs, values=None, issues=(), status=None):
    return wire(
        {
            "function": name,
            "function_version": VERSION,
            "status": status or ("incomplete" if issues else "success"),
            "inputs": inputs,
            "values": values or {},
            "issues": list(issues),
            "precision": "34 significant digits; exact decimal strings; displayed rounding is separate",
            "warnings": ["Input validity and arithmetic do not independently verify source facts."],
        }
    )


def compare_periods(previous, current):
    a, b = fact(previous), fact(current)
    issues = check_compatibility([previous, current])["issues"]
    if a["period_end"] and b["period_end"] and a["period_end"] >= b["period_end"]:
        issues.append("Current reporting period must follow the previous period.")
    if issues:
        return result("finance.compare_periods", [a, b], issues=issues)
    with localcontext() as ctx:
        ctx.prec = 34
        delta = b["value"] - a["value"]
        percent = delta / a["value"] * 100 if a["value"] > 0 else None
    output = result(
        "finance.compare_periods",
        [a, b],
        {
            "absolute_change": delta,
            "percentage_change": percent,
            "unit": a["unit"],
            "formula": "(current - previous) / previous * 100",
            "formulas": {
                "absolute_change": "current - previous",
                "percentage_change": "(current - previous) / previous * 100",
            },
        },
        issues=["Percentage growth is not meaningful for a nonpositive baseline."]
        if percent is None
        else (),
        status="not_meaningful" if percent is None else "success",
    )

    if not a.get("period_start") or not b.get("period_start"):
        output["warnings"].append(
            "Period starts are unknown; comparison uses declared period types/ends. Review stub periods and reporting-duration changes."
        )
    return output


def calculate_margins(profit, revenue):
    a, b = fact(profit), fact(revenue)
    issues = check_compatibility([profit, revenue], "ratio")["issues"]
    if (
        a["metric"]
        not in {
            "net_profit",
            "net_profit_attributable_to_owners",
            "profit_from_continuing_operations",
            "operating_profit",
            "ebitda",
            "gross_profit",
            "ebit",
        }
        or b["metric"] != "revenue"
    ):
        issues.append("Select an explicitly defined profit measure and revenue.")
    if a["unit"] not in MONEY_UNITS:
        issues.append("Profit/revenue must use an established monetary scale.")
    if (
        a["metric"] in {"net_profit", "net_profit_attributable_to_owners"}
        and a.get("source", {}).get("continuing_profit_differs") is True
    ):
        issues.append(
            "Group/owners profit differs in scope from continuing profit; select aligned continuing profit or establish reporting scope before calculating a margin."
        )
    if issues:
        return result("finance.calculate_margins", [a, b], issues=issues)
    if b["value"] <= 0:
        return result(
            "finance.calculate_margins",
            [a, b],
            issues=["Positive revenue is required."],
            status="not_meaningful",
        )
    with localcontext() as ctx:
        ctx.prec = 34
        margin = a["value"] / b["value"] * 100
    return result(
        "finance.calculate_margins",
        [a, b],
        {
            "margin_percent": margin,
            "profit_definition": a["definition"],
            "formula": "profit / revenue * 100",
        },
    )


def calculate_cashflow_metrics(cfo, capex):
    a, b = fact(cfo), fact(capex)
    issues = check_compatibility([cfo, capex], "ratio")["issues"]
    if (
        a["metric"] != "cash_flow_operating"
        or b["metric"] != "capex"
        or a["unit"] not in MONEY_UNITS
    ):
        issues.append("Select operating cash flow and explicitly defined monetary capex.")
    if issues:
        return result("finance.calculate_cashflow_metrics", [a, b], issues=issues)
    if b["value"] < 0:
        raise DomainError(
            "invalid_input",
            "Capex must be supplied as a positive outflow; review the source sign convention.",
        )
    with localcontext() as ctx:
        ctx.prec = 34
        values = {
            "cfo_minus_capex": a["value"] - b["value"],
            "capex_coverage": a["value"] / b["value"] if b["value"] else None,
            "unit": a["unit"],
            "definition": "Reported CFO minus cash capex; not automatically FCFF.",
        }
    return result("finance.calculate_cashflow_metrics", [a, b], values)


def calculate_cagr(previous, current, years):
    a, b = fact(previous), fact(current)
    duration = decimal(years, "years")
    if not Decimal(1) / 366 <= duration <= 100:
        raise DomainError(
            "invalid_input",
            "CAGR requires an explicit duration of at least one day and at most 100 years.",
        )
    issues = check_compatibility([previous, current])["issues"]
    if a["period_end"] and b["period_end"]:
        days = (date.fromisoformat(b["period_end"]) - date.fromisoformat(a["period_end"])).days
        if days <= 0 or abs(Decimal(days) / Decimal("365.25") - duration) > Decimal("0.02"):
            issues.append(
                "Explicit elapsed years do not match the reporting-period endpoints (seven-day tolerance)."
            )
    if issues:
        return result("finance.calculate_cagr", [a, b], issues=issues)
    if a["value"] <= 0 or b["value"] <= 0:
        return result(
            "finance.calculate_cagr",
            [a, b],
            issues=["CAGR requires positive endpoints."],
            status="not_meaningful",
        )
    with localcontext() as ctx:
        ctx.prec = 34
        growth = ((b["value"] / a["value"]) ** (Decimal(1) / duration) - 1) * 100
    return result(
        "finance.calculate_cagr",
        [a, b],
        {
            "cagr_percent": growth,
            "years": duration,
            "formula": "((current / previous) ** (1 / years) - 1) * 100",
        },
    )


def calculate_ttm(facts):
    if not isinstance(facts, list) or len(facts) != 4:
        raise DomainError("invalid_input", "TTM needs exactly four explicit quarterly flow facts.")
    items = [fact(v) for v in facts]
    issues = check_compatibility(facts, "ttm")["issues"]
    if any(
        v["metric"] not in TTM_FLOW_METRICS
        or v["period_type"] != "quarterly"
        or v["unit"] not in MONEY_UNITS
        for v in items
    ):
        issues.append(
            "TTM accepts monetary quarterly flows, not EPS, ratios, balance-sheet stocks or cumulative YTD data."
        )
    if any(not v.get("period_start") for v in items):
        issues.append("All four quarterly start dates must be established; dates are not inferred.")
    if any(
        v.get("source", {}).get("reported_period_days") is not None
        or v.get("source", {}).get("filed_period_days") is not None
        for v in items
    ):
        issues.append(
            "Longer or provider-derived reporting periods require separate review before TTM."
        )
    if issues:
        return result("finance.calculate_ttm", items, issues=issues)
    items.sort(key=lambda v: v["period_end"])
    for index, value in enumerate(items):
        start, end = (
            date.fromisoformat(value["period_start"]),
            date.fromisoformat(value["period_end"]),
        )
        if not 80 <= (end - start).days <= 100:
            issues.append(
                "Each observation must span a single quarter, not a YTD cumulative period."
            )
        if index and start != date.fromisoformat(items[index - 1]["period_end"]) + timedelta(
            days=1
        ):
            issues.append("Quarterly observations overlap or have a gap.")
    if issues:
        return result("finance.calculate_ttm", items, issues=issues)
    with localcontext() as ctx:
        ctx.prec = 34
        total = sum(v["value"] for v in items)
    return result(
        "finance.calculate_ttm",
        items,
        {
            "total": total,
            "unit": items[0]["unit"],
            "period_start": items[0]["period_start"],
            "period_end": items[-1]["period_end"],
            "formula": "sum of four non-overlapping quarterly flows",
        },
    )
