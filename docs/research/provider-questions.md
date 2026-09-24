# Source-access and provider questions

Prepared 23 September 2026. These are reviewable questions for future use; no message has been sent.

## Immediate academic / issuer request

Explain that a four-person professor-supervised team is building a free, six-to-eight-week Indian-company research prototype. Request a small specified set of quarterly results and annual reports for five companies. Ask whether the institution can obtain a research dataset or written permission for the following distinct activities:

1. Retrieve/import the documents through the proposed method and retain a private research copy.
2. Extract facts and searchable passages, preserving original citations.
3. Send bounded passages to a named external model provider through an MCP host, or keep processing local if required.
4. Demonstrate results to the professor and evaluators, and include limited evidence in a report or recorded demo.
5. Publish code, synthetic tests and a benchmark manifest; clarify separately whether any real data or excerpts may be published.

Ask for the applicable agreement, attribution, retention, deletion and reporting requirements. Clarify that later public/commercial hosting would be assessed separately. For NSE academic access, ask which eligible datasets and volume limits apply to this exact scope. Do not assume an academic exemption automatically extends to model processing or public demos.

## Later commercial-provider comparison

Send the same specification to each candidate so quotes are comparable. Prioritize Global Datafeeds and TrueData, then Upstox's permitted integration route, Accord, or an institutional supplier as appropriate.

| Topic | Question |
| --- | --- |
| Coverage | Which NSE/BSE issuers, security types, delisted companies and filing categories are supported? |
| History | Can we get eight quarters and two annual reports per pilot company? What backfill is available? |
| Meaning of retention | Does an advertised 30-day history limit refer to retrieval windows, event history or financial periods? |
| Provenance | Are original publisher URLs, filing timestamps, raw attachments and document IDs available? |
| Financial contexts | Are standalone/consolidated, Ind AS/IFRS, units, audit status and duration/instant contexts explicit? |
| Corrections | Can we retrieve original and revised filings, their public availability times and relationships? |
| Acquisition | REST, SFTP, batch download or stream? Authentication, quotas, rate limits, retry and backfill mechanisms? |
| Private storage | May we retain documents, facts, extracted text, search indexes and embeddings, and for how long? |
| Model processing | May excerpts or structured data be transmitted to users' third-party model providers? Under what conditions? |
| Hosted product | May a paid or free multi-user MCP/API return raw data, short excerpts, facts and calculations? |
| User-owned credentials | Is a user-authorized private adapter allowed? May any cache be shared between users? |
| Commercial terms | Pilot fee, minimum commitment, exchange pass-through charges, per-user fees, taxes and overages? |
| Exit | What must be deleted when access ends? May published research and audit evidence be retained? |
| Reliability | Support response, schema-change notices, completeness checks, missed-event recovery and service targets? |

## Trial acceptance packet

Ask for permitted samples including a normal result, different reporting units, a revised filing, standalone and consolidated statements, a missing figure, and an announcement with its original attachment. Compare them against manually reviewed originals.

Score **rights fit and evidence quality before price**. A provider that supplies convenient numbers without provenance may be useful as enrichment but cannot independently fulfill Margin's evidence promise. A quote should explicitly cover MCP/AI and redistribution; a generic claim of exchange authorization is insufficient to describe the customer's allowed use.

Keep Eikon/LSEG out of the implementation dependency list unless the institution confirms an applicable entitlement in writing. Do not repurpose desktop access credentials as a shared service account.
