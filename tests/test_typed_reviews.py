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


@pytest.mark.parametrize(
    "profile,has_text,action,reader",
    [
        ({}, True, "review_supplied_passages", None),
        ({"host_search": True}, False, "return_insufficient_evidence_or_inventory", None),
        ({"host_read_sources": False}, True, "review_supplied_passages", False),
        ({"host_read_sources": False}, False, "return_insufficient_evidence_or_inventory", False),
        ({"host_read_sources": True}, False, "read_and_register_with_host_tools", True),
        ({"host_read_sources": True}, True, "review_supplied_passages", True),
        (
            {"host_read_sources": True, "structured_assessment": False},
            False,
            "return_unreviewed_inventory",
            True,
        ),
    ],
)
async def test_optional_citation_routes_declared_capabilities_without_fetch_or_hash_change(
    adapter, profile, has_text, action, reader
):
    before = adapter.service.ledger.snapshot()
    item = source()
    if not has_text:
        item["passages"] = []
    registration = await call(adapter, "margin_register_sources", {"sources": [item]})
    sid = registration["sources"][0]["source_id"]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {
            "claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}],
            "host_profile": profile,
        },
    )
    guidance = packet["citation_protocol"]
    assert guidance["optional"] is True
    assert guidance["host_read_sources"] is reader
    assert guidance["recommended_action"] == action
    assert guidance["claims_without_passages"] == ([] if has_text else ["C1"])
    assert guidance["review_scope"] == "supplied_passages_only"
    assert guidance["original_document_verified"] is False
    if action == "read_and_register_with_host_tools":
        first, fallback = packet["next_steps"]
        assert first["mcp_execution"]["tool"] == "margin_register_sources"
        assert first["required_host_fields"] == ["sources"]
        assert not first["is_complete_input"]
        assert fallback["mcp_execution"]["tool"] == "margin_submit_assessment"
        assert fallback["bound_arguments"] == ref(packet)
    stored = copy.deepcopy(adapter.service.reviews.packets[packet["packet_id"]][1])
    assert "citation_protocol" not in stored
    stored.pop("packet_hash")
    assert digest(stored) == packet["packet_hash"]
    assert adapter.service.ledger.snapshot() == before


async def test_no_reader_can_review_supplied_text_but_not_invent_support_for_locator(adapter):
    item = source()
    item["passages"] = []
    registration = await call(adapter, "margin_register_sources", {"sources": [item]})
    sid = registration["sources"][0]["source_id"]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {
            "claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}],
            "host_profile": {"host_read_sources": False, "structured_assessment": True},
        },
    )
    values = ref(packet) | {
        "reviewer": {"host": "fixture", "model": "unspecified"},
        "assessments": [
            {
                "claim_id": "C1",
                "verdict": "supported",
                "quotes": [quote(sid)],
                "rationale": "A locator alone does not supply this quote.",
            }
        ],
    }
    rejected = await call(adapter, "margin_submit_assessment", values, error=True)
    assert rejected["error"]["code"] == "quote_mismatch"
    values["assessments"][0].update(verdict="insufficient_evidence", quotes=[])
    result = await call(adapter, "margin_submit_assessment", values)
    assert result["assessment"]["assessments"][0]["verdict"] == "insufficient_evidence"
    assert result["independently_verified"] is False
    audit = await call(adapter, "margin_audit_answer", ref(packet) | {"claim_ids": ["C1"]})
    assert audit["status"] == "incomplete"
    assert audit["assessment_coverage"]["status"] == "host_assessed"
    assert audit["assessment_counts"] == {"insufficient_evidence": 1}


