"""Invented passages/values test local contracts; not company or sentiment ground truth."""

import copy
import io
import json

import pytest
from fastapi.testclient import TestClient

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.evidence.sanitize import Sanitizer
from margin.interfaces.agent.cli import main
from margin.interfaces.agent.client import AgentClient
from margin.interfaces.workbench.app import create_app
from margin.protocols.service import ReviewService


def source(**changes):
    return {
        "issuer": "NSE:EXAMPLE",
        "title": "Fictional document",
        "url": "https://example.invalid/report.pdf",
        "kind": "original_document",
        "date": "2026-10-15",
        "date_kind": "published",
        "passages": [
            {
                "passage_id": "P1",
                "text": "Example revenue increased to 120 crore. Demand improved.",
                "locator": "PDF page 2",
            }
        ],
        **changes,
    }


def register(service, **changes):
    return service.invoke("evidence.register_sources", {"sources": [source(**changes)]})["sources"][
        0
    ]["source_id"]


def prepare(service, source_id, **changes):
    return service.invoke(
        "evidence.prepare_verification",
        {
            "claims": [
                {
                    "claim_id": "C1",
                    "text": "Example revenue was 120 crore.",
                    "source_ids": [source_id],
                }
            ],
            **changes,
        },
    )


def packet_ref(packet):
    return {k: packet[k] for k in ("packet_id", "packet_hash")}


def assessment(source_id, **changes):
    return {
        "claim_id": "C1",
        "verdict": "supported",
        "rationale": "The supplied example states this value.",
        "quotes": [
            {"source_id": source_id, "passage_id": "P1", "quote": "revenue increased to 120 crore"}
        ],
        **changes,
    }


def submit(service, packet, source_id, **changes):
    return service.invoke(
        "evidence.submit_assessment",
        packet_ref(packet)
        | {
            "reviewer": {"host": "fictional-test", "model": "unspecified"},
            "assessments": [assessment(source_id, **changes)],
        },
    )


def test_citation_roundtrip_labels_host_judgments_and_audits_overclaims():
    service = ReviewService()
    sid = register(service)
    packet = prepare(service, sid)
    assert packet["semantic_review"] == "not_reviewed" and not packet["llm_inference"]
    unreviewed = service.invoke("evidence.render_citations", packet_ref(packet))
    assert unreviewed["citations"][0]["semantic_review"] == "not_reviewed"
    first = submit(service, packet, sid)
    assert first == submit(service, packet, sid)
    assert (
        first["quote_check"] == "matched_supplied_text_only" and not first["independently_verified"]
    )
    rendered = service.invoke("evidence.render_citations", packet_ref(packet))["citations"][0]
    assert (
        rendered["semantic_review"] == "supported"
        and rendered["reviewer_origin"] == "host_reported"
    )
    assert not rendered["original_document_verified"]
    audit = service.invoke(
        "evidence.audit_answer",
        packet_ref(packet) | {"claim_ids": ["C1"], "claimed_verified_ids": ["C1"]},
    )
    assert audit["status"] == "incomplete" and audit["flags"]
    assert (
        service.invoke("evidence.audit_answer", packet_ref(packet) | {"claim_ids": ["C1"]})[
            "status"
        ]
        == "success"
    )
    assert "prose" in audit["scope"]
    with pytest.raises(DomainError, match="immutable"):
        submit(service, packet, sid, verdict="partial")


@pytest.mark.parametrize(
    "change,error",
    [
        ({"quotes": []}, "require quoted"),
        ({"quotes": [{"source_id": "other", "passage_id": "P1", "quote": "120"}]}, "outside"),
        (
            {"quotes": [{"source_id": "$SID", "passage_id": "P1", "quote": "made up"}]},
            "does not match",
        ),
        ({"claim_id": "other"}, "Unknown claim"),
    ],
)
def test_invalid_claim_quote_or_reference_does_not_commit(change, error):
    service = ReviewService()
    sid = register(service)
    packet = prepare(service, sid)
    change = copy.deepcopy(change)
    for quote in change.get("quotes", []):
        if quote["source_id"] == "$SID":
            quote["source_id"] = sid
    with pytest.raises(DomainError, match=error):
        submit(service, packet, sid, **change)
    assert (
        service.invoke("evidence.render_citations", packet_ref(packet))["citations"][0][
            "semantic_review"
        ]
        == "not_reviewed"
    )


