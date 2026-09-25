# Corpus discovery, acquisition and extraction trial

Observed 25 September 2026 on the local macOS/Python 3.12 environment. This is a development study, not a held-out financial accuracy benchmark. Current delivered behavior is maintained in [implementation status](../implementation.md); commands are in the [acquisition](../acquisition-development.md) and [ingestion](../ingestion-development.md) guides.

## Results

- Seven distinct official-source PDFs are imported privately: the previous five quarterly documents plus Infosys FY25 annual report and Q2 FY26 transcripts. Seven catalog entries reproduce their reviewed bytes; no PDFs or databases are committed.
- Four hash-bound recipes extracted **36 selected cells**, all matching visually transcribed development expectations: three metrics, three periods, four companies. All candidates remain `needs_review`; no independent reviewer, accepted-fact store or MCP fact publication exists.
- Full-document text checks found text on **674 of 705 pages**. The Infosys results package has 31 pages without a text layer; sampled pages 7 and 159 contain scanned auditor material. This is a readability inventory, not a measure of completeness or text accuracy.
- MCP now exposes discovery guidance through a tool, resource and prompt. A separate offline HTML-link parser emits unverified candidates. Neither searches the internet, downloads a filing nor changes the corpus through MCP.

## New source routes tested

Reference-project inspection suggested using aggregators as discovery indexes and examining their original document links. No reference project's package was executed, and no login/session credentials were used. Pinned code references and their source strategies are in [existing MCP ingestion](existing-mcp-ingestion.md#follow-up-25-september-2026).

| Route tested | Observation | Corpus decision |
| --- | --- | --- |
| Screener Infosys consolidated page | HTTP 200; offline parser found 66 unique PDF/viewer URL candidates after removing fragments | Useful discovery leads. Select original exchange links, then verify document identity. Not a complete or licensed financial feed |
| Tijori Infosys company page | HTTP 200; 181 unique PDF/viewer URL candidates | Useful secondary discovery and mirror leads for this company; no general authenticated integration tested |
| Yahoo Infosys financials web page | HTTP 429; no retries | Not usable through this tested route. This was not a test of the yfinance library, its session handling or all Yahoo endpoints |
| Infosys issuer earnings-call PDF | HTTP 403 with verified TLS | Direct issuer route still blocked here |
| BSE annual-report attachment discovered on Screener | HTTP 200; 370 pages; 7,591,441 bytes; repeat hash matched | Added `infosys-fy25-annual` to catalog and archive |
| BSE transcript viewer discovered on Screener | HTTP 302 explicitly naming an HTTPS `AttachHis` destination | Inspected the returned destination, then downloaded it separately; did not guess a path or enable automatic redirects |
| BSE transcript attachment | HTTP 200; 38 pages; 611,615 bytes; repeat hash matched | Added `infosys-q2-fy26-transcripts` to catalog and archive |
| Tijori annual report and transcript PDFs | Both HTTP 200 and byte-identical to the corresponding BSE attachments | Verified alternate locations, not two extra documents or independent factual corroboration; retained probe receipts, kept primary BSE URLs in catalog |

