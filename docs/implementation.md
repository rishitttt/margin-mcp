# Implementation and validation status

## User-led 0.7.0 review failure: 26 November 2026 IST

The next recorded action is one margin_review call with function
evidence.prepare_verification. That function exists in both the enum and review
registry; rejection came from invalid arguments before packet/source lookup. It
received passage/source/text plus a data run ID as packet_id and fabricated hash,
instead of claims and optional host_profile. No review-schema catalog lookup appears
in this run. No packet was created by that call.

Review's generic invalid_input mentions credentials/size for all validation failures.
Offline replay of the exact recorded arguments confirms sanitizer.clean returned
unchanged input: no credential misuse demonstrated. Schema-owned diagnostics identify
missing claims and allowed claims/host_profile. This feedback weakness remains
unpatched in 0.7.0; do not describe the error prose as a credential detection event.

User-reported sentiment function-as-tool, extra outer source/packet fields and malformed
tool-call XML/JSON do not appear in backend events; they were host-side routing/parser
failures. The suggested claim/source_locator audit_answer call is also invalid.
Context loss is unproven; model/context metadata is absent. This is not an upstream
failure, original verification or successful semantic review. Exact corrected prepare
arguments pass offline schema validation; operator made no live review/provider call,
runtime change, restart or allowance reset. Private request/response and host-reported
failure classifications are in reports/private/lmstudio-070-review-2026-11-26/.
See [review recovery](review-workflows.md#first-070-review-finding-26-november-2026).

## User-led 0.7.0 retrieval acceptance: 26 November 2026 IST

Recorded user calls confirm package_version 0.7.0, successful metadata connection,
typed announcement preview, explicit execution with the preview's actual session/
plan/key, successful result read, source import and the expected malformed generic
preview rejection. Seven user calls/14 events: six successful responses and one
deliberate invalid_input identifying missing query/allowed fields. Generic rejection
is the expected negative test, not an upstream error. Typed input was wrapped into
arguments.query by Margin; extraction remained false.

One INFY summary announcement was returned/imported as retained_provider with unknown
publication timing, original unverified and requires_resolution=true retained. The
source is supplied summary text, not downloaded PDF contents. Read-only operator MCP
status confirms same session c527a681dc9d4e28b2b2483be3deac73, B0/D6 HTTP so far,
one Drishti logical/data call and one completed estimated credit out of one allocated.
The other five HTTP attempts are metadata/lifecycle overhead; final cleanup is not
included while the backend remains active. No account balance/debit was remeasured.

Model prose incorrectly called 12 available credits: it is the HTTP limit; estimated
credit allowance is one and is now spent. Preview made no data call, but the preceding
connect did make HTTP attempts. The negative test's suggested symbols-only query would
still need the core's required discovery window/page/limit. These are reporting limits,
not evidence of another runtime defect. No patch/reinstall/restart/refetch is needed.

Private user capture/review is reports/private/lmstudio-070-live-2026-11-26/. The single
operator status request is saved separately from the original 14 user events. Visible
why summaries are present on preview/run/result/import/negative-test calls, absent on
the user's status/connect calls; no hidden reasoning or final prose is recorded. Host
model identity/context are not established by these logs. This is guided retrieval
acceptance, not a benchmark or completed citation/sentiment model test. Next: local
review of the same source without another connect/data call; source/packet TTL still
applies. Operator made zero provider/model API calls and changed no runtime or budgets.

## Typed event previews and schema feedback: 25 November 2026, 0.7.0

Evaluated plan `df45376` preceded runtime edits. Four generated typed previews add
margin_preview_news, margin_preview_announcements, margin_preview_earnings and
margin_preview_earnings_filing: **25 MCP tools**, unchanged underlying 13 retrieval,
15 local calculations, nine company functions and ten review functions. Discovery
query fields are top-level; the adapter constructs the reviewed core query wrapper.
Filing detail retains discovered-ID OR symbol/quarter selection. All paths call the
existing create_plan; no preview/GET/discovery causes provider connection or fetching.
Generic margin_preview and its catalog route remain compatible. Catalog direct_preview
names the flat alternative and its own host-advertised schema; the nested operation
schema is not its flat input schema. Exact schema authority is explicit in tools,
server instructions, catalog, guides and skill: advertised tool inputSchema for typed
calls, selected margin_catalog(include_schemas=true) for generic calls, generated from
reviewed core contracts rather than remembered examples or upstream docs. New native
contracts still require review; schema quarantine remains unchanged.

Retrieval validation now uses the existing bounded schema-owned diagnostics. The
logged flat query failure identifies missing required query and allowed fields;
unknown caller keys/values are not echoed. MCP status adds data.package_version,
separate from contract_version. Pure math, financial displays, source/quote semantics,
budgets, idempotency, provider transports and in-memory retention are unchanged.

**360 offline tests pass**, including generated-contract parity/isolation, typed versus
generic plan equivalence, wrapper/unknown-field rejection, protected diagnostics,
extraction/detail/readiness guards, explicit run/import and version distinction.
Official SDK source and installed-wheel acceptance cover all 25 tools: standalone
41 calls/82 recorded events; shared four frontends, 16 calls/32 events including four
typed-preview credit-budget holds. These use fictional providers, with no real API or
external model call. Installed checks reuse pinned dependencies, not a fresh OS setup.
Ruff/format, skill validation, links and credential/wheel checks accompany private
evidence under reports/private/typed-previews-2026-11-25/.

tools/list grew from 47,721 to 59,853 uncompressed JSON bytes (+25.42%). This measures
schema-advertisement cost, not model tokenizer usage. Typed calls remove a translation
step but do not prove small-model improvement or a 4K context fit. No new model-host
acceptance is claimed. The original 0.6.2 failed host trial remains unchanged/private.
Active mtest stays 0.6.2, with no installation, restart, quota reset or provider calls
by this build. The new versioned 0.7.0 wheel is separate from immutable older wheels.
Next: a controlled version-matched upgrade and one-source typed-preview host test,
followed by existing run/import/citation/sentiment steps without extra retrieval.

## First user-led 0.6.2 preview: 25 November 2026

Read-only operator status confirms the running backend and installed venv are 0.6.2,
same session 366a40cde7964091a21aaa9387eeb8ad, live with recording enabled. The user
called status, exact announcement catalog, one successful Drishti metadata connection
and three failed local previews. Seven reviewed schemas approved, no schema changes.
All three previews omitted the required operation.arguments.query wrapper. The first
used symbols=[INFY]; subsequent attempts changed only that field to a string. Local
invalid_input was not an API response and no announcement execution occurred.

Offline Registry validation reproduces the flat rejection and accepts the corrected
nested query. This is a host schema-use/reporting failure, not evidence of changed
upstream validation. The model also labelled contract margin.mcp.v1 as package version
and called BharatStock's explicit zero allowance unspecified. The earlier test prompt
asked for a package version that margin_status does not currently expose; use operator
status/installation metadata for that distinction. Visible why summaries are present.
Private original 12-event capture and review are in
reports/private/lmstudio-062-preview-2026-11-25/. No runtime change/new release,
operator provider call, purchase, restart or reinstallation. Corrected exact preview
input is in [review acceptance](review-workflows.md#first-062-host-preview-finding).

## Drishti-to-review repair: 25 November 2026, 0.6.2

Plan `2c1c91b` preceded one isolated INFY live pass; `78dc2b2` recorded measured
failures and the repair plan before runtime edits. Existing live 0.6.1 mtest and its
B1/D0 ledger were not restarted, installed over or given new limits.

All four upstream data operations succeeded: news (two items), summary announcement
(one, extraction=false), earnings discovery (one), and detail selected from its
returned ID. Actual **B0/D10 MCP HTTP attempts including lifecycle/cleanup**, four
logical operations, seven estimated credits; two separate free account GETs observed
943→936. This is an account-wide delta, not protection against concurrent activity.
Existing key/access was sufficient; no subscription purchase or additional API key.

The overall initial checker stopped after successful retrieval: earnings detail uses
`data: object`, causing KeyError in the list-only source importer. Announcement and
earnings sources were also empty because their attachment URL fields were ignored.
0.6.2 fixes the four reviewed projections through the same Python/HTTP/CLI/MCP core.
It preserves summary/locator paths, reported row symbols, unknown publication dates,
unverified origin and protected-locator flags from the original sanitized receipt.
Explicit mismatched rows are skipped; unknown operations/shapes stay incomplete.
No attachment extraction, generic upstream executor, model inference or new tool.
The workbench exposes the local import action on all four supported result cards.

Saved real responses were reprocessed offline: five source records (two news, one
announcement, list/detail versions of one filing). Citation round trip exercised
host-written supported/contradicted/insufficient verdicts, fabricated-quote rejection,
citation rendering, overclaim audit and inventory-only capability rejection. Sentiment
excluded all unknown-publication records in published-date mode; deliberate record-date
mode deduplicated the filing, retained four sources and kept missing/unclear annotations
outside its balance denominator. Operator labels are not independent gold or a new
LM Studio/model-host benchmark. No paid refetch occurred after the failure.

Separately, the host searched/read the matching [issuer press release](https://www.infosys.com/newsroom/press-releases/2026/worlds-first-organization-ai-maturity-level5.html)
and registered a short passage in a reader-enabled packet. Exact quote/citation and
published-date inclusion passed. The host read the website; Margin performed no web
request and still labels the semantic assessment host_reported/original unverified.
The provider phrase about sampling is not a substitute for the issuer's precise scope.

Validation: **342 offline tests pass**, Ruff/format (91 Python files), JavaScript syntax
and skill validation. Official SDK acceptance passes with 21 tools, 37 calls/74 events
standalone and four frontends/12 calls/24 events shared, over fictional fixtures only.
Installed-wheel checks reuse pinned dependencies, not a fresh OS installation. Fixed
the standalone acceptance helper's relative package-root resolution so an isolated
wheel check cannot silently fall back to the editable checkout after changing cwd.
The 0.6.2 wheel/checksum is saved separately from the immutable 0.6.1 artifact.
Private evidence and packaging checks are under
`reports/private/drishti-review-2026-11-25/`. Original
`live/summary.json` remains failed overall; it must not be overwritten by an offline
success. The new patch is not installed into the user's active environment. Next:
controlled version-matched activation, one-source small-model review test, then freeze
a benchmark profile. Concall/search admission and host-enforced final prose remain
separate future work; no claim of full native Drishti coverage or source authentication.

## Versioned wheel committed: 25 November 2026

At the user's request, the existing tested 0.6.1 wheel is saved under
[`releases/0.6.1/`](../releases/0.6.1/) with SHA256SUMS. It is byte-identical to the
earlier release evidence: 135,498 bytes, 58 archive entries, 48 Python files matching
the runtime source from `36d10b7`. Version metadata, known-key exclusion, private-file
exclusion, checksum and local documentation links were checked. No rebuild/runtime
change or new provider/model call; the existing 321-test/SDK evidence remains the
validation baseline, not a new acceptance run. Dist outputs stay ignored, and keys,
captures, private bundles and validation evidence stay outside Git. The live setup
and budgets are unchanged. [MCP installation](mcp.md#install) owns verification/setup.

## User-led 0.6.1 acceptance: 25 November 2026

The no-fetch HUL retest on the previous 0.6.0 backend returned identical data/request
ID and the pasted model answer now includes profit, revenue and the margin result.
After the user's 0.6.1 upgrade, INFY growth returned the correct amounts and distinct
absolute/percentage formulas. Same-key include_details retained report/request ID
and exposed raw INR inputs. Read-only status confirms the active 0.6.1 backend used
**B1/D0**, zero estimated Drishti credits and one request control. No extra operator
provider/model calls were made. The active B1 local allowance is now spent.

Core projection passes; the raw-versus-reporting final-answer task remains incomplete:
the model received raw details but printed report rows instead of the requested raw
value/unit pairs. It also said all values used crore despite percent/raw-INR fields
and named details.formulas instead of details.values.formulas. Clarify attribution:
BharatStock statement inputs are documented INR; Margin calculates growth/formulas
and normalizes reporting rows to crore. No new backend arithmetic/format defect was
found. Original issuer facts remain unverified.

These are guided checks with supplied arguments, not a general model benchmark or
context-overflow diagnosis. Latest calls omitted optional why; logs record tool
actions/results, not hidden reasoning or final prose. Original events/review are in
`reports/private/lmstudio-061-live-2026-11-25/`. No runtime change/new release is needed
for this audit. A same-key four-field extraction test can check raw-unit prose without
a new fetch or restart. Earlier installation-state notes below are historical.

## 0.6.0 live findings and 0.6.1 formula patch: 25 November 2026

The user-led 0.6.0 run contains one INFY growth execution, its identical-key replay,
its raw-details projection and one HUL margin execution. Original eight user tool
events are preserved privately. Read-only status confirms B2/D0 total, zero estimated
Drishti credits and two request controls. Same request ID/data for the INFY repeat;
details adds raw INR inputs without changing canonical crore rows or fetching again.
Exact growth arithmetic matches the returned inputs. HUL returned profit, revenue
and margin rows; the model's revenue-only final answer omitted two available rows.

**Margin defect:** the report builder copied a function-wide percentage-change
formula onto the absolute-change row. The model repeated incorrect metadata supplied
by Margin; the numeric amount/percent were correct. The same generic pattern attached
CAGR's formula to its input-years row. These are metadata defects, not bad API data
or arithmetic failures. Model-side errors remain separate: normalized crore values
mislabelled as raw provenance, a claim of no conversion despite Margin's normalization,
and an invalid margin_result/request_id follow-up. Context overflow is unproven.

Plan `bf43c96` preceded the 0.6.1 fix. Comparisons now add `values.formulas` by metric;
legacy `values.formula` remains the percentage formula for compatibility. The report
uses per-metric formulas/reviewed mappings, never a blanket function-wide formula.
Absolute change uses current-minus-previous; percentages use change/previous times
100. CAGR's elapsed years has no derived CAGR formula; CFO difference/coverage,
margins, TTM and grouped components retain their own formulas. Arithmetic, units,
data dependencies, response v2/rows-only shape and tool inventory are unchanged.

Regression checks first reproduced the faulty growth/CAGR metadata, then passed the
repair. **321 offline tests passed**. Source/installed-wheel SDK checks, lint/format,
documentation links and credential/package scans are recorded under
`reports/private/formula-metadata-2026-11-25/`. Live original events, review and an
offline corrected INFY projection are under `reports/private/lmstudio-060-live-2026-11-25/`.
Do not overwrite the original defective result or count an offline correction as
another live/model success. No original-issuer verification is implied.

The installed live backend remains 0.6.0 with its B2 local allowance spent. No agent
provider/model calls, purchase, live venv changes or backend restart were made. The
0.6.1 source/wheel fix does not mutate that process's cached replies. HUL can be
retested with its existing key, requesting every row including kind=result, without
another fetch. Point 4 (host-enforced final-answer validation) remains deferred.

## Canonical structured rows: 25 November 2026, 0.6.0

Plan `1ffec64` and the user-requested rows-only refinement `7281893` were published
before their respective runtime changes. Company response v2 supplies canonical
structured rows only; no generated prose summary/Markdown table. Exact row values,
units and formatted displays agree: money INR_crore, per-share INR_per_share,
percentages percent and ratios ratio. Calculated growth changes, CFO-minus-capex,
working capital/borrowings and TTM use reviewed units. Definitions, scope holds,
unknown dates and explicit comparison endpoints are preserved. Existing mathematics,
all 21 tools and data-access/duplicate/cancellation safeguards remain unchanged.

Raw-unit calculation `values`/compact `inputs` are opt-in `details`; `include_details`
changes projection, not financial intent, so the same inputs/key make no extra fetch.
The bounded record holds canonical rows plus compact details (32 KiB maximum), never
full provider payloads. Pure explicit-input/retrieval contracts are unchanged. See
[migration](mcp.md#reporting-contract-v2-and-migration).

Validation: **319 offline tests** including unit-scale, per-share, percentage/ratio,
zero/negative/null/unknown-unit, scope-held, comparison/TTM/readiness and same-key
projection coverage. All nine complete fictional company workflows have report checks.
SDK standalone and shared source/installed-wheel acceptance exercise default rows and
opt-in details: 21 tools, 37 calls/74 log events standalone, four frontends and 12
calls/24 events shared; no duplicate fetch. Fictional counts B2/D1 and B2/D0 respectively.
Installed acceptance reuses existing pinned dependencies, not a fresh cross-platform
installation. Ruff, skills, local links and credential/package checks are recorded
in the private release evidence.

Saved 0.5.0 HUL/INFY replies were reformatted offline; expected displays, computed
amounts/percentages and null starts are preserved. No fresh provider/model call or
original-source verification is claimed. Final saved-report sizes are in
`reports/private/canonical-rows-2026-11-25/`. Earlier template experiments were superseded
by the user's rows-only clarification and are not the delivered runtime.

Point 4 (host-enforced final claims/direct rendering) stays deferred. No verifier,
host hook, inference or dependency was added. A model can still misreport rows;
actual 0.6.0 model fidelity remains a user-led check. The live 0.5.0 mtest venv,
backend, keys and spent B2 allowance are untouched. Installed skill instructions
are synchronized while preserving private connection settings and old test packets.

## User-led 0.5.0 live acceptance: 25 November 2026

The user upgraded `mtest`/LM Studio to 0.5.0 and completed the guided preview,
HINDUNILVR annual margin, identical-key duplicate and INFY annual revenue-growth
checks. The private journal confirms successful direct calculations, identical
structured HUL replies/request ID, and the same backend identity throughout. Read-only
operator status confirms **two BharatStock HTTP attempts, zero Drishti attempts and
zero estimated Drishti credits**, with two finance request controls. No extra provider
fetch was made by this audit. Exact Decimal recomputation of HUL margin, INFY growth
and absolute change matched the returned values. No independent issuer verification.

Final prose remains a separate failure: the duplicate HUL answer inflated one profit
display by ten; INFY money amounts were divided by one hundred despite correct tool
input displays and percentage growth. The first answer also confused two financial
records with two input fields and suggested margin_result/run_id for a response that
has no retained run handle. Units come from reviewed documentation, not magnitude
detection. Do not score these answers as accurate merely because arithmetic succeeded.

These are guided acceptance checks with supplied exact arguments, not an autonomous
cross-model benchmark. Context exhaustion, model identity/settings and hidden reasoning
are not established by the MCP log; final prose was pasted separately by the user.
Private report/events: `reports/private/lmstudio-050-live-2026-11-25/`. All nine functions
retain offline coverage, but only fresh margins/growth were exercised in this live pass.
The backend's B2 local allowance is exhausted. Duplicate-key reporting-only retests
require no extra fetch; do not reset budgets or introduce a new key to rescue prose.
The build checkpoint below describes its earlier 0.4.0 installation state.

## Fresh-fetch company finance: 25 November 2026, 0.5.0

Plan `0e9710c` was pushed before runtime changes. `margin_company_finance` is a
self-contained typed tool over async `ResearchService.company_finance`: one fresh
BharatStock financials page, existing fact preparation/guards and one of the nine
company calculations, returning compact values/selected inputs/source context directly.
No earlier handle, retained raw source buffer, database, Margin LLM, Drishti connection
or new dependency. New keys fetch again even if legacy results exist. Default execution
is a local preview; explicit `execute: true` requires a stable key. Duplicate calls join
or return the same compact response; conflicting inputs block. Up to 200 compact
answers/controls (or smaller configured capacity), each bounded to 32 KiB, last for the
core process only. Cancellation of a waiter leaves work alive; provider uncertainty and
shutdown accounting remain guarded. No durable exactly-once/account-quota claim.

The MCP has **21 tools**, underlying catalog counts unchanged. Old retrieval, pure
math, company reuse, review, workbench/CLI and standalone/shared modes remain. No source
schema or financial compatibility checks were weakened. The initial larger page-size
proposal was rejected against the existing registry: two annual/eight quarterly rows
remain the bounds. Missing history/basis/fields stay incomplete, with no page exhaustion
or provider fallback. DCF/FCFF still require their explicit inputs/assumptions.

Validation: **288 offline tests passed**, including 36 new fresh-workflow checks. All
nine functions succeeded with deliberately complete fictional transport data. Tests
cover no-call preview/invalid inputs, one request, no raw-source buffering, ignored old
sources, units and missing dates with same-row provenance, continuing-profit selection,
scope holds, null/missing basis, quota/capacity, 401/403/429, uncertain timeout, concurrent
duplicates/conflicts, pending reads, waiter cancellation, shutdown, output bounds and
private recording. Source and installed-wheel SDK stdio acceptance each passed with
21 tools, 36 calls/72 log events and fictional B2/D1 attempts. Source/shared acceptance
passed with four frontend connections, 11 calls/22 events, stable identity, fictional
B2/D0 and zero duplicate dispatch. Installed shared acceptance passed the same checks.
Ruff lint/format and source/installed skill validation passed; the wheel was installed
in an isolated target using the existing pinned dependency environment (not a fresh
cross-platform dependency install). These use no real provider/model calls and do not establish
small-model behavioral success or current account entitlement.

Offline reprocessing of the saved 25 November HINDUNILVR annual response preserved
the expected continuing-profit margin and display units without guessed dates or new
requests. Readiness, balance-sheet, margins and cash-flow outputs succeeded; cash
conversion/profitability remained partial under the existing profit-scope guard.
Growth/CAGR remained incomplete with only one returned annual period. TTM was not
tested against that annual response. This is source-mapping/software evidence, not
independent issuer verification or another live run. See the [function map](reference/function-validation.md)
and [fresh-finance plan](design/fetch-and-calculate.md).

Private evidence: `reports/private/fresh-finance-2026-11-25/`. Versioned wheel is local
under `dist/`; no public package release or new paid plan. Existing `mtest`/LM Studio
live backend remains 0.4.0 with its prior allowances; this build does not restart it,
replace its installation, silently reset budgets or edit its keys. A controlled
version-matched upgrade and bounded live/model acceptance remain next.

## Financial fidelity and shared local state: 25 November 2026, 0.4.0

Plan `65c4901` was pushed before implementation. Retained financial results now include
`financial_view`: exact documented-INR to crore conversion, rounded displays, EPS per
share, separate operating-profit/PBT/EBITDA/total/continuing/owners labels, raw values,
source paths, reporting basis/dates, stock/flow kind, null/invalid distinctions and scope
warnings. Segments are converted separately. The view is bounded to eight rows and twenty
entries per segment array; raw payloads are unchanged. This is presentation/provenance,
not issuer-filing verification or a new financial database.

Six common local calculations have direct strict schemas: margins, unit conversion,
period comparison, cashflow metrics, profitability and balance-sheet metrics. They route
to the existing core without extra provider calls. The fourteen workflow tools/generic
calculator remain; total MCP tool count is twenty, underlying registry counts unchanged.
Source and installed skill references were synchronized; local connection settings stayed
unchanged. Measured serialized SDK tool definitions are about 41 KiB; this is not an LM
Studio tokenizer/context measurement or a model-performance result.

Optional `margin-backend` owns one core and journal behind an owner-only Unix socket.
Short-lived stdio proxies do not load provider keys or create another core. Private
framing/size/concurrency bounds, exclusive ownership, mode/version/epoch checks and safe
errors apply; lost replies are never automatically retried. Frontend disconnects preserve
active work, plans/results, idempotency and quotas. Source TTL/eviction still applies.
Backend shutdown/restart loses state and requires allowance reconciliation; this does not
provide durable account-wide accounting. Shared mode initially targets macOS/Linux;
standalone mode remains. No public HTTP or multi-user service is introduced.

Validation: **252 offline tests passed**, including private IPC guards, backend-restart
rejection, malformed frames, lost replies, no credential reflection, native schemas,
unit/label/null correctness and in-flight work surviving frontend exit. The sandbox
blocked Unix binding in the first test attempt; authorized local-socket runs passed with
external TCP blocked by the fixtures. Ruff lint/format, frontend JavaScript syntax, skill
validation and documentation links passed. Source and installed standalone acceptance
exercised all twenty tools in 33 calls/66 events with fictional data. Source and installed
shared acceptance exercised three separate frontends, nine calls/eighteen events, stable
identity, retained facts and duplicate submission with only one simulated provider attempt.
The installed wheel ran outside the checkout using existing pinned dependencies; clean
cross-platform dependency installation remains unverified. SDK negotiation was 2025-11-25,
not a claim of 2026-07-28 conformance.

The saved real HUL response was reprocessed locally to verify exact crore displays,
EPS, separate metrics, segments and continuing-profit warnings without another fetch.
A local LIVE-mode shared backend is explicitly running for mtest. Two installed status-only
frontends confirmed the same state owner and **zero B/D HTTP attempts**. Initial B allowance
was reduced from two to **one remaining local test request** after the earlier observed
request; D ceilings stay twelve HTTP/four estimated credits, not account balances. Only
Margin's host entry was switched to the socket after a private config backup; other
servers, keys and previous logs were preserved. The journal's initial readiness calls are
operator observations, not model results. No authenticated provider/model request or
purchase was made during implementation. Full evidence is private in
`reports/private/mcp-fidelity-2026-11-25/`.

Next: reconnect LM Studio and retest direct-schema construction, two-turn preview/execute,
retained-source calculations and final answer fidelity. Successful SDK/core tests do not
establish that Qwen now reports the financial values correctly. Broader host/model/rights
and public-release gates remain. [Current setup](mcp.md) owns commands and stop/start rules.

## LM Studio live financial retrieval: 25 November 2026

Qwen completed status, a fresh preview, run, status and result in one turn. The actual
receipt confirms one successful BharatStock HTTP attempt (1,513 ms), one annual
consolidated row and two total items in pagination; no Drishti operation was logged.
Score retrieval as passed and final-answer fidelity as failed: the narrative overstated
most crore values tenfold, replaced operating profit with the PBT field, expanded EBITDA
incorrectly and omitted the total-versus-continuing-profit scope caveat. The returned
payload itself remained raw INR with an explicit units warning. Provider documentation
was publicly rechecked; statement amounts are absolute INR, not crore. This is not an
independent validation of issuer financial statements.

The saved response was reprocessed through actual auto fact preparation, unit conversion,
company readiness, margins, profitability and cashflow functions, with zero new
authenticated provider/model calls. Unit evidence and continuing-profit guards survived:
readiness and the continuing-profit margin succeed, profitability is partial with mixed
scope components held, and growth/CAGR remain incomplete with only one annual row.
These core checks are separate from the observed model path, which did not call fact
preparation or calculation tools. Private corrections/outputs and receipt/hash references
are in `reports/private/lmstudio-live-2026-11-25/`. Prefer deterministic unit/metric
summaries and exact common-tool schemas next; resolve per-process state across host
restarts before promising multi-turn source reuse. Do not fetch extra pages to repeat
this review or relax financial scope checks.

## Repeated host launches and recording: 25 November 2026, 0.3.3

The active LM Studio configuration pointed --record-file at an existing log. Startup refusal was reproduced without modifying the file; app logs show corresponding repeated failures. The new mutually exclusive --record-dir option creates a unique timestamp/UUID 0600 JSONL on every launch and preserves earlier logs. New target directories are created 0700; existing directory permissions and retention are not silently changed. Fixed-file no-overwrite and write-failure safeguards remain. Source/installed repeated stdio launch tests validate recovery without provider/model calls. Validation: 233 offline tests and Ruff lint/format passed; two installed launches preserved prior logs. The mtest package and only its Margin recording configuration were updated after a private configuration backup.

Separate user-host evidence: qwen3-8b-03 executed the exact supplied payload successfully; qwen3-8b-04 independently discovered the schema, first omitted starts and received incomplete, then added the already declared starts and returned 15%. Task 1 is a pass with one recovery (three total tool calls), not first-try success. The final prose should keep the hypothetical label. These narrow arithmetic observations do not establish real-data, other-model or complete host readiness. Private evidence is under reports/private/mcp-recording-2026-11-25/.

## Financial schema-feedback repair: 25 November 2026, 0.3.2

All five failed calculation requests in the private second LM Studio log were reproduced. The catalog schema equals the runtime schema. Each had an extra `hypothetical` function-argument flag; removing it exposes a missing period-start hold, and adding the already declared starts yields 15%. Numeric strings and numbers both work. Safe bounded schema diagnostics now identify paths, permitted/missing fields and types without reflecting caller values or unknown names. No automatic repair or invented metadata was added. The top-level MCP wrapper still uses a generic nested arguments object; direct typed common tools remain proposed. **230 offline tests passed**, including repeated invalid-input recovery and diagnostic privacy. Installed-package/stdio checks and private evidence are under `reports/private/mcp-validation-2026-11-25/`; model completion remains pending a fresh-chat retest.

## MCP catalog-routing repair: 25 November 2026, 0.3.1

The first LM Studio/Qwen3-8B user attempt reached status/catalog; its private log has two
calls and no calculation/provider execution. The model then tried catalog identifiers as
MCP tool names and fabricated missing fact context in its proposed retry. This establishes
connection/discovery only, not a completed agent workflow. The earlier numbers-only test
prompt was underspecified for the fact-based margin function.

Every catalog entry now supplies `mcp_execution` (tool, binding and input location), and
tool/server instructions distinguish identifiers from callable names, recommend filtered
schema lookup and forbid invented financial context. Unknown tools produce JSON-RPC
`-32602` errors with safe recovery guidance; no alias silently dispatches calculations.
Core math and fact guards are unchanged. A declared hypothetical margin returns 15%; a
missing period start remains incomplete, with zero provider requests in live mode with
zero allowances. Actual SDK stdio tests confirm protocol errors and continued operation.
Validation: **224 offline tests passed**, Ruff lint/format passed, and all-14-tool source
acceptance passed (27 calls/54 events, fictional upstreams). Installed-wheel testing is
recorded privately under `reports/private/mcp-routing-2026-11-25/`; successful Qwen workflow
completion must still be retested. See [recovery prompt](mcp.md#lm-studio-catalog-routing-repair-031).

## Local stdio MCP alpha: 25 November 2026

Delivered package **0.3.0**, `margin-mcp` / `python -m margin.interfaces.mcp`. Fourteen workflow tools use one process-lifetime ResearchService, preserving the existing 37 retrieval/finance operations and ten review functions. The workbench/CLI/skill remain available independently; no HTTP backend is required for MCP. The [architecture](design/mcp-aggregation.md) was published before code as `07b981a`, after the tested source-only core checkpoint `6b22f57` was pushed. The user explicitly superseded the old no-MCP gate.

Implemented catalog/schema discovery, preview/company preview, session-bound idempotent run submission, bounded waits, retained results/facts, direct calculation, explicit connection/cancellation and review/source-import handoffs. Mode, per-process/call IDs and caveats survive structured plus JSON-text results. Inputs/schemas, credentials, output bounds and safe errors are guarded. Stdout is protocol only; provider connections are never started by listing/status/preview. Optional private JSONL records sanitized tool requests/results and visible why summaries, not hidden reasoning. Pre-log failures stop dispatch; post-log failures preserve the available result and warn.

Validation: **220 tests passed**, Ruff lint/format, JavaScript syntax and documentation links/diff checks. Source and isolated-wheel SDK stdio acceptance each exercised **all 14 tools in 27 calls**, negotiated **2025-11-25**, recorded **54 events**, and covered finance, idempotency, source reuse, news import and citation/sentiment round trips. Separate guards cover invalid/oversized/nonfinite input, wrong process, cancellation, EOF/lifespan cleanup, private log permissions/overwrite/write failure and live-mode zero-budget inspection. The first cancellation test mistakenly used the Drishti-only delay for a BharatStock call; an explicit in-process transport barrier fixed the test setup. These are fictional software fixtures, not live-company answers.

The wheel builds, passes credential/private-data scans, imports from an isolated target and launches its console script outside the checkout using existing pinned dependencies. Clean dependency installs on every platform and real-model host behavior remain unverified. No authenticated provider/model call, purchase or host-configuration change occurred for the adapter. Private evidence: `reports/private/mcp-alpha-2026-11-25/`; usage/configuration in [MCP guide](mcp.md). The built wheel stays in ignored `dist/`; old evaluation ZIPs remain unchanged.

Before publishing the core checkpoint, numerical evaluator inputs were moved from source into an ignored operator-supplied file; two new tests verify missing/mismatched keys fail before package creation. That checkpoint had 194 tests. Optional research remains separate and is not a product import. Next: a new-chat host trial and separately budgeted live MCP probe, then versioned model comparisons.

## Finance/data repair completion: 24 November 2026

Implemented documented auto units with evidence/provenance, explicit unknown mode, live conflicting-unit rejection, path-specific snapshot units, stock/flow fact separation and guarded calendar-quarter interval derivation. Raw provider values are preserved. TTM now accepts eligible HUL quarters; missing/longer/derived/basis-change periods remain held.

Added four local functions (balance-sheet metrics, cash conversion, profitability and fact reconciliation) and four company wrappers including data readiness. Inventory is 13 retrieval + 15 local + nine company functions, plus ten separate review functions. The company margin prefers separately returned continuing profit. Group/owners margins and cash/profit conversion are withheld when the returned continuing/total profit scopes differ. No automatic company FCFF/DCF forecast is supplied. See [finance data support](design/finance-data-support.md).

The added Drishti announcement flag was reviewed against metadata. Margin explicitly sends `include_extracted_information: false`; true remains outside the approved exposed contract. One bounded HUL summary execution succeeded. Required router/nested-schema drift guards remain.

Validation: **192 offline tests passed**, Ruff lint/format, JavaScript syntax, updated source-skill validation, separate-command synthetic CLI/recorder acceptance (33 commands) and expanded synthetic Chrome desktop/mobile acceptance. The first browser attempt lacked Playwright’s cached binary; installed Chrome worked, then an outdated catalog-count assertion was updated before the successful acceptance run. Fictional browser ledger counts are not provider usage.

Real usage for this repair: **B2/D13 HTTP** (Drishti metadata-only six plus reviewed execution/lifecycle seven), **one estimated credit**, actual debit unmeasured. The D ceiling was prospectively revised from 12 to 14 after observing lifecycle cost. No failed/uncertain paid call was retried. Initial fresh financial processing yielded 14 success/two incomplete; the later scope guard was checked by reprocessing the same responses without further calls, yielding **12 success/two partial/two incomplete** across 16 annual/quarterly company cases. **32 independent arithmetic checks matched** final outputs. Announcements, TTM and company/fact unit paths are now exercised successfully.

The issuer/NSE PDF text explains product-sales versus operating-revenue differences. Local issuer download returned 403, NSE direct transfer failed, and the browser PDF remained blank; full visual/download verification was not achieved. Selected textual comparison is not a full filing audit. The older Reliance raw/normalized earnings discrepancy was not retested.

Private evidence and hash manifest: `reports/private/finance-repair-2026-11-24/`. Old audit/evaluation ZIPs remain frozen. No provider purchase/contact, external model call, commit, push or downstream MCP implementation. Core financial definitions and acceptance still need user review before packaging.

## New-ticker function audit: 24 November 2026

Fresh HINDUNILVR/NSE calls exercised the public core and retained-data calculations.
The [function matrix](reference/function-validation.md) covers all 13 retrieval operations,
11 explicit-input local functions and five company wrappers. Outcomes: **22 success,
two incomplete TTM paths, one schema-held announcements path, four valuation functions
requiring explicit inputs**. Earnings detail now succeeded using a discovered real ID;
the earlier budget-blocked detail gap below is closed. This is retrieval success, not
independent validation of the provider's extracted earnings or original documents.

**167 offline tests passed**, including 24 new parametrized orchestration checks. Thirteen
independent Decimal recomputations matched returned-input arithmetic. Annual cash-flow
data supported metrics; quarterly CFO/capex and quarter starts were absent. Monetary
scale was caller-declared. FCFF/DCF/scenarios/sensitivity retain passing software reference
tests; no company forecasts or valuation assumptions were fabricated for this audit.

Actual attempts: **BharatStock 7, Drishti 12** including lifecycle/cleanup; eight estimated
credits, actual debit unmeasured. No paid retries. Full sanitized cases, schemas, receipts,
JUnit results, arithmetic checks and hash manifest are in the ignored private folder and
ZIP `reports/private/function-audit-HINDUNILVR-2026-11-24`. The ten review functions retain
separate offline/previous CLI/browser evidence; this was not a fresh semantic/model-host
test. Announcements schema review, independent source review and approval of core
acceptance remain gates before downstream MCP packaging. No purchase, commit or push.

## Core review workflows and readiness: 24 November 2026

Implemented core version **0.2.0**, without an LLM service, search/PDF engine, persistent
financial corpus or downstream MCP server. Read [review workflows](review-workflows.md)
for the ten delivered local functions, limits and actual Python/HTTP/CLI/UI contracts.

- Added `margin.protocols` source registration, immutable expiring citation packets,
  attributed host assessments, supplied-quote/reference checks, citation rendering,
  structured final-claim auditing, numeric/context comparison, sentiment packets,
  host annotations and deterministic source-count aggregation. Model capability profiles
  are caller declarations; no brand routing or hidden model fallback occurs.
- Added retained-news import with explicit issuer/operation/path provenance. Host-read
  passages and provider summaries stay unverified originals. Mixed/unclear/unannotated
  sentiment is separate; missing annotation is not neutral. Final prose is not automatically
  parsed, and no successful action promotes host judgments into independent verification.
- Added `/api/protocols`, `/api/protocols/invoke`, `/api/protocols/import-source`, CLI
  `workflows`/`review`/`review-sources`, and a workbench JSON tester/news import action.
  These share one backend and the existing optional --why recorder; successful review
  receipts retain full supplied arguments without provider/model calls.
- Drishti live catalog, preview and pre-submission checks now reflect actual metadata
  readiness. UI capabilities update after connection-state changes. An additive native
  `report_issue` appeared while all four approved routing schemas stayed unchanged; the
  adapter leaves additions unexposed/uncalled and still rejects missing, duplicate or
  changed required routing tools. Nested `get_announcements` remains held.
- Financial fact references now explicitly name `decoded_provider_payload` as their
  field-path root. Added successful reference coverage for all five company wrappers.
  Existing eleven finance functions remain; this is not automatic company forecasting
  or integration of Advait's code, which has not been supplied.

Validation: **143 offline tests passed**, Ruff lint/format over all maintained code,
JavaScript syntax, skill validation and documentation link/diff checks. Separate-command
CLI acceptance passed with citation/sentiment round trips and visible summaries (33 log
events); synthetic browser acceptance passed the complete existing workflows plus local
review discovery, escaped source registration and no additional provider traffic. The
first browser attempt used an incorrectly zero-Drishti fixture allowance; the corrected
fixture setup passed. A 0.2.0 wheel builds, passes credential/research-data scans and imports
from a separate installed target using existing dependencies. A clean dependency install
on every target platform remains unverified. Old 16 November private ZIPs were not rebuilt.
The installed global skill/reference was deliberately updated without changing connection
or recording configuration. Skill validation used a temporary PyYAML install only; no new
project dependency was added.

Real functional acceptance, separately retained under ignored private reports:

| Check | Actual observation |
| --- | --- |
| BharatStock | Ten HTTP attempts; all six implemented operation types succeeded across RELIANCE/TCS snapshots, annual/quarterly financials, directory, ratios, actions and prices |
| Company workflows | Margins/cash-flow/growth/CAGR succeeded for both companies with zero extra provider attempts; real TTM remained incomplete because quarterly start dates were absent |
| Drishti | Initial native catalog stopped before data dispatch; metadata-only audit identified the added unexposed tool; after the reviewed policy repair, categories/news/earnings-list succeeded |
| Citation/sentiment | Two actual returned provider news records completed host-authored citation/sentiment handoffs; supplied quotes matched, original verification stayed false, and an unsupported independent-verification claim was flagged |
| Remaining provider paths | Announcements held before preview for schema drift; earnings detail blocked before HTTP dispatch by cleanup reserve, with no retry |
| Accounting | B10; D18 observed HTTP attempts across initial/diagnostic/repair passes, plus at most one initial cleanup attempt not captured by the first pre-close snapshot (conservative bound D19, below the announced D20 cap); three estimated data credits, actual account debit not measured |

Monetary INR scales were explicitly caller-declared for functional calculations. No new
original-filing verification or independent sentiment gold is claimed. The repair report's
limits header accidentally retained first-pass defaults; its authoritative ledger correctly
records B0/D10. The probe script and a separate private reconciliation record correct the
reporting/reserve issue without overwriting original receipts or replaying paid calls.

Private evidence: `reports/private/core-acceptance-2026-11-24/`,
`reports/private/core-acceptance-2026-11-24-drishti-repair/` and
`reports/private/core-browser-2026-11-24/`. No provider purchase/contact, external model API
call, commit or push occurred. Host-authored functional annotations are not independent gold.

**MCP gate remains open:** review changed announcement inputs, complete a separately
budgeted live earnings-detail check using its real returned selector, independently review
financial/source cases, and approve the core acceptance matrix. Optional server-side
source resolution remains backlog. Downstream MCP packaging has not begun.


**24 November planning-only checkpoint:** the [build plan](plan.md) and [capability routing](design/analysis-and-protocols.md#45-capability-routing-and-model-limitations) now cover citation/sentiment workflows, simple decision trails, MCP packaging and separate model comparisons. No runtime, dependency, provider/model call, purchase, commit or push was made. These proposed features remain unimplemented. Earlier executable checks below were not rerun for this documentation revision.


### Function Lab frontend: 16 November 2026

Saved the pre-redesign nonignored working source, Git status and SHA-256 manifest in the ignored local `reports/private/frontend-checkpoints/20261116-144155/`. The ZIP includes uncommitted code/docs as they existed before this frontend change; it excludes ignored credentials/private data. It is a recovery snapshot, not a commit or a replacement for subsequent work in the other chat.

Redesigned the static workbench with charcoal navigation, violet accents, source-selection tiles, explicit process limits and two views: Retrieval and Finance. Removed the dedicated DCF tab/form; backend valuation implementations and their existing tests remain intact. All thirteen retrieval operations are inspectable/testable through the individual JSON operation tester, including directory/identity/categories. Five company workflows and scoped fact pairs remain, and all eleven local calculation contracts are available within Finance. Preview now exposes planned arguments before Run. Catalog reads/starter generation do not dispatch requests; held operations stay blocked. Old `valuation` session preferences fall back to Finance.

Validation: **126 offline pytest checks passed** in the shared checkout; Ruff lint/format over `src tests scripts research skills packaging`, JavaScript syntax and `git diff --check` passed. Updated synthetic Chrome acceptance passed prerequisite checks, duplicate-submit protection, retained reuse, unit/company isolation, history/reload, expired-source behavior, stale-preview rejection, explicit FCFF, malformed JSON, old-tab migration, full catalog access, held-operation guard, retrieval/earnings detail, escaping/redaction and both mobile layouts. No JavaScript errors or external page requests. Desktop/mobile viewport screenshots were inspected; local images remain ignored under `reports/private/frontend-redesign-checks/`. These establish software behavior only. This frontend task made zero live provider calls, purchases, commits or pushes. The main chat's agent packaging/logging work is preserved; its separate private bundle is not rebuilt by this frontend task.


16 November live-test checkpoint: separate 16-task RELIANCE/TCS runner and evaluator ZIPs are built locally; fresh live calls, DCF excluded, --why visible summaries and sanitized submission export. 126 offline tests and relocated synthetic package acceptance pass; first returned live agent pilot evaluated: 38/38 automatic checks with manual caveats (not an overall scientific score). See [live skill evaluation](live-skill-evaluation.md) for build/run instructions, actual preparation costs, source-key review status and limitations.

Current state: **the first reusable Python core and temporary local workbench are implemented and validated with synthetic data.** Provider transport is BharatStock REST + Drishti MCP; Margin MCP packaging remains later. The user’s seven-page 21 October workbench export shows eight successful live RELIANCE calls across both providers, including Drishti news, announcements and earnings discovery. Broader operation coverage, actual account debit reconciliation and financial/source verification remain pending. Authenticated source evidence remains the dated 8/9 October tests. Earlier MCP-first architecture decisions below are historical and superseded by the 20 October planning checkpoint. This file owns delivered state; [active design](design/core-workbench.md) and [plan](plan.md) own future work.

**15 November implementation checkpoint:** reviewed-path financial facts, eleven local calculation functions (including explicit-input FCFF/DCF, sensitivity and scenarios), complete sanitized argument receipts and workbench analysis controls are now implemented. Fresh bounded source inspection preceded these additions; the detailed checkpoint below separates real provider access from offline arithmetic/browser tests. No automatic source-backed DCF population, citation verifier, sentiment protocol, research harness or downstream MCP server is delivered.

## Branch transition

- Prior local-corpus/PDF implementation: preserved at `c77963d` on pushed [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1).
- Aggregation research/planning committed on `main` as `be04aba` before cleanup.
- Legacy code, tests, examples, CI, package manifests and superseded guides removed from `main` through a normal commit, without branch resets/history rewriting. Ignored local artifacts were not removed.
- `main` now contains the installable `margin-research` core/workbench, synthetic tests and current documentation. No downstream Margin MCP server, universal financial normalization or claim verifier is implemented. The old corpus CLI commands are not supported on this branch.

## Validation

### Portable local bundle and visible summaries: 16 November 2026

Built a private portable ZIP containing the runtime wheel, constrained dependencies, skill/launcher, complete function reference, generated offline schemas, relocatable setup/backend helpers and optional recorder. At the user's explicit request it includes both supplied trial keys only in `private/providers.env`. The ZIP is created with 0600 permissions under ignored `reports/private/packages`; credentials are absent from source, SKILL.md, Git and logs. The builder checks plain files and compressed wheel contents, rejects credential-bearing non-ignored repo output, and refuses existing output paths. The archive includes no previous provider payloads, model conversations, gold or workstation-specific connection configuration.

The standalone setup creates a new local runtime/skill path and optionally a labelled evaluation session from the actual question and retention date. It defaults to live mode; explicit backend startup defaults to one BharatStock attempt and zero Drishti calls. Separate agent copies still share account quota through the keys; local counters do not coordinate across machines. Source distributions now include the skill/packager/recorder helpers while excluding generated connection settings.

The skill now links a reference naming all 29 delivered functions, facts, control commands and limitations. Evaluation-session `note` supports brief visible decision/observation/limitation summaries with optional run/operation links. Logs label these as agent self-reports and version the instrumentation; task/notes/results/final answers use configured provider-key redaction. Finish reports actual summary/tool counts and flags missing summaries. No hidden chain of thought or full host transcript is captured, and recording compliance/faithfulness is not inferred. Frozen replay, model runners, independent gold/grading, citation verification, sentiment and our MCP adapter remain pending.

Validation: **117 offline tests passed**, plus Ruff lint/format over `src tests scripts research skills packaging` and the supplied skill validator. Tests cover safe credential-file parsing, keyless/private bundles, compressed-wheel spill rejection, output preservation, complete inventory coverage, summary linking/redaction/counting and previous functionality. A process test relocated the final archive into a new folder with spaces, configured a temporary workspace/session with an explicitly preinstalled runtime, started the fictional backend and recorded eight tool observations, two visible summaries and a final answer. Key redaction/idempotency/shared accounting passed; its private extraction was removed and backend stopped. The earlier sixteen-command fictional acceptance also still passed. The installed global skill/reference was updated while preserving its unrecorded connection configuration.

This update made **zero live provider calls, zero paid/model calls and no new subscription/purchase, commit or push**. Portable testing used the explicit `--skip-install` path, so fresh internet dependency installation, cross-platform setup, native discovery in every host and actual model answer quality remain unverified. One final credential-bearing ZIP remains at `reports/private/packages/margin-agent-local-2026-11-16.zip`; superseded task-created copies were removed. See [portable setup and evaluation logging](portable-agent-bundle.md).

### Pre-MCP agent interface: 16 November 2026

Added the `margin-agent` JSON CLI over the existing loopback HTTP backend, repo-maintained `margin-research` Codex skill/launcher and installer. The functions remain reusable modules in one `margin-research` Python package; the browser is optional. Separate CLI invocations share the server's plans, ledger, provider lifecycle and retained results. Catalog discovery returns compact summaries or full selected schemas; company planning schemas/defaults are now discoverable. Runs require the preview's backend identity and an explicit idempotency key. Mode mismatch, expired results and uncertain transport errors never silently retry, reset allowances or fetch replacements. The launcher strips provider-key environment variables; the action nonce is never forwarded to the agent.

Added separate optional `research/pilot.py`: private task/observation/final-answer recording, retention review date, 0700/0600 permissions, a POSIX session lock, bounded logs and backend pinning. Normal product/installed-skill use stays transient. Successful previews preserve validated arguments; raw CLI/rejected inputs are excluded. Recording failures preserve the real command result and report exit 3 without retry. This is not full host-message capture, exact request replay, frozen snapshots, independent filing gold, model runner or grading. No live pilot recording was initialized or retained. Citation verification/sentiment and downstream Margin MCP remain deferred.

The new schema path exposed a sanitizer failure on JSON Schema's list-valued `type`; fixed without weakening binary/resource rejection. Malformed retained-source IDs now validate before lookup rather than raising an internal error.

Validation: **111 offline tests passed**, including shared allowance exhaustion across command invocations, reuse/idempotency, DCF reference, catalog schemas, mode/backend changes, expired results, transport uncertainty, rejected-input privacy and recorder retention/finish behavior. Ruff lint/format passed over `src tests scripts research skills`. The supplied Skill Creator validator passed; its missing PyYAML dependency was installed only under a temporary directory, not added to project dependencies. The process acceptance script passed sixteen separate launcher commands against one fresh fictional backend, including recorded final answer and temporary-session cleanup; zero provider calls. The skill is installed at `/Users/rishit/.codex/skills/margin-research` with no recording configured. A neutral empty workspace was created outside the repo for the next fresh-chat pilot.

A separate real CLI-process check made **one BharatStock `GET /v1/stocks/RELIANCE/financials` request, zero Drishti calls and no provider retry**, under a hard one-request process cap. Returned annual consolidated facts included 24 observations, latest period `2026-03-31`. Margin matched independent Decimal arithmetic over the returned profit/revenue facts. Company cash-flow, growth and CAGR succeeded using that retained response with zero further data calls. Duplicate submissions returned the original run. INR was explicitly caller-declared for arithmetic; source units and original filing accuracy were not verified. Provider payloads stayed in process memory, recording was disabled, and the temporary backend was stopped. No new subscription/purchase, external model call, fresh-chat model evaluation, commit or push occurred.

Packaging: rebuilt the wheel with the agent modules/entry point and refreshed the editable install without dependency changes. Installed the wheel into an isolated target and verified imports resolve there, eleven calculation functions and both executable entry points using the existing dependencies. The installed global skill matches repo source and its launcher help works. Full clean dependency-resolution/cross-platform validation and an actual model choosing/using the tools remain separate pending gates. See [agent interface](agent-interface.md) for setup, commands, recorder limits and fresh-chat instructions.

### Unified workbench flow: 15 November 2026

Reproduced stale SYNTHA facts remaining after a ticker change, independent company/fact unit controls, lost visible results and inconsistent immediate-versus-preview execution. Replaced the stacked workflow with Financial functions / Retrieve data / DCF & advanced tasks sharing one preview/Run path. Snapshot/search/detail and explicit calculations now preview too. Retrieve data selects only Snapshot by default; event-provider setup and limits are collapsible.

One listing-scoped declared scale feeds company calculations and retained facts. Missing units are caught before calculation dispatch in the UI; the lower-level API still supports explicit incomplete results. Company edits clear active facts/results/preview; schema-backed inputs stay editable before preview and lock during runs. Draft revisions discard late preview responses. Loading facts no longer overwrites a calculation. Compatible fact pairs are suggested but remain editable. Results show listing, period/basis, unit declaration and readable metric labels without duplicate warnings.

Added local `GET /api/runs` for at most twenty safe control summaries. Recent runs restores older retained cards without fetching; reload restores the last compatible viewed run plus non-sensitive listing/task/unit preferences. Expired outputs remain unavailable. History preserves company labels even when payloads have been evicted. No corpus/cache or upstream retry was introduced.

Validation: **95 offline tests passed**, including history scope after payload eviction without extra calls or payload leakage. Expanded Chrome acceptance covers prerequisites before spend, preview invalidation, duplicate submission, reuse, shared units/fact suggestions, history/reload, company switches, forbidden missing-source fetch, expired-source UI, delayed stale previews, DCF/domain errors, retrieval/detail previews, escaping/redaction, and all three mobile layouts. Browser failure data are explicitly fictional software tests.

A separate live browser pass made **one BharatStock annual-financials request and zero Drishti calls**. RELIANCE/NSE returned 24 facts. The margin was checked against local decimal arithmetic; nine repeated cash-flow/growth/CAGR runs, further retained-only rechecks, history, company switches, reload and mobile geometry caused no additional provider requests. INR was caller-declared; source units/filings remain unverified. Direct in-app browser inspection also confirmed the live preview with zero provider operations and the resulting labelled margin card. Final checks also passed Ruff lint/format, JS syntax, all 77 HTML/JS target IDs, 160 local document paths, whitespace validation and credential scanning of 63 non-ignored files. Temporary browser/tab and test servers were closed. No new paid keys, model calls, purchase, commit or push.


### Financial workflow repair and company operations: 15 November 2026

Successful financial retrieval now automatically populates fact selectors; a visible retained-source picker restores sources after reload. Unit changes refresh facts locally. Concurrent preparation is deduplicated, stale loads cannot overwrite later selections, and preparation errors are visible. Asset URLs changed to help load the updated UI; an older Python server still requires restart.

Added five company financial workflows: margins, cash-flow metrics, period growth, annual endpoint CAGR and TTM. They resolve retained financials or preview one missing financials request, followed by a local calculation. They share ordinary immutable plans, runs, idempotency, budgets, bounded result retention and result cards. All eleven explicit-input calculations can also use this result-card path. Missing context remains incomplete; there is no automatic forecast/DCF completion.

Browser testing exposed and fixed an eviction bug: a new derived run could evict its own source when the five-run buffer filled. Active company runs now protect referenced source runs, without extending TTL or memory limits. A reduced two-run retention regression covers this case and repeated standalone calculations; eviction now prefers derived cards before financial source runs. Failed calculations now display safe incomplete/error output rather than a blank inspector.

Two real BharatStock annual-financials attempts were made in this repair session, with zero Drishti HTTP/data calls. The first exposed the eviction failure during repeated calculations; the second verified the fix. Each temporary server was capped at one request; restarting did not replenish account quota. A real Chrome walkthrough using RELIANCE/NSE loaded 24 facts and passed company margin, selected-fact margin, cash-flow, growth and CAGR result cards, retained reuse, reload, mobile layout and no JS errors/external browser requests. INR was explicitly caller-declared for arithmetic testing; source units/filings remain unverified. TTM live success is not claimed because returned quarter starts/history remain insufficient. No raw provider payload was saved to the repo, purchase/commit/push performed, or Drishti refresh repeated.

Offline validation: 94 tests pass, including source reuse, idempotency, eviction protection, missing units, expired/mismatched sources and standard local-function HTTP results. The final Chrome regression passed against the updated fictional server, including retained company-function result cards, retrieval/DCF/restore and mobile behavior. Ruff lint/format, JS syntax, diff whitespace, 159 local document paths and credential scanning of 63 non-ignored files passed. Temporary test servers were stopped. See the financial-analysis guide for the updated manual flow and endpoints.


### Financial foundation and fresh-source checkpoint: 15 November 2026

Implemented `margin.analysis` and `margin.finance`: retained-result fact preparation; compatibility/unit conversion; period comparisons, margins, CFO/capex, CAGR and TTM; explicit-input FCFF/DCF, bounded sensitivity and scenarios. The provider registry remains thirteen operations; `/api/analysis/functions` exposes eleven local schemas and fact preparation has its own retained-result route. New routes inherit nonce/origin/body controls. Calculations fetch no provider data, and unknown/contradictory context remains incomplete rather than being invented.

Receipts/result contract is 1.1: full sanitized supplied/effective arguments, request/retrieval timestamps and requested scope; provider-side defaults/relative dates remain unknown, not frozen replay. Injected clocks support deterministic tests. Source classification excludes decorative images while retaining explicit source-page images, without verifying claims. Actual news title/earnings ID variants and detail `data.earnings_table` are handled; print styles wrap tables. Workbench controls prepare retained facts, compare selected observations, accept unfilled explicit DCF inputs, show values/intermediates and expose advanced JSON/schema inspection.

Fresh real source calls: three BharatStock REST requests (snapshot, quarterly and annual financials), and 22 cumulative Drishti HTTP requests including schema review/lifecycle/usage and three SDK data calls. Measured Drishti debit six credits, balance 975 → 969. New native schemas initially triggered the guard; four native and seven selected nested inputs were reviewed/refreshed before data execution. One selected announcements filter was removed by the provider. All details/limits are in the [source checkpoint](research/mcp-provider-feasibility.md#fresh-payload-inspection-15-november-2026); the untested eighteen-operation remainder was not refreshed or enabled.

Validation: 91 offline tests pass, Ruff lint/format and JS syntax pass. Independent calculation examples include a constant-cash-flow perpetuity, an explicit enterprise/equity/share bridge, CAGR and four-quarter totals; tests reject missing/mixed context, double-adjustment risks, stub periods, invalid/nonfinite inputs and excessive bounds. HTTP tests show preparation/calculation does not increase provider counters. Real API annual observations also passed a local CFO/capex arithmetic check with a declared unit, without independent filing verification. Chrome browser acceptance passed using clearly fictional fixtures, separately from real source access: retained fact preparation, comparisons and the explicit DCF form, readable values, no duplicate fetch on restore, no provider dispatch from calculations, no external page requests/JS errors and mobile layout. The temporary test server was stopped. Advait's implementation is not yet supplied; the current pure calculator provides a stable integration point.

No raw provider responses, account payloads or source PDFs were added to Git. No purchase, external model call, commit or push occurred. Research capture/replay, citation verification and sentiment protocols remain outside this implementation. Source-backed forecasting/valuation input completeness and wider company/sector coverage remain open.

Handoff checks: local wheel built successfully, installed to an isolated target directory and imported there using the existing dependency environment; eleven calculation functions, the DCF reference, schema resource and workbench assets passed. This is not a clean dependency-resolution or cross-platform/host test. Scanned all 61 tracked/new non-ignored files and wheel contents for supplied credentials/encoded variants; no matches or private-data members. Native/nested JSON schemas are structurally valid. All 17 Markdown files / 161 local links and anchors, JS syntax and `git diff --check` passed. Temporary live-probe scripts/metadata were removed; no test workbench remains running.

### Product/research boundary planning: 15 November 2026

Revised the active plan and contributor/context/design pointers per user direction: prioritize product retrieval/fact/financial/DCF integration and later packaging; defer citation verification and sentiment protocols; keep the professor's capture/replay/task/gold/agent proposal in a separate optional harness consuming public product interfaces. Independent answer keys/evaluation are an explicit scientific requirement; separating the harness from default product usage is our architecture decision, not a claim that the note demanded an unrelated product.

Inspected current package/contracts and official Python packaging plus versioned MCP tools/transport references for the plan. No runtime implementation, dependency change, provider/model call, new test execution, purchase, commit or push occurred. Historical code/source evidence and the 9 November push remain unchanged. All 16 Markdown files and 149 local links/anchors passed; `git diff --check` passed. No runtime suite was rerun for these documentation-only edits.

### Documentation handoff: 9 November 2026

Prepared the documentation-only commit covering the earlier finance/protocol proposal, research review, revised plan, preserved professor progress summary and updated contributor/navigation/context documents. Added [HANDOFF.md](../HANDOFF.md), a 532-word repo map and update summary, with the professor's new notes explicitly separated from our proposed response and existing product backlog. Runtime behavior is unchanged; no provider/model calls or new financial/research capabilities are claimed.

All 16 Markdown files and 147 local links/anchors passed; `git diff --check` passed. No runtime test rerun was needed for these documentation-only edits; the last executable audit remains the 7 November checkpoint below. Private credentials and data are excluded from the commit.

### Research-direction audit: 7 November 2026

Reviewed the delivered core/provider/policy/evidence/workbench boundaries against the professor's supplied 2 November note and the earlier finance/protocol plan. Ruff lint and format checks passed; **50 offline tests passed in 1.04 seconds**. No authenticated provider/model request, runtime implementation, dependency installation, purchase, provider outreach, commit or push occurred. Public provider terms/pricing were inspected without credentials; findings and links are in the [complete review](design/research-environment-review.md).

Confirmed gaps: payloads/receipts are not durable; selected receipt fields omit full nested arguments; no immutable environment, replay request identity, independent task/gold records, agent runner or trajectory annotation exists. Generic warnings are not independent financial adjudication; provider-shaped results are not a general normalization or corporate-action join. Software tests do not establish task feasibility, financial accuracy or current account permissions/cost.

The revised [plan](plan.md) prioritizes permissioned capture/replay, fixed independently verified tasks and genuine agent runs. DCF, citation/sentiment protocols and downstream MCP remain planned product extensions. The proposed persistent research snapshot is distinct from the existing transient live workflow and is not implemented or authorized for collection/publication by this documentation change. Previous diagnostic retention dates are not extended.

Documentation validation: 15 Markdown files and 124 local links/anchors passed; `git diff --check` passed. Changes are documentation only. The historical professor-facing progress summary remains 931 words and was not rewritten for the new scope.

### Public endpoint checkpoint

A bounded sequence of 14 HTTPS requests was run without credentials or paid-data tool calls. TLS verification stayed enabled; each request had a 20-second timeout and 2 MiB response cap. No automatic retries, mutation jobs, authenticated requests or account credits were involved.

- BharatStock plans/status and both OpenAPI schemas: HTTP 200. The schemas have 35 and 30 distinct path entries respectively, not that many MCP tools; both declare OpenAPI 3.1.0.
- BharatStock quote/financials and Drishti news/announcements/concalls/account usage: HTTP 401 without keys, as expected.
- BharatStock MCP initialize: HTTP 200, version `0.1.0`, protocol `2025-06-18`; initialized notification HTTP 202; tools/list HTTP 401.
- Drishti MCP initialize: HTTP 401 without a key.

The exact methods/URLs/results and schema hashes are recorded in [provider research](research/mcp-provider-feasibility.md). Temporary raw receipts remain outside Git. This validates reachability/public contracts and authentication barriers, **not financial-data quality, paid entitlement, hosted tool schemas, effective limits or charges**.

### Repository checks

Branch preservation was verified before removing tracked legacy files. Documentation checks cover local links/anchors, stale legacy setup commands and `git diff --check`. The historical documentation-only checkpoints below predate the current runtime suite. The retired September tests do not establish current correctness. Current build/UI evidence is recorded in the final checkpoint; no downstream model-host demonstration has occurred.

### Authenticated trial checkpoint

Executed the authorized bounded RELIANCE/TCS pass on 8 October 2026 using private one-shot diagnostics. No gateway/package, committed test client or financial database was introduced. Full details, exact endpoints, dates, counts, source limitations and catalog hash are in [trial results](research/mcp-provider-feasibility.md#authenticated-trial-results-8-october-2026).

- BharatStock: 12 REST requests, all 200; two snapshots, six quarterly/four annual financial rows, forty EOD price rows, two ratio objects and four ownership rows. Identity/ISIN agrees with Drishti. Known Free native-MCP gate was not probed.
- Drishti: 25 HTTP requests (16 REST, 9 MCP), all 200/202; two metadata rows and one news/announcement/earnings summary per company. Balance 1,000 → 992, debit 8, reserved 0. Data REST limits 10/min and 1,000/day; account diagnostics 60/min and 10,000/day.
- Official MCP Python SDK 2.2.0 initialized Drishti 3.3.1, protocol 2025-11-25. The first session hit a local camelCase accessor error after a successful handshake. Corrected to snake_case and made one bounded repair session; initial request cap 20 explicitly revised to 26, unchanged credit ceiling 30. Actual catalog is **four routing tools**, not the flat public operation list. Complete one-page catalog and clean session termination succeeded; no MCP market-data operation was called.
- Four Reliance FY25 values match its downloaded/visually inspected issuer statement. TCS original downloads returned 403; indexed corroboration is weaker evidence. Numeric/financial correctness is not established for every returned cell. Financial fields lack unit/source labels; market-cap scales differ by JSON path. Quarterly cash flows are null; TCS Drishti earnings is a quarter newer than its numerical BharatStock response.
- Eighteen offline receipt checks passed for identity, dates/basis/field presence, OHLC/adjustment and P/E arithmetic, the scale finding, four issuer-value matches and accounting. This is a source evaluation, not a current Margin runtime suite or real-host demonstration.

Private receipts, temporary scripts and the issuer PDF are ignored with restricted permissions; review/delete trial output by 22 October, manually. The key file is separately retained locally. A concurrent ledger-write issue was repaired from saved receipts and corrected; future repeatable probes must use serialized/atomic recording. No commit or push was made in this pass.

Documentation validation passed for nine Markdown files and forty-three local links/anchors, plus `git diff --check`. Exact-key scanning of tracked files passed; the private credential, ledger and account response paths are ignored and absent from the Git index. No deprecated runtime command was added. Current changes remain local/uncommitted on `main`.

## Remaining gates

Follow-up surface comparison on 8 October used public guides and cached public schemas/package source only, with zero additional authenticated calls or credits. The [capability/derivation map](research/mcp-provider-feasibility.md#capability-comparison-and-research-derived-from-the-pairing) records Drishti shared/MCP-specific/REST support differences and BharatStock wrapper contracts. It also corrects filing dates to ingestion dates and documents REST announcement attachment omission. This extends research and the proposed design, not delivered runtime behavior. Follow-up documentation checks passed for nine Markdown files, forty-seven local links/anchors and `git diff --check`.

### Selected operation checkpoint: 9 October 2026

The authorized second pass completed in 14 Drishti HTTP requests (6 REST, 8 MCP), within its 16-request/10-credit bounds. Discovery had zero observed debit; MCP RELIANCE `q1_27` detailed earnings and its matching REST detail each cost three credits. Final balance 986; reserved zero. No BharatStock calls, retries, extra discovery pages or transcript-search execution occurred.

Live discovery returned twenty compact underlying-operation summaries and `has_more=true`, so the capability map remains partial. Two schemas (`search_concalls`, `get_earnings_filing`) were inspected; one schema-validated earnings operation executed successfully. Native routing catalog/version unchanged. Shared earnings-table values matched across 97 leaf fields, while MCP added raw fields and source locators. A consolidated revenue discrepancy is present: normalized ₹298,621 crore versus raw ₹311,850 crore, with the saved BharatStock row matching the latter. This is not independently verified against the Q1 issuer document.

MCP exposes PDF/page locators for this record, but they embed the supplied API key in query parameters; forwarding must sanitize credentials. Neither those URLs nor the signed attachment were fetched, and citation resolution/claim verification remains untested. Seventeen offline receipt checks passed, covering accounting, schema bounds, identity, shared values, source differences and the measured conflict. See [full evidence and partial map](research/mcp-provider-feasibility.md#authenticated-operation-discovery-and-rest-comparison-9-october-2026). Raw outputs/private diagnostics are ignored with restricted permissions and manual deletion review due 23 October. No gateway/runtime package, new committed test client, commit or push was introduced.

Repository validation: nine Markdown files / fifty-four local links and anchors passed; `git diff --check` passed; exact-key scanning of tracked working files found no keys, and private paths are absent from the index. A compilation-created private `__pycache__` directory initially had mode 0755; it was corrected to 0700 and the recursive permissions check then passed. Raw response files remained restricted.

### Function reference checkpoint: 9 October 2026

The requested metadata audit completed in 23 HTTP requests (6 REST usage checks, 17 MCP messages across two intentional SDK sessions), zero credits, balance unchanged at 986. All 25 confirmed underlying operations now have live input schemas, covering 22 market functions and three docs/workflow helpers. The four-tool native catalog remains unchanged. Both data/docs guidance modes were inspected; there was no `execute_tool` or financial retrieval in this pass. Eighteen offline source/contract checks passed after restricting an import-created private cache directory. Raw receipts remain ignored/private; deletion review due 23 October.

Delivered documentation: [human function reference](reference/drishti-functions.md) and [derived JSON contract](reference/drishti-functions.json), with native/nested inputs, defaults, REST relationships, cost/evidence status and all thirty public REST path entries. Provider schema descriptions/examples are omitted from JSON; validation keywords are preserved. This is not a runtime registry or a guarantee that discovery finds every hidden operation. Only earlier earnings execution is observed; other operation output schemas, access, costs and data quality remain untested. Exact evidence/hash/accounting is in the [dated checkpoint](research/mcp-provider-feasibility.md#drishti-function-mapping-checkpoint-9-october-2026).

Function-reference repository checks passed: ten Markdown files / sixty-nine local links and anchors; derived JSON parsed with all observed schemas structurally valid; `git diff --check`; exact-key scanning of tracked and new non-ignored files; private index exclusion and recursive permissions. Current changes are local/uncommitted. The reference was queued for display in the app; no host/model financial demonstration occurred.

The source-access gate remains partially satisfied. Broader coverage, other native-operation access/rates/billing, citation resolution and original-source review of the revenue discrepancy remain open. BharatStock native catalog/data tests would need eligible access, but are no longer a Stage 1 dependency; direct REST is the selected path. There is no delivered aggregate server or model-host demonstration.

### Architecture refinement checkpoint: 9 October 2026

Updated the architecture, milestone plan, prospective source protocol and contributor handoff using the measured findings. Proposed a small native/nested profile, dual registries, typed-selector admission, atomic session allowances, mandatory output/error sanitization, visible caveats and separate source-resolution/claim-verification stages. Offline construction is no longer gated on buying BharatStock access or completing every data-quality check; the then-proposed two-native-MCP live acceptance still required eligible access. That transport choice is superseded by the correction below.

The locally available official SDK 2.2.0 server source/API was inspected: low-level constructor callbacks `on_list_tools` / `on_call_tool` are available; old v1 decorators are not the build reference. This is API inspection, not an implemented server or successful downstream transport test. No new dependencies were installed, provider calls made, credits spent, purchase, commit or push performed during this planning update. The last observed Drishti balance remains 986. Proposed future ceilings are not executed tests or a live account quota guarantee.

Planning-update validation passed: ten Markdown files / seventy-eight local links and anchors; function-reference JSON parsed; credential-candidate scanning of all thirteen tracked/new non-ignored files passed; private credential/results paths remain outside the index; `git diff --check` passed. One renamed trial-section link was corrected before the successful rerun. No gateway/runtime suite was run or claimed. Changes remain local/uncommitted.

### Transport correction: 9 October 2026

The prior architecture refinement retained BharatStock MCP even though the authenticated tests used REST and package/reference inspection established that its MCP wraps the same data endpoints. The user flagged that inconsistency. Corrected current architecture, tool contracts, test gates, subscription advice and contributor handoff to **BharatStock REST + Drishti MCP**, exposed through one Margin MCP. Native BharatStock MCP/Developer access is no longer a release dependency. Historical source-test counts and findings are unchanged.

BharatStock now has proposed local MCP schemas mapped to six REST routes, a small documented `provider_payload` result wrapper preserving inner REST JSON/pagination, direct HTTP request accounting and no automatic retries/redirects. Synthetic tests must exercise REST and MCP upstreams separately. Existing Free/trial keys can support bounded live acceptance where entitled; later Starter/Starter is the published ₹2,600/month starting recommendation plus applicable tax/charges. Developer remains an optional higher-quota/native-MCP choice.

Public official BharatStock reference/pricing and Drishti pricing were reviewed for the correction. No authenticated provider call, credit spend, implementation, purchase, commit or push occurred. Last observed Drishti balance remains 986; current remaining allowance was not polled. The financial conflict, citation-key sanitization, untested Drishti operations and wider evidence gates remain unresolved.

Transport-correction validation passed: ten Markdown files / eighty local links and anchors; JSON reference parsing; credential scan of thirteen tracked/new non-ignored files; private index exclusion; checks for stale two-MCP requirements in active guidance; `git diff --check`. No runtime tests were run; changes remain local/uncommitted.

### Final build baseline: 9 October 2026

Evaluated the complete current design against observed REST/MCP contracts, SDK source and public primary references. Finalized the one-process Python stdio gateway over BharatStock REST + Drishti MCP, with approved exposed/nested contracts, bounded dispatch, independent adapters, mandatory metadata/result/error sanitization, visible caveats and common safe receipts/citation records. Added startup/refresh/shutdown rules and explicit first-release/later-work boundaries. Local REST results use a documented `provider_payload` structured object and matching serialized JSON text; Drishti retains native results. Price histories have a separate one-company 300-row bound so the twelve-company one-year evaluation is not silently limited by the 20-item narrative cap. In-memory budget restart limitations and known-path-only context checking are explicit.

The official tools specification/SDK references and provider docs/pricing were reviewed publicly; local SDK server callbacks were inspected without running a server. No authenticated source call, financial retrieval, new credit spend, runtime implementation, dependency install, purchase, commit or push occurred. Last observed Drishti balance remains 986; no new balance query was made. Existing source-quality and operation-entitlement gaps remain open.

Final-baseline documentation validation passed: ten Markdown files / eighty local links and anchors; JSON reference counts (25 operations, four native tools); credential scan of thirteen tracked/new non-ignored files; private index exclusion; active transport consistency; `git diff --check`. No gateway runtime tests were run or claimed. Architecture/plan/context updates remain local/uncommitted.

### Core-first/workbench planning checkpoint: 20 October 2026

The user changed delivery order: implement/test core functionality with a temporary display interface before exposing Margin as an MCP. Added the active core/workbench architecture, revised milestones and updated contributor/README/context/test guidance. The 9 October downstream MCP design is retained as a deferred adapter, not the active first implementation target. BharatStock REST and Drishti MCP remain the provider choices; only our server packaging is delayed.

Recommended a framework-independent Python service layer plus a thin local FastAPI/static HTML/JS workbench. Plans/runs, shared backend budgets, idempotent submission, provider lifecycle, sanitized results, presentation-only mapping and evidence/status boundaries are specified. Default mode is synthetic; live operations remain explicitly budgeted. No source code/package/UI, server, dependency installation, authenticated request, account check, credit spend, purchase, commit or push was introduced. Last observed balance remains 986 on 9 October, not a current balance. No runtime test or live/manual workbench demonstration occurred.

Public FastAPI lifespan/static-file docs and Streamlit forms/caching guidance were inspected to evaluate the interface approach. The recommendation is an engineering choice, not a benchmark result. Existing financial conflict, original-source/citation access, broader operation entitlements and source-quality gates remain open. No private output retention was extended or cleanup job run.

Core/workbench planning validation passed: eleven Markdown files / ninety-one local links and anchors; JSON reference inventory; credential scan of fourteen tracked/new non-ignored files; private index exclusion; active core-first/deferred-MCP guidance consistency; `git diff --check`. No tracked/new runtime code was introduced and no application/runtime tests were run. Changes remain local/uncommitted.

## First core/workbench build checkpoint

Delivered `margin-research` 0.1.0 as an installable Python package with optional workbench/development dependencies. The first build implements the active core-first architecture; it does not finish Phase 1's live/source gate.

- **Core:** strict reviewed registry, local plan previews, explicit 1–8-operation runs, immutable stored plans, idempotent submission, independent provider failures, timeout/cancellation uncertainty, shared process allowances and bounded expiring sanitized results. The core imports no FastAPI or UI modules.
- **Providers:** six exact BharatStock REST route mappings and seven Drishti nested operations through its four native wrappers. Drishti uses one SDK-owner task, explicit connection/metadata refresh, schema-hash checks, freshness/quarantine and counted protocol/implicit-catalog requests. Automatic retries, redirects, resumptions, extra pages and generic execution are blocked. SDK 2.2.0 uses `httpx2` 2.13.1; the separate REST adapter uses `httpx` 0.28.1.
- **Evidence:** known-key and credential-field/encoded-URL/text sanitization, safe unresolved source locators, preserved nulls/periods/bases, reviewed-path context warnings and the measured revenue-conflict caveat. No original-document resolver or claim verifier is delivered.
- **Workbench:** loopback FastAPI/static HTML/CSS/JS, synthetic/live labels, directory/identity actions, financial tables, EOD line, event cards, selected earnings detail, operation trace and sanitized JSON/receipt inspector. Shared backend budgets and idempotency survive page refresh. Keys are backend environment variables only; neither `.env` nor the private key file is auto-loaded.
- **Retention:** at most five payload runs, 20 MiB total, 30-minute TTL, 2 MiB operation-result cap; at most 200 control records. Eviction does not discard idempotency intent or automatically refetch. All state is process-local and cleared on shutdown; restarts are not account-wide budget resets.

Validation: Ruff lint/format passed; **47 pytest checks passed** with a default socket block. These include exact REST requests and streamed size/error bounds, the real MCP SDK against an in-process synthetic MCP upstream, schema drift/freshness, admission, accounting/cancellation, sanitization, HTTP integration and duplicate/reload behavior. No actual provider requests were made by these tests. Initial MCP-fixture failures were traced to the fixture Host lacking a port under SDK DNS-rebinding checks; adding an explicit local test port fixed both without weakening production guards.

Headless system Chrome acceptance passed on the running synthetic workbench: local assets only, no preview dispatch, duplicate Run deduplication, reload/restore without refetch, numeric/events/price chart, staged earnings detail with redacted citation/conflict, escaped HTML-like provider text, mobile overflow check and no JavaScript exceptions. Desktop/mobile screenshots were inspected locally. The browser's first wait-expression implementation conflicted with the strict CSP; the automation was changed to function callbacks, retaining the app's CSP. Synthetic browser counters are simulated, not actual requests/credits.

Dependencies were installed into the local environment and `pip check` passed. Version constraints include only the current package's development dependency closure; they are a tested Python 3.12/macOS snapshot without hashes, not a cross-platform lock guarantee. Wheel and source archive built successfully with static assets and selected contracts included; private paths were excluded. A fresh temporary Python 3.12 environment installed the built source distribution with workbench/dev dependencies under the constraints. Installed-package imports, synthetic HTTP startup/assets, all 47 tests against installed code and `pip check` passed outside the checkout. Documentation checks passed for twelve Markdown files / 109 local links and anchors; exact credential-candidate scanning of tracked/new non-ignored paths, private-index exclusion and `git diff --check` passed. See the [workbench guide](workbench.md) for executable commands.

**No authenticated provider call, current account query, credit spend, purchase, commit or push occurred in this build.** The last observed 986-credit balance is still the historical 9 October snapshot. Newly implemented live paths, live output compatibility, broader entitlements/billing, source resolution and financial accuracy remain unverified. Search/actions and unexecuted Drishti shapes are held in live mode unless explicitly opted in for a bounded test; metadata presence never silently grants access.

### Manual live-mode setup: 21 October 2026

At the user's request, stopped the running synthetic preview and configured the local workbench in live mode using existing ignored credentials in process environment only. The session caps are four BharatStock HTTP attempts, 24 Drishti HTTP attempts and seven estimated credits; explicitly enabled reviewed news, announcements and earnings-discovery shapes for manual testing. No keys were written into source, chat, logs or shell arguments. The small manual sequence is in the workbench guide. No provider request, live success or actual credit debit is established by this setup; dashboard allowance checks and explicit user actions remain next.

### First user live run and display/configuration repair: 21 October 2026

User screenshots and a read-only local status/capability inspection confirm two successful live BharatStock operations (snapshot and quarterly financials). The local ledger shows two BharatStock HTTP attempts, seven Drishti lifecycle/metadata attempts, zero Drishti logical data calls and zero estimated data credits. Drishti connected and verified all seven selected nested schemas without drift; its five-minute metadata TTL had expired at inspection. The user’s `.env` had both credential fields but an empty `MARGIN_ENABLE_OPERATIONS`, matching the runtime's local held reasons. This is not an observed provider entitlement rejection or proof of entitlement for the uncalled data operations.

The financial table had a presentation defect: fixture-only `period_end`, `consolidated` and `profit_after_tax` columns were used instead of observed REST `period_end_date`, `consolidation_type` and `net_profit`. Corrected the view to use present reviewed REST fields, retaining fiscal year/quarter and null/zero semantics without aliases, unit conversion or payload changes. Unknown layouts fall back to supplied keys. Tables now scroll horizontally rather than splitting headers/numbers across lines. Added visible explanations of local operation holds. Fictional offline rows now use the observed contract's field names; no private financial payloads were copied into fixtures.

Updated only the three selected nonsecret live-test opt-ins in the user’s ignored `.env`, preserving credential values and existing budget settings. The user-owned process was not restarted and its retained results/counters were not reset. The user must reload the environment and restart before those settings affect the server. No new provider call was initiated by this diagnosis/repair; existing local results/status and historical field-name evidence were reused. The screenshots' retrieval timestamp is not the quote's trade date; three returned financial rows do not guarantee the requested four slots or broader history.

Validation: **48 pytest checks passed**, Ruff lint/format, JS syntax and `git diff --check` passed. A Node-based optional regression executes the actual view functions against an in-memory DOM, checking observed financial keys, zero/null fidelity, unknown-shape fallback and visible local-held explanations, without browser or provider traffic. The optional browser smoke script gained financial-key assertions but was not rerun in this repair. A native browser-read attempt timed out; no live browser-render verification is claimed for the repair. No purchase, commit or push occurred.

### Connect feedback and duplicate-attempt repair: 21 October 2026

Local cached status showed the user's Connect action was active (`connecting`), with Drishti initiated HTTP counters progressing through 10–16. It subsequently reached `connected` with all seven schemas verified/fresh at 23 requests, zero Drishti logical data calls and zero estimated data credits. The original UI only refreshed status after the awaited POST and offered no pending/success feedback or repeated-click protection. Existing `not_connected` run cards are historical results and are not automatically retried after connection.

Implemented visible pending/ready/expired/error feedback, duplicate-click blocking, local progress polling and idle status polling for other tabs. Clicking Connect with fresh metadata only checks local state. Drishti plans check readiness before run submission, preventing known-not-ready mixed plans from making unrelated provider calls first. Added backend shared connection tasks with shielded waiters, fresh-metadata reuse and shutdown cleanup. This preserves the SDK owner's task/context boundary and makes no automatic metadata/data retry. Static fixes are served immediately; Python changes apply at the user's next normal restart, without forcing a restart/reset of the currently working process.

Validation: **50 pytest checks passed**, Ruff lint/format, JS syntax and `git diff --check` passed. Added regressions for concurrent/cancelled connection waiters, shared failure handling, UI pending/success/error feedback, duplicate-click suppression, fresh local reuse and preflight blocking before `/api/runs`. Read-only local HTTP checks confirm updated HTML/JS assets are served and existing metadata is fresh; no new GUI/browser-render or Drishti data-execution success is claimed. No provider connection/data call was initiated by the agent in this repair; counters reflect the user's existing actions. No purchase, commit or push occurred.

### Combined live-run PDF review: 21 October 2026

Reviewed the user-supplied seven-page browser export, including rendered pages and extracted text. It shows one completed eight-operation RELIANCE overview: five BharatStock calls (snapshot, quarterly financials, annual financials, ratios, EOD history) and three Drishti calls (news, announcements, earnings discovery), all marked success with live provider receipts. This is seven distinct registry operations because financials is called twice. The displayed run includes three quarterly rows, two annual rows, 61 retained EOD rows (20 shown), two news rows, two announcements and two earnings summaries. Requested bounds do not establish wider completeness. The PDF's financial dates/basis columns now use the corrected observed REST field names.

At export, process totals were 10/20 BharatStock HTTP attempts, 29/30 Drishti HTTP attempts and four completed estimated Drishti credits. The totals include prior actions; they are not the eight-call run's exact HTTP accounting or a measured account debit. The four-credit estimate is consistent with news 1 + summary announcements 1 + earnings discovery 2. At 29/30, the runtime's two-slot cleanup admission rule blocks further Drishti data calls; restarting does not reset actual provider quotas. Connected with expired metadata at print time does not invalidate earlier successful results. Neither standard local port was listening when this review checked status; the PDF is the evidence for this run.

#### Implemented operation inventory

These are thirteen core operations, not thirteen tools already exposed by a Margin MCP server. Downstream MCP packaging is still deferred.

| Provider | Core operation | Current evidence / interface |
| --- | --- | --- |
| BharatStock | `search_stocks` | Implemented REST mapping and search UI; held pending selected live test |
| BharatStock | `get_stock_quote` | Live success in the user run; snapshot UI |
| BharatStock | `get_stock_fundamentals` | Live success in the user run; ratios UI |
| BharatStock | `get_financials` | Quarterly and annual live success in the user run; table UI |
| BharatStock | `get_stock_prices` | Live success, 61 retained EOD rows in export; chart/table UI |
| BharatStock | `get_corporate_actions` | Implemented mapping/module; held pending selected live test |
| Drishti | `resolve_symbols` | Implemented approved core execution path; offline checks, no dedicated UI action/live data proof |
| Drishti | `get_symbols` | Implemented approved core execution path; offline checks, no dedicated UI action/live MCP data proof |
| Drishti | `get_news` | Live execution success in export; actual fields fall back to a generic table |
| Drishti | `get_announcements` | Live execution success in export; event cards and sanitized locators |
| Drishti | `get_announcement_categories` | Implemented core path; no dedicated category UI/live data proof |
| Drishti | `list_earnings` | Live execution success in export; actual records fall back to a generic table |
| Drishti | `get_earnings_filing` | Implemented core/detail action; historical 9 October upstream success, but current real-list detail selection remains incomplete |

The upstream Drishti catalog still has four native wrappers. Runtime data flows through `execute_tool`; connection checks `tools/list` and calls `describe_tools`. `read_me` and `search_tools` are known/validated catalog contracts, not currently exposed Margin operations or routine runtime calls. Eighteen of the 25 documented nested Drishti functions are not in the first-slice registry.

#### Review findings and next work

Retrieval success is established for this selected run; the presentation is not complete. News records use fields such as `title`/`specific_title` rather than the fixture's `headline`. The news and real earnings-list rows therefore reach a generic nine-column table; earnings detail is not selectable in the export. Fix reviewed title/record-ID/quarter presentation and the detail action using saved or newly permitted bounded evidence, without guessing selectors. Provider/output-contract tests need these actual shape variants while committed values remain fictional.

The PDF clips financial and price columns and visibly overlaps long news/earnings cells. On-screen horizontal scrolling is not adequate print support. Add print-specific wrapping, sizing and page-break rules; a browser print currently includes only the displayed 20 price rows and collapsed payload inspectors, not a full data export. Large metric values also need a readable representation that preserves original values and explicit unit confidence.

Citation extraction currently treats every URL as a potential source, including company logos. Separate source documents/news articles, page locators, protected attachments and decorative images; keep authorized-resolution labels and do not equate sanitized locators with verified citations. Original-document resolution and claim/page verification are still unimplemented.

Priorities: repair actual result rendering/detail selection and print layout; improve remaining-request/metadata feedback and measure actual credit deltas under a new bounded plan; selectively validate held operations and TCS without re-running the full overview; then extend semantic news/filing/concall search and later add the downstream MCP adapter. Comparisons, broad investor sentiment, public multiuser hosting and a persistent financial corpus are not delivered by this workbench.

No provider request, purchase, runtime change, new test execution, commit or push was made during this PDF review. The PDF and temporary renderings were not added to the repo. Exact supplied-credential scanning of extracted text found no matches; this is not a general proof that every URL is safe or a verification of underlying claims. The last executable code checkpoint remains 50 passing tests; it does not cover all the newly discovered real-shape/printing gaps.
