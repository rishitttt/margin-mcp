# Six-to-eight-week delivery and evaluation plan

Updated 24 September 2026. See the [functionality-to-data map](design/functionality-data-map.md) for current dependencies, scope gates and completion checks. The week-by-week table is a proposed sequence, not elapsed-time progress.

## Confirmed constraints

- Four people, learning skills as needed; Python selected for the implementation.
- Professor-supervised project intended to become a usable product.
- Free prototype; evaluate paid sources later.
- Approximately 1.5–2 months available.
- Small initial universe; no requirement for live retrieval.
- A hosted MCP/data service is a later option.
- Refinitiv Eikon access exists but is not assumed usable for this project.

## Release definition

The broader coverage target is **five selected companies**, **eight quarters and two annual reports each**; report actual gaps. First complete a cited workflow on the existing five documents across Wipro, TCS, Infosys and HCLTech, then acquire a second independent results filing per company. These are historical IT-sector samples, not current or cross-sector coverage. For the broader release, revisit company selection to include at least two from one sector and at least two other sectors; candidates may include ITC, Asian Paints and Larsen & Toubro, subject to access. Do not let the larger collection target delay accepted facts and a working host demonstration.

Select six to ten clearly defined metrics, such as revenue from operations, profit before tax, profit for the period, profit attributable to owners, basic/diluted EPS, total assets, cash and equivalents, and operating cash flow. They need not all exist at quarterly frequency. Return available annual/half-year balance-sheet and cash-flow periods honestly.

Demonstration questions:

1. Resolve a company and explain which security/listing was matched.
2. Find the latest results **available in this corpus**.
3. Return consolidated revenue with the original period, unit and exact source.
4. Compare a compatible prior quarter and show the calculation.
5. Retrieve a relevant management/risk passage and distinguish interpretation.
6. Explain why a requested figure or comparison is unavailable.
7. Generate a citation from stored evidence and reject a deliberately altered numeric claim or reporting period using the proposed [citation verification component](design/citations.md). Report the scope checked; arbitrary prose is not automatically verified.

Ownership, broad event monitoring, bank-specific metrics, prices and macro adapters are stretch work after the core gates pass. Defer a custom chat frontend.

## Milestones

| Time | Outcome | Exit evidence |
| --- | --- | --- |
| Week 1 | Confirm permitted source path, select companies and metrics, define evidence schema | Written source assessment, one usable document, two-reviewer labels, host chosen |
| Week 2 | One end-to-end local MCP workflow | Lookup → filing → one sourced fact works in a host; failures are explicit |
| Weeks 3–4 | Expand curated ingestion, normalization and comparison | Coverage inventory, repeatable import, source-linked facts, meaningful regression tests |
| Week 5 | Passage retrieval, revision/missing-data behavior, usability | Brief/earnings workflow, documented error cases and parser limitations |
| Week 6 | Freeze a submission-quality release | Benchmark results, install instructions, report, architecture and recorded demo |
| Weeks 7–8 if available | Improve portability and selected coverage | Second host, targeted accuracy fixes; optional private hosting only if rights permit |

Curated acquisition is established for the current samples. If expanding coverage stalls, reduce document breadth and prioritize the existing corpus or authorized user-file import. Use synthetic fixtures for software behavior, but do not count them as real-company accuracy evidence. Do not let a broad discovery adapter delay the first reviewed fact/citation workflow.

## Four ownership areas

These are suggested workstreams for the human team, not assignments already made.

| Owner | Responsibility | Shared interface |
| --- | --- | --- |
| A | Source permissions, acquisition, identity and manifests | Versioned document and entity records |
| B | Parsing, metric definitions and financial validation | Facts, contexts and evidence locations |
| C | Storage/query services, MCP handlers and host integration | Stable typed tool contracts |
| D | Benchmark labels, evaluation, developer experience and documentation | Test questions, scoring, reproducible experiments |

Pair A/B on source samples and C/D on real user workflows. Every material benchmark number should be independently checked by someone other than its extractor. Review integration twice weekly using the same small corpus before widening coverage.

## Evaluation design

Build **60 real-company questions**: 10 identity, 20 numeric facts, 10 period comparisons, 10 passage/citation questions, and 10 missing/conflicting/revised-data cases. Reserve 20 as a held-out set including unseen documents or issuers. Track category counts and actual source availability; do not fabricate real-world revisions if none are collected. Synthetic edge cases belong in a separate software test suite.

Label company, metric definition, unit, period, scope, accounting basis, expected value/answerability, source and exact evidence location. Numeric correctness requires the full tuple, not just a matching number. Two reviewers reconcile disagreements before freezing labels.

Compare the same host/model under: (A) no Margin, with its permitted normal research tools documented; (B) authorized raw-document retrieval only; (C) Margin's normalized facts and evidence. Freeze corpus, model identifier, prompt, tool availability and run time. Where feasible repeat trials and report variability. Record unavailable baselines rather than inventing results. An offline no-tool baseline measures data access as well as reasoning, so do not overclaim causality.

Measure entity accuracy, fact accuracy, answered-question coverage, citation precision/support, citation coverage, comparison validity, correct abstention, passage relevance, task completion, latency and token use. Include errors and unsupported questions in denominators. Report both supported-subset and full-benchmark performance.

Proposed acceptance targets (not observed results): all returned numeric facts have evidence references; at least 95% exact fact-tuple correctness on the supported held-out set; all deliberate incompatible comparisons in the software suite are rejected; no fabricated values for missing fields. Also report answer coverage so high accuracy cannot be achieved by refusing everything. Record p50/p95 query latency with hardware and cache state; set performance budgets after the first measured implementation.

## Product validation

Have three to five prospective users perform a cited results comparison with their own preferred harness. Measure time to a verified answer, failed tool calls, citation usefulness, and whether installation is understandable. Ask what they would use repeatedly. This supplies product evidence beyond a successful professor demo.

## Remaining decisions

Remaining near-term decisions: first host, final benchmark company selection, reviewed metric definitions and calendar submission date. The current sample corpus and acquisition routes are documented; wider collection and hosted-serving scope need separate assessment. Code licensing must be chosen before claiming a public reuse license. Paid suppliers, commercial packaging and hosting platforms can wait.
