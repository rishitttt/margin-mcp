# Project context and handoff

Current as of 24 September 2026. This is a concise handoff; [implementation status](implementation.md) is the detailed record of delivered behavior and validation. Use the [documentation index](README.md) to navigate usage, proposals and historical research.

## Purpose and constraints

Margin supplies Indian listed-company disclosures and source-backed evidence to a user's own AI harness through MCP. It is a professor-supervised four-person project, intended to become a usable product, with a free-prototype budget and approximately six to eight weeks available. Python is the implementation language. Live retrieval is optional; hosting can follow later. Refinitiv Eikon access is not assumed usable and is not a dependency.

The development approach is staged: build a small feature, test it, record the limitations, then expand. Preserve Indian-market scope and financial distinctions such as units, periods, standalone/consolidated basis and Ind AS/IFRS.

## Delivered

- Four read-only metadata MCP tools over stdio, backed by an explicitly imported JSON/SQLite corpus.
- A separate private PDF archive with provenance, hash checks, page inspection and recipe-based extraction for three financial metrics. Candidates remain unreviewed.
- Curated, hash-pinned acquisition for five documents across Wipro, TCS, Infosys and HCLTech. Repeat downloads and private imports succeeded; selected pages were visually inspected.
- Synthetic fixtures and demos, passing software/lint checks and CI configuration; [current validation](implementation.md#validation) records the measured results. CI has not been observed remotely; graphical host validation remains pending.

The five real documents concern September 2025, all four issuers are IT businesses, and the files/databases are local artifacts excluded from Git. A new clone contains synthetic examples and the source catalog, not the private corpus. See the [acquisition guide](acquisition-development.md).

## Current boundaries

The metadata corpus and PDF archive are not yet joined through validated real company/filing references. No extraction runs have been recorded against the acquired real documents at this checkpoint. There is no accepted-fact/review store, financial-fact MCP tool, evidence-serving tool, citation verifier, comparison service, passage search or automated filing discovery. Hosting and source redistribution permissions remain unresolved. Software tests and sample-page inspection do not establish real financial accuracy.

## Next implementation order

1. Curate real entity/filing metadata and link it to archived documents.
2. Extract the three supported metrics on real tables, independently verify their context and persist review decisions.
3. Publish accepted facts with resolvable evidence and canonical citations; verify structured numeric claims.
4. Add compatible period comparisons, passage retrieval and a cited workflow in one real MCP host.
5. Expand history, metrics and sector coverage after those gates pass.

The [functionality/data map](design/functionality-data-map.md), [citation component design](design/citations.md) and [delivery plan](plan.md) describe proposals, not additional implemented tools. Citation creation and verification are first-release priorities: creating a reference must not imply that its claim is supported.

## Source findings to preserve

BSE acquisition works for the tested filings. HCLTech's indexed `AttachLive` attachment returned 404; the same ID under `AttachHis` yielded the verified filing. Some issuer and NSE request routes still fail; these observations do not imply the companies' disclosures are unavailable. Exchange and issuer attachments may be distinct disclosures rather than byte-identical copies. See [BSE results](research/bse-acquisition-results.md) and the dated [source-code investigation](research/existing-mcp-ingestion.md).

Keep original financial labels, missing values, revision history and source locations. Real manifests record operator-declared usage scope; they do not verify licensing. Do not represent synthetic fixtures, unreviewed candidates or model interpretations as accepted real financial evidence.
