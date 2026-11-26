"""Professor demo: saved source + explicit operator judgments through the installed MCP."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class DemoError(Exception):
    pass


def failure_message(error):
    pending = [error]
    for _ in range(16):
        if not pending:
            break
        item = pending.pop(0)
        if isinstance(item, DemoError):
            return str(item)
        if isinstance(item, BaseExceptionGroup):
            pending.extend(item.exceptions[:8])
    return type(error).__name__


def validate_input(spec):
    if not isinstance(spec, dict) or spec.get("judgment_origin") != "operator_supplied":
        raise DemoError("Input must explicitly declare operator_supplied judgments.")
    if not isinstance(spec.get("source"), dict) or not spec["source"].get("passages"):
        raise DemoError("Supply real source metadata and passages; nothing is generated.")
    if not isinstance(spec.get("claims"), list) or not 1 <= len(spec["claims"]) <= 8:
        raise DemoError("Supply one to eight claims and operator assessments.")
    for claim in spec["claims"]:
        if (
            not isinstance(claim, dict)
            or not {"claim_id", "text", "verdict", "rationale"} <= claim.keys()
        ):
            raise DemoError("Each claim needs its text and explicit operator verdict/rationale.")
    if (
        not isinstance(spec.get("sentiment"), dict)
        or not {"aspect", "from", "to", "date_basis", "label", "rationale"}
        <= spec["sentiment"].keys()
    ):
        raise DemoError("Supply sentiment scope and an explicit operator label/rationale.")


async def run_demo(client, spec, *, expected_mode="live", emit=print, observations=None):
    validate_input(spec)
    observations = observations if observations is not None else []
    tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    async def call(name, arguments=None):
        if name not in tools:
            raise DemoError("Required review tool is not advertised: " + name)
        arguments = (arguments or {}) | {
            "why": "Professor demo with operator-supplied judgments; no model inference or provider retrieval."
        }
        if not Draft202012Validator(tools[name].input_schema).is_valid(arguments):
            raise DemoError("Demo input does not match advertised schema for " + name)
        result = await client.call_tool(name, arguments)
        body = result.structured_content
        observations.append({"tool": name, "result": body})
        if not isinstance(body, dict):
            raise DemoError("Expected a structured Margin MCP result; stopped.")
        if result.is_error:
            raise DemoError(
                name
                + ": "
                + body.get("error", {}).get("code", "tool_error")
                + "; stopped without retry."
            )
        return body["data"]

    status = await call("margin_status")
    if status["mode"] != expected_mode or status["tool_profile"] != "review":
        raise DemoError("Use a matching review frontend and the expected backend mode.")
    ledger = status["ledger"]
    if any(ledger["http_limits"].values()) or ledger["estimated_credit_limit"]:
        raise DemoError(
            "This demo requires zero provider/credit allowances; no backend was changed."
        )
    emit(
        f"Margin MCP {status['package_version']} | mode={status['mode']} | provider retrieval disabled"
    )
    emit("Saved supplied text. Judgments are provided by the demo operator; Margin runs no LLM.")
    registration = await call("margin_register_sources", {"sources": [spec["source"]]})
    source = registration["sources"][0]
    if registration.get("input_normalizations"):
        emit("URL normalization: plain anchor removed; passage text preserved")
    sid = source["source_id"]
    emit("Source registered: " + sid)
    emit("Title: " + source["title"])
    packet = await call(
        "margin_prepare_verification",
        {
            "claims": [
                {"claim_id": c["claim_id"], "text": c["text"], "source_ids": [sid]}
                for c in spec["claims"]
            ],
            "host_profile": {"host_read_sources": False, "structured_assessment": True},
        },
    )
    emit("Citation packet: " + packet["packet_id"])

    def refs(packet):
        return {key: packet[key] for key in ("packet_id", "packet_hash")}

    reviewer = {"host": "professor-demo", "model": "operator-supplied-no-llm"}

    def quotes(item):
        return (
            [
                {
                    "source_id": sid,
                    "passage_id": item.get("passage_id", source["passages"][0]["passage_id"]),
                    "quote": item["quote"],
                }
            ]
            if item.get("quote")
            else []
        )

    submitted = await call(
        "margin_submit_assessment",
        refs(packet)
        | {
            "reviewer": reviewer,
            "assessments": [
                {
                    "claim_id": c["claim_id"],
                    "verdict": c["verdict"],
                    "rationale": c["rationale"],
                    "quotes": quotes(c),
                }
                for c in spec["claims"]
            ],
        },
    )
    await call("margin_render_citations", refs(packet))
    audit = await call(
        "margin_audit_answer", refs(packet) | {"claim_ids": [c["claim_id"] for c in spec["claims"]]}
    )
    for item in submitted["assessment"]["assessments"]:
        claim_text = next(c["text"] for c in spec["claims"] if c["claim_id"] == item["claim_id"])
        emit(f"  {item['claim_id']}: {claim_text} -> {item['verdict']} (operator judgment)")
    emit("Assessment coverage: " + submitted["assessment_coverage"]["status"])
    emit("Claim-support audit: " + audit["status"] + " — " + json.dumps(audit["assessment_counts"]))
    if (
        audit["status"] == "incomplete"
        and audit["assessment_coverage"]["status"] == "host_assessed"
    ):
        emit(
            "All claims were assessed; at least one is not fully supported by the supplied evidence."
        )
    scope = spec["sentiment"]
    sentiment = await call(
        "margin_prepare_sentiment",
        {
            "source_ids": [sid],
            "issuer": source["issuer"],
            **{key: scope[key] for key in ("aspect", "from", "to", "date_basis")},
            "host_profile": {"host_read_sources": False, "structured_assessment": True},
        },
    )
    if not sentiment["sources"]:
        raise DemoError("No eligible source in the supplied sentiment date scope.")
    emit("Sentiment packet: " + sentiment["packet_id"])
    await call(
        "margin_submit_annotations",
        refs(sentiment)
        | {
            "reviewer": reviewer,
            "annotations": [
                {
                    "source_id": sid,
                    "relevant": True,
                    "label": scope["label"],
                    "rationale": scope["rationale"],
                    "quotes": quotes(scope),
                }
            ],
        },
    )
    aggregate = await call("margin_aggregate_sentiment", refs(sentiment))
    emit(
        f"Content scope: {source['issuer']} | {scope['aspect']} | {scope['from']} to {scope['to']} | {scope['date_basis']}"
    )
    emit("Content-sentiment counts: " + json.dumps(aggregate["counts"]))
    emit(f"Balance: {aggregate['balance']} | denominator: {aggregate['balance_denominator']}")
    emit("Original independently verified: false | Comprehensive investor sentiment: false")
    final = await call("margin_status")
    if final["ledger"]["http_attempts"] != ledger["http_attempts"]:
        raise DemoError("Shared provider counters changed during the demo; inspect other clients.")
    emit("Provider HTTP attempts added by this isolated review sequence: 0")
    return {
        "package_version": status["package_version"],
        "mode": status["mode"],
        "judgment_origin": "operator_supplied",
        "source_id": sid,
        "citation_packet_id": packet["packet_id"],
        "sentiment_packet_id": sentiment["packet_id"],
        "audit": audit,
        "sentiment": aggregate,
        "provider_attempt_delta": 0,
    }


async def main(options):
    raw = options.input.read_bytes()
    if len(raw) > 65536:
        raise DemoError("Demo input exceeds 64 KiB.")
    spec = json.loads(raw)
    validate_input(spec)
    out = options.output or Path("reports/private") / (
        "professor-demo-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    )
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    params = StdioServerParameters(
        command=str(options.executable),
        args=[
            "--backend-socket",
            str(options.backend_socket),
            "--mode",
            "live",
            "--tool-profile",
            "review",
        ],
        env=env,
    )
    observations = []
    try:
        with (out / "frontend-stderr.txt").open("w") as stderr:
            async with stdio_client(params, errlog=stderr) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    result = await run_demo(client, spec, observations=observations)
        (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print("Private demo results: " + str(out.resolve()))
    finally:
        (out / "tool-observations.json").write_text(
            json.dumps(observations, ensure_ascii=False, indent=2) + "\n"
        )
        for path in out.iterdir():
            if path.is_file():
                path.chmod(0o600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--backend-socket", type=Path, required=True)
    parser.add_argument(
        "--executable", type=Path, default=Path(sys.executable).with_name("margin-mcp")
    )
    parser.add_argument("--output", type=Path)
    try:
        asyncio.run(main(parser.parse_args()))
    except Exception as error:
        print(
            "Demo stopped: " + failure_message(error),
            file=sys.stderr,
        )
        sys.exit(1)
