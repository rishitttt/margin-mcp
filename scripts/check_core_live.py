"""Explicit bounded core acceptance: real providers, private receipts, no model inference."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.registry import Registry
from margin.core.service import ResearchService
from margin.evidence.results import data_payload
from margin.interfaces.agent.local_config import read_provider_env


async def check(output, scope="all", drishti_http=20):
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    credentials = read_provider_env(Path(__file__).resolve().parents[1] / ".env")
    if set(credentials) != {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}:
        raise DomainError("credentials", "Both keys must be configured in the ignored repo .env.")
    enabled = frozenset(Registry(Settings()).specs)
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key=credentials["BHARATSTOCK_API_KEY"],
            drishti_key=credentials["DRISHTI_API_KEY"],
            enabled_unverified=enabled,
            bharatstock_requests=10 if scope == "all" else 0,
            drishti_requests=drishti_http,
            drishti_credits=10,
            max_payload_runs=20,
            max_buffer_bytes=40 * 1024 * 1024,
        )
    )
    results = []
    summary = {
        "started_at": datetime.now(UTC).isoformat(),
        "mode": "live",
        "limits": {
            "bharatstock_http": service.settings.bharatstock_requests,
            "drishti_http": drishti_http,
            "drishti_estimated_credits": 10,
        },
        "observations": [],
        "scope": "Core functional acceptance, not an independent financial benchmark",
    }

    def save(name, value):
        clean = service.sanitizer.clean(value)
        descriptor = os.open(output / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(clean, stream, indent=2)
            stream.write("\n")

    async def batch(operations):
        plan = service.create_plan(operations)
        run = await service.start_run(plan["plan_id"], "acceptance-" + plan["plan_id"])
        await service._tasks[run["run_id"]]
        states = service.get_run(run["run_id"])
        collected = []
        for item in states["operations"]:
            result = service.get_result(run["run_id"], item["operation_id"])
            result["acceptance_run_id"] = run["run_id"]
            results.append(result)
            collected.append(result)
            save(f"{len(results):02d}-{result['operation'].replace('.', '-')}.json", result)
            summary["observations"].append(
                {
                    "operation": result["operation"],
                    "status": result["status"],
                    "error": result["error"],
                    "http_attempts": result["receipt"]["http_attempts"],
                }
            )
            print(json.dumps(summary["observations"][-1]), flush=True)
        if any(r["status"] in {"unknown", "failed"} for r in collected):
            raise DomainError(
                "acceptance_stopped", "A provider branch failed/was uncertain; no automatic retry."
            )
        return collected

    def op(name, args):
        return {"operation": name, "arguments": args}

    try:
        b = []
        for symbol in ("RELIANCE", "TCS"):
            identity = {"ticker": symbol, "exchange": "NSE"}
            b.append(op("bharatstock.get_stock_quote", identity))
            for period in ("annual", "quarterly"):
                b.append(
                    op(
                        "bharatstock.get_financials",
                        identity
                        | {
                            "period_type": period,
                            "page": 1,
                            "page_size": 2 if period == "annual" else 4,
                        },
                    )
                )
        b += [
            op("bharatstock.search_stocks", {"q": "TCS", "limit": 3}),
            op("bharatstock.get_stock_fundamentals", {"ticker": "RELIANCE", "exchange": "NSE"}),
            op(
                "bharatstock.get_corporate_actions",
                {
                    "ticker": "RELIANCE",
                    "exchange": "NSE",
                    "action_type": "dividend",
                    "page": 1,
                    "page_size": 5,
                },
            ),
            op(
                "bharatstock.get_stock_prices",
                {
                    "ticker": "TCS",
                    "exchange": "NSE",
                    "from": "2026-11-11",
                    "to": "2026-11-24",
                    "page": 1,
                    "page_size": 10,
                },
            ),
        ]
        if scope == "all":
            await batch(b[:5])
            await batch(b[5:])
            # Exercise all five company wrappers from already retained real financials.
            before = service.ledger.snapshot()
            for symbol in ("RELIANCE", "TCS"):
                for function in (
                    "finance.company_margins",
                    "finance.company_cashflow_metrics",
                    "finance.company_growth",
                    "finance.company_cagr",
                    "finance.company_ttm",
                ):
                    plan = service.plan_financial(
                        function,
                        symbol,
                        "NSE",
                        money_unit="INR",
                        period_type="quarterly" if function.endswith("ttm") else "annual",
                        fetch_missing=False,
                    )
                    run = await service.start_run(plan["plan_id"], "acceptance-" + plan["plan_id"])
                    await service._tasks[run["run_id"]]
                    result = service.get_result(
                        run["run_id"], run["operations"][-1]["operation_id"]
                    )
                    save(f"{symbol}-{function}.json", result)
                    summary["observations"].append(
                        {
                            "operation": function,
                            "symbol": symbol,
                            "status": result["status"],
                            "issues": (result.get("payload") or {}).get("issues", []),
                            "http_attempts": result["receipt"]["http_attempts"],
                        }
                    )
                    print(json.dumps(summary["observations"][-1]), flush=True)
            assert before == service.ledger.snapshot(), (
                "Local wrapper reuse unexpectedly changed provider counters"
            )
        connected = await service.connect_drishti()
        save("drishti-metadata.json", connected)
        capabilities = {item["operation"]: item for item in service.capabilities()}
        queries = [
            op("drishti.get_symbols", {"query": {"symbols": ["RELIANCE"]}}),
            op("drishti.resolve_symbols", {"queries": ["Tata Consultancy Services Limited"]}),
            op("drishti.get_announcement_categories", {}),
            op(
                "drishti.get_news",
                {
                    "query": {
                        "symbols": ["RELIANCE"],
                        "from": "2026-11-10",
                        "to": "2026-11-24",
                        "limit": 2,
                        "page": 1,
                    }
                },
            ),
            op(
                "drishti.list_earnings",
                {
                    "query": {
                        "symbols": ["RELIANCE"],
                        "from": "2026-09-01",
                        "to": "2026-11-24",
                        "limit": 1,
                        "page": 1,
                    }
                },
            ),
            op(
                "drishti.get_announcements",
                {
                    "query": {
                        "symbols": ["TCS"],
                        "from": "2026-11-10",
                        "to": "2026-11-24",
                        "limit": 1,
                        "page": 1,
                    }
                },
            ),
        ]
        if scope == "drishti":
            # Repair session: prioritize actual news/earnings/category paths, leaving
            # one data slot for a real returned earnings-detail selector.
            queries = [
                request
                for request in queries
                if request["operation"] not in {"drishti.get_symbols", "drishti.resolve_symbols"}
            ]
        admitted = []
        for request in queries:
            cap = capabilities[request["operation"]]
            if cap["enabled"]:
                admitted.append(request)
            else:
                summary["observations"].append(
                    {
                        "operation": request["operation"],
                        "status": "held_before_preview",
                        "reason": cap["held_reason"],
                        "http_attempts": 0,
                    }
                )
        # Reserve headroom for the SDK session DELETE and keep resumed diagnostics
        # within the aggregate budget. Never rerun BharatStock for a Drishti repair.
        available = max(
            0, service.ledger.limits["drishti"] - service.ledger.requests["drishti"] - 2
        )
        for request in admitted[available:]:
            summary["observations"].append(
                {
                    "operation": request["operation"],
                    "status": "not_run_remaining_http_budget",
                    "http_attempts": 0,
                }
            )
        dr = await batch(admitted[:available]) if available else []
        for result in dr:
            if result["operation"] == "drishti.get_news" and result["status"] == "success":
                imported = service.import_review_sources(
                    result["acceptance_run_id"], result["operation_id"], "NSE:RELIANCE"
                )
                save("retained-news-sources.json", imported)
                if imported["sources"]:
                    packet = service.review(
                        "sentiment.prepare_analysis",
                        {
                            "source_ids": [s["source_id"] for s in imported["sources"]],
                            "issuer": "NSE:RELIANCE",
                            "aspect": "company-related news",
                            "from": "2026-11-10",
                            "to": "2026-11-24",
                            "date_basis": "record_date",
                        },
                    )
                    save("news-review-packet.json", packet)
                    save(
                        "news-before-annotations.json",
                        service.review(
                            "sentiment.aggregate",
                            {k: packet[k] for k in ("packet_id", "packet_hash")},
                        ),
                    )
            if (
                result["operation"] == "drishti.list_earnings"
                and result["status"] == "success"
                and capabilities["drishti.get_earnings_filing"]["enabled"]
                and service.ledger.limits["drishti"] - service.ledger.requests["drishti"] >= 3
            ):
                rows = data_payload(result["payload"], result["payload_kind"]).get("data", [])
                if rows:
                    first = rows[0]
                    detail = (
                        {"earnings_id": first.get("earnings_id", first.get("id")), "detailed": True}
                        if first.get("earnings_id", first.get("id"))
                        else {
                            "symbol": first.get("symbol"),
                            "quarter": first.get("quarter"),
                            "detailed": True,
                        }
                    )
                    try:
                        await batch([op("drishti.get_earnings_filing", detail)])
                    except DomainError as error:
                        if error.code != "invalid_input":
                            raise
                        summary["observations"].append(
                            {
                                "operation": "drishti.get_earnings_filing",
                                "status": "no_valid_returned_selector",
                                "http_attempts": 0,
                            }
                        )
        summary["completed"] = True
    except DomainError as error:
        summary.update(completed=False, stopped={"code": error.code, "message": error.message})
    finally:
        await service.close()
        summary["ledger"] = service.ledger.snapshot()
        summary["finished_at"] = datetime.now(UTC).isoformat()
        save("summary.json", summary)
    print(
        json.dumps(
            {
                "report": str(output / "summary.json"),
                "completed": summary.get("completed", False),
                "ledger": summary["ledger"],
            }
        ),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-live", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scope", choices=["all", "drishti"], default="all")
    parser.add_argument("--drishti-http", type=int, choices=range(1, 21), default=20)
    args = parser.parse_args()
    asyncio.run(check(args.output.expanduser().absolute(), args.scope, args.drishti_http))


if __name__ == "__main__":
    main()
