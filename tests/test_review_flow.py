"""Fictional text tests bookkeeping and guards, never independent semantic truth."""

import copy
import json

import pytest
from mcp.shared.exceptions import MCPError

from margin.core.config import Settings
from margin.core.contracts import DomainError, encoded_size
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import SIMPLE_TOOLS, ToolView
from margin.interfaces.mcp.server import MarginMCP
from margin.protocols.service import ReviewService


def request(**changes):
    return {
        "issuer": "NSE:EXAMPLE",
        "title": "Fictional supplied summary",
        "source_url": "https://example.invalid/source#summary",
        "source_text": "Demand improved. Costs increased.",
        "record_date": "2026-11-25",
        "publication_date": None,
        "claims": ["Demand improved.", "Investors became bullish."],
        "sentiment": {
            "aspect": "demand",
            "from": "2026-11-10",
            "to": "2026-11-25",
            "date_basis": "record_date",
        },
        **changes,
    }


def submission(review_id, **changes):
    return {
        "review_id": review_id,
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
            "rationale": "Fictional host label, not market sentiment.",
        },
        **changes,
    }


def stores(service):
    return copy.deepcopy((service.sources, service.packets, service.sessions))


def test_two_calls_bind_all_references_dates_and_report_unsupported_claim():
    service = ReviewService(mode="live")
    prepared = service.invoke("review.prepare", request())
    assert prepared["status"] == "awaiting_host_review" and not prepared["complete"]
    assert prepared["context"]["record_date"] == "2026-11-25"
    assert prepared["context"]["publication_date"] is None
    assert prepared["input_normalizations"][0]["path"] == "/source_url"
    assert prepared["next_steps"][0]["bound_arguments"] == {"review_id": prepared["review_id"]}
    result = service.invoke("review.submit", submission(prepared["review_id"]))
    assert result["complete"] and result["status"] == "reviewed"
    assert [r["verdict"] for r in result["claims"]] == ["supported", "insufficient_evidence"]
    assert result["support_audit"]["status"] == "incomplete"
    assert result["support_audit"]["assessment_coverage"]["status"] == "host_assessed"
    assert result["sentiment"]["date_basis"] == "record_date"
    assert result["sentiment"]["counts"]["positive"] == 1
    assert (
        not result["original_document_verified"] and not result["sentiment"]["investor_sentiment"]
    )
    assert result["network_attempts"] == 0 and not result["llm_inference"]
    for packet in service.packets.values():
        assert packet[1]["sources"][0]["passages"][0]["text"] == request()["source_text"]


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"record_date": None}, "missing_context"),
        (
            {
                "sentiment": {
                    "aspect": "demand",
                    "from": "2026-11-10",
                    "to": "2026-11-25",
                    "date_basis": "published",
                }
            },
            "missing_context",
        ),
        ({"record_date": "2026-10-01"}, "scope_mismatch"),
        ({"claims": [], "sentiment": None}, "invalid_input"),
        ({"source_text": " "}, "invalid_input"),
        ({"source_url": "https://example.invalid/source?api_key=do-not-accept"}, "invalid_input"),
    ],
)
def test_missing_scope_or_unsafe_input_never_creates_records(changes, code):
    service = ReviewService()
    values = request(**changes)
    if values.get("sentiment", True) is None:
        values.pop("sentiment")
        code = "missing_context"
    with pytest.raises(DomainError) as caught:
        service.invoke("review.prepare", values)
    assert caught.value.code == code
    assert stores(service) == ({}, {}, {})


@pytest.mark.parametrize("record_limit", [1, 2, 3])
def test_preparation_capacity_failure_rolls_back_all_stores(record_limit):
    service = ReviewService(max_records=record_limit)
    with pytest.raises(DomainError, match="capacity"):
        service.invoke("review.prepare", request())
    assert stores(service) == ({}, {}, {})


@pytest.mark.parametrize("wrong_part", ["citation", "sentiment"])
def test_invalid_quotes_roll_back_citation_and_sentiment_together(wrong_part):
    service = ReviewService()
    prepared = service.invoke("review.prepare", request())
    before = stores(service)
    values = submission(prepared["review_id"])
    if wrong_part == "citation":
        values["claim_assessments"][0]["quote"] = "Invented quote."
    else:
        values["sentiment_annotation"]["quote"] = "Invented quote."
    with pytest.raises(DomainError, match="Quote does not match"):
        service.invoke("review.submit", values)
    assert stores(service) == before


@pytest.mark.parametrize(
    "change", ["too_few", "too_many", "missing_sentiment", "unexpected_sentiment"]
)
def test_submission_must_match_exact_prepared_scope(change):
    service = ReviewService()
    args = request()
    if change == "unexpected_sentiment":
        args.pop("sentiment")
    prepared = service.invoke("review.prepare", args)
    values = submission(prepared["review_id"])
    if change == "too_few":
        values["claim_assessments"].pop()
    if change == "too_many":
        values["claim_assessments"].append(copy.deepcopy(values["claim_assessments"][0]))
    if change == "missing_sentiment":
        values.pop("sentiment_annotation")
    before = stores(service)
    with pytest.raises(DomainError):
        service.invoke("review.submit", values)
    assert stores(service) == before


