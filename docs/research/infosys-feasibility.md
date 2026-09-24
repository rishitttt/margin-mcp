# Feasibility investigation: Infosys quarterly results

Investigated 23 September 2026. This is a **discovery and extraction-design check**, not a validated ingestion adapter or cleared dataset. The period was deliberately fixed for reproducibility; it is not represented as the latest quarter.

Follow-up, 24 September 2026: a different, 198-page Infosys board/financial package was subsequently acquired from BSE and imported privately; see [BSE results](bse-acquisition-results.md). The 21-page issuer PDF and its candidate page references below remain a historical investigation, not validated labels for that BSE package.

## Company-to-document path

1. The issuer's [share-details page](https://www.infosys.com/investors/shares/share-details.html) identifies the NSE symbol as `INFY`.
2. Its [Q2 FY2025–26 results page](https://www.infosys.com/investors/reports-filings/quarterly-results/2025-2026/q2.html) lists a 16 October 2025 announcement and distinguishes Ind AS materials from IFRS releases.
3. Follow “Standalone and consolidated results and Regulation 33 auditors reports” to the [official 21-page PDF](https://www.infosys.com/investors/reports-filings/quarterly-results/2025-2026/q2/documents/q2-and-h1-fy26-financial-results-auditorsreports.pdf).
4. The web extraction locates the consolidated results table at zero-based page 12, corresponding to **PDF page 13**. It identifies audited Ind AS results, the period ended 30 September 2025, INR crore for monetary totals, and separate per-share units.

Source-location numbering here is the PDF's physical page sequence, not an assumed printed page label. Confirm it visually during corpus validation.

## Small candidate reference set

The following values were observed in that table's extracted text. They are candidates for manual benchmark labeling, not parser-verified production records.

| Metric | Quarter ended 30 Sep 2025 | Quarter ended 30 Sep 2024 | Unit |
| --- | ---: | ---: | --- |
| Revenue from operations | 44,490 | 40,986 | INR crore |
| Profit for the period | 7,375 | 6,516 | INR crore |
| Profit attributable to owners | 7,364 | 6,506 | INR crore |

These distinct profit rows show why an unqualified `net_profit` mapping can be wrong. The same table contains quarterly, half-year and annual columns; a parser must bind each cell to the correct header. [Source PDF](https://www.infosys.com/investors/reports-filings/quarterly-results/2025-2026/q2/documents/q2-and-h1-fy26-financial-results-auditorsreports.pdf).

For the revenue values, a separate Python Decimal calculation gives:

```text
Absolute change = 44,490 - 40,986 = 3,504 crore
YoY growth = (44,490 / 40,986 - 1) × 100 = 8.5492607...%
Display: 8.55%, derived from the two reported inputs.
```

The older value is a comparative inside this later document. It does not establish what an original 2024 filing said or whether a restatement occurred. An as-of-2024 answer would need the earlier publication.

## Access and evidence log

| Check | Observed result | What it proves |
| --- | --- | --- |
| Issuer identity page | Readable through web research | A source-backed symbol association |
| Results landing page | Readable; PDF link followed | A traceable discovery path |
| PDF text | Web tool returned page-associated extraction | Candidate numbers and reporting context are discoverable |
| PDF screenshot | Screenshot references returned, but no inspectable image reached this session | Visual verification remains incomplete |
| Direct local download | Initial sandbox DNS failure; permitted external attempt then returned HTTP 403 | This environment did not establish a repeatable download path |
| Parser execution | Not performed | No extraction accuracy or performance claim yet |
| Storage / redistribution | Reviewed issuer terms; product permission not established | No cleared shared corpus created |

The 403 is an observation about this request and environment, not proof that all issuer access is impossible. No workaround, authenticated access, bulk download or anti-bot bypass was attempted.

## Original next experiment (23 September)

Obtain a permitted local copy or an authorized delivery method. Record collection time, content hash and rights scope. Visually inspect the table, label the selected cells with two reviewers, and implement extraction for one fact with exact evidence. Then repeat on a second quarter and a different issuer before generalizing the parser.

Use the [issuer terms](https://www.infosys.com/terms-of-use.html) and any document-specific permission to determine whether storage, extraction and transmission to the selected host/model are allowed. The discovery path above should not be described as an established permitted commercial-ingestion route.
