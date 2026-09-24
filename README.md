# Margin

Evidence-backed financial research for Indian listed companies, accessible from an AI harness through MCP.

Margin is an early Python prototype. It has a working metadata MCP server, private PDF ingestion and a curated document downloader. Financial-fact serving, citation verification and period comparisons are planned, not implemented.

## Current capabilities

| Component | Implemented behavior |
| --- | --- |
| Metadata MCP | `lookup_company`, `get_coverage`, `list_filings`, `get_filing` over local stdio |
| Corpus import | Validated JSON metadata imported into SQLite, with explicit replacement and revision-aware pagination |
| PDF ingestion | Private archive of original bytes, provenance and hashes; physical-page inspection |
| Candidate extraction | Explicit, hash-bound recipes for revenue from operations, profit before tax and profit for the period |
| Acquisition | Bounded HTTPS downloads from a curated URL/hash catalog, with PDF validation and importer manifests |

The MCP tools currently return **metadata only**. The PDF archive is separate from the metadata corpus; extracted candidates remain unreviewed and are not returned as financial facts.

As of 24 September 2026, five real documents across Wipro, TCS, Infosys and HCLTech have been downloaded twice with matching hashes and imported privately. They concern September 2025 and are historical development samples, not current market coverage. **Those PDFs and databases are not included in a clone.** Bundled data is synthetic; the public source catalog and acquisition commands allow a contributor to attempt the documented downloads locally.

See [implementation status](docs/implementation.md) for delivered behavior, validation and limitations.

## Quick start

Run from the repository root with Python 3.12, the tested version:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[dev]'
.venv/bin/margin import-corpus examples/synthetic-corpus.json --db data/demo.sqlite3
.venv/bin/python examples/stdio_demo.py --db data/demo.sqlite3
```

The demo launches a real stdio MCP subprocess and calls all four tools using three fictional companies and five fictional filings. No API key or model subscription is needed. Re-importing into an existing corpus requires `--replace`; it replaces the entire corpus. On Windows, use the virtual environment's `Scripts` directory instead of `bin`.

To start the MCP server for a host:

```sh
.venv/bin/margin serve --db data/demo.sqlite3
```

The process waits for MCP input; it is not an interactive chat. See [development and host configuration](docs/development.md).

## Documents and extraction

- [Acquisition guide](docs/acquisition-development.md): download one reviewed source and import it privately.
- [PDF ingestion guide](docs/ingestion-development.md): generate a synthetic PDF, inspect pages and run an extraction recipe.
- [Implemented MCP contracts](docs/tools.md): inputs, outputs, errors and limits.

Downloading a PDF does not validate its financial values. Real extraction, review/publication, metadata/archive linkage and citation verification remain the next work.

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

The next usable workflow is **real company → filing → reviewed fact → verifiable citation → compatible period comparison**. Start with the existing four-company corpus. The broader target is five selected non-financial companies, eight quarters and two annual reports each, subject to source availability, sector diversity and validation. The [delivery plan](docs/plan.md) describes the proposed sequence and evaluation.

Margin is a four-person, professor-supervised project with a free-prototype budget and a six-to-eight-week delivery window. Live feeds and hosting are optional later work; Refinitiv Eikon is not a dependency. The user's AI harness supplies the model. Margin supports research, not trade execution or personalized investment recommendations.

Keep raw third-party documents, local databases and credentials out of Git. Public download access does not establish hosted redistribution rights; see the [data policy](docs/design/data-policy.md).
