"""Reviewed units by provider operation and decoded JSON path, never by magnitude."""

from __future__ import annotations

import re
from calendar import monthrange
from datetime import date

UNIT_EVIDENCE = {
    "url": "https://bharatstockapi.com/",
    "section": "What currency and units are the numbers in?",
    "reviewed_on": "2026-11-24",
    "policy_version": "bharatstock.units.2026-11-24",
}
PERIOD_EVIDENCE = {
    "url": "https://bharatstockapi.com/reference",
    "section": "Financials: derived quarters and half-year rows",
    "reviewed_on": "2026-11-24",
}


def quarter_context(row):
    """Only the documented, explicitly unflagged calendar-quarter branch is eligible."""
    supplied = row.get("period_start_date")
    if supplied:
        return supplied, "response"
    if (
        row.get("period_type") != "quarterly"
        or "reported_period_days" not in row
        or "filed_period_days" not in row
        or row["reported_period_days"] is not None
        or row["filed_period_days"] is not None
    ):
        return None, "unknown"
    try:
        end = date.fromisoformat(row["period_end_date"])
    except (KeyError, TypeError, ValueError):
        return None, "unknown"
    if end.month not in {3, 6, 9, 12} or end.day != monthrange(end.year, end.month)[1]:
        return None, "unknown"
    return date(end.year, end.month - 2, 1).isoformat(), "provider_documentation"


def field_unit(operation, path):
    """Snapshot display metadata; unreviewed fields deliberately have no default."""
    if operation in {"bharatstock.get_stock_quote", "bharatstock.get_stock_fundamentals"}:
        if operation == "bharatstock.get_stock_quote" and path == "metrics.market_cap":
            return "INR_crore"
        if path == "market_cap":
            return "INR"
    if operation == "bharatstock.get_stock_quote":
        allowed = path == "face_value" or bool(
            re.fullmatch(r"(?:latest_price|metrics)\.[a-z_0-9]+", path)
        )
    elif operation == "bharatstock.get_stock_fundamentals":
        allowed = bool(re.fullmatch(r"[a-z_0-9]+", path))
    elif operation in {"bharatstock.get_stock_prices", "bharatstock.get_corporate_actions"}:
        allowed = bool(re.fullmatch(r"data\[\d+\]\.[a-z_0-9]+", path))
    else:
        allowed = False
    if not allowed:
        return None
    key = path.rsplit(".", 1)[-1]
    if operation in {
        "bharatstock.get_stock_quote",
        "bharatstock.get_stock_fundamentals",
        "bharatstock.get_stock_prices",
        "bharatstock.get_corporate_actions",
    }:
        if key in {
            "open",
            "high",
            "low",
            "close",
            "prev_close",
            "adjusted_close",
            "price",
            "eps",
            "diluted_eps",
            "face_value",
            "book_value_per_share",
            "dividend_per_share",
            "week_52_high",
            "week_52_low",
        }:
            return "INR_per_share"
        if key in {"volume", "shares_outstanding", "total_shares"}:
            return "shares"
        if key in {"pe_ratio", "pb_ratio", "adjustment_factor"}:
            return "ratio"
        if key in {"delivery_pct", "avg_delivery_pct_30d", "dividend_yield"}:
            return "percent"
        if key in {"turnover", "avg_turnover_30d"}:
            return "INR_lakh"
    return None