def test_replay_is_immutable_and_does_not_extend_session_ttl():
    clock = [0]
    service = ReviewService(timer=lambda: clock[0], ttl=10)
    prepared = service.invoke("review.prepare", request())
    values = submission(prepared["review_id"])
    result = service.invoke("review.submit", values)
    clock[0] = 8
    assert service.invoke("review.submit", values) == result
    changed = copy.deepcopy(values)
    changed["claim_assessments"][0]["rationale"] = "Different judgment."
    with pytest.raises(DomainError, match="immutable"):
        service.invoke("review.submit", changed)
    clock[0] = 11
    with pytest.raises(DomainError) as caught:
        service.invoke("review.submit", values)
    assert caught.value.code == "review_unavailable"
    assert stores(service) == ({}, {}, {})


def test_submit_capacity_failure_is_atomic():
    service = ReviewService()
    prepared = service.invoke("review.prepare", request())
    before = stores(service)
    service.max_bytes = (
        sum(encoded_size(item[1]) for store in before for item in store.values()) + 1
    )
    with pytest.raises(DomainError, match="capacity"):
        service.invoke("review.submit", submission(prepared["review_id"]))
    assert stores(service) == before


def test_sentiment_only_does_not_invent_a_claim():
    service = ReviewService()
    prepared = service.invoke("review.prepare", request(claims=[]))
    result = service.invoke(
        "review.submit", submission(prepared["review_id"], claim_assessments=[])
    )
    assert result["claims"] == [] and result["support_audit"] is None
    assert result["sentiment"]["eligible_sources"] == 1


def test_claims_only_preserves_unknown_dates_without_inventing_sentiment():
    service = ReviewService()
    args = request(record_date=None)
    del args["sentiment"]
    prepared = service.invoke("review.prepare", args)
    answer = submission(prepared["review_id"])
    del answer["sentiment_annotation"]
    result = service.invoke("review.submit", answer)
    assert result["complete"] and result["sentiment"] is None
    assert result["context"]["record_date"] is None
    assert result["context"]["publication_date"] is None


@pytest.mark.parametrize("field", ["source_ids", "packet_hash", "host_profile", "date_kind"])
def test_high_level_preparation_rejects_model_bookkeeping_fields(field):
    service = ReviewService()
    with pytest.raises(DomainError, match="schema"):
        service.invoke("review.prepare", request(**{field: "invented"}))
    assert stores(service) == ({}, {}, {})


def test_unknown_review_is_not_recreated_or_fetched():
    service = ReviewService()
    with pytest.raises(DomainError) as caught:
        service.invoke("review.submit", submission("rvw_" + "0" * 32))
    assert caught.value.code == "review_unavailable"
    assert stores(service) == ({}, {}, {})


def test_publication_scope_preserves_both_dates():
    service = ReviewService()
    args = request(publication_date="2026-11-20")
    args["sentiment"]["date_basis"] = "published"
    prepared = service.invoke("review.prepare", args)
    result = service.invoke("review.submit", submission(prepared["review_id"]))
    assert result["context"]["record_date"] == "2026-11-25"
    assert result["context"]["publication_date"] == "2026-11-20"
    assert result["sentiment"]["date_basis"] == "published"


@pytest.mark.parametrize("reference", ["https://example.invalid/source", "summary", "C1"])
def test_bad_legacy_reference_does_not_claim_expiry(reference):
    with pytest.raises(DomainError) as caught:
        ReviewService()._source(reference)
    assert "not an issued source handle" in caught.value.message
    assert "expired" not in caught.value.message


async def test_three_tool_view_shares_owner_and_hides_bookkeeping():
    service = ResearchService(
        Settings(bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        owner = MarginMCP(service)
        full = ToolView(owner)
        simple = ToolView(owner, "review-simple")
        assert set(simple.tools) == SIMPLE_TOOLS and len(simple.tools) == 3
        before = service.ledger.snapshot()
        prepared = (await full.call("margin_prepare_review", request())).structured_content["data"]
        result = await simple.call("margin_submit_review", submission(prepared["review_id"]))
        assert not result.is_error and result.structured_content["data"]["complete"]
        status = (await simple.call("margin_status", {})).structured_content["data"]
        assert status["tool_profile"] == "review-simple" and status["advertised_tools"] == 3
        with pytest.raises(MCPError):
            await simple.call("margin_register_sources", {})
        with pytest.raises(MCPError):
            await simple.call("margin_check_numeric_claim", {})
        assert service.ledger.snapshot() == before
        assert "source_ids" not in json.dumps(simple.tools["margin_submit_review"].input_schema)
    finally:
        await service.close()
