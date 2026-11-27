"""Deterministic presentation contracts; no fetching, inference or model calls."""

from __future__ import annotations

from copy import deepcopy
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

VALUATION_INPUT_CONTRACT = {
    "forecast_fcff": {
        "definition": "Explicit future annual free cash flow to the firm, in forecast order.",
        "origin": "Caller-supplied forecasts with reviewed assumptions; never automatically populated.",
        "not_equivalent_to": [
            "cash_flow_operating",
            "historical CFO",
            "CFO minus capex without scope review",
        ],
    },
    "debt": {
        "definition": "Explicit reviewed debt in the enterprise-to-equity bridge; include only the declared debt scope.",
        "origin": "Caller-supplied amount and debt definition.",
        "not_equivalent_to": ["total_liabilities"],
    },
    "cash": {
        "definition": "Explicit reviewed cash amount for the equity bridge, in the same monetary scale."
    },
    "wacc": {
        "definition": "Explicit annual discount rate as a decimal; not inferred from financial statements."
    },
    "terminal_growth": {
        "definition": "Explicit perpetual growth assumption as a decimal below WACC."
    },
    "diluted_shares": {
        "definition": "Actual share count, not crore/lakh shares; null leaves per-share value unavailable."
    },
    "instruction": "A valid calculation does not verify source facts. Missing inputs remain missing; no imputation, model inference or automatic CFO/debt mapping.",
}


def input_contract():
    return deepcopy(VALUATION_INPUT_CONTRACT)


def render_report(report):
    """Render only bounded canonical labels/displays; never regenerate financial prose."""

    def cell(value):
        text = str(value).replace("\n", " ").replace("\r", " ")[:2048]
        for char in ("\\", "|", "`", "[", "]", "<", ">"):
            text = text.replace(char, "\\" + char)
        return text

    lines = [
        cell(report.get("title", "Margin report")),
        "",
        "| Measure | Result |",
        "| --- | --- |",
    ]
    for row in report.get("rows", [])[:60]:
        lines.append(f"| {cell(row['label'])} | {cell(row['display'])} |")
    for note in report.get("warnings", [])[:20]:
        lines.extend(["", cell(note)])
    return "\n".join(lines)


def status_report(data):
    ledger = data["ledger"]
    rows = []
    for provider, label in (("bharatstock", "BharatStock"), ("drishti", "Drishti")):
        used, limit = ledger["http_attempts"][provider], ledger["http_limits"][provider]
        remaining = max(0, limit - used)
        rows.append(
            {
                "metric": provider + "_local_http_allowance",
                "label": label + " local HTTP allowance",
                "value": remaining,
                "unit": "HTTP_attempts",
                "used": used,
                "limit": limit,
                "scope": "local_process",
                "display": f"{used} of {limit} attempts used; {remaining} remaining locally",
            }
        )
    credit_used = ledger["completed_estimated_credits"]
    reserved = ledger["reserved_credits"]
    remaining = max(0, ledger["estimated_credit_limit"] - credit_used - reserved)
    rows.append(
        {
            "metric": "drishti_local_estimated_credit_allowance",
            "label": "Drishti local estimated-credit allowance",
            "value": remaining,
            "unit": "estimated_Drishti_credits",
            "scope": "local_process",
            "display": f"{remaining} remaining locally; {reserved} reserved; account balance not observed",
        }
    )
    rows.append(
        {
            "metric": "provider_account_balance",
            "label": "Provider account balance",
            "value": None,
            "unit": None,
            "status": "unknown",
            "display": "Unknown — no account-balance observation",
        }
    )
    report = {
        "version": "margin.status_report.v1",
        "title": "Margin local allowances",
        "rows": rows,
        "warnings": [
            "Local limits are not provider daily quotas or account balances. Internal record capacity is not HTTP allowance or credits."
        ],
    }
    report["markdown"] = render_report(report)
    return report


def dcf_report(output):
    values, inputs = output["values"], output["inputs"]
    unit = values["amount_unit"]
    suffix = {"INR": "", "INR_thousand": " thousand", "INR_lakh": " lakh", "INR_crore": " crore"}[
        unit
    ]
    horizon = len(values["forecast"])
    rows = []
    for metric, label, per_share in (
        ("forecast_present_value", "Present value of explicit forecast FCFF", False),
        (
            "terminal_value",
            f"Terminal value at end of forecast year {horizon} (undiscounted)",
            False,
        ),
        ("terminal_present_value", "Present value of terminal value (discounted)", False),
        ("enterprise_value", "Enterprise value at valuation date", False),
        ("equity_value", "Equity value after the supplied bridge", False),
        ("value_per_share_inr", "Equity value per diluted share", True),
    ):
        raw = values[metric]
        with localcontext() as context:
            context.prec = 160
            context.rounding = ROUND_HALF_EVEN
            display = (
                "Unavailable — no diluted share count supplied"
                if raw is None
                else f"₹{Decimal(str(raw)):,.2f}" + (" per share" if per_share else suffix)
            )
        rows.append(
            {
                "metric": metric,
                "label": label,
                "value": raw,
                "unit": "INR_per_share" if per_share else unit,
                "status": "unavailable" if raw is None else "success",
                "display": display,
            }
        )
    report = {
        "version": "margin.dcf_report.v1",
        "title": "DCF from explicit supplied assumptions",
        "rows": rows,
        "valuation_date": inputs["valuation_date"],
        "input_origin": inputs["input_origin"],
        "input_contract": input_contract(),
        "warnings": deepcopy(output["warnings"]),
    }
    report["markdown"] = render_report(report)
    return report
