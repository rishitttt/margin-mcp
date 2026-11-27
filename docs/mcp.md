# Run Margin locally

Version0.10.0, Python>=3.12. Use the committed wheel; publishing to PyPI or deploying a remote server is separate. all is the default supported profile (39 tools). finance6, review16 and review-simple3 are optional, not authorization boundaries.

## Install

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install /absolute/path/margin_research-0.10.0-py3-none-any.whl
```

On Windows use .venv\Scripts\python.exe and standalone mode. No npm installation is required for Margin. Workbench is optional: install the wheel with its workbench extra. [Clean-install/platform evidence](release-checks.md).

## Standalone stdio

Configure the MCP host command as the absolute installed margin-mcp executable, with:

```json
["--mode", "live", "--credentials-file", "/absolute/private/providers.env", "--record-dir", "/absolute/private/logs", "--tool-profile", "all"]
```

Set MARGIN_BHARATSTOCK_REQUESTS, MARGIN_DRISHTI_REQUESTS and MARGIN_DRISHTI_CREDITS in the host environment to a newly allocated remaining allowance. Use zero for preview/local-only checks. The credentials file contains only provider env values, parsed as data; never pass keys through tool arguments or prompts. Logging is optional; new files are private and never overwritten. stdout is protocol-only.

## Shared backend on macOS/Linux

Start the owner explicitly with confirmed remaining allowances, e.g. zero-provider testing:

```sh
MARGIN_BHARATSTOCK_REQUESTS=0 MARGIN_DRISHTI_REQUESTS=0 MARGIN_DRISHTI_CREDITS=0 /absolute/venv/bin/margin-backend --socket /absolute/private/core.sock --mode live --credentials-file /absolute/private/providers.env --record-dir /absolute/private/logs
```

Keep it running. MCP frontend command is the installed margin-mcp, with:

```json
["--backend-socket", "/absolute/private/core.sock", "--mode", "live", "--tool-profile", "all"]
```

Backend/frontend package versions must match. Frontend reconnect/profile changes preserve the same owner/allowance; owner restart loses transient handles and duplicate protection. It does not renew provider quota. Unix socket directories must be private and paths short. Windows uses standalone mode; no Unix-backend parity claim.

## Upgrade the current mtest installation

The product build does not change your active0.9.5 owner. Save logs (currently logs~) before stopping it. Do not reuse a spent allowance.

```sh
/Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --stop
/Users/rishit/Desktop/mtest/.venv/bin/python -m pip install --no-deps --force-reinstall /Users/rishit/Desktop/margin/margin-mcp/releases/0.10.0/margin_research-0.10.0-py3-none-any.whl
MARGIN_BHARATSTOCK_REQUESTS=0 MARGIN_DRISHTI_REQUESTS=0 MARGIN_DRISHTI_CREDITS=0 /Users/rishit/Desktop/mtest/.venv/bin/margin-backend --socket /Users/rishit/Desktop/mtest/shared/core.sock --mode live --credentials-file /Users/rishit/Desktop/mtest/.env --record-dir /Users/rishit/Desktop/mtest/logs
```

Keep the existing frontend command/args with --tool-profile all, reconnect and load your model. Status should show0.10.0/all39/recording enabled and local B0D0. Fresh schema discovery occurs on reconnect; old conversations may retain old tool definitions.

## Tool flow

- Status is local: copy report rows. Ledger is local HTTP/estimated-credit admission, not account balance. include_diagnostics=true adds capacities/receipt count/historical snapshots under diagnostics; those are not quotas. Core/workbench status compatibility remains.
- Ticker finance: margin_company_finance(function,ticker,execute=false) previews. Cross-group eligibility: typed margin_company_data_readiness(ticker,execute=false), no selector. Stop for preview-only tasks. Later authorized execute=true plus stable key fetches at most B1/D0 and returns calculations. Same intent/key across typed/generic routes replays; changed intent conflicts.
- Readiness output: report.readiness/report.valuation_readiness, not numeric report.rows. Numeric company results use exact report.rows displays and scope holds. No missing value becomes zero; no inferred dates/forecasts.
- Local DCF: margin_calculate_dcf takes the exact advertised top-level inputs. It requires explicit future FCFF and assumptions; CFO is not FCFF, total liabilities are not reviewed debt. report distinguishes undiscounted terminal value from present value. [Report contract](product-reports.md).
- Generic retrieval: preview exact operations, then margin_run using an actual returned plan/session/key; inspect run/result. Typed event previews avoid query-wrapper guessing. Drishti metadata connection is explicit/metered; metadata is not entitlement. No automatic retries, extra pages or source fallback.
- Reviews: prefer margin_prepare_review then margin_submit_review for supplied text; host supplies judgments. Advanced citation/sentiment primitives remain. Follow [review protocol](review-workflows.md); missing reader/text means an explicit fallback, not fabricated verification.

Function identifiers in the catalog are not callable tools. Use actual mcp_execution routes and exact schemas; inspect one selected schema, not all schemas to count tools. Status already returns the advertised tool count. All results preserve source limitations; Margin has no LLM/browser or original-authentication service.

## Tests and release

[Live checks](api-testing.md), [canonical report contracts](product-reports.md), [installation/SDK checks](release-checks.md), [actual status](implementation.md), [function tests](finance-agent-tests.md).

The complete previous guide is [archived](archive/2026-11-27-docs-mcp.md). Historical anchors below link to their dated setup, not current commands.

## Historical section links

<a id="run-margin-as-a-local-mcp-server"></a>[Historical: Run Margin as a local MCP server](archive/2026-11-27-docs-mcp.md#run-margin-as-a-local-mcp-server)

<a id="typed-readiness-and-dcf-095"></a>[Historical: Typed readiness and DCF (0.9.5)](archive/2026-11-27-docs-mcp.md#typed-readiness-and-dcf-095)

<a id="upgrade-while-keeping-all"></a>[Historical: Upgrade while keeping all](archive/2026-11-27-docs-mcp.md#upgrade-while-keeping-all)

<a id="compact-finance-profile-094"></a>[Historical: Compact finance profile (0.9.4)](archive/2026-11-27-docs-mcp.md#compact-finance-profile-094)

<a id="upgrade-and-test-with-zero-provider-allowance"></a>[Historical: Upgrade and test with zero provider allowance](archive/2026-11-27-docs-mcp.md#upgrade-and-test-with-zero-provider-allowance)

<a id="optional-local-model-api-harness"></a>[Historical: Optional local model API harness](archive/2026-11-27-docs-mcp.md#optional-local-model-api-harness)

<a id="finance-handoffs-and-readiness-093"></a>[Historical: Finance handoffs and readiness (0.9.3)](archive/2026-11-27-docs-mcp.md#finance-handoffs-and-readiness-093)

<a id="manual-zero-request-upgrade-and-test"></a>[Historical: Manual zero-request upgrade and test](archive/2026-11-27-docs-mcp.md#manual-zero-request-upgrade-and-test)

<a id="live-finance-acceptance-092"></a>[Historical: Live finance acceptance (0.9.2)](archive/2026-11-27-docs-mcp.md#live-finance-acceptance-092)

<a id="no-fabrication-guidance-091"></a>[Historical: No-fabrication guidance (0.9.1)](archive/2026-11-27-docs-mcp.md#no-fabrication-guidance-091)

<a id="two-step-review-090"></a>[Historical: Two-step review (0.9.0)](archive/2026-11-27-docs-mcp.md#two-step-review-090)

<a id="manual-upgrade-of-the-existing-mtest-installation"></a>[Historical: Manual upgrade of the existing mtest installation](archive/2026-11-27-docs-mcp.md#manual-upgrade-of-the-existing-mtest-installation)

<a id="professor-demonstration-through-the-installed-mcp"></a>[Historical: Professor demonstration through the installed MCP](archive/2026-11-27-docs-mcp.md#professor-demonstration-through-the-installed-mcp)

<a id="registration-robustness-082"></a>[Historical: Registration robustness (0.8.2)](archive/2026-11-27-docs-mcp.md#registration-robustness-082)

<a id="optional-citation-protocol-081"></a>[Historical: Optional citation protocol (0.8.1)](archive/2026-11-27-docs-mcp.md#optional-citation-protocol-081)

<a id="skills-and-host-system-prompts"></a>[Historical: Skills and host system prompts](archive/2026-11-27-docs-mcp.md#skills-and-host-system-prompts)

<a id="typed-review-tools-profiles-and-packet-handoffs"></a>[Historical: Typed review tools, profiles and packet handoffs](archive/2026-11-27-docs-mcp.md#typed-review-tools-profiles-and-packet-handoffs)

<a id="typed-retrieval-previews-and-exact-schema-authority"></a>[Historical: Typed retrieval previews and exact schema authority](archive/2026-11-27-docs-mcp.md#typed-retrieval-previews-and-exact-schema-authority)

<a id="company-finance-without-previous-results"></a>[Historical: Company finance without previous results](archive/2026-11-27-docs-mcp.md#company-finance-without-previous-results)

<a id="reporting-contract-v2-and-migration"></a>[Historical: Reporting contract v2 and migration](archive/2026-11-27-docs-mcp.md#reporting-contract-v2-and-migration)

<a id="package-distribution-and-hosting"></a>[Historical: Package distribution and hosting](archive/2026-11-27-docs-mcp.md#package-distribution-and-hosting)

<a id="choose-the-state-owner"></a>[Historical: Choose the state owner](archive/2026-11-27-docs-mcp.md#choose-the-state-owner)

<a id="shared-backend-start-once"></a>[Historical: Shared backend: start once](archive/2026-11-27-docs-mcp.md#shared-backend-start-once)

<a id="lm-studio--host-configuration"></a>[Historical: LM Studio / host configuration](archive/2026-11-27-docs-mcp.md#lm-studio--host-configuration)

<a id="tools-and-financial-output"></a>[Historical: Tools and financial output](archive/2026-11-27-docs-mcp.md#tools-and-financial-output)

<a id="normal-workflow-and-guards"></a>[Historical: Normal workflow and guards](archive/2026-11-27-docs-mcp.md#normal-workflow-and-guards)

<a id="recording-and-review-handoffs"></a>[Historical: Recording and review handoffs](archive/2026-11-27-docs-mcp.md#recording-and-review-handoffs)

<a id="validation-and-limitations"></a>[Historical: Validation and limitations](archive/2026-11-27-docs-mcp.md#validation-and-limitations)

<a id="historical-host-debug-observations"></a>[Historical: Historical host-debug observations](archive/2026-11-27-docs-mcp.md#historical-host-debug-observations)

<a id="lm-studio-catalog-routing-repair-031"></a>[Historical: LM Studio catalog-routing repair: 0.3.1](archive/2026-11-27-docs-mcp.md#lm-studio-catalog-routing-repair-031)

<a id="financial-input-diagnostics-032"></a>[Historical: Financial input diagnostics: 0.3.2](archive/2026-11-27-docs-mcp.md#financial-input-diagnostics-032)

<a id="repeated-chat-startup-repair-033"></a>[Historical: Repeated-chat startup repair: 0.3.3](archive/2026-11-27-docs-mcp.md#repeated-chat-startup-repair-033)

<a id="real-retrieval-versus-answer-accuracy"></a>[Historical: Real retrieval versus answer accuracy](archive/2026-11-27-docs-mcp.md#real-retrieval-versus-answer-accuracy)
