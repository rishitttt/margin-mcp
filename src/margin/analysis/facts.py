"""Explicit financial context alongside, never in place of, provider records."""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from margin.analysis.units import PERIOD_EVIDENCE, UNIT_EVIDENCE, quarter_context
from margin.core.contracts import DomainError
from margin.evidence.results import data_payload

VERSION = "1.0"
MONEY_UNITS = {
    "INR": Decimal(1),
    "INR_thousand": Decimal(1000),
    "INR_lakh": Decimal(100000),
    "INR_crore": Decimal(10000000),
}
UNITS = [*MONEY_UNITS, "INR_per_share", "shares", "ratio", "percent", None]
FACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "issuer",
        "metric",
        "definition",
        "value",
        "unit",
        "period_type",
        "period_end",
        "basis",
    ],
    "properties": {
        "issuer": {"type": "string", "minLength": 1, "maxLength": 100},
        "metric": {"type": "string", "minLength": 1, "maxLength": 80},
        "definition": {"type": "string", "minLength": 1, "maxLength": 250},
        "value": {"type": ["string", "number", "null"], "maxLength": 64},
        "unit": {"enum": UNITS},
        "period_type": {"enum": ["annual", "quarterly", "instant", "ttm", None]},
        "period_start": {"type": ["string", "null"], "format": "date"},
        "period_end": {"type": ["string", "null"], "format": "date"},
        "basis": {"enum": ["consolidated", "standalone", None]},
        "adjustment": {"enum": ["unknown", "as_reported", "provider_adjusted", "restated"]},
        "adjustment_reference": {"type": ["string", "null"], "maxLength": 150},
        "fact_id": {"type": "string", "maxLength": 150},
        "source": {"type": "object"},
        "unit_origin": {
            "enum": ["unknown", "response", "caller_declared", "provider_documentation"]
        },
        "transformations": {"type": "array", "maxItems": 10, "items": {"type": "object"}},
    },
}


def decimal(value, label="value") -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise DomainError("invalid_input", f"{label} must be a finite decimal number.")
    if len(str(value)) > 64:
        raise DomainError("invalid_input", f"{label} exceeds the supported precision/size.")
    try:
        result = Decimal(str(value))
        if not result.is_finite() or abs(result) > Decimal("1e24"):
            raise InvalidOperation
        if result.is_zero():
            return Decimal(0)
        if result.adjusted() < -24 or len(result.as_tuple().digits) > 34:
            raise InvalidOperation
        return result
    except (InvalidOperation, ValueError):
        raise DomainError(
            "invalid_input", f"{label} must be finite and within the supported range."
        ) from None


