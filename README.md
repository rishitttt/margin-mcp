# Margin

A Python research core for Indian financial data, integrating **BharatStock REST + Drishti MCP**. Build and test the core through a temporary local browser workbench first; add Margin's own MCP interface later.

## Current state

`main` now has an installable Python core, BharatStock REST and Drishti MCP adapters, and a temporary local browser workbench. Synthetic mode is the default: fictional companies and data, no provider network. The adapters passed offline integration tests. The user’s 21 October page-export evidence shows a successful eight-call RELIANCE run: snapshot, quarterly/annual financials, ratios and EOD prices through BharatStock, plus Drishti news, announcements and earnings discovery. Broader coverage, actual credit reconciliation, source accuracy and several live presentation paths remain pending. Margin's own MCP server is deferred.

The earlier corpus/PDF implementation is preserved on the pushed [`d1` branch](https://github.com/rishitttt/margin-mcp/tree/d1) at `c77963d`. Old corpus commands do not apply to this runtime.

**7 November planning update:** the [complete research review](docs/design/research-environment-review.md) and [revised plan](docs/plan.md) propose a bounded replayable environment, independent filing-based answers and recorded agent experiments over this core. They are not implemented. A permissioned frozen study snapshot is a specific exception to the transient live workflow; general DCF, sentiment and downstream MCP remain later/parallel work. The audit passed Ruff checks and all 50 offline tests; no new authenticated collection or model experiment was run.

## Run locally

Requires Python 3.12 or newer; dependency constraints were tested on Python 3.12/macOS ARM.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[workbench,dev]'
.venv/bin/margin-workbench --mode synthetic --port 8765
```

Open [the local workbench](http://127.0.0.1:8765). Preview a plan for fictional `SYNTHA`, then run it. Add prices or earnings discovery explicitly; select a returned earnings record to inspect its detail. No keys or subscriptions are needed for synthetic mode. See the [workbench guide](docs/workbench.md) for scenarios, live-mode controls, API usage, retention and limitations.

```sh
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/pytest -q
```

The default suite blocks real socket connections. Browser acceptance uses a fresh system Chrome/Chromium profile and a running synthetic instance; commands and evidence are in the [guide](docs/workbench.md#verification) and [implementation status](docs/implementation.md#first-coreworkbench-build-checkpoint).

## Existing source evidence

Trial tests return financial, price, ownership and event data for RELIANCE/TCS. The first pass used 12 BharatStock REST requests and 8 Drishti credits; the 9 October Drishti comparison added 14 HTTP requests and 6 credits, ending at **986**. Its four native routing tools expose underlying operations. A subsequent metadata audit mapped **25 confirmed operation schemas** in 23 HTTP requests with zero debit. One earnings execution is observed; it reveals additional source/raw fields, conflicting revenue values and credential-bearing citation URLs requiring sanitization. Four Reliance FY25 values match the original statement; broader numerical/source accuracy remains unverified. See [first results](docs/research/mcp-provider-feasibility.md#authenticated-trial-results-8-october-2026), [operation comparison](docs/research/mcp-provider-feasibility.md#authenticated-operation-discovery-and-rest-comparison-9-october-2026) and [implementation status](docs/implementation.md).

## Start here

- [Short handoff: repo map, documentation update and professor's new notes](HANDOFF.md)
- [Workbench setup and usage](docs/workbench.md)
- [Active core/workbench architecture](docs/design/core-workbench.md)
- [Later MCP interface design](docs/design/mcp-aggregation.md)
- [Provider endpoints, costs and coverage research](docs/research/mcp-provider-feasibility.md)
- [Drishti functions, inputs and REST relationships](docs/reference/drishti-functions.md)
- [API/MCP test approach and credential setup](docs/api-testing.md)
- [Delivery plan](docs/plan.md)
- [Context and handoff](docs/context.md)
- [Documentation index and update responsibilities](docs/README.md)

Phase 1 is a reusable Python core plus **FastAPI and a minimal local HTML/JavaScript workbench**. The UI calls shared services for approved provider operations, planning, budgets, sanitization, citations and receipts. Synthetic mode comes first; explicit bounded live runs follow. Tables, a price line, dated news/filings and a sanitized run inspector are enough to test the data. Drishti still uses an upstream MCP client; only our downstream MCP server/host packaging is deferred.

Later, Margin's MCP adapter calls those same services. No financial corpus, public data server, LLM service or permanent product frontend is required. The [delivery plan](docs/plan.md) replaces the previous MCP-first milestone sequence.

## Access and subscriptions

The historical tests used the supplied **BharatStock Free** key (25 requests/day) and **Drishti trial** (1,000 one-off credits); current access and balances have not been revalidated. Two data/catalog passes and one metadata audit are complete. Free BharatStock does not include native MCP; Drishti native earnings execution succeeded, while transcript search and most other operations remain untested. These historical source diagnostics do not establish that the newly implemented adapters work against current live contracts. The chosen integration uses BharatStock REST, so its native-MCP gate is not a blocker. Do not repeat completed passes against used quota; use the function reference and budget further source checks separately.

Build synthetic/core functionality without a purchase. The **9 October** Starter/Starter ₹2,600/month recommendation was historical retrieval guidance. For the new research use, consult the [7 November rights/subscription review](docs/design/research-environment-review.md#6-provider-rights-subscriptions-and-collection-cost): ordinary REST access, model evaluation, external model processing and public data/trajectory release are different questions. BharatStock's native MCP remains technically unnecessary; current published rights can still affect the appropriate plan. No plan has been purchased or account quota revalidated by this review.

Trial keys have been copied to local ignored `reports/private/mcptempkeys.txt` with permissions 0600; they have not been staged, committed or pushed. Later, `.env.example` can be copied to `.env` and filled locally. Do not paste credentials into chat or commit raw responses containing account information or signed links. The runtime reads environment variables only; it does not automatically load `.env` or the private text file. Live startup and Drishti connection are explicit; see the workbench guide.

The manual workbench needs no LLM subscription or public hosting. Later MCP use relies on the model supplied by the harness. Provider redistribution rights remain a separate condition for a public product.

Contributors and agents should read [AGENTS.md](AGENTS.md). Legacy usage, evidence experiments and code remain available on `d1`; keep current behavior claims on `main` separate from those historical results.
