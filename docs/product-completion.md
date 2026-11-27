# Product completion plan — 27 November 2026

Scope is the product only. No professor benchmark, study tasks/gold, model comparisons
or hidden-reasoning capture. Version target: 0.10.0. Keep all39 as the supported default;
finance6/review16/simple3 and generic/legacy interfaces remain available.

## Plan before implementation

1. **Clear status:** add a deterministic local-allowance report. Preserve ledger/provider/
   version/owner fields; move internal record capacities, receipts and historical balance
   into opt-in MCP diagnostics. Account balance stays unknown unless actually observed.
   Keep core/workbench status compatibility. No provider request for status/catalog.
2. **Financial contracts:** add explicit DCF input definitions/provenance requirements.
   Do not derive future FCFF from CFO or debt from total liabilities. Add labelled DCF
   report rows for forecast PV, terminal value at horizon, discounted terminal PV,
   enterprise/equity/per-share values, preserving exact raw values/math. Render these
   rows directly in the workbench and via a bounded deterministic text renderer; no LLM.
3. **Provider product regression:** user allocates B2, Drishti HTTP16 and estimated
   credits8, in an isolated service. Real keys read from ignored env only. First B call:
   typed INFY annual readiness, capture sanitized response privately, verify same-key
   replay. Second B call: HUL quarterly financials. Reuse captured responses locally for
   the nine functions; distinguish local replay from fresh wrapper execution. Drishti:
   explicit metadata connection, bounded INFY news/summary announcement/earnings list,
   optional detail using an actual returned selector, and cleanup inside cap16. No
   outside-ledger account calls, retries, fallbacks, pagination or active-owner reset.
   Stop a provider on access/schema/uncertain failure and preserve the actual outcome.
4. **Review product checks:** exact quote/reference validation, immutable review submit,
   contradiction/insufficient evidence, sentiment relevance/coverage, reader/no-reader/
   unknown-host fallbacks. Use real returned passages where available and explicitly
   operator-supplied judgments. Actual host-read passage can test the reader handoff;
   capability/quote matches do not establish independent original authenticity. No
   Margin LLM/browser, fabricated labels as source truth or market-sentiment claim.
5. **Installation/compatibility:** full offline/Ruff, SDK standalone/shared/review/finance,
   browser/DOM report rendering, true fresh-venv wheel installation with pinned runtime
   dependencies, startup/reconnect and dependency/import checks. Add a bounded CI smoke
   matrix for supported standalone platforms; remote CI results are reported only if
   observed. Shared Unix socket mode remains macOS/Linux, not Windows parity.
6. **Current docs:** archive full historical guides with repaired relative links, then
   write concise README, AGENTS, handoff, context, setup, status, plan and docs index.
   Preserve historical source/research/reference records and immutable release artifacts.
   Make current vs planned vs unverified explicit. Keep research outside product imports.
7. **Release:** versioned immutable wheel/checksum, source/archive/known-key scan,
   installed SDK checks, public acceptance matrix and private evidence. Commit/push
   authorized changes. No public data serving, PyPI publication, paid-plan purchase,
   provider contact, remote deployment or automatic upgrade of the user's live owner.

## Acceptance and reporting

- Every status/financial report is deterministic and usable without model rewriting.
- Raw math and typed/generic key guards remain; unknown/partial fields are not zero.
- Tool responses and host prose are distinct; arbitrary-host wording is not guaranteed.
- Every live attempt/estimated credit is bounded and reported separately from account
  balances. Missing access is a measured hold, not a silently passing check.
- Core/SDK/host handoff/live/clean-install/platform results have separate evidence.
- No licensed payloads/keys in Git; private tests remain ignored. No old wheel overwrite.
- Further live operations outside this B2/Dr16/credits8 allocation require a new scope.

## Progress

Implemented and validated as0.10.0. All647 offline tests, Ruff, nine source SDK groups,
nine installed-wheel SDK groups, browser/DOM and clean-venv macOS checks pass. Review
contracts pass20 local calls with real passages and explicit host judgments. Live pass
finished B2/DrHTTP10/estimated credits7. Guides consolidated, archives preserved; source
skill validates. See [acceptance](product-acceptance.md). Hosted CI outcomes and user-side
upgrade/fresh-chat checks remain explicit follow-ups; no public deployment/evaluation.
