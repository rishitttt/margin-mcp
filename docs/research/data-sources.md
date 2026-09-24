# Indian financial-data feasibility and product options

Research date: **23 September 2026**. Scope: listed-company disclosures and fundamentals, with adjacent prices and macroeconomic context. This is a broad source landscape, not an exhaustive procurement audit. Recommendations below are engineering judgments; permissions marked unresolved require a source-specific agreement or clarification.

Follow-up, 24 September 2026: a small private corpus now exists. See [recorded BSE downloads](bse-acquisition-results.md) and [current acquisition instructions](../acquisition-development.md). Provider prices, terms and external API descriptions below remain dated research observations and should be rechecked before choosing a service.

## Original recommendation

Develop a model-independent research service around a small, versioned corpus of Indian disclosures. Support customer-supplied documents and licensed provider adapters through the same data model. Begin with local operation and scheduled ingestion. Preserve the option to host the data later, with each source's entitlements enforced at serving time.

The confirmed constraint is a **free prototype in 6–8 weeks**. First investigate a permitted small document corpus and academic access through the professor. Treat commercial trials as optional future evaluation, not a prerequisite for the prototype. Existing Refinitiv Eikon access is not assumed usable. Keep the Indian scope even if acquisition is difficult.

## Source landscape

“Documented” below means public documentation was located, not that authenticated access or contractual rights were tested.

| Source family | Useful content and access | Storage / hosted use | Proposed role |
| --- | --- | --- | --- |
| NSE public disclosures | Results, announcements, ownership, annual reports; website downloads and XBRL information | Website terms restrict collection and reuse; not a general-purpose free ingestion API | Discovery and manual verification; approved acquisition route needed |
| NSE RSS | Published feed categories include announcements, results, integrated financial filings, and ownership | Reader subscription is documented; archival, downstream attachments, and product redistribution require clarification | Potential incremental discovery |
| NSE paid corporate data | Dedicated-line corporate feed; EOD announcements over SFTP | Agreement determines retention, end users, and redistribution | Direct exchange route at larger scale |
| NSE academic research access | Research-oriented datasets under an institutional process | Research conditions do not establish commercial-product rights | Investigate immediately with professor |
| BSE public disclosures / paid data | Results, ownership, announcements; paid corporate products and delivery portal | Public website access is not a redistribution license; paid terms need review | Alternative or complementary exchange coverage |
| Company investor relations | Original results PDFs, annual reports, presentations, call transcripts | Company-specific terms; public availability alone does not clear a shared corpus | Small document corpus where rights are established |
| MCA on data.gov.in | CIN, legal name, company status, incorporation and capital metadata | Published OGD license is promising; verify actual resource, exclusions and attribution | Entity enrichment, not listed-company financial statements |
| RBI DBIE | Rates, monetary, banking, external-sector and other macro series | Dataset-specific use and automated access need verification | Later contextual series |
| MoSPI eSankhyiki | Official economic statistics, downloads, documented API ecosystem and MCP | Check dataset terms and vintage; do not infer rights from a software license | Optional companion MCP or later macro adapter |
| Global Datafeeds | Documented corporate REST/WS APIs: results, ownership, announcements, attachments, annual reports | API subscription alone does not prove archival or multi-user rights | High-priority commercial trial |
| TrueData | Advertises corporate/fundamental and announcement APIs | Obtain current schema, quote, retention and redistribution terms | High-priority commercial comparison |
| Accord Fintech / ACE | Financial information services through FTP and API | Negotiated commercial terms | Enterprise alternative |
| CMIE Prowess / Capitaline | Established Indian corporate databases; possible institutional access | Academic export and external-product rights must be distinguished | Reference data, benchmark, or licensed adapter |
| Upstox fundamentals | Documented ISIN-based financial statements, ownership, ratios and corporate actions | Authentication, entitlement, caching, third-party model use and redistribution need confirmation | Promising user-authorized adapter |
| Quartr | Original investor-relations material through API and MCP | Product integrations are directed to Public API; Indian subset and rights need validation | Documents/calls supplier and product benchmark |
| Screener / Trendlyne / Tijori | Research interfaces and document discovery; Trendlyne also has MCP | Do not treat consumer access as a data resale license | Product comparison; partnership only if authorized |
| EODHD / Financial Modeling Prep | Documented global financial APIs | Indian symbol/statement coverage, original citations, and commercial rights untested | Secondary candidates, not selected |
| Broker price APIs | Quotes, candles, instruments and user portfolios depending on provider | Often user-scoped; public data display can be restricted | Separate later market-data adapter |
| User-supplied files | Customer's permitted PDFs, CSVs, XBRL or exports | Must remain within that customer's rights and permitted model-processing scope | Useful local/private mode |
| SEC EDGAR | Documented US filing infrastructure | Separate SEC access policies; unsuitable as a substitute for Indian filings | Optional later adapter or technical comparison |

