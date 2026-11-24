# Run Margin as a local MCP server

Implemented **25 November 2026**, package **0.3.0**. The stdio adapter exposes 14 workflow
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
version 0.3.0. No host registration/settings were changed automatically by the build.

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
For experiments, ask the model to include it and configure an explicit new log path:

```sh
.venv/bin/python -m margin.interfaces.mcp --mode synthetic \
  --record-file reports/private/my-mcp-run-01.jsonl
```

The parent directory must exist. Files are created 0600 and never overwritten; default
logging is off. JSONL request/response events include a monotonically increasing sequence,
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
