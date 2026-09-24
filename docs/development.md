# Development and local setup

Implemented workflows, current as of 24 September 2026. See [implementation status](implementation.md) for delivered features and [the documentation index](README.md) for other guides.

Run commands from the repository root. Python 3.12 is the tested version. No API key, model subscription or network access is needed after dependency installation for the synthetic demo.

## Install and run

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[dev]'
.venv/bin/margin import-corpus examples/synthetic-corpus.json --db data/demo.sqlite3
.venv/bin/python examples/stdio_demo.py --db data/demo.sqlite3
```

On Windows use the virtual environment's `Scripts` directory instead of `bin`. `requirements-dev.lock` constrains the runtime and development versions tested on macOS; it is not a hash-verified distribution or a complete build-environment lock. CI is configured for Python 3.12 on Linux; its remote result has not yet been observed.

The demo prints four discovered tools and results for coverage, ambiguous name lookup, symbol lookup, consolidated filings and individual filing metadata. All data is labeled synthetic. `Aarya` deliberately matches two fictional companies; `DEMOAARYASW` resolves one. The Deccan company deliberately has no filings.

The import command validates the entire manifest before replacing anything. Re-running it against an existing Margin database requires `--replace`, which replaces the entire corpus rather than merging it. Unrelated databases are rejected. Keep local databases outside version control.

## Connect an MCP host

Start the server using the installed executable and an explicit database path:

```sh
.venv/bin/margin serve --db data/demo.sqlite3
```

This command waits for MCP traffic on stdin; it is not an interactive chat or web server. Stdout is reserved for the protocol and diagnostic logs use stderr. A missing or incompatible database makes startup fail rather than creating an empty corpus.

For hosts that accept an `mcpServers` configuration object, adapt this example to absolute paths on your machine:

```json
{
  "mcpServers": {
    "margin": {
      "command": "/absolute/path/to/margin-mcp/.venv/bin/margin",
      "args": ["serve", "--db", "/absolute/path/to/margin-mcp/data/demo.sqlite3"]
    }
  }
}
```

Configuration locations and formats depend on the host. This template has not been verified in a graphical host. To complete that gate: confirm four tools appear, ask for coverage, look up `Aarya` and verify ambiguity is preserved, then retrieve `DEMOAARYASW` filings and confirm the response calls them synthetic metadata. Record the host/version and observed results. Do not interpret these checks as financial accuracy evaluation.

## Import your own metadata

Generate the authoritative input schema:

```sh
.venv/bin/margin schema > /tmp/margin-corpus-schema.json
```

Use the example manifest and generated schema together. The import boundary separates companies, securities and exchange listings. It checks duplicate identities, foreign references, reporting periods and timezone-aware publication/observation timestamps. Identifier format validation does not verify identifiers against an exchange registry.

For a real corpus, set `data_kind` to `real`, declare `metadata_usage_basis`, provide company identity source URLs/observation times and filing source URLs, and describe coverage gaps. These fields record the operator's declarations; Margin does not establish rights or verify URLs. Import does not download any content. Keep restricted manifests and third-party documents out of Git; see [data policy](design/data-policy.md).

## Validation and contribution

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
.venv/bin/python -m pip check
```

The suite covers metadata/MCP behavior, PDF ingestion and acquisition. See [current validation results](implementation.md#validation) for the observed counts and outcomes. Checks include invalid/duplicate inputs, replacement protection, unrelated and corrupt databases, identity ambiguity, filters, empty coverage, revision-checked pagination, and real stdio subprocess calls. Integration tests validate generated result schemas, annotations and actionable errors in both automatic and legacy client modes, including launching from outside the repository. See [PDF ingestion](ingestion-development.md) and [acquisition](acquisition-development.md) for those workflows and validation limits.

Keep financial logic in services, data contracts in models and MCP handlers thin. Follow [AGENTS.md](../AGENTS.md) and the [documentation update matrix](README.md#what-to-document-and-where) for code, contract, usage and handoff changes. Real documents are already archived locally, outside Git. The next milestone is to link real metadata to that archive, independently review extraction and publish facts with verifiable evidence; see [implementation](implementation.md#next-gate).
