# Margin 0.10.0

Local Python wheel; all39 remains the supported default. No npm, product LLM, database,
public publishing or automatic upgrade is required/performed.

Adds canonical local-allowance status reports with opt-in diagnostics, explicit DCF
input definitions and labelled DCF report rows rendered directly in the workbench.
Raw financial math and quote/unit/period/scope/idempotency guards remain intact.
Old MCP status consumers of company_finance_requests/receipt_count/last_historical_balance
must request include_diagnostics=true and read data.diagnostics; core status is unchanged.

[Install/upgrade](../../docs/mcp.md), [acceptance](../../docs/product-acceptance.md),
[report contracts](../../docs/product-reports.md), [checksum](SHA256SUMS).

644 offline tests, lint/format, browser/DOM, nine source SDK groups, nine installed-wheel
groups and clean macOS/Python3.12.10 installation pass. Selected real provider tests
used B2/DrHTTP10/estimated credits7. No account balances/source authenticity or arbitrary
host-model prose are verified. Hosted Linux/Windows results remain to be observed.
The user's independent mtest backend is unchanged; save logs before a manual upgrade.
