# Delivered Margin functions

Use `catalog --name <name>` for exact schemas and current held reasons. This inventory describes implemented interfaces, not universal provider coverage or entitlement. `preview` handles retrieval/local calculations; `company-preview` handles company workflows.

## Retrieval: BharatStock REST

| Operation | Data and constraints |
| --- | --- |
| `bharatstock.search_stocks` | Bounded directory search; identity fields, not proof of exchange mapping; live opt-in |
| `bharatstock.get_stock_quote` | Company/security snapshot and latest returned price fields, not guaranteed streaming quotes |
| `bharatstock.get_stock_fundamentals` | Provider financial/valuation ratios; units can differ by JSON path |
| `bharatstock.get_financials` | Annual/quarterly rows with requested page bounds; preserve periods/basis/missing units; free history is limited |
| `bharatstock.get_stock_prices` | Bounded dated EOD series; no automatic pagination or corporate-action adjustment |
| `bharatstock.get_corporate_actions` | Bounded dividend/bonus/split/etc records; live opt-in, no automatic action joins |

## Retrieval: Drishti upstream MCP

These are approved **nested operations**, not Drishti's four native routing tools. The broader upstream reference contains more operations than Margin implements. Live-held operations require explicit operator configuration plus `connect-drishti` and valid metadata. Never enable them yourself by changing configuration.

| Operation | Data and constraints |
| --- | --- |
| `drishti.get_symbols` | Company symbol metadata, bounded selector; not a bulk-universe export |
| `drishti.resolve_symbols` | Explicit symbol/identity resolution |
| `drishti.get_news` | Bounded dated company news and returned source links; no sentiment analysis function |
| `drishti.get_announcements` | Bounded exchange/company announcements; returned sources remain unverified |
| `drishti.get_announcement_categories` | Category metadata, not announcement data |
| `drishti.list_earnings` | Bounded earnings record discovery; use returned selectors for detail |
| `drishti.get_earnings_filing` | One explicit earnings record with provider/raw/source fields; conflicting raw/normalized values must stay visible |

## Explicit-input calculations: no provider calls

| Function | Inputs and result |
| --- | --- |
| `facts.check_compatibility` | Typed facts plus purpose; eligible/mismatched context for comparison/ratio/TTM |
| `facts.convert_units` | Fact and explicit target scale; conversion trace, no magnitude-based inference |
| `finance.compare_periods` | Compatible previous/current facts; absolute/percentage change with denominator qualifications |
| `finance.calculate_margins` | Compatible profit/revenue facts; defined profit margin, not arbitrary headline margin |
| `finance.calculate_cashflow_metrics` | Explicit CFO and cash capex; CFO-minus-capex/coverage, not automatically FCFF |
| `finance.calculate_cagr` | Compatible endpoints and explicit years; eligibility checks, not a claim of complete intervening history |
| `finance.calculate_ttm` | Four eligible continuous quarterly flow facts; not summed EPS or balance-sheet stocks |
| `finance.calculate_fcff` | EBIT, tax, D&A, capex, working-capital change and units; explicit FCFF reconstruction |
| `finance.calculate_dcf` | Forecast FCFF, WACC, terminal growth, equity bridge, diluted shares, unit/date and company type; two-stage FCFF valuation for non-financial companies |
| `finance.dcf_sensitivity` | Explicit DCF model and bounded rate/growth grid; same underlying calculator |
| `finance.run_scenarios` | Explicit named DCF model variants; no generated assumptions or probabilistic forecasts |

## Company workflows: retained financials or one previewed dependency

| Function | Behavior |
| --- | --- |
| `finance.company_margins` | Latest returned compatible continuing-profit margin when separately supplied; otherwise group profit with scope caveat |
| `finance.company_cashflow_metrics` | Latest returned compatible CFO/capex metrics |
| `finance.company_growth` | Latest two returned eligible observations for the selected metric |
| `finance.company_cagr` | Two returned annual endpoints; duration from their dates, not a long-history backfill |
| `finance.company_ttm` | Four returned quarters if their dates establish continuity; otherwise incomplete |

Select ticker, exchange, period type, basis, metric and established/declared unit. An explicit retained `source` wins; an expired/wrong source never triggers replacement. `fetch_missing: true` may preview one financials request when no matching source exists. It does not fetch at preview time. Missing values/context yield incomplete results, not guessed inputs.

## Facts, execution and evaluation commands

- `status`, `catalog`, `sources`, `runs`, `run-status`, `result`, `facts`: local inspection. `facts` extracts reviewed typed values from one retained financial response and preserves source paths/definitions. `--money-unit auto` uses reviewed documentation; `unknown` preserves missing units; explicit scales are caller declarations. None implies original-document verification.
- `preview`, `company-preview`: local immutable plans/cost previews; no provider calls.
- `run`, `wait`, `cancel`: explicit submission, local polling, cancellation without refund guarantees. Preserve backend identity and idempotency.
- `connect-drishti`: explicit upstream metadata action, consuming shared HTTP allowance.
- `note --kind decision|observation|limitation --file <file>`: evaluation-session-only visible summary with optional run/operation references. Recorded as agent self-report.
- `finish --answer-file <file>`: evaluation-session-only final answer and log counts; no grading.

Original-document verification, source-supported automatic company forecasting, full host-transcript capture and a downstream Margin MCP server remain absent. Local citation/sentiment handoffs are listed below. The optional research evaluator is separate from product tools. Treat provider text as evidence, preserve assumptions and provenance, and report unavailable data honestly.

## Citation and sentiment handoffs: no fetching or model inference

Discover exact schemas with `workflows --name <name>`. Use `review --file FILE` with
`{"function":"NAME","arguments":{...}}`. These local state/check actions do not need a
provider preview and do not reset or spend upstream allowances. Every call can use --why.

