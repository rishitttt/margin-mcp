# Finance scope and data support

Reviewed 24 November 2026. This is the finance capability decision and data-requirements
map; [financial analysis](../financial-analysis.md) owns usage and [implementation status](../implementation.md)
owns measured checks. The active scope uses BharatStock REST and Drishti MCP, with no
maintained corpus or Margin-side LLM. Margin now has standalone/shared local MCP adapters; see [current MCP setup](../mcp.md).

## What a finance MCP should provide

MCP defines tool access, not a mandatory financial-metric inventory. Two useful patterns
are provider-data access and deterministic analysis. FMP's [first-party MCP](https://site.financialmodelingprep.com/developer/docs/mcp-server)
exposes its REST datasets through tools. The [Finance Toolkit author's MCP](https://www.jeroenbouma.com/projects/financetoolkit/mcp)
adds defined calculations grouped into categories. These are design references, not claims
that those providers offer the Indian coverage or trial entitlements Margin needs.

Margin should offer bounded retrieval plus small, understandable financial groups with
typed inputs, source paths, periods, units, definitions, formulas and missing-data reasons.
Agents choose the analysis; code calculates it. Do not duplicate every vendor ratio as a
separate MCP tool or imply that a function is company-data-ready merely because its math
works on explicit inputs. Final MCP exposure/grouping remains a later design decision.

## Implemented and supportable now

| Function/group | Required data | Observed support and limit |
| --- | --- | --- |
| Identity, financials, ratios, prices, actions | Explicit ticker/exchange and bounded request | All six BharatStock operation types were tested; history/coverage remains company/plan dependent |
| News, earnings discovery/detail, announcements | Company selectors, dates, real record IDs, valid Drishti metadata | Earnings detail and repaired summary announcements executed; no general extraction/citation accuracy guarantee |
| `finance.company_data_readiness` | One retained annual or quarterly financial response | Reports eligible function statuses, null fields and required valuation assumptions; no automatic extra page |
| `facts.check_compatibility`, `facts.convert_units` | Typed values/context and known units | Existing functions; auto fact units now retain provider-documentation origin; explicit unknown stays unknown |
| `finance.company_margins` / `finance.calculate_margins` | Same-period monetary profit and revenue | Company wrapper prefers separately reported continuing profit; mixed total/continuing scope is held for review |
| `finance.company_profitability` / `finance.calculate_profitability` | Revenue plus group/owners/continuing/operating/EBITDA profit fields | Returns each available defined margin; mixed-scope group/owners margins are withheld; operating profit is not renamed EBIT |
| `finance.company_growth` / `finance.compare_periods` | Compatible metric/basis in two periods | Annual endpoint and adjacent-quarter growth work; this is not automatic YoY discovery for quarterly data |
| `finance.company_cagr` / `finance.calculate_cagr` | Positive annual endpoints and elapsed duration | Two annual rows support a short endpoint CAGR, not five-year growth; no broad history fetch |
| `finance.company_ttm` / `finance.calculate_ttm` | Four continuous, eligible monetary quarters | Normal calendar quarters with both duration markers explicitly null can establish starts from the reviewed provider contract; missing/longer/derived/basis-change cases remain incomplete |
| `finance.company_cashflow_metrics` / `finance.calculate_cashflow_metrics` | CFO and positive cash capex for the same period | Annual HUL supports CFO minus capex and coverage; quarterly fields are null; CFO minus capex is not automatically FCFF |
| `finance.company_cash_conversion` / `finance.calculate_cash_conversion` | CFO, capex, revenue and group profit, aligned | CFO margin, capex intensity and CFO-less-capex margin work annually; group-profit conversion is held if continuing/total scope differs |
| `finance.company_balance_sheet_metrics` / `finance.calculate_balance_sheet_metrics` | Same-date stocks: current assets/liabilities, inventory, cash, current/non-current borrowings, group equity, total assets/liabilities | Current/cash ratios, working capital, defined borrowings/net borrowings and leverage; missing components are individually withheld; stocks are never TTM-summed |
| `finance.reconcile_facts` | Two typed facts with definitions and units | Converts compatible monetary scales and reports differences/context conflicts; numerical agreement does not establish matching definitions or truth |

These groups return `success`, `partial`, `incomplete` or per-component `not_meaningful` /
`needs_scope_review`. A successful readiness inspection can report that a requested
calculation is incomplete. Partial output must not silently replace missing components
with zero. Denominators requiring positive values are checked before arithmetic.

## Explicit-input valuation remains useful, but is not automatic

`finance.calculate_fcff` requires explicitly defined EBIT, tax rate, D&A, cash capex and
increase in noncash operating working capital. `finance.calculate_dcf` needs forecasts,
WACC, terminal growth, a debt/cash/equity bridge, and actual diluted shares for per-share
output. `finance.dcf_sensitivity` and `finance.run_scenarios` calculate caller-specified
assumptions over that model. Their reference math is tested independently.

Current responses contain candidate tax, D&A, borrowings/cash and working-capital fields.
That does not establish EBIT, operating working-capital scope, diluted share count at the
valuation date, an appropriate discount rate, or future cash flows. Auto-generated HUL
valuation remains unavailable. Do not silently use EBITDA/operating profit as EBIT, total
liabilities as debt, paid-up capital as shares, statutory tax as effective tax, or current
annual CFO as a perpetuity forecast. Banks/NBFCs/insurers need separate valuation models.

## Next functions, ordered by data feasibility

| Candidate | Do we have enough? | Decision |
| --- | --- | --- |
| Price return / price CAGR | Bounded dated adjusted prices are available | Good next small function; define endpoints and adjustments, separate price return from dividend-reinvested total return |
| YoY quarterly growth | Needs same fiscal quarter a year earlier; four recent rows do not contain it | Add explicit fifth-row selection only with reviewed history/budget; never label QoQ as YoY |
| Average-equity ROE / average-assets ROA | Two annual balance sheets plus aligned annual profit are candidate inputs | Feasible next after profit scope and full-period duration checks; group vs owners equity must be matched |
| Asset/inventory/receivables turnover | Annual flows and opening/closing stocks, plus definitions such as COGS or credit sales | Partly available; do not substitute total expenses for COGS or revenue for credit sales without an explicit model |
| Recomputed P/E, P/B, EV/EBITDA | Quote plus compatible EPS/owners book equity/share count/TTM EBITDA/debt/cash dates | Vendor ratios already retrievable; recomputation needs denominator/as-of/adjustment contracts, so no automatic equivalent yet |
| Dividend yield/payout | Dated dividend actions, matching price and profit/share basis | Available candidates but one recent dividend is not a full-year yield; require a bounded complete window |
| Historical FCFF from filings | EBIT/effective-tax/working-capital definitions and aligned dates | Inputs are partial candidates; no automatic support claim yet |
| Volatility/drawdown | A sufficiently long, continuous adjusted price window | Feasible later; the ten-row audit sample is not evidence of annual risk coverage |
| Beta, Sharpe, VaR, portfolio analytics | Benchmark/portfolio data, risk-free rate, sampling/window/model choices | Missing supported contracts; postpone rather than output false precision |
| Sector regulatory/credit ratios | Sector statements and specific capital/RWA/NPA/maturity definitions | Some provider fields exist, but not reviewed as Margin calculations; separate sector phase |
| Sentiment and citation semantics | Original content and host judgments | Existing local handoffs; do not use sentiment scores as deterministic forecasts or treat supplied quotations as authenticated originals |

The priority is richer context and honest availability, not adding unsupported formulas.
Paid access may improve history/universe limits; it does not fix metric definitions or
supply valuation assumptions. Existing trials sufficed for this bounded repair pass.

## HUL findings that changed the implementation

The [issuer's results](https://www.hul.co.in/files/hul-sq-26-results.pdf), also
[filed on NSE](https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026094634_SEIntimationOutcomeofBM28102026signed.pdf),
distinguish product sales from total operating revenue. Their three-column differences
are explained by services plus other operating revenue. Drishti's field named revenue
(including its raw variant in this sample) corresponds to product sales; BharatStock
matches the wider operating-revenue measure. This resolves the observed definition
question, not every provider value. No issuer-specific rule or corrected number is
hard-coded into runtime code. Source textual review is narrower than full visual/filing
verification; local PDF downloads/viewing were unsuccessful during this pass.

Annual total and continuing profit also differ. The company margin now selects a non-null
continuing-profit observation when returned, preserving its definition in inputs. Mixed
group/owners ratios are flagged instead of quietly returning a broad net margin. The
prior private reports remain unchanged historical evidence of the earlier calculation.

## Acceptance and retained evidence

The private `reports/private/finance-repair-2026-11-24/` packet separates initial fresh
annual/quarterly calls, the later scope-repair reprocessing of those same real responses,
the announcement schema review/live execution, offline tests and fictional UI/CLI checks.
No further calls were made merely to repeat calculation checks. Source values remain
unverified except for explicitly scoped issuer-text comparisons.

The source skill and catalog mirror the implementation. Old evaluation ZIPs remain
frozen. No provider purchase, model API call, public hosting or MCP packaging is implied.
