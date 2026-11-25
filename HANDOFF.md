# Margin: quick handoff

**Latest source 0.8.0:** ten typed review tools, clearer schema/JSON/size/sanitization
errors and actual next-step packet bindings. Full profile 35 tools; optional review
frontend 14 local tools, same shared owner and no provider dispatch surface. Exact
schemas come from canonical SCHEMAS, not remembered examples. 392 tests and SDK checks
pass; saved real INFY replay is operator-authored, not a model benchmark. See
[profile/setup](docs/mcp.md#typed-review-tools-profiles-and-packet-handoffs),
[plan/evaluation](docs/design/mcp-aggregation.md#080-review-repair-plan-and-evaluation-26-november-2026)
and [validation](docs/implementation.md). Active user backend stays 0.7.0; no live
upgrade/reset/fetch. Deliberately upgrade both sides, obtain valid source handles,
then switch only the frontend to review profile and follow returned next_steps.

**Latest source 0.7.0:** four typed Drishti previews generate their exact schemas from
reviewed Registry contracts and construct query wrappers internally. Generic calls
remain; obtain their exact schema from margin_catalog. Typed calls use the actual
host-advertised inputSchema. Missing-field diagnostics and explicit package_version
address the latest model failure. 25 tools, 360 offline tests; no new live/model call.
See [MCP guide](docs/mcp.md#typed-retrieval-previews-and-exact-schema-authority),
[plan/evaluation](docs/design/mcp-aggregation.md#070-typed-retrieval-preview-plan-and-evaluation-25-november-2026)
and [validation](docs/implementation.md). Active mtest is still 0.6.2; deliberate
version-matched activation/one-source host acceptance is next. Older notes are history.

**Latest, 25 November: 0.6.2 source/review patch.** Fresh INFY Drishti news,
announcement and earnings list/detail succeeded (B0/D10 HTTP, seven credits).
Fixed source import for single-record earnings and attachment links; summaries,
row symbols/paths, unknown dates and protected-link state are preserved. Real saved
response citation/sentiment checks and a host-read issuer-page handoff pass. No LLM
runs inside Margin. See [current status](docs/implementation.md), [function map](docs/reference/function-validation.md)
and [next host test](docs/review-workflows.md#small-model-acceptance-after-activation).
The active user's 0.6.1 setup remains untouched; its wheel remains in Git. No paid
upgrade is required for this small slice. Next: activate a matching patch backend/
frontend deliberately, test one concise source in LM Studio, then freeze the research
profile; wider Drishti admission and benchmark runs follow separately.

**Wheel in Git:** the exact tested 0.6.1 artifact and checksum are under
[`releases/0.6.1/`](releases/0.6.1/). Runtime source matches `36d10b7`; generated dist
outputs stay ignored. Read [installation](docs/mcp.md#install) for checksum/setup.
No keys/private captures are included and no live instance is changed by this addition.

**Latest user-led check, 25 November:** live mtest now runs 0.6.1; B1/D0 used and
local B1 spent. HUL completeness, INFY formulas/amounts and backend details projection
pass. Raw-versus-report prose is still incomplete despite the fields being returned.
No new runtime defect or release; no operator fetch/restart. See
[current validation](docs/implementation.md) before following older activation notes.

**25 November 0.6.1:** corrects per-metric formula metadata exposed by the live
0.6.0 retest. Values/units/arithmetic are unchanged. INFY numeric reporting improved;
HUL output omitted rows in the model answer, while all rows were present in the tool.
[Implementation](docs/implementation.md) records attribution, tests and private evidence;
[MCP guide](docs/mcp.md) owns formula contracts and version-matched upgrades. The
running live backend remains 0.6.0 with B2 spent. Do not reset or silently replace it.
For future work, follow the [documentation ownership map](docs/README.md).

**25 November 0.6.0:** [reporting contract v2](docs/mcp.md#reporting-contract-v2-and-migration)
separates canonical crore/per-share/percent/ratio rows from optional raw calculation
details. Rows include deterministic displays for calculated amounts; same-key
detail inspection makes no new fetch. Existing functions/guards remain. See
[implementation](docs/implementation.md) for tests and saved-response checks.
Point 4, host-enforced final-answer validation, stays deferred. The local 0.5.0 live
backend remains untouched; no new provider/model calls in this build.

**25 November 0.5.0:** [fresh-fetch finance](docs/design/fetch-and-calculate.md) is the new company-finance path: one typed MCP call can fetch and calculate without earlier financial source handles. Old retrieval, fact, calculation and review tools remain; 21 tools total. No database, Margin LLM or new provider/model calls. [MCP guide](docs/mcp.md) owns usage, version-matched upgrades and bounded request keys; [implementation](docs/implementation.md) owns validation. The running local 0.4.0 live installation is unchanged. BharatStock Developer is the current published internal model-evaluation option; no purchase was made.

**25 November 0.4.0:** current package adds deterministic financial views, six direct typed calculation tools (twenty total), and optional local shared state across stdio frontends. [MCP guide](docs/mcp.md) explains starting/stopping the state owner and configuring the host; [implementation](docs/implementation.md) separates software/transport evidence from actual model results. Plans/results stay in bounded memory and provider keys are not packaged. The older dated notes below are historical.

**25 November MCP alpha:** the core checkpoint and plan were pushed first (`6b22f57`, `07b981a`). Package 0.3.0 now has a tested 14-tool local stdio server, independent of the browser/skill. See [MCP setup](docs/mcp.md) and [implementation](docs/implementation.md) for 220 tests, protocol/wheel acceptance and remaining host/live validation. Secrets, numerical evaluator keys, raw response packets and old private ZIPs remain excluded from Git. Earlier push-status notes below are historical.

**25 November source checkpoint:** the core includes 37 retrieval/finance functions, ten local review functions, Python/CLI/skill access and the temporary workbench. Latest baseline: 192 tests; evaluator-key separation adds two checks. Plans/results and source limits are in [implementation status](docs/implementation.md) and [function validation](docs/reference/function-validation.md). Source-only publication excludes credentials, live captures, private bundles and the numerical evaluator key. Older push/local-status notes below are historical. The user has now authorized planning and building the MCP adapter after this checkpoint is pushed.

**16 November portability update:** [private local bundles](docs/portable-agent-bundle.md) now ship the skill/runtime/setup helpers, complete function inventory and evaluation-session visible-summary commands. The user authorized trial keys inside the ignored bundle's separate private file; no source/Git keys or live captures were added. 117 tests and relocated fictional process checks pass. Actual host/model evaluation remains pending; nothing new has been pushed.

**16 November local update:** [agent access](docs/agent-interface.md) now documents the Python package, new CLI/installed Codex skill and optional private pilot recorder. The CLI shares the workbench backend; the browser is optional. Full replay/evaluation and own MCP remain pending. These changes and the prior 15 November implementation are local, not a new push; the push summary below remains historical.

**9 November 2026 — repository map, documentation update and next steps.**

**15 November update:** the [active plan](docs/plan.md) now separates product development from the optional research harness. Product retrieval/facts/comparisons/DCF and later packaging come first; citation verification and sentiment protocols are parked. The push summary below remains the 9 November historical snapshot.

**15 November implementation (local, not yet committed/pushed):** retained financial facts, eleven local comparison/FCFF/DCF/sensitivity/scenario functions and workbench controls now exist. Fresh probes used three BharatStock requests and six Drishti credits (975 → 969); see [current implementation](docs/implementation.md) and [financial analysis](docs/financial-analysis.md). The professor/research material stays separate and the historical push summary below still describes 9 November.

**Later 15 November repair (also local):** automatic financial fact loading/source selection, five company financial workflows with previewed source reuse or one request, and standard result cards for financial calculations. A two-request real annual-financials browser pass and 94 offline tests cover the repair; see the latest implementation checkpoint. No new paid keys or Drishti calls were needed.

**Latest UX repair:** the interface now has Financial functions / Retrieve data / DCF & advanced with a shared preview → Run path, one listing-scoped unit control, stale company/preview isolation and recent local run history. Validation is 95 offline tests plus expanded browser acceptance and one additional live BharatStock request (zero Drishti calls). See the current workbench guide before following historical UI steps below.

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

## Our 9 November response and backlog (sequence superseded)

Next: establish permissions and task feasibility -> add opt-in capture/offline replay -> fix a company/question roster and independently review filing answers -> run and record agents -> release permitted artifacts and reproducible analysis. Start with three release companies; expand only if coverage supports it.

Candidate tasks cover EPS, latest profit, dividends per share and CFO versus capex. Corporate-action access and capex coverage still need validation. Current results expire; receipts omit some arguments, and warnings are not independent verification.

DCF/scenarios/sensitivity, host-LLM citation workflows, sentiment protocols and downstream MCP remain the **existing product backlog**. They can follow or proceed separately without blocking the first research release. Provider purchases, collection and public-data/model-use rights remain separate decisions. Use the delivery plan for current priorities; this file is a short navigation snapshot.
