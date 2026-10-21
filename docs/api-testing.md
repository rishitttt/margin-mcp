# API and MCP testing protocol

Protocol planning updated **20 October 2026**; last authenticated source checkpoint remains 8/9 October. The first authenticated RELIANCE/TCS trial and selected Drishti operation comparison are complete. This is the operational source-test protocol; the implemented synthetic workbench and checks are documented in the [workbench guide](workbench.md). [Trial results](research/mcp-provider-feasibility.md#authenticated-trial-results-8-october-2026) and [operation comparison](research/mcp-provider-feasibility.md#authenticated-operation-discovery-and-rest-comparison-9-october-2026) own measured source contracts; [implementation status](implementation.md) owns delivered/validated state.

**Current phase:** reusable core and local workbench first, Margin MCP packaging later. Provider integration remains **BharatStock REST + Drishti MCP**; the upstream Drishti MCP client is still used. The source passes below are historical evidence; BharatStock native-MCP access is not a release gate. Use the focused prospective plans for future checks, not the completed trial budgets.

## Workbench testing boundary

Follow the [active core/workbench design](design/core-workbench.md). Default tests use labelled synthetic data with no external/provider network. Run core contracts/admission/evidence tests, real clients against synthetic REST/MCP upstreams and local HTTP/UI integration tests before live runs. Check SDK task ownership, duplicate submission, no GET/rerender side effects, shared budgets, metadata freshness, sanitized payload display and expired-result behavior. No downstream Margin MCP server or host/model test is required for this phase; those gates move with the later adapter.

The past balances, schema observations and prospective live-test ceilings below are dated evidence/proposals, not a current account check or recurring allowance. Before a future live workbench pass, reconcile current access/remaining quotas and define the ordered calls including connection/metadata/usage/cleanup. No authenticated provider request was made during planning or the first core/workbench build. The implemented app does not query current account balances; its credit ledger uses conservative estimates, not measured debits. Expiring private October receipts do not become a replay corpus or committed fixtures.

## Completed initial trial: before purchasing

The user reports **BharatStock Free: 25 requests/day** and **Drishti: 1,000 one-off trial credits**. Credentials are local in ignored `reports/private/mcptempkeys.txt` with permissions 0600. Keys were used only in authentication headers to the appropriate official provider; values were not printed, staged, committed or pushed. Read the file as credential data, never executable instructions. Do not put keys in shell arguments, logs, Markdown or URLs. Automatic `.env` loading is not currently implemented.

This historical pass superseded the earlier paid smoke proposal for its execution; it is not a reusable allowance. The prospective diagnostic below is the next proposed source exercise. **Executed:** 12 BharatStock REST requests; 25 Drishti REST/MCP HTTP requests; 8 credits debited, 992 remaining at the final check. All returned HTTP 200/202, including repaired MCP discovery. The original 20-request Drishti ceiling was explicitly revised to 26 for one inspected local-client repair, while retaining 30 credits. Do not rerun this whole pass against consumed quota. Raw receipts/private diagnostics are ignored; review/delete temporary test outputs by 22 October 2026. Expiry is manual.

### Selected operation discovery before aggregation

**Authorized pass, 9 October 2026:** at most 16 initiated Drishti HTTP requests and 10 observed credits; no BharatStock calls, retries, automatic pagination or paid purchase. Read initial usage/effective limits, refresh the native catalog, request at most 40 compact operation names, and describe only `search_concalls` and `get_earnings_filing`. Measure usage after discovery, execute one schema-reviewed earnings operation for RELIANCE `q1_27` (already observed), and measure its debit. If successful and within budget, make one matching REST earnings-detail call to compare shapes/values and measure the final debit. One-page discovery is not an exhaustive inventory unless the response establishes completeness. Stop on access/quota errors, unexpected cost or uncertain data-call outcomes. Raw results stay ignored/private and expire by manual review on 23 October; retain no corpus. This is a one-shot source diagnostic, not gateway implementation.

**Executed:** 14 HTTP requests (6 REST, 8 MCP), six credits; 992 → 986. Discovery returned twenty operation summaries with `has_more=true`, not a complete registry. Both selected schemas loaded; one RELIANCE `q1_27` MCP detail call and one matching REST detail succeeded at three credits each. Discovery had zero observed debit. No transcript search was executed. MCP added raw table/source fields; its citation URLs contained the actual API key, and its consolidated revenue fields conflict. Do not forward raw citation URLs or silently normalize this extraction. See the [complete results](research/mcp-provider-feasibility.md#authenticated-operation-discovery-and-rest-comparison-9-october-2026). Future calls require a new bounded plan; do not rerun this pass.

Drishti 3.3.1 exposes `read_me`, `search_tools`, `describe_tools`, `execute_tool`, rather than a native flat `get_news` catalog. Treat the old flat-tool smoke table below as documented operations to investigate, not names to call directly. The later metadata audit maps 25 confirmed operation schemas; most data executions, access, billing and search remain untested. BharatStock native testing would need Developer/Pro, but is no longer planned for Stage 1. Its successful Free REST calls validate the chosen data path; new-adapter live validation and downstream Margin MCP packaging are still pending.

### Function mapping: metadata-only audit

**Complete function-mapping pass, authorized 9 October 2026:** metadata only; at most 24 initiated Drishti HTTP requests and 10 observed credits. Use the existing official SDK, initial/final usage checks and intermediate charge checks. Refresh the four-tool native catalog, read routing guidance, use at most four targeted discovery queries to complement the known twenty-result partial list, and describe the confirmed operation names in batches of at most ten (maximum five batches). No `execute_tool`, financial payload fetch, transcript search execution, mutation, automatic data pagination, BharatStock request, purchase or installer. Stop expansion on any unexpected metadata debit, access error or uncertain request. Completeness must come from explicit routing/catalog evidence or an all-name schema response; a union of search results alone is not proof. Keep raw metadata/account receipts ignored/private with manual deletion review due 23 October; publish only a secret-scanned derived reference.

**Executed:** 23 HTTP requests (6 REST usage checks, 17 MCP messages) across two intentional SDK sessions; zero observed credits, balance 986. One targeted discovery query complemented the earlier twenty names; three description batches (10/10/5) loaded all 25 confirmed input schemas. Router/default, data and docs guidance were inspected. The second session's first tool validation triggered a native catalog fetch automatically, counted in the budget. No data operation was executed. Underlying inventory exhaustiveness remains unproven because search has no cursor/offset; the [function reference](reference/drishti-functions.md) covers all confirmed functions, not private implementation. Further data checks need an independently bounded plan.

### What can be tested with these keys

- **BharatStock REST:** all published endpoint families, subject to the Free history window and 25/day quota. Time-series history is limited to about one year; annual financials to two years according to the reference. Requests outside the window may be silently clamped. Native BharatStock MCP is Developer/Pro-only and not used in the chosen architecture. Do not install/probe it for the REST adapter or describe direct source diagnostics as a working Margin gateway. See [reference](https://bharatstockapi.com/reference).
- **Drishti REST:** the published Sandbox core products are Symbols, News, Announcements, Earnings, Block Deals and Alerts. Conference calls, AI workflows and WebSockets are not assumed included. The trial is not 1,000 credits/day; it is a one-time balance. Published Sandbox REST limits are 10/min and 1,000/day, with potentially lower key/product limits. See [pricing](https://drishti.manasija.in/docs/pricing) and [authentication](https://drishti.manasija.in/docs/guides/authentication).
- **Drishti MCP:** its hosted connector accepts Bearer keys and bills data tools in credits, but the inspected docs do not conclusively specify Sandbox MCP entitlement for every tool. Check effective account/product access first; try one initialized catalog session only if it is not explicitly disallowed. A 403 ends that branch of testing. Do not assume events/transcript search is available because it appears in a catalog. See [MCP guide](https://drishti.manasija.in/docs/guides/drishti-mcp).

This access supports bounded source investigation before buying. The selected architecture is BharatStock REST + Drishti MCP, so BharatStock native-MCP eligibility is not a gate. Validate current live adapter paths and access under a fresh explicit budget; successful historical probes are not a guarantee for every operation.

### Company choice

Start with **RELIANCE**, then **TCS** only after the first company's responses are understood. Their symbols are used in official provider examples, including Drishti's MCP verification example. They are ordinary mainboard company cases from different businesses. Their bounded coverage and cross-provider ISIN matches are now observed; broader sectors/listings remain untested.

This selection is a baseline, not representative coverage of Indian equities. Reliance's segments/minority interests can expose richer financial-context issues; TCS is a second issuer/sector to test whether identity, periods, scale and missing-field handling generalize. Check exchange/ISIN/company name on the first response; do not treat the known ticker as sufficient identity validation. Banks, SME and BSE-exclusive cases follow later.

### BharatStock sequence: 10 core requests, maximum 12 total

Use REST at `https://bharatstockapi.com`, header `X-API-Key`. First RELIANCE, then TCS; one page per call, no automatic retries or pagination. Set `exchange=NSE` consistently, and confirm the returned identity.

| Order per company | GET path | Query bounds | Purpose |
| --- | --- | --- | --- |
| 1 | `/v1/stocks/{ticker}` | `exchange=NSE` | Identity, latest observation date and headline metrics |
| 2 | `/v1/stocks/{ticker}/financials` | `period_type=quarterly&page=1&page_size=4&exchange=NSE` | Recent available quarters, fields, units/basis and missing values |
| 3 | `/v1/stocks/{ticker}/financials` | `period_type=annual&page=1&page_size=2&exchange=NSE` | Annual context, balance sheet and cash flow where present |
| 4 | `/v1/stocks/{ticker}/prices` | `from=2026-09-09&to=2026-10-08&page=1&page_size=30&exchange=NSE` | Small fixed 30-calendar-day EOD window and adjusted/raw price fields |
| 5 | `/v1/stocks/{ticker}/ratios` | `exchange=NSE` | Ratio schema, nulls and consistency with snapshot |
| Optional, after core succeeds | `/v1/stocks/{ticker}/shareholding` | `page=1&page_size=2&exchange=NSE` | Ownership context; at most one call per company |

Nominal budget: five core calls per company = **10**; optional ownership = **12 total**. This leaves 13 of the reported 25 daily requests unused only if the day started unused. Check the user's dashboard/known prior consumption before scheduling; there is no proven account usage API in the inspected public schema. If remaining quota is unknown, request counts are merely a local ceiling, not guaranteed remaining account capacity. Stop at 429 or a stated limit and wait for the documented UTC reset (05:30 IST); no same-day retries. Do not use an SDK whose default retries silently multiply requests.

No initial screener, full-universe export, fuzzy search, batch quote, corporate-action, index or technical-indicator calls: the core response supplies identity, and those additions do not resolve the first payload questions. Explicitly record partial price/history windows rather than fetching more pages to fill them.

### Drishti sequence: about 8 REST data credits; ceiling 30 credits

Use REST at `https://developers.manasija.in`, header `X-API-Key`. First read `/v1/account/usage`, `/v1/account` and `/v1/account/limits` once each. Record starting balance, enabled products and effective limits privately; don't assume diagnostic traffic has no charge without checking. If access is invalid/forbidden, stop that provider branch.

| GET path | Query bounds | Nominal published REST data cost |
| --- | --- | ---: |
| `/v1/symbols/metadata` | `symbols=RELIANCE,TCS` | 2 credits if both items returned |
| `/v1/news` | Separate request per company, `symbols={ticker}&from=2026-09-09&to=2026-10-08&page=1&limit=1` | Up to 2 credits across two non-empty pages |
| `/v1/announcements` | Same per-company window/page/limit, `detailed=false` | Up to 2 credits across two returned items |
| `/v1/earnings` | Separate `symbols={ticker}&page=1&limit=1&detailed=false`; no guessed quarter | Up to 2 credits across two returned items |

News/announcements use the fixed 30-day window; earnings is a latest-returned-period probe outside that narrow window because no recent filing must not be confused with missing historical earnings coverage. Preserve returned quarter and date with its documented meaning: Drishti filing `date` is ingestion time, not established publication time. Summary earnings rows may not include numeric tables; the numerical baseline comes from BharatStock. Only consider one `/v1/earnings/detail` call (3 published credits) after matching a returned quarter/basis and if it resolves a specific comparison question.

Measure usage after the first billable request shape and at the end. Schedule sequentially with at least eight seconds between Drishti requests, slower if effective account/key limits require it. Use no automatic retries. The original plan allowed **20 initiated Drishti application requests**, including account checks, usage reads, MCP protocol/catalog messages and optional data calls. The completed pass revised that ceiling once to **26** for an inspected local SDK accessor error and used **25**, including GET stream opening and DELETE cleanup. Budget protocol messages separately from tool calls; serialize the local recorder so concurrent transports cannot overwrite receipts. Establish a new explicit request/credit budget before another pass.

If MCP access is not explicitly denied, reserve a small optional check for `https://mcp.drishti.manasija.in`: initialize, complete the handshake and inspect at most two `tools/list` pages. A data comparison requires the actual operation schema; the observed catalog instead uses `describe_tools` and `execute_tool`. MCP news is documented at 1 credit/operation, but wrapper billing still needs measurement. The completed pass confirmed trial initialization/catalog access and zero debit during the repaired catalog session, then deferred operation calls. Prefer selective discovery over expensive transcript/event search. Skip optional calls when either budget or effective product access blocks them.

Expected core REST data debit is roughly **8 credits** if every bounded row/page is returned; actual account deltas are authoritative. The **30-credit ceiling** (3% of the user-reported original trial balance) includes diagnostic uncertainty and optional detail/MCP checks, not 30 additional credits. The client must reserve known next-call cost, stop on unexpected debits or unknown billable operations, and report an uncertain timeout instead of repeating it. This is a plan, not an already enforced remote billing guarantee.

No initial full-symbol universe, detailed announcement lists, attachment/transcript downloads, concalls, AI summaries/batches, alerts, WebSockets, broad searches or event backfill. These either consume more budget or have unresolved trial access. An announcement is already useful event evidence for this pass.

### Outputs and exit gate

Produce a non-secret summary: actual HTTP/MCP access, native tool availability if discovered, request counts/credit delta, fields/units/basis, earliest/latest returned periods, source links and missing/forbidden cases. For each company check a few disclosed numeric values against an original filing when available; a successful API response does not independently verify them. Provider news sentiment is a text label, not comprehensive investor sentiment.

Keep raw responses privately with explicit expiry; reuse already downloaded responses to inspect schemas/values instead of calling again. Do not store a maintained corpus or commit credentials/account records/signed links. Stop and review the first company's results before proceeding to the second. Existing Free/trial keys support bounded checks. BharatStock Starter + Drishti Starter is the later paid starting recommendation; BharatStock Developer/native MCP is not required.

## Proposed next diagnostic after architecture refinement

**Not executed or scheduled by the 9 October planning update.** At most **24 initiated Drishti HTTP requests / 15 observed credits**, no BharatStock Free MCP call, purchase, retry or automatic pagination. Reuse the 25-function snapshot; refresh only the native catalog and selected schemas needed for the pass. Use the official SDK and serialize/atomically record all accounting. Include initialization/notification, implicit catalog, GET stream, DELETE cleanup, usage reads and any source redirects in the ceiling; reserve cleanup/final-accounting slots before data calls.

The purpose is to validate the first profile and its first extension, rather than repeat the earnings comparison:

| Selected operation | Bounded shape | Published estimate / evidence question |
| --- | --- | --- |
| `resolve_symbols` | One known company name | 1 credit; candidate identity matches |
| `get_symbols` | Typed query for one selected symbol | 1; exchange/ISIN/scrip and typed filter behavior |
| `list_earnings` | One symbol, explicit 365-day discovery window, one page, at most two summaries | 2; valid fiscal IDs, latest period and source fields |
| `get_news` | One symbol, seven days, one page, at most two items | 1; timestamps, source URLs and sentiment labels |
| `get_announcements` | One symbol, 30 days, one page, at most two summary items | 1; ingestion dates and actual citation fields; no detailed extraction |
| `get_announcement_categories` | At most once if needed to interpret/filter records | 0 published; still count the request and measure usage |
| `get_concalls` | One symbol, explicit 365-day discovery window, one page, at most one summary; full transcript off | 2; trial entitlement, commentary and citation shape |
| `search_concalls` | One symbol, one topic, `LAST`, one quarter, page 1, at most two hits, relaxed matches off | 2; semantic excerpts, observed cost and source locators; keep described mode `auto` |

The published core estimate is **10 credits**, leaving up to five credits of headroom within the ceiling; costs/access/output behavior are not yet measured for these shapes. Begin with RELIANCE and review results before any TCS comparison. Do not rerun all eight operations for TCS. Only make a selected comparison if the request/credit ledger still reserves accounting/cleanup headroom. Do not re-execute earnings detail just to reproduce saved values.

Optional evidence check: use the already observed canonical earnings ID with `GET /v1/earnings/citations/{earnings_id}/pdf` on `https://developers.manasija.in`, header authentication only. First review its documented billing, redirect/access path and bounded transfer plan; skip if cost cannot be bounded. At most one resolver request and one permitted document transfer inside the same 24-request/15-credit ceiling. Do not fetch the stored key-bearing citation URL. Do not forward authentication to a different redirect host or expose signed/credential-bearing URLs. Use a separate explicit PDF size ceiling, temporary private storage and expiry; document-transfer bytes are not the gateway's 2 MiB tool-result limit. Confirm issuer/period/basis/metric definition before using the original to assess the normalized/raw revenue discrepancy. A retrieved file alone is not a verified claim. Page-citation calls are outside this pass unless separately planned.

If the source cannot be resolved safely, preserve the discrepancy as unresolved. `get_events` fallback testing, unknown-priced operations, full transcripts, broader searches and market-wide tools are later separately budgeted checks. A denied call/search entitlement is a recorded outcome; do not repeat it through REST to bypass the gate. Stop on unexpected charge, quota/access failure or uncertain data-call outcome and reconcile before proceeding. The 986-credit snapshot is historical; read current allowance without publishing account payloads.

Before any future execution, translate this proposal into a concrete ordered ledger with selected arguments, known costs, permitted transfer size and remaining cleanup slots. It is not a currently runnable client or automatic batch. Sanitization, nested admission and pacing proposed in the [architecture](design/mcp-aggregation.md) must precede forwarding live results through Margin.

The next BharatStock follow-up is at most **six initiated REST requests**, reduced further by available daily quota: one stock-search and one bounded corporate-actions request for each of RELIANCE/TCS (four core requests), with two reserved only for a specific contract gap. Reuse saved snapshots/financials/prices/ratios rather than rerunning the original pass. Use reviewed REST query parameters, header authentication, disabled retries/automatic redirects and the 2 MiB cap. Confirm actual covered history; Free can silently clamp it. Search/actions are still untested shapes. Do not call MCP authorization, initialization or catalog endpoints. Count every REST attempt, including failures, and reconcile other key use before execution. The [delivery plan](plan.md) caps the combined future Drishti diagnostic/bridge/host pilot at 50 credits and the later expanded study at 500 including that pilot; no purchase or execution is implied.

## Required subscriptions and credentials

The following provider pricing/access recommendation was last checked **9 October**, not refreshed by the 20 October core/workbench planning update. Confirm current terms, prices and account state before a later purchase/live run.

Start with the supplied BharatStock Free / Drishti trial keys for bounded tests. When paid history/quota is needed, the starting recommendation is **monthly BharatStock Starter** (₹600/month, 3,000 requests/day) and **monthly Drishti Starter** (₹2,000/month): **₹2,600/month plus applicable tax/charges**, rechecked 9 October. No subscription is purchased by this document. The previous ₹3,000 Developer/Starter recommendation applied to the superseded two-native-MCP design.

- BharatStock REST exposes all endpoint families on Free, with shorter history/25 requests per day; Starter adds paid history and quota. Developer is optional for 10,000/day or native MCP, which this architecture does not require. Source: [pricing](https://bharatstockapi.com/#pricing), [MCP reference](https://bharatstockapi.com/reference#mcp-server).
- Drishti Sandbox can evaluate selected core products with one-off trial credits, but the paid Starter is recommended for the full catalog including conference calls. Its published REST allowance is 60/min and 60,000/day, with 10,000 credits per billing cycle; verify the actual MCP product access and limiter separately. Source: [pricing](https://drishti.manasija.in/docs/pricing).
- No hosted Margin server, trading/broker subscription or LLM API subscription is required to test these endpoints. A real-model host demonstration follows later.

After activation, create keys from the provider dashboards. Copy the blank template locally:

```sh
cp .env.example .env
```

Fill `BHARATSTOCK_API_KEY` and `DRISHTI_API_KEY` in `.env`. Check that `.env` remains ignored:

```sh
git check-ignore .env
```

Do not paste keys into chat, command output or committed host configs. `.env` is not automatically loaded by SDKs/terminals; the eventual test client must explicitly read these names or receive environment variables. Do not reuse an old editable `margin` installation as evidence that the new branch has a working server. Existing ignored local virtual environments were not removed in the branch cleanup.

## Run order and bounded budget

### 1. Public/no-key preflight: completed

Fetch public plan/status/schema routes and check unauthorized responses on representative protected endpoints. Use verified TLS, a 20-second request timeout, 2 MiB result cap, sequential requests and no automatic retries. A 401 is expected in the no-key case; it does not mean the provider is unusable.

The public pass used 14 requests and is recorded in the research note. It established connectivity, schema availability and authentication barriers. It did not retrieve paid data, access a live catalog or spend account credits; later authenticated results are recorded separately.

One reproducible public check, requiring only curl:

```sh
curl --fail --show-error --max-time 20 --max-filesize 2097152 https://bharatstockapi.com/v1/plans
```

### 2. Authentication and accounting: BharatStock REST and Drishti MCP

Before new live tests, establish remaining allowances and selected operation access. Existing keys already validate BharatStock REST and one Drishti MCP data operation:

| Provider | Selected path / accounting | MCP checks |
| --- | --- | --- |
| BharatStock | Direct reviewed `/v1/...` GET with `X-API-Key`; inspect remaining quota through authoritative available account/dashboard evidence and local request accounting | None; no MCP authorization, lifecycle or catalog dependency |
| Drishti | `GET /v1/account`, `/v1/account/limits`, `/v1/account/usage` with `X-API-Key` | Initialize `https://mcp.drishti.manasija.in` with Bearer key; negotiate protocol; fetch bounded `tools/list` pages |

Record eligible products, effective limits and starting credits. For Drishti record server/protocol/catalog hashes; for BharatStock record the reviewed REST schema/version and route mapping. Store account payloads privately; publish only non-sensitive conclusions. If account data cannot distinguish charges, use the user's dashboard/ledger. Do not assume control-plane or discovery traffic is free without evidence.

Use the official MCP SDK for authenticated transport/session handling, including lifecycle/cancellation/cleanup; pin a tested version when introducing a repeatable client. Trial SDK 2.2.0 uses Python snake_case model attributes (`server_info`, `protocol_version`, `input_schema`, `next_cursor`). Do not assume older examples match. Drishti's npm CLI configures a remote connection; it is optional for a direct SDK client. BharatStock uses a direct bounded async HTTP client, with retries and automatic redirects off; its npm/hosted MCP mode is unused. Use SDK-managed sessions for Drishti. No gateway needs implementation to test upstreams directly. In core tests preserve sanitized REST JSON and Drishti native fields inside the transport-independent result. HTTP/UI views use that result; later MCP tests cover `provider_payload`, JSON TextContent mirroring and native schema fidelity. Price history permits up to 300 rows for one company/year; news/filing lists remain capped separately at 20 and these focused trials use smaller limits.

### 3. Two-company data smoke: REST sample and one Drishti MCP earnings execution completed

Start with RELIANCE and TCS, after confirming identity. Use one page per call, small explicit limits and a fixed 30-day window. Test ordinary summary data first; defer detail/attachments until support is needed.

| Question | Margin REST-backed BharatStock tools | Drishti nested MCP operations |
| --- | --- | --- |
| Correct company/listing? | `search_stocks`, `get_stock_quote` | `resolve_symbols`, `get_symbols` |
| Numerical performance? | `get_financials` quarterly/annual, `get_stock_fundamentals` | `list_earnings`, `get_earnings_filing` for an actually discovered quarter |
| What happened recently? | `get_corporate_actions`, bounded `get_stock_prices` | `get_news`, `get_announcements`, `get_events` |
| What is management saying? | Financial inputs already obtained | `get_concalls`, one targeted `search_concalls` |

Those are documented candidate operation names. Drishti's actual four-tool catalog requires operation discovery/description and execution through `execute_tool`; one earnings-detail execution is complete, while other native data executions remain pending. Construct arguments from the described operation schema; do not invent MCP date/filter parameters from REST. Pick fiscal-quarter keys from returned earnings/call metadata rather than guessing. Define BharatStock local MCP schemas against reviewed REST parameters; hosted native schemas are neither used nor required. The `get_events` row is a later held candidate, not part of the initial profile.

For the next focused comparison, prefer an operation with a specific unresolved question: transcript search for MCP-only semantic discovery, or earnings detail for numerical/source evidence. Describe before executing and measure the wrapper/operation debit separately. Check timestamp semantics and actual original-source locators; REST announcement detail deliberately omits attachment URLs, so more detail is not a guaranteed PDF-access fix. See the [surface comparison](research/mcp-provider-feasibility.md#capability-comparison-and-research-derived-from-the-pairing).

The refined **50-credit prospective pilot** includes the focused 15-credit diagnostic and later bridge/host checks; it is not an additional allowance or a 50-call unattended smoke. Allocate each run explicitly using the prospective diagnostic above and the [delivery plan](plan.md). Local estimates are not an enforced remote billing guarantee. Inspect usage after each new billable tool shape; stop if measured cost is unexpected or the account/product rejects access. An uncertain timeout is not permission to repeat a possibly billed call. No deliberate quota exhaustion or automatic page walking.

### 4. Selective REST/MCP comparison: earnings pair observed; other shapes pending

BharatStock REST is the primary path. Use Drishti REST only to diagnose a specific difference or explicitly resolve evidence, not to duplicate every MCP fetch. Exact origins: BharatStock `https://bharatstockapi.com`; Drishti `https://developers.manasija.in`. Paths below include `/v1`; authenticate with headers, never keys in query strings.

| Data | REST route and bounded arguments |
| --- | --- |
| BharatStock identity/snapshot | `GET /v1/stocks/{ticker}`; verify exchange/ISIN |
| Statements | `GET /v1/stocks/{ticker}/financials?period_type=quarterly&page_size=2`; separate annual call only if needed |
| Prices | `GET /v1/stocks/{ticker}/prices` with `from`, `to`, `page=1`, `page_size=10` |
| Ratios/ownership/actions | `GET /v1/stocks/{ticker}/ratios`, `/shareholding`, `/corporate-actions`; bounded list parameters where supported |
| Drishti news/announcements | `GET /v1/news`, `/v1/announcements` with one symbol, date bounds, `page=1`, `limit=1`; announcements summary mode |
| Earnings | `GET /v1/earnings/index` or `/v1/earnings` for discovery; `/v1/earnings/detail` for returned symbol/quarter |
| Conference calls | `GET /v1/concalls` with one symbol and `limit=1`; `/v1/concalls/detail` by returned canonical ID |
| Source evidence | On demand: `/v1/earnings/attachments`, earnings PDF/page citation routes, `/v1/concalls/transcript`; these can add charges |

REST list billing can be per item while MCP billing is per tool, so always account for the difference. Drishti has no general `/v1/events` or transcript-search REST route in the inspected schema: test these through their MCP tools. Expiring/signed URLs and authenticated citation routes need safe resolution; do not embed API keys in public citations.

### 5. Wider coverage, quality and costs: pending

Verify identity/ISIN/exchange across sources; raw field names; currency/scale; reporting basis; quarter versus annual duration; actual earliest/latest returned dates; nullable fields; pagination; timestamp precision/timezone; original sources versus provider-generated summaries. BharatStock documentation has a units inconsistency that needs actual payload/filing comparison before normalization.

Compare a few values against original filings where legally accessible. Provider agreement alone is not independent verification. News tone, management outlook and price response remain separate signals; event/price coincidence is not evidence of causality. Empty results can mean no event, missing coverage or restricted history—classify only what the response supports.

After the two-company pass succeeds, use the design's 12-company panel, including banks, a verified BSE-exclusive company and an NSE SME company. The **500-credit expanded evaluation budget** includes the smoke pass; it is not 500 additional credits by default. Record calls/observed debit, latency, returned coverage and financial/evidence correctness before deciding on an upgrade.

## Evidence and completion

Record date/time, endpoint or tool name, credential tier (no key/account identifier), query window, schema/server version, HTTP/MCP status, latency, result counts/date range, units/basis, truncation/missing cases, source-link depth and measured credit change. Keep raw responses privately in ignored `reports/private/` or a temporary directory with explicit expiry. Do not commit licensed financial datasets, personal account responses, keys or presigned links.

This phase is complete when both accounts authenticate, representative BharatStock REST and Drishti MCP operations return bounded numeric and event data, charge deltas are understood, units/coverage/evidence gaps are documented and failure cases are reproducible. These are gates for a full live-source claim. The core/workbench can be built earlier against reviewed contracts and synthetic REST/MCP upstreams, with admission/sanitization/idempotency tested before live use. Margin MCP packaging follows the core/workbench gate. Passing endpoint probes is not a delivered Margin server or verified research answer.
