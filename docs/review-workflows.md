# Citation and sentiment handoffs

Implemented **24 November 2026**, core version 0.2.0. These are local Python/HTTP/CLI
functions and a temporary workbench tester. Margin's own MCP adapter is not implemented.
The core performs no LLM inference, web search, document download or PDF extraction.
The user's host supplies passages/judgments or imports just-retained provider news text.

## What is checked, and what is not

Margin checks input schemas, reference identity, packet hashes/expiry, exact quotations
against **supplied** passages, typed numerical/context comparisons and deterministic
aggregation. It labels all semantic verdicts and sentiment annotations `host_reported`.
No returned original is independently verified. A successful local action or matched
quotation does not authenticate its website or establish that the claim is true.

The host can use a browser, file reader or a separate MCP to read an original and then
register its passages. Margin does not discover or call those tools. Unsupported hosts
receive locators/inventory and incomplete analysis; there is no fallback model or guessed
neutral label. Operator-declared profiles describe workflow availability, not competence.

## Entry points

Use the existing running backend from the [agent guide](agent-interface.md). Keep a
single backend per session; state and handles do not survive restart. These commands
perform no provider requests:

```sh
.venv/bin/margin-agent --why "Discover citation and sentiment contracts." workflows
.venv/bin/margin-agent --why "Inspect the citation packet schema." workflows --name evidence.prepare_verification
.venv/bin/margin-agent --why "Run the selected local review action." review --file request.json
```

`request.json` is exactly `{"function":"NAME","arguments":{...}}`, using the selected
schema. In the installed skill, pass the same commands to its `scripts/margin.py` helper.
All ordinary commands support the global --why option before the command; the existing
opt-in recorder captures summaries/results, including review receipt arguments.

Python: `ResearchService.review(function, arguments)` shares the service's sanitizer and
review store. The independent `margin.protocols.service.ReviewService` is also importable;
reuse one instance. Use its `invoke` method for untrusted inputs. Internal source import
assigns provider origin only after reading a retained sanitized operation result.

HTTP (all POSTs use the existing action nonce/JSON/same-origin protections):

| Route | Contract |
| --- | --- |
| GET `/api/protocols` | Ten local function schemas; zero network/inference |
| POST `/api/protocols/invoke` | Function + arguments object |
| POST `/api/protocols/import-source` | run_id, operation_id, declared issuer; retained news only |

The workbench has an expandable **Citation and sentiment handoffs** JSON tester below
the retrieval/finance panels. Load functions, inspect a schema, optionally build a template,
replace placeholder IDs with actual returned IDs, and run the local action. Results stay
inspectable JSON. Successful news cards also offer an explicit retained-text import action.
There is no automatic semantic assessment in the UI.

## Citation round trip

1. Register up to twelve source records using `evidence.register_sources`. Each has issuer,
   title, HTTP(S) locator, kind, date/date_kind and optionally bounded passages with unique
   passage IDs, text and page/section/field locators. Host records are always host-supplied.
   Decorative image URLs and exposed credentials are rejected.
2. Alternatively, after an explicit news retrieval, use
   `review-sources RUN_ID OPERATION_ID --issuer NSE:RELIANCE`. It imports up to twelve
   reviewed source-bearing rows with `retained_provider` origin and run/operation/path
   provenance. Long summaries are bounded at 6,000 characters; provider prose is not an
   original article. Unknown dates remain unknown. Wrong selected issuer filters and
   expired results fail without fetching. Financial JSON uses `facts`, not this importer.
3. Submit up to eight atomic claims to `evidence.prepare_verification`, each with a unique
   claim_id, exact claim text and allowed source_ids. The packet supplies instructions,
   source snapshots and an actual response schema. Retain its packet_id and packet_hash.
4. The host reviews the passages. If additional original text is needed, it reads that
   outside Margin, registers a new source record and prepares a new packet explicitly.
   Packets are not silently amended or refreshed.
5. `evidence.submit_assessment` accepts the exact packet reference, reviewer host/model
   identifiers and per-claim verdict/rationale/quotes. Supported, partial and contradicted
   judgments need quotes. Insufficient evidence may have none. Quotes must exactly match
   a permitted packet passage. This verifies consistency with supplied text only.
