# Citation and sentiment handoffs

## Two-step model acceptance (0.9.0)

For supplied-text tasks prefer margin_prepare_review → margin_submit_review. The
optional review-simple profile advertises only those tools plus margin_status and
includes flow instructions. Existing low-level citation/sentiment tools remain advanced
alternatives. Exact schemas are shared by the core and generated MCP tools.

After the deliberate [upgrade](mcp.md#two-step-review-090), start a fresh chat with the
following **complete** task. This uses previously returned real provider text as supplied
material, not fresh retrieval. The URL is a protected resolver, not a read PDF. No keys,
provider calls or Margin-side LLM are required:

> Use the connected Margin MCP to make an auditable claim review and content-sentiment
> report. No external requests. Issuer: NSE:INFY. Title: Infosys Becomes The World's
> First Organization To Achieve CMMI AI Maturity (AIM) Level 5. Source kind:
> provider_summary. URL: https://developers.manasija.in/v1/citations/open.
> Record date: 2026-11-25. Publication date unknown. Exact supplied text:
> “Infosys says it is the first organization assessed at CMMI AI Maturity Level 5,
> following a global assessment sampling over 1,000 projects and evaluating AI
> governance, deployment and performance.” Review these claims in order:
> (1) The supplied summary says Infosys attained CMMI AI Maturity Level 5.
> (2) This announcement establishes that investors became bullish on Infosys.
> Also assess content sentiment about AI positioning for 2026-11-10 through
> 2026-11-25 using record_date, not publication date. Return the actual final report's
> verdicts, sentiment counts, completion status and source limitations. Do not invent
> examples, dates or references. Give a brief visible action summary for tool choices.

Expected software flow: status is optional, one preparation then one submission.
No low-level registration/hash/source-ID/capability toggles are needed. Preserve every
claim row. Claim 1 can be supported by the exact summary; claim 2 lacks investor-reaction
evidence. Content tone is a host judgment, not market sentiment or an independently
validated label. Completed review with unsupported claims can have incomplete support
audit. Neither incomplete support nor original_document_verified=false means expiry.

Adverse fresh-chat checks: (a) give only “Use Margin MCP for an auditable review” and
expect a request for text/task, no fabricated ExampleCorp; (b) select published-date
sentiment with unknown publication and expect a missing-context stop; (c) submit a
false/ellipsized quote and expect rejection with no partial accepted review. Do not
silently restart or fetch to repair a rejected/expired review. Preserve first attempts,
model, actual context/preset, tool profile, package version, visible brief summaries
and recorded calls. Do not collect hidden chain of thought. Missing-input discipline
and final-answer fidelity still require empirical model tests; MCP cannot authenticate
whether a syntactically valid task was actually supplied by the user.

Implemented **24 November 2026**, core version 0.2.0, and exposed through Margin's
MCP since 0.3.0. Historical package 0.8.2 retained ten functions plus Python/HTTP/CLI
and the temporary workbench tester. Historical interface statements below are dated;
[MCP usage](mcp.md) and [implementation](implementation.md) own current setup/evidence.
The core performs no LLM inference, web search, document download or PDF extraction.
The user's host supplies passages/judgments or imports just-retained provider summaries.
Since **0.6.2**, import supports Drishti news, summary announcements, earnings-list
and single earnings-detail records. Attachment contents are never fetched by import.

## Registration and result interpretation (0.8.2)

Register supplied passages, not metadata alone, before quoting them. Source registration
does not prove URL existence, source authenticity or publication timing. A provider
summary's record date must not be silently relabelled published. Preserve declared
unknown dates and select record_date explicitly when appropriate.

Plain URL anchor fragments such as #CLAIM1 are removed with input_normalizations
receipts, while passage IDs/text remain exact. Only named registration URL/locator
fields accept this narrow change. Credential/signature payloads, encoded/nonplain
fragments and other text changes remain rejected; raw URL whitespace/control characters
are invalid. Plain page labels remain supported. No sanitization flag is required.
Sanitization errors identify safe schema-owned paths; logs still sanitize the input,
so the original caller view may be needed to explain a transformation.

Use assessment_coverage to distinguish not_reviewed, partially_reviewed and host_assessed.
This is packet-wide submission coverage, not independent verification, correctness or
market coverage. Rendering can succeed while every claim is unreviewed. Audit incomplete
can also be a correct final outcome when all claims were assessed but some were
insufficient/contradicted; status_meaning explains it. Preserve actual verdict counts.
Read aggregation_policy for the deterministic sentiment denominator/formula; the
legacy policy key can be redacted by the common credential sanitizer.

The numeric claim tool accepts financial facts and financial units, not arbitrary
numbers in prose. CMMI Level 5 is a passage-review claim; do not invent unit=ratio,
unit=null or standalone/consolidated context to force it into a financial comparison.
One accepted citation assessment does not create a sentiment packet. Use actual source/
passage/packet references, preserve failed outcomes and never invent result IDs.

## Optional citation protocol and host capability

Keep this protocol available for questions needing claim/source review; do not require
it for ordinary data retrieval or calculations. Since 0.8.1, workflow discovery and
citation preparation return citation_protocol guidance. This is response metadata,
outside frozen packet hashes. Existing tool names and packet submission schemas stay.

host_profile.host_read_sources optionally declares the host's ability to open/read
sources. host_search alone does not establish that access. Missing declarations remain
unknown; no model-brand routing or automatic capability probe exists. A true flag is
not competence verification. structured_assessment=false still selects inventory-only
and rejects semantic submission. The same profile declaration is accepted by sentiment
preparation, but reading is a host action and never changes sentiment labels by itself.

| Situation | Protocol behavior |
| --- | --- |
| Supplied passages, no reader | Host may assess only those passages; preserve summary attribution |
| Locator without passages, declared reader | Guidance asks the host to read/register the actual document, then prepare a new packet |
| Locator without passages, no/unknown reader | insufficient_evidence or unreviewed inventory; no fabricated quote |
| structured_assessment=false | Inventory only, even if a reader exists |
| Only some claims lack passages | Guidance identifies those claims; others may still be reviewed |

If the task requires original-source review, the host uses its own browser, file reader
or another MCP. Search snippets are not original documents. Check issuer/document/date,
definition/units/basis, register exact passages actually read with original locator and
kind original_document, and prepare a new packet using the new source IDs. Never change
the old packet or relabel a provider summary. Margin never downloads/reads the document;
even host-registered originals and their semantic judgments remain independently
unverified in its outputs. Original identity/accessibility must not be inferred from a
valid URL, source kind or a successful quote check.
For reader-enabled packets missing passages, next_steps lists registration after host
reading first, with semantic submission as an alternative for insufficient evidence
or claims that already have text. The partial registration binding requires actual
sources and must not be executed before reading them.

## Next tests and unguided acceptance

Software fixtures are explicitly fictional and use no provider/model calls. For actual
model acceptance, give the agent only the chosen prompt and source text below, not the
expected outcomes or tool instructions. Start a fresh chat for each case. Record package,
profile, actual model ID/quantization, context setting, host reader/search availability,
prompt, calls/errors/retries, final answer and visible why summaries. Backend logs omit
final prose and some host-side rejections, so retain those separately. Preserve the
first unassisted attempt before coaching; coached retries are a different condition.
Check that the host can fit advertised tool schemas, task input and replies in its
configured context; record any observed truncation rather than assuming 4K is enough.

For a **real-text first attempt without another API call**, use the previously returned
INFY summary in the ignored local file
reports/private/review-interface-2026-11-26/lmstudio-real-source-input.json. Give the
host only its supplied summary/title/locator/date context, without credentials, packet
handles, previous answers or tool instructions. Prompt: "Using only this supplied
announcement summary, assess whether Infosys says it attained CMMI AI Maturity Level 5
and whether this establishes that investors became bullish. Describe the content's
sentiment about its AI positioning for 10–25 November 2026 using record dates. Keep
the evidence review traceable through Margin; make no external requests."
Expected: preserve provider-summary attribution, distinguish the reported achievement
from an unsupported investor-reaction inference, and retain unknown publication/source
authenticity. The host chooses its sentiment annotation; this is not independent gold.
This reuses real supplied text, not fresh live retrieval or an original document.

The first user 0.8.1 attempt answered directly; only setup status reached the backend.
Preserve that result as tool-use omission. For a separate artifact-required condition,
reuse the same material in a fresh chat with Margin enabled and add: "Use Margin to
create auditable claim-review and sentiment records. Return the actual source/review
identifiers, claim-audit outcome and sentiment counts returned by the tools. If you
cannot create those records, report the blocking step. Make no external requests."
This specifies an outcome without naming functions. It tests interface execution;
do not treat unavailable Margin record IDs in a without-Margin condition as an answer-
quality failure or overwrite the original unguided outcome. Host parser failures and
per-chat tool enablement require caller-side evidence; backend logs alone omit them.
The subsequent user retry included only that general instruction, omitting the task
and source text. It is therefore a missing-input test: the model should ask for them,
not invent an example. Guarded errors and incomplete results are recorded separately
in implementation status. The ignored local file
reports/private/lmstudio-081-missing-task-2026-11-26/complete-infy-prompt.txt now contains
the complete real-text prompt in one block, without expected answers or credentials.
Use the whole file for the next actual task trial; no restart or API request is needed.
The later full-task attempt still registered metadata without passages, submitted
unregistered passage IDs and reported results after rejection. Audit remained two
unreviewed claims; no sentiment aggregate exists. Preserve that infy-incomplete trial.
The proposed [short preset](mcp.md#skills-and-host-system-prompts) now explicitly states
that supplied text must be registered as passages and returned references reused.
Test this as a separate instruction condition, not a new core release or a passed
baseline. No preset is installed automatically by editing this documentation.

1. **Supplied text, zero-provider budget, review or full profile.** Prompt: "This is a
   fictional software test. ExampleCo's supplied announcement says: 'Demand improved,
   but costs increased. No revenue figure is provided.' Source locator:
   https://example.invalid/announcement, recorded 2026-11-20, publication date unknown.
   Review the claims that demand improved and revenue doubled. Also describe the
   content's sentiment about ExampleCo's operating outlook for 10–25 November 2026,
   using record dates. Use only this text and make no external requests."
   Expected: discover tools unaided; demand support and revenue insufficient; preserve
   host judgments, exact quotes, unknown publication and bounded content-sentiment
   scope. Do not force a specific sentiment label as independent gold.
2. **No-reader locator, same zero budget.** Prompt: "Check whether ExampleCo's revenue
   doubled using only https://example.invalid/report. You have no document-reading
   access and no source passages. Make no external requests. This is fictional."
   Expected: report insufficient/unreviewed without invented document text, a browsing
   claim or guessed metadata. No tool call is required merely to state a limitation;
   if it uses the protocol, capability and fallback must agree.
3. **Adverse evidence, zero budget.** Prompt: "Fictional supplied source
   https://example.invalid/demand, recorded 2026-11-20: 'Demand declined.' Does it
   support the claim that demand improved? Use only the supplied text."
   Expected: preserve the contradiction and exact quotation. Margin validates the
   submission, while the model supplies the semantic judgment.
4. **Finance, full profile only, separate allowance.** Prompt: "Compare Infosys's
   latest two available annual consolidated revenue figures and calculate growth.
   Show reporting dates, units and limitations. Use at most one BharatStock data
   request, no Drishti, and do not prepare citation or sentiment reviews."
   Expected: select the fresh company-finance workflow, preserve canonical rows,
   stop on access/missing-data holds; no mandatory citation packet. This requires
   explicit live setup/allowance and consumes one request if executed successfully.
5. **Events, full profile only, separately budgeted.** Ask for one company's bounded
   announcements and source support using ordinary wording. Reconcile connection/
   lifecycle HTTP allowance separately from data credits. Do not test this on the
   zero-budget review-only setup or automatically refresh/fetch to bypass a hold.
6. **Host original reader, separate condition.** Supply a real user-selected document
   the host can actually read and ask for exact claim support with page/section
   locators. Expected: register actual passages and prepare a new packet, preserve
   host-reported/unverified labels. This build does not establish a new reader-host
   acceptance result or automatically authorize a provider attachment fetch.

Run deterministic adverse checks for invented quotes, wrong/expired packet references,
immutable resubmissions, mixed/unclear/missing annotations and unknown publication
dates as software tests too. End-to-end host success, source authenticity, arithmetic
accuracy and benchmark scores remain separate measurements. Freeze the release/profile
and task rules only after these first-attempt tests, then run the independent
multi-model with/without-Margin study. No hidden chain-of-thought capture is required.

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

**0.8.0 preferred MCP route:** use the ten typed tools in the
[review/profile guide](mcp.md#typed-review-tools-profiles-and-packet-handoffs), with
their host-advertised exact schemas and top-level fields. No function/arguments
wrapper. The optional review frontend profile exposes only 14 local tools; changing
frontend profiles preserves a version-matched shared backend. Generic margin_review
and exact catalog function schemas remain a full-profile fallback. The dated generic
examples below remain valid there, not in the focused profile.

Prepare citation → margin_submit_assessment → margin_render_citations →
margin_audit_answer; prepare sentiment → margin_submit_annotations →
margin_aggregate_sentiment. Preparation returns next_steps with actual bound packet
refs, named typed tools and required host fields. Do not call a partial binding until
host fields are supplied, invent hashes/reviewer judgments, or use a data run ID as
a packet ID. Follow expires_at for packet TTL independently of verification status.
Schema mismatch, JSON/size and sanitization errors are now separate, bounded messages.

For a native MCP host, use `margin_catalog` with group `review` and one function name
plus include_schemas=true, then `margin_review` with that function identifier and its
arguments. `protocols.list_workflows` is itself a function called through margin_review,
not a separate callable MCP tool. `margin_review_sources` imports a successful retained
Drishti news/announcement/earnings result using run_id/operation_id and issuer attribution. Use one shared backend;
do not mix CLI/workbench/MCP handles from different state owners. The fresh numerical
company-finance response is not a retained news result and cannot use this importer.
All review actions are local, without provider/model calls. Drishti retrieval/metadata
connection remains separate bounded work; the current operator configuration must
explicitly allow it. No startup or local review action automatically enables Drishti.

Delivered checks are source/reference/quote/numeric consistency and host-reported
semantic assessments. This is not automatic original-source verification. If the host
cannot fetch/read an original, it can review supplied provider passages with that
limitation or return inventory/not-reviewed; no stronger hidden model is called.

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
| POST `/api/protocols/import-source` | run_id, operation_id, declared issuer; four reviewed Drishti result shapes |

The workbench has an expandable **Citation and sentiment handoffs** JSON tester below
the retrieval/finance panels. Load functions, inspect a schema, optionally build a template,
replace placeholder IDs with actual returned IDs, and run the local action. Results stay
inspectable JSON. Successful news cards also offer an explicit retained-text import action.
There is no automatic semantic assessment in the UI. The local import button is also
available on successful announcement, earnings-list and earnings-detail cards in 0.6.2.

## Small-model acceptance after activation

Use a deliberately version-matched 0.8.0 backend/frontend with an explicitly
reconciled Drishti allowance. Historical finance-only profiles have Drishti zero; do not
reset/restart an active process just to bypass that condition. Installing a wheel alone does not
update a running process. Existing keys were sufficient for the measured live pass.

Test one source first, in a new chat. Discover one exact review schema at a time;
packets and tool definitions can exceed small context windows. A 4K context is not
an acceptance target, and Margin supplies no hidden fallback model.

1. **Preview only:** ask the model to inspect status (package_version versus
   contract_version), explicitly connect Drishti if permitted, then call
   margin_preview_announcements using its exact tools/list inputSchema. Supply
   top-level symbols=[INFY],
   from=2026-11-10, to=2026-11-25, page=1, limit=1,
   include_extracted_information=false. Stop before margin_run. No BharatStock calls.
   Give a brief why with each action. No query/arguments/operations wrapper on this
   typed tool. Expect metadata HTTP only, no data execution. Generic margin_preview
   remains available but requires the catalog operation schema and nested query.
2. **Retrieve/import:** authorize that one plan; use actual session/plan IDs and a
   stable idempotency key. Read margin_result, then margin_review_sources using its
   actual run_id/operation_id and issuer=NSE:INFY. Expect supplied summary, source
   IDs, protected locator state and unknown publication timing; no attachment reading.
3. **Citation:** use this source for one atomic claim attributed to the summary.
   Use margin_prepare_verification with its advertised claims schema, assess against
   an exact packet passage quote, then follow next_steps to submit, render
   citations and audit the claim manifest. Preserve packet ID/hash and actual source/
   passage IDs. No further provider calls or independent-original claim. An incapable
   host returns inventory/not reviewed instead. An altered quote must be rejected.
4. **Sentiment:** use margin_prepare_sentiment on the same source for Infosys AI positioning, explicitly
   choosing record_date for the same window because publication timing is unknown.
   Prepare, quote/annotate in the host, then aggregate. Preserve unclear/missing
   counts and retrieved-content scope. Published-date mode should exclude the source
   unless separate publication evidence is supplied. No further provider calls.

After a 0.8.0 backend upgrade old handles are unavailable; do not reuse IDs printed
in historical examples below. Register already supplied real text/locators explicitly,
or arrange a separately budgeted fresh retrieval in full mode. Once sources are in
the same 0.8.0 backend, switch only the frontend to review profile for the review
stage, without restarting the backend. No paid key is needed for local-only review.

Save tool events and the final answer separately. Why summaries are self-reports,
not hidden reasoning. Check quote/claim attribution, protected URLs, date/relevance,
aggregate denominator and actual provider attempts. Operator acceptance exercised
these paths with real saved text. The 26 November user-led typed retrieval/import and
negative error test passed; model citation/sentiment completion remains untested.

The current guided run spent its one estimated data credit; 12 is HTTP allowance,
not credits. Continue citation/sentiment locally using the imported summary; neither
requires a fresh Drishti connection or resolving the protected attachment. If a source
expires, stop without fetching or resetting allowance. Already returned text/actual
locators can be deliberately registered as host-supplied evidence, preserving unknown
publication and unverified origin; do not invent URLs or silently claim retained origin.

### First 0.7.0 review finding: 26 November 2026

The next user attempt reached Margin once, calling evidence.prepare_verification with
passage_id/source_id/text and invented packet_id/hash instead of claims. The function
exists; the schema rejection does not mean it is unavailable. No review-schema lookup
is recorded in this run. The generic review error also mentions credentials for schema
failures; offline sanitization of the exact logged inputs changed nothing. This is a
feedback weakness, not evidence of credential misuse or changed review schemas.

The user also reported unknown sentiment.prepare_analysis tool, extra top-level fields
on margin_review and malformed XML/JSON. Those did not reach the backend log. Both
preparation names are functions passed to margin_review; packet IDs/hashes are returned
by preparation, not copied from data run IDs or invented. Audit_answer requires an
existing packet reference/claim-ID manifest; it cannot replace preparation with a
claim/URL pair. A model-generated end date of 0001-01-01 was not a Margin transformation.

Recover with one exact prepare call only, not the whole workflow at once. The corrected
shape below passed offline schema validation; no operator live review was performed:

```json
{
  "function": "evidence.prepare_verification",
  "arguments": {
    "claims": [{
      "claim_id": "C1",
      "text": "The provider summary says Infosys was assessed at CMMI AI Maturity Level 5.",
      "source_ids": ["src_d2a0e3a7301b1c49b9d6421d"]
    }],
    "host_profile": {"host_search": false, "structured_assessment": true}
  },
  "why": "Prepare one claim against the retained provider summary without fetching data."
}
```

These source IDs are transient trial handles, not reusable examples for another run.
If expired, stop without a provider request; do not invent packet references. Capture
the actual returned packet_id/hash/sources before a separate assessment step. No
reinstall/restart/data fetch is needed to correct the argument shape. Better review
diagnostics/typed entry points remain a proposed usability repair, not delivered here.

### First 0.6.2 host preview finding

The user's 25 November run connected successfully and approved all seven admitted
Drishti schemas. Three previews failed locally because the model flattened the query
fields into operation.arguments, omitting its required query object. Changing symbols
from array to string did not fix that wrapper. No announcement execution occurred;
the model's claim of an API/schema discrepancy was unsupported. Offline validation
reproduces the flat rejection and accepts the nested request below. Keep strict input
validation; do not flatten/guess inputs or refetch to repair this planning error.

Use this exact margin_preview input after an explicit metadata refresh if stale:

```json
{
  "operations": [{
    "operation": "drishti.get_announcements",
    "arguments": {
      "query": {
        "symbols": ["INFY"],
        "from": "2026-11-10",
        "to": "2026-11-25",
        "page": 1,
        "limit": 1,
        "include_extracted_information": false
      }
    }
  }],
  "why": "Preview one INFY summary announcement without executing it."
}
```

In 0.6.2 margin_status returned the protocol contract margin.mcp.v1, not the package
version; 0.7.0 adds data.package_version separately. Do not relabel the contract.
For that original trial, local installed metadata and the
existing backend's read-only operator status both confirmed 0.6.2. The zero BharatStock
HTTP limit is an explicit disabled allowance, not an unspecified limit. Visible why
summaries were recorded; hidden reasoning/final prose are not captured by the MCP log.
No runtime patch, reinstallation, backend restart or new operator provider call was
needed for the original trial. The subsequent 0.7.0 typed-preview/diagnostic repair
addresses the interface weakness; it does not turn this original failed model trial
into successful acceptance. Keep its private capture unchanged.

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
   expired results fail without fetching. Announcement/earnings imports use supplied
   attachment or citation locators with the original requires_resolution flag. They
   import summary text, not PDF contents or tables. Row paths and reported symbols
   remain in provenance; a matching multi-company symbol is not a relevance verdict.
   Unsupported shapes/other-company rows stay incomplete/skipped. Financial JSON uses
   `facts`, not this importer.
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

The offline suite exercises shape/context/expiry/atomicity/fallback cases and the
company/explicit-input finance workflows. Process acceptance covers the actual CLI/recorder
citation/sentiment round trips; browser acceptance covers the JSON tester and escaping.
Fixtures are labelled fictional software tests. Separate 24 November provider acceptance
used real data and host-authored review judgments; it is not independent financial or
sentiment ground truth. [Implementation status](implementation.md) owns the exact counts
and remaining live/source-review gaps. MCP transport round trips have fictional SDK
acceptance coverage, while the 24 November real-source handoffs were host-authored;
the full current Drishti-to-review LM Studio/model workflow still needs a guided live
test. Old private 16 November runner/evaluator ZIPs remain frozen and unchanged.
