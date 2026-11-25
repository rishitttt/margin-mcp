"""Fictional source text checks routing/state contracts, not independent judgments."""

import copy
import math

import pytest
from jsonschema import Draft202012Validator

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.evidence.sanitize import Sanitizer
from margin.interfaces.mcp.server import MarginMCP
from margin.interfaces.mcp.tools import DIRECT_REVIEWS, definitions
from margin.protocols.schemas import SCHEMAS
from margin.protocols.service import ReviewService, digest


def source():
    return {
        "issuer": "NSE:EXAMPLE",
        "title": "Fictional supplied text",
        "url": "https://example.invalid/review",
        "kind": "provider_summary",
        "date": "2026-11-01",
        "date_kind": "published",
        "passages": [{"passage_id": "P1", "text": "Demand improved.", "locator": "summary"}],
    }


@pytest.fixture
async def adapter():
    service = ResearchService(
        Settings(bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def call(adapter, tool, values=None, error=False):
    result = await adapter.call(tool, values or {})
    assert result.is_error is error, result.structured_content
    Draft202012Validator(adapter.tools[tool].output_schema).validate(result.structured_content)
    return result.structured_content.get("data", result.structured_content)


def ref(packet):
    return {k: packet[k] for k in ("packet_id", "packet_hash")}


def quote(sid, text="Demand improved."):
    return {"source_id": sid, "passage_id": "P1", "quote": text}


@pytest.mark.parametrize("tool,function", DIRECT_REVIEWS.items())
def test_review_tool_schema_is_exact_core_copy_without_wrapper_or_mutation(tool, function):
    schema = definitions()[tool].input_schema
    expected = copy.deepcopy(SCHEMAS[function])
    schema["properties"].pop("why")
    assert schema == expected
    schema["properties"].clear()
    assert SCHEMAS[function] == expected
    assert definitions()[tool].input_schema["properties"]


async def test_typed_citation_roundtrip_uses_real_next_steps_and_keeps_snapshot_immutable(adapter):
    before = adapter.service.ledger.snapshot()
    registration = await call(adapter, "margin_register_sources", {"sources": [source()]})
    sid = registration["sources"][0]["source_id"]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {
            "claims": [
                {
                    "claim_id": "C1",
                    "text": "The fictional summary reports better demand.",
                    "source_ids": [sid],
                }
            ],
            "host_profile": {"host_search": False, "structured_assessment": True},
        },
    )
    stored = copy.deepcopy(adapter.service.reviews.packets[packet["packet_id"]][1])
    hashed = copy.deepcopy(stored)
    hashed.pop("packet_hash")
    assert digest(hashed) == packet["packet_hash"]
    assert "next_steps" not in stored
    assert packet["sources"][0]["original_document_verified"] is False
    step = packet["next_steps"][0]
    assert step["mcp_execution"]["tool"] == "margin_submit_assessment"
    assert step["bound_arguments"] == ref(packet)
    assert step["required_host_fields"] == ["reviewer", "assessments"]
    assert not step["is_complete_input"]
    reviewer = {"host": "fictional-test", "model": "fixture"}
    assessment = {
        "claim_id": "C1",
        "verdict": "supported",
        "quotes": [quote(sid)],
        "rationale": "Fictional supplied passage explicitly reports improved demand.",
    }
    bad = await call(
        adapter,
        "margin_submit_assessment",
        ref(packet)
        | {
            "reviewer": reviewer,
            "assessments": [assessment | {"quotes": [quote(sid, "Invented absent text")]}],
        },
        error=True,
    )
    assert bad["error"]["code"] == "quote_mismatch"
    assert adapter.service.reviews.packets[packet["packet_id"]][1] == stored
    submitted = await call(
        adapter,
        step["mcp_execution"]["tool"],
        step["bound_arguments"]
        | {
            "reviewer": reviewer,
            "assessments": [assessment],
        },
    )
    next_step = submitted["next_steps"][0]
    assert next_step["is_complete_input"]
    rendered = await call(adapter, next_step["mcp_execution"]["tool"], next_step["bound_arguments"])
    assert rendered["citations"][0]["reviewer_origin"] == "host_reported"
    assert not rendered["citations"][0]["original_document_verified"]
    audit = rendered["next_steps"][0]
    assert (
        audit["required_host_fields"] == ["claim_ids"]
        and "claim_ids" not in audit["bound_arguments"]
    )
    result = await call(
        adapter, audit["mcp_execution"]["tool"], audit["bound_arguments"] | {"claim_ids": ["C1"]}
    )
    assert result["status"] == "success"
    step["bound_arguments"]["packet_hash"] = "0" * 64
    assert (
        adapter.service.reviews.packets[packet["packet_id"]][1]["packet_hash"]
        == ref(packet)["packet_hash"]
    )
    assert adapter.service.ledger.snapshot() == before


async def test_sentiment_uses_its_own_stage_actual_refs_and_missing_is_not_neutral(adapter):
    sid = (await call(adapter, "margin_register_sources", {"sources": [source()]}))["sources"][0][
        "source_id"
    ]
    packet = await call(
        adapter,
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
    next_step = packet["next_steps"][0]
    assert next_step["mcp_execution"]["tool"] == "margin_submit_annotations"
    assert next_step["required_host_fields"] == ["reviewer", "annotations"]
    unreviewed = await call(adapter, "margin_aggregate_sentiment", ref(packet))
    assert unreviewed["balance"] is None and unreviewed["counts"]["unannotated"] == 1
    fabricated = await call(
        adapter, "margin_aggregate_sentiment", ref(packet) | {"packet_hash": "0" * 64}, error=True
    )
    assert fabricated["error"]["code"] == "packet_mismatch"
    run_id = await call(
        adapter,
        "margin_aggregate_sentiment",
        ref(packet) | {"packet_id": "fictional-run-id"},
        error=True,
    )
    assert run_id["error"]["code"] == "packet_unavailable"
    submitted = await call(
        adapter,
        "margin_submit_annotations",
        next_step["bound_arguments"]
        | {
            "reviewer": {"host": "fixture", "model": "fixture"},
            "annotations": [
                {
                    "source_id": sid,
                    "relevant": True,
                    "label": "positive",
                    "quotes": [quote(sid)],
                    "rationale": "Fictional test label for improved demand.",
                }
            ],
        },
    )
    final_step = submitted["next_steps"][0]
    result = await call(adapter, final_step["mcp_execution"]["tool"], final_step["bound_arguments"])
    assert result["balance"] == "1" and result["balance_denominator"] == 1
    assert not result["investor_sentiment"]
    assert adapter.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


async def test_inventory_hints_do_not_request_semantics_and_cannot_bypass_capability_guard(adapter):
    sid = (await call(adapter, "margin_register_sources", {"sources": [source()]}))["sources"][0][
        "source_id"
    ]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {
            "claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}],
            "host_profile": {"structured_assessment": False},
        },
    )
    assert packet["next_steps"][0]["mcp_execution"]["tool"] == "margin_render_citations"
    assert packet["next_steps"][0]["is_complete_input"]
    rejected = await call(
        adapter,
        "margin_submit_assessment",
        ref(packet)
        | {
            "reviewer": {"host": "fixture", "model": "fixture"},
            "assessments": [
                {
                    "claim_id": "C1",
                    "verdict": "supported",
                    "quotes": [quote(sid)],
                    "rationale": "Fictional test.",
                }
            ],
        },
        error=True,
    )
    assert rejected["error"]["code"] == "unsupported_assessment"


async def test_sentiment_inventory_and_cross_workflow_refs_remain_distinct(adapter):
    sid = (await call(adapter, "margin_register_sources", {"sources": [source()]}))["sources"][0][
        "source_id"
    ]
    packet = await call(
        adapter,
        "margin_prepare_sentiment",
        {
            "source_ids": [sid],
            "issuer": "NSE:EXAMPLE",
            "aspect": "demand",
            "from": "2026-11-01",
            "to": "2026-11-25",
            "date_basis": "published",
            "host_profile": {"structured_assessment": False},
        },
    )
    action = packet["next_steps"][0]
    assert (
        action["is_complete_input"]
        and action["mcp_execution"]["tool"] == "margin_aggregate_sentiment"
    )
    aggregate = await call(adapter, action["mcp_execution"]["tool"], action["bound_arguments"])
    assert aggregate["status"] == "incomplete" and aggregate["counts"]["unannotated"] == 1
    wrong = await call(adapter, "margin_render_citations", ref(packet), error=True)
    assert wrong["error"]["code"] == "packet_mismatch"


def test_review_schema_diagnostics_do_not_claim_credentials_or_echo_unknown_values():
    service = ReviewService()
    with pytest.raises(DomainError) as caught:
        service.invoke(
            "evidence.prepare_verification",
            {
                "packet_id": "fictional-data-run",
                "packet_hash": "hash_12345",
                "private-field": "private-value",
            },
        )
    msg = caught.value.message
    assert (
        "missing required fields: claims" in msg and "allowed fields: claims, host_profile" in msg
    )
    assert "credentials" not in msg and "private-field" not in msg and "private-value" not in msg
    assert len(msg) < 2100 and not service.packets


@pytest.mark.parametrize(
    "arguments,expected",
    [
        ({"claims": "x" * 66000}, "64 KiB"),
        ({"claims": math.nan}, "finite JSON"),
        ({"claims": object()}, "finite JSON"),
    ],
)
def test_size_and_json_failures_remain_separate_from_schema_and_sanitization(arguments, expected):
    with pytest.raises(DomainError, match=expected):
        ReviewService().invoke("evidence.prepare_verification", arguments)


def test_actual_sanitization_failure_is_separate_and_never_echoes_secret():
    service = ReviewService(sanitizer=Sanitizer(["fixture-private-secret"]))
    with pytest.raises(DomainError) as caught:
        service.invoke(
            "evidence.register_sources",
            {"sources": [source() | {"title": "fixture-private-secret"}]},
        )
    assert (
        "sanitization" in caught.value.message
        and "fixture-private-secret" not in caught.value.message
    )
    assert not service.sources


async def test_packet_expiry_is_checked_independently_of_original_verification(adapter):
    timer = [0]
    adapter.service.reviews = ReviewService(ttl=10, timer=lambda: timer[0])
    sid = (await call(adapter, "margin_register_sources", {"sources": [source()]}))["sources"][0][
        "source_id"
    ]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {"claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}]},
    )
    assert packet["sources"][0]["original_document_verified"] is False
    timer[0] = 11
    expired = await call(adapter, "margin_render_citations", ref(packet), error=True)
    assert expired["error"]["code"] == "packet_unavailable"
    assert adapter.service.ledger.requests == {"bharatstock": 0, "drishti": 0}
