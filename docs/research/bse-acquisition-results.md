# Working exchange acquisition: 24 September 2026

Follow-up, 25 September 2026: [corpus trial](corpus-trial.md) records new aggregator-discovered BSE documents, fresh failure checks and real extraction results.

Four BSE-hosted PDFs were downloaded twice each, with matching hashes across the two acquisitions, and imported into the private archive. Together with the earlier issuer-hosted Wipro results, we now have five distinct real documents for four companies. This establishes a small usable document set, not comprehensive exchange coverage.

## Acquired documents

| Catalog key | Contents | Pages | Bytes | Source |
| --- | --- | ---: | ---: | --- |
| `tcs-q2-fy26-results` | Audited standalone/consolidated results and auditor reports | 22 | 6,202,548 | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/b5a9119d-5d7f-4030-a898-879287327a87.pdf) |
| `hcltech-q2-fy26-results` | Unaudited standalone/consolidated results and limited review reports | 27 | 7,628,005 | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/eb3e5f52-2c5b-497b-8cb2-bfda6772bed2.pdf) |
| `infosys-q2-fy26-board` | Board outcome and financial package containing multiple accounting bases and statements | 198 | 24,602,967 | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/1f505822-671c-4544-a6aa-f7274b3aa685.pdf) |
| `wipro-q2-fy26-press` | Press release and media presentation; distinct from the 33-page Regulation 33 filing | 17 | 1,165,930 | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/7f1a68bf-fa8f-4732-80a5-40416354c498.pdf) |

All concern the quarter ended 30 September 2025. Publication dates were checked against covering letters: TCS 9 October; HCLTech 13 October; Infosys and Wipro 16 October 2025. Downloads returned HTTP 200 with verified TLS. The second transfers took approximately 0.22-1.05 seconds in this environment; this is a small observation, not an availability guarantee.

The exact URLs, metadata and SHA-256 values are in [the curated catalog](../../examples/public-document-sources.json). Discovery was through targeted web research, followed by direct local downloads. No exchange listing API was integrated.

## What fixed acquisition

**An independent primary source:** BSE attachments delivered TCS and Infosys filings despite issuer-site access denials. HCLTech's issuer delivery failure also did not affect its BSE attachment. These are separately verified filings for the required period, not byte-equivalent copies of the failed issuer URLs. In particular, the earlier failed TCS download was an annual report; the acquired TCS filing is quarterly results.

**A historical attachment path:** the indexed HCLTech URL under `AttachLive` returned HTTP 404 and an HTML body. Testing the same attachment identifier under `AttachHis` returned the 27-page PDF. This supports using that verified historical URL for this filing. It does not prove every 404 can be fixed by path substitution. The catalog preserves the originally discovered URL separately from the successful source URL.

**Separate TLS and HTTP diagnosis:** all new probes verified TLS. Infosys's issuer PDF still returned 403. An alternate official HCLTech PDF path and the previously identified NSE Wipro attachment still produced curl error 92 (HTTP/2 stream error) after TLS with no bytes. Previous HTTP/1.1 attempts timed out. Neither source's exact network/edge failure has been established. Certificate verification was never disabled, and access denials were not repeatedly retried.

**Check bytes and document identity:** HTTP success alone is insufficient. A valid PDF, page bounds, maximum byte size and a previously reviewed SHA-256 are required by the reproducible command. No 403/404 HTML response was imported. File titles are taken from document contents, not guessed from misleading filenames: HCLTech's issuer filename says audited, while its acquired filing identifies unaudited results and limited review reports.

## Repeat the working path

The [acquisition guide](../acquisition-development.md) is the maintained usage reference; the commands below reproduce this recorded experiment.

From the repository root, use a fresh output directory:

```sh
.venv/bin/python examples/acquire_document.py tcs-q2-fy26-results \
  --output data/private/tcs-reproduction
.venv/bin/margin import-document data/private/tcs-reproduction/results.pdf \
  --manifest data/private/tcs-reproduction/document.json \
  --archive data/private/real-archive
```

Other source keys are listed above; the catalog also includes `wipro-q2-fy26-reg33`. `examples/acquire_wipro.py` remains a compatibility entry point for the original command. This is intentionally a curated reproduction workflow: a new document first needs discovery, content inspection and a catalog entry. Automatic discovery, archive-path fallback and periodic refresh are not implemented.

Shared acquisition code lives in `src/margin_mcp/acquisition.py`. It uses system curl with its default config disabled, verified HTTPS, no redirects/retries, 10-second connect and 30-second transfer limits, a 35-second process limit, and the existing 25 MiB/500-page PDF bounds. Changed hashes require review. Success produces `results.pdf`, `acquisition.json` and `document.json`; existing directories are protected. The importer remains a separate operation.

## Local evidence and validation

Validated second copies, receipts, manifests and import results are stored in `data/private/bse-verified/<catalog-key>/`. The shared archive is `data/private/real-archive/documents.sqlite3`. Initial response headers, transfer diagnostics and rendered inspection pages are in `data/private/source-probes-20260924/`. All are ignored by Git.

Visual checks covered TCS physical page 8 (consolidated results), HCLTech page 2 (consolidated Ind AS results), Infosys page 32 (IFRS INR press-release tables), and Wipro page 1 (cover identifying the release/presentation). These checks confirm document purpose and sample page readability; they do not validate every page or extract accepted financial facts. The Infosys package needs section selection before extracting Ind AS versus IFRS figures. TCS/HCLTech text contains recognition artifacts despite visible tables.

Offline acquisition tests cover TLS/HTML/HTTP failures, timeout, transport errors, malformed receipts, changed documents, output preservation, catalog validation and HTTPS-only sources. Live requests remain manual checks outside CI. Full suite: **80 tests passed**, Ruff checks passed.

Next work: link real metadata to the archive, validate extraction and review records, and expose accepted facts with citations. Automated discovery follows the first working evidence workflow; see the [feature/data map](../design/functionality-data-map.md). MCP tools still expose only metadata; no real extracted facts have been published. Hosted redistribution rights remain a separate unresolved deployment requirement.
