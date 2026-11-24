"""Offline checks over returned answers and live receipts; no Margin or model imports."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from zipfile import ZipFile


def number(value):
    if isinstance(value, bool) or value is None:
        raise ValueError
    try:
        n = Decimal(str(value).replace(",", ""))
        if not n.is_finite() or abs(n) > Decimal("1e24"):
            raise ValueError
        return n
    except InvalidOperation:
        raise ValueError from None


def read_submission(path):
    with ZipFile(path) as archive:
        members = {i.filename: i for i in archive.infolist()}
        if (
            len(members) != len(archive.infolist())
            or sum(i.file_size for i in members.values()) > 70 * 1024 * 1024
        ):
            raise ValueError("Duplicate/oversized submission members")
        for name in members:
            if (
                Path(name).is_absolute()
                or ".." in Path(name).parts
                or name.endswith("providers.env")
            ):
                raise ValueError("Unexpected submission path/credentials")
        required = {
            "answers.json",
            "report.md",
            "session/session.json",
            "session/answer.json",
            "session/events.jsonl",
            "submission-manifest.json",
        }
        if not required <= members.keys() or set(members) - required - {"session/backend.json"}:
            raise ValueError("Unexpected or missing submission members")
        manifest = json.loads(archive.read("submission-manifest.json"))
        if set(manifest["sha256"]) != set(members) - {"submission-manifest.json"}:
            raise ValueError("Incomplete checksum manifest")
        for name, expected in manifest["sha256"].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError("Submission checksum mismatch")
        answers = json.loads(archive.read("answers.json"))
        events = [
            json.loads(line)
            for line in archive.read("session/events.jsonl").decode().splitlines()
            if line.strip()
        ]
        final = json.loads(archive.read("session/answer.json"))
        if json.loads(final["answer"]) != answers:
            raise ValueError("Submitted answer differs from recorded final answer")
        return answers, events


def native_data(result):
    payload = result.get("payload")
    if not isinstance(payload, dict):
        return {}
    if result.get("payload_kind") != "mcp_result":
        return payload
    data = payload.get("structuredContent", payload.get("structured_content"))
    if isinstance(data, dict):
        return data
    for item in payload.get("content", []):
        if item.get("type") == "text":
            try:
                value = json.loads(item.get("text", ""))
                if isinstance(value, dict):
                    return value
            except ValueError:
                pass
    return {}


def trace_index(events):
    run_by_operation = {}
    results = {}
    operations = {}
    ledgers = []
    modes, backends = set(), set()
    why_count = 0
    for event in events:
        if event.get("event_type") != "tool_observation":
            continue
        response = event.get("response", {})
        if response.get("mode"):
            modes.add(response["mode"])
        if response.get("backend_id"):
            backends.add(response["backend_id"])
        why_count += bool(response.get("decision_summary"))
        data = response.get("data", {})
        if not isinstance(data, dict):
            continue
        if "ledger" in data:
            ledgers.append(data["ledger"])
        if data.get("run_id"):
            for op in data.get("operations", []):
                run_by_operation[op["operation_id"]] = data["run_id"]
                operations[op["operation_id"]] = op
        if data.get("operation_id") and data.get("operation"):
            results[data["operation_id"]] = data
    references = {(run, op) for op, run in run_by_operation.items()}
    return {
        "runs": run_by_operation,
        "results": results,
        "operations": operations,
        "references": references,
        "ledgers": ledgers,
        "modes": modes,
        "backends": backends,
        "why_count": why_count,
    }


def compare_field(actual, expected):
    if actual.get("value") is None:
        return False, "Missing value"
    if "accepted" in expected:
        return actual["value"] in expected["accepted"], "Accepted outcome comparison"
    if (
        isinstance(expected["value"], bool)
        or not isinstance(expected["value"], (int, float))
        and not expected.get("numeric")
    ):
        return actual["value"] == expected["value"], "Exact value comparison"
    try:
        observed, target = number(actual["value"]), number(expected["value"])
        unit = expected.get("unit")
        if unit and actual.get("unit") != unit:
            return False, "Unit does not match the required output convention"
        if expected.get("basis") and actual.get("basis") != expected["basis"]:
            return False, "Reporting basis mismatch"
        if expected.get("period_end") and actual.get("period_end") != expected["period_end"]:
            return False, "Reporting period mismatch"
        return abs(observed - target) <= number(
            expected.get("tolerance", "0.0001")
        ), "Numerical comparison"
    except ValueError:
        return False, "Invalid/nonfinite numeric value"


def evaluate(answers, events, gold):
    if answers.get("benchmark_id") != gold["benchmark_id"] or answers.get("as_of") != gold["as_of"]:
        raise ValueError("Benchmark/reference-date mismatch")
    items = answers.get("answers", [])
    task_ids = [item.get("task_id") for item in items]
    if len(task_ids) != len(set(task_ids)) or set(task_ids) != set(gold["task_ids"]):
        raise ValueError("Missing/unknown/duplicate task IDs")
    for item in items:
        if item.get("status") not in {
            "ok",
            "qualified",
            "unavailable",
            "blocked",
            "not_attempted",
        } or not isinstance(item.get("fields"), dict):
            raise ValueError("Invalid task status/fields")
        for field in item["fields"].values():
            if (
                not isinstance(field, dict)
                or not isinstance(field.get("evidence"), list)
                or any(not isinstance(ref, dict) for ref in field["evidence"])
            ):
                raise ValueError("Invalid field/evidence format")
    by_task = {item["task_id"]: item for item in items}
    trace = trace_index(events)
    checks, flags = [], []

    def check(task, field, expected, origin):
        actual = by_task.get(task, {}).get("fields", {}).get(field, {})
        passed, message = compare_field(actual, expected)
        refs = actual.get("evidence", [])
        linked = any(
            (ref.get("run_id"), ref.get("operation_id")) in trace["references"] for ref in refs
        )
        if not linked:
            passed, message = False, "No evidence reference found in the supplied live trace"
        checks.append(
            {
                "task_id": task,
                "field": field,
                "passed": passed,
                "expected": expected,
                "actual": actual,
                "origin": origin,
                "note": message,
            }
        )

    for task, fields in gold["expected"].items():
        for field, expected in fields.items():
            check(
                task, field, expected, expected.get("origin", "issuer_filing_or_defined_contract")
            )

    # Dynamic cash-capex arithmetic is checked against this run, not yesterday's provider values.
    for result in trace["results"].values():
        operation = result.get("operation")
        data = native_data(result)
        args = result.get("receipt", {}).get("arguments", {})
        if operation == "bharatstock.get_financials" and args.get("period_type") == "annual":
            prefix = {"RELIANCE": "R", "TCS": "T"}.get(args.get("ticker"))
            for row in data.get("data", []):
                if (
                    not prefix
                    or row.get("period_end_date") != "2026-03-31"
                    or row.get("consolidation_type") != "consolidated"
                ):
                    continue
                try:
                    cfo = number(row.get("cash_flow_operating")) / Decimal(10_000_000)
                    capex = number(row.get("capex")) / Decimal(10_000_000)
                except ValueError:
                    flags.append(
                        f"{prefix}-CASH: live inputs missing; manually adjudicate source gap"
                    )
                    continue
                values = {"provider_capex_fy26": capex, "cfo_minus_capex_fy26": cfo - capex}
                if capex > 0:
                    with localcontext() as context:
                        context.prec = 40
                        values["capex_coverage"] = cfo / capex
                for field, value in values.items():
                    check(
                        prefix + "-CASH",
                        field,
                        {
                            "value": str(value),
                            "numeric": True,
                            "unit": "ratio" if field == "capex_coverage" else "INR_crore",
                            "period_end": "2026-03-31",
                            "basis": "consolidated",
                        },
                        "current_run_provider_inputs_not_independent_capex_truth",
                    )
                if prefix == "T":
                    flags.append(
                        "TCS capex definition needs review: independently defined FY26 PPE+intangible cash purchases are 4037 crore; do not equate the API capex field with that definition without reconciliation."
                    )
        if operation == "bharatstock.get_stock_prices":
            rows = sorted(
                data.get("data", []), key=lambda r: r.get("trade_date", r.get("date", ""))
            )
            if args.get("ticker") == "TCS" and len(rows) >= 2:
                try:
                    first, last = number(rows[0].get("close")), number(rows[-1].get("close"))
                    values = {
                        "tcs_first_date": rows[0].get("trade_date", rows[0].get("date")),
                        "tcs_last_date": rows[-1].get("trade_date", rows[-1].get("date")),
                        "tcs_first_close": str(first),
                        "tcs_last_close": str(last),
                        "tcs_price_change_percent": str((last / first - 1) * 100),
                    }
                    for field, value in values.items():
                        check(
                            "MARKET",
                            field,
                            {
                                "value": value,
                                "numeric": "date" not in field,
                                "unit": "percent"
                                if "percent" in field
                                else "INR_per_share"
                                if "close" in field
                                else None,
                            },
                            "current_run_price_receipt_not_exchange_gold",
                        )
                except (ValueError, ArithmeticError):
                    flags.append("TCS price inputs are incomplete; manually inspect the receipt")
    used = sorted(
        {op.get("operation") for op in trace["operations"].values() if op.get("operation")}
    )
    forbidden = sorted(set(used) & set(gold["forbidden_operations"]))
    if forbidden:
        flags.append("Out-of-scope valuation calls: " + ", ".join(forbidden))
    if trace["modes"] != {"live"}:
        flags.append("Trace does not establish exclusively live execution")
    if len(trace["backends"]) != 1:
        flags.append("Expected one shared backend identity for the run")
    if not trace["ledgers"]:
        flags.append("No status-ledger snapshots supplied")
    for ledger in trace["ledgers"]:
        attempts = ledger.get("http_attempts", {})
        if (
            attempts.get("bharatstock", 0) > 10
            or attempts.get("drishti", 0) > 40
            or ledger.get("completed_estimated_credits", 0) > 10
        ):
            flags.append("Observed process accounting exceeds test bounds")
    completed = sum(item.get("status") != "not_attempted" for item in items)
    summaries = [e for e in events if e.get("event_type") == "agent_summary"]
    return {
        "benchmark_id": gold["benchmark_id"],
        "grading_scope": "Automatic numeric/contract checks only; not a final scientific evaluation",
        "gold_review_status": gold["review_status"],
        "passed_checks": sum(c["passed"] for c in checks),
        "total_checks": len(checks),
        "automatic_check_percent": round(100 * sum(c["passed"] for c in checks) / len(checks), 2)
        if checks
        else None,
        "attempted_tasks": completed,
        "total_tasks": len(items),
        "operations_seen": used,
        "not_exercised": sorted(set(gold["in_scope_operations"]) - set(used)),
        "visible_summaries": len(summaries),
        "tool_calls_with_why": trace["why_count"],
        "hidden_reasoning_captured": False,
        "flags": sorted(set(flags)),
        "checks": checks,
        "manual_review_required": gold["manual_review"],
        "scoring_limit": "Do not interpret missing/blocked live data as model error without inspecting receipts. Dynamic checks assert response fidelity, not independent real-world truth. Self-reported notes do not prove internal reasoning.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path)
    parser.add_argument("--gold", type=Path, default=Path(__file__).with_name("gold.json"))
    parser.add_argument("--output", type=Path, default=Path("evaluation.json"))
    args = parser.parse_args()
    try:
        answers, events = read_submission(args.submission)
        result = evaluate(answers, events, json.loads(args.gold.read_text()))
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "report": str(args.output),
                    "passed": result["passed_checks"],
                    "total": result["total_checks"],
                    "manual_review_required": True,
                }
            )
        )
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"error": "invalid_submission_or_key", "detail": str(error)[:200]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
