# Financial functions, research protocols and evidence verification

**Detailed implementation proposal — 29 October 2026. Planning only.**

**7 November priority update:** retain these contracts as the product backlog. The [research-environment review](research-environment-review.md) and [delivery plan](../plan.md) supersede this document's first-release sequencing: capture/replay, fixed filing-grounded tasks and actual agent trajectories come first. General DCF, sentiment, the full host-LLM citation round trip and downstream MCP are not gates for that research release. The transient live workflow remains; a separately permissioned bounded research snapshot is a proposed exception to the earlier no-persistence boundary. Protocols/helpers supplied to agents must be explicit versioned experimental conditions. No capability below has become implemented through this planning update.

This document specifies proposed extensions to the existing core and workbench. Function names are proposed interfaces, not claims that they exist. It complements the [core architecture](core-workbench.md); [implementation status](../implementation.md) remains authoritative for delivered behavior. The [delivery plan](../plan.md) owns milestones.

## 1. Product boundary and first release

Retain Python, BharatStock REST, Drishti MCP and the shared core. Finish/test the core through the temporary browser interface before exposing the new functions through Margin MCP. The user's harness supplies the LLM; Margin does not need its own model subscription or autonomous agent service.

The first release should support four bounded workflows: a company financial review, quarterly-results comparison, explicit-assumption DCF valuation, and news/filing sentiment with claim-linked evidence. Use RELIANCE/TCS for continuity, then add a small, justified coverage panel. A successful one-company response is not market-wide validation.

Separate four responsibilities:

| Layer | Owns | Output |
| --- | --- | --- |
| Retrieval | Approved provider operations, identity, filters, page/window limits, cost and access | Sanitized provider-shaped records and receipts |
| Deterministic analysis | Arithmetic, compatibility checks, deduplication rules, schema/reference validation | Reproducible calculations with formulas, inputs and failures |
| Research protocols | Versioned procedures, required evidence, output schemas and stop conditions | A plan or task packet for a person/host LLM |
| Host LLM | Contextual extraction, passage interpretation, relevance and sentiment judgments, narrative synthesis | Structured assessments linked to supplied evidence |

Protocols guide agents; they cannot force an arbitrary host to follow instructions. Budgets, input constraints, evidence-ID validity and calculation eligibility must be enforced in core services. Ordinary prose generated outside Margin cannot be automatically certified as compliant.

## 2. Foundation: typed facts without discarding source payloads

Add a fact layer alongside existing provider payloads. Each fact needs an opaque ID, company identity (ISIN/exchange/symbol), metric definition, original field path/value, canonical value if conversion is supported, currency/scale, sign convention, period start/end, duration versus point-in-time classification, standalone/consolidated basis, retrieval/as-of times, source/record references and verification state. Unknowns remain explicit.

Every calculation result should include `function_version`, `input_fact_ids`, assumptions with origins, formula/convention, intermediate values, output unit, missing inputs, warnings and evidence references. Distinguish observed data, mathematical derivations, user assumptions and model-proposed assumptions. Structural validation of an assumption does not establish its financial reasonableness.

Use decimal-safe financial arithmetic and explicit rounding policies. Do not infer units from magnitude, treat missing values as zero, mix parent-attributable profit with group profit, silently combine standalone/consolidated statements, or equate filing ingestion time with publication time. Track fiscal calendars rather than assuming every company has the same year-end.

| Proposed service | Contract and failure behavior | Priority |
| --- | --- | --- |
| `research.get_capabilities` | Existing registry/status presented with availability, schema state, observed access, costs and held reasons; local-only | First release |
| `research.plan` | Task, identity, periods, permitted sources and allowances -> explicit operations, dependencies, estimates and missing prerequisites; no retrieval during planning | First release |
| `facts.prepare` | Provider record references + reviewed mapping version -> typed facts preserving original paths; unknown mappings stay unconverted | First release, internal initially |
| `facts.check_compatibility` | Fact IDs + requested calculation -> issuer/period/basis/unit/definition checks and exact missing inputs | First release |
| `facts.convert_units` | Explicit known source/target scale -> converted value with reversible trace; FX additionally requires a supplied, dated conversion rate | First release, internal initially |
| `facts.reconcile_candidates` | Competing fact IDs -> differences, restatement/definition questions and unresolved conflicts; never average conflicting accounting values | First release |
| `research.get_coverage` | Requested versus returned periods/rows, missing fields and publication/ingestion limitations | First release |

