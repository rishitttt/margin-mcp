# Implementation and validation status

Current state: **the first reusable Python core and temporary local workbench are implemented and validated with synthetic data.** Provider transport is BharatStock REST + Drishti MCP; Margin MCP packaging remains later. The user’s seven-page 21 October workbench export shows eight successful live RELIANCE calls across both providers, including Drishti news, announcements and earnings discovery. Broader operation coverage, actual account debit reconciliation and financial/source verification remain pending. Authenticated source evidence remains the dated 8/9 October tests. Earlier MCP-first architecture decisions below are historical and superseded by the 20 October planning checkpoint. This file owns delivered state; [active design](design/core-workbench.md) and [plan](plan.md) own future work.

## Branch transition

- Prior local-corpus/PDF implementation: preserved at `c77963d` on pushed [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1).
- Aggregation research/planning committed on `main` as `be04aba` before cleanup.
- Legacy code, tests, examples, CI, package manifests and superseded guides removed from `main` through a normal commit, without branch resets/history rewriting. Ignored local artifacts were not removed.
- `main` now contains the installable `margin-research` core/workbench, synthetic tests and current documentation. No downstream Margin MCP server, universal financial normalization or claim verifier is implemented. The old corpus CLI commands are not supported on this branch.

## Validation

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
