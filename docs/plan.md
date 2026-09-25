# Six-to-eight-week delivery and evaluation plan

Updated 25 September 2026. This is the active proposal, not implemented behavior or elapsed-time progress. See [implementation status](implementation.md) for delivered capabilities and [architecture](design/architecture.md) for boundaries.

## Confirmed constraints

- Four people, Python, professor-supervised project intended to become a usable product.
- Free prototype, approximately six to eight weeks; paid services and hosting can be evaluated later.
- Indian-market research through the user's own AI harness, without a custom chat frontend or mandatory model subscription.
- Focus on external APIs/tools and temporary evidence retrieval. Do not build, expand, backfill or schedule maintenance of our own financial corpus.
- Preserve existing local metadata, discovery, acquisition, archive and extraction functionality as optional utilities and regression fixtures.
- Providers are interchangeable candidates, not a fixed list. Refinitiv Eikon is not an assumed entitlement.
- Continuous live feeds are not required. On-demand retrieval can use available historical data from upstream providers.

## Release definition

Deliver a cited research workflow that starts without importing a metadata corpus: resolve an Indian company, select an available source, retrieve financial/contextual data or temporarily read a document, and return bounded evidence to the host. The current server still requires an imported database; removing that requirement for external mode is work to implement, not current behavior.

Start with one source and a few representative questions, then add a complementary source. Verify actual access, history, units, reporting basis, source attribution and failure behavior before choosing providers. Retain provider-reported values, extraction candidates and independently reviewed facts as distinct statuses. Citation depth must match available evidence; an API value without a filing locator cannot claim page-level verification.

Temporary sessions hold only the material required for a question, with bounded files/results, expiry and cleanup. The default external workflow does not promote content into the persistent archive. Existing import commands remain available when explicitly chosen. The [architecture](design/architecture.md#extensible-capabilities-and-preservation) specifies the shared capability and evidence boundaries.

Demonstration questions:

1. Resolve a company and identify the security/listing unambiguously.
2. Retrieve a financial metric with its reporting basis, period, unit, provider and actual coverage.
3. Compare compatible periods and show the inputs and formula; reject incompatible or missing inputs.
4. Discover a filing/transcript, read relevant pages temporarily and return source-linked excerpts.
5. Summarize recent news and management commentary while distinguishing provider labels from model interpretation.
6. Explain unavailable history, failed providers, expired evidence or unsupported claims honestly.
7. Produce a cited answer in one real MCP host without maintaining a local financial database.

News tone, management outlook, analyst concerns and market response are separate signals. Social sentiment requires an evaluated source. Broad monitoring, automatic trading, model training and exhaustive source coverage are outside the first release.

### Proposed corpus composition

**Superseded collection proposal; retained here to preserve earlier references.** The earlier target was five companies, eight quarterly results and two annual reports each (50 core coverage slots), with optional calls/presentations toward 90–130 slots. This is no longer an active collection or release target. There is no replacement document-count goal.

The seven acquired PDFs and existing extraction study remain development evidence, not a corpus to expand. See [current measurements](implementation.md#real-document-checkpoint) and [experiment findings](research/corpus-trial.md). Small synthetic or permitted test fixtures and independently checked evaluation cases do not require maintaining a financial-data repository.

## Milestones

The sequence below is a proposed allocation, not a claim that these weeks have elapsed.

| Time | Outcome | Exit evidence |
| --- | --- | --- |
| Week 1 | Shared capability/evidence contracts and one source feasibility test | Actual bounded responses, coverage/access limits, example research questions |
| Week 2 | First external MCP path and provider-only startup | Fresh startup without corpus import, source-linked output, explicit errors; existing local regression checks pass |
| Weeks 3–4 | Temporary document sessions and a complementary source | Page-aware retrieval, expiry/cleanup, duplicate/conflict handling, compatible financial contexts |
| Week 5 | Citations, comparisons and bounded news/sentiment workflow | Supported claims linked to evidence; interpretations and gaps are visible |
| Week 6 | Submission-quality release | Host demonstration, evaluation, setup instructions and report |
| Weeks 7–8 if available | Targeted reliability and portability improvements | Second host/source checks, fixes driven by measured failures; optional hosting |

If a provider is blocked by access or cost, test another capability-compatible source or reduce the demonstration scope. Do not fall back to building a historical warehouse as the default remedy. Preserve failed experiments and avoid counting documented features as tested integrations.

## Four ownership areas

Suggested workstreams for the human team, not assignments already made:

| Owner | Responsibility | Shared interface |
| --- | --- | --- |
| A | Source evaluation, adapters, identity and quota/history handling | Capability and provider response contracts |
| B | Temporary extraction, financial semantics and evidence | Context-preserving facts/passages with expiry and status |
| C | MCP tools, routing, sessions and host integration | Small typed tool contracts and compatibility checks |
| D | Independent evaluation, citations, developer experience and docs | Labelled questions, support checks and reproducible fixtures |

Integrate using the same small question set. Financial/evidence labels should be checked by someone other than the extractor. Preserve all existing local commands and tests while adding new modes.

## Evaluation design

Evaluate research tasks rather than corpus volume. Cover identity, financial facts, compatible comparisons, passages/citations, news/sentiment support and missing/conflicting/expired data. Include quota exhaustion, partial pagination/history and provider failure cases. Final question counts and split are to be set after access testing; the earlier 60-question corpus benchmark is a reference proposal, not a collection prerequisite.

Use independent labels for company, metric, period, basis, unit, expected answerability and source support. Keep software fixtures separate from live financial accuracy evidence. Use small permitted or synthetic response fixtures for repeatable tests; do not assume volatile upstream responses are reproducible. Freeze model, prompt, tool availability, source query window and retrieval time in each experiment. Historical as-of claims require upstream evidence for that date.

Where feasible compare the same host/model using its ordinary tools, direct provider/raw-document access, and Margin's normalized tools/evidence. Record differences in access rather than attributing all gains to reasoning. Test unseen documents/questions without tuning to their labels.

Measure exact financial-context correctness, answer coverage, citation support/location, comparison validity, passage relevance, sentiment support and correct abstention. Also measure source calls/credits, latency, expired-session behavior and task completion. A sentiment label's agreement with another model is not proof of market sentiment or price prediction. Report category performance and unanswered cases; set numeric acceptance thresholds after a baseline is measured.

## Product validation

Have three to five prospective users perform a financial comparison and a document/news research task in their own harness. Measure time to inspect supporting evidence, failed calls, installation friction and citation usefulness. Confirm that the new external path requires no corpus import while the old local workflow still works.

## Remaining decisions

Select the first accessible provider and complementary capability, credential model, session lifetime, host, representative companies/questions and calendar submission date. Establish actual free-tier access and evidence depth before promising coverage. Code licensing must be chosen before claiming a public reuse license. No provider purchase, outreach or account creation is implied by this plan.
