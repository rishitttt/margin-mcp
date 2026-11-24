# Run Margin as a local MCP server

Implemented **25 November 2026**, current package **0.3.3**. The stdio adapter exposes 14 workflow
tools over the same core used by the workbench and CLI. It makes 37 retrieval/finance
functions and ten local review functions discoverable. The web server and skill are not
required for MCP use. [Architecture](design/mcp-aggregation.md) records the plan published
before implementation; [function validation](reference/function-validation.md) and
[finance support](design/finance-data-support.md) describe actual data limits.

## Install and launch

From the checkout, install into your Python >=3.12 environment:

```sh
.venv/bin/python -m pip install -c requirements-dev.lock -e .
.venv/bin/python -m margin.interfaces.mcp --mode synthetic
# Equivalent installed console entry point:
.venv/bin/margin-mcp --mode synthetic
```

The process waits for JSON-RPC on stdin; it is not a terminal chat or a website. Add it to
your MCP host instead of typing company questions into that terminal. Stdout is protocol
only; a short startup/mode message goes to stderr. Closing the host/stdio connection
closes the core and provider tasks. No data is fetched at startup, discovery or preview.

Synthetic mode contains fictional software examples. It can test integration without
keys but cannot answer a real-company question. Live mode uses actual providers and the
existing process limits. Export provider keys locally or explicitly supply an ignored
provider env file:

```sh
.venv/bin/python -m margin.interfaces.mcp --mode live --credentials-file .env
```

The credential file is parsed as data; no shell code is executed. It supplies provider
keys only. Set mode, allowances and enabled operations explicitly in the environment or
host config. There is no automatic `.env` loading. Avoid keys in tool arguments, URLs,
logs, source or config committed to Git. There is no public remote server or HTTP port.

## Host-neutral configuration

Adapt this common `mcpServers` form to your host's configuration UI/format. Use absolute
paths; a GUI host may not inherit your shell's virtual-environment PATH. Hosts supporting
stdio can launch this process; browser-only remote connectors need a later HTTP transport.

```json
{
  "mcpServers": {
    "margin": {
      "command": "/absolute/path/to/margin-mcp/.venv/bin/python",
      "args": [
        "-m", "margin.interfaces.mcp", "--mode", "live",
        "--credentials-file", "/absolute/path/to/margin-mcp/.env"
      ],
      "env": {
        "MARGIN_BHARATSTOCK_REQUESTS": "2",
        "MARGIN_DRISHTI_REQUESTS": "12",
        "MARGIN_DRISHTI_CREDITS": "4",
        "MARGIN_ENABLE_OPERATIONS": "bharatstock.get_financials,drishti.get_news"
      }
    }
  }
}
```

These are example **process ceilings**, not measured account balances or permission to
reset consumed quota. Choose a fresh bounded allowance for your experiment. Key access
does not remove operation opt-ins or changed/expired-schema holds. Drishti metadata must
be explicitly connected before its data operations; no npm install is needed.

For an offline first connection use `--mode synthetic`, omit the credential-file args
and keep the limits small. The host should see 14 tools named `margin_*` and server
version 0.3.3. No host registration/settings were changed automatically by the build.

## Tools and normal flow

| Tool | Use |
| --- | --- |
| `margin_status` | Read mode, process/session ID, provider readiness, local ledger and recording status |
| `margin_catalog` | Summaries or exact schemas; groups `retrieval`, `calculations`, `company`, `review` or `all` |
| `margin_preview` | Validate one to eight whitelisted retrieval/calculation operations without executing |
| `margin_company_preview` | Preview company calculation/source reuse or one explicitly allowed financial request |
| `margin_run` | Submit a plan using its session ID and idempotency key; optional 0–30 second wait |
| `margin_run_status` | Inspect/wait without starting extra work |
| `margin_result` | Read one retained operation's payload, receipt and limitations; never refetch |
| `margin_sources` | Retained financial-source handles |
| `margin_facts` | Prepare typed facts using `auto`, explicit units or unknown/null |
| `margin_calculate` | Execute one explicit-input deterministic calculation without data calls |
| `margin_cancel` | Explicit run cancellation, preserving already dispatched/uncertain accounting |
| `margin_connect_drishti` | Explicit metadata connection/refresh; requires current process ID and HTTP allowance |
| `margin_review` | Local citation/sentiment functions, schemas discovered through catalog |
| `margin_review_sources` | Import retained news text; no browsing or source fetch |

