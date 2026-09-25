# Exchange sources and existing MCP acquisition approaches

Latest experiment: [25 September corpus trial](corpus-trial.md) adds two documents through aggregator-discovered BSE links and tests 36 real financial cells. The earlier investigation below remains a dated record.

## Follow-up: 25 September 2026

Three additional public repositories were cloned into temporary folders for source inspection only. None was installed or executed. Their underlying public sources were tested separately with bounded requests; see the [trial results](corpus-trial.md#new-source-routes-tested).

| Project and inspected revision | Actual source strategy in code | Implication for Margin |
| --- | --- | --- |
| LogeshR15/screener-mcp, `396dd7d315a2a5a1184df8165d78ae5cb3f3503d` | [Document tools](https://github.com/LogeshR15/screener-mcp/blob/396dd7d315a2a5a1184df8165d78ae5cb3f3503d/src/screener_mcp/tools/documents.py) parse annual-report/concall links from Screener HTML; fall back to NSE annual-report metadata. A separate pdfplumber/RAG path downloads linked PDFs | Copy the separation of discovery and document processing as an architectural idea. Public Screener Infosys HTML worked, and two original BSE documents were acquired. No reason to adopt its embedding stack before a retrieval benchmark |
| LaZZy0v0/tijori-finance-mcp, `64be6c49f99a3fb3355ab5a727ce05cf260a7acc` | [Company tools](https://github.com/LaZZy0v0/tijori-finance-mcp/blob/64be6c49f99a3fb3355ab5a727ce05cf260a7acc/src/tools/company.js) inspect the knowledge-base section for `files.tijorifinance.com` links. The [browser layer](https://github.com/LaZZy0v0/tijori-finance-mcp/blob/64be6c49f99a3fb3355ab5a727ce05cf260a7acc/src/browser.js) loads saved authenticated browser state | Our separate public-page test needed no account and found matching mirrors of the two BSE files. This does not establish access to the project's authenticated features or reuse rights. Filenames alone are insufficient period/date evidence |
| vanshikaaa01/nse-bse-mcp, `b3749a8b3fe6cd2788736be0375dad453875b96b` | [Server](https://github.com/vanshikaaa01/nse-bse-mcp/blob/b3749a8b3fe6cd2788736be0375dad453875b96b/server.py) calls yfinance's `Ticker.financials`, `balance_sheet` and `cashflow`, scales values to crore | Its NSE/BSE branding does not imply original exchange-PDF ingestion. Our plain Yahoo financials-page request got 429; yfinance itself was not run. Normalized provider values would need original evidence and financial-context verification |

The earlier Tapetide inspection found a hosted-service bridge; its proprietary upstream collection remains unknown. Do not infer that its advertised coverage supplies a reusable free raw-document corpus. Software licensing, successful public viewing, data storage and hosted redistribution are different questions.

The useful result was **Screener discovery → original BSE files**, with **Tijori copies checked by hash**. Margin's new offline parser generalizes observed HTML anchor extraction without importing third-party code, logging in, crawling sites or automatically downloading candidates. Paid/authenticated providers remain untested options, not current corpus dependencies. The [Tijori access inventory](corpus-trial.md#tijori-access-inventory) separates annual-report, earnings-release, presentation and call-document URL candidates from the two files actually acquired, and records untested platform-data boundaries.

Follow-up: [four BSE documents have now been acquired and imported](bse-acquisition-results.md), with a reusable command and curated catalog. Discovery remains manual; the proposed exchange listing adapter below is still pending.

Investigated 24 September 2026 IST. This supplements [acquisition troubleshooting](acquisition-troubleshooting.md). Source inspection is not a successful live integration test.

## Source families

Company investor-relations sites and exchange archives are both primary document sources. NSE/BSE collate disclosures submitted by issuers, while issuer websites organize their own results, reports and presentations. SEBI's [corporate-filings directory](https://www.sebi.gov.in/curation/corporate_filings.html) links to both exchanges' financial results, shareholding, governance and other disclosure categories. This is a useful official discovery map, not itself a bulk document API.

An exchange attachment can be identical to an issuer-hosted PDF, contain an additional covering letter, or be a different disclosure concerning the same event. Match company, period, document purpose, reporting basis and revision before treating files as substitutes. SHA-256 detects byte-identical files; different hashes do not establish different financial content. Keep provenance for each location even when bytes match.

Provider APIs are another route to normalized financial fields or document metadata. Their coverage, evidence links, credentials and storage conditions need evaluation independently. An MCP that returns financial numbers does not necessarily acquire original PDFs or preserve page-level evidence.

For cross-listed Indian companies, foreign regulatory filings can provide supplementary evidence, but are not a general Indian-market corpus. For example, this [Wipro SEC exhibit](https://www.sec.gov/Archives/edgar/data/1123799/000119312525245284/d62510dex994.htm) reports consolidated IFRS results; it must not silently replace an Ind AS source.

## What we actually obtained

Wipro's issuer-hosted Q2 FY26 results downloaded successfully twice: 33 pages, 3,375,941 bytes, identical SHA-256. It is imported into the private archive, and physical page 11 was rendered and visually checked. See the troubleshooting note for receipts and reproduction commands. No real financial candidates have been accepted or published through MCP.

A related [NSE Wipro attachment](https://nsearchives.nseindia.com/corporate/Wipro_Secretarial_16102025171657_FinancialswithUDIN.pdf) was readable through web research. It is a ten-page follow-up containing auditor reports with UDINs, dated 16 October 2025. Its covering letter explicitly refers to previously filed financial statements. It is not the same 33-page results document.

Direct local acquisition of that NSE attachment failed after successful TLS: HTTP/2 produced a stream INTERNAL_ERROR with no bytes; HTTP/1.1 timed out after 15 seconds with no bytes. Web readability does not establish that our local downloader received the PDF. Nor do these failures establish that the entire NSE archive is inaccessible.

Earlier issuer tests also have different failure modes: TCS returned a verified-TLS HTTP 403 Akamai denial; HCLTech completed TLS but failed or stalled during HTTP delivery. A Python certificate-chain issue was separately resolved and did not resolve the TCS denial. The precise edge/network cause remains unproven. These failures occur before PDF extraction.

## Implementations inspected

Public repositories were cloned for source inspection only. Their packages were not installed or executed; authenticated services were not called.

### Tapetide

Revision `30001bcdb3764d51ce14547cb23f07e7da505db3`.

The public [src/index.ts](https://github.com/Tapetide-hq/nse-bse-indian-stock-market-data-mcp/blob/30001bcdb3764d51ce14547cb23f07e7da505db3/src/index.ts) bridges local stdio JSON-RPC to Tapetide's hosted MCP endpoint. It exchanges a configured token for access and forwards requests. The public package does not expose the backend's upstream data-collection pipeline. Advertised coverage therefore is not evidence of a reusable public exchange downloader.

### bshada/nse-bse-mcp

Revision `d2dc31d0597c2be9416a8301a0500e9a21658fa3`.

The [NSE handler](https://github.com/bshada/nse-bse-mcp/blob/d2dc31d0597c2be9416a8301a0500e9a21658fa3/src/handlers/nse-handler.ts) delegates announcements and annual-report discovery to `nse-bse-api`. The [document handler](https://github.com/bshada/nse-bse-mcp/blob/d2dc31d0597c2be9416a8301a0500e9a21658fa3/src/handlers/document-handler.ts) separately downloads URLs using Node HTTP/HTTPS, handles selected redirects, caches files and extracts PDF text. This downloader does not automatically inherit the discovery client's exchange session. It can still encounter delivery failures.

We also inspected the underlying library at revision `95d0ef2022e1cd7d65480adaf7ba369c31a78607`. Its [HTTP client](https://github.com/bshada/nse-bse-api/blob/95d0ef2022e1cd7d65480adaf7ba369c31a78607/src/nse/http/http-client.ts) uses a cookie jar, visits the NSE homepage before requests, and supports Axios or Got HTTP/2. Its own downloader shares that session. This library revision is a separate reference, not proof of the exact dependency version executed by the MCP: the inspected manifest and lockfile also differ in their version references.

### manitgupta/NSE-MCP

Revision `8fe76bc51fc2beb5013eb252592b285be8e1b5c0`.

The [session module](https://github.com/manitgupta/NSE-MCP/blob/8fe76bc51fc2beb5013eb252592b285be8e1b5c0/src/nse/session.ts) visits NSE pages and retains cookies. Fetch code adds caching, request spacing and session refresh. The [announcement tool](https://github.com/manitgupta/NSE-MCP/blob/8fe76bc51fc2beb5013eb252592b285be8e1b5c0/src/tools/announcements.ts) retrieves announcement metadata and constructs attachment links. Returning a PDF link does not establish successful file acquisition or extraction.

## Proposed experiment at the time of inspection

Keep Python and our existing archive. MCP is the interface layer; changing languages will not resolve source-specific HTTP failures.

1. Add a bounded discovery experiment for one company and one reporting period, using observed NSE/BSE announcement responses. Preserve raw metadata, publication time, attachment URL and discovery source. Do not guess attachment paths.
2. Test discovered exchange attachments and issuer alternatives independently. Respect denials and rate limits; keep TLS verification, request budgets and diagnostics. Ordinary session support is a hypothesis to test, not a promise of access.
3. Import successfully validated PDFs using the existing hash/provenance pipeline. Classify related disclosures separately from alternate locations of the same document.
4. Build the first real extraction recipe against the already acquired Wipro PDF, manually verify its cells, and keep candidates unpublished until reviewed.

Subsequent [BSE work](bse-acquisition-results.md) completed manual discovery, validated downloads and private imports for four attachments. Automatic discovery, a general NSE/BSE adapter, an automatic fallback resolver and real extraction validation remain pending. Reference projects' code licenses do not establish rights to redistribute their underlying data; public hosted use needs separate assessment.
