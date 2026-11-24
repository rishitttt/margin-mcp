# Financial facts and local calculations

Implemented **15 November 2026** over the existing Python core/workbench. Updated 24 November: the provider registry has thirteen retrieval operations; the local calculation catalog has fifteen functions, plus retained-result fact preparation and nine company financial workflows. See the [finance data-support decision](design/finance-data-support.md). Pure calculations make no network calls. A company workflow may include one explicitly previewed financials request. Ten local citation/sentiment handoff functions were added on 24 November; see [review workflows](review-workflows.md). Research capture/replay and downstream Margin MCP remain separate/deferred.

## Unit evidence: 24 November 2026

The current [BharatStock FAQ](https://bharatstockapi.com/) explicitly documents absolute INR
for monetary statement lines. EPS remains INR/share. This supports the HUL audit's declared
INR scale, but does not alter its historical receipts or independently verify every figure.
`money_unit: "auto"` is now the default for company planning and fact preparation. It uses reviewed provider documentation with `unit_origin: "provider_documentation"` and dated source evidence. Explicit null (or the facts query/CLI `unknown`) preserves unknown units. Explicit scales remain caller-declared; live BharatStock financials reject declarations conflicting with documented INR. Convert prepared facts separately. Raw financial rows are unchanged.

Unit handling must be path-specific: HUL snapshot root and ratios `market_cap` equal
10,000,000 times snapshot `metrics.market_cap`; the nested value is crore-scaled, consistent
with the [reference's screener convention](https://bharatstockapi.com/reference).
Drishti HUL earnings cells explicitly carry `Rs in crores` or `Rs/share`; its
[official examples](https://drishti.manasija.in/docs/use-cases/stock-brokers) also show
lakh-scaled earnings and event-level currency/unit fields. Never make a provider-wide
crore assumption. Counts, multiples, percentages and per-share amounts require separate types.

The earlier eight saved-input checks passed. The subsequent issuer-text review explains HUL revenue differences as product sales versus total operating revenue; these remain distinct metrics, not interchangeable values. Annual total/continuing profit also differs, so company margin now prefers returned continuing profit and flags mixed-scope group/owners ratios. See the [dated research finding](research/mcp-provider-feasibility.md#unit-evidence-audit-24-november-2026)
and private supplement `reports/private/unit-audit-HINDUNILVR-2026-11-24/REPORT.md`.
The original function-audit packet remains unchanged. The earlier unit-only investigation made no authenticated calls; subsequent repair usage is recorded in implementation status.

## Use the workbench

Start the backend using the [setup guide](workbench.md); after updating an older process, restart it and hard-refresh the page. Live mode uses real company data. Synthetic mode is labelled fictional software-test data.

1. Enter the ticker and exchange on the left. Choose **Finance** or **Retrieval**. The initial financial task does not execute or select provider requests.
2. Choose **Financial data readiness** first when unsure which fields are available. Select periods/basis and **Monetary unit policy → Auto · documented provider units**, then preview. The same policy applies to individual facts. Documentation evidence establishes the provider contract, not original-filing verification. Retrieval can be inspected without a unit selection.
3. Choose **Preview financial function**, review company/context, retained reuse versus one data request and costs, then **Run selected operations**. Changing inputs or task invalidates a preview. Stale asynchronous preview responses cannot reinstate an old plan. Inputs are locked during an active run.
4. Successful financial retrieval loads facts automatically. Open **Use individual financial facts** for source selection, suggested pairs and known period starts. Suggested values remain editable and pass the same compatibility checks. This mode also uses preview, then Run. Loading facts never replaces a displayed calculation result.
5. **Finance → Local function tester** exposes all fifteen local calculations with a selected schema and explicit JSON arguments. Preview, inspect arguments, then Run. The dedicated DCF tab/form is temporarily removed; valuation functions remain in the backend and local tester. JSON inputs are independent of the sidebar company and no forecast assumptions are prefilled.
6. Use **Recent runs** to inspect earlier output. The last selected run, company/task and listing-specific unit declaration are restored on reload when compatible. Only non-sensitive UI preferences/IDs are stored in session storage, not provider data. History returns at most twenty local control summaries; expired/evicted payloads remain unavailable and are not refetched. Switching company clears active facts, result selection and preview; an explicitly viewed other-company run stays labelled with its own context.

Changing the declared scale refreshes retained facts locally. Unknown/mixed units, missing fields, unsupported adjustment comparisons and incompatible periods return incomplete output. Enter period starts only when established. Same-period ratios may use fields from the exact same retained provider row when its start is absent; unrelated rows do not gain that exception. TTM needs actual dates and continuity.

Drishti connection and process limits are collapsible sidebar sections; limits start expanded. Drishti is required for event operations only; BharatStock financial functions do not require it. Snapshot, directory search, earnings details, selected facts and local JSON functions now all preview before execution. The UI defaults to Snapshot only in Retrieve data; it does not silently select paid event operations.

## Company financial functions

The **Finance** task needs no prior fact selection. Enter the listing on the left, choose the function, period type, consolidation basis and declared monetary scale, then preview. A matching retained financial response is reused automatically. If none exists, the checked **Allow one financials request** option adds exactly one BharatStock financials request to the preview, followed by the local calculation. Only Run executes it. Uncheck this option to forbid data calls.

| Company function | Automatic selection |
| --- | --- |
| `finance.company_margins` | Continuing profit when non-null, otherwise reported group profit; latest matching revenue; explicit scope in inputs |
| `finance.company_data_readiness` | Inspect latest fields, period availability, function outcomes and missing valuation assumptions |
| `finance.company_profitability` | Separately defined continuing/group/owners/operating/EBITDA margins; mixed scopes withheld |
| `finance.company_cash_conversion` | CFO/revenue, capex intensity, CFO-less-capex margin and eligible profit conversion |
| `finance.company_balance_sheet_metrics` | Current/cash ratios, working capital, gross/net borrowings and leverage from same-date stock facts |
| `finance.company_cashflow_metrics` | Operating cash flow and capex from that same period |
| `finance.company_growth` | Chosen metric from the latest two returned matching periods |
| `finance.company_cagr` | Chosen metric from two annual endpoints; elapsed years = endpoint days / 365.25 |
| `finance.company_ttm` | Chosen metric from four quarterly periods; requires established dates/continuity; normal calendar quarters may use reviewed explicit duration metadata |

These bounded selections are not claims about the latest available filing or long-term coverage. No basis substitution, extra page, fallback provider or forecast assumption is invented. Missing fields/dates/units return `incomplete` with reasons; metric groups may return `partial` with per-component status and formula. A matching response with missing fields is not silently replaced by another request. Explicit expired/mismatched sources also do not trigger replacement calls. DCF/FCFF still require explicit inputs; forecasts are not assembled automatically.

Company workflows and all fifteen explicit-input functions can return standard result cards through plans/runs. Active company calculations protect their source run from buffer eviction, subject to existing TTL/memory limits. Eviction prefers derived calculation cards before financial source runs, so repeated local calculations do not force paid refetches. Financial sources remain transient and evictable when necessary. Source and assumption context is retained in the result/receipt.

## Functions and limits

| Function | Inputs / behavior |
| --- | --- |
| `facts.prepare` | Retained successful BharatStock financial result; twelve reviewed metric paths, preserving total versus owners' profit, reported/diluted/adjusted EPS, original values and missing context. Drishti tables are not silently mapped into this fact model |
| `finance.calculate_profitability` | Typed aligned revenue/profit facts; per-component scope/missing checks |
| `finance.calculate_cash_conversion` | Aligned CFO/capex/revenue/profit; no missing values invented |
| `finance.calculate_balance_sheet_metrics` | Same-date stock facts; component formulas/units/status returned |
| `finance.reconcile_facts` | Unit-normalized value differences plus metric/context conflicts; no truth selection |
| `facts.check_compatibility` | Two to four facts; comparison/ratio/TTM purpose; issuer, unit, basis, metric/definition, period and adjustment checks |
| `facts.convert_units` | Explicit known INR monetary scales; conversion lineage; no inferred units or FX |
| `finance.compare_periods` | Absolute/percentage changes; nonpositive baseline gives an undefined percentage, not an ordinary growth claim |
| `finance.calculate_margins` | Defined profit/revenue, compatible period/basis/scale; positive revenue required |
| `finance.calculate_cashflow_metrics` | Operating cash flow and positive cash capex; surplus and coverage. CFO minus capex is not automatically FCFF |
| `finance.calculate_cagr` | Positive endpoints and explicit elapsed years consistent with their dates |
| `finance.calculate_ttm` | Four consecutive non-overlapping quarterly monetary flows, with known start/end dates. Rejects EPS/stocks, gaps and YTD spans; missing/longer/derived duration markers remain insufficient |
| `finance.calculate_fcff` | Explicit EBIT, decimal tax rate, D&A, positive capex and increase in noncash operating working capital, all in one declared amount scale |
| `finance.calculate_dcf` | One to twenty annual FCFF forecasts, WACC/growth, explicit debt/cash/other equity adjustments, optional diluted shares, amount unit, valuation date and `company_type=non_financial` |
| `finance.dcf_sensitivity` | Explicit base model plus up to nine rates per axis; at most 81 cells. Invalid combinations are marked rather than silently changed |
| `finance.run_scenarios` | Explicit base model plus up to five named overrides; no implicit probabilities, generated forecasts or investment ranking |

The pure functions live in `margin.analysis.facts`, `margin.analysis.calculations`, `margin.analysis.ratios` and `margin.finance.dcf`. `margin.analysis.service.calculate(function, arguments)` supplies schema-based dispatch. The reusable `ResearchService` adds credential checks and output bounds; routes do not implement financial arithmetic.

Fact and function schemas are available from the local catalog. Function version is `1.0`; financial decimal outputs are strings at 34 significant-digit calculation precision. The UI rounds for readability; the full record preserves decimal strings. Request/result byte bounds remain enforced. Inputs must be finite, bounded and context-compatible; validation is not a statement that an assumption is financially reasonable.

Reported EPS is not automatically adjusted. Comparing per-share facts requires a compatible adjustment state and shared adjustment reference. Adjusted fields preserve the provider value/factor and are not divided again. A shared retrieval timestamp is used only as a reference for the provider-adjusted fields within that response, not as independent proof of its methodology.

## DCF convention

```text
FCFF = EBIT × (1 − tax_rate) + D&A − capex − increase_in_operating_working_capital
PV(year t) = supplied_FCFF[t] / (1 + WACC)^t
Terminal value = final_supplied_FCFF × (1 + g) / (WACC − g)
Enterprise value = forecast PVs + discounted terminal value
Equity value = enterprise value − debt + cash + other_equity_adjustments
INR per share = equity value × amount_scale_in_INR / actual_diluted_share_count
```

Requires `0 < WACC <= 1`, `-1 < g < WACC`, positive terminal-year FCFF and a positive share count if supplied. Debt/cash are nonnegative; other adjustments are signed. Early negative cash flows and negative equity are retained. No automatic WACC, driver forecasting, FCFE, mid-year convention, bank model or provider-to-DCF input completion is implemented. Forecasts/assumptions remain caller supplied until Advait's work and source preparation are reviewed. Method reference: [CFA Institute free cash flow valuation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation).

## Local HTTP surface

| Method / route | Behavior |
| --- | --- |
| `GET /api/analysis/company-functions` | Nine company workflow names/descriptions; no network |
| `GET /api/analysis/sources` | Available retained financial source IDs/selectors; no network |
| `POST /api/analysis/plans` | Company workflow preview; resolve retained source versus one explicit dependency |
| `GET /api/runs` | Up to twenty local run control summaries; listing, operations and status; no payloads or refetch |
| `GET /api/analysis/functions` | Fifteen schemas/versions; local-only, zero provider credits |
| `POST /api/analysis` | `{function, arguments}`; returns calculation/compatibility result. Requires the existing action nonce, same-origin JSON and byte limits |
| `GET /api/runs/{run_id}/operations/{operation_id}/facts` | Prepare retained financial facts; optional `money_unit=INR`, `INR_thousand`, `INR_lakh` or `INR_crore`; default `auto`, explicit `unknown` preserves missing units |

Example company preview body for `POST /api/analysis/plans`:

```json
{"function":"finance.company_margins","ticker":"RELIANCE","exchange":"NSE","period_type":"annual","basis":"consolidated","metric":"revenue","money_unit":"auto","fetch_missing":true}
```

`money_unit: "auto"` uses reviewed documentation. Explicit null deliberately preserves unknown units and may produce an incomplete result. Declaring `INR` is a caller assertion, not verification. An optional `source: {"run_id":"...","operation_id":"..."}` selects an exact retained result; omitting it allows matching local reuse. Submit the returned plan through the existing `POST /api/runs`. Pure functions may also be submitted as `{operations:[{operation:"finance.calculate_dcf",arguments:{...}}]}` through `POST /api/plans` without a data dependency.

Malformed input returns a safe domain error. Valid but insufficient/incompatible facts return `status=incomplete`; non-meaningful arithmetic is labelled. Neither path invents inputs or calls a provider. Every result keeps source and assumption limitations visible.

## Retrieval contracts and evidence limits

`OperationResult.contract_version=1.1`. Receipts retain prior selectors plus full sanitized supplied/effective arguments and request/retrieval times. Effective arguments mean those sent to the provider: implicit provider defaults and relative-window evaluation are not known/frozen. The UTC receipt clock and overview as-of date can be injected for tests; this is not a replay implementation.

Fresh 15 November source inspection preceded the new financial functions. The annual sample contained CFO/capex; quarterly fields remained null. Adjusted EPS fields/factor and separate owners' profit were present. Units were absent at row level. See the [source checkpoint](research/mcp-provider-feasibility.md#fresh-payload-inspection-15-november-2026) for bounded costs and limitations. No newly observed values were copied into committed fixtures.

Software tests use invented numerical examples, including the independent constant-cash-flow perpetuity check. Source probes use real API calls and are reported separately. Neither a passing DCF test nor a provider agreement verifies the underlying financial statement. Advait's existing code has not yet been supplied; the current calculator is an independently testable explicit-input implementation behind a replaceable interface.
