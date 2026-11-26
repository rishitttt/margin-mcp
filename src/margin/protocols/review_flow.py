"""Two-step supplied-text review; bookkeeping only, never semantic inference."""

import copy
import hashlib
import json
from contextlib import contextmanager
from uuid import uuid4

from margin.core.contracts import DomainError
from margin.protocols.handoffs import step


@contextmanager
def atomic(service):
    service._expire()
    stores = (service.sources, service.packets, service.sessions)
    snapshots = [store.copy() for store in stores]
    try:
        yield
    except BaseException:
        for store, snapshot in zip(stores, snapshots, strict=True):
            store.clear()
            store.update(snapshot)
        raise


def prepare(
    service,
    issuer,
    title,
    source_url,
    source_text,
    record_date,
    claims,
    source_kind="provider_summary",
    publication_date=None,
    sentiment=None,
):
    if not claims and sentiment is None:
        raise DomainError(
            "missing_context",
            "Supply actual user claims or a sentiment scope; ask for missing input, do not generate an example.",
        )
    selected = None
    if sentiment is not None:
        if sentiment["from"] > sentiment["to"]:
            raise DomainError("invalid_input", "Use ordered sentiment dates from the task.")
        selected = record_date if sentiment["date_basis"] == "record_date" else publication_date
        if selected is None:
            raise DomainError(
                "missing_context",
                "The selected sentiment date is unknown. Preserve record_date separately from publication_date; ask for context or omit sentiment.",
            )
        if not sentiment["from"] <= selected <= sentiment["to"]:
            raise DomainError(
                "scope_mismatch",
                "Supplied date is outside the requested window; do not invent another date.",
            )
    with atomic(service):

        def register(date, kind):
            return service.register_sources(
                [
                    {
                        "issuer": issuer,
                        "title": title,
                        "url": source_url,
                        "kind": source_kind,
                        "date": date,
                        "date_kind": kind,
                        "passages": [
                            {
                                "passage_id": "summary",
                                "text": source_text,
                                "locator": "supplied summary",
                            }
                        ],
                    }
                ],
                provenance={
                    "record_date": record_date,
                    "publication_date": publication_date,
                    "date_origin": "caller_declared_not_independently_verified",
                },
            )["sources"][0]

        base_date = record_date if record_date is not None else publication_date
        base_kind = (
            "unknown" if record_date is not None or publication_date is None else "published"
        )
        source = register(base_date, base_kind)
        citation = None
        if claims:
            citation = service.prepare_verification(
                [
                    {"claim_id": f"C{i + 1}", "text": text, "source_ids": [source["source_id"]]}
                    for i, text in enumerate(claims)
                ],
                host_profile={"host_read_sources": False, "structured_assessment": True},
            )
        sentiment_packet = None
        if sentiment is not None:
            desired_kind = "published" if sentiment["date_basis"] == "published" else "unknown"
            sentiment_source = (
                source
                if (base_date, base_kind) == (selected, desired_kind)
                else register(selected, desired_kind)
            )
            sentiment_packet = service.prepare_analysis(
                [sentiment_source["source_id"]],
                issuer,
                sentiment["aspect"],
                sentiment["date_basis"],
                host_profile={"host_read_sources": False, "structured_assessment": True},
                **{"from": sentiment["from"], "to": sentiment["to"]},
            )

        def refs(packet):
            return {key: packet[key] for key in ("packet_id", "packet_hash")} if packet else None

        review_id = "rvw_" + uuid4().hex
        context = {
            "issuer": issuer,
            "title": title,
            "url": source["url"],
            "kind": source_kind,
            "record_date": record_date,
            "publication_date": publication_date,
            "origin": "host_supplied",
            "original_document_verified": False,
        }
        session = {
            "review_id": review_id,
            "citation": refs(citation),
            "sentiment": refs(sentiment_packet),
            "context": context,
            "claim_texts": claims,
            "submission_digest": None,
            "result": None,
        }
        service._save(service.sessions, {review_id: session})
        packets = [p for p in (citation, sentiment_packet) if p]
        created = min(service.packets[p["packet_id"]][0] for p in packets)
        service.sessions[review_id] = (created, service.sessions[review_id][1])
        required = ["claim_assessments"] if claims else []
        if sentiment_packet:
            required.append("sentiment_annotation")
        binding = {"review_id": review_id} | ({} if claims else {"claim_assessments": []})
        return {
            "status": "awaiting_host_review",
            "complete": False,
            "review_id": review_id,
            "context": context,
            "source_text": source_text,
            "claims": [{"claim_number": i + 1, "text": t} for i, t in enumerate(claims)],
            "sentiment_scope": sentiment,
            "expires_at": min(p["expires_at"] for p in packets),
            "instructions": "Submit judgments in the same claim order with exact quote substrings (or null for insufficient evidence). Use only this review_id; Margin binds all source/passage/packet references. No original is authenticated. If the user supplied no task/material, ask rather than inventing it.",
            "next_steps": [step("review.submit", binding, required)],
        }


