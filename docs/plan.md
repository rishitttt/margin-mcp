# Delivery and evaluation plan

Updated for the **first core/workbench build**. The synthetic core, provider adapters and temporary interface are implemented; authenticated runtime/source validation and Margin MCP packaging remain open. [Core/workbench architecture](design/core-workbench.md) is the active design; [later MCP adapter](design/mcp-aggregation.md) preserves the packaging target. [Implementation status](implementation.md) owns delivered behavior and [API testing](api-testing.md) owns bounded source experiments.

## Current objective

Build and validate the core financial-research functionality through a **local browser workbench before packaging our own MCP server**. The same Python services must later support MCP without rewriting providers, validation, budgets or evidence handling. Provider transport stays **BharatStock REST + Drishti MCP**; the latter still requires an MCP client during this phase.

Implemented **FastAPI + a small local HTML/CSS/JavaScript interface**, one process/worker bound to loopback. The core is framework-independent. No React app, public hosting, database/corpus, LLM service or chat UI is a prerequisite. Synthetic mode is the default. The workbench is a development tool, not a financial-data repository or product frontend.

Existing evidence is the 8/9 October trial and 25-function schema map. It supports beginning core implementation, not universal live access or accuracy claims. Last observed Drishti balance was 986 on **9 October**, not a current reading. The initial build used no agent-initiated authenticated API requests or purchase. The user’s 21 October PDF now adds successful combined live execution evidence, with presentation/billing/source gaps recorded in implementation status.

## Build sequence

