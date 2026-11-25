# Function validation status

**0.7.0 typed preview checkpoint:** four event preview tools project reviewed
Registry contracts and call the same planner. 360 offline tests pass: direct/generic
plan equivalence, zero-fetch previews, strict nesting/field diagnostics, extraction/
selector/readiness guards, explicit run/import and package-versus-contract version.
SDK software acceptance covers 25 tools in standalone/shared modes. Generic operation
inventory and live data outcomes below are unchanged; no fresh provider/model call or
claim of improved host behavior. See [schema authority](../mcp.md#typed-retrieval-previews-and-exact-schema-authority).

**25 November first 0.6.2 model preview:** Drishti connection/schema refresh passed.
Three announcement previews failed locally because the host omitted arguments.query;
no data execution. Flat failure/nested acceptance reproduced offline. This is a host
input-shape error; upstream schema drift is not established. See
[corrected request](../review-workflows.md#first-062-host-preview-finding). Do not
count this trial as completed model retrieval/citation/sentiment acceptance.

## Drishti/review stage: 25 November 2026, 0.6.2

| Function/path | Current evidence | Remaining limit |
| --- | --- | --- |
| drishti.get_news | Fresh INFY two-row success | Multi-company results need host relevance; provider dates are not established publication dates |
| drishti.get_announcements | Fresh INFY one-row summary success, extraction=false | Attachment is a protected locator, not read text |
| drishti.list_earnings | Fresh INFY one-row success | Bounded response is not complete filing coverage |
| drishti.get_earnings_filing | Fresh discovered-ID success | Table accuracy/original authentication not established; this filing's raw/normalized revenue agrees |
| margin_review_sources | Real saved-response reprocessing of all four shapes passes after object/URL/protection-flag fixes | Zero new fetch; missing/unknown/mismatched sources remain incomplete |
| evidence.register_sources / prepare_verification / submit_assessment / render_citations / audit_answer | Real-summary host round trip; fabricated quote and verification overclaim rejected/flagged; host-read issuer-page passage also checked | Host judgments, no automatic original authentication or arbitrary final-prose audit |
| sentiment.prepare_analysis / submit_annotations / aggregate | Real-summary record-date scope, duplicate exclusion, unclear/missing labels and exact balance checked | Retrieved content only; unknown publication dates excluded in published mode |
| evidence.check_numeric_claim | Existing offline scale/context regression coverage retained | Not re-run against an independent issuer numeric answer in this pass |
| Drishti symbols / symbol resolution / categories | Earlier evidence retained | Not called in this INFY pass |

All four data calls succeeded; the original overall checker failed during subsequent
source import. The fixed projection was verified **offline**, not by repeating those
paid calls. Actual B0/D10 MCP HTTP including cleanup, seven estimated/observed account
credits, plus two free account GETs. See [implementation](../implementation.md) and
[test procedure](../api-testing.md). No new model-host completion is claimed.

## Patched live acceptance: 25 November 2026

HUL's cached all-rows retest now preserves profit, revenue and margin in final prose.
0.6.1 INFY money/formula reporting and same-key raw-details projection pass, with
one current-process BharatStock attempt and no Drishti. Raw-unit final-answer coverage
remains incomplete: tool details contain INR, but the model repeated canonical crore
rows. This is separate from correct backend projection; no new runtime defect was
found. Source figures remain provider-unverified. See [implementation](../implementation.md).

## Live rows and formula metadata: 25 November 2026, 0.6.1

The 0.6.0 INFY numeric rows, same-key repeat and details projection passed with B2/D0
total including HUL. HUL returned all three expected rows; the model reported revenue
only. Raw-detail prose and an invented margin_result lookup also failed fidelity.
Absolute-change formula metadata was incorrect in Margin itself, despite correct
numbers. 0.6.1 fixes per-result formulas and excludes CAGR's formula from input years;
321 offline tests pass, including regressions. [Implementation](../implementation.md)
owns attribution/evidence. No new live fetch/model acceptance or changed math is claimed.

## Reporting contract v2: 25 November 2026, 0.6.0

All nine company workflows retain their existing mathematics/data requirements and
now expose canonical structured report rows. Calculated amounts and source inputs
use matching reporting scales; raw calculation fields are optional details. Same-key
projection is tested without a second fetch. Saved 0.5.0 HUL margin and INFY growth
replies were reformatted offline with correct displays. These presentation checks
do not repeat live data calls, authenticate issuer values or establish model prose
accuracy; the observed 0.5.0 model reporting failures below remain failures.
See [implementation](../implementation.md) and [migration](../mcp.md#reporting-contract-v2-and-migration).

## User-led fresh live checks: 25 November 2026

On the 0.5.0 installed MCP, HINDUNILVR `finance.company_margins` and INFY
`finance.company_growth` succeeded with two total BharatStock attempts and no Drishti.
HUL duplicate replay used the same request ID/data without another fetch. Exact
arithmetic matches the returned INR inputs. Model prose still mis-scaled HUL profit
and INFY money amounts; tool execution and final-answer fidelity must be scored
separately. No original-source verification or fresh live execution of the other seven
company functions is claimed. [Implementation](../implementation.md) owns the full
observation and the distinction from saved-response/fictional-data checks below.

## Fresh-finance interface: 25 November 2026, 0.5.0

All nine existing company functions are now accessible through `margin_company_finance`:
fresh fetch and calculation in one explicitly executed call, without prior source handles.
All nine succeeded against complete fictional transport data. The saved-real column
below is offline reprocessing of the user's one-row HINDUNILVR annual response, not
a new provider call or independent answer key. No underlying math/guards were changed.

| Company function suffix | Complete fictional data | Saved HUL annual response |
| --- | --- | --- |
| `data_readiness` | success | success; reports supported/held components |
| `balance_sheet_metrics` | success | success |
| `cash_conversion` | success | partial; continuing/total-profit scope review |
| `profitability` | success | partial; continuing/total-profit scope review |
| `margins` | success | success; continuing profit selected, dates not invented |
| `cashflow_metrics` | success | success; CFO-minus-capex remains distinct from FCFF |
| `growth` | success | incomplete; only one returned annual period |
| `cagr` | success | incomplete; only one returned annual period |
| `ttm` | success | not tested with this annual-only response |

Every fresh execution uses at most one BharatStock request and zero Drishti requests.
New keys mean fresh requests; repeating the same financial inputs/key protects against
duplicates only in the current core process. Legacy reuse remains available separately.
The unchanged retrieval/local/review inventory and older live outcomes below remain
historical evidence. [Implementation](../implementation.md) owns release validation;
[MCP usage](../mcp.md) owns the new contract and limitations.

## Current repair checkpoint: 24 November 2026

Current inventory: **13 retrieval, 15 local calculation and nine company functions** (37), plus ten local review functions separately. **192 offline tests passed**. Fresh repair calls used B2/D13 HTTP including metadata/lifecycle, one estimated Drishti credit; actual debit was not measured. Summary announcements now succeed with the reviewed extraction flag explicitly false. Other retrieval outcomes below come from the earlier run and were not all repeated.

The final calculations reused the two fresh real responses after the continuing-profit scope repair, with zero additional requests. Thirty-two independent arithmetic checks matched. Selected issuer PDF text explains the three HUL revenue differences; full visual/download verification was unavailable.

| Company function | Annual | Quarterly |
| --- | --- | --- |
| `finance.company_data_readiness` | success | success |
| `finance.company_balance_sheet_metrics` | success | success |
| `finance.company_cash_conversion` | partial: mixed profit scope withheld | incomplete: CFO/capex absent |
| `finance.company_profitability` | partial: group/owners scope withheld | success |
| `finance.company_margins` | success: continuing profit | success: continuing profit |
| `finance.company_cashflow_metrics` | success | incomplete: CFO/capex absent |
| `finance.company_growth` | success | success |
| `finance.company_cagr` | success | not applicable |
| `finance.company_ttm` | not applicable | success: documented eligible intervals |

New low-level functions are `finance.calculate_balance_sheet_metrics`, `finance.calculate_cash_conversion`, `finance.calculate_profitability` and `finance.reconcile_facts`. Existing explicit FCFF/DCF/scenario/sensitivity math remains reference-tested; automatic company valuation still needs facts and assumptions. The [finance support map](../design/finance-data-support.md) and [complete skill inventory](../../skills/margin-research/references/functions.md) own definitions and input requirements.

Private current evidence: `reports/private/finance-repair-2026-11-24/REPORT.md`, `financials/` (fresh initial execution), `financials-final/` (final scope-aware reprocessing), `source-reconciliation.json`, announcement schema/live receipts and offline/browser/CLI evidence. Old packets below remain unchanged.

## Original HUL audit, before repairs

Updated 24 November 2026 for core 0.2.0. This reference separates software correctness evidence from a single fresh HINDUNILVR/NSE run. No original financial document or market fact was independently verified.

All 29 retrieval/local-calculation/company functions have passing offline orchestration/reference coverage in the 167-test suite. Fictional software fixtures are not real-company ground truth. The HUL audit made seven BharatStock and twelve Drishti HTTP attempts (eight estimated credits). Raw sanitized responses and receipts are private, not committed.

| Function | Purpose | Offline | HUL live-data outcome |
| --- | --- | --- | --- |
| `bharatstock.search_stocks` | Bounded security-directory lookup | passed | success |
| `bharatstock.get_stock_quote` | Security identity, snapshot and latest returned quote | passed | success |
| `bharatstock.get_stock_fundamentals` | Provider valuation/fundamental ratios | passed | success |
| `bharatstock.get_financials` | Annual and quarterly financial rows | passed | success |
| `bharatstock.get_stock_prices` | Bounded dated EOD price series | passed | success |
| `bharatstock.get_corporate_actions` | Bounded dividend/action records | passed | success |
| `drishti.get_news` | Bounded company-related news | passed | success |
| `drishti.get_symbols` | Company metadata/identity | passed | success |
| `drishti.resolve_symbols` | Company-name-to-symbol candidates | passed | success |
| `drishti.get_announcements` | Company announcements under the approved schema | passed | held_before_dispatch |
| `drishti.get_announcement_categories` | Announcement category taxonomy | passed | success |
| `drishti.list_earnings` | Find real earnings IDs/quarters | passed | success |
| `drishti.get_earnings_filing` | Retrieve one discovered earnings record/detail | passed | success |
| `facts.check_compatibility` | Check financial context compatibility | passed | success |
| `facts.convert_units` | Convert explicit monetary scales with trace | passed | success |
| `finance.compare_periods` | Absolute and percentage period change | passed | success |
| `finance.calculate_margins` | Profit/revenue margin | passed | success |
| `finance.calculate_cashflow_metrics` | CFO minus defined capex and coverage | passed | success |
| `finance.calculate_cagr` | Growth annualized over explicit duration | passed | success |
| `finance.calculate_ttm` | Sum four eligible consecutive quarterly flows | passed | incomplete |
| `finance.calculate_fcff` | Explicit EBIT/tax/D&A/capex/working-capital FCFF | passed | needs_explicit_inputs |
| `finance.calculate_dcf` | Discount explicit FCFF forecasts and equity bridge | passed | needs_explicit_inputs |
| `finance.dcf_sensitivity` | Bounded discount-rate/terminal-growth grid | passed | needs_explicit_inputs |
| `finance.run_scenarios` | Calculate explicit named valuation scenarios | passed | needs_explicit_inputs |
| `finance.company_margins` | Select retained company facts and calculate margin | passed | success |
| `finance.company_cashflow_metrics` | Select retained CFO/capex and calculate cash metrics | passed | success |
| `finance.company_growth` | Select eligible retained period pair and compare | passed | success |
| `finance.company_cagr` | Select retained annual endpoints and calculate CAGR | passed | success |
| `finance.company_ttm` | Select four retained quarters and calculate eligible TTM | passed | incomplete |

## Outcomes and limits

- 22 successful functions; two TTM paths incomplete because quarter starts are missing; announcements held for changed schema; four valuation functions require explicit inputs.
- Passing DCF/FCFF/scenario/sensitivity reference math is not automatic company valuation. No unsupported forecasts/working-capital assumptions were supplied.
- Annual cash-flow metrics succeeded; returned quarterly CFO/capex were null.
- A real discovered HUL q2_27 ID successfully selected earnings detail. This establishes live detail retrieval, not extraction correctness or original citation verification.
- Thirteen independent Decimal recomputations matched this run’s arithmetic. Caller-declared INR units and provider definitions remain unverified.
- The additional ten citation/sentiment review functions have passing separate offline/CLI/browser evidence; no claim that all were rerun as HUL semantic tasks.

## Inspect or reproduce

Private output: `reports/private/function-audit-HINDUNILVR-2026-11-24/REPORT.md`, `function-matrix.json`, `cases/`, `arithmetic-crosschecks.json`, `offline-tests.xml`, and the matching private ZIP. Keep the packet private; it contains provider response data, not keys.

The explicit opt-in runner is `scripts/audit_functions.py`; obtain a new bounded allowance before any repeat. It never overwrites an old run or retries a failed/uncertain paid branch. Schemas/source-code hashes are recorded. [API testing](../api-testing.md) owns setup/budgets; [financial analysis](../financial-analysis.md) and [review workflows](../review-workflows.md) explain interfaces.
