# Margin: an MCP interface for Indian financial research

*Project summary — 28 November 2026*

## Purpose and use case

We have built Margin to help AI assistants work with Indian listed-company financial
and event data. An analyst, student or developer can connect Margin to an MCP-compatible
assistant and ask questions such as: “How has Infosys’ annual revenue grown?”, “Which
financial ratios can be calculated from the available data?” or “Does this announcement
support a particular claim?”

Margin provides the data access, calculation tools and review workflows. The connected
model interprets the question, chooses tools and explains the results. We do not run our
own LLM or maintain a financial-data warehouse.

## What has been created

- **Provider integration:** BharatStock REST supplies supported financial and market
  data; Drishti MCP supplies supported news, announcements and earnings records. Users
  supply their own provider keys and use their own subscriptions or trial allowances.
- **Financial functions:** growth, CAGR, eligible quarterly trailing-twelve-month totals,
  profitability, liquidity and cash-flow metrics, unit conversion and data-readiness
  checks. FCFF, discounted cash flow (DCF), sensitivity and scenario calculations use
  explicitly supplied inputs and assumptions; forecasts are not generated automatically.
- **Citation and content-sentiment workflows:** the host model reviews supplied or
  host-read passages. Margin checks references and exact quotations, records submitted
  judgments, produces citation reports and aggregates sentiment annotations. It does
  not independently establish source authenticity or investor sentiment.
- **Reusable interfaces:** a shared Python core, a local MCP server exposing 39 tools,
  a CLI/skill interface and an optional web workbench for testing. The package is
  published on PyPI as `margin-mcp` version 0.10.1 under the MIT license.
- **Operational controls:** strict input schemas, explicit request limits, duplicate-call
  protection, structured results and optional local logs. Brief tool-choice explanations
  can be recorded; these are visible model self-reports, not hidden internal reasoning.

## How it works

1. The user asks a question in the connected assistant. The model discovers Margin’s
   advertised tools and input schemas.
2. For retrieval, Margin validates the request and checks local allowances before
   contacting the relevant provider. Preview operations can describe a request without
   fetching data. Company-finance workflows can fetch a bounded financial response and
   calculate the requested result directly.
3. Calculations run in Python rather than relying on model arithmetic. Results preserve
   reporting dates, units, accounting basis, definitions and missing-data warnings.
4. Margin returns structured report rows and source information. The assistant presents
   them to the user. Review tasks additionally require the host’s evidence-linked
   judgments; Margin validates and aggregates those submissions.

For example, a revenue-growth request retrieves the available matching annual periods,
calculates absolute and percentage changes, and returns the dated inputs and computed
results. Missing data is reported rather than replaced with invented values.

## Current status and limitations

The current release has 654 passing repository tests and 637 passing tests from its
public source distribution. Hosted checks cover Windows, macOS and Linux, including
package installation and MCP startup. Selected real-provider checks succeeded for
Infosys and Hindustan Unilever financial data and Infosys-filtered event retrieval.
These checks establish selected-case functionality, not universal company coverage.

The product is usable for local research and demonstrations. Provider facts remain
unverified against original filings. Host models can still choose the wrong tool or
misstate a correct result, particularly when context is constrained. Broader coverage
and controlled comparisons across models remain future work.

## Proposed evaluation

We will create a master set with independently checked reference answers, initially
covering Infosys and Hindustan Unilever. A proposed starting size is 40 scored questions
plus eight separate calibration questions. Tasks will cover retrieval, financial
calculations, explicit-assumption valuation, claim review, content sentiment, and
handling missing data or incompatible units/periods. The scored questions and answer
keys will be fixed before the main experiment; answer keys will not be shown to models.

Our initial model cohort will be:

| Model | Purpose |
| --- | --- |
| [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | Small-model test and comparison with the same family's 8B model |
| [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | Continuity with our existing local trials |
| [Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) | An already-installed model from another family |
| [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) | A different reasoning/tool-use architecture, also already installed |

A hosted model such as [GPT-6.2 Sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol)
can be added as a separately budgeted reference. These are proposed comparisons, not
claims about which model will perform best.

Each model will receive the **same questions with and without Margin**, in fresh
contexts, with matched settings and three repetitions. Supplied-data tasks will give
both conditions identical evidence; live retrieval tasks will be reported separately,
with common source access where feasible. This separates calculation/review assistance
from the benefit of obtaining data. We will score answer accuracy, units and reporting
scope, evidence support, task completion, latency and tool/provider usage. Context
overflow and tool-selection failures will remain visible in the results.

For reasoning-trace analysis, we will retain prompts, final answers, actual tool calls,
arguments, responses, errors, timestamps and one-line explanations of important choices.
We will additionally capture model-emitted thinking where exposed by the local runtime;
[LM Studio's streaming API](https://lmstudio.ai/docs/developer/rest/streaming-events)
provides reasoning and tool events. Hosted APIs may expose only
[summaries](https://developers.openai.com/api/docs/guides/reasoning#reasoning-summaries). Explanations
will be labelled as model self-reports, not guaranteed internal reasoning. We will
analyze patterns in tool selection, error recovery, evidence use and unsupported claims,
and relate these to task success.
