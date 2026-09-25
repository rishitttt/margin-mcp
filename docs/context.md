# Project context and handoff

Current as of 25 September 2026. This is a concise handoff; [implementation status](implementation.md) is the detailed record of delivered behavior and validation. Use the [documentation index](README.md) to navigate usage, proposals and historical research.

## Purpose and constraints

Margin supplies Indian listed-company disclosures and source-backed evidence to a user's own AI harness through MCP. It is a professor-supervised four-person project, intended to become a usable product, with a free-prototype budget and approximately six to eight weeks available. Python is the implementation language. Live retrieval is optional; hosting can follow later. Refinitiv Eikon access is not assumed usable and is not a dependency.

The development approach is staged: build a small feature, test it, record the limitations, then expand. Preserve Indian-market scope and financial distinctions such as units, periods, standalone/consolidated basis and Ind AS/IFRS.

Confirmed direction: focus on external APIs/tools and temporary evidence sessions. Do not build or expand our own financial corpus; preserve existing local functionality as optional utilities and regression fixtures. Users should not need to maintain a personal financial database for the external path. Tijori, BharatStockAPI and Drishti are examples, not an exclusive provider list. Financial research, discovery, extraction, citations and comparisons remain in scope; news and sentiment add research capabilities. See [architecture](design/architecture.md#extensible-capabilities-and-preservation). External adapters, session expiry and sentiment are not implemented, and the current server still requires an imported metadata corpus.

## Delivered

- Four read-only metadata MCP tools over stdio, plus a discovery-plan tool, workflow resource and prompt. Guidance uses host-provided web capabilities; it does not fetch or ingest through MCP.
- Offline HTML link discovery preserves unverified URL candidates and source-page provenance.
- A separate private PDF archive with provenance, hash checks, page inspection and recipe-based extraction for three financial metrics. Candidates remain unreviewed.
- Curated acquisition for seven documents across four companies, now including Infosys FY25 annual report and Q2 FY26 transcripts. Repeat downloads/imports succeeded; two Tijori copies matched BSE hashes.
- Four real recipes extracted 36 selected cells matching visual development transcriptions. Independent review remains pending; 31 pages in the Infosys results package lack text extraction; sampled pages are scans. See the [corpus trial](research/corpus-trial.md).
- Synthetic fixtures and demos, passing software/lint checks and CI configuration; [current validation](implementation.md#validation) records the measured results. CI has not been observed remotely; graphical host validation remains pending.

The seven real documents cover FY25 and September 2025 reporting; all four issuers are IT businesses, and the files/databases are local artifacts excluded from Git. A new clone contains synthetic examples and the source catalog, not the private corpus. See the [acquisition guide](acquisition-development.md).

The previous five-company/eight-quarter corpus expansion is superseded, not an active collection target. Existing source experiments remain useful reference evidence. Tijori/Screener can provide discovery leads; [tested access levels](research/corpus-trial.md#tijori-access-inventory) distinguish indexed links, acquired files and untested platform data.

## Current boundaries

The metadata corpus and PDF archive are not yet joined through validated real company/filing references. Four real extraction runs are recorded; all candidates remain unreviewed. There is no accepted-fact/review store, financial-fact MCP tool, evidence-serving tool, citation verifier, comparison service, passage search or automated filing discovery. Hosting and source redistribution permissions remain unresolved. Software tests and sample-page inspection do not establish real financial accuracy.

## Next implementation order

1. Define shared capability, provenance and evidence contracts; evaluate one accessible external source with actual bounded requests.
2. Add provider-only startup without metadata import, preserving existing local-tool behavior and regression checks.
3. Add temporary document fetch, page-aware reading/search, evidence references and explicit expiry/cleanup.
4. Add a complementary source, compatible comparisons and citations; preserve provider-reported versus extracted/reviewed status.
5. Evaluate a cited workflow in one real host, then news/sentiment support, deduplication and source conflicts.

Provider choice remains open. The archive's existing metadata-linkage and independent-review gaps remain documented, but completing a local fact warehouse is not a dependency for this sequence. No planned corpus expansion, historical backfill or scheduled collection.

The [architecture](design/architecture.md), [functionality/data map](design/functionality-data-map.md), [citation design](design/citations.md) and [delivery plan](plan.md) describe proposals, not additional implemented tools. Citation creation and verification remain priorities; creating a reference must not imply its claim is supported.

## Source findings to preserve

BSE acquisition works for the tested filings. HCLTech's indexed `AttachLive` attachment returned 404; the same ID under `AttachHis` yielded the verified filing. Some issuer and NSE request routes still fail; these observations do not imply the companies' disclosures are unavailable. Exchange and issuer attachments may be distinct disclosures rather than byte-identical copies. See [BSE results](research/bse-acquisition-results.md) and the dated [source-code investigation](research/existing-mcp-ingestion.md).

Keep original financial labels, missing values, revision history and source locations. Real manifests record operator-declared usage scope; they do not verify licensing. Do not represent synthetic fixtures, unreviewed candidates or model interpretations as accepted real financial evidence.