Start with `margin_status`. Then request exact schemas, for example:

```json
{"group":"company","name":"finance.company_data_readiness","include_schemas":true}
```

Pass this to `margin_company_preview` for a real listing only in live mode:

```json
{"function":"finance.company_data_readiness","ticker":"HINDUNILVR","exchange":"NSE","period_type":"annual","money_unit":"auto","fetch_missing":true,"why":"Inspect which annual financial calculations the returned fields support."}
```

Inspect the preview's operations and estimated costs. Run only wanted data work using
the returned `session_id`, `data.plan_id` and a new 8–100 character idempotency key.
Read the run's operation IDs, then call `margin_result`. Reusing the same plan/key returns
the same run. After an ambiguous response, use that same key or inspect status; do not
create another submission to force a retry. Old process IDs are rejected after restart.

Company workflows default to `fetch_missing: false`; explicit true allows one financials
request only when a matching retained source is absent. Missing fields in an existing
source do not trigger replacement calls or extra pages. `margin_calculate` never fills
inputs automatically. Use [financial analysis](financial-analysis.md) for units, stock/flow
separation, eligible TTM periods, continuing-profit scope and explicit-input valuation.

Citation/sentiment workflows are reached through `margin_review`; invoke
`protocols.list_workflows` with empty arguments for the process, then inspect exact
review schemas. Host passages/judgments remain attributed. Quote matches and numerical
checks do not authenticate a website or original filing; unsupported hosts retain an
unreviewed/incomplete result rather than receiving hidden Margin-side model inference.

## Results, errors and cancellation

Each call returns matching JSON text and structured JSON with `contract_version`,
`session_id`, `call_id`, `mode`, `tool` and `data` or a safe `error`. Optional submitted
`why` appears as `decision_summary`. Preserve nested provider payloads, source paths,
units, bases, dates, warnings and receipts. A local calculation's `partial`, `incomplete`
or `not_meaningful` is a valid domain result, not necessarily MCP `isError=true`.

Tool/schema/access failures return `isError=true` with a stable domain code; raw provider
exceptions and headers are withheld. Inputs are bounded to 64 KiB, outputs are bounded,
and known credentials are rejected/redacted. Available schemas do not prove live product
entitlement or financial truth. Tool annotations are hints, not authorization controls.

Run/status waits are bounded to 30 seconds. Cancelling that waiter leaves an already
submitted core run active and recoverable by its existing key/ID. Use `margin_cancel`
to cancel the run itself. A cancelled upstream request may already have been billed;
there is no refund or automatic-retry claim. Results expire/evict without refetch.

## Optional decision and observation logs

Every tool accepts an optional `why`: one visible line of 1–280 characters. This is a
self-reported explanation, not internal reasoning or evidence of a faithful explanation.
For experiments, ask the model to include it and configure a recording directory.
Version 0.3.3 creates a unique timestamp/UUID JSONL file on each server launch, including
when a host restarts the process for a new chat:

```sh
.venv/bin/python -m margin.interfaces.mcp --mode synthetic \
  --record-dir reports/private/my-mcp-run
```

The directory is created if absent (0700 for a newly created target directory). Files
are created 0600 and never overwritten; default logging is off. There is no automatic
log pruning or aggregation across processes. The alternative `--record-file NEW_PATH`
still requires an existing parent directory and a previously unused filename. These
options are mutually exclusive. Prefer `--record-dir` in persistent host configuration
so repeated launches do not require editing filenames. JSONL request/response events include a monotonically increasing sequence,
process/call IDs, sanitized arguments/results, mode and timestamp. `call_id` in tool output
links to those events. Logs can contain licensed source text and must stay private.
The 64-MiB process-log bound fails before another dispatch when reached. Pre-action write
failure stops dispatch; a post-action failure returns the existing result with a warning,
not a hidden retry. Optional logs are not complete host conversations, hidden reasoning,
a frozen-data replay engine or an independent benchmark. The old skill/pilot logger stays
separate. Do not compare old and new task versions without freezing their contracts.

