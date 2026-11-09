# Margin: quick handoff

**9 November 2026 — repository map, documentation update and next steps.**

## What is on main

Margin has a reusable Python financial-research core and a temporary local browser workbench. It integrates **BharatStock REST + Drishti MCP**, with 13 reviewed operations, bounded execution, sanitization, receipts and expiring results. The user's 21 October RELIANCE demonstration showed selected successful calls across both providers. Broader coverage, financial accuracy and actual billing remain unverified.

The 7 November audit passed lint/format and 50 offline tests. This push adds documentation and plans; **it does not implement replay, an agent runner, DCF, citation verification, sentiment protocols or Margin's own MCP server**. The previous corpus/PDF project remains on `d1`.

## Where everything is

| Location | Purpose |
| --- | --- |
| [README](README.md), [workbench guide](docs/workbench.md) | Overview, installation and running locally |
| [Core](src/margin/core/), [providers](src/margin/providers/) | Operation contracts, registry, coordination and upstream clients |
| [Policy](src/margin/policy/), [evidence](src/margin/evidence/) | Local budgets, sanitization, warnings and source locators |
| [Workbench](src/margin/interfaces/workbench/), [tests](tests/) | Local HTTP/static interface and offline regression coverage |
| [Implementation status](docs/implementation.md), [context](docs/context.md) | Delivered/observed behavior, limitations and current handoff |
| [Documentation index](docs/README.md), [AGENTS](AGENTS.md) | Reading order and documentation/contribution responsibilities |
| [Provider research](docs/research/mcp-provider-feasibility.md), [function reference](docs/reference/drishti-functions.md), [API testing](docs/api-testing.md) | Dated findings, tool/endpoint mappings and bounded testing procedure |

## What this documentation push includes

- [Research review and architecture](docs/design/research-environment-review.md): current-code gaps, proposed integration, task/data feasibility, dated subscription/rights findings and release gates.
- [Revised delivery plan](docs/plan.md): active priorities and human workstreams.
- [Finance/protocol design](docs/design/analysis-and-protocols.md): detailed longer-term function contracts.
- Updated README, handoff/context, implementation checkpoint, contributor instructions and design cross-references.
- [Earlier professor progress summary](docs/updates/progress-summary-2026-10-28.md): preserved as a historical snapshot, not the new scope.

Credentials, private responses and source PDFs are excluded.

## Professor's new notes — separate from delivered work

The supplied **“Margin: The Research Vision and the First Public Release” (Nikhil George, 2 November)** proposes studying how agents acquire and combine evidence. Its three separate objects are the **environment**, the agent's **trajectory**, and an **independently verified answer key**.

It requests bounded frozen responses, fixed ordinary financial questions, filing-grounded answers, genuine iterative tool-use decisions and reproducible records. Approximately six companies/four questions/two models would yield 48 trajectories; smaller credible studies are acceptable. A new MCP server and general DCF are not prerequisites. Public replay depends on data permissions. This section summarizes the supplied notes; it does not mean those requirements are implemented.

## Our proposed response and existing product backlog

Next: establish permissions and task feasibility -> add opt-in capture/offline replay -> fix a company/question roster and independently review filing answers -> run and record agents -> release permitted artifacts and reproducible analysis. Start with three release companies; expand only if coverage supports it.

Candidate tasks cover EPS, latest profit, dividends per share and CFO versus capex. Corporate-action access and capex coverage still need validation. Current results expire; receipts omit some arguments, and warnings are not independent verification.

DCF/scenarios/sensitivity, host-LLM citation workflows, sentiment protocols and downstream MCP remain the **existing product backlog**. They can follow or proceed separately without blocking the first research release. Provider purchases, collection and public-data/model-use rights remain separate decisions. Use the delivery plan for current priorities; this file is a short navigation snapshot.
