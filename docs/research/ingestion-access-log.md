# Real-document acquisition log

Update, 24 September 2026: four BSE documents downloaded twice with identical hashes and imported privately: TCS results, HCLTech results, Infosys board/financial package and Wipro press release/presentation. HCLTech's indexed BSE live URL returned 404; its historical attachment URL succeeded. See [verified sources and commands](bse-acquisition-results.md). Earlier failures below do not imply these companies' filings remain unavailable.

Historical observations from 23 September 2026. The table records the initial issuer-site attempts and subsequent Wipro success. TCS and HCLTech issuer-route failures persisted; their later BSE acquisition success is recorded above.

| Source | Observation |
| --- | --- |
| Infosys Q2 FY26 | Existing investigation located the original results PDF; its earlier direct download returned 403. The issuer landing page remains discoverable. |
| TCS financial-statements page | Web research could read the page, but a direct local HTTPS request returned 403 after using the system trust store for certificate verification. |
| TCS FY26 annual report | Direct request to the original publicly linked PDF returned 403. No bytes were retained. |
| HCLTech Q2 FY26 | Official financial-results page linked the original PDF. The web reader reported unsupported `application/octet-stream`; direct local requests timed out with 30-second and 60-second timeouts. No PDF was retained. |
| Wipro Q2 FY26 | Two HTTP 200 downloads, identical SHA-256, 33 readable pages. Imported into private archive and physical page 11 visually inspected. See troubleshooting report. |

No authentication, anti-bot bypass or bulk collection was attempted in these probes. Source-specific access failures do not prove the documents are unavailable to a person using their own browser. Private source files and extraction outputs must remain outside Git.

Links:

- [Infosys investigation](infosys-feasibility.md)
- [TCS results directory](https://www.tcs.com/investor-relations/financial-statements)
- [TCS annual report](https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/ar/annual-report-2025-2026.pdf)
- [TCS use conditions](https://www.tcs.com/who-we-are/legal/legal-disclaimer)
- [HCLTech results directory](https://www.hcltech.com/en-us/investor-relations/financial-results)
- [HCLTech original Q2 FY26 PDF](https://www.hcltech.com/sites/default/files/documents/investor-reports/Audited-Financial-Results-for-the-quarter-ended-September-30-2025_0.pdf)
- [HCLTech use conditions](https://www.hcltech.com/en-us/disclaimer)

Issuer terms distinguish limited informational use from public redistribution; no shared or commercial corpus rights have been established. The generated synthetic PDF remains the reproducible test input. Its visual inspection and extraction results are described in [the ingestion guide](../ingestion-development.md).
