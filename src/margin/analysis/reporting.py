"""One deterministic reporting scale; raw calculation details stay separate."""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation, localcontext

from margin.analysis.facts import MONEY_UNITS
from margin.analysis.presentation import LABELS

REPORT_VERSION = "margin.company_report.v1"
RESULT_LABELS = {
    "margin_percent": "Profit margin (using the selected profit definition)",
    "absolute_change": "Absolute change",
    "percentage_change": "Percentage change",
    "cagr_percent": "CAGR",
    "years": "Elapsed years used for CAGR",
    "cfo_minus_capex": "Operating cash flow minus cash capex (not FCFF)",
    "capex_coverage": "Operating cash flow / cash capex",
    "total": "TTM total",
    "working_capital": "Working capital",
    "current_ratio": "Current assets / current liabilities",
    "current_assets_less_inventory_ratio": "Current assets less inventories / current liabilities",
    "cash_ratio": "Cash and cash equivalents / current liabilities",
    "gross_borrowings": "Reported gross borrowings (lease coverage follows provider fields)",
    "net_borrowings": "Reported borrowings less cash and cash equivalents",
    "borrowings_to_total_equity": "Reported gross borrowings / group total equity",
    "liabilities_to_assets": "Total liabilities / total assets",
    "cfo_margin_percent": "Operating cash flow margin",
    "cfo_to_group_profit": "Operating cash flow / group net profit",
    "capex_to_revenue_percent": "Cash capex / revenue",
    "cfo_less_capex_margin_percent": "CFO minus cash capex / revenue (not FCFF)",
    **{
        metric + "_margin_percent": label + " / revenue"
        for metric, label in LABELS.items()
        if metric
        in {
            "net_profit",
            "profit_from_continuing_operations",
            "net_profit_attributable_to_owners",
            "operating_profit",
            "ebitda",
        }
    },
}


def formatted_value(raw, unit):
    """Return an exact value and matching display unit, never inferred by magnitude."""
    target = "INR_crore" if unit in MONEY_UNITS else unit
    if unit not in {*MONEY_UNITS, "INR_per_share", "percent", "ratio", "years"}:
        return None, None, "Unavailable: reporting unit is unknown", "unavailable"
    if raw is None:
        return None, target, "Not available", "unavailable"
    try:
        if isinstance(raw, bool) or len(str(raw)) > 256:
            raise ValueError
        value = Decimal(str(raw))
        if (
            not value.is_finite()
            or (value and abs(value.adjusted()) > 96)
            or len(value.as_tuple().digits) > 128
        ):
            raise ValueError
        with localcontext() as context:
            context.prec = max(34, len(value.as_tuple().digits) + 8)
            context.rounding = ROUND_HALF_EVEN
            if unit in MONEY_UNITS:
                value = value * MONEY_UNITS[unit] / MONEY_UNITS["INR_crore"]
            if target == "INR_crore":
                display = f"₹{value:,.2f} crore"
            elif target == "INR_per_share":
                display = f"₹{value:,.2f} per share"
            elif target == "percent":
                display = f"{value:,.2f}%"
            elif target == "ratio":
                display = f"{value:,.2f}×"
            else:
                display = f"{value:,.6f} years"
        return format(value, "f"), target, display, "success"
    except (InvalidOperation, ValueError, TypeError):
        return None, target, "Unavailable: invalid reporting value", "unavailable"


def result_context(output, inputs, values):
    ends = sorted({item["period_end"] for item in inputs if item.get("period_end")})
    starts = {item.get("period_start") for item in inputs}
    types = {item.get("period_type") for item in inputs}
    start = next(iter(starts)) if len(starts) == 1 else None
    end = ends[0] if len(ends) == 1 else None
    kind = next(iter(types)) if len(types) == 1 else output.get("selection", {}).get("period_type")
    if output.get("function", "").endswith("_ttm") and "total" in values:
        start, end, kind = values.get("period_start"), values.get("period_end"), "ttm"
    return {
        "period_type": kind,
        "period_start": start,
        "period_end": end,
        "comparison_period_ends": ends if end is None and len(ends) > 1 else [],
    }


def numeric_row(kind, metric, label, raw, unit, period, status="success", **extra):
    value, target, display, rendered_status = formatted_value(raw, unit)
    if status != "success":
        value, display = None, f"Withheld ({status})"
    return {
        "kind": kind,
        "metric": metric,
        "label": label,
        "value": value,
        "unit": target,
        "display": display,
        "status": status if status != "success" else rendered_status,
        **period,
        **extra,
    }


def company_report(output, details):
    """Formatting only: no inference, source fetching, fact repair or final-prose audit."""
    inputs, values = details.get("inputs", []), details.get("values", {})
    rows = []
    for item in inputs:
        context = {key: item.get(key) for key in ("period_type", "period_start", "period_end")}
        rows.append(
            numeric_row(
                "input",
                item["metric"],
                item["definition"],
                item.get("value"),
                item.get("unit"),
                context,
            )
        )
    context = result_context(output, inputs, values)
    components = details.get("components", {})
    units = {
        "margin_percent": "percent",
        "percentage_change": "percent",
        "cagr_percent": "percent",
        "years": "years",
        "capex_coverage": "ratio",
        **{key: values.get("unit") for key in ("absolute_change", "cfo_minus_capex", "total")},
    }
    unmapped = []
    metadata = {
        "profit_definition",
        "formula",
        "unit",
        "definition",
        "period_start",
        "period_end",
        "periods_returned",
        "null_fields_latest_period",
        "calculation_readiness",
        "valuation_readiness",
    }
    for metric in dict.fromkeys([*values, *components]):
        if metric in metadata:
            continue
        label = RESULT_LABELS.get(metric)
        if not label:
            unmapped.append(metric)
            continue
        component = components.get(metric, {})
        extra = {
            k: component[k]
            for k in ("formula", "issue", "missing_fields", "requires_positive")
            if k in component
        }
        if not component and values.get("formula"):
            extra["formula"] = values["formula"]
        if metric == "margin_percent" and values.get("profit_definition"):
            extra["profit_definition"] = values["profit_definition"]
            label = "Margin using " + values["profit_definition"]
        if metric in {"total", "absolute_change", "percentage_change", "cagr_percent"}:
            extra["input_metric"] = output.get("selection", {}).get("metric")
            measure = LABELS.get(extra["input_metric"], extra["input_metric"] or "selected metric")
            label += " in " + measure
        if metric == "cfo_minus_capex":
            extra["definition"] = values.get("definition")
        rows.append(
            numeric_row(
                "result",
                metric,
                label,
                values.get(metric),
                component.get("unit", units.get(metric)),
                context,
                component.get("status", "success"),
                **extra,
            )
        )

    readiness = values.get("calculation_readiness", {})
    readiness_rows = [
        {
            "function": function,
            "status": item["status"],
            "issues": item.get("issues", []),
            "components": item.get("components", {}),
        }
        for function, item in readiness.items()
    ]
    ends = sorted({item["period_end"] for item in inputs if item.get("period_end")}) or values.get(
        "periods_returned", []
    )
    report = {
        "contract_version": REPORT_VERSION,
        "rows": rows,
        "period_ends": ends,
    }
    if readiness_rows:
        report["readiness"] = readiness_rows
        report["valuation_readiness"] = values.get("valuation_readiness", {})
        report["null_fields_latest_period"] = values.get("null_fields_latest_period", [])
    if unmapped:
        report["unmapped_fields"] = unmapped
    return report