def test_capability_fallbacks_and_missing_passages_never_invent_support():
    service = ReviewService()
    sid = register(service, passages=[])
    packet = prepare(
        service, sid, host_profile={"host_search": False, "structured_assessment": False}
    )
    assert packet["route"] == "inventory_only"
    with pytest.raises(DomainError, match="inventory-only"):
        submit(service, packet, sid, verdict="insufficient_evidence", quotes=[])
    packet = prepare(service, sid)
    result = submit(service, packet, sid, verdict="insufficient_evidence", quotes=[])
    assert result["assessment"]["assessments"][0]["verdict"] == "insufficient_evidence"
    assert not result["independently_verified"]
    with pytest.raises(DomainError, match="exact packet"):
        service.invoke("evidence.render_citations", packet_ref(packet) | {"packet_hash": "wrong"})


def test_expiry_capacity_atomicity_and_retention_not_extended_by_submission():
    clock = [0]
    service = ReviewService(timer=lambda: clock[0], ttl=10)
    sid = register(service)
    packet = prepare(service, sid)
    clock[0] = 8
    submit(service, packet, sid)
    clock[0] = 11
    with pytest.raises(DomainError, match="expired"):
        service.invoke("evidence.render_citations", packet_ref(packet))
    with pytest.raises(DomainError, match="expired"):
        prepare(service, sid)
    tiny = ReviewService(max_records=1)
    with pytest.raises(DomainError, match="capacity"):
        tiny.invoke(
            "evidence.register_sources",
            {"sources": [source(), source(url="https://example.invalid/other")]},
        )
    assert tiny.sources == {}
    invalid = ReviewService()
    with pytest.raises(DomainError, match="Decorative"):
        invalid.invoke(
            "evidence.register_sources",
            {"sources": [source(), source(url="https://example.invalid/logo.svg")]},
        )
    assert invalid.sources == {}


def test_secret_injection_unknown_functions_and_false_verification_fields_are_rejected():
    service = ReviewService(sanitizer=Sanitizer(["fictional-secret-12345678"]))
    for item in [
        source(title="fictional-secret-12345678"),
        source(url="https://example.invalid/report?api_key=private"),
        source(verified=True),
    ]:
        with pytest.raises(DomainError):
            service.invoke("evidence.register_sources", {"sources": [item]})
    for function in [[], "does.not.exist"]:
        with pytest.raises(DomainError, match="Unknown"):
            service.invoke(function, {})
    assert service.sources == {}


def sentiment_packet(service, ids, **changes):
    return service.invoke(
        "sentiment.prepare_analysis",
        {
            "source_ids": ids,
            "issuer": "NSE:EXAMPLE",
            "aspect": "demand",
            "from": "2026-10-01",
            "to": "2026-10-31",
            "date_basis": "published",
            **changes,
        },
    )


def test_sentiment_scope_duplicates_missing_annotations_and_exact_balance():
    service = ReviewService()
    ids = [register(service, url=f"https://example.invalid/{i}") for i in range(5)]
    duplicate = register(service, url="https://example.invalid/0", title="Duplicate summary")
    old = register(service, date="2026-09-01")
    unknown = register(service, url="https://example.invalid/unknown", date_kind="unknown")
    other = register(service, issuer="NSE:OTHER")
    packet = sentiment_packet(service, [*ids, duplicate, old, unknown, other])
    assert len(packet["sources"]) == 5 and len(packet["excluded"]) == 4
    before = service.invoke("sentiment.aggregate", packet_ref(packet))
    assert (
        before["balance"] is None
        and before["counts"]["neutral"] == 0
        and before["counts"]["unannotated"] == 5
    )
    annotations = [
        {
            "source_id": sid,
            "relevant": True,
            "label": label,
            "rationale": "Fictional label, not financial evidence.",
            "quotes": [{"source_id": sid, "passage_id": "P1", "quote": "Demand improved."}],
        }
        for sid, label in zip(
            ids, ["positive", "positive", "negative", "neutral", "mixed"], strict=True
        )
    ]
    service.invoke(
        "sentiment.submit_annotations",
        packet_ref(packet)
        | {"reviewer": {"host": "fixture", "model": "fixture"}, "annotations": annotations},
    )
    result = service.invoke("sentiment.aggregate", packet_ref(packet))
    assert result["balance"] == "0.25" and result["balance_denominator"] == 4
    assert (
        result["counts"]["mixed"] == 1
        and not result["investor_sentiment"]
        and not result["coverage_complete"]
    )
    assert result["annotation_origin"] == "host_reported"
    record = sentiment_packet(service, [unknown], date_basis="record_date")
    assert len(record["sources"]) == 1


