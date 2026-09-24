# Curated document acquisition

Implemented workflow, current as of 24 September 2026. This guide downloads a specific reviewed document and prepares it for private import. It does not discover new filings or query a live exchange feed.

## Prerequisites

Complete the [development setup](development.md) and run commands from the repository root. The acquisition example also requires system `curl` with JSON `--write-out` and `--max-filesize` support, a working certificate trust store, and HTTPS network access. Python 3.12 and system curl on macOS were used for the recorded live checks. Network behavior on other machines may differ.

Original PDFs and databases are excluded from Git. A fresh clone has no real corpus. The [source catalog](../examples/public-document-sources.json) contains URLs, descriptive metadata and reviewed SHA-256 values; it does not include the documents themselves.

## Available sources

| Source key | Document | Recorded pages |
| --- | --- | ---: |
| `wipro-q2-fy26-reg33` | Issuer-hosted Regulation 33 results | 33 |
| `wipro-q2-fy26-press` | BSE press release and media presentation | 17 |
| `tcs-q2-fy26-results` | BSE results and auditor reports | 22 |
| `infosys-q2-fy26-board` | BSE board outcome and financial package | 198 |
| `hcltech-q2-fy26-results` | BSE results and limited review reports | 27 |

All concern September 2025. They are different documents, not interchangeable copies. The Infosys package contains multiple accounting bases and currencies; choose the relevant section before extraction. Successful access does not establish public hosting or redistribution rights.

## Download and import

Choose a fresh output directory:

```sh
.venv/bin/python examples/acquire_document.py tcs-q2-fy26-results \
  --output data/private/tcs-acquisition
.venv/bin/margin import-document data/private/tcs-acquisition/results.pdf \
  --manifest data/private/tcs-acquisition/document.json \
  --archive data/private/real-archive
```

The downloader writes three files only after transfer, PDF and hash validation:

- `results.pdf`: original source bytes, without rewriting.
- `acquisition.json`: source/discovery URLs, acquisition time, HTTP/TLS details, bytes, pages and hash.
- `document.json`: provenance manifest for `import-document`, labelled `real` and `local_only`.

The import command returns a `document_id`. Use it with `inspect-document` as described in the [PDF ingestion guide](ingestion-development.md). Import does not populate the metadata MCP corpus, accept financial facts or establish licensing.

To repeat a download, select another fresh directory; existing acquisition directories are never overwritten. The original Wipro command remains available:

```sh
.venv/bin/python examples/acquire_wipro.py --output data/private/wipro-acquisition
```

## Validation and failure behavior

The shared implementation uses verified HTTPS, disables curl's default configuration, and sets a 10-second connect timeout, 30-second transfer deadline, 35-second process deadline and 25 MiB limit. It requires HTTP 200, unencrypted valid PDF bytes within the 500-page bound, and an exact match to the catalog hash. It does not follow redirects or automatically retry.

| Failure | Meaning and next action |
| --- | --- |
| `OUTPUT_EXISTS` | Use a new output directory to preserve the earlier acquisition. |
| `HTTP_403` / `HTTP_429` | Access denial or rate limit; investigate the permitted route instead of repeatedly retrying. |
| `HTTP_404` | Re-check the published link or a confirmed historical location. HCLTech's live-to-historical path fix was verified for one attachment, not implemented as a general fallback. |
| Other non-200 status, including redirects | Inspect the source URL; no PDF is published by the downloader. |
| `DOWNLOAD_FAILED` | Inspect the curl exit/error text to distinguish certificate, transport or size failures. |
| `DOWNLOAD_TIMEOUT` | The curl process exceeded its deadline. A longer timeout is not evidence of a source fix. |
| `INVALID_RECEIPT` | Curl returned incomplete transfer metadata; check the installed curl version. |
| `INVALID_PDF` / `PDF_PROCESSING_FAILED` | The body is not a supported, readable PDF; HTML error pages must not be imported. |
| `SOURCE_CHANGED` | The returned PDF differs from the reviewed bytes. Inspect the new document before changing the catalog hash or metadata. |

Do not disable certificate verification. A changed source or unavailable URL should remain visible as a failed acquisition, not silently become another document with the old identity.

## Adding a source

Discover and download it in a bounded research experiment first. Verify the issuer, document purpose, publication date, accounting sections and reporting period; inspect representative pages. Compute its SHA-256 and add an entry matching `AcquisitionSource` in `src/margin_mcp/acquisition.py`. Record how the URL was discovered and what was actually verified. Keep originals and diagnostic responses private.

The catalog is deliberately curated. It can reproduce known files but cannot discover replacements, certify completeness or validate their financial numbers. Automatic discovery, refresh, accepted-fact publication and citation verification remain future work.

## Evidence and tests

See [BSE results](research/bse-acquisition-results.md) and [issuer troubleshooting](research/acquisition-troubleshooting.md) for recorded live observations. Live network checks are manual; CI uses generated PDFs and mocked transfers. The [implementation status](implementation.md#validation) records the latest observed test results.
