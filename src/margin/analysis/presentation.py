"""Reviewed financial labels and exact display units, never inferred from magnitude."""

from decimal import Decimal, localcontext

from margin.analysis.facts import STOCK_FIELDS, decimal
from margin.analysis.units import UNIT_EVIDENCE
from margin.core.contracts import DomainError
from margin.evidence.results import data_payload

LABELS = {
    "revenue": "Reported revenue from operations",
    "total_income": "Total income",
    "operating_profit": "Reported operating profit (not assumed EBIT)",
    "profit_before_tax": "Profit before tax",
    "ebitda": "EBITDA (earnings before interest, taxes, depreciation and amortisation)",
    "net_profit": "Reported total net profit",
    "profit_from_continuing_operations": "Reported profit from continuing operations",
    "net_profit_attributable_to_owners": "Net profit attributable to owners",
    "cash_flow_operating": "Net operating cash flow",
    "capex": "Reported cash capex (not FCFF)",
    "total_assets": "Total assets at period end",
    "total_liabilities": "Total liabilities at period end (not debt)",
    "total_equity": "Group total equity including minority interests",
    "equity_attributable_to_owners": "Equity attributable to owners",
    "current_assets": "Current assets at period end",
    "current_liabilities": "Current liabilities at period end",
    "cash_and_cash_equivalents": "Cash and cash equivalents",
    "borrowings_current": "Current borrowings",
    "borrowings_non_current": "Non-current borrowings",
    "eps": "Reported basic EPS",
    "diluted_eps": "Reported diluted EPS",
}
PER_SHARE = {"eps", "diluted_eps"}


def metric_entry(key, label, raw, path, per_share=False):
    entry = {
        "metric": key,
        "label": label,
        "source_path": path,
        "raw_value": raw,
        "raw_unit": "INR_per_share" if per_share else "INR",
        "unit": "INR_per_share" if per_share else "INR_crore",
        "value": None,
        "display": "Not returned",
        "status": "missing" if raw is None else "success",
        "period_kind": "point_in_time"
        if key in STOCK_FIELDS
        else "per_share_flow"
        if per_share
        else "flow",
    }
    if raw is not None:
        try:
            with localcontext() as context:
                context.prec = 34
                value = decimal(raw) / (Decimal(1) if per_share else Decimal(10000000))
                entry["value"] = format(value, "f")
                entry["display"] = f"₹{value:,.2f}" + (" per share" if per_share else " crore")
        except DomainError:
            entry.update(status="invalid", display="Invalid numeric value")
    return entry


def financial_view(result):
    """Build a bounded sidecar; the source record and stored payload are not modified."""
    if result.get("operation") != "bharatstock.get_financials":
        return None
    payload = data_payload(result.get("payload"), result.get("payload_kind"))
    source_rows = payload.get("data") if isinstance(payload, dict) else None
    view = {
        "contract_version": "margin.financial_view.v1",
        "status": "success",
        "reporting_instruction": "Use these labels and displays in answers. Do not rescale an already formatted crore amount. Raw payload is preserved for inspection; formatting does not verify issuer facts.",
        "raw_statement_unit": "INR",
        "display_statement_unit": "INR_crore",
        "crore_divisor": "10000000",
        "eps_unit": "INR_per_share",
        "unit_origin": "provider_documentation",
        "unit_evidence": UNIT_EVIDENCE.copy(),
        "verification": "provider_record_unverified",
        "coverage": "Selected reviewed metrics/segments only; raw response may contain additional fields.",
        "rounding": "Display: two decimal places; value: exact decimal string.",
        "rows": [],
    }
    if not isinstance(source_rows, list):
        return view | {
            "status": "unavailable",
            "note": "Unrecognized financial row shape; inspect the retained payload.",
        }
    if not source_rows:
        return view | {"status": "empty"}
    view["row_limit"] = 8
    view["rows_omitted"] = max(0, len(source_rows) - 8)
    selectors = result.get("receipt", {}).get("arguments", {})
    for index, row in enumerate(source_rows[:8]):
        if not isinstance(row, dict):
            view["status"] = "partial"
            continue
        item = {
            "ticker": selectors.get("ticker"),
            "exchange": selectors.get("exchange"),
            "period_type": row.get("period_type"),
            "fiscal_year": row.get("fiscal_year"),
            "period_start": row.get("period_start_date"),
            "period_end": row.get("period_end_date"),
            "basis": row.get("consolidation_type"),
            "metrics": [],
            "segments": [],
            "warnings": ["Provider record; original filing not independently verified."],
        }
        try:
            different = (
                row.get("net_profit") is not None
                and row.get("profit_from_continuing_operations") is not None
                and decimal(row["net_profit"]) != decimal(row["profit_from_continuing_operations"])
            )
        except DomainError:
            different = None
        item["continuing_profit_differs"] = different
        if different:
            item["warnings"].append(
                "Total group/owners profit and continuing profit have different scopes. Do not silently substitute them or compute mixed-scope margins; use the financial functions' scope assessment."
            )
        for key, label in LABELS.items():
            if key not in row:
                continue
            entry = metric_entry(key, label, row[key], f"data[{index}].{key}", key in PER_SHARE)
            if entry["status"] == "invalid":
                view["status"] = "partial"
            item["metrics"].append(entry)
        item["segments_omitted"] = 0
        for key, label in (
            ("segment_revenue", "Reported segment revenue"),
            ("segment_results", "Reported segment result"),
        ):
            segments = row.get(key)
            if not isinstance(segments, list):
                continue
            item["segments_omitted"] += max(0, len(segments) - 20)
            for segment_index, segment in enumerate(segments[:20]):
                if not isinstance(segment, dict) or "value" not in segment:
                    continue
                entry = metric_entry(
                    key, label, segment["value"], f"data[{index}].{key}[{segment_index}].value"
                )
                entry["segment"] = segment.get("segment")
                item["segments"].append(entry)
                if entry["status"] == "invalid":
                    view["status"] = "partial"
        view["rows"].append(item)
    return view
