# BharatStock and Drishti: MCP access, endpoints and coverage

Research checkpoints: **8–9 October 2026**. Purpose: establish the evidence behind the [aggregation design](../design/mcp-aggregation.md). This is a dated investigation, not an implemented adapter or a full-market coverage report. Trial accounts now authenticate; no paid purchase has been observed. The [first authenticated trial](#authenticated-trial-results-8-october-2026) supersedes earlier no-key observations; the [operation comparison](#authenticated-operation-discovery-and-rest-comparison-9-october-2026) adds selected live schemas, execution and source-link evidence.

**Current decision:** use BharatStock REST + Drishti MCP behind Margin's MCP interface. Earlier Developer/Starter and two-native-MCP recommendations below are retained as dated research history, not current build requirements. See the [transport correction](#transport-decision-correction-9-october-2026) and current [architecture](../design/mcp-aggregation.md).

**Delivery-order update, 20 October:** build reusable core services and a local workbench first; Margin MCP packaging is deferred. Provider transport choice is unchanged. See the [active architecture](../design/core-workbench.md); the historical source evidence below remains unchanged.

## Method and observations

Read the supplied five-page *Margin MCP* PDF, official provider guides/pricing/references, current MCP specifications and SDK/proxy documentation. Downloaded public OpenAPI schemas and public npm archives into a temporary research directory; inspected source **without installing or executing those packages**. Queried BharatStock's explicitly public status, plan and attribution endpoints. Sent bounded unauthenticated MCP initialization requests to both published URLs, then notification/catalog requests to BharatStock. No API keys, authenticated data calls, upstream financial extractions, purchases or provider outreach occurred.

The first download attempt failed because the system Python's TLS certificate chain was unavailable. Retrying with system `curl` and TLS verification intact succeeded; this was a local research-client issue, not a provider download failure. Browser extraction of the JSON schema URLs failed, but direct HTTPS downloads succeeded. Do not disable TLS verification as a remedy.

| Artifact/check | Observed result | Limit of evidence |
| --- | --- | --- |
| BharatStock REST OpenAPI | HTTPS JSON download, 112,940 bytes, OpenAPI 3.1.0 | Schema descriptions/examples are not financial observations |
| Drishti REST OpenAPI | HTTPS JSON download, 145,935 bytes, OpenAPI 3.1.0 | Guide labels it 3.0.1; downloaded artifact declares 3.1.0 and does not include every MCP-only operation |
| `bharatstock-mcp` npm archive | Latest registry version 0.1.2; inspected 31 tool registrations and SDK calls | Does not establish the hosted catalog is identical |
| `drishti-mcp` npm archive | Latest registry version 0.1.4; installer writes hosted URL/Bearer configurations | Contains no hosted MCP tool implementation/schema |
| BharatStock `GET /v1/plans` | Free 25/day; Starter 3,000; Developer 10,000; Pro 50,000, with prices below | Public current plan metadata, not our account's counters |
| BharatStock `GET /v1/status` | Operational, 43/43 provider checks passing; provider `last_verified=2026-10-07T16:45:57.057758+00:00` | Self-reported internal checks, no independent financial validation |
| BharatStock `GET /v1/data-sources` | Public dataset-origin register downloaded | Dataset-level attribution, not a source page for each financial cell |
| BharatStock MCP `initialize` | HTTP 200; server name `bharatstock`, version `0.1.0`; negotiated `2025-06-18` from a `2025-11-25` proposal; tools capability | Initialization alone is not authentication/data entitlement; differs from npm version |
| BharatStock initialized notification / `tools/list` | HTTP 202 / HTTP 401; JSON-RPC error `-32001`, missing-key message | No hosted catalog obtained; no data tools called |
| Drishti MCP `initialize` | HTTP 401, `invalid_token` response | Endpoint reachable; protocol version/catalog/data remain untested |

For reproducibility, SHA-256 digests of downloaded artifacts:

- BharatStock OpenAPI: `e02d6d373786c85b4ef190893393b734744d2e7d55ef549603c186b5d19683e4`.
- Drishti OpenAPI: `b4e45c56fc3d3f853cda272518c84e9ede523c4260d508f7a964288c120f7734`.
- BharatStock MCP 0.1.2 archive: `75c3450c4a45af4d5fc3a318f8d3ca0963457e40d3dbfe70dd1de5aeb1adefb0`.
- Drishti MCP 0.1.4 archive: `6a02cb8acedda33183cd405d9114653d478b699e3a7dc14d9a70a0a5cf141d1d`.

Schemas/prices can change at the same URL. Temporary downloads are not committed source datasets; hashes identify this inspection, not an assurance that a future download will match. Authenticated coverage at that initial public-research checkpoint was **zero**; the later trial below measures two companies.

## Paid and free options

Prices are advertised INR/month, observed at research time. Do not assume GST inclusion, credit top-up prices, rollover, academic discounts or multi-user licenses. No annual commitment is recommended before feasibility tests.

| Provider/plan | Monthly price | Published request allowance | History / MCP relevance |
| --- | ---: | --- | --- |
| BharatStock Free | ₹0 | 25/day/key | Recent one-year time series, two years for annual financials per reference; no native MCP entitlement |
| BharatStock Starter | ₹600 | 3,000/day/key | Paid history; no native MCP entitlement |
| BharatStock Developer | ₹1,000 | 10,000/day/key | Native MCP eligible; recommended first paid plan |
| BharatStock Pro | ₹7,500 | 50,000/day/key | Native MCP eligible; more quota, not an established need for this team |
| Drishti Sandbox | ₹0 | REST 10/min, 1,000/day plan-wide | 1,000 trial credits once; selected core products, no WebSocket; not a renewable monthly free budget |
| Drishti Starter | ₹2,000 | REST 60/min, 60,000/day plan-wide | 10,000 credits/billing cycle; full REST catalog; recommended first paid plan |
| Drishti Pro | ₹10,000 | REST 180/min, 180,000/day plan-wide | 50,000 credits/billing cycle |
| Drishti Enterprise | Custom | Custom | Agreement-dependent full-market access; older Scale account identifiers may persist |

BharatStock pricing/rates were also confirmed against its unauthenticated [plan register](https://bharatstockapi.com/v1/plans). Its [pricing page](https://bharatstockapi.com/#pricing) and [reference](https://bharatstockapi.com/reference#rate-limits) describe the entitlement gate and history. Drishti publishes both plan and call-cost tables in [pricing](https://drishti.manasija.in/docs/pricing).

Recommended total: **₹3,000/month** for Developer + Starter. Developer + Sandbox is a ₹1,000/month feasibility alternative, but trial exhaustion and conference-call/event MCP entitlements must be checked. Developer + Drishti Pro is ₹11,000/month; both Pro plans total ₹17,500/month. Upgrade Drishti first only if measured credits/throughput justify it; raising BharatStock's quota will not remedy a Drishti credit shortage. Two cycles of the recommended pairing cost ₹6,000 before any taxes/extra charges. No server-hosting fee is required for the initial local gateway.

### Rate limits are different kinds of bounds

BharatStock documents a per-key UTC calendar-day reset, i.e. **05:30 IST**. Its MCP guide says the underlying plan's limits/history also apply to MCP. No public per-minute allowance was established. Do not invent one or call its EOD service a live-tick feed.

Drishti's published RPM/daily figures are explicitly **REST plan-wide** limits. MCP has its own tool-credit table but no independently specified MCP RPM table in the material inspected. Use REST figures as conservative planning inputs, not confirmed MCP ceilings. Account/key/product restrictions may reduce access, and the reset timezone for Drishti's daily counter was not established. Confirm with actual accounts and error responses. Its [authentication guide](https://drishti.manasija.in/docs/guides/authentication) describes per-key/product restrictions; [limits/errors guidance](https://drishti.manasija.in/docs/guides/errors-rate-limits) points to authoritative account endpoints.

Effective capacity is constrained by all of: remaining source requests, per-minute admission, remaining credits, product entitlement, payload size, query windows and retrieval latency. Quotas add neither coverage nor independent source verification. Multiple developers/processes share account limits where applicable; separate API keys do not necessarily add plan-wide capacity.

The inspected BharatStock JS SDK 0.1.11 defaults to three retries for network failures and 429s (up to four HTTP attempts). MCP handlers generally invoke one SDK endpoint/page, without automatically fetching all pages. The published HTTP wrapper checks `/v1/mcp/authorize` on requests; the hosted deployment's counting behavior remains unverified. Its tool errors stringify the SDK error into content, so HTTP retry headers/structured details may not survive the wrapper. Reserve for retries/control traffic, do not equate one Margin call with exactly one billed request, and do not automatically retry at the gateway.

## Connections and authentication

| Surface | Exact address | Credential convention |
| --- | --- | --- |
| BharatStock MCP | `https://bharatstockapi.com/v1/mcp` | Bearer API key; Developer/Pro |
| Drishti MCP | `https://mcp.drishti.manasija.in` | Bearer API key or its MCP OAuth flow |
| BharatStock REST origin | `https://bharatstockapi.com` | `X-API-Key`; paths below include `/v1` |
| Drishti REST origin | `https://developers.manasija.in` | `X-API-Key`; paths below include `/v1` |
| BharatStock schema | `https://bharatstockapi.com/openapi.json` | Public, downloaded successfully |
| Drishti schema | `https://developers.manasija.in/openapi.json` | Public, downloaded successfully |

Sources: [BharatStock MCP reference](https://bharatstockapi.com/reference#mcp-server), [Drishti MCP reference](https://drishti.manasija.in/docs/guides/drishti-mcp), [Drishti OpenAPI guide](https://drishti.manasija.in/docs/integrations/openapi-spec). Stage 1 calls MCP protocol methods; REST addresses describe underlying capabilities and optional account diagnostics, not an implemented third transport path.

## BharatStock tool-to-endpoint inventory

Exact tool names below were inspected in [npm 0.1.2](https://registry.npmjs.org/bharatstock-mcp/0.1.2); endpoint mappings were checked in the package's SDK dependency [bharatstock 0.1.11](https://registry.npmjs.org/bharatstock/0.1.11) and the public [REST schema](https://bharatstockapi.com/openapi.json). All listed routes use GET. Hosted names/schemas still require authenticated `tools/list`.

| Native MCP tool | REST path |
| --- | --- |
| `get_stock_quote` | `/v1/stocks/{ticker}` |
| `get_company_profile` | `/v1/stocks/{ticker}` (same detail response as quote) |
| `get_stock_quotes_batch` | `/v1/stocks/quotes` |
| `get_stock_prices` | `/v1/stocks/{ticker}/prices` |
| `get_financials` | `/v1/stocks/{ticker}/financials` |
| `get_stock_fundamentals` | `/v1/stocks/{ticker}/ratios` |
| `get_technical_indicators` | `/v1/stocks/{ticker}/technical-indicators` |
| `get_shareholding` | `/v1/stocks/{ticker}/shareholding` |
| `get_corporate_actions` | `/v1/stocks/{ticker}/corporate-actions` |
| `get_stock_bulk_deals` | `/v1/stocks/{ticker}/bulk-deals` |
| `get_stock_block_deals` | `/v1/stocks/{ticker}/block-deals` |
| `get_stock_insider_trades` | `/v1/stocks/{ticker}/insider-trades` |
| `compare_sector_peers` | `/v1/stocks/compare` |
| `search_stocks` | `/v1/search` |
| `get_stock_rank` | `/v1/movers` |
| `get_price_shockers` | `/v1/price-shockers` |
| `run_screener` | `/v1/screener` |
| `list_indices` | `/v1/indices` |
| `get_index_prices` | `/v1/indices/{name}/prices` |
| `get_fii_dii_activity` | `/v1/market/fii-dii` |
| `get_bulk_deals` | `/v1/deals/bulk` |
| `get_block_deals` | `/v1/deals/block` |
| `get_insider_trades` | `/v1/insider-trades` |
| `search_mutual_fund_schemes` | `/v1/mf/schemes` |
| `get_mutual_fund_scheme` | `/v1/mf/schemes/{scheme_code}` |
| `get_mutual_fund_nav` | `/v1/mf/schemes/{scheme_code}/nav` |
| `get_mutual_fund_returns` | `/v1/mf/schemes/{scheme_code}/returns` |
| `get_mutual_fund_holdings` | `/v1/stocks/{ticker}/mf-holdings` |
| `list_mutual_fund_portfolios` | `/v1/mf/portfolios` |
| `get_mutual_fund_portfolio_holdings` | `/v1/mf/portfolios/{scheme_name}/holdings` |
| `get_data_status` | `/v1/status` (public REST) |

Other schema routes relevant to investigation: `GET /v1/stocks` (paginated universe), `/v1/mcp/authorize` (authenticated eligibility), `/v1/plans`, `/v1/mf-coverage`, `/v1/data-sources` (public registers). They are not extra native tools in the inspected package. Listing the universe through REST would be an explicit diagnostic/export exercise, not a continuous Margin corpus job.

Contract details to preserve/test:

- Native MCP uses camelCase arguments such as `fromDate`, `toDate`, `periodType`, `pageSize`, `actionType`; REST uses `from`, `to`, `period_type`, `page_size`, `action_type`. Discover actual schemas rather than mixing conventions.
- Quote batching supports up to 50 symbols. The package's price page limit is 500; financial/shareholding/action page limits are 50. REST limits may be wider on other endpoints than the MCP schema permits. Never widen native schemas based on REST alone.
- `get_financials` accepts quarterly or annual cadence; separate calls can be required. Statements include P&L, newer BS fields, annual CF, segment data where present, consolidation/audit context and bank/insurance fields. Optional fields are not guaranteed populated.
- `get_company_profile` and `get_stock_quote` call the same record: don't fetch both in a research workflow. `compare_sector_peers` takes a sector, not a requested list of firms. FII/DII flow is market-wide; stock FII/DII holdings are a different dataset.
- Price adjustment covers split/bonus changes; it does not include dividend reinvestment. Technical indicators may be null until enough prior observations exist. Screener results are precomputed, not a point-in-time historical screen.
- The npm server returns JSON as text content and errors as `isError` text. The JS SDK decodes field names to camelCase. REST schema examples alone are insufficient to define Stage 2 MCP result parsers.

## Drishti tools, credits and REST relationships

Exact operation names/costs below are documented in the [MCP guide](https://drishti.manasija.in/docs/guides/drishti-mcp). **Live discovery correction:** authenticated server 3.3.1 exposes four routing tools rather than these operations directly. Treat this table as the published eighteen-operation inventory; the 9 October metadata audit additionally describes all 25 confirmed functions in the [current reference](../reference/drishti-functions.md). Only earnings detail has executed data evidence; other operation access/billing/results remain untested. A semantically corresponding REST route is **not proof** that MCP calls that route or has the same billing.

| Documented MCP operation | Published credits per call | REST relationship in inspected public schema |
| --- | ---: | --- |
| `resolve_symbols` | 1 | No exact equivalent documented; metadata lookup is not fuzzy resolution |
| `get_symbols` | 1 | `GET /v1/symbols/metadata` |
| `get_news` | 1 | `GET /v1/news` |
| `get_announcement_categories` | 0 | `GET /v1/announcements/categories` |
| `get_announcements` | 1; detailed 2 | `GET /v1/announcements` |
| `search_announcements` | 1 | No text/semantic search route in inspected REST schema |
| `get_events` | 1 | No general `/v1/events` route in inspected REST schema; don't invent it |
| `list_earnings` | 2; detailed 3 | `GET /v1/earnings`; compact `/v1/earnings/index` also exists |
| `get_earnings_filing` | 3 | `GET /v1/earnings/detail` |
| `get_concalls` | 2; detailed 3 | `GET /v1/concalls`; `/v1/concalls/detail` is separate |
| `search_concalls` | 2 | No transcript-search route in inspected REST schema |
| `get_price_and_volume_since` | 2 | No corresponding price-history REST route in inspected schema |
| `get_sectoral_data` | 1 | No corresponding sector REST route in inspected schema |
| `get_sector_wise_companies` | 1 | No corresponding peer REST route in inspected schema |
| `get_52w_data` | 2 | No corresponding 52-week REST route in inspected schema |
| `get_top_movers` | 1 | No corresponding movers REST route in inspected schema |
| `get_top_traded` | 1 | No corresponding top-traded REST route in inspected schema |
| `get_daily_summary` | 1 | REST `POST /v1/daily-summary/` generates a portfolio summary; do not equate it with the MCP daily-digest fetch |

The [coding guide](https://drishti.manasija.in/docs/guides/build-with-drishti-mcp) additionally names `get_upcoming_concalls` (cost not in the inspected MCP pricing table), documentation tools `search_docs`, `get_doc`, `read_me`, five prompt-helper tools (`get_default_system_prompt`, `get_company_research_prompt`, `get_earnings_concall_prompt`, `get_market_development_prompt`, `get_subagent_prompt`) and instruction resources. These descriptions do not establish an exhaustive or immutable live catalog. Don't assume unlisted costs are zero. Do not include unrelated docs/prompt helpers in the default market profile without a reason.

### Exact REST support routes and limits

The public [OpenAPI document](https://developers.manasija.in/openapi.json) establishes these routes. The authenticated trial below tests metadata, news, announcements, earnings summaries and account diagnostics; other routes remain untested:

| Capability | Exact REST endpoint(s) | Relevant bounds/evidence |
| --- | --- | --- |
| News/filings | `GET /v1/news`, `/v1/announcements`, `/v1/announcements/categories` | Symbol/scrip filters, dates, page/limit; news sentiment filter; announcements support category/importance/detail |
| Company metadata | `GET /v1/symbols/metadata` | Up to 20 symbols or scrip codes/request; full-universe use has separate paid access/cost |
| Earnings discovery | `GET /v1/earnings/index`, `/v1/earnings`, `/v1/earnings/upcoming` | IDs, symbol/scrip, date and fiscal quarter filters where supported; latest record for each symbol/quarter is not a full revision archive |
| Earnings detail/links | `GET /v1/earnings/detail`, `/v1/earnings/attachments` | Detail uses symbol or scrip code plus `quarter`; attachments uses returned IDs, resolved on demand |
| Earnings citations | `GET /v1/earnings/citations/{earnings_id}/pdf`, `/v1/earnings/citations/{earnings_id}/page/{page}` | Authenticated redirects; 1-indexed page locator, docs relate it to `budget_pages`; actual page support/browser auth must be verified |
| Conference calls | `GET /v1/concalls/index`, `/v1/concalls`, `/v1/concalls/upcoming`, `/v1/concalls/detail` | Canonical ID preferred for special/non-quarterly calls; fiscal key such as `q4_26` must be interpreted rather than guessed |
| Transcript links | `GET /v1/concalls/transcript`, `POST /v1/concalls/transcripts`, `GET /v1/concalls/citations/{concall_id}/pdf` | Transcript/audio links may be presigned and expire; availability is separate from analysis/summary |
| Alerts/deals | `GET /v1/alerts`, `/v1/block-deals` | Structured deal prints; alerts are curated product signals, not an exhaustive market-event feed |
| Account diagnostics | `GET /v1/account`, `/v1/account/limits`, `/v1/account/usage`, `/v1/account/ledger` | Access, effective limits, balance/counters, charge history; server-side control plane if needed, not LLM-visible account data |
| Addon configuration | `GET /v1/account/announcement-addon`, `PUT /v1/account/announcement-addon/categories` | Configuration mutation; not a default Stage 1 forwarded capability |
| AI batch workflows | `POST/GET /v1/batch/jobs`, `GET/DELETE /v1/batch/jobs/{job_id}`, `GET /v1/batch/jobs/{job_id}/results`, `POST /v1/daily-summary/` | Generation/batch/mutation costs and lifecycle; outside initial aggregation |

Typical REST list routes limit symbol/scrip filters to 20 and pages to 50 rows; metadata batches also cap at 20. The [pagination guide](https://drishti.manasija.in/docs/guides/pagination-filtering) describes `data`/`has_next`, narrow date windows and more costly detail mode. These are REST limits; do not assume identical Drishti MCP arguments. Dates can be ISO datetimes; some example timestamps lack an offset, so the normalizer must not silently assign a timezone.

Important REST-versus-MCP cost differences from published pricing: news REST is one credit per non-empty page; announcement/earnings/concall lists charge **per returned item**, with higher detail rates. REST earnings detail costs three, delivered transcript/audio links four per ready item, alerts five per non-empty page, metadata one per returned item, and full universe 50 for a non-empty response with the required access. Citation PDF routes' schema descriptions mention one credit after resolving a source; verify the specific page-route debit separately. MCP costs above are the published per-tool table. Filling in a missing MCP feature through REST can radically change costs; it must be an explicit choice.

An authenticated API citation URL is not automatically a clickable citation for a host/browser: do not put `api_key` in a returned URL. Prefer an available original public source URL, or a safely resolved expiring link with explicit expiry/access limits. A provider-generated earnings table, summary or sentiment block is not an independently reviewed extraction.

### Capability comparison and research derived from the pairing

Follow-up public-documentation/package review on **8 October 2026**; no additional authenticated requests or trial credits were used. The operation table above is the complete eighteen-operation market list on the inspected MCP guide, with a nineteenth candidate (`get_upcoming_concalls`) in the coding guide. Only the four routing tools in the trial catalog below are observed native tools. An operation's presence in a guide does not establish current schema, access, completeness or execution cost through those wrappers.

| Research task proposed for Margin | Drishti candidate operations | Additional inputs / limits |
| --- | --- | --- |
| Company identity and research routing | `resolve_symbols`, `get_symbols` | Match exchange/ISIN with BharatStock; fuzzy matches need disambiguation |
| Dated company-development timeline | `get_news`, `get_announcements`, `search_announcements`, `get_events` | Bound dates/categories; distinguish ingestion, publication and effective dates; deduplicate overlapping reports |
| Earnings brief with context | `list_earnings`, `get_earnings_filing`, `get_concalls` | BharatStock supplies multi-period numerical inputs; detailed earnings may corroborate selected figures, with units/basis checked |
| Topic research across filings/calls | `search_announcements`, `search_concalls` | Search for capex, orders, exports or regulatory issues; retrieve supporting text/source before treating a hit as evidence |
| Guidance follow-through | `get_concalls`, `search_concalls`, `get_earnings_filing` | Compare dated management claims with later compatible financial periods; guidance and provider interpretation remain distinct |
| Upcoming catalysts | `get_events`, documented `get_upcoming_concalls` | REST also has earnings/concall upcoming lists; event calendars are incomplete until measured |
| Sector/peer context | `get_sectoral_data`, `get_sector_wise_companies` | Combine compatible BharatStock ratios/financials for comparisons; a peer list alone provides no valuation conclusion |
| Price/volume context around developments | `get_price_and_volume_since`, `get_52w_data` | BharatStock OHLCV/indices/actions can supply benchmark and adjustment inputs; descriptive association requires valid publication times, not ingestion timestamps |
| Market discovery and daily overview | `get_top_movers`, `get_top_traded`, `get_daily_summary` | Date/as-of time and coverage must be known; digest fetch is different from generating a personalized portfolio report |
| Sentiment context | News labels, concall guidance/risk/sentiment blocks; price/volume operations | Press tone, management outlook and market reaction are separate signals, not a comprehensive measure of retail/social/investor sentiment |

These are proposed combinations for the user's model to reason over, not delivered Margin tools or independently validated analyses. No persistent corpus is necessary: retrieve a bounded response on demand, preserve provenance in the response, and keep only permitted temporary evaluation receipts.

Drishti's MCP is **not a one-to-one REST facade**:

- Shared families include identity metadata, news, announcements, earnings and conference calls. REST detail already offers financial tables, guidance, risks and sentiment analysis; those are not uniquely MCP features. The [earnings-detail guide](https://drishti.manasija.in/docs/api-reference/earnings/get-one-earnings-filing) describes expanded extraction, and the [concall-detail guide](https://drishti.manasija.in/docs/api-reference/conference-calls/get-one-conference-call) includes management guidance, risk commentary and transcript links.
- MCP documents semantic announcement/transcript search, fuzzy company resolution, corporate-event retrieval, sector/peer context and market-discovery/price operations with **no matching route in the inspected public REST schema**. This is a documentation-surface difference, not proof that private/internal API routes do not exist. Search semantics, source granularity and limits still require operation descriptions and real results.
- REST additionally documents direct attachment/citation resolution, compact indexes, upcoming earnings/calls, alerts/deals, account usage/ledger, batch generation and addon configuration. These are not all represented in the public MCP operation list. They do not automatically belong in the initial read-only gateway; an evidence adapter would be a separately selected capability if MCP cannot supply source locators.
- Python/TypeScript SDKs provide code-level REST control and separate WebSocket support, rather than adding MCP-only semantic search merely by installing an SDK. See the [Python SDK](https://drishti.manasija.in/docs/sdks/python) and [TypeScript SDK](https://drishti.manasija.in/docs/sdks/typescript). A hosted MCP connection is not a WebSocket market subscription.
- Billing differs by surface. For illustration, REST metadata for two returned firms is two credits versus the published one-credit MCP operation; ten summary REST announcement items cost ten versus a published one-credit MCP call **if** its supported result shape returns those items. Conversely, a one-item REST earnings summary is one credit versus published two for `list_earnings`. These are conditional pricing comparisons, not measured savings: result bounds, wrapper costs, entitlements and actual debits are pending. Do not conclude MCP is always cheaper.

BharatStock's inspected MCP package is a **thin wrapper around the same REST datasets**, rather than an additional research engine:

| Contract | REST | Inspected MCP 0.1.2 / JS SDK 0.1.11 |
| --- | --- | --- |
| Coverage | 35 distinct public schema paths, including control/public registers | 31 tools mapping to 30 distinct routes; quote/profile duplicate the same stock endpoint; five REST paths are unwrapped |
| Authentication/access | `X-API-Key`; Free/Starter can use REST within their plan | Hosted Bearer key or local environment key; Developer/Pro eligibility applies to both native modes |
| Arguments | `period_type`, `page_size`, `from`, `to`, `action_type` | `periodType`, `pageSize`, `fromDate`, `toDate`, `actionType` |
| Result envelope | JSON with snake_case fields; paged data has nested `pagination` | SDK recursively converts keys to camelCase and flattens pagination to `page`, `pageSize`, `totalItems`, `totalPages`; MCP serializes that JSON into text content |
| Page limits | Prices max 1,000; financials max 100 | Prices max 500; financials max 50; native schema is the applicable contract |
| Execution | Caller controls HTTP/paging/retry | One SDK endpoint/page per handler; no automatic all-page iteration; SDK can make up to four attempts on network failures/429s |
| Errors/control traffic | HTTP status/headers available to caller | Tool errors become `isError` text; local startup authorizes access, and published HTTP wrapper authorizes requests; hosted counting is not established |

Source basis: [MCP/reference](https://bharatstockapi.com/reference#mcp-server), [public REST schema](https://bharatstockapi.com/openapi.json), and the versioned npm artifacts linked in the inventory. Local npm stdio requires Node; remote hosted HTTP does not require the caller to install npm. The inspected package and observed unauthenticated hosted version differ, so package contracts are not yet authenticated hosted contracts. CamelCase conversion does not repair numeric units, null fields, stale quarters or missing per-cell citations. No separate MCP-owned financial dataset or semantic transcript-search engine was found in that package.

### Timestamp and source-link corrections

The [announcement REST guide](https://drishti.manasija.in/docs/api-reference/announcements/list-announcements) explicitly identifies `date` as **ingestion time** and says REST/WebSocket payloads omit attachment URLs, title/headline/descriptor fields and internal storage keys. Detail adds summary/extracted information, not an automatic original-filing URL. Earnings/concall detail guides also define `date` as ingestion time. Earlier trial wording that called earnings dates “filed” was too strong and is corrected below. Do not infer announcement publication time, exchange latency or event-day price reaction from those timestamps.

Original-source evidence needs separate evaluation. REST earnings attachments and earnings/concall citation routes can resolve source locators where available; an announcement citation route is not present in the inspected schema. MCP source-link behavior is untested. The [earnings PDF citation guide](https://drishti.manasija.in/docs/api-reference/earnings/open-earnings-pdf-citation) describes stored-source resolution with original-source fallback; that is not claim verification or guaranteed perpetual public access. Provider images and generated commentary remain different evidence types from an issuer PDF or transcript page.

There is also documentation drift within REST: the concall-detail prose emphasizes symbol/quarter, while the downloaded OpenAPI accepts canonical `id` as well. Use the actual inspected schema when constructing a diagnostic, and record any provider rejection rather than assuming prose, SDK and MCP contracts are identical.

## Expected numeric and event coverage

BharatStock advertises 5,000+ stocks, 11+ years of price history, broad NSE/BSE categories and 72 screener metrics. This is **addressable advertised coverage**, not 5,000 fully populated research profiles. Its reference explains that `data_coverage` flags describe what a pipeline can populate rather than checking actual non-null rows. Its FAQ/reference also warn of missing SME/micro-cap financials, incomplete classifications, newer integrated BS availability and annual CF cadence. Drishti documents rich event/call/news tools but no fixed universe/history-depth guarantee was established in this investigation.

The joint research population is the measured intersection for a task, not the union of two marketing universes. Useful overlap includes company identity, earnings versus financial statements, price/volume and actions versus announcements. Compare the same company, exchange, period, consolidation basis, units and update time; never silently average discrepancies. Shared original filings mean agreement may not be independent.

**Units require an early check:** BharatStock's homepage says statement values use absolute INR; screener market cap and market-wide FII/DII flow use crores. The reference's Reliance financial example contains values that appear crore-scaled relative to the claimed statement convention. That appearance is an inference, not a measured API defect. Drishti earnings examples have field-level units such as `Rs crore`. Preserve raw values/units and verify paid payloads against issuer filings before any global conversion. The REST schema's optional numeric fields alone cannot resolve this discrepancy.

What the pairing can plausibly support: dated numeric company snapshots, financial trend inputs, screens, ownership/actions, news/filing discovery, earnings commentary and topic search of transcripts. What remains unproven: universal BSE/SME coverage, exact historical event retention, intraday/full order-book data, dividend-reinvested returns, historic point-in-time revisions, comprehensive social/investor sentiment and cell-level citations for every metric. News tone, management outlook, transaction observations and price reaction are separate signals. On-demand retrieval requires no maintained corpus; small evaluation receipts/fixtures still need retention permission.

## Workload arithmetic and upgrade triggers

These are **planning estimates** using documented operation credits, excluding routing-helper discovery/description, MCP lifecycle messages, retries, extra pages, attachments, account diagnostics and other users. Drishti's four-tool live catalog adds wrapper traffic with unmeasured operation billing; these are data-operation profiles, not total native HTTP counts or an implemented compound tool. Recalculate after describe/execute tests.

| Profile, one company | BharatStock native calls | Drishti data operations / documented credits |
| --- | ---: | --- |
| Lean | Quote + quarterly financials + ratios = 3 | Resolve + news + announcements = 3 calls / 3 credits |
| Full | Quote + quarterly + annual financials + ratios + prices + actions = 6 | Resolve + news + announcements + events + concalls + earnings filing = 6 calls / 9 credits |

At a **20% credit reserve**, Drishti Starter supplies 8,000 planned usable credits/cycle: at most 2,666 lean or 888 full profiles in a cycle. For an illustrative 30-day cycle, that averages about **89 lean or 30 full company researches/day**, shared by the team, not per developer. Pro supplies 40,000 usable credits: 13,333 lean or 4,444 full/cycle, about 444 or 148/day. These are upper bounds for only those profiles, not guarantees of complete responses. Trial 1,000 credits similarly gives roughly 266 lean or 88 full at reserve, only if the required products are allowed, and does not replenish daily.

BharatStock Developer's 20%-reserved daily allowance is 8,000 nominal requests. Under a nominal one-request-per-call assumption, lean/full would permit 2,666/1,333 profiles per day; that assumption needs billing verification and is not a gateway guarantee. A very conservative provisional five-request reservation per native call (entitlement traffic plus up to four SDK attempts) would reduce these to 533/266; hosted behavior could differ. In either illustration Drishti's **billing-cycle credits** constrain sustained full-profile volume first.

For the proposed 12-company panel, one full-profile pass is nominally 72 BharatStock native calls, 72 Drishti calls and 108 Drishti credits. Repeat pages, transcript search/detail, independent evidence checks and account measurements add to that; set an initial **500-credit research-test budget** with an explicit stop, rather than unrestricted source exploration. Measure actual charge deltas for each shape before projecting scale.

Upgrade only when evidence shows a problem: first trim duplicate/unused calls, default to summary results and batch where native tools support it; then consider Drishti Pro for credits/throughput. No published credit top-up price was established, so do not assume it beats a plan change. Do not buy BharatStock Pro solely because its dataset sounds larger; its extra quota is the relevant demonstrated difference here.

## Account validation and product permissions still required

Before implementation: obtain securely supplied eligible keys; initialize and collect paginated catalogs/schemas; measure one ordinary/detailed/empty/error/search call's cost; read effective account limits; verify financial units/basis and requested history; inspect returned original URLs/citation fields; test BSE-exclusive/SME cases; record negotiated versions and latency. Do not deliberately exhaust paid quotas to test a 429—simulate it locally and use naturally observed limits or a tightly restricted test key.

Before public product deployment: clarify the intended aggregated MCP use, organizational/team key access, public versus private hosting, raw-result redistribution, retention, user attribution and exchange data licensing. BharatStock's [terms](https://bharatstockapi.com/terms) restrict key sharing, re-serving/substantially raw data and competing data products, and condition retained paid data on an active subscription. Buying a Developer/Pro plan does not grant a public data-feed license. A private BYOK connector is the proposed feasibility architecture, not a blanket permission conclusion. Do not assume four people may copy a personally bound key, or that adding normalization removes source restrictions. Drishti's technical docs do not establish a redistribution entitlement; its subscription/agreement must be checked.

This research recommends plans and bounded tests. It does not authorize purchases, contact providers or assert a legal interpretation as settled. The active design requires no Margin financial warehouse and leaves the existing `d1` snapshot intact.

## Follow-up: branch cleanup and public endpoint pass

The user subsequently authorized clearing/pushing `main` and endpoint testing, and confirmed that subscriptions **have not been purchased**. `d1` at `c77963d` was pushed first; planning was committed as `be04aba`, then legacy tracked runtime/tests/examples/manifests/CI and superseded guides were removed from `main` without a reset or force-push. Current planning/research remain. Ignored local data/environments were not deleted.

A fresh sequential **14-request** preflight used system curl with TLS verification, 20-second timeouts, 2 MiB response caps and no retry. No credentials, authenticated data requests or paid tool calls were involved. Temporary raw receipts are outside Git. Results:

| Method | Exact URL | Observed HTTP/result |
| --- | --- | --- |
| GET | `https://bharatstockapi.com/v1/plans` | 200; Developer ₹1,000/month and 10,000/day, other tiers unchanged from the table above |
| GET | `https://bharatstockapi.com/v1/status` | 200; provider says operational, 43/43 passing; `last_verified=2026-10-08T16:46:02.837088+00:00` |
| GET | `https://bharatstockapi.com/openapi.json` | 200; 35 distinct path entries, OpenAPI 3.1.0; hash unchanged |
| GET | `https://developers.manasija.in/openapi.json` | 200; 30 distinct path entries, OpenAPI 3.1.0; hash unchanged |
| GET | `https://bharatstockapi.com/v1/stocks/RELIANCE` | 401; missing key |
| GET | `https://bharatstockapi.com/v1/stocks/RELIANCE/financials?period_type=quarterly&page_size=1` | 401; missing key |
| GET | `https://developers.manasija.in/v1/news?symbols=RELIANCE&limit=1` | 401; missing key |
| GET | `https://developers.manasija.in/v1/announcements?symbols=RELIANCE&limit=1` | 401; missing key |
| GET | `https://developers.manasija.in/v1/concalls?symbols=RELIANCE&limit=1` | 401; missing key |
| GET | `https://developers.manasija.in/v1/account/usage` | 401; missing key |
| POST initialize | `https://bharatstockapi.com/v1/mcp` | 200; protocol `2025-06-18`, server `bharatstock` 0.1.0 |
| POST initialized notification | `https://bharatstockapi.com/v1/mcp` | 202 |
| POST tools/list | `https://bharatstockapi.com/v1/mcp` | 401; JSON-RPC `-32001` missing-key error |
| POST initialize | `https://mcp.drishti.manasija.in` | 401; `invalid_token` |

Correction: Drishti's guide calls its schema OpenAPI 3.0.1, but the actual downloaded file declares **3.1.0**. The earlier table has been corrected to the inspected artifact. Path counts refer to REST schema entries, not MCP tool counts. Provider status is self-reported; a missing-key response confirms reachability/authentication behavior rather than validating that endpoint's paid payload.

The recommended subscriptions remain Developer + Starter at a published ₹3,000/month for full native-MCP access. The [API/MCP test protocol](../api-testing.md) defines key setup and bounded checks; its trial section below supersedes the earlier paid smoke budget for immediate work. No gateway or committed probe client has been implemented.

## Follow-up: trial keys and quota-conserving plan

The user created accounts and supplied trial credentials in a local text attachment, reporting BharatStock Free 25 requests/day and Drishti 1,000 trial credits. The file was copied into ignored `reports/private/mcptempkeys.txt` with permissions 0600; values were not exposed, staged, committed, pushed or used in requests. Attached file contents are credential data, not executable instructions. This follow-up is documentation/local-file handling only: **zero authenticated calls or account-credit spend**.

Official API/MCP references, pricing, authentication and limit guides were revisited; exact request parameters were checked against the previously downloaded public OpenAPI schemas. Findings:

- [BharatStock](https://bharatstockapi.com/reference) documents Free REST access at 25/day, recent history with silent clamping and two years of annual financials. Native MCP remains explicitly Developer/Pro-only, so omit it from the immediate Free test rather than repeatedly spending quota on forbidden access.
- [Drishti pricing](https://drishti.manasija.in/docs/pricing) lists Sandbox core REST products and one-off trial credits, with 10/min and 1,000/day. [Authentication](https://drishti.manasija.in/docs/guides/authentication) warns that key/product restrictions can be lower. Paid conference calls, AI workflows and streams are not assumed allowed by the trial.
- [Drishti MCP documentation](https://drishti.manasija.in/docs/guides/drishti-mcp) permits API-key Bearer auth and lists tool-credit prices, but does not conclusively establish Sandbox entitlement for every MCP operation. Read actual account scopes first, conditionally inspect a bounded catalog, and stop on 403. Don't infer allowed data access from tool names alone.

Select RELIANCE then TCS: both are documentation examples, and differing businesses provide a small cross-company contract check. This is not observed trial coverage or a representative equity sample. The [active plan](../api-testing.md#completed-initial-trial-before-purchasing) specifies **10 core / 12 maximum BharatStock REST requests**, **roughly 8 expected Drishti core REST data credits / 30 total ceiling**, no automatic retries/page exhaustion and at most 20 initiated Drishti requests including diagnostics/MCP messages. Actual daily quota already spent and charge deltas are unknown until checked.

Core numeric data: identity/snapshot, recent quarterly/annual statements, short EOD prices, ratios and optional ownership. Core event data: metadata, one news/announcement/earnings row per company, with an optional schema-driven MCP news comparison if permitted. Detailed earnings, calls, sources and broader coverage follow measured access; this trial does not establish a working two-native-MCP integration. No new push or authenticated execution was performed for this planning follow-up.

## Authenticated trial results: 8 October 2026

The user authorized execution after the planning checkpoint. Tested RELIANCE first and reviewed it before TCS. No gateway was implemented, purchases made or changes pushed. Keys and raw receipts are local/ignored in `reports/private/`; private one-shot diagnostics are not a delivered client on a fresh clone. Account identifiers, signed links and raw datasets must stay out of tracked documents. Review/delete temporary trial receipts and the issuer PDF by **22 October 2026**; this is a retention instruction, not an automatic deletion job. Credential deletion/rotation is separate.

### Execution and accounting

- **BharatStock: 12 authenticated REST requests, all HTTP 200**, no retries or extra pages. Exactly six per company: snapshot, quarterly financials, annual financials, prices, ratios, shareholding. Latency 0.29–2.13 seconds. No quota headers were observed. Twelve locally initiated requests do not establish remaining daily account quota; the maximum would be 13 remaining if these were its only requests that UTC day.
- **Drishti: 25 authenticated HTTP requests total**: 16 REST (7 bounded data requests and 9 account/usage checks) plus 9 SDK-managed MCP lifecycle/catalog requests across two sessions. Twenty-three returned 200 and two initialized notifications returned 202. REST latency 0.11–1.44 seconds. MCP receipt timing includes deliberate pacing/locking and is not a clean server benchmark.
- Starting balance **1,000**, ending **992**, reserved **0**, debit **8**. Observed first-shape deltas: metadata 2; one news page 1; one announcement summary 1; one earnings summary 1. TCS's three summary requests account for the other 3. Final MCP catalog session had an independently measured zero balance delta. No MCP financial/news operation was executed.
- The initial local Drishti request ceiling was 20. A local SDK attribute error interrupted the first session after initialization. After inspecting the error and usage, the repair ceiling was explicitly revised to **26 requests**, preserving the **30-credit ceiling**; actual total was 25. This was one repair of a known client error, not an automatic retry of uncertain billable data.
- Control-plane and data limits differ: `/account/limits` returned **REST 10/min, 1,000/day**, and **account 60/min, 10,000/day**. Response headers corroborated 10 for data and 60 for account routes. The earlier higher-limit observation concerned account traffic, not a higher Sandbox data allowance. Trial plan metadata was Sandbox with zero recurring cycle credits. Account product flags included concalls and AI-summary products, but their endpoints/billing were not tested; enabled flags do not prove the complete paid catalog works.
- REST used system curl, TLS verification, 25-second timeout, 2 MiB cap and credentials supplied through stdin configuration rather than process arguments. Drishti traffic was sequential and paced at least eight seconds apart. MCP used the existing local **official Python SDK 2.2.0** and its HTTP transport, with request instrumentation, no reconnect/retry allowance and bounded discovery. No global npm/client configuration was changed.

The temporary ledger initially lost two completed BharatStock shareholding entries during a concurrent SDK write. They were restored from saved successful receipts; the SDK writer was corrected to refresh the ledger after pacing. Final counts were reconciled to twelve BharatStock response files and all twenty-five Drishti requests. Future repeatable probes should serialize ledger updates or use an atomic recorder.

### Bounded endpoint matrix

Exact origins/queries are in the [trial protocol](../api-testing.md#bharatstock-sequence-10-core-requests-maximum-12-total). Price/news/announcement bounds were 9 September–8 October 2026; no page walking occurred.

| Endpoint family | RELIANCE | TCS | Interpretation |
| --- | --- | --- | --- |
| BharatStock snapshot `/v1/stocks/{ticker}` | NSE, ISIN matched | NSE, ISIN matched | Identity agrees with Drishti; latest price date 8 October |
| `/financials`, quarterly, page size 4 | 3 rows | 3 rows | Q3 FY26, Q4 FY26, Q1 FY27; 31 December 2025–30 June 2026; response total 3 |
| `/financials`, annual, page size 2 | 2 rows | 2 rows | FY25 and FY26, years ended 31 March 2025/2026; response total 2 |
| `/prices`, page size 30 | 20 rows | 20 rows | 9 September–8 October; OHLCV, adjustment factor/adjusted close; total 20 |
| `/ratios` | One object, 17 fields | One object, 17 fields | No nulls in these objects; context says annual FY26, date 8 October |
| `/shareholding`, page size 2 | 2 rows | 2 rows | 31 March/30 June 2026; total 3 across 2 pages; second page not fetched |
| Drishti `/symbols/metadata` | One record | One record | Single two-symbol request; ISIN and BSE scrip codes present |
| `/news`, limit 1 | One, dated 7 October | One, dated 7 October | Both neutral labels, publisher links, `has_next=true`; not comprehensive sentiment |
| `/announcements`, summary, limit 1 | One, ingested 7 October | One, ingested 1 October | Category/summary/image, `has_next=true`; ingestion date is not publication date; no original filing URL |
| `/earnings`, summary, limit 1 | `q1_27`, ingestion date 17 July | `q2_27`, ingestion date 8 October | Summary/image only, `has_next=true`; not independently established filing dates; no numeric table or original PDF link |

This yielded **10 financial rows, 40 price rows, 4 ownership rows, 2 company metadata rows and 6 news/filing summaries**, plus two snapshots and two ratio objects. It is a two-company contract sample, not evidence of universe/history coverage. In particular, TCS's Drishti Q2 FY27 summary precedes that quarter appearing in the BharatStock numerical response; cross-provider freshness must be checked before combining latest results.

### Extraction, units and evidence

- Financial rows have **83 keys**. Across five rows per company, Reliance has 254 populated slots / 216 scalar numeric slots; TCS 252 / 214. These counts include metadata and overlapping facts, not independently verified financial cells or a percentage of project requirements.
- Revenue, net profit, PBT, tax and EPS are populated in all ten rows. All four annual rows have balance-sheet totals, CFO/CFI/CFF, capex and segment objects. Each company's Q4 row has balance-sheet totals; its Q1/Q3 rows do not. Quarterly cash flows/capex are null in all six rows. Banking/insurance-specific keys are mostly null as expected for these issuers.
- All rows state **consolidated**, with fiscal year/quarter/end date and audit flags. Quarterly Q4 is marked audited; Q1/Q3 unaudited; annual rows audited. Do not fill missing quarterly balance sheets/cash flows with annual values. Delivery quantity/percentage are null in the sampled price data; null is not zero.
- Financial responses have no explicit unit field or per-cell original-source link. Four Reliance FY25 values were independently matched against the [issuer statement](https://www.ril.com/ar2024-25/pdf/RIL-Integrated-Annual-Report-2024-25.pdf), PDF page 100, printed pages **196–197**, with the rendered table visually inspected: revenue from operations ₹980,136 crore; profit for year ₹81,309 crore; owners' profit ₹69,648 crore; EPS ₹51.47. The API's monetary totals equal these figures times **10,000,000**, while EPS remains rupees/share. This supports absolute-INR statements for this sampled row, not a blanket unit assumption for every field.
- Reliance's API `revenue` corresponds to **revenue from operations**, after GST recovered, rather than the issuer's larger gross value-of-sales headline. Total profit and profit attributable to owners are separate. Comparisons must preserve these definitions.
- **Market-cap scale differs within the same snapshot**: root `market_cap` and `/ratios.market_cap` are 10,000,000 times `metrics.market_cap` for both companies. The nested metric is crore-scaled; the other values are rupee-scaled. Normalize by provider + JSON path, never by field name alone. Snapshot and ratio EPS/P-E/ROE/ROCE agree; both P/E values pass price/EPS arithmetic at displayed precision. These consistency checks do not independently verify ratios or establish TTM versus annual derivation merely from the context label.
- Both TCS issuer PDF URLs tried returned **403** to curl; browser PDF opening also failed. Indexed primary-source content corroborates FY25 [revenue/EPS](https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2024-25/ar/annual-report-2024-2025.pdf) and [total profit](https://www.tcs.com/content/dam/tcs/pdf/discover-tcs/investor-relations/faq/tcs-integrated-annual-report-2024-2025-2pager.pdf) after conversion. This is **indexed corroboration, not a downloaded/visually verified TCS statement**. Recent FY26/FY27 values, price observations, ownership and all other cells remain independently unverified.
- News has a publisher URL; summary announcements/earnings have a provider-hosted image, not an original exchange attachment or page citation. Do not present the image as the original filing. Detailed earnings/attachments, concall transcripts, semantic search and claim-level citations were deferred. API-level attribution works; claim-level verification is incomplete.

Eighteen offline checks on already saved receipts passed: identities, periods/basis/core fields, bounded dates, OHLC/adjustment and P/E arithmetic, the market-cap scale finding, four independently checked Reliance figures and final request/debit reconciliation. No maintained corpus, live-model test or current Margin runtime test suite was created.

### Actual MCP discovery and the npm question

The [Drishti setup guide](https://drishti.manasija.in/docs/guides/drishti-mcp) explicitly says its npm CLI writes client configuration and does **not** run a local MCP server. Hosted HTTP with Bearer auth is sufficient. [BharatStock](https://bharatstockapi.com/reference#mcp-server) offers either `npx -y bharatstock-mcp` (local stdio) or its hosted URL; both require Developer/Pro. Installing npm does not resolve a Free entitlement gate. Package READMEs inspected locally agree with those instructions; no installer was executed.

Drishti authenticated initialization reports **`drishti-mcp` 3.3.1**, protocol **2025-11-25**, tool/resource/prompt capabilities. Resource/prompt listings were not fetched. SDK 2.2.0 uses Python attributes `server_info`, `protocol_version`, `next_cursor` and `input_schema`; mixing these with older SDK camelCase examples caused the initial local `AttributeError`. Correcting the accessor produced a successful complete catalog page, followed by successful session deletion. This was not an authentication, npm or provider failure.

The live catalog has **four tools**, no next cursor:

| Actual native tool | Observed input schema / function |
| --- | --- |
| `read_me` | Optional nullable `mode`; routing guidance |
| `search_tools` | `query`, `limit` (default 8); compact operation discovery |
| `describe_tools` | Required `names` (string or string array); operation descriptions/input schemas |
| `execute_tool` | Required `name`, optional nullable `arguments` object; execute a previously described operation |

The first three advertise generic object output schemas; `execute_tool` advertises none. Native tool annotations are absent. SHA-256 of the **SDK-decoded catalog snapshot**: `c384c28d705a7416be73645bb6cbb8121c964db019feba969dd8da1113041166` (not a digest of raw SSE bytes).

The public guides still describe a flat operation list such as `get_news`, `get_events` and `search_concalls`. They do not explain these four wrappers in the inspected pages; a targeted official-site search found no indexed explanation. The observed flow is **search → describe → execute**. Underlying operation inventory/schema, wrapper billing, read permissions and a data call through `execute_tool` remain pending. Do not claim that a returned `tools/list` or REST summary validates native MCP financial execution. BharatStock native MCP was deliberately not tested with its known-ineligible Free key.

Before implementation: make a small second discovery-focused pass with a fresh explicit budget, load only one or two operation schemas, measure wrapper charges, and test one bounded permitted operation. The gateway must namespace the four actual Drishti tools and gate `execute_tool` by the selected underlying operation/schema/cost. Exposing a generic executor without that check would defeat a native-tool allowlist. Do not fabricate `drishti__get_news` as a discovered native tool.

## Authenticated operation discovery and REST comparison: 9 October 2026

The user authorized the proposed selected-operation test and asked whether the other Drishti functions were mapped and how REST/MCP differences were established. This pass used the existing trial key and official Python MCP SDK 2.2.0, with private one-shot diagnostics, not a gateway implementation. The pre-execution local bounds were **16 initiated HTTP requests / 10 credits**, one discovery page, two descriptions, one native earnings execution and at most one matching REST detail request. No retries, pagination, BharatStock calls, purchases, configuration installer or provider outreach occurred.

### Accounting and live inventory

- **14 authenticated Drishti HTTP requests:** six REST and eight MCP; thirteen HTTP 200 and one initialized notification HTTP 202. MCP includes initialize, notification, stream GET, tools/list, search, describe, execute and session DELETE. REST includes four usage checks, one limits check and one earnings-detail comparison.
- Balance **992 → 992 after discovery → 989 after MCP earnings → 986 after REST detail**, final reserved zero. Discovery had zero observed debit; each successful detail call cost three. This establishes those shapes in this session, not universal free discovery or error/timeout billing.
- Server remains **3.3.1**, protocol **2025-11-25**. Native catalog remains the same four routing tools and hash. Effective REST RPM is 10; account diagnostics RPM 60; trial WebSocket active-symbol limit zero. No MCP-specific throughput bound was established.
- `search_tools(query="", limit=40)` returned **20 compact operation summaries, `has_more=true`**. A larger requested limit did not establish a full catalog or discoverable cursor. We did not exhaust discovery. Five market operations in the public flat guide were absent from this partial result; that does not mean removed or inaccessible.

The following mappings are **live names/summaries versus public REST capability matches**. Only the two bold names have described schemas; only earnings was executed. Other route relationships are family-level comparisons, not proof of identical inputs/results or internal HTTP calls.

| Discovered underlying operation | Public REST relationship / mapping status |
| --- | --- |
| `search_docs`, `get_doc`, `get_workflow_prompt` | Documentation/workflow helpers; no market-data REST equivalent established |
| `get_block_deals` | `/v1/block-deals`; newly observed beyond the eighteen-operation flat guide |
| `get_news` | `/v1/news` |
| `get_symbols` | `/v1/symbols/metadata` |
| `resolve_symbols` | Semantic company-name resolution; no public REST fuzzy-search route |
| `get_daily_summary` | Fetches an existing digest; not REST `POST /v1/daily-summary/` generation |
| `get_announcements` | `/v1/announcements` |
| `search_announcements` | Summary describes semantic + lexical filing retrieval; no corresponding public REST text-search route |
| `get_announcement_categories` | `/v1/announcements/categories` |
| `get_concalls` | `/v1/concalls` family; detailed shape not described in this pass |
| `get_upcoming_concalls` | `/v1/concalls/upcoming` |
| `get_upcoming_earnings` | `/v1/earnings/upcoming`; newly observed beyond the flat guide |
| `get_events` | Summary specifies NSE corporate calendar; no general public REST event route |
| **`search_concalls`** | Hybrid dense+sparse transcript search with fiscal-quarter filters; no corresponding public REST search route |
| `search_news` | Summary describes lexical/Mongo retrieval; REST `/v1/news` has feed filters but no documented full-text query |
| `list_earnings` | `/v1/earnings` family |
| **`get_earnings_filing`** | `/v1/earnings/detail`; paired execution confirms shared facts with additional MCP fields |
| `get_price_and_volume_since` | Summary says single anchor day by default, compact series only with `series=true`; no public REST historical-price route |

The three helpers plus seventeen market operations above total twenty. `get_sectoral_data`, `get_sector_wise_companies`, `get_52w_data`, `get_top_movers` and `get_top_traded` remain documented-only in this partial discovery. The five separately named prompt helpers in the coding guide were not observed here; `get_workflow_prompt` was. Do not assume equivalence without describing it. No Margin function registry has been implemented.

### Two inspected operation schemas

`search_concalls` requires `search_query`; optional inputs include `symbols` (string/list), `quarter_selector` (default `LAST`), `num_quarters` (2), `specific_quarters`, `result_mode` (`auto`), `page` (1), `per_page` (20), `candidate_top_k` (0), market-cap min/max (0), and `include_relaxed_matches` (true). Its description states that hits can include transcript-PDF `citation_url` and company-discovery result modes. These output claims are **not executed search evidence**. The schema uses generic strings/integers without enumerated modes or numeric bounds; schema validation alone does not impose a bounded research policy. Cap result sizes/windows and review accepted modes before admission.

`get_earnings_filing` accepts optional nullable `symbol`, `quarter`, `earnings_id` and boolean `detailed` (false). It declares no required fields or one-of constraint, although its description expects symbol/quarter or an existing ID. Admission must enforce that meaningful selector separately. Unlike the inspected REST detail parameters, MCP offers `earnings_id`; REST additionally supports `scrip_code`. The executed nested arguments were **`symbol=RELIANCE`, `quarter=q1_27`, `detailed=true`**, validated against the live schema and constrained to one already observed company/quarter.

### Paired payload and financial findings

MCP execution returned a `data` envelope with a filing record, structured standalone/consolidated tables, fiscal labels, units, expanded fields and source locators. The single REST comparison was `GET /v1/earnings/detail?symbol=RELIANCE&quarter=q1_27&detailed=true`. Both returned the same record ID, company and quarter. Across their **97 shared earnings-table leaf fields, values matched exactly**. This is strong evidence of shared content for this filing, not proof of identical internal implementations or all other operations.

| Observed difference | MCP | REST detail |
| --- | --- | --- |
| Result container | MCP result/content with decoded `data` | Direct JSON record |
| `scrip_code` | Integer | String |
| Filing `date` | Same timestamp without offset | Same timestamp with `+00:00` |
| Raw table fields | Four raw period labels plus raw revenue/expenses per basis | Those twelve additional nested fields absent |
| Source locators | `attachment_url`, PDF and two page citation URLs | Those two top-level fields absent in this response; separate REST resolution routes exist |

The consolidated table has a material conflict: normalized current-period `revenue` is **₹298,621 crore**, exactly its previous-quarter revenue, while `revenue_from_operations_raw.current_period_value` is **₹311,850 crore**. The previously saved BharatStock consolidated Q1 FY27 row (period end 30 June 2026) is ₹3,118,500,000,000, matching the raw value after conversion. Consolidated PAT is ₹23,196 crore in both Drishti surfaces and matches the saved BharatStock total-profit field. Consolidated Drishti EPS is null, while BharatStock returns a value. These are provider comparisons and an internal discrepancy, **not independent verification against the Q1 issuer PDF**. Do not silently substitute raw revenue or use the reported growth fields until definition/source checks resolve the conflict. Identically named operating-profit fields also need metric-definition review before cross-provider mapping.

### Citation behavior and forwarding constraint

MCP returned an expiring signed attachment URL and citation locators for the PDF and pages **9 and 18**. Crucially, all three API citation URLs contain **the supplied Drishti key in an `api_key` query parameter**, confirmed locally without displaying it. These raw URLs were not fetched, exposed in documentation or pushed. The signed attachment and citation pages are locators only: original-file reachability, page content, claim support and browser-auth behavior remain untested.

Stage 1 therefore needs explicit credential sanitization even when preserving native results: remove credential-bearing query values from content/structured content before the model, logs or downstream tools receive them; report that a sanitized API locator requires authorized resolution rather than presenting it as a publicly working citation. Prefer a verified original public source when available. A server-side evidence resolver is a later optional capability, not implemented here. Returned provider guidance telling the model to cite links does not authorize leaking the key or skipping page verification.

### Evidence strength and reproducibility

We establish differences through three separate comparisons: **live operation names/descriptions**, **public REST methods/parameters**, and **one paired data execution**. Today's freshly downloaded OpenAPI remains 3.1.0 with thirty paths and SHA-256 `b4e45c56fc3d3f853cda272518c84e9ede523c4260d508f7a964288c120f7734`, identical to yesterday. Absence of a public search route does not prove the absence of private/internal APIs or a separate database. Nor does one shared financial payload establish parity of all operations. Do not claim all tools are mapped to exact implementation functions; we have a partial capability map, two input schemas and one empirical pair.

Private receipts are in ignored `reports/private/discovery-20261009/`, with restricted permissions and manual review/deletion due **23 October 2026**. Hashes: native catalog `c384c28d705a7416be73645bb6cbb8121c964db019feba969dd8da1113041166`; operation search `2e38ca2fded2e3d98c7b4bed9172f9c1c40303a6422ff637aab6639f30c585ae`; two descriptions `c1c5edee81e7c1165b302623e7c1ed68be73c2c29703f111a359b301fff4782e`. Seventeen offline receipt checks passed for accounting, schema/selection bounds, identity, shared values, source-field differences, credential-query presence and financial discrepancy/cross-provider matches. These are source-diagnostic checks, not a gateway runtime suite or real-model-host evaluation. No commit/push occurred.

## Drishti function-mapping checkpoint: 9 October 2026

The user requested a complete picture of function mapping. A separately budgeted metadata-only pass used at most **24 HTTP requests / 10 credits**, no data execution, financial retrieval or BharatStock traffic. It completed with **23 authenticated Drishti requests: 6 REST usage checks and 17 MCP messages across two intentional SDK sessions**. Twenty-one responses were HTTP 200 and two initialized notifications HTTP 202. Balance stayed **986**, final reserved zero; no observed debit at any intermediate check. This measures these discovery/description/guidance shapes, not a blanket promise of free unknown operations.

The first session refreshed the unchanged four-tool catalog, read the default router, queried `search_tools` for sector/movers/traded/52-week/price context and described **25 confirmed operation names** in batches of ten, ten and five. Targeted discovery found the five previously documented-only market operations. The second session read `read_me(mode="data")` and `read_me(mode="docs")`; SDK call validation also fetched its native catalog automatically, included in the request total. This was planned guidance inspection, not retrying an uncertain operation. SDK 2.2.0 and server 3.3.1/protocol 2025-11-25 remained unchanged. All calls were sequentially paced with no reconnect/retry allowance or data executor admitted.

The current human-readable contract is [Drishti function map](../reference/drishti-functions.md); its [derived JSON snapshot](../reference/drishti-functions.json) contains all 25 input schemas, four native schemas and reverse relationships for thirty REST paths. These files have a distinct purpose from this dated evidence log: they are the integration reference. They contain no raw data/account payloads, signed result URLs or credentials. Provider description/example prose is omitted from the JSON while schema constraints/defaults/references are preserved. No Margin function registry or gateway has been implemented.

Completeness is bounded: all market operations from the inspected flat guide, the live routing guides and known search results now have described schemas. There are **22 market operations and three documentation/workflow helpers**. The native `tools/list` is complete at four, but `search_tools` caps at twenty and exposes no offset/cursor; a union of guides/search results cannot prove absence of hidden/unlisted operations. Do not characterize our schema map as inspection of private implementation code or permission to execute all functions. Only earnings detail has an observed data execution from the earlier pass.

Material findings from descriptions, **not new executed data results**:

- Seven functions accept nested typed `query` objects, plus permissive arbitrary-object/string/null alternatives. Inputs such as relative `lookback_days`, record `ids` and index expansion are not equivalent to the plain public REST query contract. ID refetch overrides date/symbol/page filters; typed date-only boundaries use UTC. Validate logical exclusivity, expansions and the typed branch independently of the permissive outer schema.
- Announcement, concall and earnings descriptions expose citation/source fields; concalls additionally have `include_full_transcript`. REST announcement attachment omission therefore does not establish equivalent MCP omission. Actual link shapes/billing/availability remain unexecuted for announcements and concalls; apply the known citation-key sanitization rule to all operations before forwarding.
- `get_events` describes an empty-window fallback to the latest ten events. Date-window success must not be assumed from a successful call. Historical price retrieval defaults to one anchor day unless `series=true`.
- Top movers excludes absolute daily changes of 20% or more; top traded uses a filtered volume ranking. Market-cap units, several mode values and output coverage remain unresolved. Peer discovery describes a basic-industry fallback, not an independently validated universal peer graph.
- The current `get_workflow_prompt` supports seven workflow values. Older separately named prompt helpers are not confirmed aliases; do not publish them as live operations. Eighteen market operations have published MCP prices; **seven confirmed functions have no established MCP price**, rather than an assumed zero price.

Eighteen offline source/contract checks passed: request/credit accounting, no data execution, schema validity, operation counts, seven nested query wrappers, reverse REST coverage, reference-example validity and private permissions. A metadata import initially created a mode-0755 `__pycache__` directory; it was restricted to 0700 and the recursive check then passed. Raw receipts remained private. Keep `reports/private/function-map-20261009/` ignored with manual review/deletion due **23 October**. No purchase, outreach, commit or push occurred.

SHA-256 of the three private description receipts: batch one `76f313403e98a7a1d211428a55a5919bf88392ba8e01631607f987debf616c0a`; batch two `070b471df466dcc3ef9498153f60d89b2320dcebd3e67fbddd7b0078ca624d01`; batch three `f607448c3ced4659a97960cab989055633de5a633b2836e086691c719c383e85`. The unchanged native catalog is `c384c28d705a7416be73645bb6cbb8121c964db019feba969dd8da1113041166`; the derived JSON snapshot is `208476ccab3368286c9cf26b212c27eed9eeb1bbf262cc67453f20ff3a71052b` at this checkpoint. These identify snapshots, not future compatibility guarantees.

## Architecture refinement evidence: 9 October 2026

Planning follow-up used the completed private receipts/derived function reference, local official Python MCP SDK 2.2.0 source and public [SDK documentation](https://py.sdk.modelcontextprotocol.io/) / [versioned tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). No authenticated provider request or credit debit occurred. Low-level `mcp.server.Server` exposes constructor callbacks including `on_list_tools` / `on_call_tool`, `run` and `create_initialization_options`; old v1 decorators are not its inspected interface. Server-side transport remains untested. Pinning 2.2.0 is a proposed implementation starting point, not a new committed dependency.

The resulting [architecture](../design/mcp-aggregation.md) separates native catalog discovery from nested execution admission, mandates sanitization/context handling before forwarding and distinguishes provider/source-locator attribution from resolved/verified evidence. The [delivery plan](../plan.md) permits offline bridge work before full live entitlement or twelve-company coverage; earlier “before implementation” source-check lists are live-source/semantic acceptance gates, not a requirement to delay synthetic transport work. The refined prospective test ceilings supersede older future smoke proposals; historical executed passes remain unchanged.

## Transport decision correction: 9 October 2026

The user identified a planning inconsistency: all authenticated BharatStock tests used REST, and our inspected package already established a wrapper over the same data, but the refined design still required BharatStock native MCP. Corrected the chosen architecture to **BharatStock REST + Drishti MCP**, with one downstream Margin MCP. This is an explicit architecture change; no previously tested REST call is relabelled as an MCP call.

Public [BharatStock reference](https://bharatstockapi.com/reference) was rechecked: MCP wraps the same data endpoints, while its Free/Starter native-MCP gate is separate from REST access. Use direct REST for the six reviewed data families and retain field/pagination/context differences rather than copying the JS MCP contract. The direct adapter controls attempts and pagination without an unused hosted wrapper. Native MCP remains optional future work, not a fallback on REST errors. Drishti remains MCP because the observed discovery/executor and described searches/market capabilities are not all represented by its inspected public REST schema; this does not prove extra private datasets or successful access to every operation.

Rechecked [BharatStock pricing](https://bharatstockapi.com/#pricing) and [Drishti pricing](https://drishti.manasija.in/docs/pricing): use existing Free/trial keys for bounded prototype work. For later paid history/quota, BharatStock Starter at ₹600/month with 3,000/day plus Drishti Starter at ₹2,000/month gives a published ₹2,600/month starting recommendation, plus applicable tax/charges. BharatStock pricing explicitly excludes tax. Developer at ₹1,000/month is optional for 10,000/day or native MCP; its access gate no longer blocks the release. Drishti operation entitlements/costs remain subject to selected execution tests. No purchase or authenticated request occurred during this correction.

Software acceptance changes accordingly: a synthetic REST service and synthetic MCP service behind the downstream stdio client, REST mapping/header/pagination/retry checks, native Drishti fidelity/admission checks and source-independent sanitization/budget tests. Live acceptance needs actual REST and MCP paths through Margin, not two native upstream MCPs. The next BharatStock source proposal is at most six REST requests within remaining daily quota for search/actions gaps; successful saved financial/price/ratio receipts should be reused. Historical authenticated totals and the last observed Drishti balance of 986 remain unchanged.

## Final architecture evaluation: 9 October 2026

Reviewed the current transport, contract, lifecycle, output and stage decisions using existing trial evidence and public [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), [SDK reference](https://py.sdk.modelcontextprotocol.io/), [BharatStock reference](https://bharatstockapi.com/reference) and [Drishti MCP guide](https://drishti.manasija.in/docs/guides/drishti-mcp). Inspected local SDK 2.2.0 callback declarations without launching a server or making an authenticated call. MCP structured output is object-shaped and a declared output schema must be respected; the local REST wrapper and mirrored sanitized JSON text therefore have an explicit role, while Drishti native schema fidelity remains separate. Metadata refresh supplies evidence for review, not automatic operation approval.

New public availability observation: the [BharatStock homepage](https://bharatstockapi.com/) currently reports licensing-related maintenance affecting institutional-flow display. This is provider-published availability information, not an authenticated `/v1/market/fii-dii` test or proof of the route's exact response. Do not promise that family as sentiment coverage until separately checked; it is outside the first profile. Rechecked published pricing; the Starter/Starter starting recommendation is unchanged. No source-test count, credit balance or financial-verification claim was extended by this architecture evaluation.

## Temporary interface evaluation: 20 October 2026

For the user's core-first request, evaluated a local FastAPI/static HTML/JS workbench, Streamlit and a separate React/TypeScript app. Primary references inspected: [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/), [static files](https://fastapi.tiangolo.com/tutorial/static-files/), [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form) and [caching/resource guidance](https://docs.streamlit.io/develop/concepts/architecture/caching). No framework was installed, benchmarked or implemented. FastAPI lifecycle can own shared app resources and serve local assets; Streamlit forms can batch input changes. Choosing the former is an engineering judgment for explicit request actions and async adapter/ledger ownership, not a claim that the latter cannot implement a safe UI.

The active design separates core operations/records from HTTP and future MCP result objects. A temporary interface does not require a maintained financial server/corpus, model or public deployment. No provider/pricing/account refresh was performed; 9 October schemas, prices and the 986-credit snapshot stay dated evidence, not a current entitlement/remaining-budget guarantee. No authenticated data/credit spend or receipt retention change occurred.
