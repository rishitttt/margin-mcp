# Margin

A proposed Python MCP gateway for Indian financial research, combining **BharatStock MCP + Drishti MCP** into one connection for a user's own AI harness.

## Current state

`main` is the new aggregation workspace: architecture, provider research, an endpoint-test protocol and contributor context. The earlier corpus/metadata/PDF implementation has been removed from this branch through a normal commit and preserved on the pushed [`d1` branch](https://github.com/rishitttt/margin-mcp/tree/d1) at `c77963d`.

**No aggregated MCP or installable Margin package exists on `main` yet.** Do not use the old `margin serve` or corpus-import commands here. Existing ignored local PDFs/databases and virtual environments have not been deleted; they are not part of a new clone or the new runtime.

Public and unauthenticated provider endpoints have been checked. Financial/event payloads, authenticated catalogs and billing remain untested: the user has not purchased the plans yet. See [implementation and validation status](docs/implementation.md).

## Start here

- [Architecture and stage boundaries](docs/design/mcp-aggregation.md)
- [Provider endpoints, costs and coverage research](docs/research/mcp-provider-feasibility.md)
- [API/MCP test approach and credential setup](docs/api-testing.md)
- [Delivery plan](docs/plan.md)
- [Context and handoff](docs/context.md)
- [Documentation index and update responsibilities](docs/README.md)

Stage 1 forwards reviewed native read tools under provider namespaces. Stage 2 can add normalized financial/event records, compatible comparisons and citation support after measuring actual source behavior. No Margin-owned financial corpus is required.

## Access and subscriptions

The recommended initial pairing is BharatStock **Developer** + Drishti **Starter**, currently published at ₹1,000 + ₹2,000 per month. Exact account access, taxes, team permissions and billing are confirmed during onboarding/testing. Higher tiers are not needed merely to begin.

Copy `.env.example` to `.env` and fill the two keys locally after activating the subscriptions. `.env` is ignored by Git. Do not paste credentials into chat or commit raw responses containing account information or signed links. There is no runtime that automatically loads this file yet; the test client must explicitly read it or use environment variables.

Margin uses the model supplied by the harness; endpoint testing itself needs no LLM subscription or hosted server. Provider redistribution rights remain a separate condition for a public product.

Contributors and agents should read [AGENTS.md](AGENTS.md). Legacy usage, evidence experiments and code remain available on `d1`; keep current behavior claims on `main` separate from those historical results.
