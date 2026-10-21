import json


def data_payload(payload, kind):
    if kind == "rest_json":
        return payload
    structured = payload.get("structuredContent", payload.get("structured_content"))
    if structured is not None:
        return structured
    for block in payload.get("content", []):
        if block.get("type") == "text":
            try:
                return json.loads(block["text"])
            except (ValueError, KeyError):
                pass
    return payload


def inspect_result(payload, kind, operation):
    """Only reviewed shapes. Unknown layouts stay visible as provider JSON."""
    data = data_payload(payload, kind)
    warnings = ["Provider output is not independently verified against an original document."]
    rows = data.get("data") if isinstance(data, dict) else data if isinstance(data, list) else None
    empty = rows == []
    if operation.endswith("get_financials"):
        warnings += [
            "Preserve reporting basis and period; null cash flow is not zero.",
            "Units are unconfirmed unless explicitly supplied by this response.",
        ]
    if operation.endswith(("get_stock_quote", "get_stock_fundamentals")):
        warnings.append(
            "Market-cap scales can differ by JSON path; no automatic conversion applied."
        )
    if operation.startswith("drishti."):
        warnings.append(
            "Filing date can mean ingestion; unknown/offset-free times are not assigned a timezone."
        )
    if operation.endswith("get_news"):
        warnings.append(
            "Provider news sentiment is text tone, not comprehensive investor sentiment."
        )
    if operation.endswith("get_earnings_filing"):
        warnings.append(
            "Known earnings extraction discrepancy: inspect normalized/raw definitions and original evidence before deriving growth."
        )
        if isinstance(data, dict):
            consolidated = data.get("consolidated", {})
            raw = (
                consolidated.get("revenue_from_operations_raw", {})
                if isinstance(consolidated, dict)
                else {}
            )
            if (
                isinstance(raw, dict)
                and "current_period_value" in raw
                and consolidated.get("revenue") != raw["current_period_value"]
            ):
                warnings.append(
                    "Returned normalized revenue and raw revenue differ. Neither has been selected as authoritative."
                )
    coverage = {
        "status": "empty" if empty else "provider_record",
        "row_count": len(rows) if isinstance(rows, list) else None,
        "pagination": data.get("pagination") if isinstance(data, dict) else None,
        "as_of": data.get("as_of_date") if isinstance(data, dict) else None,
        "note": "Requested scope is not a claim of complete returned coverage.",
    }
    return data, warnings, coverage, empty
