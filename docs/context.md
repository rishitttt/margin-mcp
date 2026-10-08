# Project context and handoff

Current checkpoint: 8 October 2026. [Implementation status](implementation.md) owns delivered/validated state; [documentation index](README.md) routes the remaining material.

## Direction and constraints

Margin is a four-person professor-supervised Indian financial-research project. The user's harness owns the model. First build a Python MCP gateway over **BharatStock MCP + Drishti MCP**, preserving reviewed native tools; normalize financial/event records, comparisons and citations later. Do not maintain a Margin financial corpus. Eikon, hosting, live streams and a custom frontend are not prerequisites.

Paid plans are permitted. Recommend BharatStock Developer + Drishti Starter at published ₹3,000/month. The user confirmed subscriptions are **not purchased yet**; no credentials are configured. The earlier six-to-eight-week estimate dates from September, not a new deadline. Team and public-product permissions remain unresolved.

## Branch and delivered state

The prior implementation is preserved at `c77963d` on **pushed `origin/d1`**. Its source, tests, fixtures, CI, package manifests and old documentation have been removed from `main` in a normal history-preserving transition. The aggregation planning/research was committed first. Ignored local data/virtual environments remain private and are not a new runtime.

`main` contains current architecture/research, status/context, roadmap, API test protocol and a blank `.env.example`. It has no installable Margin package, MCP gateway or old corpus commands. Do not claim the old implementation or its September test count as current `main` behavior.

## Source evidence

Public OpenAPI schemas and BharatStock plan/status registers were downloaded successfully. Both inspected schemas are OpenAPI **3.1.0**; Drishti's guide calls its spec 3.0.1, so prefer the actual downloaded artifact. Both MCP endpoints are reachable: BharatStock allows no-key initialization but rejects tool discovery, while Drishti rejects no-key initialization. Representative protected REST endpoints reject requests without keys. No authenticated financial/event record or credit debit has been tested.

The inspected BharatStock npm package has 31 tools; its hosted initialization reports an older version. Drishti's installer points to its hosted server and does not reveal hosted schemas. MCP-only Drishti event/search tools do not have equivalent public REST routes. Units/basis, SME/BSE coverage, history, original source links and actual MCP rate/billing behavior are the next evidence gates.

## Next steps

1. Activate Developer + Starter and supply keys locally through ignored `.env`/environment; test client must explicitly load them.
2. Follow [API/MCP testing](api-testing.md): account diagnostics, authenticated catalogs, two-company smoke test, billing/context checks, then the bounded 12-company panel if successful.
3. Implement the minimal bridge from [aggregation design](design/mcp-aggregation.md) only after measured contracts; add policies/receipts and host evaluation before semantic orchestration.

The current endpoint checks use direct temporary research requests, not a committed test client or aggregation implementation. Accounts/keys are the remaining prerequisite for authenticated tests; no purchase or provider outreach has occurred.
