# Delivery and evaluation plan

Updated **7 November 2026** after reviewing the current code, the 29 October product proposal and the professor's 2 November research note. This is planning, not new implementation or authorization for paid calls/publication. The [complete review and architecture](design/research-environment-review.md) owns the audit, record contracts, task/data matrix, rights/pricing findings and research design. [Implementation status](implementation.md) owns delivered behavior. The [finance/protocol proposal](design/analysis-and-protocols.md) remains the longer-term product backlog.

## Current objective

Deliver a small, inspectable research environment over the existing Python core: individually callable operations, bounded frozen responses where permitted, fixed ordinary financial questions, independently filing-verified answer keys and genuine recorded agent trajectories. Keep BharatStock REST + Drishti MCP and the local workbench. A new downstream MCP server, general DCF, full sentiment workflow and universal provenance framework are not first-research-release dependencies.

The existing thirteen-operation core remains useful. Replay, capture, task/gold records and the agent runner do not yet exist. The 7 November audit passed lint/format and 50 offline tests; the latest selected live workflow evidence remains the user's 21 October RELIANCE export. Software checks do not establish source accuracy, current account rights or market-wide coverage.

## Build sequence

Estimate roughly **3–5 working weeks for four contributors after feasibility and permissions are settled**, with source review and implementation overlapping. No new project deadline is inferred. Reduce companies/tasks before reducing evidence fidelity or independent review.

| Stage | Work package | Exit gate |
| --- | --- | --- |
| 0 — feasibility, first 2–3 team days | Applicable provider/account agreements; private retention/public release/model-use scope; request-to-question coverage; two development-company filing checks; explicit collection/cost manifest | Choose exact public capture, restricted collection or separately labelled filing reconstruction; at least one viable task family with independent evidence |
| 1 — foundation, 4–6 days | Full request identity and pinned clock; opt-in capture journal; immutable manifest; offline replay; selected real-shape/detail/citation repairs | Replay needs no key/network/live metadata; stable supported responses, distinct unsupported/empty/failure states, safe crash/write behavior |
| 2 — cases, parallel 4–7 days | Predeclare selection rule/roster/questions before agent outcomes; permitted bounded collection; independent answer keys and cross-review; freeze versions | Every task has observable evidence or justified insufficiency; source rights, periods, units, basis and transformations explicit |
| 3 — experiments, 3–5 days | Iterative model runner, ordered event logs, fixed model/tool profiles and budgets; development smoke then final runs | Agent chooses subsequent calls; no predetermined prefetch; complete or explicitly incomplete trajectories; gold and extra evidence tools isolated |
| 4 — release, 3–5 days | Outcome labels/subset annotations, reproducible analysis, worked example, data card/codebook, rights-reviewed files and clean reproduction instructions | Actual files support each claimed analysis/replay/recollection capability; limitations stated |

## Functional scope and staged runs

Start with a three-company research release, aiming for approximately six if coverage permits. The final roster is not automatically RELIANCE/TCS: use a recorded rule covering accessible evidence, corporate-action cases and controls. Fix question families/definitions before observing agent outcomes. EPS changes, latest reported profit, dividend-per-share comparisons and CFO versus cash capex are candidates, not proven current capabilities.

Use only selected operations and documented admissible arguments, not all thirteen by default. Financials, corporate actions, earnings discovery/detail and announcements are the likely starting subset. Corporate actions still need live validation; capex and dividend coverage are unproven. Add a bounded issuer-evidence lookup only when necessary to make a task answerable within the environment. Gold sources alone cannot make facts discoverable to agents.

Two models × six companies × four questions gives 48 target trajectories; three companies gives 24. Neither is a release gate. Real study data must be documented real observations. Fictional software fixtures remain separate. No mutated values or invented traps should be presented as natural source problems.

## Core and interface acceptance

Reuse the existing core/contracts, not the workbench HTTP layer, for agent tools. Live retrieval keeps current controls and transient results. Capture is opt-in and permissioned; replay is a separate offline path returning frozen agent-visible results and warnings without running current provider readiness or silently falling through to live.

Record full supplied/resolved arguments, known transformations, original periods/values, retrieval receipts, failures, redactions and checksums. Distinguish original provider information, Margin enrichment and experiment metadata. Unknown adjustment rules remain unknown. Pin relative windows and question cutoffs; changing warnings, helpers or available filings creates a new version/profile.

Keep UI repairs scoped to faithful result/source/detail inspection first. Full print polish is useful but does not block a function-based experiment. Add only minimal snapshot and trajectory inspection views as needed; avoid a frontend rebuild.

Required tests cover request identity, pinned dates, stable replay, schema/policy versions, missing/empty/unsupported distinctions, failed-response replay, no live fallback or spending, safe capture writes, sanitization, complete runner logs and answer-key isolation. Independently review financial arithmetic and accounting definitions.

## Budgets, retained state and existing source plans

The complete review contains a six-company planning example of 18 BharatStock requests and 54 Drishti MCP credits for 24 data operations, before extra pages, metadata/lifecycle traffic, account diagnostics, sources and optional news. It is not an approved collection budget or measured full cost. Obtain a bounded per-request manifest and current entitlements before dispatch. Replays spend no provider credits; model tokens and annotation effort are separate costs.

The old Starter/Starter purchase advice concerns ordinary retrieval, not the new research use. Use the [dated rights/subscription review](design/research-environment-review.md#6-provider-rights-subscriptions-and-collection-cost) before selecting plans; a subscription does not establish public dataset, trajectory redistribution or external model-use rights. No purchase or provider outreach is authorized by this document.

Proposed persistent research artifacts are an explicit, permission-gated exception to the transient live workflow. They are bounded/versioned, not a maintained market corpus or backfill. Old raw diagnostics have overdue manual review dates; do not reuse or extend retention implicitly. Private keys, restricted captures and private answer keys remain outside Git, public release paths and agent-visible files.

## Four-person work split

| Workstream | Owns | Review |
| --- | --- | --- |
| Core | Request contracts, capture, replay, stability and live regressions | Integration contributor verifies offline/no-fallback behavior |
| Finance, including Advait | Task definitions, filing calculations, first-pass answer keys; optional separate DCF | Evidence contributor independently checks keys before model outcomes |
| Evidence/provider | Applicable rights, coverage, source provenance, bounded collection manifest | Finance/core review definitions and access/cost assumptions |
| Integration/research | Runner, trajectory records, analysis, inspection and reproducibility | Others review leakage, labels and clean setup |

Each stream owns tests/documentation. These are human workstreams, not autonomous delegation instructions.

## Later evaluation and deferred material

After a reliable baseline, add typed compatibility/comparison helpers, citation task/assessment workflows, explicit-assumption FCFF DCF/scenarios/sensitivity and bounded sentiment protocols from the existing design. Add them to experiments as explicit versioned conditions; do not silently alter the baseline or use host-LLM assessments as independent gold.

Then package stable services through Margin MCP and validate a real host. Selective semantic search/concall additions follow demonstrated tasks. Broader sectors, market-wide claims, public multiuser hosting and cross-domain generality remain later work.

### Proposed corpus composition

Retained for older links. The old maintained corpus project remains superseded on `d1`. The proposed exception is a small permissioned, immutable research environment with declared tool/request coverage, independently verified evidence and explicit public/restricted/reconstructed status.

### Remaining gates

Feasibility/rights -> capture/replay -> predeclared cases and independent keys -> frozen environment -> genuine trajectories -> inspectable release. Rebuilding analysis, replaying the same environment and recollecting live data need separate tested instructions. Environment fidelity and independently justified answers take priority over task count, feature count and packaging.
