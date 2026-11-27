"""Explicit B2/Dr16/estimated-credit8 product regression; no account probes/retries.

Run only with a newly approved allocation. Captures are private diagnostic evidence,
not a product database, professor evaluation or independently verified financial truth.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from dataclasses import asdict
from pathlib import Path

from margin.analysis.company import FUNCTIONS, calculate_company
from margin.analysis.reporting import company_report
from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.interfaces.agent.local_config import read_provider_env
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.server import MarginMCP


def event_requests():
    window = {"symbols": ["INFY"], "from": "2026-11-10", "to": "2026-11-27", "page": 1}
    return [
        {"operation": "drishti.get_news", "arguments": {"query": window | {"limit": 2}}},
        {
            "operation": "drishti.get_announcements",
            "arguments": {"query": window | {"limit": 1, "include_extracted_information": False}},
        },
        {
            "operation": "drishti.list_earnings",
            "arguments": {"query": window | {"from": "2026-09-01", "limit": 1}},
        },
    ]


def detail_request(result):
    from margin.evidence.results import data_payload

    payload = data_payload(result["payload"], result["payload_kind"])
    rows = payload.get("data", []) if isinstance(payload, dict) else []
    row = rows[0] if rows and isinstance(rows[0], dict) else {}
    if row.get("symbol") != "INFY":
        return None
    identifier = row.get("earnings_id") or row.get("id")
    values = (
        {"earnings_id": identifier, "detailed": True}
        if identifier
        else (
            {"symbol": "INFY", "quarter": row["quarter"], "detailed": True}
            if row.get("quarter")
            else None
        )
    )
    return {"operation": "drishti.get_earnings_filing", "arguments": values} if values else None


async def main(args):
    logging.disable(logging.CRITICAL)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    keys = read_provider_env(args.env_file)
    allowed = frozenset(r["operation"] for r in event_requests()) | {"drishti.get_earnings_filing"}

    class CapturingService(ResearchService):
        async def execute(self, request, operation_id):
            outcome = await super().execute(request, operation_id)
            record = self.sanitizer.clean(asdict(outcome))
            captures.append(record)
            save(f"response-{len(captures):02d}.json", record)
            return outcome

    service = CapturingService(
        Settings(
            mode="live",
            bharatstock_key=keys.get("BHARATSTOCK_API_KEY", ""),
            drishti_key=keys.get("DRISHTI_API_KEY", ""),
            bharatstock_requests=2,
            drishti_requests=16,
            drishti_credits=8,
            enabled_unverified=allowed,
        )
    )
    recorder = ToolRecorder(directory=output / "logs")
    owner = MarginMCP(service, recorder)
    captures, observations, imports = [], [], []
    summary = {
        "kind": "operator_product_acceptance_not_model_or_source_verification",
        "version": "0.10.0",
        "limits": {
            "bharatstock_http": 2,
            "drishti_http_including_lifecycle": 16,
            "estimated_drishti_credits": 8,
        },
        "account_calls": 0,
        "active_user_backend_changed": False,
        "providers": {},
    }

    def save(name, value):
        clean = service.sanitizer.clean(value)
        fd = os.open(output / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(clean, stream, indent=2, allow_nan=False)
            stream.write("\n")

    async def call(tool, values=None):
        result = await owner.call(
            tool,
            (values or {})
            | {
                "why": "Approved bounded product regression; no retries, corpus or professor evaluation."
            },
        )
        body = result.structured_content
        observations.append({"tool": tool, "arguments": values or {}, "result": body})
        if result.is_error:
            raise DomainError(
                body["error"]["code"],
                "Product check stopped; inspect private error, no automatic retry.",
            )
        return body["data"]

    async def run(request, key):
        plan = await call("margin_preview", {"operations": [request]})
        run = await call(
            "margin_run",
            {
                "session_id": owner.session_id,
                "plan_id": plan["plan_id"],
                "idempotency_key": key,
                "wait_seconds": 30,
            },
        )
        if run["status"] in {"queued", "running"}:
            run = await call("margin_run_status", {"run_id": run["run_id"], "wait_seconds": 30})
        if run["status"] in {"queued", "running"}:
            raise DomainError(
                "uncertain_outcome", "Operation still active; no new submission.", uncertain=True
            )
        op = run["operations"][0]
        result = await call(
            "margin_result", {"run_id": run["run_id"], "operation_id": op["operation_id"]}
        )
        if result["status"] not in {"success", "empty"}:
            raise DomainError(
                "provider_stopped", "Provider returned failed/held outcome; no retry."
            )
        return run, op, result

    try:
        save("status-before.json", await call("margin_status"))
        try:
            inputs = {
                "ticker": "INFY",
                "exchange": "NSE",
                "period_type": "annual",
                "basis": "consolidated",
                "execute": True,
                "include_details": True,
                "idempotency_key": "product-INFY-annual-0100",
            }
            ready = await call("margin_company_data_readiness", inputs)
            if ready["status"] == "running":
                ready = await call("margin_company_data_readiness", inputs)
            if (
                ready["status"] == "running"
                or not captures
                or captures[-1]["status"] not in {"success", "empty"}
            ):
                raise DomainError("provider_stopped", "Annual request unavailable; no retry.")
            annual = captures[-1]
            before = service.ledger.snapshot()
            replay = await call(
                "margin_company_finance", inputs | {"function": "finance.company_data_readiness"}
            )
            assert replay == ready and before == service.ledger.snapshot()
            save("readiness-live.json", ready)
            _, _, quarterly = await run(
                {
                    "operation": "bharatstock.get_financials",
                    "arguments": {
                        "ticker": "HINDUNILVR",
                        "exchange": "NSE",
                        "period_type": "quarterly",
                        "page": 1,
                        "page_size": 8,
                    },
                },
                "product-HUL-quarterly-0100",
            )
            local = {}
            for function in sorted(FUNCTIONS):
                is_ttm = function == "finance.company_ttm"
                selected = {
                    "ticker": "HINDUNILVR" if is_ttm else "INFY",
                    "exchange": "NSE",
                    "basis": "consolidated",
                    "period_type": "quarterly" if is_ttm else "annual",
                    "metric": "revenue",
                    "money_unit": "auto",
                    "source_run_id": None,
                    "source_operation_id": (quarterly if is_ttm else annual)["operation_id"],
                }
                result = calculate_company(function, selected, quarterly if is_ttm else annual)
                result["report"] = company_report(result, result)
                local[function] = result
            save(
                "same-response-local-functions.json",
                {
                    "kind": "local calculations over two just-returned real responses; not nine fresh wrapper requests",
                    "results": local,
                },
            )
            summary["providers"]["bharatstock"] = {
                "status": "completed",
                "readiness_status": ready["status"],
                "local_function_statuses": {k: v["status"] for k, v in local.items()},
                "cross_alias_replay": "no extra request",
            }
        except (DomainError, AssertionError, KeyError) as exc:
            summary["providers"]["bharatstock"] = {
                "status": "stopped",
                "code": exc.code if isinstance(exc, DomainError) else type(exc).__name__,
            }
        print(
            json.dumps({"provider": "bharatstock", **summary["providers"]["bharatstock"]}),
            flush=True,
        )
        try:
            save(
                "drishti-metadata.json",
                await call("margin_connect_drishti", {"session_id": owner.session_id}),
            )
            event_statuses = []
            requests = event_requests()
            for index, request in enumerate(requests):
                run_result, op, result = await run(request, f"product-INFY-event-0100-{index}")
                imported = await call(
                    "margin_review_sources",
                    {
                        "run_id": run_result["run_id"],
                        "operation_id": op["operation_id"],
                        "issuer": "NSE:INFY",
                    },
                )
                imports.append({"operation": request["operation"], "import": imported})
                event_statuses.append(
                    {
                        "operation": request["operation"],
                        "status": result["status"],
                        "imported_sources": len(imported.get("sources", [])),
                    }
                )
                print(json.dumps(event_statuses[-1]), flush=True)
                if request["operation"] == "drishti.list_earnings":
                    detail = detail_request(result)
                    if detail:
                        run_result, op, result = await run(detail, "product-INFY-event-detail-0100")
                        imported = await call(
                            "margin_review_sources",
                            {
                                "run_id": run_result["run_id"],
                                "operation_id": op["operation_id"],
                                "issuer": "NSE:INFY",
                            },
                        )
                        imports.append({"operation": detail["operation"], "import": imported})
                        event_statuses.append(
                            {
                                "operation": detail["operation"],
                                "status": result["status"],
                                "imported_sources": len(imported.get("sources", [])),
                            }
                        )
                    else:
                        event_statuses.append(
                            {
                                "operation": "drishti.get_earnings_filing",
                                "status": "not_run_no_returned_selector",
                            }
                        )
            summary["providers"]["drishti"] = {"status": "completed", "events": event_statuses}
        except (DomainError, AssertionError, KeyError) as exc:
            summary["providers"]["drishti"] = {
                "status": "stopped",
                "code": exc.code if isinstance(exc, DomainError) else type(exc).__name__,
            }
        print(json.dumps({"provider": "drishti", **summary["providers"]["drishti"]}), flush=True)
    finally:
        await service.close()  # includes metered MCP cleanup; never restarts user's owner
        summary["ledger_after_cleanup"] = service.ledger.snapshot()
        save("observations.json", observations)
        save("imported-real-sources.json", imports)
        save("summary.json", summary)
        recorder.close()
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-live", required=True, action="store_true")
    parser.add_argument(
        "--env-file", type=Path, default=Path(__file__).resolve().parents[1] / ".env"
    )
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