Persist only a minimal private operational spend/intent ledger if needed across restarts. It must not contain provider keys or financial-response archives. Distinguish local allowances, observed HTTP attempts, published credit estimates, measured account debits and host-model token usage. Include diagnostics, implicit catalogs and cleanup in request planning.

## 3. Deterministic financial functions

### 3.1 Financial review and comparisons

These are Python functions callable directly and through the workbench; expose only useful public operations through MCP later. Internal helpers do not each need a public tool.

| Function | Required inputs and output | Important guard |
| --- | --- | --- |
| `finance.compare_periods` | Compatible period facts -> absolute changes, percentage changes and explanations of missing comparisons | No ordinary percentage-growth headline for zero/negative baselines without a defined policy; retain absolute changes |
| `finance.calculate_cagr` | Positive endpoints and explicit elapsed years -> annualized growth | Reject nonpositive endpoints, invalid duration and incompatible definitions |
| `finance.calculate_ttm` | Four complete, consecutive, non-overlapping quarterly flow observations -> trailing total | Never sum balance-sheet stocks or EPS mechanically; reject gaps/mixed revisions |
| `finance.calculate_margins` | Revenue and explicitly defined profit measures -> margins and changes in percentage points | Distinguish operating/EBITDA/net/owner-attributable measures; reject invalid denominators |
| `finance.calculate_cashflow_metrics` | Reviewed CFO, capex, profit and debt/cash facts -> CFO/profit, a labelled CFO-minus-capex measure and selected leverage metrics | CFO-minus-capex is not automatically FCFF; sign and classification must be explicit |
| `finance.calculate_returns` | Dated prices with declared adjustment basis -> bounded price returns | Label unadjusted returns; do not call them total shareholder returns or ignore splits/dividends |
| `finance.calculate_valuation_multiples` | Compatible price/share count, earnings, debt/cash and flow facts -> selected multiples | Match point-in-time prices to stated earnings windows; report non-meaningful denominators |
| `finance.compare_companies` | Explicit peer set and compatible metrics -> descriptive comparison | Later extension; no hidden peer selection or automatic investment ranking |

Release order: comparisons and margins, cash-flow preparation, then DCF. CAGR/TTM must report insufficient history when subscription windows do not supply the required periods. Do not bypass this by inventing historical observations.

### 3.2 DCF: implement one model well first

Agree the contract with Advait before integrating his work. First support a two-stage FCFF model for appropriate non-financial companies: explicit forecast years plus perpetual-growth terminal value. FCFF is discounted at WACC; FCFE, if added later, must use a separate equity-model contract and cost of equity. This distinction follows [CFA Institute's free cash flow valuation treatment](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation) and [Damodaran's firm/equity valuation framework](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/lectures/val.html).

Do not apply the generic FCFF template to banks/insurers in the initial release. Sector-specific models, FCFE and dividend/residual-income approaches are separate extensions.

| Proposed function | Input -> output | Release |
| --- | --- | --- |
| `finance.prepare_valuation_inputs` | Historical facts, valuation date and model -> eligible inputs, missing facts, conflicts and required assumptions | First release |
| `finance.calculate_fcff` | EBIT, tax assumption, D&A, positive capex outflow and increase in noncash operating working capital -> FCFF with components | First release |
| `finance.build_forecast` | Explicit driver assumptions by year OR explicitly supplied FCFF forecasts -> dated forecast series and assumption trace | First release |
| `finance.calculate_dcf` | Approved forecast, WACC, terminal growth, equity bridge, diluted shares, currency/basis and discount convention -> valuation breakdown | First release |
| `finance.dcf_sensitivity` | Same model + bounded WACC/growth grids -> table with invalid cells marked | First release |
| `finance.run_scenarios` | Explicit base/upside/downside assumption sets -> comparable outputs; no implicit probabilities | First release |
| `finance.calculate_wacc` | Explicit cost/weight/tax inputs with dates and provenance -> WACC breakdown | Next; initial DCF may accept supplied WACC |
| `finance.reverse_dcf` | Reference market value and one bounded unknown -> implied assumption and solver diagnostics | Later |
| `finance.calculate_fcfe` | Equity cash flows with explicit financing assumptions -> equity model inputs | Later |

