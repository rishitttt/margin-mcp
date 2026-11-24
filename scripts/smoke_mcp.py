"""Real stdio SDK acceptance with fictional data; refuses non-synthetic mode."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(args):
    args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    root = Path(__file__).resolve().parents[1]
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("MARGIN_") and key not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}
    }
    env.update(
        PYTHONPATH=str(args.package_root or root / "src"),
        MARGIN_BHARATSTOCK_REQUESTS="2",
        MARGIN_DRISHTI_REQUESTS="12",
        MARGIN_DRISHTI_CREDITS="6",
    )
    log = args.output.resolve() / "tools.jsonl"
    server_args = ["--mode", "synthetic", "--record-file", str(log)]
    params = StdioServerParameters(
        command=str(args.entrypoint or sys.executable),
        args=server_args if args.entrypoint else ["-m", "margin.interfaces.mcp", *server_args],
        env=env,
        cwd=str(args.output.resolve()),
    )
    observations = []
    tools = {}

    async def call(session, name, arguments=None, expect_error=False):
        arguments = (arguments or {}) | {
            "why": "Exercise the fictional MCP acceptance path without real provider calls."
        }
        response = await session.call_tool(name, arguments)
        assert response.is_error is expect_error, response.content
        body = response.structured_content
        assert json.loads(response.content[0].text) == body
        Draft202012Validator(tools[name].output_schema).validate(body)
        assert body["mode"] == "synthetic"
        observations.append({"tool": name, "arguments": arguments, "result": body})
        return body

    with (args.output / "stderr.txt").open("w") as stderr:
        async with stdio_client(params, errlog=stderr) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                assert len(tools) == 20
                status = await call(session, "margin_status")
                assert not any(status["data"]["ledger"]["http_attempts"].values())
                session_id = status["session_id"]
                catalog = (await call(session, "margin_catalog"))["data"]["groups"]
                assert [
                    len(catalog[k]) for k in ["retrieval", "calculations", "company", "review"]
                ] == [13, 15, 9, 10]
                exact = await call(
                    session,
                    "margin_catalog",
                    {"group": "company", "name": "company_data_readiness", "include_schemas": True},
                )
                assert exact["data"]["groups"]["company"][0]["planning_schema"]

                async def run(plan, key):
                    args = {
                        "session_id": session_id,
                        "plan_id": plan["plan_id"],
                        "idempotency_key": key,
                    }
                    started = (await call(session, "margin_run", args))["data"]
                    state = (
                        await call(
                            session,
                            "margin_run_status",
                            {"run_id": started["run_id"], "wait_seconds": 2},
                        )
                    )["data"]
                    assert state["status"] not in {"queued", "running"}
                    return state

                plan = (
                    await call(
                        session,
                        "margin_company_preview",
                        {
                            "function": "finance.company_data_readiness",
                            "ticker": "SYNTHA",
                            "exchange": "NSE",
                            "fetch_missing": True,
                        },
                    )
                )["data"]
                run_state = await run(plan, "mcp-smoke-company")
                again = (
                    await call(
                        session,
                        "margin_run",
                        {
                            "session_id": session_id,
                            "plan_id": plan["plan_id"],
                            "idempotency_key": "mcp-smoke-company",
                        },
                    )
                )["data"]
                assert again["run_id"] == run_state["run_id"]
                result = (
                    await call(
                        session,
                        "margin_result",
                        {
                            "run_id": run_state["run_id"],
                            "operation_id": run_state["operations"][-1]["operation_id"],
                        },
                    )
                )["data"]
                assert (
                    result["payload"]["values"]["valuation_readiness"]["status"]
                    == "needs_explicit_inputs"
                )
                source = (await call(session, "margin_sources"))["data"]["sources"][0]
                facts = (
                    await call(
                        session, "margin_facts", {k: source[k] for k in ["run_id", "operation_id"]}
                    )
                )["data"]["facts"]
                assert all(f["unit_origin"] == "provider_documentation" for f in facts)
                latest = max(f["period_end"] for f in facts if f["period_end"])
                current = {f["metric"]: f for f in facts if f["period_end"] == latest}
                revenue = current["revenue"]
                await call(
                    session, "margin_convert_units", {"value": revenue, "target_unit": "INR_crore"}
                )
                await call(
                    session,
                    "margin_calculate_margins",
                    {"profit": current["net_profit"], "revenue": revenue},
                )
                await call(
                    session,
                    "margin_calculate_cashflow_metrics",
                    {
                        "cfo": current["cash_flow_operating"],
                        "capex": current.get(
                            "capex",
                            revenue
                            | {
                                "metric": "capex",
                                "value": None,
                                "definition": "Capex absent in this fictional software fixture",
                                "source": {"kind": "software_fixture_missing_field"},
                            },
                        ),
                    },
                )
                await call(
                    session, "margin_calculate_profitability", {"facts": list(current.values())}
                )
                await call(
                    session,
                    "margin_calculate_balance_sheet_metrics",
                    {"facts": list(current.values())},
                )
                previous = next(
                    f for f in facts if f["metric"] == "revenue" and f["period_end"] != latest
                )
                await call(
                    session, "margin_compare_periods", {"previous": previous, "current": revenue}
                )
                metric = (
                    await call(
                        session,
                        "margin_calculate",
                        {
                            "function": "finance.calculate_fcff",
                            "arguments": {
                                "ebit": "100",
                                "tax_rate": "0.25",
                                "depreciation": "10",
                                "capex": "20",
                                "change_in_working_capital": "5",
                                "amount_unit": "INR",
                            },
                        },
                    )
                )["data"]
                assert metric["values"]["fcff"] == "60.00"
                await call(
                    session,
                    "margin_run",
                    {
                        "session_id": "stale-process",
                        "plan_id": plan["plan_id"],
                        "idempotency_key": "do-not-dispatch",
                    },
                    expect_error=True,
                )
                await call(session, "margin_cancel", {"run_id": run_state["run_id"]})

                await call(session, "margin_connect_drishti", {"session_id": session_id})
                plan = (
                    await call(
                        session,
                        "margin_preview",
                        {
                            "operations": [
                                {
                                    "operation": "drishti.get_news",
                                    "arguments": {
                                        "query": {
                                            "symbols": ["SYNTHA"],
                                            "lookback_days": 7,
                                            "page": 1,
                                            "limit": 1,
                                        }
                                    },
                                }
                            ]
                        },
                    )
                )["data"]
                state = await run(plan, "mcp-smoke-news")
                imported = (
                    await call(
                        session,
                        "margin_review_sources",
                        {
                            "run_id": state["run_id"],
                            "operation_id": state["operations"][0]["operation_id"],
                            "issuer": "NSE:SYNTHA",
                        },
                    )
                )["data"]
                assert imported["sources"]

                async def review(function, arguments):
                    return (
                        await call(
                            session, "margin_review", {"function": function, "arguments": arguments}
                        )
                    )["data"]

                workflows = await review("protocols.list_workflows", {})
                assert workflows["workflows"]
                source = {
                    "issuer": "NSE:SYNTHA",
                    "title": "Fictional supplied passage",
                    "url": "https://example.invalid/fictional-report",
                    "kind": "original_document",
                    "date": "2026-11-01",
                    "date_kind": "published",
                    "passages": [
                        {"passage_id": "P1", "text": "Demand improved.", "locator": "page 1"}
                    ],
                }
                sid = (await review("evidence.register_sources", {"sources": [source]}))["sources"][
                    0
                ]["source_id"]
                packet = await review(
                    "evidence.prepare_verification",
                    {
                        "claims": [
                            {"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}
                        ]
                    },
                )
                ref = {k: packet[k] for k in ["packet_id", "packet_hash"]}
                await review(
                    "evidence.submit_assessment",
                    ref
                    | {
                        "reviewer": {"host": "software-fixture", "model": "none"},
                        "assessments": [
                            {
                                "claim_id": "C1",
                                "verdict": "supported",
                                "rationale": "Supplied fictional passage says this.",
                                "quotes": [
                                    {
                                        "source_id": sid,
                                        "passage_id": "P1",
                                        "quote": "Demand improved.",
                                    }
                                ],
                            }
                        ],
                    },
                )
                citations = await review("evidence.render_citations", ref)
                assert citations["citations"]
                sentiment = await review(
                    "sentiment.prepare_analysis",
                    {
                        "source_ids": [sid],
                        "issuer": "NSE:SYNTHA",
                        "aspect": "demand",
                        "from": "2026-11-01",
                        "to": "2026-11-25",
                        "date_basis": "published",
                    },
                )
                sr = {k: sentiment[k] for k in ["packet_id", "packet_hash"]}
                await review(
                    "sentiment.submit_annotations",
                    sr
                    | {
                        "reviewer": {"host": "software-fixture", "model": "none"},
                        "annotations": [
                            {
                                "source_id": sid,
                                "relevant": True,
                                "label": "positive",
                                "rationale": "Fictional annotation for a protocol test.",
                                "quotes": [
                                    {
                                        "source_id": sid,
                                        "passage_id": "P1",
                                        "quote": "Demand improved.",
                                    }
                                ],
                            }
                        ],
                    },
                )
                balance = await review("sentiment.aggregate", sr)
                assert balance["counts"]["positive"] == 1 and not balance["investor_sentiment"]
                final = (await call(session, "margin_status"))["data"]
                assert final["ledger"]["http_attempts"]["bharatstock"] == 1
                assert {o["tool"] for o in observations} == set(tools)

    events = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(events) == len(observations) * 2
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    assert all(o["result"]["call_id"] in {e["call_id"] for e in events} for o in observations)
    for path in args.output.iterdir():
        assert b"synthetic-private-key-never-forward" not in path.read_bytes()
        path.chmod(0o600)
    summary = {
        "status": "passed",
        "mode": "fictional_software_fixtures",
        "protocol_version": initialized.protocol_version,
        "server_version": initialized.server_info.version,
        "tools": len(tools),
        "calls": len(observations),
        "recorded_events": len(events),
        "catalog_counts": {k: len(v) for k, v in catalog.items()},
        "real_provider_calls": 0,
        "model_calls": 0,
        "fictional_ledger": final["ledger"],
        "entrypoint": str(args.entrypoint) if args.entrypoint else "source module",
        "isolated_package_root": str(args.package_root) if args.package_root else None,
    }
    for name, value in [("observations.json", observations), ("summary.json", summary)]:
        path = args.output / name
        path.write_text(json.dumps(value, indent=2) + "\n")
        path.chmod(0o600)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--entrypoint", type=Path, help="Optional installed margin-mcp executable")
    parser.add_argument(
        "--package-root", type=Path, help="Optional isolated installed package directory"
    )
    asyncio.run(main(parser.parse_args()))