async def test_host_original_handoff_requires_new_source_packet_and_never_authenticates(adapter):
    before = adapter.service.ledger.snapshot()
    locator = source() | {"passages": [], "kind": "source_locator"}
    sid = (await call(adapter, "margin_register_sources", {"sources": [locator]}))["sources"][0][
        "source_id"
    ]

    async def prepare(sid):
        return await call(
            adapter,
            "margin_prepare_verification",
            {
                "claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}],
                "host_profile": {"host_read_sources": True},
            },
        )

    initial = await prepare(sid)
    original = source() | {"kind": "original_document", "url": "https://example.invalid/original"}
    new_source = (await call(adapter, "margin_register_sources", {"sources": [original]}))[
        "sources"
    ][0]
    updated = await prepare(new_source["source_id"])
    assert updated["packet_id"] != initial["packet_id"]
    assert new_source["source_id"] != sid
    assert initial["citation_protocol"]["recommended_action"] == "read_and_register_with_host_tools"
    assert updated["citation_protocol"]["recommended_action"] == "review_supplied_passages"
    assert new_source["original_document_verified"] is False
    retained = adapter.service.reviews.packets[initial["packet_id"]][1]
    assert retained["sources"][0]["passages"] == []
    assert adapter.service.ledger.snapshot() == before


async def test_workflow_discovery_marks_citation_optional_and_exposes_host_reading_steps(adapter):
    result = await call(adapter, "margin_review_workflows")
    policy = result["workflows"][0]["citation_protocol"]
    assert policy["optional"] is True
    assert policy["review_scope"] == "supplied_passages_only"
    assert len(policy["original_source_steps"]) == 4
    assert "host_assesses_supplied_passages_or_returns_inventory" in result["workflows"][0]["steps"]
    assert "host_reads_original_and_submits_assessment" not in result["workflows"][0]["steps"]


async def test_partial_text_inventory_preserves_other_claims_and_host_contradiction(adapter):
    registration = await call(
        adapter,
        "margin_register_sources",
        {"sources": [source(), source() | {"passages": [], "url": "https://example.invalid/link"}]},
    )
    text_id, link_id = [s["source_id"] for s in registration["sources"]]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {
            "claims": [
                {"claim_id": "C1", "text": "Demand declined.", "source_ids": [text_id]},
                {"claim_id": "C2", "text": "Sales doubled.", "source_ids": [link_id]},
            ],
            "host_profile": {"host_search": True, "host_read_sources": False},
        },
    )
    assert packet["citation_protocol"]["claims_without_passages"] == ["C2"]
    result = await call(
        adapter,
        "margin_submit_assessment",
        ref(packet)
        | {
            "reviewer": {"host": "fixture", "model": "fixture"},
            "assessments": [
                {
                    "claim_id": "C1",
                    "verdict": "contradicted",
                    "quotes": [quote(text_id)],
                    "rationale": "Supplied text reports the opposite direction.",
                },
                {
                    "claim_id": "C2",
                    "verdict": "insufficient_evidence",
                    "quotes": [],
                    "rationale": "No readable source passage is available.",
                },
            ],
        },
    )
    assert result["assessment_origin"] == "host_reported"
    audit = await call(adapter, "margin_audit_answer", ref(packet) | {"claim_ids": ["C1", "C2"]})
    assert audit["assessment_counts"] == {"contradicted": 1, "insufficient_evidence": 1}
    assert audit["original_document_verified"] is False


def ref(packet):
    return {k: packet[k] for k in ("packet_id", "packet_hash")}


def quote(sid, text="Demand improved."):
    return {"source_id": sid, "passage_id": "P1", "quote": text}


