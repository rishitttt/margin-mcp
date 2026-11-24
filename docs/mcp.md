# Run Margin as a local MCP server

Current release **0.4.0**, 25 November 2026. Twenty MCP tools expose the existing
37 retrieval/finance and ten review functions. Six common calculations now have directly
advertised strict schemas. The core, CLI and workbench remain available independently.
The [architecture](design/mcp-aggregation.md) owns the plan published before this change;
[implementation](implementation.md) owns evidence and limitations.

## Install

Python >=3.12. Install the versioned wheel into a dedicated environment, or install the
checkout for development with `.venv/bin/python -m pip install -c requirements-dev.lock -e .`.
Console commands are `margin-mcp`, `margin-backend`, and the existing `margin-agent` and
optional `margin-workbench`. No new package dependency is required for shared mode.
The package is not yet published to PyPI; use the local wheel or checkout.

A stdio process waits for protocol messages, not typed company questions. Configure an
MCP host to launch it. Stdout is reserved for JSON-RPC; diagnostics use stderr. The web
interface and skill are not prerequisites. No provider is connected at discovery/startup.

## Choose the state owner

| Mode | Configuration | State lifetime |
| --- | --- | --- |
| Standalone | `margin-mcp --mode synthetic` or explicit live credentials | One stdio process; a host restart loses its plans/results/counters |
| Shared, recommended for LM Studio | Explicitly start `margin-backend`; frontend uses `--backend-socket` | Backend survives frontend/new-chat restarts; existing TTL/memory limits apply |

Shared mode is **local single-user macOS/Linux Unix IPC**, not a hosted HTTP service or
protocol-level session store. Standalone remains available on other systems; clean
cross-platform installation is still a separate release gate. Backend and frontends must
run the same package version and OS user. No automatic backend start/restart/retry occurs.

## Shared backend: start once

Choose an absolute socket path below 100 encoded bytes in a private directory. A missing
target directory is created 0700; an existing directory must already be owned by you and
0700. Socket permissions are 0600. Do not point the socket path at a regular file.

Example, after deciding a fresh **remaining test allowance**, not an account balance:

```sh
MARGIN_BHARATSTOCK_REQUESTS=1 \
MARGIN_DRISHTI_REQUESTS=12 \
MARGIN_DRISHTI_CREDITS=4 \
MARGIN_ENABLE_OPERATIONS=bharatstock.get_financials,drishti.get_news \
/absolute/venv/bin/margin-backend \
  --socket /absolute/private-dir/core.sock \
  --mode live \
  --credentials-file /absolute/private/providers.env \
  --record-dir /absolute/private/logs
```

Keep that process running. It alone loads provider credentials, owns HTTP clients and
Drishti lifecycle, and records sanitized tool calls. The credential file is parsed as
data, supplies provider keys only and is not automatically loaded. Configure mode and
budgets through the explicit flags/environment. No keys belong in tool arguments or Git.
For a first offline check use `--mode synthetic` and omit the credential file; resulting
companies/values are fictional and cannot answer real-company questions.

Use these operator commands to inspect/stop it; neither makes a provider request:

```sh
/absolute/venv/bin/margin-backend --socket /absolute/private-dir/core.sock --status
/absolute/venv/bin/margin-backend --socket /absolute/private-dir/core.sock --stop
```

Stopping the backend cancels work/shuts upstream clients and loses in-memory state.
Dispatched requests may already be billed. Reconcile allowance before a later restart;
this is not durable daily/account-wide quota enforcement. A lock prevents two cooperative
backends owning the same address. A stale socket may be removed only after acquiring that
lock and establishing no active listener; unrelated files are never overwritten.

## LM Studio / host configuration

Adapt this `mcpServers` form in the host's config editor. In LM Studio use Program >
Install > Edit mcp.json. Launch the frontend with absolute paths:

```json
{
  "mcpServers": {
    "margin": {
      "command": "/absolute/venv/bin/margin-mcp",
      "args": [
        "--backend-socket", "/absolute/private-dir/core.sock",
        "--mode", "live"
      ]
    }
  }
}
```

Credentials, allowances and `--record-dir` belong on the **backend**, not this frontend.
The frontend's `--mode` is an optional expectation check; a mismatch fails closed.
Configuring backend credentials or recording on the proxy is rejected. Frontend disconnect
or cancellation does not close the backend or cancel an already submitted run. Use the
explicit cancellation tool to cancel a run. Shared mode retains one identity across
frontends; restarting the backend invalidates old handles rather than reusing them.

For the local mtest setup the socket is `/Users/rishit/Desktop/mtest/shared/core.sock` and
the executable is `/Users/rishit/Desktop/mtest/.venv/bin/margin-mcp`. After a wheel upgrade,
restart the backend deliberately and reconnect the host; never silently replenish spent
allowances. The existing `.env` and logs remain private, outside the package.

## Tools and financial output

The original workflow tools remain: `margin_status`, `margin_catalog`, `margin_preview`,
`margin_company_preview`, `margin_run`, `margin_run_status`, `margin_result`,
`margin_sources`, `margin_facts`, `margin_calculate`, `margin_cancel`,
`margin_connect_drishti`, `margin_review`, `margin_review_sources`.

Six **direct** tools take the financial fields at the top level, without a `function`
selector or nested `arguments` wrapper. Their JSON Schemas are advertised in tools/list:

