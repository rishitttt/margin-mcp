# Storage, refresh and evidence policy

Proposed policy, updated 24 September 2026. The current prototype enforces local-only PDF manifests and records operator-declared usage basis; it does not implement the full entitlement, retention or hosted-serving system below. These requirements do not imply permissions have been obtained.

## Separate technical capability from usage rights

A file can be technically downloadable while its use in a shared product remains unresolved. Distinguish four questions for every source: may Margin acquire it, retain it, process it with an external model, and serve it to this user? Local/private operation does not automatically authorize every kind of processing. Citation does not by itself grant reuse rights.

Record a source policy with an agreement or terms reference and review date. Track permissions independently for raw documents, extracted text, structured facts, embeddings, excerpts, and derived results. Do not assume that extracting facts or building an embedding removes all contractual restrictions. Unknown permissions stay unknown rather than becoming `true` by default.

Recommended policy fields:

```text
source_id, terms_url, reviewed_at, evidence_reference
acquisition_method, automated_fetch_allowed
raw_storage_allowed, text_storage_allowed, fact_storage_allowed
embedding_allowed, external_model_processing_allowed
raw_redistribution_allowed, excerpt_redistribution_allowed
fact_redistribution_allowed, derived_output_allowed
audience_scope, tenant_scope, retention_days, expires_at
attribution_text, deletion_requirements, review_status
```

Allow `allowed`, `denied`, `unknown`, or `conditional`, with the condition captured explicitly. Default serving policy denies a use that has no established permission. Academic/private records must not migrate into a public dataset just because the deployment changes.

## What to store versus retrieve

All retention recommendations below are conditional on the relevant source policy.

| Data | Storage recommendation | Refresh or live behavior |
| --- | --- | --- |
| Issuer and security identities | Versioned records with identifier validity dates and evidence | Initial manual verification; review on corporate events and periodic schedule |
| Filing metadata | Append-only publication observations with source links and revision relationships | Curated import in prototype; authorized feed or batch checks later |
| Original PDF/XBRL/HTML | Immutable private object keyed by content hash when retention is allowed | Fetch once; preserve a new version if bytes change |
| Parsed pages and tables | Rebuildable outputs tied to file hash and parser version | Reprocess after parser changes; keep earlier evidence lineage |
| Normalized reported facts | Exact decimals, source units, contexts and supporting locations | Updated by new filings; never silently replace historical facts |
| Calculated comparisons | Inputs, formula version and output; recomputable cache | Compute on request from compatible facts |
| Search index / embeddings | Derived, permission-scoped and deletable | Rebuild from permitted text; lexical search first |
| Macro observations | Values plus release/vintage metadata and units | Refresh around releases; preserve revisions when available |
| Price observations | Separate store and source policy if added | On demand or EOD; report market timestamp and adjustment basis |
| User documents | Private workspace/tenant scope and explicit retention | User-directed imports; deletions propagate to derivatives |
| User questions and model answers | Minimal operational retention; do not create a hidden training corpus | Store only what the product needs and the user expects |

There is no need for the language model's question to trigger an upstream download each time. Scheduled ingestion plus a fast local query is live access to Margin's stored data; it should be labeled with its real freshness, not advertised as a live exchange feed.

## Time and revision semantics

Preserve `period_start`, `period_end`, `period_kind`, `published_at`, `first_observed_at`, `retrieved_at`, and `normalized_at` separately. A fiscal-quarter label alone is insufficient. A historical document acquired today was publicly available in the past but was not necessarily present in Margin then.

Support two explicit views eventually: what was publicly available by a date, and what Margin had ingested by a date. If publication timing is uncertain, say so. A later restatement of an older period must not appear in an earlier as-of answer.

Store same-byte duplicates once, with multiple publisher references. Semantically similar exchange and issuer documents require a separate relationship rather than blind hash deduplication. Record `supersedes` or `corrects` links with evidence. Conflicting facts remain visible with their sources; a preferred-source rule must not erase the conflict.

## Serving behavior

Return a coverage summary with each tool result: supported companies, periods, document types, latest successful ingestion, gaps, and whether sources were refreshed for this request. Use `latest_available_in_corpus` unless the service can establish broader completeness.

Return normalized facts with source document, page/table/cell or XBRL context, source URL, and provenance state. Distinguish `reported`, `derived`, and `inferred`. A provider-supplied number without an original filing location is `provider_reported`; it must not masquerade as filing-verified.

Missing values have reasons such as `not_disclosed`, `not_in_corpus`, `parse_failed`, `not_comparable`, or `not_authorized`. Preserve reported zero as zero. Never fall back from consolidated to standalone without making the change explicit.

For hosted use, check source entitlements before returning facts or excerpts. Keep user files and credentials isolated. If a source requires deletion, remove originals and applicable extracted text, facts, indexes, caches and backups according to the agreed retention process.

## Free-prototype boundary

Keep the public repository focused on code, documentation, synthetic fixtures, and material explicitly permitted for redistribution. Keep private corpus files out of Git. Store collection manifests and provenance only to the extent permitted. A synthetic fixture can test software, but it cannot count as a real-company accuracy result.

A small private corpus has been acquired, as recorded in [BSE acquisition results](../research/bse-acquisition-results.md). Permission to host or redistribute that collection has not been established. Use explicit permission, an applicable academic route, or authorized customer-supplied files. The [source study](../research/data-sources.md) records the observed terms that motivate this boundary.