@pytest.mark.parametrize("field", ["url", "locator"])
async def test_registration_normalizes_plain_anchors_and_preserves_passage_quotes(adapter, field):
    before = adapter.service.ledger.snapshot()
    item = source()
    item["passages"][0]["locator"] = item["url"]
    owner = item if field == "url" else item["passages"][0]
    owner[field] += "#CLAIM1"
    original = copy.deepcopy(item)
    result = await call(adapter, "margin_register_sources", {"sources": [item]})
    assert item == original
    expected = "/sources/0/url" if field == "url" else "/sources/0/passages/0/locator"
    assert result["input_normalizations"] == [
        {"path": expected, "change": "plain_url_fragment_removed"}
    ]
    registered = result["sources"][0]
    assert registered["passages"][0]["text"] == item["passages"][0]["text"]
    assert registered["passages"][0]["passage_id"] == "P1"
    sid = registered["source_id"]
    packet = await call(
        adapter,
        "margin_prepare_verification",
        {"claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}]},
    )
    submitted = await call(
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
                    "rationale": "Supplied fictional text.",
                }
            ],
        },
    )
    assert submitted["quote_check"] == "matched_supplied_text_only"
    assert submitted["independently_verified"] is False
    assert adapter.service.ledger.snapshot() == before


@pytest.mark.parametrize(
    "fragment",
    [
        "api_key=unconfigured",
        "token=unconfigured",
        "secret:unconfigured",
        "authorization:BearerSomething",
        "api_key%3Dhidden",
        "summary%20label",
        "synthetic-private-key-never-forward",
    ],
)
def test_registration_still_rejects_sensitive_or_nonplain_fragments(fragment):
    item = source()
    item["passages"][0]["locator"] = item["url"] + "#" + fragment
    service = ReviewService()
    with pytest.raises(DomainError) as caught:
        service.invoke("evidence.register_sources", {"sources": [item]})
    assert "/sources/0/passages/0/locator" in caught.value.message
    assert fragment not in caught.value.message
    assert not service.sources


@pytest.mark.parametrize(
    "location",
    [
        "text",
        "query",
        "userinfo",
        "unknown_field",
        "leading_space",
        "newline",
        "host_case",
        "scheme_case",
    ],
)
def test_plain_anchor_does_not_permit_other_sanitization_changes(location):
    item = source()
    item["url"] += "#summary"
    if location == "text":
        item["passages"][0]["text"] = "secret=never-forward"
    elif location == "query":
        item["url"] = "https://example.invalid/review?api_key=never-forward#summary"
    elif location == "userinfo":
        item["url"] = "https://user:password@example.invalid/review#summary"
    elif location == "leading_space":
        item["url"] = " " + item["url"]
    elif location == "newline":
        item["url"] = "https://example.invalid/re\nview#summary"
    elif location == "host_case":
        item["url"] = "https://EXAMPLE.invalid/review#summary"
    elif location == "scheme_case":
        item["url"] = "HTTPS://example.invalid/review#summary"
    else:
        item["secret"] = "never-forward"
    service = ReviewService()
    with pytest.raises(DomainError):
        service.invoke("evidence.register_sources", {"sources": [item]})
    assert not service.sources


@pytest.mark.parametrize("field", ["url", "locator"])
@pytest.mark.parametrize("control", ["\n", "\t", "\x00", " "])
def test_registration_rejects_raw_url_controls_atomically(field, control):
    item = source()
    raw = f"https://example.invalid/re{control}view"
    if field == "url":
        item["url"] = raw
    else:
        item["passages"][0]["locator"] = raw
    service = ReviewService()
    with pytest.raises(DomainError):
        service.invoke("evidence.register_sources", {"sources": [source(), item]})
    assert not service.sources


def test_sanitization_diagnostic_omits_unknown_keys_and_values():
    item = source()
    item["unknown-sensitive-field"] = {"api_key": "private-placeholder-never-echo"}
    service = ReviewService()
    with pytest.raises(DomainError) as caught:
        service.invoke("evidence.register_sources", {"sources": [item]})
    assert "/sources/0" in caught.value.message
    assert "unknown-sensitive-field" not in caught.value.message
    assert "private-placeholder-never-echo" not in caught.value.message
    assert not service.sources


