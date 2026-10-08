# Working on Margin

These instructions apply to human contributors and coding agents.

## Start here

Read [README.md](README.md), [context](docs/context.md) and [implementation status](docs/implementation.md). Inspect branch/worktree state before editing and preserve unrelated work. Use the [documentation index](docs/README.md) for task-specific references.

`main` is the aggregation workspace. The previous corpus/PDF implementation is preserved on the pushed `d1` branch at `c77963d`. It is no longer delivered software on `main`. Do not restore old ingestion work as the default response to provider limits, rewrite history or force-push without an explicit request.

## Scope and engineering

- Indian listed-company research, four-person professor-supervised team. Python 3.12+ and the official MCP SDK are the proposed stack; no runtime package currently exists on this branch.
- First aggregate BharatStock MCP and Drishti MCP using reviewed native read tools. Normalized tools, comparisons and citation verification follow measured contracts. Do not maintain a Margin financial database/corpus.
- Paid plans are permitted. Developer + Starter is the recommendation; accounts are not active as of this checkpoint. Do not purchase, create accounts or contact providers without user instructions. Eikon is not a dependency.
- Preserve numeric units, fiscal periods, consolidation basis, original source links, missing values and provenance. Never describe provider analysis, synthetic examples or unchecked extracts as independently verified facts.
- Keep credentials, account payloads, raw licensed responses, PDFs/databases and signed URLs out of Git and logs. `.env`/private output directories are ignored; `.env.example` contains blanks only. A `.env` file is not automatically loaded by SDKs.
- Make bounded read-only provider tests. No broad backfills, automatic page exhaustion, mutation/batch jobs or deliberate quota exhaustion. Measure actual charge deltas; native call counts are not guaranteed underlying request counts.
- Separate provider credential contexts. Never forward a user's Margin token as an upstream key. Only connect to the documented provider hosts.
- Do not add speculative dependencies, agents, frontend, vector database or LLM service. The host owns the model and prose.
- When runtime code is introduced, protocol stdout and diagnostic stderr must remain separate. Thin handlers should call independently testable services.

## Documentation and validation

- `docs/implementation.md`: delivered state, dated checks and limitations. Separate public probes, authenticated source tests, transport tests, financial accuracy and real-host evaluation.
- `docs/design/mcp-aggregation.md`: architecture and proposed contracts. Do not mark designs as implemented without evidence.
- `docs/research/mcp-provider-feasibility.md`: dated source links, inspected versions/schemas, observations, prices and unresolved access. Preserve history and correct factual errors transparently.
- `docs/api-testing.md`: credential setup, test sequence, bounds, endpoints and acceptance evidence. Update with actual runnable commands only when a test client exists.
- `docs/plan.md`: priorities/gates; `docs/context.md`: concise handoff; README: brief orientation; `docs/README.md`: navigation/update responsibilities.
- No project-wide churn for a typo or unchanged internal refactor. New documents need a distinct purpose and an index entry.
- For documentation/removal-only changes, check local links/anchors, stale commands and `git diff --check`. Do not claim the retired suite ran on `main`.
- When executable code/dependencies are introduced, establish lint/format/test commands in the same change and run meaningful checks, including real MCP transport tests. Do not count SDK-client success as model-host verification.

Before handoff, review changed paths for private data, record checks actually run and say what remains blocked/unverified. Provider/team/product permissions must be established before public raw-data serving; an API subscription alone does not settle redistribution.
