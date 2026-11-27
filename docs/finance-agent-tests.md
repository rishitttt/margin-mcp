# Product smoke tasks

These are product checks, not the professor benchmark. Keep all if preferred. Record actual calls/results separately from final prose; no hidden reasoning. Start fresh chats after upgrade/reconnect and keep the model/context/preset recorded when comparing behavior.

## Zero-provider status

Prompt: Use the connected Margin MCP to inspect version, profile, tool count and local provider allowances. Make no provider requests.

Expected0.10.0/all39. Read canonical report: local HTTP allowance/estimated Dr credit budget, account balance unknown. Internal capacities require include_diagnostics and are not credits. No catalog schema dump is needed for tool count.

## Preview-only readiness

Prompt: Use Margin MCP to preview one annual consolidated INFY financial response that would determine which profitability, cash-conversion and liquidity calculations the returned fields support. Do not fetch or calculate values yet. Explain how the later readiness result and valuation prerequisites would be read.

Expected typed readiness or correct generic data_readiness, execute=false, no fetch. Later result fields report.readiness/report.valuation_readiness; missing execution key is not missing preview input. No CFO->FCFF, liabilities->debt mapping or generated DCF assumptions.

## Explicit local DCF

Prompt: Use Margin MCP for an explicitly hypothetical DCF: annual forecast FCFF [10,10,10] INR; WACC0.10; terminal growth0; debt20 INR; cash5 INR; other equity adjustments-2 INR; diluted shares10; valuation date2026-11-27; company type non_financial. Make no provider calls. Report enterprise, equity and per-share values using the canonical report.

Expected EV100/equity83/per-share8.3 INR. Terminal value at year3 is100; its discounted PV75.13. Assumptions are supplied, not retrieved/source-verified. Optional negative inputs should reject, never trigger a data fetch.

## Real-provider checks

Use [bounded API tests](api-testing.md) only with a new allocation. Current completed pass is B2/DrHTTP10/estimated credits7. [Function status](reference/function-validation.md) distinguishes live, local replay and software fixtures. [Historical agent tasks/results](archive/2026-11-27-docs-finance-agent-tests.md) remain frozen.

## Historical section links

<a id="test-finance-discovery-through-margin"></a>[Historical: Test finance discovery through Margin](archive/2026-11-27-docs-finance-agent-tests.md#test-finance-discovery-through-margin)

<a id="what-is-already-available"></a>[Historical: What is already available](archive/2026-11-27-docs-finance-agent-tests.md#what-is-already-available)

<a id="immediate-no-call-model-test"></a>[Historical: Immediate no-call model test](archive/2026-11-27-docs-finance-agent-tests.md#immediate-no-call-model-test)

<a id="live-model-tasks-and-prerequisites"></a>[Historical: Live model tasks and prerequisites](archive/2026-11-27-docs-finance-agent-tests.md#live-model-tasks-and-prerequisites)

<a id="set-margin_bharatstock_requests-to-the-newly-authorized-remaining-test-allocation"></a>[Historical: Set MARGIN_BHARATSTOCK_REQUESTS to the newly authorized remaining test allocation.](archive/2026-11-27-docs-finance-agent-tests.md#set-margin_bharatstock_requests-to-the-newly-authorized-remaining-test-allocation)

<a id="measured-operator-checks--27-november"></a>[Historical: Measured operator checks — 27 November](archive/2026-11-27-docs-finance-agent-tests.md#measured-operator-checks--27-november)