@pytest.mark.parametrize("workflow", ["citation", "sentiment"])
async def test_partial_host_submission_coverage_never_reports_full_assessment(adapter, workflow):
    registered = await call(
        adapter,
        "margin_register_sources",
        {"sources": [source(), source() | {"url": "https://example.invalid/second"}]},
    )
    ids = [s["source_id"] for s in registered["sources"]]
    reviewer = {"host": "fixture", "model": "fixture"}
    if workflow == "citation":
        packet = await call(
            adapter,
            "margin_prepare_verification",
            {
                "claims": [
                    {"claim_id": f"C{i}", "text": "Demand improved.", "source_ids": [sid]}
                    for i, sid in enumerate(ids)
                ]
            },
        )
        assert packet["assessment_coverage"]["status"] == "not_reviewed"
        result = await call(
            adapter,
            "margin_submit_assessment",
            ref(packet)
            | {
                "reviewer": reviewer,
                "assessments": [
                    {
                        "claim_id": "C0",
                        "verdict": "supported",
                        "quotes": [quote(ids[0])],
                        "rationale": "Fictional supplied passage.",
                    }
                ],
            },
        )
        projected = await call(adapter, "margin_render_citations", ref(packet))
        assert projected["status"] == "success"
        missing = ["C1"]
    else:
        packet = await call(
            adapter,
            "margin_prepare_sentiment",
            {
                "source_ids": ids,
                "issuer": "NSE:EXAMPLE",
                "aspect": "demand",
                "from": "2026-11-01",
                "to": "2026-11-25",
                "date_basis": "published",
            },
        )
        assert packet["assessment_coverage"]["status"] == "not_reviewed"
        result = await call(
            adapter,
            "margin_submit_annotations",
            ref(packet)
            | {
                "reviewer": reviewer,
                "annotations": [
                    {
                        "source_id": ids[0],
                        "relevant": True,
                        "label": "positive",
                        "quotes": [quote(ids[0])],
                        "rationale": "Fictional supplied passage.",
                    }
                ],
            },
        )
        projected = await call(adapter, "margin_aggregate_sentiment", ref(packet))
        assert projected["status"] == "incomplete"
        assert projected["counts"]["unannotated"] == 1
        assert projected["investor_sentiment"] is False
        assert "(positive+negative+neutral)" in projected["aggregation_policy"]
        missing = [ids[1]]
    assert result["assessment_coverage"] == projected["assessment_coverage"]
    assert projected["assessment_coverage"]["status"] == "partially_reviewed"
    assert projected["assessment_coverage"]["reviewed_count"] == 1
    assert projected["assessment_coverage"]["total_count"] == 2
    assert projected["assessment_coverage"]["unreviewed_ids"] == missing


@pytest.mark.parametrize("tool,function", DIRECT_REVIEWS.items())
def test_review_tool_schema_is_exact_core_copy_without_wrapper_or_mutation(tool, function):
    schema = definitions()[tool].input_schema
    expected = copy.deepcopy(SCHEMAS[function])
    schema["properties"].pop("why")
    assert schema == expected
    schema["properties"].clear()
    assert SCHEMAS[function] == expected
    assert definitions()[tool].input_schema["properties"]


async def test_maturity_level_is_not_a_financial_numeric_fact(adapter):
    before = adapter.service.ledger.snapshot()
    item = {
        "issuer": "NSE:EXAMPLE",
        "metric": "CMMI AI Maturity Level",
        "definition": "Maturity certification",
        "value": "5",
        "unit": "level",
        "period_type": "instant",
        "period_end": "2026-11-25",
        "basis": "standalone",
    }
    result = await call(
        adapter, "margin_check_numeric_claim", {"claim": item, "evidence": item}, error=True
    )
    assert result["error"]["code"] == "invalid_input"
    assert adapter.service.ledger.snapshot() == before
    assert "certification" in adapter.tools["margin_check_numeric_claim"].description


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
            "host_profile": {
                "host_search": False,
                "host_read_sources": False,
                "structured_assessment": True,
            },
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
