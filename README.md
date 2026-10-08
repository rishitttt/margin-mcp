# Margin

Evidence-backed financial research for Indian listed companies, accessible from an AI harness through MCP.

Margin is an early Python prototype. It has a metadata MCP server with agent discovery guidance, private PDF ingestion and a curated document downloader. Financial-fact serving, citation verification and period comparisons are planned, not implemented.

The active proposal, updated 8 October 2026, is to **aggregate BharatStock MCP and Drishti MCP into one Margin connection**, then add normalized financial/event research tools. The user now permits paid plans; research recommends BharatStock Developer + Drishti Starter at a published ₹3,000/month. No aggregation code or authenticated data integration exists yet. See the [aggregation architecture and stages](docs/design/mcp-aggregation.md) and [endpoint, quota and coverage research](docs/research/mcp-provider-feasibility.md). Building or maintaining a Margin financial corpus is outside this scope.

The previous committed implementation is preserved on local branch `d1` at `c77963d`. It also remains on `main`; this planning task has not cleared or reset it. The capabilities and quick start below describe that existing local prototype, not the proposed aggregated MCP.

## Current capabilities

| Component | Implemented behavior |
| --- | --- |
| Metadata MCP | `lookup_company`, `get_coverage`, `list_filings`, `get_filing` over local stdio |
| Discovery guidance | `get_discovery_plan`, a workflow resource and `discover_filings` prompt; offline HTML document-link discovery |
| Corpus import | Validated JSON metadata imported into SQLite, with explicit replacement and revision-aware pagination |
| PDF ingestion | Private archive of original bytes, provenance and hashes; physical-page inspection |
| Candidate extraction | Explicit, hash-bound recipes for revenue from operations, profit before tax and profit for the period |
| Acquisition | Bounded HTTPS downloads from a curated URL/hash catalog, with PDF validation and importer manifests |

The four corpus-query tools return **metadata only**; the discovery tool returns guidance without fetching sources. The PDF archive is separate from the metadata corpus; extracted candidates remain unreviewed and are not returned as financial facts.

As of 25 September 2026, seven real documents across Wipro, TCS, Infosys and HCLTech have been downloaded repeatedly with matching hashes and imported privately, including Infosys FY25 annual report and Q2 FY26 transcripts. They are historical development samples, not current market coverage. A 36-cell extraction study matched visually transcribed development expectations; independent review remains pending. See the [corpus trial](docs/research/corpus-trial.md). **Those PDFs and databases are not included in a clone.** Bundled data is synthetic; the public source catalog and acquisition commands allow a contributor to attempt the documented downloads locally.

See [implementation status](docs/implementation.md) for delivered behavior, validation and limitations.

## Quick start

Run from the repository root with Python 3.12, the tested version:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[dev]'
.venv/bin/margin import-corpus examples/synthetic-corpus.json --db data/demo.sqlite3
.venv/bin/python examples/stdio_demo.py --db data/demo.sqlite3
```

The demo launches a real stdio MCP subprocess and calls the four metadata tools using three fictional companies and five fictional filings, then retrieves the discovery plan/resource/prompt for a real-company search target without fetching it. No API key or model subscription is needed. Re-importing into an existing corpus requires `--replace`; it replaces the entire corpus. On Windows, use the virtual environment's `Scripts` directory instead of `bin`.

To start the MCP server for a host:

```sh
.venv/bin/margin serve --db data/demo.sqlite3
```

The process waits for MCP input; it is not an interactive chat. See [development and host configuration](docs/development.md).

## Documents and extraction

- [Acquisition guide](docs/acquisition-development.md): download one reviewed source and import it privately.
- [PDF ingestion guide](docs/ingestion-development.md): generate a synthetic PDF, inspect pages and run an extraction recipe.
- [Implemented MCP contracts](docs/tools.md): inputs, outputs, errors and limits.

Downloading a PDF does not validate its financial values. Existing four-company extraction recipes remain reusable experiments; their review and archive-linkage gaps are documented. The active work is external adapters, temporary evidence retrieval and citations, without making local archive completion a prerequisite.

## Development

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
.venv/bin/python -m pip check
```

See [current validation results](docs/implementation.md#validation) for the latest observed tests, lint/formatting and dependency checks. CI is configured for Python 3.12 on Linux; a remote run and graphical MCP-host validation have not been observed. Software tests do not establish real financial extraction accuracy.

Contributors and their coding agents should follow [AGENTS.md](AGENTS.md) and the [documentation update matrix](docs/README.md#what-to-document-and-where). Read the core orientation files first, then only the guides and research relevant to the task.

```text
src/margin_mcp/   Python models, stores, services, acquisition and MCP/CLI entry points
examples/         Synthetic fixtures, runnable demos and curated source catalog
tests/            Metadata, stdio integration, PDF ingestion and acquisition tests
docs/             Usage guides, implementation status, plans and dated research
.github/          CI configuration
```

## Roadmap and documentation

Start with the [documentation index](docs/README.md). The [feature/data map](docs/design/functionality-data-map.md) defines priorities and acceptance checks; the [citation design](docs/design/citations.md) specifies the proposed creation and verification component.

The next milestone is **one MCP connection → namespaced read tools from both providers**, without corpus import. Authenticate and measure actual schemas, costs and coverage before building normalized research, comparisons or citation verification. The [delivery plan](docs/plan.md) links the current stage gates; older corpus and temporary-session proposals are deferred reference material.

Margin is a four-person, professor-supervised project. The original September estimate was six to eight weeks; the new schedule and provider accounts remain to be confirmed. Paid plans are now acceptable; live feeds and hosting are optional later work. Refinitiv Eikon is not a dependency. The user's AI harness supplies the model. Margin supports research, not trade execution or personalized investment recommendations.

Keep raw third-party documents, local databases and credentials out of Git. Public download access does not establish hosted redistribution rights; see the [data policy](docs/design/data-policy.md).
