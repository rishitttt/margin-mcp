# Project context and handoff

Current as of 8 October 2026. [Implementation status](implementation.md) owns delivered capabilities; [documentation index](README.md) routes usage, design and research.

## Current direction

Margin is a professor-supervised four-person Indian financial-research project. The user's AI harness supplies the model. Python remains the implementation language. The new first stage is **one aggregated MCP over BharatStock MCP and Drishti MCP**, using existing native read tools. Higher-level normalized tools, comparisons, temporary extraction and citation verification are later stages. Do not build or maintain a Margin financial corpus.

The user now permits paid subscriptions. Research recommends BharatStock Developer + Drishti Starter at a published ₹3,000/month, with Drishti credits likely to constrain sustained research before daily request quotas. Accounts, purchases and credentials have not been observed. The earlier six-to-eight-week estimate dates from September; it is not a newly confirmed calendar deadline. Live feeds/hosting remain optional, and Eikon is not a dependency.

Read the [aggregation design](design/mcp-aggregation.md) for architecture, tool policy, proposed package boundaries and acceptance gates. Read [provider feasibility](research/mcp-provider-feasibility.md) for exact URLs, tool/REST mappings, rates, price scenarios, observed probes and coverage uncertainty. Earlier architecture/session/corpus proposals are reference material; they do not override this stage order.

## Delivered software and repository state

The existing code is still the local prototype: metadata MCP tools/discovery guidance, offline HTML link discovery, separate PDF archive/candidate extraction and curated document acquisition. It requires an imported metadata corpus. Seven private PDFs and the dated 36-cell development extraction study remain historical evidence, not product coverage; candidates are unreviewed. A clone contains synthetic fixtures and a source catalog, not those PDFs/databases. See [implementation status](implementation.md) for the full boundary and recorded validation.

`d1` preserves the prior committed state at `c77963d`; it is local and has not been observed pushed. Before planning edits, `main` pointed at the same commit and was clean. This task has updated documentation only: no reset/clearing, runtime migration, new MCP tools or provider adapters. Do not remove old code without a subsequent reviewable transition.

There is no aggregation, provider-only startup, financial-fact service, comparison service, accepted-fact store, evidence-serving tool or citation verifier implemented. Latest runtime checks remain the dated September checkpoint; no fresh full suite or model-host verification is implied by this research.

## Evidence learned in this scope

- Current public API schemas were downloaded and inspected. BharatStock npm 0.1.2 has 31 tools; Drishti npm 0.1.4 configures a hosted connector and does not contain its server tool schemas.
- Both published MCP URLs are reachable. BharatStock initialized without a key but rejected tool discovery; Drishti rejected initialization. No authenticated financial/event data was retrieved.
- The hosted BharatStock initialization version differs from its inspected npm package version. Its internal request retries/control traffic need usage measurement before equating native calls with quota units.
- Drishti's public MCP catalog includes search/events capabilities absent from its public REST schema; do not invent equivalent endpoints. Published REST RPM limits are not independently verified MCP ceilings.
- Numeric units/basis, SME/micro-cap coverage, event retention, original source links and page citations require paid-payload checks. Addressable universe is not complete joint coverage.
- Paid API access does not automatically permit public raw-data re-serving or key sharing. Private entitled-credential access is the proposed feasibility setup; team/product permissions require clarification before broader operation.

## Next implementation order

1. Obtain eligible accounts/secure keys through the user's chosen process; authenticate catalogs, schemas, plan limits and representative calls. Measure credits and numerical/evidence coverage on the small panel before making guarantees.
2. Decide the reviewable `main` transition while preserving `d1`; create a provider-only local gateway with two upstream MCP clients and namespaced, reviewed native tools.
3. Add quota admission, independent failures, receipts, schema preservation, shutdown, bounded payloads and routing guidance; test actual stdio transport and one real host.
4. Compare direct two-provider access with aggregation using the same tasks/model. Build a few normalized tools only after results justify them.

The present user request is research/planning only. This list is a proposal for later work, not authorization to implement it now. Existing acquisition findings, financial-context rules and citation designs remain useful historical foundations; do not expand their corpus as a workaround for provider limitations.
