# Margin

Margin aggregates Indian listed-company financial and event data from **BharatStock REST** and **Drishti MCP**. It provides deterministic financial calculations and host-side citation/content-sentiment workflows without maintaining a financial corpus or running an LLM server.

Current release: **0.10.0**, Python3.12+. The default local MCP advertises39 tools; finance6/review16/simple3 are optional views. Generic and typed APIs use the same core. [Wheel](releases/0.10.0/margin_research-0.10.0-py3-none-any.whl) · [checksum](releases/0.10.0/SHA256SUMS).

- [Install/connect](docs/mcp.md): standalone or explicitly started shared backend; keep all if preferred.
- [Current status and measured limits](docs/implementation.md).
- [Deterministic status/DCF reports](docs/product-reports.md): direct rendering, explicit units/timing and input definitions.
- [Bounded live checks](docs/api-testing.md), [product plan](docs/product-completion.md), [release checks](docs/release-checks.md).
- [Financial functions](docs/financial-analysis.md), [review protocols](docs/review-workflows.md), [all documentation](docs/README.md).

The latest bounded pass succeeded on INFY annual financial readiness, HUL quarterly financials, and INFY news/announcements/earnings discovery/detail. Two real financial responses supported local checks of all nine company workflows. This is selected-case validation, not universal company coverage or source authentication. Actual usage: B2/DrHTTP10/7 estimated Drishti credits; account debits were not queried.

0.10.0 adds clear local-allowance reports, opt-in internal diagnostics, explicit valuation-input definitions and labelled DCF report rows rendered directly in the workbench. Existing financial math, source/scope checks and duplicate protection remain. Models may still rewrite tool results incorrectly; canonical reports can be displayed without model narration.

The product stores only bounded transient state and optional private diagnostic logs. It does not automatically browse originals, generate forecasts or verify source authenticity. Review judgments are host-supplied. DCF requires explicit assumptions and supports the initial non-financial-company template.

Local wheel installation is available. Public PyPI publication and remote hosting are separate actions, not performed by this release. The professor's evaluation harness remains independent and outside this product pass. [Historical development notes](docs/archive/README.md) preserve earlier evidence and setups; corpus work remains on d1.

## Historical section links

<a id="current-state"></a>[Historical: Current state](docs/archive/2026-11-27-readme.md#current-state)

<a id="run-locally"></a>[Historical: Run locally](docs/archive/2026-11-27-readme.md#run-locally)

<a id="existing-source-evidence"></a>[Historical: Existing source evidence](docs/archive/2026-11-27-readme.md#existing-source-evidence)

<a id="start-here"></a>[Historical: Start here](docs/archive/2026-11-27-readme.md#start-here)

<a id="access-and-subscriptions"></a>[Historical: Access and subscriptions](docs/archive/2026-11-27-readme.md#access-and-subscriptions)
