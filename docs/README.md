# Documentation index and update responsibilities

`main` contains the core, local stdio MCP alpha, workbench, CLI and skill. See [MCP setup](mcp.md) for the 0.6.1 server and host-neutral configuration. The 24 November [build plan](plan.md) covers retrieval/finance repairs, citation and content-sentiment workflows, capability-aware fallbacks, thin MCP packaging and a separate cross-model benchmark with short decision trails. Review handoffs and finance repairs are delivered; The stdio MCP alpha is delivered; selected LM Studio observations are recorded; broader host/model evaluation and the separate benchmark remain planned. The professor's research harness remains optional and independent of product installation. Historical corpus code stays on `d1`.

| Document | Authority |
| --- | --- |
| [Self-contained company finance](design/fetch-and-calculate.md) | Fresh-fetch execution contract, subscription findings and build/acceptance plan |
| [Project README](../README.md) | Purpose, branch state and reading order |
| [Quick handoff](../HANDOFF.md) | Current release/activation state and repo map; dated professor-note and older push summaries remain below |
| [Contributor instructions](../AGENTS.md) | Shared human/agent rules |
| [Context](context.md) | Concise current handoff and blockers |
| [Workbench guide](workbench.md) | Install/run/configure the implemented core and temporary interface; synthetic scenarios and executable checks |
| [MCP setup](mcp.md) | Delivered stdio tools, configuration, process budgets, logs, usage and protocol/packaging validation |
| [Agent interface](agent-interface.md) | Python/CLI/skill packaging, shared backend, fresh-chat setup, command contracts and the separate optional private pilot recorder |
| [Portable local agent bundle](portable-agent-bundle.md) | Private ZIP distribution, optional trial keys, per-agent setup, complete function coverage and visible-summary logging for evaluation |
| [Live skill evaluation](live-skill-evaluation.md) | Separate two-ticker runner/evaluator packages, live-call budgets, visible tool-choice summaries, submission export and gold/manual-review limits |
| [Review workflows](review-workflows.md) | Delivered no-inference citation/sentiment functions, CLI/HTTP/UI usage, origins, state, capability fallbacks and limitations |
| [Finance scope and data support](design/finance-data-support.md) | Implemented financial groups, observed inputs, deferred analytics, MCP design references and HUL definition findings |
| [Financial analysis](financial-analysis.md) | Implemented facts/calculations/DCF contracts, workbench usage, local HTTP surface and limitations |
| [Implementation status](implementation.md) | Delivered capabilities and dated validation |
| [Function validation matrix](reference/function-validation.md) | Current inventory, dated HUL/INFY outcomes, tool-versus-model failures and private evidence locations |
| [Professor progress summary: 28 October](updates/progress-summary-2026-10-28.md) | Shareable summary under 1,000 words; a dated snapshot for meeting preparation, not the current status authority |
| [Delivery plan](plan.md) | Active milestones and evaluation gates |
| [Research-environment review and integration](design/research-environment-review.md) | Historical 7 November audit and research proposal: capture/replay, independent answers, trajectories, dated rights findings and feasibility; 15 November separates this optional harness from product delivery |
| [Core/workbench design](design/core-workbench.md) | Active reusable core, temporary UI/HTTP adapter, run contracts, lifecycle, evidence and phase acceptance |
| [Financial functions and protocols proposal](design/analysis-and-protocols.md) | Financial/citation/sentiment contracts and capability-routing/fallback design; the current build plan owns active priorities |
| [MCP architecture](design/mcp-aggregation.md) | Published implementation plans, public tool mapping, lifecycle/state/logging rules and dated acceptance |
| [Provider feasibility](research/mcp-provider-feasibility.md) | Dated endpoint/tool/schema inspection, plans, limits, coverage and public probes |
| [API/MCP testing](api-testing.md) | Accounts/credentials, bounded test approach and evidence to record |
| [Drishti function reference](reference/drishti-functions.md) | Current confirmed operation map, nested inputs, REST relationships, cost/evidence limits and derived JSON schema snapshot |

## What to document and where

The person or agent changing a component owns its documentation update in the same change. Code/observed outputs establish behavior; documents must distinguish proposed, delivered, measured, unverified and historical states.

| Change | Update |
| --- | --- |
| Capability added/removed or material limitation | Implementation status; refresh context/README if affected |
| Core, interface, schemas or operation policy | Core/workbench design; later MCP design for protocol-specific changes; workbench guide for executable setup/usage |
| Source/endpoint/plan investigation | Provider research: date, URL, method, version/hash, outcome and limits |
| Test client, setup or validation procedure | Workbench guide for local commands; API testing: requirements, commands, defaults, bounds and failure behavior; actual results in implementation/research |
| Scope, priority, benchmark or budget | Delivery plan and relevant design; context for the next actionable step |
| Research snapshot, tool profile, task, answer key or trajectory | Research design and versioned manifests/codebook when implemented; record source rights, selection/as-of rules, full request identity, independent review and exact reproduction claim; keep restricted records and private gold outside agent/public paths |
| Credential/data-serving/retention policy | AGENTS and relevant design/usage; state provider permissions still unresolved |
| Document added/moved/retired | This index and inbound references; point historical material to `d1` |
| Live/model test or defect | Implementation and function matrix: tested version, exact trigger, expected/actual result, provider attempts, source verification limits and whether the fault is in Margin or model prose; private captures and original defective results stay excluded from Git |

For further development, start with context and HANDOFF, then the owning contract above.
Record a reproduction/regression check with each confirmed defect. Distinguish source/
wheel version from the active installed backend: publishing a fix does not patch a
running process or renew its quota. Preserve original evidence before creating corrected
offline projections. Visible why summaries and pasted final answers are not hidden
reasoning; note missing model/context metadata instead of guessing. Update the relevant
contract, implementation, function map and handoff in the same change, then validate
links and appropriate checks before pushing. Plans, implemented behavior, offline
checks, actual live calls and model-answer fidelity are separate evidence categories.

One primary home per topic. Do not duplicate test totals, copy raw provider payloads into docs, add a document per conversation or turn a proposal into a delivered claim. Check links/anchors and applicable executable examples before handoff. For code changes establish and run appropriate lint/format/tests; documentation-only changes do not justify claiming a full suite.
