# Margin build and evaluation plan

**25 November delivery checkpoint:** the planned stdio MCP alpha is implemented as package 0.3.0, with 14 workflow tools, 220 tests and source/isolated-wheel protocol acceptance. Core/data limits are preserved. [MCP usage](mcp.md) and [implementation](implementation.md) own delivered behavior/evidence. Next gates are a fresh-chat host trial, a separately budgeted live MCP probe and versioned model comparisons; no model-host result is inferred from SDK tests.

**25 November MCP implementation plan:** core checkpoint `6b22f57` was pushed after 194 tests and a source/private-data review. The user authorizes the local stdio MCP alpha. [MCP architecture and acceptance](design/mcp-aggregation.md) now owns the 14-tool mapping, lifespan, state/budget/logging boundaries and sequence. This planning revision precedes runtime implementation; no provider/model requests are planned for initial protocol checks.

## Active repair pass: 24 November 2026

**Completed core pass:** documented units, normal-quarter eligibility, continuing-profit guards, eight additional finance interfaces, reviewed summary announcements and tests are delivered. See [implementation](implementation.md), [current function matrix](reference/function-validation.md) and [finance decisions](design/finance-data-support.md). Missing quarterly CFO/capex, automatic forecasts and full original-source validation remain limits. The numbered plan below records the agreed implementation sequence.

Authorized scope: repair HUL findings, establish finance/data support and implement useful
data-supported functions before MCP packaging. Preserve existing work and old private packets.

1. Review the issuer's Q2 result tables to reconcile product-sales versus total revenue;
   retain metric identity, period, basis and source locators instead of overwriting providers.
2. Add explicit auto/documented unit handling with raw-value/evidence lineage, preserving
   unknown and caller-declared modes. Map balance-sheet stocks separately from flow facts.
3. Establish quarter starts only under reviewed provider metadata rules (explicit duration
   markers present, normal calendar-quarter end, no longer/derived-period flags); reject
   cumulative, missing-marker and ambiguous cases. Propagate basis-change warnings.
4. Add deterministic balance-sheet and cash-conversion metrics plus retained-company
   wrappers and a financial-data readiness function. Readiness explains missing fields,
   periods and assumptions; it must not imply a general accuracy verdict or fetch extra pages.
   Keep existing margins/growth/CAGR/TTM and explicit FCFF/DCF/scenarios/sensitivity.
5. Inspect changed announcement inputs, update only reviewed contracts and retain strict
   drift/selector/cost bounds. No generic schema bypass or unrelated native tool exposure.
6. Validate regression/reference math, service/CLI/HTTP/browser paths and real saved HUL
   data separately. Live allowance: at most B2 and D14 HTTP including lifecycle, six estimated
   credits, no retries or pagination. Prefer saved responses/public issuer documents; stop
   at access/quota/uncertain outcomes. No purchase or broader corpus collection.
7. Save a new ignored private result packet and update finance coverage, usage, skill
   reference and current status. Document finance MCP patterns from primary sources and
   distinguish delivered, data-limited and assumption-dependent functions. Core remains
   transport-independent; no downstream MCP server is implemented in this pass.

The metadata-only pass used D6 HTTP including cleanup and zero estimated credits. The
Drishti bound was revised from D12 to D14 before further execution to accommodate a second
reviewed-schema connection and cleanup; no failed/uncertain data call is retried.

Updated **24 November 2026**. This is the active build plan following the user's 23–24
November decisions. Citation verification and sentiment protocols are back in scope;
this supersedes the 15 November deferral. This document describes proposed work, not
newly delivered features. Product and optional evaluation remain separate.

**Implementation checkpoint:** core 0.2.0 delivers the lightweight citation/sentiment handoffs and readiness repairs. [Review workflows](review-workflows.md) owns actual interfaces and [implementation status](implementation.md) owns checks/gaps. Original-source resolution/parsing remains optional backlog. MCP packaging has not begun.

## 1. Starting point and release boundary

Reuse Python, BharatStock REST, upstream Drishti MCP, the financial core, workbench and
agent CLI. Do not rewrite adapters or restore the `d1` corpus project. The first live
skill pilot passed 38 selected automatic checks; it also exposed incomplete data,
announcement discovery disagreement and untested wrappers. See [pilot evaluation](live-skill-evaluation.md).
It is a development result, not proof of general accuracy or MCP-host compatibility.

The bounded product release comprises reliable retrieval, reviewed deterministic finance,
on-demand evidence resolution, citation-review and content-sentiment workflows, and a
thin local MCP adapter. DCF remains explicit-assumption unless source mappings are
independently established. No maintained financial corpus, public hosting, background
crawler or mandatory model subscription is introduced.

