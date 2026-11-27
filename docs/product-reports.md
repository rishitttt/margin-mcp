# Canonical product reports

Reports are deterministic data/presentation from Margin. They can be rendered directly
without an LLM. They do not prove source accuracy or guarantee how another host rewrites
them. Raw calculations retain exact decimal strings; displayed rounding is separate.

## Status — margin.status_report.v1

margin_status returns report.rows and report.markdown. HTTP rows contain provider,
local used/limit/remaining and unit HTTP_attempts. The Dr estimated-credit row is a
local admission estimate, not measured account debit. Provider account balance remains
unknown unless actually observed; this pass performs no account probes.

MCP status includes ledger/providers/version/owner/recording fields. Internal record
capacity, receipt count and historical balance are omitted by default. Request
include_diagnostics=true to inspect them under diagnostics. Migration: old MCP consumers
of company_finance_requests/receipt_count/last_historical_balance should use diagnostics;
core service/workbench status remain compatible. Internal capacities are not quotas.

## DCF — margin.dcf_report.v1

Typed and generic DCF calls return the same report alongside existing raw values:

| Row | Meaning |
| --- | --- |
| forecast_present_value | Discounted explicit future FCFF |
| terminal_value | Undiscounted terminal value at the forecast horizon |
| terminal_present_value | Terminal value discounted to valuation date |
| enterprise_value | Forecast PV plus terminal PV |
| equity_value | EV minus supplied debt plus supplied cash/other adjustments |
| value_per_share_inr | Equity converted from its monetary scale to INR per actual diluted share |

Rows carry metric/label/exact value/unit/display/status. Monetary displays preserve the
supplied INR scale; per-share output is INR_per_share. Null shares leave the per-share
row unavailable; negative equity is not floored. The report identifies input origin and
valuation date. Workbench renders these rows before generic scalar fields. Markdown is
bounded and escaped, generated from the same labels/displays, not model prose.

For the supplied test FCFF10/10/10, WACC0.1/growth0, debt20/cash5/adjustment-2/shares10
in INR: EV100, equity83, per-share8.3; terminal value100 at year3, terminal PV75.13.
This is explicit hypothetical arithmetic, not a company forecast or market valuation.

## Valuation input contract

Forecast FCFF is explicitly future free cash flow to the firm, not automatically CFO.
Debt is a reviewed bridge input, not total liabilities. WACC/growth are explicit decimal
assumptions, cash uses the same money scale, diluted_shares is actual shares rather than
crore/lakh shares. Missing inputs remain missing. No imputation, automatic forecasting,
hidden model or source authentication. The reviewed contract is embedded in schema
descriptions, readiness valuation metadata and the DCF report.

Company report rows retain their existing canonical crore/ratio/percentage format.
Readiness is nonnumeric eligibility, read report.readiness/valuation_readiness. It never
turns available fields into verified source facts. Limited inventory-adjusted liquidity
does not establish a fully adjusted quick ratio.