Initial formulas/conventions:

```text
FCFF = EBIT × (1 − tax_rate) + D&A − capex − change_in_operating_NWC
Terminal value at N = FCFF_(N+1) / (WACC − terminal_growth)
Operating enterprise value = PV(explicit FCFF) + PV(terminal value)
Equity value = operating EV + nonoperating assets − debt − other senior/non-common claims
Per-share value = equity value / stated diluted share count
```

Declare end-of-year discounting initially and the timing of the first forecast cash flow. An equity bridge must avoid double-counting cash/net debt and explicitly address noncontrolling interests, preferred claims and other material adjustments where applicable. Terminal growth, reinvestment and stable-state assumptions must be visible; [Damodaran's terminal-value discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/termvalapproaches.htm) is a reference for reviewing this model design.

Validate finite values, positive share count, declared decimal-rate units, tax-rate bounds, currency/scale consistency, explicit discount/forecast periods and `WACC > terminal_growth`. Bound forecast length and sensitivity cells; flag a nonpositive stable-state cash flow or implausible terminal assumptions for model review rather than silently forcing a positive valuation. Mixed accounting bases, missing required bridge adjustments or unsupported FCFF reconstruction return incomplete/blocked results. A supplied hypothetical model can still run with labelled assumptions; it must not be presented as a fully data-supported company valuation.

Return yearly cash flows and present values, terminal value and its contribution, enterprise/equity bridge, per-share result, sensitivity/scenario outputs, all assumptions, input evidence and limitations. Do not attach a buy/sell recommendation or portray an assumption-dependent result as an observed fact. Never equate net profit, EBITDA or CFO alone with valuation cash flows.

## 4. Citation and verification component

### 4.1 Separate attribution, checks and judgment

A working URL is not proof of a claim. A genuine document can be irrelevant to the company, period, basis or metric. Model agreement is not deterministic verification. Use separate status fields:

- Availability: located / retrieved / inaccessible / expired.
- Integrity: document hash recorded; quoted text matches or fails to match a retained passage.
- Context: issuer, period, basis and units matched / mismatched / unknown.
- Numerical check: passed / failed / insufficient evidence / not applicable.
- Semantic review: not reviewed / host-model supported / partial / contradicted / unclear / human reviewed.

A verdict must name the method and evidence used. A correct quotation alone cannot become a supported-claim verdict. A host-model assessment cannot become `deterministically_verified` merely because its JSON is valid. Support refers to attribution within the inspected evidence, not a guarantee that an issuer or publisher is truthful.

### 4.2 Proposed operations and state

| Function | Contract | Network effect |
| --- | --- | --- |
| `evidence.classify_sources` | Provider results -> source kinds, public/protected locators and irrelevant-image exclusions | None |
| `evidence.resolve_source` | Server-known source ID + permitted retrieval plan -> bounded document/excerpt handle, hash and provenance | Explicit, budgeted |
| `evidence.extract_passages` | Document handle + selected pages/sections -> passages/table cells with PDF index and printed-page labels | Local after retrieval; OCR optional later |
| `evidence.check_numeric_claim` | Typed claim + evidence facts/cells -> value/context/tolerance checks or unresolved status | None |
| `evidence.prepare_verification` | Atomic claims + retained evidence -> host-LLM task packet | None; never quietly resolves missing documents |
| `evidence.submit_assessment` | Packet ID + structured host assessments -> reference/quotation/schema checks and preserved model judgments | None |
| `evidence.render_citations` | Validated claim/evidence links + style -> human-readable citations with verification labels | None |
| `evidence.audit_answer` | Final claim manifest + citations -> coverage, missing sources, unsupported promotions and contradictions | None; prose-to-claim extraction is a separate model task |

Use opaque, unpredictable, session-bound handles. Packets bind exact evidence hashes, claim text, task/protocol versions, expiry and allowed evidence IDs. A missing/expired document cannot silently trigger a new charge. Return an explicit request for a newly planned resolution.

### 4.3 Full citation workflow

1. The host identifies atomic claims or submits selected typed numerical claims. Separate reported facts, calculations, assumptions, opinions and forecasts.
2. Margin maps candidates to existing provider records and canonical source IDs. Source selection is task-specific: financial claims normally seek issuer/exchange filings; news claims may cite the originating article. Provider summaries remain labelled summaries.
3. The host explicitly requests permitted resolution for unresolved sources. Margin uses reviewed official resolver routes and bounded downloads. Never expose a generic authenticated arbitrary-URL fetcher or forward provider auth across hosts.
4. Extract selected passages/table cells, record document hash and page/section coordinates, and check company/period/basis/unit context. Source text is untrusted data, including instructions embedded inside documents.
5. Run available deterministic numeric/context/quotation checks. Units and rounding tolerances derive from the source's displayed precision; discrepancies are not reconciled by averaging.
6. Package unresolved semantic questions for the user's LLM with exact evidence IDs and a response schema.
7. The LLM returns one assessment per claim, citing supplied passage IDs and quoting support/counterevidence. It must be able to say unclear, insufficient evidence or contradicted.
8. Margin validates IDs, packet freshness, quoted substrings and schema; it combines these checks with the separately labelled semantic assessments.
9. The host writes/revises the answer. A final structured claim/citation manifest is audited before presenting an attributed answer. If the host skips this step, Margin does not claim the complete answer was audited.

If direct originals are unavailable, preserve provider attribution and an unresolved-original status. OCR uncertainty, corrected filings, restatements and conflicts require explicit review rather than a stronger-looking citation badge.

### 4.4 Portable handoff to the user's LLM

Use a task/result round trip as the baseline. Before MCP packaging, the workbench can export a sanitized JSON packet and accept a pasted structured assessment. After packaging, the host can perform the same steps with tools.

```json
{
  "task_id": "opaque-task-handle",
  "protocol": "citation_review@1",
  "expires_at": "declared-expiry",
  "claims": [{"id": "C1", "text": "Atomic claim", "kind": "reported_fact"}],
  "evidence": [{
    "id": "E1", "source_id": "S1", "document_hash": "recorded-hash",
    "pdf_page_index": 8, "printed_page_label": "9", "passage": "bounded source excerpt"
  }],
  "deterministic_checks": [],
  "known_conflicts": [],
  "required_output": "claim_id, verdict, evidence_ids, support_quotes, rationale, limitations"
}
```

```json
{
  "task_id": "opaque-task-handle",
  "assessments": [{
    "claim_id": "C1", "verdict": "insufficient_evidence",
    "evidence_ids": ["E1"], "support_quotes": [],
    "rationale": "The passage does not establish the claimed period.",
    "limitations": ["Original statement table not available"]
  }]
}
```

`required_output` above describes the intent; implementation supplies an actual versioned JSON Schema. Assessments without trustworthy host/model metadata are marked self-reported. The host may use its main model or a separately selected reviewer; neither choice creates independent ground truth automatically.

MCP sampling can optionally request host-side model work when the client declares support and permits it. The portable design must not depend on sampling or require a Margin-owned LLM key. See the [official sampling contract](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling).

## 5. Sentiment protocol and deterministic aggregation

The first scope is **sentiment expressed in retrieved company-related news/filings**, not comprehensive market or investor sentiment. Broader sentiment would need additional populations and data access.

1. Define company, question/aspect, window, language, source set, retrieval cutoff and permitted spend.
2. Retrieve bounded news/filing records; report requested versus returned coverage and distinguish published, updated and ingested timestamps. Do not allow future information into an as-of analysis.
3. Group exact duplicates deterministically; mark likely syndicated/event duplicates for model or human review. Several articles repeating one report must not automatically become several independent observations.
4. Build a packet of eligible records and bounded excerpts with provenance. Title-only items and provider summaries have explicit evidence limitations.
5. Ask the host LLM to label company relevance, positive/negative/neutral/mixed/unclear tone, aspect, time horizon, reported event versus opinion/speculation, supporting passage IDs and counterevidence. Preserve provider-supplied labels separately.
6. Validate the annotation schema, IDs and quotations. A model's confidence number is not a calibrated probability; omit aggregate probability claims in v1.
7. Aggregate with a declared, deterministic policy. Default to counts by distinct reviewed event and a simple labelled balance score only where its denominator is meaningful. Keep mixed/unclear/missing observations separate; report sample size, exclusions, concentration and contradictions.
8. Return a source-linked summary for the host to explain, preserving uncertainty and the original-source/summary distinction.

| Proposed function | Behavior |
| --- | --- |
| `sentiment.prepare_analysis` | Retained record IDs + explicit scope -> deduplicated inventory, limitations and host task packet |
| `sentiment.submit_annotations` | Packet ID + per-record labels/evidence -> structural validation and labelled model/provider judgments |
| `sentiment.aggregate` | Validated annotations + versioned weighting policy -> counts, optional balance, coverage and concentration |
| `sentiment.compare_windows` | Two compatible bounded analyses -> descriptive changes with sample/source differences; later extension |

A simple initial balance can be `(positive - negative) / (positive + negative + neutral)` after the declared grouping policy. Exclude mixed/unclear from that denominator but display their counts. Return undefined if the denominator is zero. This is an engineered summary of annotations, not a probability of price movement or a validated measure of all investors' views. Alternative weights need explicit versions and separate evaluation.

## 6. Versioned research protocols

Store protocols as structured definitions with readable instructions, required/optional steps, input/output schemas, admissible tools, evidence requirements, limits and stop conditions. Each task/result records the protocol version.

| Protocol | Workflow and enforced checkpoints |
| --- | --- |
| `company_research@1` | Resolve identity -> inspect coverage -> select financial/event windows -> retrieve -> compare/analyse -> cite; require exchange/identity and visible missing coverage |
| `quarterly_review@1` | Establish fiscal quarter and reporting basis -> obtain comparable quarters -> compute deltas -> inspect developments -> attribute claims; no silent quarter/basis joins |
| `dcf_valuation@1` | Select model -> check inputs -> separate facts/assumptions -> calculate -> sensitivity/scenarios -> cite inputs -> explain conditional result |
| `citation_review@1` | Claim decomposition -> source resolution -> deterministic checks -> semantic task -> validated assessment -> rendered citations/audit |
| `sentiment_review@1` | Define scope -> retrieve -> group duplicates -> host annotations -> validate -> aggregate -> cite limitations |
| `conflict_review@1` | Preserve competing facts -> check metric/period/basis/unit/restatement -> seek original evidence -> resolve with a reason or retain conflict |
| `event_context@1` | Later: build sourced event timeline and descriptive market context; no causal claim from ingestion-time/price coincidence |

Add `protocols.get_protocol` / `protocols.validate_submission` as portable tool fallbacks. MCP prompts can offer user-selectable entry workflows and resources can expose versioned guidance/schemas, but hosts choose how to use them; mandatory checks stay in tools. These roles align with the official [prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) and [resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) contracts.

## 7. Provider extensions and data sufficiency

Preserve the existing thirteen approved operations. Validate held search/actions/identity/category paths and the real earnings-detail selection before broader expansion.

First extensions should be `search_news`, `search_announcements`, `get_concalls` and `search_concalls`, selected only when they support evaluated workflows. Review each nested schema, access, cost, output structure and source depth before admission. Events/upcoming calendars, block deals and sector screens follow later; the mapped 25-operation inventory is not an automatic allowlist.

Create a per-function sufficiency checklist. For example, DCF input preparation may require annual cash-flow components, debt/cash, minority claims and an appropriately scaled share count. Available Free history and provider nulls may be insufficient. Options are explicit user-supplied inputs, permitted temporary original-source extraction, or rechecking a paid tier when it addresses a measured gap. Never buy, backfill or silently upgrade access as part of a calculation.

No new provider subscription is required merely to implement pure calculations and protocol validation. Before later live tests, recheck current key access/allowances; historical balances and pricing do not define present capacity.

## 8. Storage, bounds and interfaces

Keep financial payloads, evidence excerpts and documents temporary. Reuse compatible permitted data within a task to avoid repeated quota use; no background ingestion, vector corpus or permanent market database. An operational ledger is separate from financial content.

Proposed initial evidence bounds, to be tuned after measurement: up to 20 atomic claims, five candidate sources, three resolved documents and ten selected pages per task; 25 MiB per document; bounded excerpt/host-context size. Existing 2 MiB tool-result limits remain separate from document-transfer limits. All resolution, redirects, diagnostics and cleanup must fit the explicit HTTP/credit plan. Permit only reviewed destinations, sanitize before persistence/output, and never give the model a credential-bearing URL.

Task handles and excerpts expire with declared TTLs. Expired tasks fail explicitly. Preserve retrieval time, source identity, hash and method in results so the user can retain an audit record without Margin retaining a corpus. Retention and excerpt sharing must respect provider permissions; the current expired historical receipt deadlines are not extended by this plan.

Proposed modules alongside the existing core:

```text
src/margin/
  facts/          provider mappings, metric definitions, compatibility and units
  finance/        pure calculations, DCF, scenarios and sensitivity
  evidence/       source registry, temporary resolution, passages and verification
  protocols/      versioned workflows, task schemas and submission validation
  sentiment/      packets, annotation validation, grouping and aggregation
  interfaces/
    workbench/    evidence/assumption inspectors and manual host-LLM handoff
    mcp/          later thin tools, prompts/resources and transport lifecycle
```

Do not expose every helper as an MCP tool. Choose public operations around user intent; keep the provider namespaces, calculation versions and evidence/task contracts stable. Return structured results and a readable representation, respecting the supported MCP output contract. See [official tools and structured output](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). The versioned references are contract references, not a claim that the pinned SDK supports every later feature; test SDK/host capabilities before changing dependencies.

## 9. Work packages, dependencies and acceptance

A roughly five-week first-release plan for four contributors, with parallel work, is a scope estimate rather than a promised deadline. Provider/source access is a gate, not a reason to report untested features as complete.

| Package | Suggested effort/sequence | Acceptance |
| --- | --- | --- |
| A. Current workflow repair | Week 1, 2–3 days | Actual news/earnings fields display correctly, detail selection works, source images excluded, PDF columns readable; regression cases reproduce real shapes with invented values |
| B. Fact/accounting contracts | Week 1 into week 2 | Identity/units/basis/period checks block incompatible calculations; budget/usage/metadata/cleanup accounting is inspectable; selected live paths have documented outcomes |
| C. Deterministic finance | Weeks 2–3, parallel with evidence | Comparisons, FCFF, DCF and bounded sensitivity reproduce independent reference examples; missing-input and sector limitations are explicit |
| D. Citation tasks and resolver | Weeks 2–3 | Selected source can be resolved transiently, numeric check run, semantic packet exported and assessment validated without fake verification promotion |
| E. Protocols and sentiment | Weeks 3–4 | Versioned procedures and packet/annotation/aggregation flow work through the workbench using a user-selected LLM |
| F. Selective provider extension | Weeks 3–4 only as needed | A few new operations pass schema, entitlement, billing, bounds and source checks; skip extensions irrelevant to the first workflows |
| G. MCP adapter | Week 4 after core contracts stabilize | Same services accessible through local stdio; tools list without paid fetches; host prompt/resource fallback tested; optional sampling capability checked separately |
| H. Integrated evaluation/handoff | Cases designed in week 1; execution weeks 4–5 | Reproducible two-company demo, independently checked calculations/evidence sample, measured costs and honest limitations |

Critical dependency: current repairs -> context/fact contracts -> parallel finance/evidence -> protocols/sentiment integration -> MCP/host evaluation. Pure finance development can begin from explicit inputs before live extraction is solved; automated source-supported valuation cannot.

Suggested ownership: Advait leads financial definitions/calculations; one contributor owns provider/fact/accounting integration; one owns evidence/protocols; one owns workbench/MCP/integration evaluation. Numerical and claim-verification reference cases should be reviewed by someone other than their implementer. Each owner updates contracts, usage and status in the same change.

## 10. Test and evaluation plan

Keep the existing tests; add cases that target real limitations rather than merely increasing test count. Default automated tests remain offline, using provider-shaped contracts with fictional values. Use bounded authorized live calls to establish real coverage/access/cost; no deliberate quota exhaustion or broad backfill.

- Finance: independent worked examples, rounding/scale/date/basis checks, zero/negative baselines, incomplete quarters, cash-flow classification, missing share counts and debt adjustments, invalid WACC/growth, overflow/nonfinite values and scenario reproducibility. Test discount-rate monotonicity only under the assumptions where it should hold, such as fixed positive future cash flows.
- Evidence: wrong issuer/period/basis/unit, altered documents, printed versus PDF page numbers, forged/expired IDs, nonexistent quotations, contradictory passages, restatements, OCR ambiguity, duplicate secondary sources, decorated image URLs and instructions embedded in source text. Lexically matching quotations with unsupported interpretations must not pass semantic review automatically.
- Sentiment: ambiguous company names, syndicated duplicates, opinion versus reported fact, negation, mixed tone, sparse samples, timestamp uncertainty and incomplete articles. Add Hindi/mixed-language coverage only with explicit language handling and appropriate labelled evaluation; do not assume English testing establishes it.
- Operations: concurrent tabs, shared connections, cancellation, uncertain charges, result expiry, restart accounting, partial provider access, source-download bounds and no credential leakage. GUI/CSS fixes should be checked in browser and print, not inferred from unit tests.
- Host evaluation: approximately 20–30 predefined tasks across retrieval, comparisons, DCF, evidence verification and sentiment. Start with RELIANCE/TCS; expand coverage only under a separate budget. Compare direct provider access, aggregation alone and aggregation plus protocols/calculations with the same model, questions, as-of evidence and comparable budgets. Record host/model versions, context and generation settings; report variance and failures.

Measure numerical accuracy, correct abstentions, citation support and coverage, false verification rate, retrieval coverage, duplicate dispatch, latency, HTTP attempts, measured credits and host tokens separately. Evaluate semantic assessments against a small independently reviewed claim set. Citation support and answer correctness are distinct dimensions; [ALCE](https://aclanthology.org/2023.emnlp-main.398/) is a methodological reference, not evidence that our verifier is accurate.

First-release gates: deterministic functions match reference calculations within declared precision; no critical credential leaks or duplicate paid dispatches in exercised paths; no promotion of model judgments to deterministic verification; selected live workflows and source failures are documented; an actual host can complete the packet/assessment round trip. Set task-quality thresholds after a pilot baseline rather than inventing performance claims now.

## 11. Deliberately later work

FCFE, reverse DCF, sector-specific valuation, broad peer ranking, comprehensive investor sentiment, causal event studies, portfolio optimization, forecasts trained on market data and all remaining provider operations are later scope. Public multiuser hosting needs separate user isolation, provider permission and account-wide accounting work. None is a prerequisite for the first credible local research release.

No runtime implementation, authenticated provider request, purchase, dependency installation or model call is authorized/executed by this planning document. Public primary references were reviewed for financial-method and MCP/citation design; live access and financial inputs must be established during the corresponding work packages.
