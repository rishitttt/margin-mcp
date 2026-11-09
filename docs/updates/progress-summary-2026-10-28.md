# Margin: Progress Summary

**28 October 2026**

## Aim and current stage

Margin is an Indian equity research project intended to give an LLM or agent harness one interface to company financials, market data, news and filings. We are building the retrieval and research core first, testing it through a temporary browser interface, and will expose that core through our own Model Context Protocol (MCP) server later.

We have built an installable Python package and a working local test interface. We have not yet packaged Margin as an MCP server or built an autonomous financial analyst. Data is retrieved from external providers on demand; we are not maintaining our own financial corpus.

## What we have implemented

The current architecture is:

`Browser workbench -> FastAPI -> shared Python core -> BharatStock REST / Drishti MCP`

BharatStock supplies numerical company and market data. Drishti supplies news, announcements and earnings records through its hosted MCP. We use BharatStock's REST API directly because the inspected BharatStock MCP wraps the same underlying data endpoints. The core is independent of the browser interface, so the later Margin MCP adapter can reuse it.

We have implemented **13 approved core operations**:

- **BharatStock (6):** company search, stock snapshot, financial statements, valuation ratios, historical end-of-day prices and corporate actions.
- **Drishti (7):** company-name resolution, company metadata, news, announcements, announcement categories, earnings discovery and individual earnings detail.

Implementation does not mean every operation has been validated live. Some remain restricted pending focused tests. These are core operations, not thirteen tools already exposed by a Margin MCP server.

The workbench lets us choose a company and exchange, select modules, preview the exact operation plan, execute it, and inspect tables, a price chart, event records, warnings and sanitized provider responses. Each result includes its provider, retrieval time and an execution receipt.

The shared core also implements bounded queries, input validation, request pacing, process-level budgets, estimated credit accounting, duplicate-run protection, partial failures, timeout/cancellation handling and temporary result retention. Credentials remain in the backend; known secrets and credential-bearing URLs are sanitized before results reach the interface. Drishti connections check the approved tool schemas and require explicit refresh when metadata expires.

## What we have demonstrated

The recorded live workbench run on **21 October** completed eight calls for Reliance: snapshot, quarterly financials, annual financials, ratios and EOD prices from BharatStock, followed by news, announcements and earnings discovery from Drishti. All eight returned successfully. This is seven distinct operations because financials was requested twice.

That run displayed three quarterly rows, two annual rows, 61 price observations, two news items, two announcements and two earnings summaries. It demonstrates the combined numerical-and-events retrieval path for one company; it does not establish comprehensive market coverage or financial accuracy. The run's Drishti estimate was four credits, without independent reconciliation against the account debit.

Earlier provider investigations exercised Reliance and TCS and compared Drishti earnings detail with its REST counterpart. We also mapped **25 confirmed Drishti operation schemas** and their REST relationships; only seven are admitted by the current core.

The last recorded automated validation had **50 passing tests**, covering provider adapters, schema checks, budgets, sanitization, duplicate submissions, connection handling and local HTTP/view behavior. Offline tests do not replace live data or original-source checks.

## What we learned and what remains incomplete

Combining providers requires preserving financial context. We found market-cap scales differing by response field, missing cash-flow values, numerical quarters older than event summaries, and conflicting normalized/raw earnings values. We retain warnings instead of silently reconciling these differences. Four Reliance FY25 values were previously checked against an issuer statement; broad cell-level verification remains open.

The live demonstration exposed UI gaps: actual news and earnings fields sometimes fall back to generic tables, real earnings-list records do not yet consistently offer the detail action, and printing clips wide tables. Citation extraction also includes decorative image URLs that should not be treated as evidence. We preserve sanitized source locators, but have not implemented authenticated document resolution or claim/page verification.

Current budgets are process-local and reset on restart; they are not durable account-wide controls. Credit estimates are not measured billing. Most operations, companies and sectors still need focused live evaluation. Derived financial analysis, comparisons, transcript search, broader sentiment analysis and an LLM-facing Margin MCP remain unfinished.

## Work in progress: financial analysis

Alongside the integration work, we are developing finance-specific functions, including **discounted cash flow (DCF) valuation**. These are still in progress and are not included in the 13-operation count or the demonstrated live results. We intend to keep financial inputs, valuation assumptions and resulting calculations traceable, while distinguishing provider data from assumptions supplied by the user or model.

## Planned functions, protocols and next steps

Our immediate priorities are to improve how live news and earnings responses are displayed, complete earnings-detail navigation, fix PDF print formatting, and validate additional operations under small explicit budgets.

We also plan to add more financial analysis functions and research protocols. These protocols will define repeatable procedures for agents using the data, alongside the MCP connection interface:

- **Sentiment analysis protocol:** specify source selection, time windows, company relevance, aggregation and uncertainty, while distinguishing news tone from broader investor sentiment.
- **Citation protocol:** define source selection, claim-to-source links, document/page references and verification status, with explicit handling of inaccessible or conflicting evidence.
- **Additional functions and workflows:** integrate and validate DCF and other financial calculations, comparisons, and selected news, filing and transcript research capabilities.

These are planned extensions, not completed capabilities. After validating the core workflows, we will package Margin as an MCP server and evaluate it in an actual agent harness for accuracy, coverage, citation quality and request cost.
