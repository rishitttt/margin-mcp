# Product acceptance — 0.10.0, 27 November 2026

This is product validation, not the professor's model benchmark. Private evidence is
under reports/private/product-{live,review-final,release}-2026-11-27 and is ignored by
Git. Provider facts and host semantic judgments are not independently authenticated.

| Area | Observed outcome | Scope and limits |
| --- | --- | --- |
| Offline regression | 644 passed | Includes schemas, budget/replay, units, periods, scope and review guards; no external sockets |
| Lint/format | passed, 110 Python files formatted | Current src/tests/scripts |
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
| Linux/Windows hosted CI | workflow added; remote pass not yet observed | Python3.12 standalone matrix; shared Unix backend remains macOS/Linux only |

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

- User upgrades the separate mtest installation manually; it remains0.9.5/B0D0 here.
- Fresh-chat smoke in the user's selected host/model, checking actual calls and canonical
  reports rather than prose alone. Do not claim tool use from a plausible answer.
- Observe the new hosted platform workflow before claiming remote Linux/Windows passes.
- Broader companies/endpoints need a new explicit live allocation. Automatic forecasting,
  source authenticity, market-wide sentiment, public PyPI/hosting and professor evaluation
  are outside this release.

Failed first attempts are retained privately: a stale browser unit-warning assertion,
a stale review catalog-count wait (replaced by exact runtime catalog comparison), and a
restricted-sandbox unit run whose 15 Unix-socket tests passed after local-socket access.
No runtime financial guard was weakened to make these checks pass.