The optional `research/` project owns tasks, independent gold, model runs and analysis.
Product installation must not depend on that project, test-company lists or answer keys.

**24 November clarification:** no LLM inference or verifier-model service runs inside
Margin. All semantic extraction, claim-support and sentiment judgments use the user's
host/model. Ordinary API requests, parsing and arithmetic do not require LLM compute.
For citations, start with provider provenance/source locators plus a host review protocol;
source fetching/reading may use the host browser or a separate fetch/document MCP.
Margin cannot call other host tools merely because they are installed. Its own bounded
non-LLM source reader is an optional portability extension, not a mandatory first stage.
Until Margin itself checks source content, returned semantic/quote judgments remain
host-reported; schema validation alone does not independently verify them. Batch B below
is the staged evidence backlog, not a requirement to build PDF extraction first.

## 2. Architecture and responsibilities

```mermaid
flowchart TD
    H[Host agent and model] --> M[Margin MCP adapter]
    H --> W[Common host search tools when configured]
    M --> C[Core registry, budgets and financial functions]
    M --> P[Versioned citation and sentiment workflows]
    C --> B[BharatStock REST and Drishti MCP]
    P --> E[Temporary source resolution, passages and checks]
    P --> Q[Bounded assessment packet returned to host]
    Q --> H
    H --> A[Submit labelled assessment and evidence references]
    A --> P
    R[Separate evaluation runner] --> H
    R --> L[Private decision trails and independent evaluator]
```

- **Margin:** retrieval, bounded source access, exact arithmetic, context checks, packet
  state, evidence/citation formatting and validation of references/quotes/assessment shape.
- **Host/model:** research choices, optional search, claim decomposition and semantic
  support/sentiment judgments. Valid JSON is not proof of correct interpretation.
- **Operator:** provider configuration, allowed sources, budgets and a declared host profile.
- **Evaluator:** independent source-backed answers and blinded review; it must not adopt
  the tested model's verification labels as ground truth.