def test_sentiment_empty_irrelevant_unclear_and_invalid_refs():
    service = ReviewService()
    sid = register(service, date=None)
    empty = sentiment_packet(service, [sid])
    assert service.invoke("sentiment.aggregate", packet_ref(empty))["status"] == "incomplete"
    sid = register(service)
    packet = sentiment_packet(service, [sid])
    annotation = {
        "source_id": "unknown",
        "relevant": True,
        "label": "positive",
        "quotes": [],
        "rationale": "Fixture",
    }
    with pytest.raises(DomainError, match="excluded or unknown"):
        service.invoke(
            "sentiment.submit_annotations",
            packet_ref(packet)
            | {"reviewer": {"host": "fixture", "model": "fixture"}, "annotations": [annotation]},
        )
    annotation.update(source_id=sid, relevant=False, label="unclear")
    service.invoke(
        "sentiment.submit_annotations",
        packet_ref(packet)
        | {"reviewer": {"host": "fixture", "model": "fixture"}, "annotations": [annotation]},
    )
    result = service.invoke("sentiment.aggregate", packet_ref(packet))
    assert result["balance"] is None and result["counts"]["irrelevant"] == 1


def financial_fact(**changes):
    return {
        "issuer": "NSE:EXAMPLE",
        "metric": "revenue",
        "definition": "Fictional operating revenue",
        "value": "1200000000",
        "unit": "INR",
        "period_type": "annual",
        "period_start": "2025-04-01",
        "period_end": "2026-03-31",
        "basis": "consolidated",
        **changes,
    }


def test_numeric_claim_checks_scale_context_missing_values_and_tolerance():
    service = ReviewService()
    args = {"claim": financial_fact(value="120", unit="INR_crore"), "evidence": financial_fact()}
    result = service.invoke("evidence.check_numeric_claim", args)
    assert result["numeric_check"] == "passed" and result["context_check"] == "matched"
    assert not result["original_document_verified"] and result["semantic_review"] == "not_reviewed"
    args["claim"]["issuer"] = "NSE:OTHER"
    result = service.invoke("evidence.check_numeric_claim", args)
    assert result["status"] == "incomplete" and result["numeric_check"] == "passed"
    args["claim"] = financial_fact(value=None)
    assert (
        service.invoke("evidence.check_numeric_claim", args)["numeric_check"]
        == "insufficient_evidence"
    )
    args["claim"] = financial_fact(value="1200000001")
    assert service.invoke("evidence.check_numeric_claim", args)["numeric_check"] == "failed"
    assert (
        service.invoke("evidence.check_numeric_claim", args | {"absolute_tolerance": "1"})[
            "numeric_check"
        ]
        == "passed"
    )
    with pytest.raises(DomainError, match="negative"):
        service.invoke("evidence.check_numeric_claim", args | {"absolute_tolerance": "-1"})


def test_http_cli_protocol_roundtrip_nonce_and_unknown_functions():
    service = ResearchService(Settings())
    with TestClient(create_app(service=service), base_url="http://127.0.0.1") as http:

        def factory(url, **kwargs):
            return AgentClient(url, http=http, **kwargs)

        def call(*args):
            output = io.StringIO()
            code = main(list(args), client_factory=factory, output=output)
            assert code == 0, output.getvalue()
            return json.loads(output.getvalue())["data"]

        assert http.post("/api/protocols/invoke", json={}).status_code == 403
        assert len(call("workflows")["functions"]) == 10
        registration = call(
            "review",
            "--json",
            json.dumps(
                {"function": "evidence.register_sources", "arguments": {"sources": [source()]}}
            ),
        )
        sid = registration["sources"][0]["source_id"]
        packet = call(
            "review",
            "--json",
            json.dumps(
                {
                    "function": "evidence.prepare_verification",
                    "arguments": {
                        "claims": [
                            {"claim_id": "C1", "text": "Fictional claim", "source_ids": [sid]}
                        ]
                    },
                }
            ),
        )
        result = call(
            "review",
            "--json",
            json.dumps({"function": "evidence.render_citations", "arguments": packet_ref(packet)}),
        )
        assert result["citations"][0]["source_origin"] == "host_supplied"
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    assert service.reviews.sources == {}


