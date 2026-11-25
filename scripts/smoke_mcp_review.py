"""Official SDK review-profile acceptance; fictional text, no provider/model calls."""

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
from mcp.shared.exceptions import MCPError


async def main(options):
    options.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    out = options.output.resolve()
    package = (options.package_root or Path(__file__).resolve().parents[1] / "src").resolve()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env.update(
        PYTHONPATH=str(package),
        MARGIN_BHARATSTOCK_REQUESTS="0",
        MARGIN_DRISHTI_REQUESTS="0",
        MARGIN_DRISHTI_CREDITS="0",
    )
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "margin.interfaces.mcp",
            "--mode",
            "synthetic",
            "--tool-profile",
            "review",
            "--record-dir",
            str(out / "logs"),
        ],
        env=env,
        cwd=str(out),
    )
    observations = []
    with (out / "stderr.txt").open("w") as stderr:
        async with stdio_client(params, errlog=stderr) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                assert "local review profile" in initialized.instructions
                tools = {tool.name: tool for tool in (await client.list_tools()).tools}
                assert (
                    len(tools) == 14 and "margin_review" not in tools and "margin_run" not in tools
                )

                async def call(name, values=None, error=False):
                    values = (values or {}) | {
                        "why": "Exercise fictional local review acceptance without provider calls."
                    }
                    result = await client.call_tool(name, values)
                    assert result.is_error is error, result.content
                    body = result.structured_content
                    assert json.loads(result.content[0].text) == body
                    Draft202012Validator(tools[name].output_schema).validate(body)
                    assert body["mode"] == "synthetic"
                    observations.append({"tool": name, "arguments": values, "result": body})
                    return body.get("data", body)

                status = await call("margin_status")
                assert status["package_version"] == initialized.server_info.version
                assert status["tool_profile"] == "review"
                catalog = await call("margin_catalog", {"group": "all", "include_schemas": True})
                assert set(catalog["groups"]) == {"review"}
                assert all(
                    row["mcp_execution"]["tool"] in tools for row in catalog["groups"]["review"]
                )
                workflows = await call("margin_review_workflows")
                assert workflows["workflows"][0]["mcp_steps"]
                assert workflows["workflows"][0]["citation_protocol"]["optional"] is True
                source = {
                    "issuer": "NSE:EXAMPLE",
                    "title": "Fictional review fixture",
                    "url": "https://example.invalid/review",
                    "kind": "provider_summary",
                    "date": "2026-11-01",
                    "date_kind": "published",
                    "passages": [
                        {"passage_id": "P1", "text": "Demand improved.", "locator": "summary"}
                    ],
                }
                registered = await call("margin_register_sources", {"sources": [source]})
                sid = registered["sources"][0]["source_id"]
                packet = await call(
                    "margin_prepare_verification",
                    {
                        "claims": [
                            {"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}
                        ],
                        "host_profile": {"host_read_sources": False, "structured_assessment": True},
                    },
                )
                assert (
                    packet["citation_protocol"]["recommended_action"] == "review_supplied_passages"
                )
                assert packet["citation_protocol"]["host_read_sources"] is False
                reviewer = {"host": "software-fixture", "model": "none"}
                quote = {"source_id": sid, "passage_id": "P1", "quote": "Demand improved."}
                action = packet["next_steps"][0]
                assert action["mcp_execution"]["tool"] == "margin_submit_assessment"
                submitted = await call(
                    action["mcp_execution"]["tool"],
                    action["bound_arguments"]
                    | {
                        "reviewer": reviewer,
                        "assessments": [
                            {
                                "claim_id": "C1",
                                "verdict": "supported",
                                "quotes": [quote],
                                "rationale": "Fictional supplied text explicitly states this.",
                            }
                        ],
                    },
                )
                action = submitted["next_steps"][0]
                rendered = await call(action["mcp_execution"]["tool"], action["bound_arguments"])
                assert rendered["citations"][0]["original_document_verified"] is False
                action = rendered["next_steps"][0]
                assert action["required_host_fields"] == ["claim_ids"]
                await call(
                    action["mcp_execution"]["tool"],
                    action["bound_arguments"] | {"claim_ids": ["C1"]},
                )
                fact = {
                    "issuer": "NSE:EXAMPLE",
                    "metric": "revenue",
                    "definition": "Fictional revenue",
                    "value": "100",
                    "unit": "INR",
                    "period_type": "annual",
                    "period_end": "2026-03-31",
                    "basis": "standalone",
                }
                compared = await call(
                    "margin_check_numeric_claim", {"claim": fact, "evidence": fact}
                )
                assert compared["numeric_check"] == "passed"
                sentiment = await call(
                    "margin_prepare_sentiment",
                    {
                        "source_ids": [sid],
                        "issuer": "NSE:EXAMPLE",
                        "aspect": "demand",
                        "from": "2026-11-01",
                        "to": "2026-11-25",
                        "date_basis": "published",
                    },
                )
                action = sentiment["next_steps"][0]
                annotated = await call(
                    action["mcp_execution"]["tool"],
                    action["bound_arguments"]
                    | {
                        "reviewer": reviewer,
                        "annotations": [
                            {
                                "source_id": sid,
                                "relevant": True,
                                "label": "positive",
                                "quotes": [quote],
                                "rationale": "Fictional positive label for improved demand.",
                            }
                        ],
                    },
                )
                action = annotated["next_steps"][0]
                aggregate = await call(action["mcp_execution"]["tool"], action["bound_arguments"])
                assert aggregate["balance"] == "1" and not aggregate["investor_sentiment"]
                await call(
                    "margin_result",
                    {"run_id": "fictional-absent", "operation_id": "fictional-absent"},
                    error=True,
                )
                await call(
                    "margin_review_sources",
                    {
                        "run_id": "fictional-absent",
                        "operation_id": "fictional-absent",
                        "issuer": "NSE:EXAMPLE",
                    },
                    error=True,
                )
                invalid = await call(
                    "margin_prepare_verification",
                    {"packet_id": "fictional-run-id", "packet_hash": "hash_12345"},
                    error=True,
                )
                assert "missing required fields: claims" in invalid["error"]["message"]
                assert "credentials" not in invalid["error"]["message"]
                try:
                    await client.call_tool("sentiment.prepare_analysis", {})
                except MCPError as error:
                    assert error.error.code == -32602
                    assert "margin_prepare_sentiment" in error.error.message
                else:
                    raise AssertionError("Function-as-tool must not execute as an alias.")
                final = await call("margin_status")
                assert final["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}
                assert final["ledger"]["completed_estimated_credits"] == 0
                assert {row["tool"] for row in observations} == set(tools)
    logs = list((out / "logs").glob("*.jsonl"))
    events = [json.loads(line) for path in logs for line in path.read_text().splitlines()]
    recorded_ids = {event["call_id"] for event in events}
    unrecorded = [row for row in observations if row["result"]["call_id"] not in recorded_ids]
    # Existing recording begins after outer tool-schema validation. The deliberate
    # malformed typed input is rejected before that point; retain it in observations.
    assert len(unrecorded) == 1 and unrecorded[0]["tool"] == "margin_prepare_verification"
    assert len(logs) == 1 and len(events) == (len(observations) - len(unrecorded)) * 2
    summary = {
        "status": "passed",
        "mode": "fictional_software_fixtures",
        "profile": "review",
        "version": initialized.server_info.version,
        "tools": len(tools),
        "calls": len(observations),
        "recorded_events": len(events),
        "frontend_unknown_tool_rejections": 1,
        "unrecorded_tool_schema_rejections": len(unrecorded),
        "real_provider_calls": 0,
        "model_calls": 0,
        "package_root": str(package),
    }
    for name, data in [("summary.json", summary), ("observations.json", observations)]:
        (out / name).write_text(json.dumps(data, indent=2) + "\n")
    for path in out.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--package-root", type=Path)
    asyncio.run(main(parser.parse_args()))