## Validation and remaining gates

```sh
.venv/bin/pytest -q
.venv/bin/python scripts/smoke_mcp.py --output reports/private/my-mcp-smoke
```

The smoke runner uses actual SDK stdio messages but **fictional company data**. It refuses
non-synthetic results, exercises all 14 tools, records 27 calls/54 sanitized events, and
checks discovery, preview/run, idempotency, finance, source import and citation/sentiment
handoffs. Its counters are simulated and must not be reported as provider usage.

Source and isolated-wheel stdio acceptance passed with protocol 2025-11-25. The wheel was
installed into a separate target and launched outside the checkout using existing pinned
dependencies. This is not a clean dependency install on all operating systems or a model
reasoning evaluation. No authenticated provider/model request was used to build/test this
adapter. Existing real core tests remain separately documented. A fresh-chat model-host
trial, a separately budgeted live MCP pass and cross-model benchmarking are next steps;
the professor's evaluation harness remains independent of product installation.

The [25 November distribution/release evaluation](design/mcp-aggregation.md#distribution-and-live-release-evaluation-25-november)
separates local package publication, optional MCPB/registry discovery and later HTTP
hosting. It also records the untested 2026-07-28 protocol path, protocol-error repair,
clean-install/host acceptance gates and provider-rights questions. Current SDK acceptance
is not a claim of latest-revision conformance or readiness for multi-user hosting.


## LM Studio catalog-routing repair: 0.3.1

The first user-reported Qwen3-8B attempt reached status and catalog, then the host rejected
`finance.calculate_margins` / `finance_calculate_margins` as unknown tools. The private log
contains only those first two calls; no calculation or provider request reached Margin.
This is an actual host observation, not a successful host workflow acceptance.

Catalog names are function identifiers. Call **`margin_calculate`** with
`{"function":"finance.calculate_margins","arguments":{"profit":...,"revenue":...}}`.
Do not call or rename the function as a separate MCP tool. Version 0.3.1 adds an explicit
`mcp_execution` route to every catalog entry, stronger tool/server instructions and safe
JSON-RPC errors for unknown tool names. Request one named schema to avoid sending every
financial schema to a small model. A host may reject an unknown tool before contacting
Margin, so server error recovery cannot replace clear discovery instructions.

The earlier suggested numbers-only margin prompt was underspecified for the fact-based
calculation. Profit/revenue facts need matching units, issuer, reporting period and basis;
missing period starts do not establish compatible flows. Never invent metadata to pass
validation. For a **declared hypothetical software check**, paste:

> Use only registered Margin MCP tools. Discover just finance.calculate_margins with
> margin_catalog(group="calculations", name="finance.calculate_margins",
> include_schemas=true). Then call margin_calculate with that function identifier and
> nested arguments. This is explicitly a hypothetical example: issuer EXAMPLE_ONLY,
> INR amounts, standalone annual period from 2025-04-01 through 2026-03-31, net profit
> 150 and revenue 1000. Use those declared assumptions, label the output hypothetical,
> make no provider calls, and include a brief top-level why with each tool call.

Expected calculation: 15%, with zero provider usage. This example is not a real company's
financial result. If using actual financial data, use retained prepared facts and their
actual source context. If context is unavailable, report incomplete or request it.

Install the new 0.3.1 wheel into the separate test environment, change the configured log
path to a **new** filename before reconnecting, and start a fresh chat so cached schemas
and failed-call history are cleared. Existing recordings are never overwritten. The
patched source and installed-package SDK checks do not prove that Qwen now completes the
workflow; repeat the LM Studio chat test and retain its new log separately.


## Financial input diagnostics: 0.3.2

The second LM Studio/Qwen attempt reached `margin_calculate` five times. Each request
added an unsupported `hypothetical` field inside the function arguments; the first also
used unsupported `currency`/`date` fields and omitted required fact context. Subsequent
requests omitted `period_start`. The recorded catalog schema exactly matches the runtime
schema: numeric strings and numbers are both supported. This was not schema drift.

Version 0.3.2 replaces opaque local-function/MCP validation messages with bounded paths,
allowed field names, missing required fields and expected types/formats. Messages do not
quote supplied values, unknown property names or dynamic caller keys. Validation remains
strict: no dropping extra fields, coercing inputs or inventing facts. For margins, the
specific root guidance is `/: unexpected fields; allowed fields: profit, revenue.`
Remove the extra flag, then use the already explicitly declared period start on both
facts. Removing the flag alone passes schema validation but leaves the calculation
incomplete; adding the declared starts yields 15% for the hypothetical example.

There are two levels of schema exposure: `tools/list` advertises the strict MCP wrapper
but leaves its nested `arguments` object generic. `margin_catalog` returns the complete
selected function schema on demand, which is also used for runtime validation. The
catalog successfully delivered the exact schema in this observed run. Directly typed
MCP tools for a small set of common functions are a planned usability improvement;
this patch does not claim that those have been implemented. Inlining all calculation
and review schemas at once needs a context-size and host-compatibility evaluation.

After upgrading to 0.3.2, reconnect with a fresh recording filename (for example `03`
if unused), and start a new chat. Explain hypothetical status in `why` or fact `source`,
not an undeclared flag inside function `arguments`. Retest actual model recovery; offline
reproduction is not proof of a successful model conversation.


## Repeated-chat startup repair: 0.3.3

The LM Studio configuration reused `--record-file .../qwen3-8b-04.jsonl`, which already
existed. Reproducing startup with that target failed while preserving its contents;
LM Studio logs also showed repeated startup failures. This is a recording collision,
not evidence that a model or financial calculation crashed the server. The fixed-file
configuration was unsuitable for a host that can start a fresh process for a new chat.

Use `--record-dir /Users/rishit/Desktop/mtest/logs` in the local test configuration in
place of the fixed-file flag and filename. Each process generates its own new log;
existing recordings remain untouched. Files correspond to process lifetimes, not a
promise of one file per chat: hosts may reuse or restart server processes. Restarting
still resets process-local counters and retained handles; it does not replenish upstream
quota. No persistent financial corpus or account-wide budget store is added.

Repeated source/installed stdio launches into the same recording directory must both
initialize, write separately and preserve prior log hashes. Provider/model calls for this
repair remain zero. Existing fixed-file refusal/0600/log-failure safeguards remain.

The prior user test also established narrow model-host success: the fully specified call
in qwen3-8b-03 succeeded once, and the independent-construction task in qwen3-8b-04 used
one catalog call, received incomplete for missing starts, then supplied the declared
starts and returned 15%. Record the latter as a pass with one recovery, not a first-try
pass or a full real-provider/host compatibility evaluation.

## Real retrieval versus answer accuracy

The subsequent HINDUNILVR annual one-row request completed in one model turn with one
BharatStock HTTP attempt. The model's final prose nevertheless contained tenfold crore
conversion errors and mixed up operating profit and PBT. The raw result included the
correct documented-INR warning; the model did not use fact preparation/unit conversion.
Treat transport success, data interpretation, arithmetic and source verification as
separate evaluation dimensions. Reprocessing this same saved response through the local
financial core preserved the unit/scope guards without further provider calls. See the
25 November live-review checkpoint in [implementation](implementation.md).

For financial statements, `margin_facts` prepares retained typed facts and unit evidence.
`facts.convert_units`, invoked through `margin_calculate`, performs the actual conversion.
Neither authenticates issuer filings. Conversion to crore divides absolute INR by
10,000,000; EPS remains INR per share. Never silently rename total profit as continuing
profit or operating profit as EBIT/PBT. More pages remain explicit data work and are not
authorized by a provider's pagination count. After a process restart, expired source
handles must not silently trigger a replacement request.
