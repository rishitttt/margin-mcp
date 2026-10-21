# Core and local workbench guide

This is the runnable guide for the first core/workbench build. [Implementation status](implementation.md#first-coreworkbench-build-checkpoint) owns validation evidence; [architecture](design/core-workbench.md) explains the boundaries; [source testing](api-testing.md) owns live-test budgets. Margin's own MCP server is not packaged yet.

## Install and run

Use Python 3.12 or newer. The tested dependency snapshot is Python 3.12/macOS ARM; other platforms/versions are not yet checked.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[workbench,dev]'
.venv/bin/margin-workbench --mode synthetic --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The CLI binds loopback, one worker, no reload and no access logs. Stop with Ctrl-C. Restarting clears memory, results, submissions and counters. The version snapshot constrains the current dependency closure; it has no hashes and is not a universal cross-platform lock.

Install `'.[workbench]'` for the UI without development tools, or `'.'` for the core alone. No npm/frontend build, model subscription, database or provider key is needed in synthetic mode. SDK 2.2.0's `httpx2` transport and BharatStock's standard `httpx` are intentionally separate dependencies.

## Try the workflow

1. Keep fictional `SYNTHA` / NSE, or use Search directory to choose `SYNTHB` / BSE. These are fictional issuers, never actual Reliance/TCS records. Search itself requires preview/run; typing does not fetch anything.
2. Select modules. Defaults are snapshot, quarterly financials, company news and announcements. Preview lists the exact operations and estimated credits without provider calls. Run explicitly executes that immutable plan.
3. Add EOD prices to see a local line and table. The view shows up to twenty rows, with remaining bounded rows in the sanitized payload. No automatic second page is fetched.
4. Add earnings discovery. Select “Inspect this earnings record” on a returned record to make an explicit detail run. Synthetic detail deliberately contains conflicting normalized/raw revenue and a credential-bearing URL sentinel; the UI must show the conflict and sanitized authorized-resolution locator.
5. Open “Sanitized provider payload & receipt” to inspect retained data, warnings, coverage and accounting. Restore last run after a page reload reads existing local results; it never repeats a fetch. Expired/evicted results stay unavailable until a newly previewed explicit run.

A plan contains 1–8 operations and expires after ten minutes. Repeated submission with the same key returns the same run; another plan cannot reuse that key. Separate new previews are deliberately new intent. No automatic enrichment, retries or page exhaustion occurs. Company identity, fiscal period, basis, null values and provider sentiment labels remain as supplied; chart/table formatting is not financial verification.

The initial overview bounds are four quarterly/two annual rows, up to 100 EOD rows in a default 90-day price window, five corporate actions, two news items/seven days, two announcements/30 days and two earnings summaries/365 days. These are request bounds, not completeness claims. The core permits larger reviewed limits (prices 300 rows/one year; quarterly eight rows) for explicit operations. Earnings detail is a separate action.

## Synthetic scenarios

Start a separate synthetic process/port, or stop the first one before reusing its port:

```sh
.venv/bin/margin-workbench --mode synthetic --port 8766 --scenario drishti_unavailable
.venv/bin/margin-workbench --mode synthetic --port 8767 --scenario empty_news
.venv/bin/margin-workbench --mode synthetic --port 8768 --scenario unsafe_output
```

| Scenario | Expected outcome |
| --- | --- |
| `none` | Normal fictional numeric/events workflow, staged detail conflict and URL redaction |
| `drishti_unavailable` | Failed event operations with successful BharatStock sections; partial run, no fallback data |
| `empty_news` | Explicit empty news; successful empty is not an upstream failure |
| `unsafe_output` | Unsupported opaque output is withheld, never rendered as trusted content |

Timeout/cancellation, uncertain spending, metadata drift/freshness, buffer limits and duplicate submissions are tested offline. The scenario switch is never accepted in live mode. Synthetic counters represent simulated attempts and estimated credits, not real account consumption.

## First manual live run: 21 October 2026

The user requested real API data for manual testing. The running local instance was switched to live mode with the saved trial credentials held in its environment. Startup itself makes no provider request. This does not establish that the keys remain valid or that current quotas/access are available.

This session is limited to four BharatStock HTTP attempts, 24 Drishti HTTP attempts (including connection/catalog/cleanup) and seven estimated Drishti credits. News, announcements and earnings discovery are explicitly enabled for this bounded test; directory search and corporate actions remain held. Do not rerun all previous trial calls or treat the process ceilings as current account balances.

1. Check remaining allowance/key validity in the provider dashboards first. Reload `http://127.0.0.1:8765`; confirm the LIVE badge. Enter `RELIANCE`, exchange `NSE`. Clear other modules and select Snapshot + Quarterly financials. Preview, then Run once: two BharatStock REST calls. Avoid Inspect snapshot as an additional call if snapshot is already in the plan.
2. Inspect company identity/ISIN, returned reporting period/basis and missing fields; expand the sanitized payload and receipts. A successful response does not establish numerical correctness. Stop on access, rate-limit or uncertain errors.
3. Click Connect / refresh Drishti once and wait for connected. This uses real lifecycle/catalog/schema requests and may take roughly a minute under conservative pacing. On an error, preserve the displayed error/receipt and do not repeatedly reconnect. Schema changes require review.
4. Select only Company news + Announcements, preview and Run once: two nested Drishti operations, two published estimated credits. News uses seven days; announcements 30 days; empty results can be valid. Check actual dashboard debit after the run.
5. Optional, if remaining allowance permits: run only EOD price history (one further BharatStock request). Separately run only Earnings discovery (two estimated credits); then inspect one returned earnings record (three estimated credits). Total for this full sequence: three BharatStock data calls, four Drishti data operations and seven estimated credits, plus counted Drishti lifecycle traffic. No TCS run is included yet.

Refresh/Restore reads local retained results; a new Preview/Run is new paid intent. Do not repeat an action after an uncertain result. The app measures initiated HTTP attempts but does not fetch current balances or measure actual credit debits. Report which operation failed, its safe error code and displayed counters; never share keys or unsanitized provider URLs.

### If Connect appears to do nothing

The original UI waited for the metadata POST before updating status, so the button appeared inert during paced SDK connection/schema traffic. It also allowed repeated clicks; earlier failed run cards correctly remained unchanged after connection. The repair shows Connecting/progress/connected/error text, disables duplicate clicks and polls local status, including connections started by another tab. Fresh connection checks reuse local state instead of repeating upstream discovery. Drishti Run now checks local readiness before creating a run; earlier blocked runs are never automatically replayed.

Hard-refresh the page (Cmd+Shift+R on macOS) to load the new controls. When Connected appears, select only the desired Drishti modules, preview a **new** plan and Run once. No server restart is needed to load the static UI repair. Backend sharing of concurrent Connect requests and fresh-metadata reuse is also implemented; that Python change takes effect on the next normal restart. Do not restart just to reset a low request counter. Expired metadata needs one explicit counted refresh.

This repair was checked with offline core/view regressions and local HTTP asset/status reads. In the observed user process, Drishti eventually reached connected with all seven selected schemas verified/fresh, at 23 initiated HTTP attempts and zero logical data operations. That is metadata success, not a successful data/credit-billing test. The agent did not click Connect or initiate provider/data calls during this diagnosis.

### If Drishti options show “held”

Connection/schema validation and local operation opt-in are separate. `connected` does not automatically enable previously unexecuted data shapes, and `held` is not a provider subscription rejection. The user’s first live run had successful metadata checks but an empty opt-in variable. In your own local `.env`, set:

```dotenv
MARGIN_ENABLE_OPERATIONS=drishti.get_news,drishti.get_announcements,drishti.list_earnings
```

Stop the existing server with Ctrl-C, then reload that user-authored configuration in the same repo terminal before launching:

```sh
set -a
source .env
set +a
.venv/bin/margin-workbench --mode live --port 8766
```

The app does not auto-load `.env`. Connecting alone, editing a file without restarting, or exporting variables in a different terminal does not change the running process. Existing nonsecret caps should be reviewed against actual prior spend; restarting resets local counters but not provider quotas. Refresh the page, connect once, then select only news and announcements, preview and run. This avoids repeating successful BharatStock work. Current metadata expires after five minutes, so a later live operation may need another explicit, counted refresh.

Financial display uses actual REST `period_end_date`, `fiscal_year`, `quarter`, `consolidation_type` and `net_profit` where returned. A column omitted from the view is not proof that the provider omitted it; the sanitized payload remains authoritative for returned field presence. Retained results can be reread with Refresh/Restore before restart/expiry; no refetch is needed for a presentation-only fix.

## Registry and transport map

`GET /api/capabilities` is a local snapshot of approved contracts and held reasons, not live discovery or proof of entitlement. Runtime contracts are in `src/margin/core/registry.py` and the selected `src/margin/resources/drishti-contracts.json`. The broader [25-function reference](reference/drishti-functions.md) is documentation, not a blanket executor allowlist.

| Core operation | Upstream | New runtime's live state |
| --- | --- | --- |
| `bharatstock.search_stocks` | `GET /v1/search` | Explicit opt-in; untested live shape |
| `bharatstock.get_stock_quote` | `GET /v1/stocks/{ticker}` | Historical route observed; new adapter live check pending |
| `bharatstock.get_stock_fundamentals` | `GET /v1/stocks/{ticker}/ratios` | Historical route observed; new adapter live check pending |
| `bharatstock.get_financials` | `GET /v1/stocks/{ticker}/financials` | Historical route observed; new adapter live check pending |
| `bharatstock.get_stock_prices` | `GET /v1/stocks/{ticker}/prices` | Historical route observed; new adapter live check pending |
| `bharatstock.get_corporate_actions` | `GET /v1/stocks/{ticker}/corporate-actions` | Explicit opt-in; untested live shape |
| `drishti.resolve_symbols` | Native `execute_tool` → `resolve_symbols` | Explicit opt-in; schema observed only |
| `drishti.get_symbols` | Native `execute_tool` → `get_symbols` | Explicit opt-in; schema observed only |
| `drishti.get_news` | Native `execute_tool` → `get_news` | Explicit opt-in; schema observed only |
| `drishti.get_announcements` | Native `execute_tool` → `get_announcements` | Explicit opt-in; schema observed only |
| `drishti.get_announcement_categories` | Native `execute_tool` → `get_announcement_categories` | Explicit opt-in; schema observed only |
| `drishti.list_earnings` | Native `execute_tool` → `list_earnings` | Explicit opt-in; schema observed only |
| `drishti.get_earnings_filing` | Native `execute_tool` → `get_earnings_filing` | Historical execution observed; new adapter live check pending |

BharatStock uses only `https://bharatstockapi.com` with `X-API-Key`. Drishti uses only its fixed hosted MCP endpoint with Bearer authentication. Explicit Drishti connect uses the SDK handshake/catalog and describes the seven reviewed nested schemas; it does not execute data operations. All four native wrapper contracts and selected input schemas are checked. Changed/expired metadata blocks the affected operation; it does not update the approved contract automatically.

## Live configuration and limits

The executable reads exported environment variables only. It never auto-loads `.env` or `reports/private/mcptempkeys.txt`. Keep keys local/backend-side; do not put them in browser forms, URLs, shell arguments or Git. The blank [.env.example](../.env.example) lists configuration names. Do not execute the supplied text file as a shell script.

| Variable | Default / meaning |
| --- | --- |
| `MARGIN_MODE` | `synthetic`; CLI `--mode` overrides it |
| `BHARATSTOCK_API_KEY`, `DRISHTI_API_KEY` | Empty; live operations require the corresponding exported key |
| `MARGIN_BHARATSTOCK_REQUESTS` | 20 initiated HTTP attempts per process |
| `MARGIN_DRISHTI_REQUESTS` | 30 initiated HTTP attempts per process, including SDK/lifecycle/catalog traffic |
| `MARGIN_DRISHTI_CREDITS` | 20 conservative estimated credits per process, not observed balance/debits |
| `MARGIN_ENABLE_OPERATIONS` | Empty; comma-separated full operation names explicitly approved for bounded testing of otherwise held live shapes |
| `MARGIN_SYNTHETIC_SCENARIO` | `none`; CLI `--scenario` overrides it; forbidden in live mode |

After a reviewed allowance/call plan, launch `.venv/bin/margin-workbench --mode live --port 8765`. Startup/status/preview perform no external request. “Connect / refresh Drishti” is an explicit budgeted metadata action; Drishti data calls require this connection and unexpired approved schemas. BharatStock has no MCP/catalog setup. Synthetic identifiers are rejected in live mode. Live-held modules are disabled until explicitly opted in; the synthetic default four-module overview is not automatically enabled live.

Live request pacing is at most two BharatStock attempts/second and nine Drishti attempts/minute, subject to stricter account limits. Drishti admission keeps two HTTP slots for cleanup; catalog/connect itself still needs enough headroom. Response/result caps are 2 MiB. No automatic retry, redirect-following or SSE resumption is enabled. An uncertain dispatched outcome retains its conservative estimate and holds further calls to that provider for reconciliation; cancellation is not an upstream refund.

**The app does not currently query account usage, effective subscriptions or actual credit deltas.** Its local caps do not account for other clients, past sessions or provider-specific key limits. Restarting is not permission to spend a new daily allowance. Historical balance 986 on 9 October is labelled stale. Reconcile current dashboards/account diagnostics and set smaller ceilings under the [bounded source protocol](api-testing.md) before any live pass. No purchase is needed for synthetic work; current live access/prices need fresh checking before upgrading.

## Local HTTP and direct core use

These routes are only for the loopback workbench:

| Route | Effect |
| --- | --- |
| `GET /api/status`, `GET /api/capabilities` | Local state/contracts only |
| `POST /api/provider-connections/drishti` | Explicit connection and selected schema refresh |
| `POST /api/plans` | Local validation/preview; explicit `operations` or an overview request |
| `POST /api/runs` | Execute stored plan with `plan_id` and `idempotency_key` |
| `GET /api/runs/{run_id}` | Local status/receipts |
| `GET /api/runs/{run_id}/operations/{operation_id}` | Retained sanitized result only |
| `POST /api/runs/{run_id}/cancel` | Stop queued/local work, preserving uncertain dispatched cost |

POSTs require JSON, the `action_nonce` returned by local status in `X-Margin-Action`, and a matching Origin when supplied. The server validates Host, caps request bodies at 64 KiB and serves a strict local CSP. There is no public user-auth/multitenancy layer or generic URL-fetch route.

The reusable service can run without FastAPI:

```python
import asyncio
from dataclasses import asdict
from margin.core.config import Settings
from margin.core.contracts import OperationRequest
from margin.core.service import ResearchService

async def main():
    service = ResearchService(Settings())  # synthetic, even if environment has keys
    try:
        result = await service.execute(OperationRequest(
            "bharatstock.get_stock_quote", {"ticker": "SYNTHA", "exchange": "NSE"}
        ))
        print(asdict(result))  # synthetic, sanitized result and receipt
    finally:
        await service.close()

asyncio.run(main())
```

Use `create_plan`, `start_run`, `get_run` and `get_result` for run/idempotency/buffering behavior. Direct operation execution still shares admission/evidence/accounting but is not a stored run. No future MCP adapter should call the workbench HTTP routes to retrieve data; it should use these same services.

## Retained results and evidence limits

Only sanitized payloads are held in process memory: five completed runs, 20 MiB total and a 30-minute TTL. Control/idempotency records have their own bounded capacity (200); reaching capacity blocks new work rather than silently deleting paid intent. At most five runs are active; per-provider calls serialize. Shutdown clears state. Browser session storage holds only a last-run ID. No persistent financial cache, corpus or response export is built.

Citations are locators extracted from provider output. A sanitized API locator is labelled as requiring authorized resolution. No authenticated source/PDF fetch or claim/page verification occurs. Unknown units are unknown, nulls remain missing, event ingestion dates are not relabelled publication dates, and the known raw/normalized revenue discrepancy remains visible. Synthetic success and source agreement do not establish accuracy.

## Verification

```sh
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/pytest -q
.venv/bin/python -m pip check
.venv/bin/python -m build --no-isolation
```

When Node is available, pytest also runs the actual view functions against an in-memory DOM for financial-field and held-reason regressions; this optional check skips without Node. No Node/npm toolchain is required to run the app. The default pytest fixture rejects real sockets. REST tests use `httpx.MockTransport`; MCP integration uses the real SDK against an in-process ASGI upstream; HTTP tests use an ASGI client. There is no automatic live test in the suite.

Optional browser acceptance, with the synthetic server running on port 8765 and a system Chrome/Chromium executable:

```sh
.venv/bin/python scripts/smoke_workbench.py --port 8765 \
  --browser '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --output /tmp/margin-workbench-smoke
```

Use a fresh synthetic process for repeatable counters/headroom. The script verifies mode before data actions, blocks external page requests, uses a fresh headless profile and saves fictional screenshots only when requested. Playwright is a dev dependency; no browser binary is automatically downloaded by installation. Default executable selection requires an already installed Playwright browser if `--browser` is omitted.

Known gaps: authenticated new-client compatibility/access/billing and measured live coverage; clean installation on other platforms; original-source/citation resolution; fuller output layouts; semantic transcript search; normalized comparisons; downstream Margin MCP and actual model-host evaluation. Complete the small live/source gate before expanding operations or claiming the initial pilot finished.
