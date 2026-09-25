# Documentation index

Updated 25 September 2026. Start with [implementation status](implementation.md) for what works today. Usage guides describe executable workflows; design documents describe intended behavior; research notes preserve dated observations.

## Reading order

Not every Markdown file is required reading. None is needed to execute the installed Python code, although the project README supplies package metadata and usage instructions. Keep the documentation in the repository; choose what to read by role and task:

| Priority | Read when | Files |
| --- | --- | --- |
| Core orientation | Joining the project or starting a behavior change | Root `README.md`, `AGENTS.md`, `context.md`, `implementation.md` |
| Working reference | Running, integrating or changing a component | `development.md`, `tools.md`, `acquisition-development.md`, `ingestion-development.md` as relevant |
| Planning reference | Implementing a feature or changing direction | `plan.md` and the relevant `design/` documents |
| Historical/reference | Investigating sources, understanding a decision or writing the academic report | Relevant `research/` notes; not all on every task |

This index is navigation. It does not duplicate implementation status or replace contributor instructions. A normal new contributor can follow this sequence:

1. [Project README](../README.md) — purpose, capabilities and quick start.
2. [Development guide](development.md) — installation, synthetic demo, testing and MCP host configuration.
3. [Implemented tool contracts](tools.md) — four metadata tools, the discovery tool/resource/prompt, their schemas, errors and limits.
4. [Acquisition guide](acquisition-development.md) and [PDF ingestion guide](ingestion-development.md) — download, import, inspect and extract candidates.
5. [Feature/data map](design/functionality-data-map.md) — priorities, dependencies and completion checks.
6. [Citation design](design/citations.md) — proposed citation creation, claim verification and answer audits.

## Current implementation and team context

| Document | Purpose |
| --- | --- |
| [Implementation status](implementation.md) | Current capabilities, code map, local validation and milestone history |
| [Project context](context.md) | Concise handoff, constraints, boundaries and next implementation order |
| [Development](development.md) | Setup, contribution checks, metadata import and host configuration |
| [Tool contracts](tools.md) | Authoritative implemented MCP behavior |
| [Acquisition](acquisition-development.md) | Curated source catalog, downloads, manifests and troubleshooting |
| [PDF ingestion](ingestion-development.md) | Archive, recipes, extraction outputs and limitations |
| [Delivery plan](plan.md) | Active external-source/session roadmap, superseded corpus target, workstreams and evaluation |
| [Contributor instructions](../AGENTS.md) | Repository engineering conventions |

## Design proposals

A design's presence does not mean its tools or schemas are implemented. Check [status](implementation.md) and [tool contracts](tools.md) before describing delivered capabilities.

| Document | Purpose |
| --- | --- |
| [Feature/data map](design/functionality-data-map.md) | Active external build order and retained earlier local-path dependency analysis |
| [Architecture](design/architecture.md) | Target service boundaries, domain records, comparison rules and deployment |
| [Ingestion design](design/ingestion.md) | Existing ingestion foundations and remaining source/extraction/publication work |
| [Citations](design/citations.md) | Proposed evidence identities, creation, verification results and evaluation |
| [Data policy](design/data-policy.md) | Proposed storage, revision, serving and source-permission rules |

## Dated research and experiments

These records distinguish documentation found, code inspected, transfers observed and capabilities actually tested. Provider terms, prices and third-party APIs are observations at the stated research date, not guarantees of current access. External links have not been revalidated as part of the documentation cleanup.

| Document | How to use it |
| --- | --- |
| [Corpus trial](research/corpus-trial.md) | 25 September source experiments, Tijori access inventory, seven-document corpus, 36-cell extraction study and coverage gaps |
| [BSE acquisition results](research/bse-acquisition-results.md) | Initial successful exchange downloads, hashes, content checks and limits |
| [Issuer acquisition troubleshooting](research/acquisition-troubleshooting.md) | Earlier Wipro success and issuer-route failures; use the acquisition guide for current commands |
| [Initial access log](research/ingestion-access-log.md) | Historical failures and links to subsequent successes |
| [Infosys feasibility](research/infosys-feasibility.md) | Early issuer-site discovery and unvalidated example numbers; not benchmark truth |
| [Existing MCP ingestion](research/existing-mcp-ingestion.md) | Source inspection of other projects, with pinned revisions and verification limits |
| [Data-source landscape](research/data-sources.md) | Broad source/provider research, dated access/rights observations and product comparisons |
| [MCP reference guide](research/mcp-reference-guide.md) | Protocol/reference patterns and technology candidates |
| [Provider questions](research/provider-questions.md) | Future evaluation questions; no provider engagement is implied |

## What to document and where

The contributor changing behavior owns its documentation update, whether that contributor is a person or an agent. Apply only relevant rows; small internal changes do not require a project-wide documentation sweep.

