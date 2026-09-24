# Implementation status and decisions

Current as of 24 September 2026. This document describes delivered behavior. [Tool contracts](tools.md) specify the implemented MCP API; files in [design/](README.md#design-proposals) describe intended extensions.

## Delivered components

| Component | Code | Current behavior |
| --- | --- | --- |
| Metadata contracts | `models.py` | Company/security/listing identities, filing records, corpus provenance and typed responses |
| Metadata storage | `storage.py` | Validated atomic JSON-to-SQLite import, explicit replacement, revision token and read-only queries |
| Query services | `services.py` | Company resolution, declared coverage, filtered/paginated filings and individual filing metadata |
| MCP server | `server.py` | Four read-only metadata tools over stdio using official MCP SDK 2.2.0 |
| PDF contracts | `ingestion_models.py` | Document manifests and hash-bound financial extraction recipes |
| PDF archive/extraction | `ingestion.py` | Immutable PDF blobs, provenance registrations, physical-page inspection and unreviewed candidate runs |
| Acquisition | `acquisition.py` | Bounded verified HTTPS, PDF/hash checks, receipts and import manifests for curated sources |
| CLI | `cli.py`, `__main__.py` | Metadata import/schema/server and PDF import/inspection/extraction/schema commands |

All code lives under `src/margin_mcp/`. Examples include the synthetic metadata corpus, an MCP client demo, a generated PDF/recipe demo, and `acquire_document.py` with its five-source catalog. Acquisition is an example command outside the MCP query path; `acquire_wipro.py` preserves the original entry point.

## Current behavior and limits

- Python 3.12 is tested; runtime/development constraints are in `requirements-dev.lock`.
- `lookup_company`, `get_coverage`, `list_filings` and `get_filing` return metadata only. `get_filing` always reports `content_available=false`.
- Metadata imports preserve issuer/security/listing distinctions. Queries do not create missing databases. Replacement requires the explicit CLI flag.
- Pagination uses offsets with a corpus revision token to detect replacement. It does not pin a snapshot across separate calls.
- The metadata store loads one validated snapshot into memory. Its bounds are 5 MiB, 1,000 companies and 10,000 filings, not a whole-market scalability claim.
- The separate `documents.sqlite3` archive stores original bytes, provenance and extraction runs. Company/filing references are not yet joined to metadata records.
- PDFs must be unencrypted, at most 25 MiB and 500 pages. Recipes use physical pages, bounding boxes, context anchors and exact decimal parsing.
- Supported candidate metrics are revenue from operations, profit before tax and profit for the period, in INR with explicit scale. Runs are `needs_review` or `failed`; no accepted-fact publication exists.
- Acquisition uses reviewed URL/hash entries, verified HTTPS and bounded requests. It does not crawl, automatically discover filings, follow redirects or refresh the corpus.
- Synthetic data is explicitly labelled. Real manifests record operator declarations and `local_only` processing, not independently established redistribution permission.

See the [development](development.md), [ingestion](ingestion-development.md) and [acquisition](acquisition-development.md) guides for reproducible commands.

## Real-document checkpoint

Five distinct PDFs have been downloaded twice with matching hashes and imported privately:

| Issuer | Document | Pages |
| --- | --- | ---: |
| Wipro | Issuer-hosted Q2 FY26 Regulation 33 results | 33 |
| Wipro | BSE-hosted press release and media presentation | 17 |
| TCS | BSE-hosted quarterly results and auditor reports | 22 |
| Infosys | BSE-hosted board outcome and financial package | 198 |
| HCLTech | BSE-hosted quarterly results and limited review reports | 27 |

These are historical September 2025 IT-sector samples. Original files, receipts, page renders and databases are ignored local artifacts, absent from a new clone. The source catalog is included. See [acquisition evidence](research/bse-acquisition-results.md) for observed URLs and limitations.

Selected pages were visually inspected. No real-document extraction runs, accepted financial facts or financial accuracy benchmark have been completed. Download and PDF validation are not financial verification.

## Validation

Last observed locally on 24 September 2026:

| Check | Result |
| --- | --- |
| Metadata/services and real stdio integration | 39 tests passed |
| PDF ingestion/extraction on controlled fixtures | 28 tests passed |
| Acquisition validation with mocked transfers | 13 tests passed |
| Total | **80 tests passed** |
| Ruff lint and formatting | Passed |
| Dependency consistency | Passed |

Live source downloads were separate manual checks, not CI dependencies. Stdio integration exercised automatic and legacy client modes. CI is configured in `.github/workflows/test.yml` for Python 3.12 on Linux; a remote run has not been observed. Graphical host usage, real financial accuracy, citation verification and hosted deployment remain unverified.

## Next gate

Connect real entity/filing metadata to the archive, build and independently review real extraction recipes, then expose accepted facts with resolvable citations. Add compatible comparisons only after the input facts and their contexts are verified. See the [feature/data map](design/functionality-data-map.md) and [citation design](design/citations.md).

Automatic exchange discovery, broader history/sectors, ownership, prices and hosting follow this workflow. The [delivery plan](plan.md) provides scope gates and benchmark targets; its targets are not observed results.

## Milestone history

| Date | Milestone | Validation at that time |
| --- | --- | --- |
| 23 September 2026 | Metadata corpus, four MCP tools and synthetic client demo | 39 tests |
| 23 September 2026 | Private PDF archive and region-based candidate extraction | 67 tests |
| 23 September 2026 | Reproducible issuer-hosted Wipro acquisition | 73 tests |
| 24 September 2026 | Four BSE documents, shared downloader and curated catalog | 80 tests |
| 24 September 2026 | Feature/data map and citation creation/verification design | Documentation only; no new tools |

Earlier research notes preserve the observations made at their dates. This status document and implemented tool contracts take precedence over their original “next experiment” suggestions.