def wire(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    return value


def fact(value: dict) -> dict:
    try:
        Draft202012Validator(FACT_SCHEMA, format_checker=FormatChecker()).validate(value)
    except ValidationError:
        raise DomainError(
            "invalid_input", "Check the financial-fact schema; no implicit context coercion."
        ) from None
    out = copy.deepcopy(value)
    if out["value"] is not None:
        out["value"] = decimal(out["value"])
    if (
        out.get("period_start")
        and out.get("period_end")
        and out["period_start"] > out["period_end"]
    ):
        raise DomainError("invalid_input", "Fact period start must precede its end.")
    return out


def check_compatibility(facts, purpose="comparison"):
    if (
        purpose not in {"comparison", "ratio", "ttm"}
        or not isinstance(facts, list)
        or not 2 <= len(facts) <= 4
    ):
        raise DomainError(
            "invalid_input", "Select two to four facts and a supported compatibility purpose."
        )
    items = [fact(v) for v in facts]
    issues = []
    for key in ("issuer", "unit", "basis", "period_type"):
        if any(v.get(key) is None for v in items):
            issues.append(f"Unknown {key}.")
        elif len({v[key] for v in items}) != 1:
            issues.append(f"Different {key} values.")
    if any(v["value"] is None for v in items):
        issues.append("Missing numeric value; null is not zero.")
    if any(v["period_end"] is None for v in items):
        issues.append("Unknown reporting period end.")
    if purpose in {"comparison", "ttm"} and any(
        v.get("source", {}).get("basis_changed") is True for v in items
    ):
        issues.append("Provider marks a reporting-basis change; review before comparison or TTM.")
    if purpose in {"comparison", "ttm"}:
        for key in ("metric", "definition"):
            if len({v[key] for v in items}) != 1:
                issues.append(f"Different {key} values.")
        if purpose == "comparison" and all(
            v.get("period_start") and v.get("period_end") for v in items
        ):
            durations = [
                (date.fromisoformat(v["period_end"]) - date.fromisoformat(v["period_start"])).days
                for v in items
            ]
            if max(durations) - min(durations) > 7:
                issues.append(
                    "Reporting durations differ; a stub period must not become ordinary growth."
                )
        if any("eps" in v["metric"].lower() or v["unit"] == "INR_per_share" for v in items):
            adjustments = {v.get("adjustment", "unknown") for v in items}
            if "unknown" in adjustments or len(adjustments) != 1 or adjustments == {"as_reported"}:
                issues.append("Per-share reporting/adjustment comparability is not established.")
            if (
                any(not v.get("adjustment_reference") for v in items)
                or len({v.get("adjustment_reference") for v in items}) != 1
            ):
                issues.append("A shared explicit per-share adjustment reference is required.")
    if purpose == "ratio":
        for key in ("period_start", "period_end"):
            same_source_row = (
                key == "period_start"
                and all(v.get(key) is None for v in items)
                and all(v.get("source", {}).get("row_reference") for v in items)
                and len({v["source"]["row_reference"] for v in items}) == 1
            )
            if same_source_row:
                continue
            # Both missing starts are unknown, not evidence of the same period.
            if any(not v.get(key) for v in items) or len({v.get(key) for v in items}) != 1:
                issues.append(f"Same known {key} required.")
    if any(v["period_type"] == "instant" for v in items):
        issues.append("These flow calculations do not accept point-in-time balance-sheet facts.")
    return {
        "function": "facts.check_compatibility",
        "function_version": VERSION,
        "status": "success" if not issues else "incomplete",
        "compatible": not issues,
        "issues": issues,
    }


def convert_units(value, target_unit):
    item = fact(value)
    if item["unit"] not in MONEY_UNITS or target_unit not in MONEY_UNITS:
        raise DomainError(
            "incompatible_units",
            "Convert only explicitly known INR amount scales; no inferred units or FX.",
        )
    if item["value"] is None:
        return {
            "function": "facts.convert_units",
            "function_version": VERSION,
            "status": "incomplete",
            "issues": ["Missing value."],
        }
    with localcontext() as ctx:
        ctx.prec = 34
        converted = item["value"] * MONEY_UNITS[item["unit"]] / MONEY_UNITS[target_unit]
    trace = {
        "function_version": VERSION,
        "source_unit": item["unit"],
        "target_unit": target_unit,
        "input_value": str(item["value"]),
        "factor": str(MONEY_UNITS[item["unit"]] / MONEY_UNITS[target_unit]),
    }
    item["value"], item["unit"] = converted, target_unit
    item["transformations"] = [*item.get("transformations", []), trace]
    return wire(
        {
            "function": "facts.convert_units",
            "function_version": VERSION,
            "status": "success",
            "fact": item,
        }
    )


FIELDS = {
    "revenue": "BharatStock reported revenue from operations; not necessarily product sales or management turnover",
    "net_profit": "Reported group net profit; not owners-attributable profit",
    "profit_from_continuing_operations": "Reported group profit from continuing operations",
    "net_profit_attributable_to_owners": "Reported net profit attributable to owners",
    "operating_profit": "Reported operating profit; not automatically EBIT",
    "ebitda": "Reported EBITDA",
    "cash_flow_operating": "Reported net operating cash flow",
    "capex": "Provider capex: purchase of PPE and intangibles; positive outflow convention requires review",
    "depreciation_and_amortisation": "Reported depreciation and amortisation",
    "eps": "Reported basic EPS as filed; comparability requires review",
    "diluted_eps": "Reported diluted EPS as filed; comparability requires review",
    "eps_adjusted": "Provider basic EPS adjusted for subsequent bonus/split multiplier",
    "diluted_eps_adjusted": "Provider diluted EPS adjusted for subsequent bonus/split multiplier",
}

STOCK_FIELDS = {
    "current_assets": "Reported current assets at period end",
    "current_liabilities": "Reported current liabilities at period end",
    "inventories": "Reported inventories at period end",
    "cash_and_cash_equivalents": "Reported cash and cash equivalents; excludes other investments",
    "borrowings_current": "Reported current borrowings; not all liabilities or necessarily all leases",
    "borrowings_non_current": "Reported non-current borrowings; not all liabilities or necessarily all leases",
    "total_equity": "Reported group total equity including minority interests",
    "equity_attributable_to_owners": "Reported equity attributable to owners",
    "total_assets": "Reported total assets at period end",
    "total_liabilities": "Reported total liabilities at period end",
}
FIELDS.update(STOCK_FIELDS)


def prepare_financial_facts(result: dict, money_unit="auto"):
    """Reviewed BharatStock financial fields only. Units never inferred from magnitude."""
    if money_unit == "unknown":
        money_unit = None
    if money_unit is not None and (
        not isinstance(money_unit, str) or money_unit not in ("auto", *MONEY_UNITS)
    ):
        raise DomainError(
            "invalid_input", "Choose an explicit supported monetary scale or leave it unknown."
        )
    if result.get("operation") != "bharatstock.get_financials" or result.get("status") not in {
        "success",
        "empty",
    }:
        raise DomainError(
            "unsupported_mapping",
            "Fact preparation currently supports successful BharatStock financial results only.",
        )
    data = data_payload(result["payload"], result["payload_kind"])
    rows = data.get("data") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise DomainError(
            "unsupported_mapping", "Unknown financial envelope; inspect the provider payload."
        )
    receipt = result.get("receipt", {})
    args = receipt.get("arguments", receipt.get("selectors", {}))
    if not args.get("ticker") or not args.get("exchange"):
        raise DomainError(
            "incomplete_context", "Receipt does not establish the requested company/listing."
        )
    facts = []
    automatic = money_unit == "auto"
    if result.get("mode") == "live" and money_unit not in {None, "auto", "INR"}:
        raise DomainError(
            "unit_conflict",
            "BharatStock financial amounts are documented in INR. Use auto/INR; convert prepared facts separately.",
        )
    resolved_unit = "INR" if automatic else money_unit
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DomainError("unsupported_mapping", "Unknown financial row shape.")
        start, period_origin = quarter_context(row)
        for key, definition in FIELDS.items():
            if key not in row:
                continue
            per_share = key in {"eps", "diluted_eps", "eps_adjusted", "diluted_eps_adjusted"}
            value = {
                "issuer": f"{args['exchange']}:{args['ticker']}",
                "metric": key,
                "definition": definition,
                "value": row[key],
                "unit": "INR_per_share"
                if per_share and resolved_unit
                else None
                if per_share
                else resolved_unit,
                "unit_origin": "provider_documentation"
                if automatic
                else "caller_declared"
                if money_unit
                else "unknown",
                "period_type": "instant" if key in STOCK_FIELDS else row.get("period_type"),
                "period_start": None if key in STOCK_FIELDS else start,
                "period_end": row.get("period_end_date"),
                "basis": row.get("consolidation_type"),
                "adjustment": "provider_adjusted" if key.endswith("_adjusted") else "as_reported",
                "adjustment_reference": receipt.get("retrieved_at")
                if key.endswith("_adjusted")
                else None,
                "fact_id": f"{result['operation_id']}:{index}:{key}",
                "source": {
                    "provider": "bharatstock",
                    "operation_id": result["operation_id"],
                    "row_reference": f"{result['operation_id']}:data[{index}]",
                    "field_path": f"data[{index}].{key}",
                    "path_root": "decoded_provider_payload",
                    "original_value": row[key],
                    "mode": result.get("mode"),
                    "retrieved_at": receipt.get("retrieved_at"),
                    "verification": "unverified",
                    "eps_adjustment_factor": row.get("eps_adjustment_factor"),
                    "unit_evidence": UNIT_EVIDENCE if automatic else None,
                    "period_start_origin": "not_applicable"
                    if key in STOCK_FIELDS
                    else period_origin,
                    "period_evidence": PERIOD_EVIDENCE
                    if period_origin == "provider_documentation"
                    else None,
                    "reported_period_type": row.get("period_type"),
                    "reported_period_days": row.get("reported_period_days"),
                    "filed_period_days": row.get("filed_period_days"),
                    "basis_changed": row.get("basis_changed"),
                    "statement_format": row.get("statement_format"),
                    "continuing_profit_differs": decimal(row["net_profit"])
                    != decimal(row["profit_from_continuing_operations"])
                    if row.get("net_profit") is not None
                    and row.get("profit_from_continuing_operations") is not None
                    else None,
                },
            }
            facts.append(wire(fact(value)))
    return {
        "function": "facts.prepare",
        "function_version": VERSION,
        "facts": facts,
        "status": "success" if facts else "empty",
        "mapping": "bharatstock.financials.v2",
        "warnings": [
            "Provider values are unverified. Auto units use reviewed provider documentation; null explicitly keeps units unknown.",
            "Quarter starts use explicit response dates or the reviewed unflagged-calendar-quarter contract; no EPS adjustment or source verification is applied.",
        ],
    }