@pytest.mark.asyncio
async def test_readiness_drift_is_consistent_in_catalog_preview_and_submission():
    class Drishti:
        ready = False

        def assert_ready(self, spec):
            if not self.ready:
                raise DomainError("schema_changed", "Schema changed in fictional adapter")

        def status(self):
            return {"state": "connected"}

        async def close(self):
            pass

    adapter = Drishti()
    service = ResearchService(
        Settings(
            mode="live", drishti_key="fictional", enabled_unverified=frozenset({"drishti.get_news"})
        ),
        drishti=adapter,
    )
    operation = {
        "operation": "drishti.get_news",
        "arguments": {
            "query": {
                "symbols": ["RELIANCE"],
                "from": "2026-10-01",
                "to": "2026-10-02",
                "limit": 1,
                "page": 1,
            }
        },
    }
    try:
        cap = next(x for x in service.capabilities() if x["operation"] == operation["operation"])
        assert not cap["enabled"] and cap["held_code"] == "schema_changed"
        with pytest.raises(DomainError, match="Schema changed"):
            service.create_plan([operation])
        adapter.ready = True
        plan = service.create_plan([operation])
        adapter.ready = False
        with pytest.raises(DomainError, match="Schema changed"):
            await service.start_run(plan["plan_id"], "fictional-stale-plan")
        assert not service.runs and not service._idempotency
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_import_retained_news_preserves_origin_and_expiry_without_refetch():
    service = ResearchService(Settings())
    try:
        operation = {
            "operation": "drishti.get_news",
            "arguments": {
                "query": {
                    "symbols": ["SYNTHA"],
                    "from": "2026-10-01",
                    "to": "2026-10-20",
                    "limit": 1,
                    "page": 1,
                }
            },
        }
        plan = service.create_plan([operation])
        run = await service.start_run(plan["plan_id"], "source-import-fictional")
        await service._tasks[run["run_id"]]
        oid = run["operations"][0]["operation_id"]
        before = service.ledger.snapshot()
        imported = service.import_review_sources(run["run_id"], oid, "NSE:SYNTHA")
        record = imported["sources"][0]
        assert record["origin"] == "retained_provider"
        assert record["passages"][0]["locator"] == "data[0].summary"
        assert record["provenance"]["path_root"] == "decoded_provider_payload"
        packet = prepare(service.reviews, record["source_id"])
        assert packet["sources"][0]["original_document_verified"] is False
        assert service.ledger.snapshot() == before
        with pytest.raises(DomainError, match="symbol filter"):
            service.import_review_sources(run["run_id"], oid, "NSE:SYNTHB")
        service._buffers.clear()
        with pytest.raises(DomainError, match="expired"):
            service.import_review_sources(run["run_id"], oid, "NSE:SYNTHA")
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


def test_workflow_discovery_partial_assessments_and_atomic_batch_validation():
    service = ReviewService()
    workflows = service.invoke("protocols.list_workflows", {})
    assert [w["protocol"] for w in workflows["workflows"]] == [
        "citation_review@1",
        "sentiment_review@1",
    ]
    sid = register(service)
    packet = service.invoke(
        "evidence.prepare_verification",
        {
            "claims": [
                {"claim_id": key, "text": "Fictional claim", "source_ids": [sid]}
                for key in ["C1", "C2"]
            ]
        },
    )
    with pytest.raises(DomainError, match="Unknown claim"):
        service.invoke(
            "evidence.submit_assessment",
            packet_ref(packet)
            | {
                "reviewer": {"host": "fixture", "model": "fixture"},
                "assessments": [assessment(sid), assessment(sid, claim_id="missing")],
            },
        )
    assert all(
        c["semantic_review"] == "not_reviewed"
        for c in service.invoke("evidence.render_citations", packet_ref(packet))["citations"]
    )
    submit(service, packet, sid)
    result = service.invoke(
        "evidence.audit_answer", packet_ref(packet) | {"claim_ids": ["C1", "C2"]}
    )
    assert result["assessment_counts"] == {"supported": 1, "not_reviewed": 1}
    assert result["status"] == "incomplete"
    with pytest.raises(DomainError, match="unique"):
        service.invoke("evidence.audit_answer", packet_ref(packet) | {"claim_ids": ["C1", "C1"]})