Current progress: increments 0–3 have an implementation and offline integration checks; increment 4 has started with the user’s successful eight-call RELIANCE workflow. News/earnings rendering, detail selection and print defects found in the export must be resolved before claiming the interface complete. Browser acceptance covers the main workflow; remaining Phase 1 work is bounded live validation, original-source review where obtainable, and clean/manual handoff. See [delivered evidence](implementation.md#first-coreworkbench-build-checkpoint) and [runnable guide](workbench.md). This does not mark all live shapes or Phase 1 complete.

Estimates below are working effort for a four-person team, subject to availability and provider access. They are not a new submission deadline. The first useful synthetic vertical slice should precede the full interface; plan roughly **6–9 working days** for an initial core/workbench pilot, with workstreams in parallel where interfaces are agreed.

| Increment | Deliverable | Acceptance / evidence |
| --- | --- | --- |
| 0: contracts and scaffold; 0.5–1 day | Python package/test setup, core request/result/plan/receipt records, approved operation registry, synthetic mode | Tests run without keys or external/provider network; no FastAPI import in core; raw licensed outputs are not fixtures |
| 1: execution vertical slice; 1–2 days | One REST snapshot and one reviewed Drishti earnings operation through policy, adapters, sanitizer and receipt services | Real clients against synthetic REST/MCP servers; identity/context preserved, errors/unsafe output handled and spend reserved atomically |
| 2: workbench shell; 1–2 days, can overlap increment 1 | FastAPI lifecycle, local static UI, plan/run controls and sanitized result inspector | Search/Run are explicit actions; GET/rerender makes no data call; keys stay backend-side; duplicate Run causes one dispatch |
| 3: useful research modules; 1–2 days | Company identity; financials/ratios/prices/actions; selected news/filings/earnings; simple bounded overview preset | Realistic synthetic tables/price line/event cards, separate periods/bases/units, partial-provider behavior and trace/citation display |
| 4: bounded live/source review; about 1 day, access permitting | RELIANCE first, selective TCS comparison; current allowances checked under an explicit budget | Actual REST/MCP paths, measured requests/credits, new-operation access and source-quality gaps recorded; no blanket financial verification |
| 5: manual demo and handoff; 0.5–1 day | Repeatable setup, five workbench scenarios and evidence report | Same services work directly and via UI; no duplicate fetch on refresh; known conflict/missing/uncertain cases visible |
| Later: MCP adapter | Tool listing, result/error conversion and stdio lifecycle over the tested core | Real downstream MCP transport tests, then paired host/model evaluation; no separate retrieval implementation |
| Later: evidence/semantic extensions | Transcripts/search, transient source resolver, selected compatible financial/event tools | Independent entitlement/cost/source checks; no automatic expansion to every mapped operation |

Implement admission and sanitation in the first slice, not after the live UI. The first live result can be displayed through the minimal inspector; a polished dashboard is not a gate. A synthetic UI alone is not source validation. Conversely, upstream MCP SDK success is not a delivered Margin MCP server or a model-host demo.

## Functional scope and staged runs

| Area | First-phase operations |
| --- | --- |
| Identity | BharatStock search/snapshot; selective Drishti resolution/metadata cross-check |
| Numeric data | BharatStock quarterly/annual financials, ratios, bounded EOD prices and corporate actions |
| Events/evidence context | Drishti news, announcements/categories, earnings list/detail; safe source locators and provider analysis labels |
| Diagnostics | Reviewed operation discovery/states, payload inspection, context warnings, receipts, requested/actual coverage and estimated/observed costs |
| Combined use | Explicit operation plans; start with snapshot + quarterly financials + news + announcements; optional modules are selected, not automatically fetched |

Earnings detail is staged: list a small set, select a returned record/quarter and then fetch that detail. Semantic call search is the first extension after data access/billing/citation checks; market calendars with fallback, ownership/screener expansion and broad sentiment remain later. No autonomous agent, iterative broad discovery, universal reconciliation or claim verifier is in the initial phase.

The 9 October design's thirteen proposed downstream MCP tools are a **later packaging profile**, not a requirement to expose thirteen browser controls now. The workbench calls core operation services. For Drishti the adapter internally uses the four actual wrappers and reviewed nested inputs. Twenty-five known schemas are documentation, not permission to enable all operations.

## Core and interface acceptance

- Provider tests cover exact REST mapping/headers/pagination and selected Drishti nested schemas/logical bounds; malformed filters, IDs/window conflicts, index expansion and schema drift fail before dispatch.
- Sanitization covers provider JSON/text/errors/catalog/guidance, embedded/encoded URLs and fake credentials. UI views never receive unsanitized payloads, keys or private signed URLs.
- Backend state survives browser refresh/tab changes, shares one ledger and one provider context, and deduplicates run submission. Payload expiry/eviction does not permit replay; expired results are not refetched automatically.
- Adapter lifecycle tests cover async task ownership, implicit MCP catalog traffic, independent provider errors, timeout/cancellation, shutdown and uncertain billing. No automatic data retry or quota exhaustion test against real accounts.
- Present known context faithfully: original values/paths, period/basis, nulls, conflicting fields, stale numeric versus newer event dates, publication versus ingestion and citation evidence level. Unknown layouts stay unverified.
- Use separate limits: news/announcements up to 20 records/30 days; earnings/call discovery up to 365 days; eight quarterly/two annual financial rows; prices up to 300 rows for one company/year. Trials use smaller scopes. A second page is another explicit operation.
- Manual scenarios: company selection with ambiguity; financial and price inspection; news/filing display; selected earnings detail/conflict; one partial/failed/uncertain run. Default tests/scenarios are synthetic and labelled. Selected live scenarios document what was actually checked.

Ruff/pytest, package metadata and a tested development dependency constraint snapshot are delivered with the first package; maintain them alongside runtime changes. Core and HTTP/UI tests are required in Phase 1. Margin stdio packaging/real-model host comparisons are later gates, while the upstream Drishti MCP client is still tested now.

## Budgets, retained state and existing source plans

No authenticated live execution occurred in the first core/workbench build. The [test protocol](api-testing.md) retains historical results and prospective bounds; before any later live run, reconcile current key/account state and write an ordered plan including metadata, data, usage checks and cleanup. The 986-credit snapshot and October pricing are historical evidence, not fresh account information. Do not purchase or upgrade solely to build synthetic/core functionality.

| Future source exercise | Existing proposed ceiling / interpretation |
| --- | --- |
| Focused Drishti diagnostic | At most 24 HTTP requests / 15 observed credits, including lifecycle/accounting; selected shapes only, not a standing recurring allowance |
| Focused BharatStock follow-up | At most six REST requests, further reduced by remaining daily quota; search/actions gaps, not a replay of the twelve-request initial trial |
| Initial live pilot | Up to 50 prospective Drishti credits total including the focused diagnostic; allocate each run first |
| Expanded coverage | At most 500 prospective credits including the pilot; deferred until measured costs justify the study |

The backend's proposed run/process allowances and the stricter source-test ceiling both apply. Account-wide limits/other processes remain external. No auto-reload/multiple workers during live sessions. A process restart loses in-memory spend history and is not a daily cap. Keep only bounded, expiring sanitized results for inspection; no persistent financial-response cache or data export by default. Idempotency/accounting records are separate from payload buffers and cannot be reset by UI navigation.

Private outputs from 8/9 October have manual review dates 22/23 October. This plan does not extend retention or authorize putting saved licensed payloads into fixtures. Reuse the documented findings and synthetic cases; review private artifacts before any permitted use. Current subscription advice is maintained as dated research, and should be rechecked before purchase.

## Four-person work split

| Workstream | Owns | Shared artifact |
| --- | --- | --- |
| A: providers/contracts | BharatStock REST, Drishti session/discovery, reviewed operation maps and selected live checks | Adapter contract and synthetic upstream fixtures |
| B: core/policy | Service records, planner/coordinator, validation, budgets, cancellation and safe evidence pipeline | Tested execution path and result/receipt interface |
| C: workbench | FastAPI lifecycle/routes, local UI, view mapping, idempotency integration and run inspector | Thin interface that calls shared services |
| D: evaluation/docs | Independent source/financial checks, test cases, demo rubric and setup/status documents | Evidence report and clean-environment reproduction |

Agree on contracts first; integrate provider and policy tests before adding live credentials to the UI. These are suggested human responsibilities, not delegation to autonomous agents or authorization to contact providers.

## Later evaluation and deferred material

After the two-company pilot, the existing twelve-company coverage panel can measure eight-quarter/two-annual/year-price and event/source coverage. Requested slots remain targets, not acquired data; original-source availability and checked financial cells are separate measures. No corpus acquisition target is restored.

Paired real-host evaluation moves to the MCP phase. Its baseline uses the same REST-backed BharatStock adapter plus directly attached Drishti MCP. The workbench phase measures provider/core correctness, request/credit behavior, inspectability and manual workflow completion; it does not claim LLM accuracy improvements.

### Proposed corpus composition

Retained for older links. Earlier document-count/archive targets are superseded. Historic code/documents remain on [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1/docs). Current work retrieves external data on demand and retains only explicitly permitted temporary diagnostic material.

### Remaining gates

Before live workbench execution: tests for shared admission, sanitization, idempotency, lifecycle and local interface safety. Before live-source claims: selected entitlement, billing and real-return evidence. Before financial normalization/claim verification: compatible definitions/context and original evidence resolving the known conflict. Before Margin MCP: stable core contracts and workbench validation, then actual downstream transport/host tests. Before public hosting: separate provider permissions, user auth, isolation and accounting design. None of these gates requires a financial corpus.