| Change | Document these details | Primary file(s) to update |
| --- | --- | --- |
| Capability completed, removed or materially limited | Delivered behavior, implementation boundary, evidence of completion, remaining gaps | [implementation.md](implementation.md); refresh [context.md](context.md) and root README summary only if affected |
| MCP tool, resource or prompt added/changed | Exact arguments/defaults, result shape, errors, limits, pagination, evidence behavior and realistic example | [tools.md](tools.md), matching code/tests; mark the relevant design section's implementation status |
| Installation, dependencies, CLI/server or host setup | Requirements, portable commands, configuration, expected result and failure handling | [development.md](development.md); root README quick start if affected; dependency manifests/constraints and CI when applicable |
| PDF import, parsing, recipes or archive behavior | Accepted inputs, schema/version, units/periods, outputs, failure states, replay/migration behavior and reproducible example | [ingestion-development.md](ingestion-development.md); relevant design rationale in [design/ingestion.md](design/ingestion.md) |
| Source acquisition or catalog change | Exact source/discovery URL, issuer/filing identity, publication date, hash, observed status, timeouts and repeatability limits | [acquisition-development.md](acquisition-development.md) for usage; `examples/public-document-sources.json` for reviewed entries; relevant `research/` note for observations |
| Citation or financial semantics change | Metric/context definitions, evidence requirements, verification scope/verdicts, formulas and mismatch cases | [design/citations.md](design/citations.md) or [design/architecture.md](design/architecture.md) for decisions; [tools.md](tools.md) and applicable usage guide for implemented behavior |
| Architecture/storage decision | Problem, chosen approach, meaningful alternative/tradeoff, data compatibility and decision status | Relevant file under `design/`; [implementation.md](implementation.md) for actual delivered layout/behavior |
| Scope, priority or benchmark change | Feature dependencies, completion gate, dataset/split, scoring and rationale | [plan.md](plan.md), [design/functionality-data-map.md](design/functionality-data-map.md); [context.md](context.md) if next steps change |
| Validation checkpoint | Date/environment, commands/checks run, outcomes, failures and limits; separate local, CI, host and financial accuracy evidence | [implementation.md](implementation.md#validation); benchmark/experiment detail in the relevant dated report |
| Source/provider investigation | Links and date, method (documentation/source inspection/live call), result and interpretation limits | Relevant `research/` note; follow up historical findings without rewriting them as current facts |
| Data-use or serving policy | Declared scope, supporting reference, unresolved conditions and what software enforces | [design/data-policy.md](design/data-policy.md); affected usage/contracts only if behavior changes |
| Document added, moved or retired | Purpose, reading priority, replacement link and affected references | This index and all inbound links; avoid adding a second authority for an existing topic |
| Contributor/agent workflow change | Durable shared rules, required checks and update responsibilities | Root [AGENTS.md](../AGENTS.md); this matrix only if routing changes |

## Authority and consistency rules

1. **Code and tests establish observed behavior; documents explain it.** A failed check or mismatch is a finding to resolve, not a reason to treat a proposal as implemented. Tests alone do not establish real financial correctness.
2. **One primary home per topic.** `implementation.md` owns current status and validation; `tools.md` owns the documented implemented MCP contract; usage guides own runnable workflows; design files own rationale and proposals; research owns dated observations. Root README and context are brief summaries with links.
3. **Use explicit status.** Distinguish proposed, implemented, partially implemented, unreviewed and historical work. When a design is built, update its status/boundaries and the implemented contract together. A future API table must not masquerade as a delivered tool list.
4. **Keep counters and evidence in one place.** Maintain current test totals and detailed validation in `implementation.md`. Link to them from guides. Historical reports retain the totals observed at their date; do not update those as if an old experiment were rerun.
5. **Record only real checks.** Separate software tests, successful downloads, visual inspection, financial extraction accuracy and graphical host behavior. Record observation date/environment and missing checks. Use private artifact paths or content IDs for local evidence, with portable reproduction steps; do not commit the artifacts.
6. **Preserve time and provenance.** Keep research failures and superseded decisions dated with follow-up/replacement links. An accessible document does not establish completeness, latest-market coverage or redistribution rights.
7. **Keep handoff brief.** Context contains current constraints, state, blockers and next actions. Do not append conversation history, routine test transcripts or a new per-task Markdown report.
8. **Update incrementally.** Inspect current files before applying edits, preserve unrelated contributors' work and resolve conflicting summaries. Move/merge a document only when its purpose overlaps another, updating inbound links and preserving useful evidence.

## New documents and retirement

Prefer an existing topical file. Add a document only for a distinct, reusable purpose such as a new subsystem's operational guide or a substantial dated experiment. Give it a purpose, status/date, links to related authoritative files and an entry here. Avoid one document per conversation, task, agent or failed request.

Research notes are optional reading, but preserve useful acquisition evidence and support the academic report. They need not be deleted to simplify onboarding. If several eventually become repetitive, merge/archive them deliberately and leave replacement links; do not silently discard unique findings.

## Handoff check

Before handing over a change, review the applicable rows above, check local links/headings and any edited executable examples, and follow the code-validation rules in [AGENTS.md](../AGENTS.md). Confirm the commit includes no private source artifacts. Report the changed behavior, documentation updated, checks actually run and remaining limitations. No status update is necessary for an unrelated typo fix.
