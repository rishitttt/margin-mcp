"""Local review/host-capability contract check with caller-supplied real material.

No browsing, provider key, Margin LLM or professor evaluation. Judgments are supplied
by the host; successful quote checks are not independent semantic/source verification.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
from pathlib import Path

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.server import MarginMCP


async def main(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    material = json.loads(args.material.read_text())
    reader = json.loads(args.reader_source.read_text())
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    recorder = ToolRecorder(directory=output / "logs")
    owner = MarginMCP(service, recorder)
    observations = []

    async def call(name, values, expect_error=False):
        response = await owner.call(name, values)
        observations.append(
            {"tool": name, "arguments": values, "result": response.structured_content}
        )
        assert response.is_error is expect_error, response.structured_content
        return response.structured_content.get("error" if expect_error else "data")

    try:
        prepared = await call("margin_prepare_review", material["prepare"])
        submission = material["submit"] | {"review_id": prepared["review_id"]}
        bad = copy.deepcopy(submission)
        bad["claim_assessments"][0]["quote"] = (
            "This deliberately invalid quote is not in the supplied source."
        )
        rejected = await call("margin_submit_review", bad, True)
        assert rejected["code"] == "quote_mismatch"
        result = await call("margin_submit_review", submission)
        assert result["complete"] and result["judgment_origin"] == "host_reported"
        assert not result["original_document_verified"]
        assert [r["verdict"] for r in result["claims"]] == [
            r["verdict"] for r in submission["claim_assessments"]
        ]
        assert result == await call("margin_submit_review", submission)
        changed = copy.deepcopy(submission)
        changed["claim_assessments"][0]["rationale"] += " Changed submission."
        assert (await call("margin_submit_review", changed, True))["code"] == "assessment_conflict"

        source = reader["source"]
        locator = {k: copy.deepcopy(v) for k, v in source.items()}
        locator.update(kind="source_locator", passages=[])
        registered = await call("margin_register_sources", {"sources": [locator]})
        source_id = registered["sources"][0]["source_id"]
        claim = {"claim_id": "R1", "text": reader["claim"], "source_ids": [source_id]}
        capabilities = []
        for profile, expected in [
            (
                {"host_read_sources": False, "structured_assessment": True},
                "return_insufficient_evidence_or_inventory",
            ),
            (
                {"host_read_sources": True, "structured_assessment": True},
                "read_and_register_with_host_tools",
            ),
            ({}, "return_insufficient_evidence_or_inventory"),
            ({"structured_assessment": False}, "return_unreviewed_inventory"),
        ]:
            packet = await call(
                "margin_prepare_verification", {"claims": [claim], "host_profile": profile}
            )
            assert packet["citation_protocol"]["recommended_action"] == expected
            assert packet["citation_protocol"]["host_read_sources"] is profile.get(
                "host_read_sources"
            )
            capabilities.append({"declaration": profile, "action": expected})
            if profile.get("structured_assessment") is False:
                refusal = await call(
                    "margin_submit_assessment",
                    {
                        "packet_id": packet["packet_id"],
                        "packet_hash": packet["packet_hash"],
                        "reviewer": submission["reviewer"],
                        "assessments": [
                            {
                                "claim_id": "R1",
                                "verdict": "insufficient_evidence",
                                "quotes": [],
                                "rationale": "Inventory-only host cannot submit an assessment.",
                            }
                        ],
                    },
                    True,
                )
                assert refusal["code"] == "unsupported_assessment"

        # Host has actually read this short public page passage outside Margin.
        registered = await call("margin_register_sources", {"sources": [source]})
        read_id = registered["sources"][0]["source_id"]
        packet = await call(
            "margin_prepare_verification",
            {
                "claims": [claim | {"source_ids": [read_id]}],
                "host_profile": {"host_read_sources": True, "structured_assessment": True},
            },
        )
        assert packet["citation_protocol"]["recommended_action"] == "review_supplied_passages"
        await call(
            "margin_submit_assessment",
            {
                "packet_id": packet["packet_id"],
                "packet_hash": packet["packet_hash"],
                "reviewer": submission["reviewer"],
                "assessments": [
                    {
                        "claim_id": "R1",
                        "verdict": "supported",
                        "quotes": [
                            {
                                "source_id": read_id,
                                "passage_id": source["passages"][0]["passage_id"],
                                "quote": reader["quote"],
                            }
                        ],
                        "rationale": "Host-read passage explicitly supports the description; authenticity remains unverified.",
                    }
                ],
            },
        )
        rendered = await call(
            "margin_render_citations",
            {"packet_id": packet["packet_id"], "packet_hash": packet["packet_hash"]},
        )
        assert not rendered["citations"][0]["original_document_verified"]
        relevance = None
        if args.irrelevant_source:
            supplied = json.loads(args.irrelevant_source.read_text())
            registered = await call("margin_register_sources", {"sources": [supplied]})
            sid = registered["sources"][0]["source_id"]
            packet = await call(
                "margin_prepare_sentiment",
                {
                    "source_ids": [sid],
                    "issuer": "NSE:INFY",
                    "aspect": "Investor event scheduling",
                    "from": "2026-11-10",
                    "to": "2026-11-27",
                    "date_basis": "record_date",
                },
            )
            reference = {k: packet[k] for k in ("packet_id", "packet_hash")}
            unannotated = await call("margin_aggregate_sentiment", reference)
            assert (
                unannotated["counts"]["unannotated"] == 1
                and unannotated["balance_denominator"] == 0
            )
            await call(
                "margin_submit_annotations",
                reference
                | {
                    "reviewer": submission["reviewer"],
                    "annotations": [
                        {
                            "source_id": sid,
                            "relevant": False,
                            "label": "unclear",
                            "quotes": [],
                            "rationale": "Host read the supplied item: unrelated to Infosys investor-event scheduling despite the provider symbol filter.",
                        }
                    ],
                },
            )
            relevance = await call("margin_aggregate_sentiment", reference)
            assert (
                relevance["counts"]["irrelevant"] == 1
                and relevance["balance_denominator"] == 0
                and relevance["balance"] is None
            )
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
        summary = {
            "status": "passed",
            "kind": "product_host_handoff_with_explicit_Codex_host_judgments_not_model_benchmark",
            "claim_verdicts": [r["verdict"] for r in result["claims"]],
            "sentiment_counts": result["sentiment"]["counts"],
            "reader_capability_cases": capabilities,
            "host_read_source_url": source["url"],
            "original_document_verified": False,
            "provider_requests": 0,
            "margin_llm_calls": 0,
            "wrong_quote": "rejected atomically",
            "changed_submission": "conflict",
            "identical_replay": "same report",
            "irrelevant_source": "excluded, zero balance denominator"
            if relevance
            else "not supplied",
            "calls": len(observations),
        }
        (output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary))
    finally:
        await service.close()
        recorder.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    parser.add_argument("--reader-source", type=Path, required=True)
    parser.add_argument("--irrelevant-source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
