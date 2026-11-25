"""Versioned local review contracts shared by Python, HTTP, CLI and future MCP."""

from margin.analysis.facts import FACT_SCHEMA


def obj(properties, required=()):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(required),
    }


def text(maximum=250):
    return {"type": "string", "minLength": 1, "maxLength": maximum, "pattern": r"\S"}


def array(items, maximum=12, minimum=0):
    return {"type": "array", "items": items, "maxItems": maximum, "minItems": minimum}


ID = text(100)
PROFILE = obj(
    {
        "host_search": {
            "type": "boolean",
            "description": "Declared host search access; does not imply document-reading access.",
        },
        "host_read_sources": {
            "type": "boolean",
            "description": "Declared host ability to open/read sources with its own tools. Omitted means unknown; Margin does not test or invoke those tools.",
        },
        "structured_assessment": {
            "type": "boolean",
            "description": "False selects inventory-only. True is a declaration, not verified semantic competence.",
        },
    }
)
PASSAGE = obj(
    {"passage_id": ID, "text": text(6000), "locator": text(120)}, ["passage_id", "text", "locator"]
)
SOURCE = obj(
    {
        "issuer": text(100),
        "title": text(400),
        "url": text(2000),
        "kind": {
            "enum": ["original_document", "news_article", "provider_summary", "source_locator"]
        },
        "date": {"type": ["string", "null"], "format": "date"},
        "date_kind": {"enum": ["published", "ingested", "unknown"]},
        "passages": array(PASSAGE, 8),
    },
    ["issuer", "title", "url", "kind", "date", "date_kind"],
)
CLAIM = obj(
    {"claim_id": ID, "text": text(1500), "source_ids": array(ID, 6, 1)},
    ["claim_id", "text", "source_ids"],
)
QUOTE = obj(
    {"source_id": ID, "passage_id": ID, "quote": text(2000)}, ["source_id", "passage_id", "quote"]
)
REVIEWER = obj({"host": text(100), "model": text(100)}, ["host", "model"])
ASSESSMENT = obj(
    {
        "claim_id": ID,
        "verdict": {"enum": ["supported", "partial", "contradicted", "insufficient_evidence"]},
        "quotes": array(QUOTE, 8),
        "rationale": text(1000),
    },
    ["claim_id", "verdict", "quotes", "rationale"],
)
ANNOTATION = obj(
    {
        "source_id": ID,
        "relevant": {"type": "boolean"},
        "label": {"enum": ["positive", "negative", "neutral", "mixed", "unclear"]},
        "quotes": array(QUOTE, 4),
        "rationale": text(1000),
    },
    ["source_id", "relevant", "label", "quotes", "rationale"],
)
PACKET = {"packet_id": ID, "packet_hash": text(64)}
SCHEMAS = {
    "protocols.list_workflows": obj({}),
    "evidence.register_sources": obj({"sources": array(SOURCE, 12, 1)}, ["sources"]),
    "evidence.prepare_verification": obj(
        {"claims": array(CLAIM, 8, 1), "host_profile": PROFILE}, ["claims"]
    ),
    "evidence.submit_assessment": obj(
        PACKET | {"reviewer": REVIEWER, "assessments": array(ASSESSMENT, 8, 1)},
        [*PACKET, "reviewer", "assessments"],
    ),
    "evidence.render_citations": obj(PACKET, PACKET),
    "evidence.audit_answer": obj(
        PACKET | {"claim_ids": array(ID, 8, 1), "claimed_verified_ids": array(ID, 8)},
        [*PACKET, "claim_ids"],
    ),
    "evidence.check_numeric_claim": obj(
        {
            "claim": FACT_SCHEMA,
            "evidence": FACT_SCHEMA,
            "absolute_tolerance": {"type": ["string", "number"], "maxLength": 64},
        },
        ["claim", "evidence"],
    ),
    "sentiment.prepare_analysis": obj(
        {
            "source_ids": array(ID, 12, 1),
            "issuer": text(100),
            "aspect": text(200),
            "from": {"type": "string", "format": "date"},
            "to": {"type": "string", "format": "date"},
            "date_basis": {"enum": ["published", "record_date"]},
            "host_profile": PROFILE,
        },
        ["source_ids", "issuer", "aspect", "from", "to", "date_basis"],
    ),
    "sentiment.submit_annotations": obj(
        PACKET | {"reviewer": REVIEWER, "annotations": array(ANNOTATION, 12, 1)},
        [*PACKET, "reviewer", "annotations"],
    ),
    "sentiment.aggregate": obj(PACKET, PACKET),
}
