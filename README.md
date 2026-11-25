# Margin

**25 November release 0.5.0:** the new `margin_company_finance` tool fetches fresh financials and returns one of the nine existing company calculations directly. It requires no previous result handle or financial database; only compact request answers/duplicate-control keys stay in process memory. Twenty-one MCP tools now expose the unchanged function inventory. See [usage](docs/mcp.md#company-finance-without-previous-results), [plan/subscriptions](docs/design/fetch-and-calculate.md) and [validation](docs/implementation.md). The older dated notes below are historical; the running 0.4.0 live installation has not been silently replaced.

**25 November release 0.4.0:** financial results now include deterministic crore/EPS displays, metric labels and scope warnings. Six common financial functions have direct strict MCP schemas (twenty tools total). An optional explicitly started local Unix-socket backend retains plans, results and quotas across LM Studio frontend restarts. Standalone mode remains available. Read [current setup](docs/mcp.md) and [architecture](docs/design/mcp-aggregation.md). No new authenticated data/model calls were used to implement this release; earlier dated checkpoints below are historical.

**25 November recording patch (0.3.3):** `--record-dir` generates a unique private log per server launch, avoiding LM Studio new-chat startup collisions. Existing logs remain unchanged; `--record-file` retains its no-overwrite behavior. [Recording setup](docs/mcp.md#optional-decision-and-observation-logs).

**25 November schema-feedback patch (0.3.2):** the second Qwen trial reached calculations but added an unsupported input flag. Exact catalog/runtime schemas agree. Bounded validation errors now identify locations and allowed/missing fields, preserving strict financial guards. See [input diagnostics](docs/mcp.md#financial-input-diagnostics-032).

**25 November MCP patch (0.3.1):** catalog entries now identify the actual MCP tool and argument binding, addressing the first LM Studio/Qwen attempt to call `finance.calculate_margins` as a tool. Unknown tools return protocol errors. Fact context guards remain unchanged. See [routing repair and test prompt](docs/mcp.md#lm-studio-catalog-routing-repair-031); reload the host with a new log filename after installing the patch. Successful model-host completion remains to be retested.

**25 November MCP alpha (0.3.0):** a local stdio MCP server now exposes the validated core through 14 workflow tools. No web backend or skill is required for MCP use. Read [MCP setup](docs/mcp.md) for installation/configuration, shared process state, logs and limitations. Core checkpoint `6b22f57` and the implementation plan `07b981a` were pushed before adapter work. The old dated notes below remain historical.

**24 November finance repair:** documented auto units, reporting-period eligibility, continuing-profit scope, data readiness, profitability, cash conversion and liquidity/borrowings groups are implemented. Summary announcements passed a reviewed-schema live check. See [finance scope/data support](docs/design/finance-data-support.md) and [current results](docs/reference/function-validation.md).

**24 November core 0.2.0:** the first no-inference citation/content-sentiment handoffs are implemented through Python, HTTP, CLI and a workbench JSON tester. Drishti readiness/catalog handling is repaired. See [review workflows](docs/review-workflows.md) and [validation status](docs/implementation.md). Margin’s own MCP packaging remains behind the core-validation gate.

**24 November build plan:** finish retrieval/finance validation, add capability-aware citation and content-sentiment workflows, package the stable core as MCP, and evaluate it through a separate cross-model harness with simple decision trails. See the [active plan](docs/plan.md). These additions are planned; the delivered runtime remains the core/workbench/CLI/skill described below. Older dated deferrals are superseded.

A Python research core for Indian financial data, integrating **BharatStock REST + Drishti MCP**. Build and test the core through a temporary local browser workbench first; add Margin's own MCP interface later.

**16 November agent interface:** reusable Python modules now also have a `margin-agent` JSON CLI and installed Codex skill, sharing the local backend without opening the browser. See [agent setup](docs/agent-interface.md). An optional private pilot recorder is separate from normal usage; frozen replay, independent grading and Margin's own MCP server remain unimplemented.

The [portable local test bundle](docs/portable-agent-bundle.md) adds relocatable setup, the full function inventory, optional private trial credentials and visible decision-summary logging. These private artifacts stay outside Git.

## Current state

`main` now has an installable Python core, BharatStock REST and Drishti MCP adapters, and a temporary local browser workbench. Synthetic mode is the default: fictional companies and data, no provider network. The adapters passed offline integration tests. The user’s 21 October page-export evidence shows a successful eight-call RELIANCE run: snapshot, quarterly/annual financials, ratios and EOD prices through BharatStock, plus Drishti news, announcements and earnings discovery. Broader coverage, actual credit reconciliation, source accuracy and several live presentation paths remain pending. Margin's own MCP server is deferred.

The earlier corpus/PDF implementation is preserved on the pushed [`d1` branch](https://github.com/rishitttt/margin-mcp/tree/d1) at `c77963d`. Old corpus commands do not apply to this runtime.

**15 November planning update:** the [active plan](docs/plan.md) now prioritizes retrieval repairs, stable fact/receipt contracts, deterministic analysis and DCF integration, then Python/MCP packaging. Citation verification and sentiment protocols are deferred. The professor's proposal is retained as a **separate optional research harness** consuming Margin's public interface; snapshots, answer keys and agent experiments are not product requirements or implemented features. The [7 November research review](docs/design/research-environment-review.md) preserves the earlier analysis, with its old priorities explicitly superseded.

**15 November implementation:** typed financial facts, compatibility/unit checks, comparisons/margins/cash-flow/CAGR/TTM and explicit-input FCFF/DCF/sensitivity/scenarios are now implemented, with local workbench controls. News/earnings shapes and detail navigation were repaired after fresh provider probes; selected Drishti schemas were reviewed/refreshed. See [financial analysis](docs/financial-analysis.md). Financial results now populate fact selectors automatically. Five company financial workflows can reuse retained data or preview one financials request and return ordinary result cards. These calculations do not automatically populate a source-supported company valuation. The research harness, citation verification, sentiment protocols and downstream MCP remain deferred.

## Run locally

Requires Python 3.12 or newer; dependency constraints were tested on Python 3.12/macOS ARM.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[workbench,dev]'
.venv/bin/margin-workbench --mode synthetic --port 8765
```

Open [the local workbench](http://127.0.0.1:8765). Choose a task for fictional `SYNTHA`: Finance or Retrieval. The redesigned function lab exposes all 13 retrieval operations, nine company workflows and the 15 local calculations; the dedicated DCF tab/form is temporarily removed. Preview its inputs/source/cost, then Run. Retrieval defaults to Snapshot only; earnings details also preview before running. No keys or subscriptions are needed for synthetic mode. See the [workbench guide](docs/workbench.md) for scenarios, live-mode controls, API usage, retention and limitations.

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
- [Agent CLI, Codex skill and optional private pilot](docs/agent-interface.md)
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
