# Working on Margin

These instructions apply to human contributors and coding agents working in this repository.

## Start here

1. Read [README.md](README.md), [current context](docs/context.md) and [implementation status](docs/implementation.md) at the start of a task that changes behavior.
2. Check the working tree and relevant code/tests before editing. Preserve unrelated work, including changes made by another contributor or agent.
3. Use the [documentation index](docs/README.md) to read only the guides/designs relevant to the task. Reading every research note is unnecessary.
4. Follow the [documentation update matrix](docs/README.md#what-to-document-and-where) for affected files. Update documentation in the same change as the behavior it describes.

Design documents are proposals unless their implementation is confirmed in code and current status. Research notes are dated evidence, not implementation instructions. If documentation and code disagree, inspect the behavior/tests and reconcile the relevant docs; do not claim a feature works merely because it is designed.

## Product constraints

- Indian listed-company research; do not substitute a US-only dataset.
- Four-person team, free prototype, approximately six to eight weeks from September 2026.
- Paid-provider entitlements and hosted redistribution rights remain unresolved. Curated local acquisition exists; do not rely on Eikon or paid APIs.
- Preserve evidence, units, periods and standalone/consolidated distinctions during candidate extraction and future fact publication.
- Focus new work on external APIs/tools and temporary evidence retrieval. Do not build, expand, backfill or schedule maintenance of a Margin-owned financial corpus as an active project goal. Preserve existing local metadata, discovery, acquisition, archive and extraction functionality as optional utilities and regression fixtures. The product direction includes provider APIs/tools and temporary document sessions without requiring users to maintain a corpus; named providers are examples, not a fixed dependency list. See `docs/design/architecture.md` for the proposed boundaries.
- Never represent synthetic examples as real financial evidence. Keep synthetic labeling in tool responses.

## Engineering

- Python 3.12+, official MCP SDK, thin MCP handlers, independently testable domain services.
- Keep network acquisition separate from queries. Corpus-query tools remain read-only and metadata-only; discovery guidance must not imply network access or verified facts.
- Do not add speculative dependencies, agents, a vector database, or a frontend without a concrete need.
- SQLite queries must not create a missing database. Corpus replacement requires the CLI's explicit flag.
- Keep raw third-party documents, credentials and local databases out of Git.
- All protocol traffic goes to stdout; diagnostic logs go to stderr.
- Run `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .` and `.venv/bin/pytest` after meaningful code changes. Integration tests must exercise the real stdio transport.
- Do not claim model-host verification from a programmatic client test alone.

## Documentation responsibilities

- **Implemented status:** `docs/implementation.md` owns delivered capabilities, current validation results and material limitations. Record the date, actual checks and what remains unverified. Do not copy current test totals into other guides; historical experiment totals stay dated.
- **API behavior:** `docs/tools.md` owns implemented MCP inputs, outputs, errors and limits. Update examples and tests alongside contract changes; proposed tools belong in `docs/design/` until implemented.
- **Usage:** update `docs/development.md`, `docs/ingestion-development.md` or `docs/acquisition-development.md` when their commands, inputs, outputs or failure behavior change. Keep README quick-start commands aligned when affected.
- **Design and decisions:** explain the problem, chosen approach, tradeoff, status and acceptance check in the relevant existing design file. Update `docs/plan.md` only when priorities, scope or evaluation gates change.
- **Handoff:** update `docs/context.md` for material changes to capabilities, constraints, blockers or next steps. Keep it a short present-tense summary with links; do not append a transcript of each task.
- **Research:** record source URL, observation date, method, result and limits in the relevant research note. Distinguish downloaded/inspected/tested from advertised or inferred. Preserve prior observations with dated follow-ups.
- **Navigation:** update `docs/README.md` when adding, moving or removing a document. Prefer extending an existing topical file over adding a new Markdown file.
- **No unnecessary churn:** a typo, formatting-only change or internal refactor with unchanged behavior does not require updates to status, roadmap or every guide. Do not invent validation to fill a template.

## Before handing off

- Apply the relevant update-matrix rows; revise only summaries affected by the change. Check current files again if others have edited them concurrently.
- Verify changed commands/examples with fresh outputs where practical and check local Markdown links/headings. Keep paths portable.
- Run the engineering checks above for meaningful code changes. For documentation-only changes, check links and changed executable examples; do not claim a fresh full-suite run if none occurred.
- Keep raw documents, credentials, private manifests and databases out of the commit. Preserve synthetic labels and explicitly distinguish private local evidence from files available in a clone.
- Summarize what changed, checks actually run, remaining limitations and the next actionable step. State material checks not run and why. Do not mark proposed, partial or unreviewed work complete.

For an agent that does not automatically load `AGENTS.md`, explicitly include it in the task's reading instructions. Keep other editor/agent instruction files as pointers to this file rather than duplicating its rules.