Discovery pages: [Screener Infosys](https://www.screener.in/company/INFY/consolidated/), [Tijori Infosys](https://www.tijorifinance.com/company/infosys-limited/), [Yahoo financials](https://finance.yahoo.com/quote/INFY.NS/financials/), [Infosys results hub](https://www.infosys.com/investors/reports-filings/quarterly-results/2025-2026/q2.html).

Verified additions:

| Document | Primary URL and SHA-256 | Identity check |
| --- | --- | --- |
| Infosys FY25 annual report | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/4527f4d2-dac4-4528-a1dc-5070fd9e140d.pdf); `6224d11244d3f44f7e95901428a8ff23164f383cd1960e02a47483c48612a3c5` | Cover dated 2 June 2025; FY2024-25 integrated report, BRSR and AGM notice |
| Infosys Q2 FY26 transcripts | [BSE PDF](https://www.bseindia.com/xml-data/corpfiling/AttachHis/cf4a6179-8e43-4959-b055-91f1f7f4f076.pdf); `5f8c7daa665148a4eb40556bb74bf312655fca5d5b99d841a1f9317a8f09d6b3` | Cover filed 21 October 2025, calls held 16 October; press conference starts physical page 2, earnings call page 17 |

Tested mirror URLs: [Tijori annual report](https://files.tijorifinance.com/insight/india/149/Annual%20Report/AR-25.pdf), [Tijori transcript package](https://files.tijorifinance.com/insight/india/149/Conference%20Call/CC-Sep25.pdf). The latter's filename says September although the calls occurred in October: infer neither event date nor publication date from a filename. Hosted reuse/redistribution remains unresolved; technical success is not a license.

## Tijori access inventory

Follow-up on 25 September 2026: re-opened the public [Infosys company page](https://www.tijorifinance.com/company/infosys-limited/) through web research and classified the previously saved local candidate JSON. This follow-up did not acquire additional PDFs, execute the reference MCP, log in or test an authenticated API. The web-rendered page and the saved HTTP response are separate observations; do not assume identical snapshots.

The local saved page's SHA-256 is `b23f6abe532b0447efaeb7113f1b3c11f74708af9c2fab68e9e747e8d497ae42`. Grouping the 181 fragment-deduplicated candidate URLs by percent-decoded path category produced:

| URL path category | Candidate URLs | What was actually acquired in the original trial |
| --- | ---: | --- |
| Annual Report | 17 | One FY25 report, byte-identical to its BSE attachment |
| Earnings Release | 64 | None through Tijori |
| Investor Presentation | 20 | None through Tijori |
| Conference Call | 68 | One Q2 FY26 transcript package, byte-identical to its BSE attachment |
| Other Report | 3 | None through Tijori |
| Other paths | 9 | Not classified as document families; includes source-linked files and methodology material |
| Total | 181 | Two checked mirror files; not additional distinct corpus documents |

These are URL classifications, not content-verified document counts or coverage within our proposed two-year window. One conference-call URL occurs with both a literal space and its encoded form: percent-decoding paths for a diagnostic comparison reduces the total to 180 URL keys (67 conference-call paths). The implemented parser only deduplicates fragments; it does not perform this additional normalization. Neither count deduplicates bytes or confirms unique disclosures. Retain original URLs and use content hashes after acquisition.

The public page recheck showed annual reports, earnings releases, presentations and conference-call links, plus financial/research surfaces: ratios, financial statements, revenue mix, operating metrics, peer comparisons, corporate actions and shareholding navigation. Some historical views displayed premium-access messages. Source links beside operating metrics can help locate evidence pages, but their numeric correctness and full histories were not imported or verified. The page also contains generated summaries/reports and third-party discussion links; these must not be classified as original company disclosures merely because they occur on the same page. No stable public bulk API, full free history or entitlement to all these views was established.

Observed endpoint families are the HTML discovery page `/company/infosys-limited/` and the file host `files.tijorifinance.com`. Saved links include `/insight/india/149/<category>/<filename>.pdf` and other paths such as `/india/company/149/...`. These are observed file locations, not an API contract: do not guess IDs, construct unobserved files or infer dates solely from names. The tested `CC-Sep25.pdf` contains October calls.

Practical use for Margin: prioritize primary exchange/issuer attachments found through these indexes; retain Tijori as a secondary discovery/mirror route; validate every selected file with the same acquisition and evidence pipeline. Broader platform figures, premium views, generated analysis and authenticated features remain separate evaluations. Public page access and two successful mirrors do not establish bulk access, all-company coverage or hosted reuse rights. See the [pinned reference-project inspection](existing-mcp-ingestion.md#follow-up-25-september-2026).

## What the experiment yielded and changed

- Alternative hosting resolved acquisition for selected documents even though several issuer routes still failed. A failed host route is not evidence that the disclosure does not exist.
- Aggregator indexes supplied useful original-document leads. Discovery, successful acquisition and accepted financial evidence are separate coverage measures.
- Byte hashes established two alternate copies of existing documents; counting mirrors would exaggerate corpus size. URL encoding also creates duplicate-looking candidates before byte comparison.
- The 36-cell trial supports deterministic extraction on selected layouts with explicit context. It does not establish whole-document extraction, unseen-layout performance or independent financial accuracy.
- Scan detection, conflicting financial labels, mixed accounting sections and filename/event-date differences identify concrete validation requirements for corpus expansion.
- The next useful milestone is metadata/archive linkage and independently reviewed, cited facts through MCP. Optional corpus growth should follow the [release scope](../plan.md#proposed-corpus-composition), not displace that milestone.

## Download failures rechecked

Six default-protocol probes were made with verified TLS, no redirects/retries, 8-second connection and 18-second transfer deadlines. TCS issuer annual report and Infosys issuer results still returned 403. HCLTech issuer and the related NSE Wipro attachment still failed with curl HTTP/2 error 92 and zero bytes. A single HTTP/1.1 test on each returned zero-byte timeouts after 15 seconds. The BSE TCS and issuer Wipro control downloads succeeded with the original hashes. An initial sandbox DNS failure was an environment limitation, not a source failure; the recorded external checks used approved network access.

Consequences: changing HTTP version did not fix the two tested transport failures. Alternative official hosts work for selected documents. An ordinary browser-saved original remains a possible local import path, but no new browser-download success is claimed here. Do not repeatedly retry 403/429, disable TLS, treat an HTML viewer as a PDF, or replace an annual report with quarterly results. See [earlier URL-specific diagnostics](acquisition-troubleshooting.md).

## Financial extraction study

Selected consolidated Ind AS tables:

| Company | Physical PDF page | Source scale | Cells matched / selected |
| --- | ---: | --- | ---: |
| Wipro | 11 | INR million | 9 / 9 |
| TCS | 8; accounting-standard note on 11 | INR crore | 9 / 9 |
| HCLTech | 2 | INR crore | 9 / 9 |
| Infosys | 162; accounting-standard note on 167 | INR crore | 9 / 9 |

Each recipe selects revenue from operations, profit before tax and **total profit for the period**, for July–September 2025, July–September 2024 and April–September 2025. These are comparative columns from four documents, not twelve independently acquired filings. All share the filing's publication date; comparative values are not established as known at their original period end.

Illustrative extracted July–September 2025 values, normalized to INR crore for this table:

| Company | Revenue | Profit before tax | Total profit for period |
| --- | ---: | ---: | ---: |
| Wipro | 22,697.3 | 4,282.4 | 3,262.4 |
| TCS | 65,799 | 16,068 | 12,131 |
| HCLTech | 31,942 | 5,702 | 4,236 |
| Infosys | 44,490 | 10,229 | 7,375 |

These are development candidates, not published accepted facts. Original scales/values, physical pages, bounding boxes and anchors are preserved in the run. Recipes and transcribed expectations are in [examples/real-extraction](../../examples/real-extraction/study.json); the [runner](../../examples/evaluate_real_corpus.py) reports missing documents, extraction errors, context mismatches and value mismatches with a failing exit status.

Method: render the tables, select rows/columns and context regions, transcribe expected values, run existing extraction, compare exact decimals and normalized INR values, and replay the recipes. The same operator prepared recipes and checked their outputs. This establishes feasibility on chosen cells, not independent semantic verification, recall across the PDFs or performance on unseen layouts. Negative software tests ensure the evaluator rejects incorrect value, scale, period, basis, missing input and extraction errors.

Observed pitfalls:

- All four statements separate total profit from profit attributable to owners; do not label either with an ambiguous `net_profit` field.
- TCS has both profit before exceptional items and tax, and profit before tax after exceptional items. This recipe selects the latter.
- Wipro's text layer reads parts of labels incorrectly, including `0rofit`, while selected numbers are readable. Preserve the raw anchor rather than silently rewriting evidence.
- Infosys contains Ind AS/IFRS and INR/USD sections plus scanned pages. The recipe deliberately selects the consolidated Ind AS INR section, not the early IFRS press-release table.
- A whole group header is retained where duration labels span multiple columns. Cell-to-column semantics are operator-mapped; anchor matching alone cannot verify that mapping.

## How much of the intended corpus is usable?

| Data family | Present in current documents? | Program status |
| --- | --- | --- |
| Revenue, PBT, total profit | All four companies | 36 mapped candidates extracted and checked; independent review pending |
| Owners' profit, EPS, expenses and other income | Visible in selected results tables | Not supported by current metric contract/recipes |
| Balance sheets and cash flows | Present in results packages | Inspection works on text pages; no typed extraction contracts for instant balances/cash-flow periods yet |
| Segment/operating metrics and guidance | Present in selected packages/presentations | Text inspection; no normalized metric or guidance extraction |
| Annual-report narrative, policies and risks | One FY25 Infosys report now acquired | Page inspection available; no passage-search index or answer verification |
| Earnings-call commentary/Q&A | One Infosys package now acquired | Text available across 38 pages; no speaker-aware passage search or claim verifier |
| Dedicated shareholding histories, prices, macro, consensus | Not collected for these features | No adapters or coverage claims |

Full text inventory: Wipro results 33/33 pages, Wipro release 17/17, TCS 22/22, HCLTech 27/27, Infosys results 167/198, Infosys annual report 370/370, Infosys transcripts 38/38. A page with some text may still contain unreadable tables/images, so these counts overstate neither financial extraction nor OCR coverage. OCR is not installed/integrated in this prototype.

## Storage and next gate

The current archive stores immutable original PDF blobs by hash, separate provenance registrations, and recipe/parser-bound extraction runs. Discovery candidate JSON and acquisition diagnostics stay private outside that archive. This study contains seven blobs, seven registrations and four real extraction runs. Page text is inspected on demand; there is no persisted full-text index yet.

Next: persist source candidates/statuses and observed redirects in a source registry; link real metadata and archive IDs without inventing publication times; independently review the 36 cells; add accepted-fact/evidence publication. Then add OCR for scanned sections, typed balance-sheet/cash-flow metrics, passage retrieval and a second independent results filing per company. Keep acquisition separate from read-only MCP queries.

Local evidence: `data/private/source-probes-20260925/` contains transfer receipts, saved discovery pages, parsed candidates and mirror copies. `data/private/corpus-trial-20260925/` contains renders, evaluation JSON and page-text coverage. The two new repeat downloads and import receipts are under `data/private/infosys-fy25-annual-repeat/` and `data/private/infosys-q2-fy26-transcripts-repeat/`. These paths are absent from a fresh clone.
