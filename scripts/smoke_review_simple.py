"""Official-SDK three-tool acceptance. Fictional source/host labels, zero provider calls."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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
            "review-simple",
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
                assert "review-simple" in initialized.instructions
                tools = (await client.list_tools()).tools
                assert {t.name for t in tools} == {
                    "margin_status",
                    "margin_prepare_review",
                    "margin_submit_review",
                }

                async def call(name, args=None):
                    result = await client.call_tool(
                        name,
                        (args or {})
                        | {
                            "why": "Fictional three-tool SDK acceptance; no provider or model calls."
                        },
                    )
                    body = result.structured_content
                    assert not result.is_error, body
                    assert body == json.loads(result.content[0].text)
                    observations.append({"tool": name, "result": body})
                    return body["data"]

                before = await call("margin_status")
                assert before["tool_profile"] == "review-simple" and before["advertised_tools"] == 3
                assert before["review_readiness"]["provider_auth_required"] is False
                prepared = await call(
                    "margin_prepare_review",
                    {
                        "issuer": "NSE:EXAMPLE",
                        "title": "Fictional SDK input",
                        "source_url": "https://example.invalid/source#summary",
                        "source_text": "Demand improved.",
                        "record_date": "2026-11-25",
                        "publication_date": None,
                        "claims": ["Demand improved.", "Investors became bullish."],
                        "sentiment": {
                            "aspect": "demand",
                            "from": "2026-11-10",
                            "to": "2026-11-25",
                            "date_basis": "record_date",
                        },
                    },
                )
                step = prepared["next_steps"][0]
                assert step["mcp_execution"]["tool"] == "margin_submit_review"
                assert step["bound_arguments"] == {"review_id": prepared["review_id"]}
                values = step["bound_arguments"] | {
                    "claim_assessments": [
                        {
                            "verdict": "supported",
                            "quote": "Demand improved.",
                            "rationale": "Fictional host judgment.",
                        },
                        {
                            "verdict": "insufficient_evidence",
                            "quote": None,
                            "rationale": "No investor reaction in supplied text.",
                        },
                    ],
                    "sentiment_annotation": {
                        "relevant": True,
                        "label": "positive",
                        "quote": "Demand improved.",
                        "rationale": "Fictional host label.",
                    },
                }
                result = await call("margin_submit_review", values)
                assert result["complete"] and result["support_audit"]["status"] == "incomplete"
                assert result["sentiment"]["counts"]["positive"] == 1
                assert (
                    not result["original_document_verified"]
                    and not result["sentiment"]["investor_sentiment"]
                )
                assert await call("margin_submit_review", values) == result
                after = await call("margin_status")
                assert before["ledger"] == after["ledger"]
    events = [
        json.loads(line)
        for p in (out / "logs").glob("*.jsonl")
        for line in p.read_text().splitlines()
    ]
    assert len(events) == len(observations) * 2
    summary = {
        "status": "passed",
        "version": initialized.server_info.version,
        "profile": "review-simple",
        "tools": 3,
        "calls": len(observations),
        "events": len(events),
        "real_provider_calls": 0,
        "model_calls": 0,
        "package_root": str(package),
        "tool_definition_bytes": len(
            json.dumps(
                [t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in tools],
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode()
        ),
        "instruction_bytes": len(initialized.instructions.encode()),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
    for path in out.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--package-root", type=Path)
    asyncio.run(main(parser.parse_args()))
