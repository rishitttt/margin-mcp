# API and MCP testing protocol

Current checkpoint: 8 October 2026. The public/no-key checks have run; authenticated testing is pending subscriptions and keys. This is the operational test plan, not a delivered test client. [Provider research](research/mcp-provider-feasibility.md) owns observed source contracts and results; [implementation status](implementation.md) owns delivered/validated state.

## Required subscriptions and credentials

Buy **monthly BharatStock Developer** (published ₹1,000/month) and **monthly Drishti Starter** (₹2,000/month). Total published price: ₹3,000/month; confirm tax/invoice, account/team access and activation details during onboarding. Higher tiers are unnecessary for a bounded first test.

- BharatStock Free/Starter do not include its native MCP; Developer is the minimum published eligible tier. Source: [pricing](https://bharatstockapi.com/#pricing), [MCP reference](https://bharatstockapi.com/reference#mcp-server).
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

The latest pass used 14 requests and is recorded in the research note. It established connectivity, schema availability and authentication barriers. It did not retrieve paid data, access a live catalog or spend account credits.

One reproducible public check, requiring only curl:

```sh
curl --fail --show-error --max-time 20 --max-filesize 2097152 https://bharatstockapi.com/v1/plans
```

### 2. Authentication and accounting: pending

Once eligible keys are available, independently establish access before any financial test:

| Provider | REST control-plane checks | MCP checks |
| --- | --- | --- |
| BharatStock | `GET /v1/mcp/authorize` with `X-API-Key` | Initialize `https://bharatstockapi.com/v1/mcp` with Bearer key; negotiate protocol; fetch all bounded `tools/list` pages |
| Drishti | `GET /v1/account`, `/v1/account/limits`, `/v1/account/usage` with `X-API-Key` | Initialize `https://mcp.drishti.manasija.in` with Bearer key; negotiate protocol; fetch bounded `tools/list` pages |

Record eligible products, effective limits, starting credits, server/protocol versions and a hash of the discovered schemas. Store account payloads privately; publish only non-sensitive conclusions. If account data cannot distinguish charges, use the user's dashboard/ledger. Do not assume control-plane or discovery traffic is free without evidence.

Use the official MCP SDK for authenticated transport/session handling, including lifecycle/cancellation/cleanup; pin a tested version when introducing a repeatable client. Do not hand-roll Streamable HTTP sessions based on the unauthenticated curl probes. No gateway needs to be implemented to test upstream MCPs directly.

### 3. Two-company smoke test: pending

Start with RELIANCE and TCS, after confirming identity. Use one page per call, small explicit limits and a fixed 30-day window. Test ordinary summary data first; defer detail/attachments until support is needed.

| Question | BharatStock native tools | Drishti native tools |
| --- | --- | --- |
| Correct company/listing? | `search_stocks`, `get_stock_quote` | `resolve_symbols`, `get_symbols` |
| Numerical performance? | `get_financials` quarterly/annual, `get_stock_fundamentals` | `list_earnings`, `get_earnings_filing` for an actually discovered quarter |
| What happened recently? | `get_corporate_actions`, bounded `get_stock_prices` | `get_news`, `get_announcements`, `get_events` |
| What is management saying? | Financial inputs already obtained | `get_concalls`, one targeted `search_concalls` |

Those are documented candidate names, not a claim that the hosted schemas have been authenticated. Construct arguments from the actual catalog; do not invent Drishti MCP date/filter parameters from its REST reference. Pick fiscal-quarter keys from returned earnings/call metadata instead of guessing the latest quarter.

Budget the first authenticated smoke pass around **50 Drishti credits**, including some diagnostic/evidence headroom, and at most **50 initiated data calls across providers**. This is a proposed local stop/estimate, not an enforced limiter or guarantee of remote charges. Inspect usage after each new billable tool shape; stop if measured cost is unexpected or the account/product rejects access. An uncertain timeout is not permission to repeat a possibly billed call. No deliberate quota exhaustion or automatic page walking.

### 4. Selective REST/MCP comparison: pending

Use REST only to diagnose a specific difference, not to duplicate every MCP fetch. Exact origins: BharatStock `https://bharatstockapi.com`; Drishti `https://developers.manasija.in`. Paths below include `/v1`; authenticate with headers, never keys in query strings.

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

### 5. Coverage, quality and costs: pending

Verify identity/ISIN/exchange across sources; raw field names; currency/scale; reporting basis; quarter versus annual duration; actual earliest/latest returned dates; nullable fields; pagination; timestamp precision/timezone; original sources versus provider-generated summaries. BharatStock documentation has a units inconsistency that needs actual payload/filing comparison before normalization.

Compare a few values against original filings where legally accessible. Provider agreement alone is not independent verification. News tone, management outlook and price response remain separate signals; event/price coincidence is not evidence of causality. Empty results can mean no event, missing coverage or restricted history—classify only what the response supports.

After the two-company pass succeeds, use the design's 12-company panel, including banks, a verified BSE-exclusive company and an NSE SME company. The **500-credit expanded evaluation budget** includes the smoke pass; it is not 500 additional credits by default. Record calls/observed debit, latency, returned coverage and financial/evidence correctness before deciding on an upgrade.

## Evidence and completion

Record date/time, endpoint or tool name, credential tier (no key/account identifier), query window, schema/server version, HTTP/MCP status, latency, result counts/date range, units/basis, truncation/missing cases, source-link depth and measured credit change. Keep raw responses privately in ignored `reports/private/` or a temporary directory with explicit expiry. Do not commit licensed financial datasets, personal account responses, keys or presigned links.

This phase is complete when both accounts authenticate, representative native tools return bounded numeric and event data, charge deltas are understood, units/coverage/evidence gaps are documented and failure cases are reproducible. Then implement aggregation against those measured contracts. Passing endpoint probes is not a delivered Margin server or verified research answer.
