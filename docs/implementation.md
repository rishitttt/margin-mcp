# Implementation and validation status

Current checkpoint: 8 October 2026. This file owns delivered state and test evidence. [Design](design/mcp-aggregation.md) and [delivery plan](plan.md) describe future work.

## Branch transition

- Prior local-corpus/PDF implementation: preserved at `c77963d` on pushed [`d1`](https://github.com/rishitttt/margin-mcp/tree/d1).
- Aggregation research/planning committed on `main` as `be04aba` before cleanup.
- Legacy code, tests, examples, CI, package manifests and superseded guides removed from `main` through a normal commit, without branch resets/history rewriting. Ignored local artifacts were not removed.
- `main` now contains the current documentation and blank credential template. No installable Margin package, aggregate MCP, normalized financial tools or citation verifier is implemented. The old CLI commands are not supported on this branch.

## Validation

### Public endpoint checkpoint

A bounded sequence of 14 HTTPS requests was run without credentials or paid-data tool calls. TLS verification stayed enabled; each request had a 20-second timeout and 2 MiB response cap. No automatic retries, mutation jobs, authenticated requests or account credits were involved.

- BharatStock plans/status and both OpenAPI schemas: HTTP 200. The schemas have 35 and 30 distinct path entries respectively, not that many MCP tools; both declare OpenAPI 3.1.0.
- BharatStock quote/financials and Drishti news/announcements/concalls/account usage: HTTP 401 without keys, as expected.
- BharatStock MCP initialize: HTTP 200, version `0.1.0`, protocol `2025-06-18`; initialized notification HTTP 202; tools/list HTTP 401.
- Drishti MCP initialize: HTTP 401 without a key.

The exact methods/URLs/results and schema hashes are recorded in [provider research](research/mcp-provider-feasibility.md). Temporary raw receipts remain outside Git. This validates reachability/public contracts and authentication barriers, **not financial-data quality, paid entitlement, hosted tool schemas, effective limits or charges**.

### Repository checks

Branch preservation was verified before removing tracked legacy files. Documentation checks cover local links/anchors, stale legacy setup commands and `git diff --check`. There is no runtime suite on this branch yet; the retired September tests were not rerun and do not establish aggregation correctness. No graphical/model-host demonstration has occurred.

## Remaining gates

The user has not purchased plans or supplied keys. Follow [API testing](api-testing.md) once they are available. Establish actual MCP schemas/billing, numeric units/basis, history/coverage and source links before implementing the gateway. Financial correctness and real host integration need independent evidence after transport checks pass.
