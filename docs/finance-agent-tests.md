# Test finance discovery through Margin

**0.9.1 patch after the first model baseline:** full 0.9.0 discovery failed: wrong
annual-TTM choice, then invented amount/date in malformed manual calculator JSON.
No provider data call occurred. Qwen3-8B context 30,183; reported last-generation prompt
17,611/generated496 does not establish context overflow. Preserve the original trial.
Source 0.9.1 adds explicit no-fabrication policy and growth-vs-TTM/company-first guidance;
no new profile or guaranteed behavior change. [Manual upgrade](mcp.md#no-fabrication-guidance-091),
then repeat the identical goal-only prompt as a separate experimental condition. Keep
model/preset/context/profile fixed and record first attempts. Old task/rubric baseline
labels remain 0.9.0; record actual installed version for each new run.

Current baseline: package 0.9.0, full profile (`all`), 37 advertised tools. No new wheel
is needed. Review profiles intentionally hide BharatStock/finance execution. MCP hosts
receive the advertised schemas and initialization guidance; the model still decides
whether to call a tool and how well to follow that guidance. That is the behavior under
test, not an MCP guarantee.

## What is already available

- Six BharatStock retrieval operations: search_stocks, get_stock_quote,
  get_stock_fundamentals, get_financials, get_stock_prices and get_corporate_actions.
  Catalog exposure does not establish access to every endpoint.
- Nine company finance workflows: data readiness, margins, revenue/other metric growth,
  CAGR, TTM, cashflow metrics, profitability, cash conversion and balance-sheet metrics.
  The fresh-company tool fetches at most one financials page and computes internally;
  it needs no prior source/fact handle. Defaults are preview-only; execution needs a
  stable request key. Same inputs/key replay; a new key can fetch again.
- Fifteen explicit-input calculation functions, including supplied-assumption valuation.
  These are local and do not discover company forecasts. DCF requires explicit inputs.

Full catalog entries give descriptions and exact operation schemas. Company entries
retain the legacy mcp_execution route for retained data and expose fresh_mcp_execution
for the preferred fresh-fetch tool. Its actual tools/list schema is authoritative;
legacy planning_schema fields such as fetch_missing are not fresh-tool inputs. Function
identifiers are selectors, not callable tool names. Generic raw retrieval needs exact
catalog schema nesting and preview → run → result. Do not turn a successful preview
into a claim that data has been retrieved.

## Immediate no-call model test

Change the Margin frontend args from --tool-profile review/review-simple to:

```json
"--tool-profile", "all"
```

Reconnect only the frontend; keep the current backend running. Open a fresh chat with
Margin enabled. No key, allowance or backend restart is needed to inspect local catalog:

```text
Use the connected Margin MCP to inspect the financial capabilities available to you.
Even if live retrieval is unavailable, discover which capability fits a question about
Infosys annual consolidated revenue growth. Explain its purpose, the inputs needed,
and the maximum provider calls it would require. Do not fetch data or invent values.
Give a brief visible explanation for your tool choices.
```

Expected: identify the relevant company capability from actual discovery, distinguish
fresh/legacy paths and local discovery from missing live auth/quota, preserve the
one-request bound. It must not claim a financial answer or call an imagined tool.
Return expanded calls/results and final prose, including failed first attempts.

## Live model tasks and prerequisites

Use [tasks.json](../research/finance-discovery/tasks.json) one prompt per fresh chat.
Keep [rubric.json](../research/finance-discovery/rubric.json) with the reviewer, not in the
agent prompt. D00/G01–G03 use no data calls. F01–F04 need a separately authorized four-
request allowance; E01–E06 need six additional requests. Live values are not fixed gold.

The 27 November operator run already consumed its entire four-request authorization.
A still-zero active backend cannot execute these live tasks, even if the account has
requests remaining. When a new model-test allowance is confirmed, save the old ledger,
stop the owner explicitly and start a live owner with the private credentials file:

```sh
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --status
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --stop
# Set MARGIN_BHARATSTOCK_REQUESTS to the newly authorized remaining test allocation.
MARGIN_BHARATSTOCK_REQUESTS=0 MARGIN_DRISHTI_REQUESTS=0 MARGIN_DRISHTI_CREDITS=0 /Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --mode live --credentials-file /Users/rishit/Desktop/mtest/.env --record-dir /Users/rishit/Desktop/mtest/logs
```

The safe example deliberately permits zero provider attempts until the new allocation
is set. Do not repeat a spent four-request allowance or restart to rescue an expired
handle. Keys are read as data; never paste them into prompts/config tool arguments.
No paid plan was needed for the measured operator run; future account balance and
endpoint entitlement must be checked rather than inferred from those successes.

Score discovery, schema validity, budget/duplicate control, math, source scope, units,
holds and final prose separately. Capture actual model/context/preset/profile and brief
visible choice summaries; tool logs omit some host parse failures and final prose.
Do not capture hidden thinking or treat a choice explanation as privileged reasoning.

## Measured operator checks — 27 November

All nine company previews pass; all six raw BharatStock routes are discoverable.
Fourteen local discovery/preview calls leave the ledger unchanged. Live HUL margin,
INFY growth, INFY annual readiness and HUL snapshot all succeed, exactly four BharatStock
attempts, no Drishti. Exact decimal math and canonical value/unit/display checks pass
for margin/growth. Same-key repeats do not fetch again.

INFY annual readiness reports seven supported calculations; its numeric rows array is
empty by design. It still has readiness and valuation_readiness output. These are
field-eligibility results, not seven separately called company workflows. TTM requires
compatible quarterly data. Automatic DCF is unsupported without explicit assumptions.
Source originals, current account balance and autonomous model choice are unverified.

Private capture: reports/private/finance-discovery-2026-11-27/REPORT.{json,md}, live-01/.
The initial preview-01 stopped locally because the active owner had no key. It spent
zero provider requests. The configured isolated test owner was closed after its four
attempts; the user's active review owner was not changed. No model call was made.

The checkout frontend/checker must match the running backend package version.
Do not run a new 0.9.1 frontend over an old 0.9.0 owner; upgrade deliberately first.

The scripts/check_finance_discovery.py checker attaches to an existing live owner and
only permits status, catalog, preview and execute=false company calls. It stops if a
preview is held; it never repairs setup. scripts/check_finance_live.py is an explicit,
isolated four-request operator diagnostic; do not rerun without a new authorization.
Results are operator SDK evidence, not autonomous-model acceptance or issuer truth.
