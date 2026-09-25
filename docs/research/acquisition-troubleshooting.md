# Successful real-document acquisition

Follow-up, 25 September 2026: [corpus trial](corpus-trial.md) records new aggregator-discovered BSE documents, fresh failure checks and real extraction results.

Update, 24 September 2026: [BSE acquisition now works for TCS, Infosys, HCLTech and Wipro](bse-acquisition-results.md). The issuer/NSE failures below remain route-specific. The original Wipro command now shares the reusable, hash-pinned acquisition implementation.

Historical experiment, verified 23 September 2026. Wipro's original Q2 FY26 Regulation 33 results PDF was downloaded twice, imported into the private archive, and visually inspected. TCS and HCLTech issuer routes were unsuccessful in this experiment. This resolves the immediate real-document acquisition blocker without claiming all sources work.

## Diagnosis

| Source | Measured behavior | Conclusion |
| --- | --- | --- |
| TCS | Verified TLS; HTTP/2 403 from `AkamaiGHost` in about 0.15 seconds; 515-byte Access Denied HTML body | Server/edge rejection, not a slow PDF or parsing failure. Exact client/network/region rule is unknown. |
| HCLTech, HTTP/2 | TCP/TLS succeeds in about 0.12 seconds, then stream `INTERNAL_ERROR`, no body | Failure occurs after connection; the failing origin/CDN/network component cannot be conclusively identified. |
| HCLTech, HTTP/1.1 | TLS succeeds; zero response bytes before a 15-second deadline | Switching protocol did not fix delivery. Earlier 30/60-second Python requests also timed out. |
| Wipro | Two HTTP 200 transfers, 3,375,941 bytes each; about 1.49 and 0.56 seconds | Ordinary system curl works, with identical document hashes across both requests. |

Earlier default Python SSL requests lacked a usable certificate chain. The system trust-store context resolved that separate issue; it did not resolve the denied/stalled sources. No certificate validation was disabled.

The normal in-app browser loaded TCS's financial-results page, but the PDF showed a blank viewer and yielded no verified document artifact. That browser observation is not proof of successful PDF acquisition.

The practical approach is source-specific diagnostics and verified acquisition routes. Do not save an HTML denial as a PDF, repeatedly retry 403, or assume longer timeouts solve delivery. Browser impersonation, cookies, credentials, alternate proxies and anti-bot bypass were not used.

## Reproduce

System curl and the installed project are required. Choose a new output directory:

```sh
.venv/bin/python examples/acquire_wipro.py --output data/private/wipro-q2-fy26-acquisition
.venv/bin/margin import-document data/private/wipro-q2-fy26-acquisition/results.pdf \
  --manifest data/private/wipro-q2-fy26-acquisition/document.json \
  --archive data/private/real-archive
```

The current compatibility command uses the shared downloader and reviewed catalog described in [the acquisition guide](../acquisition-development.md). It makes one HTTPS request with verified TLS, a 10-second connect timeout, 30-second transfer deadline, 35-second process deadline and 25 MiB limit. It requires HTTP 200, valid PDF bytes/pages and the catalog SHA-256. It writes the original, an acquisition receipt and importer manifest only after validation, and refuses an existing output directory. It does not follow redirects, retry access denials or crawl links; review a changed source before updating the catalog.

Source links:

- [Official filing directory](https://www.wipro.com/investors/corporate-governance/stock-exchange-filings/)
- [Original Regulation 33 PDF](https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/2025-2026/q2fy26/regulation-33-financial-results-q2fy26.pdf)
- [Dated results announcement](https://www.wipro.com/newsroom/press-releases/2025/wipro-announces-results-for-the-quarter-ended-september-30-2025/)

## Evidence retained locally

```text
Bytes: 3375941
Physical pages: 33
SHA-256: fbd030c17809cef911cf55e71af0e383d1bf56990a6b216c2c8cf122e52f6dde
Verified PDF: data/private/wipro-q2-fy26-repeat/results.pdf
Receipt: data/private/wipro-q2-fy26-repeat/acquisition.json
Manifest: data/private/wipro-q2-fy26-repeat/document.json
Import result: data/private/wipro-q2-fy26-repeat/import.json
Page inspection: data/private/wipro-q2-fy26-repeat/page-11.json
Rendered page: data/private/wipro-q2-fy26/page-11.png
Archive: data/private/real-archive/documents.sqlite3
Document ID: bce9d0c0d8944d0f162749f132154d7e46d7f32c233afcfa15b87aa476c21c04
```

Physical page 11 (printed page 1) was visually inspected. It identifies consolidated Ind AS results, INR millions and distinct three-month, six-month and annual columns. The page inspector returned 580 words. Some embedded text contains OCR-like label/punctuation errors, so text availability is not proof of accurate financial extraction. Other sections include standalone results and a different accounting standard. Select the section explicitly before preparing a recipe.

At this milestone, 73 tests passed: the original 67 plus six acquisition tests covering provenance/output protection, 403/302/429, HTML responses, TLS errors and process timeout. The later shared downloader expanded the suite; see [current validation](../implementation.md#validation). Tests use generated PDFs; live requests are manual validation, not CI dependencies.

This is user-directed private research. HTTP access does not establish hosted or redistribution rights. Original files, receipts and archive are ignored by Git. No facts from the real document have been accepted or published. Next: verify a hash-bound extraction recipe against this document and record a review before exposing facts through MCP.
