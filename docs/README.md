# Documentation index and update responsibilities

`main` contains the core/workbench; the 7 November plan adds a bounded replayable research environment before broader product/MCP packaging. That environment is proposed, not delivered. The earlier corpus implementation and its guides/research are preserved on [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1), not delivered here. Start with README, context and status; read the remaining documents relevant to the task.

| Document | Authority |
| --- | --- |
| [Project README](../README.md) | Purpose, branch state and reading order |
| [Quick handoff: 9 November](../HANDOFF.md) | Short repo map and documentation-push summary; separates the professor's new notes from our response and existing product backlog |
| [Contributor instructions](../AGENTS.md) | Shared human/agent rules |
| [Context](context.md) | Concise current handoff and blockers |
| [Workbench guide](workbench.md) | Install/run/configure the implemented core and temporary interface; synthetic scenarios and executable checks |
| [Implementation status](implementation.md) | Delivered capabilities and dated validation |
| [Professor progress summary: 28 October](updates/progress-summary-2026-10-28.md) | Shareable summary under 1,000 words; a dated snapshot for meeting preparation, not the current status authority |
| [Delivery plan](plan.md) | Active milestones and evaluation gates |
| [Research-environment review and integration](design/research-environment-review.md) | 7 November code/plan audit against the professor's 2 November note; capture/replay architecture, independent answers, trajectories, rights/pricing findings, data feasibility and release gates; planning only |
| [Core/workbench design](design/core-workbench.md) | Active reusable core, temporary UI/HTTP adapter, run contracts, lifecycle, evidence and phase acceptance |
| [Financial functions and protocols proposal](design/analysis-and-protocols.md) | Longer-term calculation contracts, DCF, citation verification/LLM handoff, sentiment and protocols; its earlier first-release sequence is superseded by the research plan |
| [Later MCP design](design/mcp-aggregation.md) | Deferred downstream MCP packaging over the tested core; native tool/result contracts and later host gates |
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

One primary home per topic. Do not duplicate test totals, copy raw provider payloads into docs, add a document per conversation or turn a proposal into a delivered claim. Check links/anchors and applicable executable examples before handoff. For code changes establish and run appropriate lint/format/tests; documentation-only changes do not justify claiming a full suite.
