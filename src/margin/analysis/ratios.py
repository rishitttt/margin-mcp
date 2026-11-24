"""Small, defined metric groups; missing components never become zero."""

from decimal import localcontext

from margin.analysis.calculations import result
from margin.analysis.facts import MONEY_UNITS, fact
from margin.core.contracts import DomainError


def aligned(facts, stock=False):
    if not isinstance(facts, list) or not 1 <= len(facts) <= 60:
        raise DomainError("invalid_input", "Supply one to sixty typed facts.")
    items = [fact(f) for f in facts]
    issues = []
    for key in ("issuer", "basis", "period_type", "period_end", "unit"):
        if any(v.get(key) is None for v in items) or len({v.get(key) for v in items}) != 1:
            issues.append(f"Same established {key} is required.")
    if any(v["unit"] not in MONEY_UNITS for v in items):
        issues.append("Use one established monetary scale; convert explicitly before calculating.")
    if stock and any(v["period_type"] != "instant" for v in items):
        issues.append("Balance-sheet metrics require point-in-time facts.")
    if not stock:
        if any(v["period_type"] not in {"annual", "quarterly", "ttm"} for v in items):
            issues.append("Flow metrics require reporting-period flows.")
        starts = {v.get("period_start") for v in items}
        rows = {v.get("source", {}).get("row_reference") for v in items}
        if len(starts) != 1 or (None in starts and (len(rows) != 1 or None in rows)):
            issues.append("Use aligned periods or fields from the exact same retained row.")
    metrics = [v["metric"] for v in items]
    if len(set(metrics)) != len(metrics):
        issues.append("Duplicate metric observations are ambiguous.")
    return items, {v["metric"]: v["value"] for v in items}, issues


def group(name, facts, specs, stock=False):
    items, fields, issues = aligned(facts, stock)
    if issues:
        return result(name, items, issues=issues)
    values, components = {}, {}
    with localcontext() as ctx:
        ctx.prec = 34
        for metric, required, formula, fn, positive in specs:
            unit = (
                "percent"
                if metric.endswith("_percent")
                else items[0]["unit"]
                if metric in {"working_capital", "gross_borrowings", "net_borrowings"}
                else "ratio"
            )
            missing = [k for k in required if fields.get(k) is None]
            invalid = [k for k in positive if fields.get(k) is not None and fields[k] <= 0]
            if any(
                f["metric"] in required
                and f["metric"] in {"net_profit", "net_profit_attributable_to_owners"}
                and f.get("source", {}).get("continuing_profit_differs") is True
                for f in items
            ):
                components[metric] = {
                    "status": "needs_scope_review",
                    "formula": formula,
                    "unit": unit,
                    "issue": "Group/owners profit differs from continuing profit; establish aligned scope before using this ratio.",
                }
                continue
            if missing or invalid:
                components[metric] = {
                    "status": "incomplete" if missing else "not_meaningful",
                    "missing_fields": missing,
                    "requires_positive": invalid,
                    "formula": formula,
                    "unit": unit,
                }
                continue
            values[metric] = fn(fields)
            components[metric] = {"status": "success", "formula": formula, "unit": unit}
    output = result(
        name,
        items,
        values,
        status="success" if len(values) == len(specs) else "partial" if values else "incomplete",
    )
    output["components"] = components
    output["amount_unit"] = items[0]["unit"]
    if any(
        v.get("source", {}).get("statement_format") in {"bank", "nbfc", "insurer"} for v in items
    ):
        output["warnings"].append(
            "These are generic accounting metrics, not bank/insurer regulatory adequacy or sector valuation measures."
        )
    return output