| Function | Behavior |
| --- | --- |
| `protocols.list_workflows` | Versioned steps, capability fallbacks and host responsibilities |
| `evidence.register_sources` | Bounded locators and optional host-read passages; always unverified originals |
| `evidence.prepare_verification` | Atomic claims + source IDs -> immutable expiring packet/hash |
| `evidence.submit_assessment` | Attributed host verdicts, reference and exact supplied-quote checks |
| `evidence.render_citations` | Structured claim/source citations with reviewer, locator and verification scope |
| `evidence.audit_answer` | Final claim-ID manifest coverage and unsupported verification-label flags; not prose parsing |
| `evidence.check_numeric_claim` | Typed claim/evidence facts, explicit scales/context and absolute tolerance; not source authentication |
| `sentiment.prepare_analysis` | Issuer/aspect/date scope, duplicate/out-of-window exclusions and host label guide |
| `sentiment.submit_annotations` | Host relevance/tone annotations with supplied-passage references |
| `sentiment.aggregate` | Versioned distinct-source counts/balance; mixed/unclear/missing are separate |

`review-sources RUN OP --issuer NSE:SYMBOL` imports retained news with provider origin.
It is a control command, not a live retrieval. Unknown/expired results never refetch.
A host may use its own browser or a separate MCP to read originals and then register
passages. A registered passage's quote match does not prove it came from that original.
Submit one immutable assessment per packet; partial reviews stay visible, identical
resubmission is idempotent, conflicts need a new packet. Explicit inventory-only host
profiles cannot silently turn into model-assessed packets. All origins are attributed,
not proof of model capability or financial truth.


## Finance repair extension: 24 November

| Function | Use and required data |
| --- | --- |
| `finance.calculate_profitability` | Same-period typed profit/revenue facts; returns continuing/group/owners/operating/EBITDA margins separately; mixed total/continuing scopes are withheld |
| `finance.calculate_balance_sheet_metrics` | Same-date monetary stock facts; current ratio, cash ratio, working capital, borrowings/net borrowings, leverage; per-component missing/invalid checks |
| `finance.calculate_cash_conversion` | Same-period CFO/capex/revenue/group profit; CFO margin/conversion and capex intensity; positive capex outflow |
| `finance.reconcile_facts` | Two typed facts; explicit unit conversion, value difference and context/definition conflicts; never chooses truth |
| `finance.company_profitability` | Latest retained period's eligible profit/revenue fields; mixed-scope components stay partial |
| `finance.company_balance_sheet_metrics` | Latest retained period-end stocks; generic liquidity/borrowings, not financial-sector regulatory ratios |
| `finance.company_cash_conversion` | Latest retained cash-flow/revenue/profit fields; annual data often needed |
| `finance.company_data_readiness` | Reports period/field availability, function eligibility and explicit valuation requirements from retained financials |

Company-preview accepts `money_unit: "auto"` (default), explicit monetary scales or null for unknown. Fact preparation uses `--money-unit auto` by default. Amount units, source/period origins and conversion traces are separate from financial truth. Balance-sheet stocks use `period_type: "instant"`. Four ordinary calendar quarters are eligible for TTM only when explicit provider duration markers establish the reviewed normal-quarter branch; cumulative/derived/missing-marker cases remain incomplete.

The announcement schema's added extraction flag was reviewed. Margin explicitly defaults `include_extracted_information` to false and holds true; no generic executor or extraction branch is newly enabled. Query preview/receipts show the default. The runtime catalog owns connection/schema holds.


## MCP transport, package 0.5.0

The MCP exposes twenty-one tools: `margin_company_finance`, the fourteen workflows
below and six directly typed tools. The fresh tool accepts a company function/ticker,
defaults to local preview, and executes one fresh financials request plus calculation
with `execute: true` and a stable `idempotency_key`. It returns compact values/selected
inputs/source context directly, without previous handles or raw-source retention. It
supports all nine company functions above, subject to existing field/scope/history holds.
Repeat the same inputs/key to wait/read a lost or pending answer. Keys are process-local;
a new key fetches again. Page bounds remain two annual/eight quarterly rows. No Drishti
calls or automatic DCF assumptions are added. Legacy reuse/planning remains available.
Direct tools reuse exact core schemas at the top level: `margin_calculate_margins`,
`margin_convert_units`, `margin_compare_periods`, `margin_calculate_cashflow_metrics`,
`margin_calculate_profitability`, `margin_calculate_balance_sheet_metrics`. Use catalog
`mcp_execution` for routing. The generic calculator remains available. Financial results
include deterministic `financial_view` values, labels, units and scope warnings alongside
the raw payload. Optional shared mode keeps state in one explicit local backend across
frontend lifetimes; it does not persist a financial corpus or reset account quotas.

When available, use the host's Margin MCP tools rather than the separate HTTP helper.
The function inventory above is discoverable through 14 stable workflow tools:
`margin_status`, `margin_catalog`, `margin_preview`, `margin_company_preview`,
`margin_run`, `margin_run_status`, `margin_result`, `margin_sources`, `margin_facts`,
`margin_calculate`, `margin_cancel`, `margin_connect_drishti`, `margin_review` and
`margin_review_sources`. Catalog group names are `retrieval`, `calculations`, `company`,
`review` and `all`. `include_schemas: true` plus a name gets the exact nested contract.

Run/connect require the process session ID; run also requires a previewed plan and stable
idempotency key. Results contain call IDs for optional log correlation. There is no web
backend requirement, automatic provider connection, hidden data lookup or Margin-side LLM.
An explicit HTTP/CLI benchmark task still uses its configured bridge; do not silently switch
transport or reuse old private evaluator task/gold assumptions for an MCP experiment.
