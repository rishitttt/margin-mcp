# BharatStock and Drishti: MCP access, endpoints and coverage

Research date: **8 October 2026**. Purpose: establish the evidence behind the [aggregation design](../design/mcp-aggregation.md). This is a dated investigation, not an implemented adapter or a verified market-data coverage report. The user has confirmed willingness to pay for plans; no purchase/account access has been observed.

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

Schemas/prices can change at the same URL. Temporary downloads are not committed source datasets; hashes identify this inspection, not an assurance that a future download will match. Authenticated coverage measured this task: **zero companies/financial cells/event records**.

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

Exact names/costs below are documented in the [MCP guide](https://drishti.manasija.in/docs/guides/drishti-mcp). Hosted schemas/arguments and implementation fan-out remain uninspected because no key was supplied. A semantically corresponding REST route is **not proof** that the MCP implementation calls that route or has the same billing.

| Native MCP tool | Published credits per call | REST relationship in inspected public schema |
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

The public [OpenAPI document](https://developers.manasija.in/openapi.json) establishes these routes, but **none was called with credentials**:

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

## Expected numeric and event coverage

BharatStock advertises 5,000+ stocks, 11+ years of price history, broad NSE/BSE categories and 72 screener metrics. This is **addressable advertised coverage**, not 5,000 fully populated research profiles. Its reference explains that `data_coverage` flags describe what a pipeline can populate rather than checking actual non-null rows. Its FAQ/reference also warn of missing SME/micro-cap financials, incomplete classifications, newer integrated BS availability and annual CF cadence. Drishti documents rich event/call/news tools but no fixed universe/history-depth guarantee was established in this investigation.

The joint research population is the measured intersection for a task, not the union of two marketing universes. Useful overlap includes company identity, earnings versus financial statements, price/volume and actions versus announcements. Compare the same company, exchange, period, consolidation basis, units and update time; never silently average discrepancies. Shared original filings mean agreement may not be independent.

**Units require an early check:** BharatStock's homepage says statement values use absolute INR; screener market cap and market-wide FII/DII flow use crores. The reference's Reliance financial example contains values that appear crore-scaled relative to the claimed statement convention. That appearance is an inference, not a measured API defect. Drishti earnings examples have field-level units such as `Rs crore`. Preserve raw values/units and verify paid payloads against issuer filings before any global conversion. The REST schema's optional numeric fields alone cannot resolve this discrepancy.

What the pairing can plausibly support: dated numeric company snapshots, financial trend inputs, screens, ownership/actions, news/filing discovery, earnings commentary and topic search of transcripts. What remains unproven: universal BSE/SME coverage, exact historical event retention, intraday/full order-book data, dividend-reinvested returns, historic point-in-time revisions, comprehensive social/investor sentiment and cell-level citations for every metric. News tone, management outlook, transaction observations and price reaction are separate signals. On-demand retrieval requires no maintained corpus; small evaluation receipts/fixtures still need retention permission.

## Workload arithmetic and upgrade triggers

These are **planning estimates** using documented MCP credits, excluding automatic retries, extra pages, attachments, account diagnostics and other users. Stage 1 forwards individual tools; these profiles describe a host workflow, not an implemented compound tool.

| Profile, one company | BharatStock native calls | Drishti native calls / credits |
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

The recommended subscriptions remain Developer + Starter at a published ₹3,000/month. The [API/MCP test protocol](../api-testing.md) defines local key setup, catalog/account checks, a 50-credit smoke pass within the 500-credit expanded budget, selective REST comparisons, numeric/event quality checks and recorded evidence. These authenticated steps remain pending accounts/keys; no gateway or committed probe client has been implemented.