BALANCE = [
    (
        "working_capital",
        ["current_assets", "current_liabilities"],
        "current_assets - current_liabilities",
        lambda f: f["current_assets"] - f["current_liabilities"],
        [],
    ),
    (
        "current_ratio",
        ["current_assets", "current_liabilities"],
        "current_assets / current_liabilities",
        lambda f: f["current_assets"] / f["current_liabilities"],
        ["current_liabilities"],
    ),
    (
        "current_assets_less_inventory_ratio",
        ["current_assets", "inventories", "current_liabilities"],
        "(current_assets - inventories) / current_liabilities; not a fully adjusted quick ratio",
        lambda f: (f["current_assets"] - f["inventories"]) / f["current_liabilities"],
        ["current_liabilities"],
    ),
    (
        "cash_ratio",
        ["cash_and_cash_equivalents", "current_liabilities"],
        "cash_and_cash_equivalents / current_liabilities",
        lambda f: f["cash_and_cash_equivalents"] / f["current_liabilities"],
        ["current_liabilities"],
    ),
    (
        "gross_borrowings",
        ["borrowings_current", "borrowings_non_current"],
        "borrowings_current + borrowings_non_current; lease coverage follows provider fields",
        lambda f: f["borrowings_current"] + f["borrowings_non_current"],
        [],
    ),
    (
        "net_borrowings",
        ["borrowings_current", "borrowings_non_current", "cash_and_cash_equivalents"],
        "gross_borrowings - cash_and_cash_equivalents",
        lambda f: (
            f["borrowings_current"] + f["borrowings_non_current"] - f["cash_and_cash_equivalents"]
        ),
        [],
    ),
    (
        "borrowings_to_total_equity",
        ["borrowings_current", "borrowings_non_current", "total_equity"],
        "gross_borrowings / group_total_equity",
        lambda f: (f["borrowings_current"] + f["borrowings_non_current"]) / f["total_equity"],
        ["total_equity"],
    ),
    (
        "liabilities_to_assets",
        ["total_liabilities", "total_assets"],
        "total_liabilities / total_assets",
        lambda f: f["total_liabilities"] / f["total_assets"],
        ["total_assets"],
    ),
]
CONVERSION = [
    (
        "cfo_margin_percent",
        ["cash_flow_operating", "revenue"],
        "CFO / revenue * 100",
        lambda f: f["cash_flow_operating"] / f["revenue"] * 100,
        ["revenue"],
    ),
    (
        "cfo_to_group_profit",
        ["cash_flow_operating", "net_profit"],
        "CFO / group net profit",
        lambda f: f["cash_flow_operating"] / f["net_profit"],
        ["net_profit"],
    ),
    (
        "capex_to_revenue_percent",
        ["capex", "revenue"],
        "positive cash capex / revenue * 100",
        lambda f: f["capex"] / f["revenue"] * 100,
        ["revenue"],
    ),
    (
        "cfo_less_capex_margin_percent",
        ["cash_flow_operating", "capex", "revenue"],
        "(CFO - cash capex) / revenue * 100; not FCFF",
        lambda f: (f["cash_flow_operating"] - f["capex"]) / f["revenue"] * 100,
        ["revenue"],
    ),
]


def calculate_balance_sheet_metrics(facts):
    return group("finance.calculate_balance_sheet_metrics", facts, BALANCE, stock=True)


def calculate_cash_conversion(facts):
    if any(
        f.get("metric") == "capex" and f.get("value") is not None and fact(f)["value"] < 0
        for f in facts
    ):
        raise DomainError("invalid_input", "Cash capex must use a positive outflow convention.")
    return group("finance.calculate_cash_conversion", facts, CONVERSION)


def calculate_profitability(facts):
    specs = [
        (
            metric + "_margin_percent",
            [metric, "revenue"],
            f"{metric} / revenue * 100",
            lambda f, m=metric: f[m] / f["revenue"] * 100,
            ["revenue"],
        )
        for metric in [
            "net_profit",
            "profit_from_continuing_operations",
            "net_profit_attributable_to_owners",
            "operating_profit",
            "ebitda",
        ]
    ]
    output = group("finance.calculate_profitability", facts, specs)
    output["warnings"].append(
        "Margins follow the supplied profit/revenue definitions; operating profit is not relabelled EBIT, and group profit may include discontinued operations."
    )
    return output


def reconcile_facts(left, right):
    a, b = fact(left), fact(right)
    issues = [
        f"Different or unknown {k}."
        for k in ("issuer", "basis", "period_type", "period_end")
        if a.get(k) is None or a.get(k) != b.get(k)
    ]
    if a.get("period_start") != b.get("period_start"):
        issues.append("Different reporting-period starts.")
    if a.get("adjustment", "unknown") != b.get("adjustment", "unknown"):
        issues.append("Different adjustment conventions; review restatements before comparison.")
    if a["unit"] == "INR_per_share" and (
        not a.get("adjustment_reference")
        or a.get("adjustment_reference") != b.get("adjustment_reference")
    ):
        issues.append("Per-share comparability needs a shared explicit adjustment reference.")
    if a["metric"] != b["metric"] or a["definition"] != b["definition"]:
        issues.append("Metric definitions differ; source review is required even if values match.")
    if a["value"] is None or b["value"] is None:
        issues.append("Missing value; null is not zero.")
    comparable_units = a["unit"] in MONEY_UNITS and b["unit"] in MONEY_UNITS
    if not comparable_units and (a["unit"] is None or a["unit"] != b["unit"]):
        issues.append("Incompatible or unknown units.")
    values = {}
    if (
        a["value"] is not None
        and b["value"] is not None
        and (comparable_units or (a["unit"] is not None and a["unit"] == b["unit"]))
    ):
        with localcontext() as ctx:
            ctx.prec = 34
            av = a["value"] * (MONEY_UNITS[a["unit"]] if comparable_units else 1)
            bv = b["value"] * (MONEY_UNITS[b["unit"]] if comparable_units else 1)
            values = {
                "left_normalized": av,
                "right_normalized": bv,
                "difference": av - bv,
                "unit": "INR" if comparable_units else a["unit"],
                "numerically_equal": av == bv,
            }
    if values and not values["numerically_equal"]:
        issues.append(
            "Values differ after unit conversion; neither source was selected as authoritative."
        )
    return result("finance.reconcile_facts", [a, b], values, issues=issues)