Use one citation protocol with capability-dependent routes; do not maintain GPT/Qwen/Claude
branches or infer ability from model names. Standard MCP negotiation advertises client
features such as sampling, not browsing availability or citation competence. Application
profiles are proposed Margin metadata, not standard MCP capability fields. Details and
fallbacks live in [capability routing](design/analysis-and-protocols.md#45-capability-routing-and-model-limitations).

## 3. Implementation batches and acceptance

### Batch A — repair retrieval and stabilize shared contracts

1. Make current Drishti metadata state visible consistently in catalog, preview and
   execution. Changed/expired contracts must never look ready. Preserve adapter guards.
2. Validate the four remaining company wrappers with retained real-source references and
   offline shape cases; test their reuse and incomplete-input outcomes. Successful TTM
   needs genuinely established consecutive periods, not inferred starts.
3. Review capex and revenue definitions, source scales and EPS adjustment mappings. Keep
   TCS's capex definition discrepancy visible until reconciled.
4. Standardize evidence references: source ID, operation/run ID, explicit path root,
   original field/value, period/basis/unit, transformations and verification method.
5. Keep core, workbench, CLI and future MCP adapters on the same services and budgets.

**Acceptance:** meaningful regressions cover schema drift, incomplete data, cross-company
inputs, unit ambiguity, idempotency and retained reuse; no hidden refetch/retry; selected
live checks use a separately bounded request plan. Update implementation/function docs.

### Batch B — minimal evidence and citation workflow

Implement the contracts already proposed in [evidence design](design/analysis-and-protocols.md#4-citation-and-verification-component):

1. `evidence.classify_sources`: distinguish issuer/exchange filings, original news,
   provider summaries, protected locators and decorative links.
2. `evidence.resolve_source`: explicitly resolve a server-known source through an approved
   route. Stream with type/size/time bounds, validate destinations/redirects, isolate
   credentials and return a temporary handle/hash or an honest inaccessible outcome.
3. `evidence.extract_passages`: bounded PDF pages/text/table cells with page coordinates
   and extraction limitations. Only reviewed structured-cell mappings support deterministic
   numeric checks; uncertain PDF table interpretation remains unresolved or an attributed
   model assessment. OCR is a later extension if real cases require it.
4. `evidence.check_numeric_claim`: check typed values and known context with declared
   tolerances; do not equate matching numbers with a fully supported narrative claim.
5. `evidence.prepare_verification` / `submit_assessment`: frozen claim/evidence packets,
   structured host judgments, quote/reference validation and explicit unknown outcomes.
6. `evidence.render_citations` / `audit_answer`: format claim-linked citations and report
   missing evidence, contradictory claims and unsupported verification labels.

**Discovery:** begin with returned source locators and known issuer/exchange paths. Add a
search-provider adapter only after a bounded provider/coverage/cost probe. A host can search
and submit candidate locators for admission; the server does not assume it can see or call
other host tools. No full web-search engine or local source repository is required.

**Acceptance:** tests include matching/mismatching figures, wrong company/period/basis,
quoted text without claim support, inaccessible originals, expired packets, malicious
source instructions and unsupported host capabilities. A browser-less host receives
usable evidence when server resolution works; absent semantic assessment stays unreviewed.

### Batch C — finance completion and bounded sentiment

Finance can progress alongside Batch B:

- Independently reproduce comparison, CAGR, TTM and cash-flow reference examples.
- Reconcile Advait's work when supplied; retain the existing DCF contract rather than
  duplicating it. Check FCFF, equity bridge, scenarios and sensitivity with explicit inputs.
- Document automatic company-input coverage separately from arithmetic correctness.

Sentiment follows stable evidence IDs/packets:

- Implement `sentiment.prepare_analysis`, `submit_annotations` and `aggregate` using the
  [sentiment design](design/analysis-and-protocols.md#5-sentiment-protocol-and-deterministic-aggregation).
- Define target entity/aspect, historical window, source coverage and labels; group exact
  duplicates and preserve unsupported/unclear annotations and provider labels separately.
- Require evidence passages for entity relevance and model sentiment judgments. Without
  semantic annotation, return a source inventory and missing-analysis status, not neutral.
- Keep aggregation deterministic and versioned; no price prediction or comprehensive
  investor-sentiment claim. Window comparison is later scope.

**Acceptance:** independent finance reference checks; sentiment cases for other-company
summaries, mixed tone, duplicate events, empty data, conflicting evidence and absent
annotations. Two human reviewers establish study labels, with disagreement retained.

### Batch D — thin MCP packaging and simple decision trails

**Packaging gate:** finish the agreed core in Batches A–C and run the core acceptance matrix first. Only then implement the downstream MCP adapter. Existing Python/HTTP/CLI adapters remain the test interface until that gate passes.

- Add proposed `src/margin/interfaces/mcp/` and a local `margin-mcp` stdio entry point.
  Reuse core contracts; do not proxy our CLI/HTTP layer or create a service per tool call.
- Use explicit input/output schemas, structured errors and concise task-oriented tools.
  Keep provider-native calls available where needed; do not expose every internal helper.
- Expose versioned workflow definitions through a discoverable tool/resource. MCP prompts
  are optional conveniences; no assumption that every client supports or applies them.
- Keep packet round trips as the portable baseline. MCP sampling is optional after client
  support and pinned-SDK compatibility tests, not a release requirement.
- Retain the existing short `why` summary mechanism. The explicit evaluation runner
  records the actual tool name, sanitized arguments/result/error, summary and final
  answer/evidence references. Missing summaries are counted, never invented afterward.
- Normal product use remains transient. The recorder is explicitly enabled per study;
  no full hidden-reasoning capture system is required. The MCP adapter supplies a generic
  observation seam; optional research code consumes it, never the reverse.

**Acceptance:** clean wheel install; real MCP initialization/list/call tests; cancellation,
upstream lifecycle, readiness/errors, stdout purity and credential redaction. Demonstrate
one real host using bounded allowances and one browser-less client completing a citation
packet. Validate unsupported profiles without a hidden model fallback.

### Batch E — separate benchmark and cross-model evaluation

Prepare cases alongside product work, then freeze before main runs:

1. Keep RELIANCE/TCS as development cases; select held-out companies/questions before
   observing their model outcomes. Include calculations, evidence checks, sentiment,
   conflicting/missing information and appropriate abstention.
2. Another contributor independently checks gold, definitions, pages, tolerances and
   acceptable incomplete answers. Product citation judgments are not independent gold.
3. Use one common host loop/search interface where possible. Start with two small open
   checkpoints and one stronger comparator; verify checkpoint/runtime access before
   selecting the final roster. The shortlist is a candidate list, not an installation.
4. Compare common research tools, raw-provider tools and full Margin. Additional runs
   remove finance/citation/sentiment components to attribute improvements.
5. Keep current fresh-live-call preference. Pin financial periods/event windows, interleave
   condition order, retain permitted response hashes and report evidence drift/outages.
   Frozen replay is a separate possible experiment, not silently substituted.
6. Freeze tool/protocol versions, model checkpoints, prompts, thinking/quantization
   settings, tool/step/token budgets and logging requirements. Record profile differences.
7. Repeat runs. Separate correctness, evidence support, abstention, tool validity, provider
   failures, latency and cost; do not interpret aggregate arithmetic checks as total success.
8. Annotate decision trails for discovery, tool choice, invalid calls, recovery, repeated
   fetching, evidence reuse, protocol completion and unsupported assumptions. Use two
   reviewers on a subset; distinguish observed actions from self-reported explanations.
9. Predeclare main hypotheses; treat later pattern discovery as exploratory. Record
   missing trace visibility and avoid attributing host differences to model intelligence.

**Acceptance:** runner/evaluator isolation, real model-tool loops, independently reviewed
held-out tasks, repeated runs and a reproducible manifest. Cost the provider/model matrix
and confirm applicable evaluation scope before launching a large collection. No purchase,
provider contact or experiment is triggered by this planning revision.

## 4. Team allocation and next concrete batch

| Workstream | First responsibility | Review partner |
| --- | --- | --- |
| Core/provider | Batch A readiness, definitions, evidence reference contract | Finance/source |
| Finance/source | Independent numeric examples and DCF reconciliation | Core/provider |
| Evidence/protocol | Batch B packets/resolution, capability routing, then sentiment | Finance/source |
| Integration/evaluation | Thin MCP adapter, decision-log seam and separate runner | Core/provider |

Roles are proposed; no individual assignment or separate agent task has been dispatched.

**Implement first:** A's metadata/preview repair and source-reference contract, plus the
minimal B packet/status contracts. Next add bounded source resolution and the packet
round trip. Validate these before broader sentiment or a large model experiment. Independent gold preparation can proceed alongside core work. MCP transport implementation waits for the core-validation gate.

**Release gates:** reliable contracts → evidence/capability fallbacks → independently
checked finance and sentiment annotation flow → clean MCP/host acceptance → frozen study
conditions → repeated cross-model evaluation. A product release need not wait for a
finished research paper; the main study must use a versioned product release.

## 5. Documentation and source references

- [Implementation](implementation.md) owns delivered behavior and actual checks.
- [Finance/protocol design](design/analysis-and-protocols.md) owns citation/sentiment
  contracts and capability routing; [finance guide](financial-analysis.md) owns delivered functions.
- [MCP design](design/mcp-aggregation.md) preserves adapter/transport constraints; its
  older first-release sequencing is superseded here.
- [Research review](design/research-environment-review.md) preserves the professor's
  independent evaluation requirements and historical feasibility/rights research.
- [MCP lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
  [sampling](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) and
  [prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) are
  versioned references. Verify compatibility with the installed SDK before implementing;
  these links are not a claim that this is the latest protocol version.

The earlier 24 November revision was planning only. The user subsequently authorized core implementation and validation before MCP packaging; see implementation status for work actually completed. The prior validation checkpoint remains
126 offline tests; documentation/link checks for this revision are separate.

## 6. Core acceptance matrix before MCP packaging

| Area | Required coverage | Evidence gate |
| --- | --- | --- |
| Retrieval | All 13 contracts, schema/readiness changes between preview and run, bounds/redaction/empty/error cases | Offline integration plus bounded selected live probes; untestable upstream paths reported explicitly |
| Finance | All 11 local functions and all five company wrappers; missing context and retained reuse | Independent arithmetic/reference tests; no guessed source values |
| Citation handoff | Source registration/import, claim packets, host assessments, quote/context/numeric checks, rendering and structured final-claim audit | No hidden fetch/inference; host-reported versus independently checked scope preserved |
| Sentiment | Explicit date/entity scope, duplicates, positive/negative/neutral/mixed/unclear, missing/relevance exclusions and deterministic aggregation | Host labels remain attributed; empty/missing analysis never becomes neutral |
| Workflow state | Immutable hashes, expiry/capacity, atomic/idempotent submissions, invalid references and capability fallbacks | No persistence/corpus, no retries/refetch; bounded process-local state |
| Interfaces | Same services through Python, local HTTP and JSON CLI, visible why/recorder compatibility | End-to-end client acceptance before adding MCP |

The lightweight citation/sentiment core uses host-supplied passages or retained provider
text. No PDF reader, source search service or Margin-side model is required. Server-side
source fetching/parsing is a later optional extension with its own acceptance gate.