6. `evidence.render_citations` returns claim/source links with title, URL, date, passage
   locators, reviewer origin and explicit original-verification status.
7. `evidence.audit_answer` accepts the final claim-ID manifest. It counts supported,
   partial, contradicted, insufficient and not-reviewed claims; unknown IDs are rejected.
   Attempts to claim independent verification are flagged. It does not parse arbitrary
   final prose, confirm the host used all necessary evidence or prove semantic correctness.

`evidence.check_numeric_claim` separately accepts two existing financial-fact records
(`claim`, `evidence`) and optional nonnegative absolute_tolerance, expressed in the claim's
unit. It compares explicit INR scales and metric/context/adjustment metadata without
inferring a scale. Numeric and context outcomes remain separate; identical numbers from
wrong issuers are not a successful contextual check. Results are comparisons of supplied
facts, not authentication against an original filing. Caller tolerance must be justified
from source precision; the tool does not choose or validate that justification.

## Sentiment round trip

- `sentiment.prepare_analysis`: source IDs, declared issuer, aspect, explicit from/to dates
  and date_basis. Published-date scope excludes unknown/ingested dates; record_date scope
  is a deliberate alternative that does not establish publication timing. Other declared
  issuers, missing/out-of-window dates and duplicate exact locators are explicitly excluded.
- The packet provides positive/negative/neutral/mixed/unclear definitions and entity/evidence
  instructions. It does not inherit provider sentiment as an authoritative answer.
- `sentiment.submit_annotations`: reviewer metadata and source-level relevance, label,
  rationale and supporting quotes. Relevant non-unclear labels require quoted passages;
  no annotation may refer to an excluded source. All labels remain host reports.
- `sentiment.aggregate`: distinct-source counts and balance
  `(positive-negative)/(positive+negative+neutral)`. Mixed, unclear, irrelevant and
  unannotated sources are displayed separately and excluded from that denominator.
  Zero denominator returns null. Missing annotations never become neutral; partial/empty
  packets return incomplete. Counts are not independent-event counts, price predictions
  or comprehensive investor sentiment. Publication/as-of and entity accuracy remain
  limited by the declared/provider metadata and host judgments.

## State, capability and error behavior

Prepared inputs have immutable hashes; assessments are stored separately. Identical
resubmission is idempotent; a different submission needs a new packet. Partial submissions
are allowed but missing claims/labels remain visible. Validation is atomic: one invalid
reference/quote rejects the entire submission. Submissions do not extend original TTL.

A `host_profile` may declare `host_search` and `structured_assessment`. False structured
assessment selects inventory-only and rejects assessment submission until a new packet
with an updated profile is deliberately prepared. Unspecified availability is a handoff,
not verified ability. There are no model-brand branches or automatic capability probes.

Defaults: 30-minute source/packet TTL, 64 KiB action input, at most eight citation claims
and twelve sources per packet. Backend review state has max_records/max_buffer_bytes bounds
separate from operation-result retention (default 200 records/20 MiB); standalone ReviewService
uses 2 MiB. State is process-local and cleared at shutdown; no disk corpus is created.

Expected failures include source_unavailable, packet_unavailable, packet_mismatch,
quote_mismatch, missing_support, assessment_conflict, unsupported_assessment and capacity.
They never cause provider retries, refetches or model calls. Protected source locators stay
labelled as requiring resolution; this core does not obtain credentials for the host.

## Validation and remaining gate

The offline suite exercises shape/context/expiry/atomicity/fallback cases, all five company
wrappers and original finance tests. Process acceptance covers the actual CLI/recorder
citation/sentiment round trips; browser acceptance covers the JSON tester and escaping.
Fixtures are labelled fictional software tests. Separate 24 November provider acceptance
used real data and host-authored review judgments; it is not independent financial or
sentiment ground truth. [Implementation status](implementation.md) owns the exact counts
and remaining live/source-review gaps. Own MCP packaging waits for that core-validation
review; old private 16 November runner/evaluator ZIPs remain frozen and unchanged.