| Tool | Core function / inputs |
| --- | --- |
| `margin_calculate_margins` | `finance.calculate_margins`: profit and revenue facts |
| `margin_convert_units` | `facts.convert_units`: value fact and target_unit |
| `margin_compare_periods` | `finance.compare_periods`: previous and current facts |
| `margin_calculate_cashflow_metrics` | `finance.calculate_cashflow_metrics`: cfo and capex facts |
| `margin_calculate_profitability` | `finance.calculate_profitability`: facts array |
| `margin_calculate_balance_sheet_metrics` | `finance.calculate_balance_sheet_metrics`: facts array |

Catalog entries identify their actual `mcp_execution` route. Use exact schema lookup for
other functions. Catalog identifiers such as `finance.calculate_margins` are not tool
names and must not be renamed heuristically. Generic `margin_calculate` remains supported
for all fifteen functions, with its original `function` + `arguments` shape.

Financial results now include `financial_view` alongside the unchanged raw payload.
It deterministically converts reviewed statement fields/segments from INR to INR crore,
keeps EPS in INR/share, names operating profit/PBT/EBITDA separately and shows exact
values, rounded displays, raw values, source paths, basis and dates. The view covers at
most eight rows and twenty entries per segment array, with omission counts. It is a
selected view, not a claim that all financial data/periods were returned. Read its labels
and display strings; do not scale a formatted crore amount again. Null is not zero.
The continuing/total-profit warning and financial scope guards remain. Formatting or
schema validation does not independently authenticate issuer figures.

`margin_facts` prepares retained typed inputs with `auto` documented units; direct
`margin_convert_units` performs explicit further conversion. Company workflows default
to `fetch_missing: false`; explicit true may preview one missing financials dependency.
Pure calculations never fetch. Use company readiness before assuming a metric is
supported. Preserve starts/ends, stocks versus flows, units, basis and profit definitions;
missing/incompatible facts produce valid incomplete/partial outcomes, not fabricated data.
DCF continues to require explicit forecasts/assumptions. See [financial analysis](financial-analysis.md).

## Normal workflow and guards

Start with status. Preview an explicit bounded operation or company workflow, inspect its
costs/holds, then submit with the returned session ID, plan ID and one idempotency key.
Repeat a lost submission only with the SAME plan/key. Plans expire after ten minutes;
results are TTL/eviction bounded (default thirty minutes, five retained runs, twenty MiB).
After an unknown/expired source, stop; never silently fetch a replacement. Shared mode
preserves these handles across frontend restarts only while that backend and retention
remain valid. Read result payloads explicitly; a run summary is not a result.

Tool results include mode, contract version, backend/process session ID and per-call ID,
matching JSON text and structured JSON. Valid partial/incomplete results are not necessarily
MCP errors. Unknown tools are protocol errors. Schema feedback is bounded, identifies
allowed/missing fields and does not echo caller values or arbitrary keys. Input is capped
at 64 KiB. Private local RPC has bounded framing and up to sixteen simultaneous handlers;
failed/lost replies never trigger automatic replay. No public listener or multi-user
authorization service is introduced. Known credentials are rejected/redacted by the core.

Drishti connection/metadata refresh is explicit and counts HTTP allowance. Its schema
presence does not establish live entitlement. Neither a backend restart nor a zero-credit
estimate proves upstream quota was restored or a BharatStock request is free.

## Recording and review handoffs

Logging is off by default. Use backend `--record-dir` for shared mode; one unique private
JSONL is created per backend lifetime, spanning frontend sessions. Standalone also supports
`--record-dir`, or legacy `--record-file NEW_PATH` with no overwrite. New directories are
0700 and files 0600. No automatic pruning is enabled; keep licensed traces private and
apply the applicable retention policy. The 64-MiB log bound stops another dispatch when
full. Pre-write failure prevents dispatch; post-action failure returns the available
result with a warning, never a hidden retry.

Every tool accepts a one-line `why` self-report. Logs capture sanitized requests/results
and call IDs, not final prose, host conversations or hidden reasoning. Citation/sentiment
semantics remain host assessments through `margin_review`; workflow discovery is local.
Margin runs no LLM and cannot invoke other host tools merely because they are installed.

## Validation and limitations

```sh
.venv/bin/pytest -q
.venv/bin/python scripts/smoke_mcp.py --output reports/private/new-standalone-check
.venv/bin/python scripts/smoke_mcp_shared.py --package-root src --output reports/private/new-shared-check
```

Unix-socket tests require local socket-binding permission; the test fixtures prohibit
external TCP/provider requests. The standalone runner exercises all twenty tools in 33
calls/66 events using fictional data. The shared runner exercises three separate frontends,
retained results/facts and duplicate submission without duplicate dispatch. Saved real HUL
responses are checked separately without fetching again. These are software/transport
checks, not proof of model answer accuracy. The latest-revision protocol conformance,
clean cross-platform installs, larger-model comparisons, source accuracy and remote hosting
remain separate release gates. Existing SDK acceptance negotiated 2025-11-25; do not
infer 2026-07-28 conformance. [Distribution evaluation](design/mcp-aggregation.md#distribution-and-live-release-evaluation-25-november).

## Historical host-debug observations

The dated notes below describe earlier releases. Their fixed-file, fourteen-tool and
standalone state constraints are superseded by the current setup above where noted.

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