For the secondary SEC option, the official documentation describes submissions and XBRL JSON APIs and bulk archives. Any future adapter should follow the linked access policies and preserve accounting-basis differences. [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).

## Exchange access findings

NSE's terms explicitly prohibit systematic automated collection and impose broad content-use restrictions. Its data policy also makes redistribution agreement-dependent. Therefore an undocumented website JSON endpoint is not a dependable product foundation merely because a wrapper can reach it. [NSE terms](https://www.nseindia.com/static/nse-terms-of-use), [data policy](https://www.nseindia.com/static/market-data/nse-data-policy).

NSE separately advertises RSS subscriptions for corporate updates. This is a documented discovery mechanism worth evaluating under its applicable conditions. Feed history, missed-event recovery, attachment access and hosted redistribution remain unverified. A feed is not necessarily a complete archive. [NSE RSS](https://www.nseindia.com/static/rss-feed).

The paid corporate-data page lists an EOD SFTP product, available after 8 p.m. IST, at **₹5,00,000 per annum** domestically. It also lists **₹10,60,000** for corporate data via a customer-owned dedicated line; confirm that product's billing period, connectivity charges, taxes, fields and rights in a quote. The page is marked updated 11 June 2026. [NSE corporate products](https://www.nseindia.com/static/market-data/corporate-data-subscription).

BSE's search-indexed domestic tariff lists annual EOD announcements at **₹5,00,000**, EOD results and ownership at **₹3,00,000 each**, and a three-product open-website/mobile redistribution line at **₹12,00,000**; taxes are excluded. These are budget signals, not current offers: direct retrieval of the tariff returned HTTP 403 in this investigation. Whether an MCP/API product fits that license is unresolved. [BSE tariff](https://www.bseindia.com/downloads1/Information_Products_Pricing_Sheet.pdf), [delivery portal](https://marketdata.bseindia.com/).

NSE's disclaimer describes research-oriented access without cost up to a stated aggregate **2 GB** threshold, subject to eligibility and NSE conditions, potentially including institutional documentation and reporting. It excludes commercial uses from that research route. Ask the professor to investigate eligible datasets and the precise process; do not interpret this as blanket free access to the whole exchange corpus. [NSE research conditions](https://www.nseindia.com/static/nse-disclaimer), [research initiatives](https://www.nseindia.com/static/research/research-initiatives).

NSE documents XBRL taxonomies and, in April 2025, introduced an Integrated Filing–Financial utility. Parser design must allow different filing generations and sector taxonomies. The availability of submission utilities does not prove public bulk retrieval of instance files. [XBRL information](https://www.nseindia.com/static/companies-listing/xbrl-information), [April 2025 circular](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Circular_02042025_0.pdf).

SEBI's filing directory helps map official categories to NSE/BSE pages. It is a directory, not a unified financial-facts API. [SEBI directory](https://www.sebi.gov.in/curation/corporate_filings.html).

## Issuer documents and government sources

Issuer websites are useful for exact provenance, but their permissions differ. Infosys' terms restrict copying, redistribution and mirroring. TCS permits personal non-commercial viewing/downloads subject to conditions and restricts public/commercial use. Neither establishes a general license for Margin's shared commercial corpus. Resolve document-specific permission or use an appropriately licensed supplier. [Infosys terms](https://www.infosys.com/terms-of-use.html), [TCS disclaimer](https://www.tcs.com/who-we-are/legal/legal-disclaimer).

The MCA catalog lists company-master fields and an update date of 22 July 2026. However, the page retrieved here also displayed “No Result Found” and a sandbox notice. Treat resource availability and record freshness as **unverified**, rather than turning that catalog date into a claim of current company data. Confirm a downloadable resource and its actual snapshot date. [MCA catalog](https://www.data.gov.in/catalog/company-master-data).

The OGD platform identifies its content as licensed under Government Open Data License–India. That license supports commercial and non-commercial reuse with conditions including attribution, subject to exclusions. Apply it to the relevant covered resource; do not extend it to exchange or private-company websites. [OGD policies](https://www.data.gov.in/policies), [license](https://ap.data.gov.in/godl).

RBI reports that DBIE moved to **data.rbi.org.in**. The old URL in the brief should be treated as legacy. Public series availability is established, but a production public API contract, automated quotas and redistribution terms were not verified. [RBI annual report](https://rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1440), [current DBIE](https://data.rbi.org.in/).

MoSPI publishes eSankhyiki downloads and an official MCP page; its NSO repository documents a Python API client. A companion MCP may let users obtain macro context without Margin maintaining a second statistical platform. The official MCP page was visible in search but timed out on direct retrieval; no connection test was performed. [eSankhyiki](https://esankhyiki.mospi.gov.in/), [official MCP](https://datainnovation.mospi.gov.in/mospi-mcp), [NSO client](https://github.com/nso-india/mospi-esankhyiki).

## Providers worth testing

**Global Datafeeds:** the public API catalog is unusually concrete. However, its history table lists 30 days for several corporate endpoints. Confirm whether this means query lookback, event retention, or underlying historical coverage, and how older statements can be backfilled. Ask for original document links and revised-filings examples. No authenticated response was tested. [API list](https://docs.globaldatafeeds.in/list-of-apis-923685m0), [coverage table](https://docs.globaldatafeeds.in/type-of-corporate-data-available-1142925m0).

**TrueData:** the provider advertises separate fundamental and announcement APIs. Request sample payloads and an explicit multi-user AI/MCP license; exchange authorization by itself does not describe the rights granted to a particular customer. [TrueData](https://www.truedata.in/).

**Upstox:** its 11 May 2026 announcement documents company profiles, income statements, balance sheets, cash flows, ownership, ratios, actions and peers using ISINs. Statements support standalone/consolidated options. Evaluate original-document provenance and as-reported history before accepting it as evidence-grade. No account, price or redistribution entitlement was validated. [Launch documentation](https://upstox.com/developer/api-documentation/announcements/company-fundamentals-api/), [authenticated profile example](https://upstox.com/developer/api-documentation/get-company-profile/).

**Accord, CMIE and Capitaline:** these are credible commercial/institutional routes to investigate. Accord advertises FTP/API delivery; CMIE and Capitaline describe broad corporate databases. Existing library access could help the academic benchmark, but it does not establish hosting rights. API availability for the team's exact CMIE/Capitaline entitlement remains unknown. [Accord](https://www.accordfintech.com/website), [CMIE ProwessIQ](https://prowessiq.cmie.com/kommon/bin/sr.php?kall=wclrdhtm&nvdt=20190909165709660&nvpc=075000000000&nvtype=TOPICAL+QUERY), [Capitaline](https://www.capitaline.com/).

**Global APIs:** EODHD and FMP document fundamentals APIs. Their existence does not establish the quality or completeness of the required Indian subset. Trial them against exactly the same company/period/citation benchmark before choosing one. [EODHD](https://eodhd.com/financial-apis/stock-etfs-fundamental-data-feeds), [FMP](https://site.financialmodelingprep.com/developer/docs/stable/latest-financial-statements).

**Consumer and broker tools:** Screener's published license is limited to personal non-commercial transitory viewing and restricts copying/public use. Kite's terms restrict public display of live market data. These illustrate why a cheap subscription or accessible library cannot automatically supply a hosted research service. Tijori partnership/API terms were not established in this pass. [Screener terms](https://www.screener.in/guides/terms/), [Kite terms](https://kite.trade/terms/).

## Existing products and differentiation

| Product | Verified public positioning | Consequence for Margin |
| --- | --- | --- |
| [Quartr MCP](https://quartr.com/mcp) | First-party investor-relations material in AI workflows | Evidence-backed financial MCP is an existing category |
| [Quartr developer documentation](https://mcp.quartr.com/docs) | Individual research MCP; product builders directed to Public API | Use the correct commercial integration route; confirm Indian-company coverage |
| [Trendlyne MCP](https://help.trendlyne.com/support/solutions/folders/84000350327) | Financial-data tools and separate MCP subscriptions | Indian data delivered through MCP is already available |
| [Tapetide repository](https://github.com/Tapetide-hq/nse-bse-indian-stock-market-data-mcp) | Advertises broad NSE/BSE research tools; public package bridges to a remote service | Inspect as a workflow benchmark; advertised coverage/accuracy not independently tested |
| [MoSPI MCP](https://datainnovation.mospi.gov.in/mospi-mcp) | Official statistics through MCP | Consider composing with it for macro context |

Margin's proposed contribution is transparent evidence lineage, understandable financial semantics, revision-aware comparisons, a reproducible Indian benchmark, and deployment with customer-owned or licensed data. These are hypotheses to demonstrate, not claims that competing products lack those features.

## Decision order

1. Investigate the NSE academic route and permission for a small issuer-document corpus; do not depend on the team's Eikon access.
2. For a later paid phase, compare sample/rights information from Global Datafeeds, TrueData and Upstox; include Accord or an institutional provider if available. No purchase is needed for the prototype plan.
3. Score candidates by permitted use, original citations, historical depth, correction history, coverage, reliability and total price, in that order.
4. Establish one usable corpus before generalizing ingestion.
5. Keep source adapters replaceable so a changed license or unreliable feed does not require rewriting the MCP layer.

No purchases, signups, provider messages or external publication were performed during this research.
