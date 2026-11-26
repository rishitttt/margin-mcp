# Run Margin as a local MCP server

## Two-step review (0.9.0)

**Current: 0.9.0, 26 November 2026 IST.** 37 full tools, 16 advanced `review`
tools, or three `review-simple` tools. The following older release/demo sections are
historical or advanced alternatives. The core inventory is 13 retrieval operations,
15 explicit calculations, nine company workflows and twelve local review functions.

Use `margin_prepare_review` with the actual issuer, title, source_url, exact source_text,
record_date (nullable), ordered claims (or [] for sentiment only), and optional
publication_date/source_kind/sentiment scope. Source and date claims remain caller
supplied. The exact inputSchema in tools/list is authoritative; do not add nested
arguments, source IDs, packet hashes or host_profile. Missing text/task must be requested
from the user. Missing selected sentiment dates are rejected before any state is saved.

Read the prepared text and submit one verdict/quote/rationale per claim in the same
order through `margin_submit_review`, using its one returned review_id. Include
sentiment_annotation exactly when sentiment was prepared. Exact quote substrings are
required where the existing evidence rules require them; an unsupported claim can
use null. Preparation is incomplete; submission returns all claim rows, citations,
support_audit and optional sentiment counts. `complete=true` means the requested
review was submitted, not that all claims are supported or originals authenticated.
Semantic judgments still come from the caller. No numeric comparator for CMMI levels.

The server binds all old packet/source/passage IDs and hashes internally, preserves
separate record/publication dates, and rejects partial or changed resubmissions.
Identical submissions replay the stored result. State is bounded in-process memory
(default 30 minutes, 200 records, 2 MiB combined across review stores), not a database;
frontend reconnection preserves it only while the same owner and TTL survive. Failed
prepare/submit rolls back its changes. A new backend loses old review IDs. It never
fetches material to repair an unavailable review.

### Manual upgrade of the existing mtest installation

The build does not upgrade or restart your active 0.8.2 backend. Save its ledger/logs
before stopping it; old review IDs will become unavailable. With the existing installed
dependencies, run:

```sh
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --status
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --stop
/Users/rishit/Desktop/mtest/.venv/bin/python -m pip install --no-deps --force-reinstall /Users/rishit/Desktop/margin/margin-mcp/releases/0.9.0/margin_research-0.9.0-py3-none-any.whl
MARGIN_BHARATSTOCK_REQUESTS=0 MARGIN_DRISHTI_REQUESTS=0 MARGIN_DRISHTI_CREDITS=0 /Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --mode live --record-dir /Users/rishit/Desktop/mtest/logs
```

Keep that terminal running. Local supplied-text review needs no keys or subscription.
Set the LM Studio MCP entry to:

```json
{
  "mcpServers": {
    "margin": {
      "command": "/Users/rishit/Desktop/mtest/.venv/bin/margin-mcp",
      "args": ["--backend-socket", "/Users/rishit/Desktop/mtest/shared/core.sock", "--mode", "live", "--tool-profile", "review-simple"]
    }
  }
}
```

