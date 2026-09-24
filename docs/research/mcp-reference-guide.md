# MCP implementation references and selection guide

Reviewed 23 September 2026. This compares documented designs; it is not a runtime benchmark or code audit of the referenced projects.

Follow-up, 24 September 2026: Margin now uses Python, official MCP SDK 2.2.0, SQLite and pdfplumber; see [implementation status](../implementation.md). Subsequent [source-code inspection](existing-mcp-ingestion.md) covers selected Indian MCP projects. External documentation below is a dated reference, not a claim of current compatibility.

## Three implementation patterns

An API-backed MCP translates a small set of model-facing tools into requests to an existing API. A corpus-backed MCP queries a database and document index populated by ingestion jobs. A computation-backed MCP performs validated calculations over retrieved inputs. These patterns can coexist in one service.

Margin should combine a stored corpus and deterministic financial operations. Add live API adapters when a source has suitable access and rights. The host's model interprets the question and synthesizes the answer; Margin does not need its own model to retrieve facts or calculate changes.

## Reference projects

| Reference | What to study | Limits |
| --- | --- | --- |
| [Official Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Tool registration, schemas, transports, error handling, examples and client tests | Follow documentation for the pinned release |
| [MoSPI eSankhyiki MCP](https://github.com/nso-india/esankhyiki-mcp) | Discover → metadata → data workflow; separate API client and FastMCP handlers; parameter validation and observability | Statistical API access differs from extracting corporate filings |
| [GitHub MCP server](https://github.com/github/github-mcp-server) | Configurable toolsets, read-only operation and compatibility aliases | A larger service than Margin initially needs |
| [MCP reference servers](https://github.com/modelcontextprotocol/servers) | Small examples of protocol features and SDK use | Repository explicitly says examples are not production-ready solutions |
| [MCP Inspector](https://github.com/modelcontextprotocol/inspector) | Inspect discovery and invoke tools without relying on model behavior | Does not establish financial correctness |
| [Quartr MCP documentation](https://mcp.quartr.com/docs) | Financial research workflows and document-oriented tools | Product reference; do not assume its internal implementation or rights are public |
| [Tapetide repository](https://github.com/Tapetide-hq/nse-bse-indian-stock-market-data-mcp) | Indian-market workflows and distribution | The public local package describes a bridge to a remote backend |

The MoSPI repository documents four tools: `list_datasets`, `get_indicators`, `get_metadata`, and `get_data`. Its architecture separates the server, HTTP client, Swagger parameter definitions, and telemetry. For Margin, use the same principle of discovering valid identifiers and coverage before fetching facts; do not force unnecessary discovery calls when the caller already has validated IDs.

## Formal standard versus engineering choices

The [MCP specification](https://modelcontextprotocol.io/specification/latest/server/tools) defines how capabilities are described and invoked. It covers tool schemas, structured results, protocol messages and errors. The [transport specification](https://modelcontextprotocol.io/specification/latest/basic/transports) defines stdio and Streamable HTTP. Use an SDK for protocol mechanics.

Python versus TypeScript, SQLite versus PostgreSQL, and lexical versus vector search are application choices. They are not mandated by MCP. Likewise MCP does not certify data accuracy, establish source licenses, or prescribe a financial ontology.

The official SDK list includes Python and TypeScript as Tier 1. At this review date, the Python repository describes v2 as its stable release line and documents breaking changes from v1. Avoid combining old tutorial imports with a new unpinned installation. [SDK list](https://modelcontextprotocol.io/docs/sdk), [Python SDK](https://github.com/modelcontextprotocol/python-sdk).

Standalone [FastMCP](https://gofastmcp.com/getting-started/welcome) is a framework that supplies higher-level schema, validation, transport and authentication facilities. It is an alternative development layer, not the protocol specification. Its current documentation warns that main-branch features may precede stable releases. The official SDK and standalone FastMCP have related history but should not be treated as interchangeable packages or version lines.

## Recommended Margin stack

- **Python with the official SDK**, keeping tool handlers thin. Standalone FastMCP is a reasonable alternative if a short compatibility experiment demonstrates useful reductions in work. Do not build both.
- **Typed validation and Decimal calculations** for financial facts and comparisons.
- **SQLite and private local files** for the first corpus; PostgreSQL and object storage when concurrent hosting justifies them.
- **SQL queries for numbers; lexical passage search for narrative evidence.** Add semantic retrieval only when it improves a labeled retrieval benchmark.
- **pdfplumber as the first machine-generated PDF candidate.** Its documentation describes table extraction and visual debugging and notes that it works best on machine-generated PDFs. Evaluate on the real corpus. [Project](https://github.com/jsvine/pdfplumber).
- **Arelle as an XBRL parsing/validation candidate.** Confirm taxonomy compatibility and required validation plugins for Indian filings; it does not eliminate metric mapping. [Project](https://github.com/Arelle/Arelle).
- **Docling as a candidate for harder document layouts and OCR needs**, subject to measured quality and resource costs. Do not require it before observing the need. [Project](https://github.com/docling-project/docling).
- **MCP Inspector, automated client tests, and two real hosts** for interoperability checks. Use a separate manually labeled financial benchmark for answer correctness.

Python/official SDK, SQLite and pdfplumber have since been selected. The other entries remain evaluation candidates, not measured winners. Compare extraction correctness, evidence-location quality, installation effort, memory/latency and maintenance cost before expanding the stack.

## Tool quality requirements

Keep a compact set of domain-oriented tools with explicit names, parameters, reporting basis and coverage. Supply output schemas and structured data with a short readable representation where needed for host compatibility. Return source URLs and exact locations for evidence, rather than expecting the model to reconstruct citations.

Differentiate empty results, unavailable periods, ambiguous entities, incompatible comparisons, upstream failure and permission denial. Bound result sizes and expose pagination. Apply source and user entitlements in code. Read-only annotations are useful metadata, not access controls.

A good first acceptance task is: a caller resolves an Indian company, retrieves two compatible revenue facts, calculates growth, and verifies both cited cells in the original document. Passing a transport test alone is insufficient.

## Reference data for evaluation

Use original company filings as the authoritative reference for what the company reported in that document and period. Compare structured filings against corresponding published statements, keeping conflicts visible. Prefer an independently reviewed source label over a second aggregator's number.

Screener, Trendlyne or an institutionally authorized database can support manual sanity checks within their terms. They are not automatically licensed ingestion sources or authoritative labels: normalization and restatement choices may differ.

A reference label should include company, metric, value, unit, dates, reporting basis, accounting standard, publication/version, and document location. Two reviewers should reconcile disagreements. Keep synthetic edge-case tests distinct from measured accuracy on real filings.
