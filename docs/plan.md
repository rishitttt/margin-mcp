# Delivery and evaluation plan

Updated 8 October 2026. Proposal only; no aggregation implemented. The user now wants **BharatStock MCP + Drishti MCP as one aggregated MCP first**, and permits paid plans. [Aggregation architecture](design/mcp-aggregation.md) owns design decisions and exact stage acceptance checks; [provider research](research/mcp-provider-feasibility.md) owns endpoint, quota, price and coverage evidence. [Implementation status](implementation.md) owns delivered software.

## Active scope

A local Python MCP gateway serves the user's harness and connects to both hosted upstream MCPs. It requires no metadata import or Margin financial database. Begin with namespaced native read tools and preserve upstream schemas/results. Later add selected normalized tools from the supplied PDF, shared financial/event records, comparisons and stronger evidence support. The host supplies the LLM.

Research recommends BharatStock Developer + Drishti Starter at a published ₹3,000/month. Accounts/keys, actual entitlement/billing, team permissions and the new calendar deadline remain unverified. The original six-to-eight-week estimate was given in September; implementation estimates below are working-day allocations, not elapsed progress or a new submission date.

No corpus building, historical backfill, exchange crawler, trading engine, frontend, LLM hosting or WebSocket ingestion is required. Preserve the prior committed prototype on `d1`. It also remains on `main`; planning has not cleared/reset code. Decide any removal/isolation in a later normal commit.

## Milestones

| Sequence | Proposed outcome | Exit evidence |
| --- | --- | --- |
| 0; 1–2 days | Access, catalogs, contracts and small coverage exercise | Both eligible keys authenticate; actual schemas, costs, history, units/basis and evidence depth recorded |
| 1a; 2–3 days | Minimal local aggregation | Real stdio client discovers/calls both sources through Margin; no corpus prerequisite; native schema/result preservation |
| 1b; 2–3 days | Reliability and observability | Independent failures, limits, receipts, cancellation, cleanup, credential isolation and bounded results tested |
| 1c; 2–3 days | Real host demonstration and baseline | At least six paired tasks, source attribution and measured call/credit costs; clear unavailable/partial cases |
| 2; after evidence review | A few semantic financial/event tools | Compatible normalization/comparison and actual claim support checked; do not implement all ten names automatically |
| Later; optional | Hosted/multi-user deployment or more sources | Provider/team permissions, user auth, tenant isolation, accounting and hosting need independently established |

The architecture document assigns four ownership areas for the human team: upstream access/contracts; MCP bridge/lifecycle; policy/identity/provenance; independent evaluation/host/docs. Work against shared schema snapshots and the same question set.

## Evaluation

Use the proposed 12-company panel in the architecture: ten liquid mainboard firms across sectors, one verified BSE-exclusive firm, one NSE SME firm. Request bounded quarterly/annual rows, one year of EOD prices and 30 days of events/news. This is a coverage experiment, not a dataset collection target. Report requested versus returned periods and non-null financial fields, original-link support and event/call history separately.

Compare directly attaching the two provider MCPs with using Margin, holding host/model/credentials/windows constant. Stage 1's expected contribution is a single configuration plus reliable policy/observability; accuracy improvement is a hypothesis, not a claim. Include numeric-plus-event research, identity ambiguity, missing history, empty events, source failures, quota/credit errors and citation insufficiency. Stage 2 can evaluate normalization/orchestration against this baseline.

Measure task completion, identity/context correctness, answerability, citation/source support, correct abstention, schema/result fidelity, latency and upstream calls/credits. Independently inspect a small set of numeric cells and dated events rather than counting transport tests as financial verification. Keep model/prompt/schema/query date/version fixed in each trial; latest provider data is not point-in-time historical evidence. Use synthetic/minimized software fixtures and permitted temporary private snapshots, without committing raw provider datasets.

The initial source-test budget proposed in research is 500 Drishti credits with an explicit stop. Actual per-tool charges and MCP rate enforcement must be established before claiming sustained capacity or hard quota guarantees. Do not buy higher tiers until measurements show the constraint.

## Deferred material and remaining gates

Earlier external REST/session plans and normalized architecture remain in [architecture](design/architecture.md), [feature/data map](design/functionality-data-map.md) and [citations](design/citations.md).

### Proposed corpus composition

This heading is retained for older research links. The earlier 50-document core-corpus target and 90–130 optional coverage slots are superseded. Seven acquired PDFs remain historical development evidence; completing a local archive/fact warehouse is not a prerequisite for aggregation. The current target is a bounded external-provider coverage experiment, not document collection.

### Remaining gates

Before implementation, verify eligible key access and the actual hosted catalogs/billing. Before public operation, establish raw-data re-serving, institutional/team access and retention permissions; paying for a plan does not settle these. No provider purchase/outreach is implied, and this research task has not implemented the milestones.