Reconnect the MCP and start a fresh chat. Status must report package_version=0.9.0,
tool_profile=review-simple, advertised_tools=3, recording_enabled=true and zero HTTP
attempts. Disconnected/unconfigured providers do not block these local review actions.
The initialization instructions carry the flow; a custom skill/preset is optional.
Use the complete task/text in [the acceptance prompt](review-workflows.md#two-step-model-acceptance-090).
A frontend-only profile switch preserves a matching shared owner's state; it is not an
authorization boundary. Full mode remains appropriate for finance/retrieval.

Historical 0.8.2 baseline: 35 full-profile tools exposed the existing
37 retrieval/finance and ten review functions. Six common calculations now have directly
advertised strict schemas. The core, CLI and workbench remain available independently.
The [architecture](design/mcp-aggregation.md) owns the plan published before this change;
[implementation](implementation.md) owns evidence and limitations.

## Professor demonstration through the installed MCP

The repo-only scripts/demo_mcp_review.py is an official-SDK client for the existing
zero-budget shared backend. It neither launches/restarts that backend nor changes the
wheel, credentials or allowance. The prepared local input uses saved real INFY provider
text and **explicit operator-supplied** claim/sentiment judgments. It demonstrates tool
execution, quote/reference checks, unsupported-claim handling and aggregation, not
model selection, fresh retrieval or independent source authentication.

With the current 0.8.2 backend running, from this repo:

```sh
/Users/rishit/Desktop/mtest/.venv/bin/python scripts/demo_mcp_review.py \
  --backend-socket /Users/rishit/Desktop/mtest/shared/core.sock \
  --input reports/private/professor-demo-2026-11-26/input.json
```

The known wrong-quote variant should stop with quote_mismatch and exit nonzero:

```sh
/Users/rishit/Desktop/mtest/.venv/bin/python scripts/demo_mcp_review.py \
  --backend-socket /Users/rishit/Desktop/mtest/shared/core.sock \
  --input reports/private/professor-demo-2026-11-26/bad-quote.json
```

Each run creates a fresh private reports/private/professor-demo-* directory containing
result.json on success, normalized tool observations and frontend stderr. Backend tool
events have an explicit Professor demo why/reviewer label; exclude them from model trials.
The real input files are intentionally ignored and available only in this workspace.
Other installations must supply their own authorized source/annotations; the script's
--help and fictional software tests describe the format. It refuses missing input and
nonzero provider allowances, validates advertised schemas and stops on failed calls.
An incomplete claim-support audit is expected when every claim is assessed but one
lacks evidence. No sentiment outcome is inferred by the script: its label comes from
the operator input and is transparently submitted/aggregated by Margin.

## Registration robustness (0.8.2)

Plain URL anchors on source URLs/passage locators normalize with safe
input_normalizations receipts; exact passage text/IDs remain unchanged. Credentials,
signatures, encoded/nonplain fragments and other text changes remain rejected. Raw URL
whitespace/control characters are invalid; plain page labels remain supported. No
sanitization parameter is required. Error paths use schema-owned names without values.

assessment_coverage separates submission completeness from successful read/render
operations. Audit status_meaning explains why a fully assessed but insufficient or
contradicted claim keeps audit incomplete. Coverage never authenticates originals or
establishes market sentiment. Numeric checking remains financial-only; maturity or
certification levels use passage review, without fabricated financial units/basis.
See [workflow details](review-workflows.md#registration-and-result-interpretation-082).

## Optional citation protocol (0.8.1)

Citation review is available when the task needs claim/source support; it is not a
prerequisite for ordinary retrieval or math. Discovery/preparation return
citation_protocol guidance outside frozen packet hashes. Optional
host_profile.host_read_sources declares actual host reader access; host_search does
not imply it, and absent means unknown. Declared capability is not competence proof.
A no-reader host can review supplied passages. Without passages, report insufficient
or inventory-only; structured_assessment=false still prohibits semantic submissions.
If originals are needed, an actually available host reader may read/register exact
original passages and prepare a new packet. Margin does not fetch, run an LLM or
independently authenticate originals. See [protocol/fallbacks](review-workflows.md#optional-citation-protocol-and-host-capability)
and [goal-only host tests](review-workflows.md#next-tests-and-unguided-acceptance).

## Skills and host system prompts

The repo's [Margin skill](../skills/margin-research/SKILL.md) supplies procedural guidance
for hosts supporting skills; the MCP remains the callable interface. Connecting an MCP
does not automatically install/load that skill. Attaching a Markdown file supplies text
only if the host actually includes it; do not assume native skill discovery in every app.
The existing skill also has a CLI bridge for compatible coding agents, which is a
different execution condition from directly using the MCP tools.

For LM Studio, a compact reusable system-prompt preset is an optional alternative.
[LM Studio presets](https://lmstudio.ai/docs/app/presets) can bundle system text and
generation settings. Append this guidance to the host's existing instructions rather
than replacing its unrelated rules:

```text
Margin MCP is available for Indian financial research and auditable review tasks.
Choose its tools from the user's goal and their current advertised schemas.
If the task, issuer, claims, source text or required context is missing, ask for it;
do not invent a sample task, source URL, financial value, quote or record identifier.
For requested Margin review records, follow returned workflow guidance and use actual
tool references. Include supplied source text as passages when registering it;
metadata-only registration cannot support quote checks. Reuse returned source,
passage and packet references. Report completion only after successful results confirm it.
Preserve incomplete/error outcomes, units, dates and source-verification limitations.
Keep citation review optional for ordinary retrieval/math. Make provider calls only
within the user's authorized scope and configured allowance. Use brief action summaries.
```

This is a proposed preset, not an installed configuration or tested improvement. Keep
the complete user task/source material in the test prompt; a system instruction cannot
supply missing research input. Record MCP-only, preset and skill conditions separately.
Source/quote checks validate supplied material; they cannot authenticate invented host
text. Consult the [delivery review](design/mcp-aggregation.md#instruction-delivery-review-26-november-2026)
for observed primary-source examples and evaluation limits.

## Typed review tools, profiles and packet handoffs

Use each tool's exact host-advertised inputSchema at the top level. No function/
arguments wrapper is needed. These schemas are copied from protocols.schemas.SCHEMAS;
the underlying ten functions and generic margin_review remain available in full mode.

| Typed tool | Core function |
| --- | --- |
| margin_review_workflows | protocols.list_workflows |
| margin_register_sources | evidence.register_sources |
| margin_prepare_verification | evidence.prepare_verification |
| margin_submit_assessment | evidence.submit_assessment |
| margin_render_citations | evidence.render_citations |
| margin_audit_answer | evidence.audit_answer |
| margin_check_numeric_claim | evidence.check_numeric_claim |
| margin_prepare_sentiment | sentiment.prepare_analysis |
| margin_submit_annotations | sentiment.submit_annotations |
| margin_aggregate_sentiment | sentiment.aggregate |

Citation preparation takes claims with existing source_ids. Sentiment preparation
takes source_ids, issuer, aspect, flat from/to and date_basis—not raw text/window.
Neither preparation accepts invented packet refs. Follow returned next_steps:
select mcp_execution.tool, merge bound_arguments with required_host_fields, then
validate against that tool's schema. is_complete_input=false means a partial binding,
not an executable request. Host reviewer/judgments/quotes and actual final claim_ids
remain caller input. Preparation returns real packet_id/hash; they are not run IDs.
Hints are response metadata outside the frozen packet hash, not a stored assessment.
Inventory-only profiles point to render/aggregate without manufacturing judgments.
Packet expires_at concerns TTL; original_document_verified concerns authenticity.

Review errors now distinguish JSON/size failures, content requiring sanitization and
schema mismatch. A schema error identifies missing/allowed fields without claiming
credential misuse or echoing arbitrary caller keys/values. All quote/hash/source,
capability, TTL/capacity and no-refetch guards remain. Margin still runs no LLM.

`margin-mcp --tool-profile all` is the default full surface. For a local review stage,
add `--tool-profile review` to the **frontend** command, standalone or shared. It
advertises 14 tools: the ten above plus status/catalog/result/review_sources; no
provider connect/run, retrieval previews, finance or generic margin_review. Catalog
is scoped to review and all means all review functions. Function names are labels,
not callable aliases; unknown/hidden tools fail before forwarding. This is a frontend
view, not an authorization boundary; other full clients retain the same owner/budgets.

Example LM Studio shared frontend arguments after a version-matched upgrade:

```json
[
  "--backend-socket", "/Users/rishit/Desktop/mtest/shared/core.sock",
  "--mode", "live",
  "--tool-profile", "review"
]
```

Change only frontend profile/reconnect to preserve the same backend's source/packet
state (subject to TTL); do not restart the backend to switch profiles. Upgrading an
older backend to 0.8.2 still requires a deliberate restart and loses old handles.
Review mode can register host-supplied real text or read/import already retained
results without provider keys or requests. It never fetches missing/expired sources.
Status data.tool_profile and advertised_tools describe the frontend view, separate
from package_version/contract_version. Backend recording stores underlying calls;
frontend profile projections/instructions, host parse failures, hidden reasoning and
final prose are not recorded there. Outer tool-schema rejections can occur before
recording too; capture caller-side results when evaluating failures.

Historical 0.8.0 tools/list JSON bytes: full 35 tools 82,930; review 14 tools 29,088,
51.40% below 0.7.0's 59,853. This is uncompressed byte size, not token/context fit or
proof of model improvement. The guided 0.8.0 host round trip passed; unguided
0.8.1 model acceptance remains separate.

## Typed retrieval previews and exact schema authority

Prefer these local planning tools for the common event paths:

| Tool | Reviewed core operation | Inputs |
| --- | --- | --- |
| margin_preview_news | drishti.get_news | Query fields at tool top level |
| margin_preview_announcements | drishti.get_announcements | Query fields at top level; extraction=false |
| margin_preview_earnings | drishti.list_earnings | Query fields at tool top level |
| margin_preview_earnings_filing | drishti.get_earnings_filing | Actual earnings_id OR symbol + discovered quarter |

**Use the exact schema supplied by the server.** Typed calls use that tool's
`tools/list` inputSchema: do not add query, arguments or operations wrappers. Schemas
are already advertised by the host; tools/list is protocol discovery, not an additional
callable Margin tool. Schemas
are generated from reviewed `Registry.specs`, sourced from the packaged Drishti
contract snapshot with Margin's admission restrictions. The adapter constructs the
core query wrapper. All selector/window/page/limit, readiness, cost and schema guards
remain; preview never connects, refreshes or fetches automatically.

Generic `margin_preview` remains compatible. Before constructing one, obtain the
selected exact operation schema through `margin_catalog` with its name and
include_schemas=true. Preserve that schema's nesting, including arguments.query
where required. Reuse an already inspected current schema; do not load every schema,
guess from examples/memory, or substitute the upstream provider's broader input rules.
Catalog `mcp_execution` still describes generic binding; `direct_preview` identifies
the flat alternative and its own tools/list schema authority. Live metadata changes
cannot silently replace reviewed contracts; changed operations stay held.

Example typed local preview (after explicit connection if needed):

```json
{
  "symbols": ["INFY"],
  "from": "2026-11-10",
  "to": "2026-11-25",
  "page": 1,
  "limit": 1,
  "include_extracted_information": false,
  "why": "Preview one summary announcement without fetching data."
}
```

Pass it to `margin_preview_announcements`; execute only the resulting plan through
the existing margin_run/session/idempotency workflow. Unknown fields remain rejected.
Retrieval errors now name schema-owned missing/allowed fields (such as missing query)
without echoing unknown caller names/values. `margin_status.data.package_version`
identifies software; envelope.contract_version remains margin.mcp.v1.

Tradeoff: tools/list measured 59,853 JSON bytes versus 47,721 for 0.6.2 (+25.42%).
These are uncompressed byte counts, not host-tokenizer/context guarantees. Smaller
models still need sufficient context; actual behavioral improvement needs a new
user-led host test. No live install/restart is performed by publishing this patch.

## Company finance without previous results

Prefer `margin_company_finance` for ticker-based financial questions. It fetches fresh
BharatStock financials, prepares facts and calculates internally. No database or prior
result/fact handle is required. `execute` defaults false: a local preview. To execute
within the user's authorized scope, call the same tool with these top-level arguments:

```json
{
  "function": "finance.company_margins",
  "ticker": "HINDUNILVR",
  "exchange": "NSE",
  "period_type": "annual",
  "basis": "consolidated",
  "execute": true,
  "idempotency_key": "hul-annual-margin-test-001",
  "why": "Fetch one annual financials page and calculate the continuing-profit margin."
}
```

This is one maximum BharatStock request, zero Drishti calls/credits. Nine existing
company functions are supported: margins, profitability, balance-sheet metrics,
cash conversion, cash-flow metrics, growth, CAGR, TTM and data readiness. Use their
exact `finance.company_*` identifiers advertised in the tool schema. Defaults: NSE,
consolidated, annual (quarterly for TTM), revenue for growth/CAGR/TTM. No automatic
DCF forecasts or FCFF assumptions. Explicit-input calculators remain local.

Each new key fetches page 1 fresh, up to two annual or eight quarterly rows, even if
other retained financial sources exist. Basis is selected locally; more pages are not
fetched to resolve insufficient history, mixed bases or missing cash flows. Growth/CAGR
need two eligible endpoints; TTM needs four comparable quarterly flows and established
duration. Read partial components and scope holds; a subscription cannot create absent
issuer fields. The returned `report` contains canonical structured rows; source timestamps, caveats and `usage` remain. Raw calculation details
are optional as described below. No full provider payload is returned or added to
retained financial buffers.

The call waits at most 30 seconds. If `status` is `running`, repeat the SAME financial
inputs and key to wait/read; `wait_seconds` and `include_details` may be changed. If a reply was lost,
also reuse that key. A new key means a new request, not a recovery. Conflicting inputs
are rejected. Up to 200 compact responses/control records (or smaller `max_records`)
remain in memory, each at most 32 KiB; keys never silently expire into a new fetch.
At capacity, new requests are blocked. This protects duplicates within one core process
only. Backend restart loses that protection and does not renew account quota. A hosted
multi-worker service needs separate shared quota/request control, not a financial corpus.
Optional private logs can retain compact tool outputs; the new response is not a raw
source handle usable by `margin_facts` or `margin_result`. Legacy tools keep their buffers.

For a fresh model benchmark, current public guidance is BharatStock Developer at
INR 1,500/month before tax, with internal model evaluation and full history. Ordinary
on-demand querying is permitted on any plan within entitlements; Free's advertised
60/day does not establish this older 25/day key's quota. No Drishti purchase is needed
for this tool. See the dated [plan and subscription sources](design/fetch-and-calculate.md).
The user has now activated 0.6.1: the latest INFY execution/details read used B1/D0
and confirmed the formula patch. The backend's local B1 allowance is spent. This
validation made no extra operator fetch; source facts remain unverified. Follow the version-matched upgrade guidance below
and reconcile remaining allowances before any controlled cutover.

## Reporting contract v2 and migration

**0.6.1 formula correction:** read each row's own `formula`. Absolute change is
`current - previous`; percentage change is `(current - previous) / previous * 100`.
Raw comparison `details.values.formulas` maps each metric explicitly. The legacy
`details.values.formula` is retained as the percentage formula for compatibility;
do not apply it to every output. CAGR's elapsed-years row has no CAGR result formula.
Other standalone/grouped results use their own reviewed formulas. No arithmetic/unit
change or new fetch is involved. Cached answers in an already-running 0.6.0 backend
remain unchanged; this patch requires a deliberate version-matched upgrade.

Package 0.6.0 changes only the company convenience response shape, now explicitly
`response_version: margin.company_finance.v2`. The outer MCP envelope remains v1;
there are still 21 tools and no new dependency or model inference. The pure explicit-
input calculations and legacy retrieval/retained-source workflows are unchanged.

- Default: `report.rows`, explicit period/readiness metadata. Scale guidance lives in
  tool descriptions rather than repeated result prose.
  No generated summary or Markdown table.
  Row `value` is an exact decimal string in the SAME `unit` as its `display`.
  Statement amounts and calculated money use INR_crore, per-share amounts
  INR_per_share, percentages percent, ratios ratio, elapsed years years. Display
  rounding uses Decimal ROUND_HALF_EVEN, two decimals (six for elapsed years).
- Growth includes a ready-formatted absolute change; CFO-minus-capex, borrowings,
  working capital and TTM are formatted by reviewed units too. Missing/unknown units
  stay unavailable; zero is not missing. Partial/scope-held components remain visible.
  Comparison endpoints are labelled as period ends, never fabricated fiscal starts.
- Use the row displays without rescaling, preserving warnings, definitions,
  basis and dates. Unknown starts remain unknown; source figures remain unverified.
- For inspection add `include_details: true` to the SAME financial inputs/key. Raw
  `inputs`, exact calculation `values`, components, formulas and precision are now
  under `details`. This is a response projection and consumes no additional request.
  Consumers of old top-level values must migrate to `details.values` explicitly or
  use the canonical reporting rows. Never mix raw-INR detail values with crore rows.
- The bounded request record stores report plus compact details, at most 32 KiB.
  It still does not retain the full provider response. Reports contain structured rows only, without duplicated rendered prose/table.
  Payload size is measured in the private saved-response checks; byte counts do not
  establish a host tokenizer/context guarantee.

Point 4, host-enforced final-claim validation/direct rendering, is deferred. It is not
needed to use this repair. A host/model can still rewrite a correct report; there is
no automatic final-prose interception or hidden verifier. Original-source verification
is also separate. See [plan and boundaries](design/fetch-and-calculate.md).

## Install

Python >=3.12. Install the versioned wheel into a dedicated environment, or install the
checkout for development with `.venv/bin/python -m pip install -c requirements-dev.lock -e .`.
Console commands are `margin-mcp`, `margin-backend`, and the existing `margin-agent` and
optional `margin-workbench`. No new package dependency is required for shared mode.
The package is not yet published to PyPI; use the local wheel or checkout.

### Package distribution and hosting

Recommendation checked 26 November 2026: **PyPI first for this Python implementation**,
using the existing wheel/console entry points; uvx provides an isolated launcher for
MCP hosts. Package name and command name differ, so use --from. After publishing our
release under a confirmed available name, the proposed launcher is:

```sh
uvx --python 3.12 --from 'margin-research==0.8.2' margin-mcp --tool-profile review
```

This is a future publication example, not a claim that our package/name is available
on PyPI now. Keep full/shared installations version-matched. For repeatable local
state-owning backend use a pinned persistent installation as documented above; a
launcher does not automatically start/retain the shared backend or configure keys.

npm/npx would suit a JavaScript implementation or a deliberately maintained launcher
wrapper. For Margin it would add a second packaging/runtime layer around the existing
Python code; defer it unless users need npx specifically. Package distribution and a
future hosted MCP endpoint are separate delivery options and can coexist.

Before public publication, confirm package ownership/name/metadata/license, validate
clean installs, rehearse on TestPyPI, then publish the selected version to PyPI. No
registry upload/account action is performed by this recommendation. References:
[Python packaging/publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[uv tool execution/version pinning](https://docs.astral.sh/uv/guides/tools/),
[npx behavior](https://docs.npmjs.com/cli/v11/commands/npx/).

The current tested 0.8.2 wheel is committed at
[`releases/0.8.2/margin_research-0.8.2-py3-none-any.whl`](../releases/0.8.2/margin_research-0.8.2-py3-none-any.whl),
with [`SHA256SUMS`](../releases/0.8.2/SHA256SUMS). Earlier tested 0.6.1/0.6.2/0.7.0/0.8.0/0.8.1 artifacts
remain in their versioned directories with original checksums. Keep release artifacts immutable and publish
a new package version for later runtime changes. Generated `dist/` outputs remain
ignored; only deliberately reviewed versioned release files belong in Git.

From the repository root, verify the committed artifact before installation:

```sh
(cd releases/0.8.2 && shasum -a 256 -c SHA256SUMS)
```

The wheel contains no provider keys or private captures. Credentials/configuration
remain separate. Offline regression and installed-wheel SDK acceptance are separate
from a clean cross-platform installation or real model-host acceptance.

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

For a controlled upgrade to 0.8.2, inspect/save the old ledger and logs, stop the
old backend with its existing executable, then install the new wheel into that venv:

```sh
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --stop
/Users/rishit/Desktop/mtest/.venv/bin/python -m pip install --no-deps --force-reinstall /Users/rishit/Desktop/margin/margin-mcp/releases/0.8.2/margin_research-0.8.2-py3-none-any.whl
```

These are manual instructions, not actions performed during this build. Existing pinned
dependencies are reused. Restart explicitly using the backend command above only
after setting reconciled remaining provider allowances; do not copy the old allowance
as if nothing was spent. With no confirmed requests remaining, set the BharatStock
allowance to zero and test only local actions (including review). Both backend and frontend must be 0.8.2;
reconnect the host after the version-matched restart. No provider key belongs in commands.

## Tools and financial output

`margin_company_finance` is the fresh-fetch convenience tool above. Company catalog
entries also advertise its `fresh_mcp_execution` route; legacy `mcp_execution` remains.

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

0.6.2 expands `margin_review_sources` to four retained Drishti shapes: news, summary
announcements, earnings discovery and single earnings detail. It imports supplied
summaries/attachment locators, preserving original protected-link flags and row-symbol/
path provenance. It never reads attachments or infers publication dates/relevance.
Unknown shapes/explicit issuer mismatches remain incomplete/skipped. See the
[one-source host test](review-workflows.md#small-model-acceptance-after-activation).

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
