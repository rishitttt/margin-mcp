# Product acceptance — 0.10.0, 27 November 2026

This is product validation, not the professor's model benchmark. Private evidence is
under reports/private/product-{live,review-final,release}-2026-11-27 and is ignored by
Git. Provider facts and host semantic judgments are not independently authenticated.

| Area | Observed outcome | Scope and limits |
| --- | --- | --- |
| Offline regression | 647 passed | Includes schemas, budget/replay, units, periods, scope and review guards; no external sockets |
| Lint/format | passed, 111 Python files formatted | Current src/tests/scripts |
| Source SDK | nine groups passed | All39, review16, simple3, shared reconnect, generic/finance, previews, typed all/finance; fictional software fixtures |
| Installed-wheel SDK | same nine groups passed | Fresh venv, actual packaged code; no provider/model calls |
| Workbench | browser and Node DOM checks passed | Explicit DCF canonical rows, finance/retrieval/review, escaping, mobile layouts; labelled synthetic fixtures |
| Clean installation | passed on macOS, Python3.12.10 | New venv without system packages, pinned runtime dependencies, pip check, three CLI help entrypoints, all39/zero-budget stdio and DCF |
| Live financial access | INFY annual readiness and HUL quarterly retrieval passed | Two real requests, one per financial response |
| Local finance over real captures | all nine workflows returned success | Eight annual INFY workflows and quarterly HUL TTM; not nine fresh calls; component holds remain possible |
| Live Drishti | news, summary announcement, earnings list/detail passed | INFY filter, bounded pages/selectors; five source records imported locally; no attachments fetched |
| Duplicate protection | typed/generic same-key replay returned same result | No extra financial request |
| Review handoff | 20 local calls passed | Real provider passage, explicit operator judgments; supported/insufficient/contradicted, quote rejection, identical replay/changed-submit conflict |
| Host reader handoff | actual public Infosys page read and supplied passage accepted | Host tool reading, not a Margin browser or automatic source-authentication service |
| Capability fallbacks | reader/no-reader/unknown/inventory-only contracts passed | Declarations exercised locally, not four independent host/model trials |
| Relevance | unrelated provider-filtered news excluded | Unannotated/irrelevant does not become neutral; empty balance denominator stays unknown |
| Skill | validator passed | Source skill updated; no global install or model behavior guarantee |
| Hosted platform CI | Windows, Ubuntu and macOS all passed | Python3.12 wheel install/standalone smoke; portable contracts on all, full647 regression on Unix; shared Unix backend remains macOS/Linux only |

## Actual live usage

Authorized: B2, Drishti HTTP16 including lifecycle, estimated credits8.
Used: **BharatStock2 / Drishti HTTP10 / estimated credits7**, reserved0/uncertain0 after
cleanup. Four Drishti logical data calls. No account probes, retries, extra pages,
provider purchases or changes to the user's active backend. Account balances/debits
were not measured. Do not rerun this spent allocation.

The selected operations worked with current keys; no paid subscription was required
for this pass. This establishes neither access to every endpoint/company nor data
redistribution rights. Provider issuer filters can include unrelated news; earnings
list/detail can overlap. Host relevance and deduplication remain necessary.

## Remaining checks/actions

- User upgraded mtest to0.10.0; the observed host smoke below records remaining behavior gaps. No automatic upgrade/restart was performed by Codex.
- Fresh-chat smoke in the user's selected host/model, checking actual calls and canonical
  reports rather than prose alone. Do not claim tool use from a plausible answer.
- Hosted platform checks passed for application/test commit ac49544: [actual run](https://github.com/rishitttt/margin-mcp/actions/runs/45976665943). Documentation-only follow-ups do not alter the wheel.
- Broader companies/endpoints need a new explicit live allocation. Automatic forecasting,
  source authenticity, market-wide sentiment, public PyPI/hosting and professor evaluation
  are outside this release.

Failed first attempts are retained privately: a stale browser unit-warning assertion,
a stale review catalog-count wait (replaced by exact runtime catalog comparison), and a
restricted-sandbox unit run whose 15 Unix-socket tests passed after local-socket access.
No runtime financial guard was weakened to make these checks pass.

The first hosted macOS job passed. Initial Linux failure was a test using monotonic
timestamp zero to simulate expiry on a freshly booted runner; the test now expires
relative to its recorded timestamp. Initial Windows test setup blocked Python's
stdlib socketpair self-pipe. The fixture now permits only that synchronous loopback
operation; three guard tests retain ordinary loopback/external-connect rejection.
Application/wheel code is unchanged by these portability fixes. The remaining Windows DOM test required explicit UTF-8 for the rupee symbol instead
of its default code page. Final jobs all passed. Official Actions versions were refreshed
after a runtime warning.

## User host smoke after upgrade

LM Studio/Qwen3-8B, package0.10.0, observed27 November; context setting not supplied.
Two private backend logs were frozen under reports/private/client-smoke-2026-11-27-1005.
This is a product smoke observation, not the professor's benchmark.

- Status correctly distinguished local limits and unknown account balance. Internal
  retention capacity appeared because the caller explicitly requested diagnostics.
- INFY annual consolidated growth executed successfully: B1/D0, canonical rows agree
  with the pasted final answer. The model's margin_result(request_id) follow-up is
  unsupported; fresh-company details use the same original inputs/key with include_details.
- HUL margin task selected readiness and stopped at execute=false/default preview;
  B0/D0. No margin calculation completed. Correct route is company_margins through
  margin_company_finance. Tool selection/execution remains a host acceptance gap.
- No DCF call appears in these two logs. The pasted hand-calculated answer does not
  test Margin's DCF engine and omits equity/per-share outputs.
- Two-step source review completed: supported/insufficient-evidence claims, one positive
  host annotation, original authenticity false. Bounded annotation coverage is not
  market coverage. The model's financial-impact follow-up is unsupported.

No provider requests, owner restart/configuration change or runtime fix was performed
while inspecting these records. New guided retries must be labelled separately from
unguided discovery; use confirmed remaining allowance and never refetch to inspect
an existing result.
