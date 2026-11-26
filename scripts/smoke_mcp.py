"""Real stdio SDK acceptance with fictional data; refuses non-synthetic mode."""

from __future__ import annotations

import argparse
import asyncio
import copy
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
        PYTHONPATH=str((args.package_root or root / "src").resolve()),
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
                assert len(tools) == 37
                status = await call(session, "margin_status")
                assert not any(status["data"]["ledger"]["http_attempts"].values())
                session_id = status["session_id"]
                catalog = (await call(session, "margin_catalog"))["data"]["groups"]
                assert [
                    len(catalog[k]) for k in ["retrieval", "calculations", "company", "review"]
                ] == [13, 15, 9, 12]
                exact = await call(
                    session,
                    "margin_catalog",
                    {"group": "company", "name": "company_data_readiness", "include_schemas": True},
                )
                assert exact["data"]["groups"]["company"][0]["planning_schema"]
                contract = exact["data"]["company_execution_contract"]
                assert contract["provider"] == "bharatstock"
                assert contract["execution"]["maximum_provider_requests"] == {
                    "bharatstock": 1,
                    "drishti": 0,
                }
                assert contract["execution"]["session_id_required"] is False
                assert contract["preview"]["execute"] is False

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
                for tool in (
                    "margin_preview_news",
                    "margin_preview_announcements",
                    "margin_preview_earnings",
                    "margin_preview_earnings_filing",
                ):
                    preview_arguments = (
                        {"earnings_id": "fictional-filing-001", "detailed": True}
                        if tool.endswith("filing")
                        else {"symbols": ["SYNTHA"], "lookback_days": 7, "page": 1, "limit": 1}
                    )
                    typed_plan = (await call(session, tool, preview_arguments))["data"]
                    assert typed_plan["data_operations"] == {"bharatstock": 0, "drishti": 1}
                    assert typed_plan["plan_id"]
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

                review_inputs = {}

                async def review(function, arguments):
                    review_inputs[function] = copy.deepcopy(arguments)
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
                await review("evidence.audit_answer", ref | {"claim_ids": ["C1"]})
                numeric_fact = {
                    "issuer": "NSE:SYNTHA",
                    "metric": "revenue",
                    "definition": "Fictional revenue",
                    "value": "100",
                    "unit": "INR",
                    "period_type": "annual",
                    "period_end": "2026-03-31",
                    "basis": "standalone",
                }
                await review(
                    "evidence.check_numeric_claim",
                    {"claim": numeric_fact, "evidence": numeric_fact},
                )
                from margin.interfaces.mcp.tools import DIRECT_REVIEWS

                for tool, function in DIRECT_REVIEWS.items():
                    if function in review_inputs:
                        await call(session, tool, review_inputs[function])
                fresh_inputs = {
                    "function": "finance.company_margins",
                    "ticker": "SYNTHA",
                    "execute": True,
                    "idempotency_key": "mcp-smoke-fresh-finance",
                }
                preview = await call(
                    session,
                    "margin_company_finance",
                    {
                        k: v
                        for k, v in fresh_inputs.items()
                        if k not in {"execute", "idempotency_key"}
                    },
                )
                assert preview["data"]["status"] == "preview"
                step = preview["data"]["next_steps"][0]
                assert step["mcp_execution"]["tool"] == "margin_company_finance"
                assert step["required_host_fields"] == ["idempotency_key"]
                assert step["requires_execution_authorization"] and not step["creates_plan_id"]
                assert step["do_not_use_tools"] == ["margin_run"]
                execution = step["bound_arguments"] | {
                    "idempotency_key": fresh_inputs["idempotency_key"]
                }
                fresh = await call(session, step["mcp_execution"]["tool"], execution)
                assert fresh["data"]["status"] == "success"
                assert fresh["data"]["request_lifecycle"]["state"] == "finished"
                duplicate = await call(session, "margin_company_finance", fresh_inputs)
                assert duplicate["data"] == fresh["data"]
                assert (
                    len([row for row in fresh["data"]["report"]["rows"] if row["kind"] == "input"])
                    == 2
                )
                assert "details" not in fresh["data"]
                inspected = await call(
                    session, "margin_company_finance", fresh_inputs | {"include_details": True}
                )
                assert inspected["data"]["report"] == fresh["data"]["report"]
                assert inspected["data"]["details"]["inputs"][1]["unit"] == "INR"
                high = (
                    await call(
                        session,
                        "margin_prepare_review",
                        {
                            "issuer": "NSE:EXAMPLE",
                            "title": "Fictional high-level review",
                            "source_url": "https://example.invalid/high-level",
                            "source_text": "Demand improved.",
                            "record_date": "2026-11-25",
                            "claims": ["Demand improved."],
                        },
                    )
                )["data"]
                high_result = (
                    await call(
                        session,
                        "margin_submit_review",
                        {
                            "review_id": high["review_id"],
                            "claim_assessments": [
                                {
                                    "verdict": "supported",
                                    "quote": "Demand improved.",
                                    "rationale": "Fictional host judgment.",
                                }
                            ],
                        },
                    )
                )["data"]
                assert (
                    high_result["complete"] and high_result["claims"][0]["verdict"] == "supported"
                )
                final = (await call(session, "margin_status"))["data"]
                assert final["ledger"]["http_attempts"]["bharatstock"] == 2
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
        "isolated_package_root": str(args.package_root.resolve()) if args.package_root else None,
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