def submit(service, review_id, claim_assessments, sentiment_annotation=None, reviewer=None):
    service._expire()
    if review_id not in service.sessions:
        raise DomainError(
            "review_unavailable",
            "Review ID is unknown or expired. Use the exact review_id returned by preparation; nothing was recreated or fetched.",
        )
    session = copy.deepcopy(service.sessions[review_id][1])
    if len(claim_assessments) != len(session["claim_texts"]):
        raise DomainError(
            "assessment_count",
            "Submit one assessment per prepared claim in the original order; do not omit or add claims.",
        )
    if bool(session["sentiment"]) != (sentiment_annotation is not None):
        raise DomainError(
            "assessment_scope",
            "Submit sentiment exactly when it was prepared; do not omit or invent a workflow.",
        )
    reviewer = reviewer or {"host": "caller", "model": "unspecified"}
    submission = {
        "claims": claim_assessments,
        "sentiment": sentiment_annotation,
        "reviewer": reviewer,
    }
    fingerprint = hashlib.sha256(
        json.dumps(submission, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    citation = (
        service._packet(**session["citation"], kind="citation") if session["citation"] else None
    )
    sentiment = (
        service._packet(**session["sentiment"], kind="sentiment") if session["sentiment"] else None
    )
    if session["result"] is not None:
        if fingerprint != session["submission_digest"]:
            raise DomainError(
                "assessment_conflict",
                "This review has an immutable submission. Prepare a new review for different judgments.",
            )
        return copy.deepcopy(session["result"])
    with atomic(service):

        def quotes(item, packet):
            return (
                [
                    {
                        "source_id": packet["sources"][0]["source_id"],
                        "passage_id": "summary",
                        "quote": item["quote"],
                    }
                ]
                if item["quote"] is not None
                else []
            )

        audit, citations, aggregate = None, [], None
        if citation:
            service.submit_assessment(
                **session["citation"],
                reviewer=reviewer,
                assessments=[
                    {
                        "claim_id": c["claim_id"],
                        "verdict": a["verdict"],
                        "rationale": a["rationale"],
                        "quotes": quotes(a, citation),
                    }
                    for c, a in zip(citation["claims"], claim_assessments, strict=True)
                ],
            )
            citations = service.render_citations(**session["citation"])["citations"]
            audit = service.audit_answer(
                **session["citation"], claim_ids=[c["claim_id"] for c in citation["claims"]]
            )
        if sentiment:
            service.submit_annotations(
                **session["sentiment"],
                reviewer=reviewer,
                annotations=[
                    {
                        "source_id": sentiment["sources"][0]["source_id"],
                        **{k: sentiment_annotation[k] for k in ("relevant", "label", "rationale")},
                        "quotes": quotes(sentiment_annotation, sentiment),
                    }
                ],
            )
            aggregate = service.aggregate(**session["sentiment"])
        rows = [
            {
                "claim_id": f"C{i + 1}",
                "text": text,
                **copy.deepcopy(a),
                "judgment_origin": "host_reported",
            }
            for i, (text, a) in enumerate(
                zip(session["claim_texts"], claim_assessments, strict=True)
            )
        ]
        result = {
            "status": "reviewed",
            "complete": True,
            "review_id": review_id,
            "context": session["context"],
            "claims": rows,
            "support_audit": audit,
            "citations": citations,
            "sentiment": aggregate,
            "judgment_origin": "host_reported",
            "original_document_verified": False,
            "limitations": [
                "Judgments are supplied by the caller; matching quotes do not establish source authenticity, user provenance or truth.",
                "Review completion is distinct from all claims being supported; content sentiment is not comprehensive investor sentiment.",
            ],
        }
        session.update(submission_digest=fingerprint, result=result)
        service._save(service.sessions, {review_id: session})
        return result
