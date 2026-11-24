import json
from decimal import Decimal, InvalidOperation

from margin.analysis.units import UNIT_EVIDENCE, field_unit


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
            "Monetary statement amounts are documented as INR; EPS is INR/share. Fact preparation retains the unit evidence separately from raw provider data.",
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
            "Inspect earnings definitions, units and original evidence before deriving growth; a historical provider conflict is not evidence that every filing conflicts."
        )
        if isinstance(data, dict):
            record = data.get("data", data)
            table = record.get("earnings_table", record) if isinstance(record, dict) else {}
            consolidated = table.get("consolidated", {}) if isinstance(table, dict) else {}
            raw = (
                consolidated.get("revenue_from_operations_raw", {})
                if isinstance(consolidated, dict)
                else {}
            )
            revenue = consolidated.get("revenue") if isinstance(consolidated, dict) else None
            normalized = (
                revenue.get("current_period_value") if isinstance(revenue, dict) else revenue
            )
            raw_value = raw.get("current_period_value") if isinstance(raw, dict) else None
            if normalized is not None and raw_value is not None:
                units_match = (
                    isinstance(revenue, dict)
                    and revenue.get("unit") is not None
                    and revenue.get("unit") == raw.get("unit")
                )
                if not units_match:
                    warnings.append(
                        "Normalized/raw revenue units are missing or different; no numerical equivalence has been assumed."
                    )
                else:
                    try:
                        a, b = Decimal(str(normalized)), Decimal(str(raw_value))
                        if not a.is_finite() or not b.is_finite():
                            raise InvalidOperation
                        if a != b:
                            warnings.append(
                                "Returned normalized revenue and raw revenue differ in the same declared unit. Neither has been selected as authoritative."
                            )
                    except InvalidOperation:
                        warnings.append(
                            "Normalized/raw revenue could not be compared as finite numbers."
                        )
    coverage = {
        "status": "empty" if empty else "provider_record",
        "row_count": len(rows) if isinstance(rows, list) else None,
        "pagination": data.get("pagination") if isinstance(data, dict) else None,
        "as_of": data.get("as_of_date") if isinstance(data, dict) else None,
        "note": "Requested scope is not a claim of complete returned coverage.",
    }
    units = {}

    def inspect_units(value, path="", depth=0):
        if depth > 5 or len(units) >= 200:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                unit = field_unit(operation, child_path)
                if unit and not isinstance(child, (dict, list)):
                    units[child_path] = unit
                inspect_units(child, child_path, depth + 1)
        elif isinstance(value, list):
            for index, child in enumerate(value[:200]):
                inspect_units(child, f"{path}[{index}]", depth + 1)

    inspect_units(data)
    if units:
        coverage["field_units"] = units
        coverage["unit_evidence"] = UNIT_EVIDENCE
    return data, warnings, coverage, empty
