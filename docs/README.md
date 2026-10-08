# Documentation index and update responsibilities

`main` owns the new aggregated-MCP work. The earlier implementation and its guides/research are preserved on [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1), not delivered here. Start with README, context and status; read the remaining documents relevant to the task.

| Document | Authority |
| --- | --- |
| [Project README](../README.md) | Purpose, branch state and reading order |
| [Contributor instructions](../AGENTS.md) | Shared human/agent rules |
| [Context](context.md) | Concise current handoff and blockers |
| [Implementation status](implementation.md) | Delivered capabilities and dated validation |
| [Delivery plan](plan.md) | Active milestones and evaluation gates |
| [Aggregation design](design/mcp-aggregation.md) | Proposed architecture, native contract policy and later semantic tools |
| [Provider feasibility](research/mcp-provider-feasibility.md) | Dated endpoint/tool/schema inspection, plans, limits, coverage and public probes |
| [API/MCP testing](api-testing.md) | Accounts/credentials, bounded test approach and evidence to record |

## What to document and where

The person or agent changing a component owns its documentation update in the same change. Code/observed outputs establish behavior; documents must distinguish proposed, delivered, measured, unverified and historical states.

| Change | Update |
| --- | --- |
| Capability added/removed or material limitation | Implementation status; refresh context/README if affected |
| Architecture, schemas or tool policy | Aggregation design; document the implemented contract and usage separately when code exists |
| Source/endpoint/plan investigation | Provider research: date, URL, method, version/hash, outcome and limits |
| Test client, setup or validation procedure | API testing: requirements, commands, defaults, bounds and failure behavior; actual results in implementation/research |
| Scope, priority, benchmark or budget | Delivery plan and relevant design; context for the next actionable step |
| Credential/data-serving/retention policy | AGENTS and relevant design/usage; state provider permissions still unresolved |
| Document added/moved/retired | This index and inbound references; point historical material to `d1` |

One primary home per topic. Do not duplicate test totals, copy raw provider payloads into docs, add a document per conversation or turn a proposal into a delivered claim. Check links/anchors and applicable executable examples before handoff. For code changes establish and run appropriate lint/format/tests; documentation-only changes do not justify claiming a full suite.
