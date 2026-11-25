# Project context and handoff

**25 November user-led 0.6.1 validation:** current live mtest backend is now 0.6.1,
B1/D0 spent. HUL's old-key all-rows answer passed before the upgrade. INFY amounts
and corrected formulas pass; include_details reuses the same request/report and
returns raw INR. The model still did not print the requested raw/report value-unit
pairs and misstated some attribution/field paths. No new code change is needed;
same-key explicit extraction can be retested without fetching/restarting. Evidence
is in implementation and private lmstudio-061-live audit. Older source-versus-active
version notes below apply to their dated checkpoints.

**25 November 0.6.1 patch:** user-led 0.6.0 rows tests confirm correct INFY money/
growth and duplicate/details behavior; status B2/D0, local B2 spent. HUL supplied all
three rows, but the model omitted profit/margin. A Margin-side inherited-formula bug
was found and fixed in source: per-metric comparison/report formulas, no CAGR formula
on years, arithmetic unchanged. See [implementation](implementation.md) and
[MCP contract](mcp.md). The 0.6.1 wheel does not update the active 0.6.0 process;
do not reset allowances or claim its cached replies were patched. Existing HUL key
supports a no-fetch all-rows retest. Raw captures stay private; point 4 stays deferred.

**25 November 0.6.0 reporting repair:** default company response v2 now supplies
canonical rows with consistent units and formatted
calculated amounts. Raw calculation fields moved into opt-in details; same-key
projection does not fetch again. Existing math/holds and 21 tools remain. Point 4
(host-enforced final prose) is deferred. [MCP migration](mcp.md#reporting-contract-v2-and-migration)
and [implementation](implementation.md) own behavior/evidence. Saved HUL/INFY reports
were reformatted offline; no new model success is claimed. The live mtest backend
remains 0.5.0 with B2 spent; do not upgrade/restart/reset it silently. A local 0.6.0
wheel is for deliberate version-matched installation after allowance reconciliation.

**25 November user-led 0.5.0 retest:** local mtest/backend now runs 0.5.0. Guided HUL
margin, same-key replay and INFY growth succeed; ledger B2/D0, B2 local allowance spent.
The tool arithmetic/units are correct relative to returned inputs, but the model's final
prose still mis-scales money. No proof of context exhaustion or original-source accuracy.
See [implementation](implementation.md) and the private live audit. Next useful retest
is reporting-only with existing keys, without restarting or fetching again. Older
installation-state notes below describe their build checkpoints, not current setup.

**25 November 0.5.0 checkpoint:** `margin_company_finance` provides explicitly executed fresh financials plus existing deterministic company math in one tool call. It does not read/write the retained raw-source buffers and needs no earlier handles; at most one BharatStock request, no Drishti. Local preview is default, stable keys protect duplicate requests within one process, and compact answers/control records are bounded. All prior interfaces remain. [MCP usage](mcp.md) owns commands and [fresh-fetch design](design/fetch-and-calculate.md) owns subscription/retention choices. Current live `mtest` backend remains 0.4.0 pending a controlled upgrade/allowance reconciliation; no new provider/model calls in this build.

**25 November 0.4.0 checkpoint:** deterministic financial_view output and six directly typed common calculation tools address the observed Qwen interpretation/schema failures. Optional private Unix-socket shared mode keeps one core/identity/ledger alive across frontend restarts; source TTL/eviction remains. Backend credentials/recording stay in the state owner. No automatic start/retry or persistent data corpus is added. [Current MCP setup](mcp.md) owns commands and lifecycle. The workbench/CLI process remains separate; do not mix its handles with shared MCP handles. Model-host improvement requires a fresh retest.

**25 November delivered MCP alpha:** package 0.3.0 exposes 14 stdio workflow tools over one core. 220 tests and source/isolated-wheel SDK acceptance pass; each acceptance run used 27 calls/54 log events and zero real provider/model requests. [MCP setup](mcp.md) owns commands/configuration; [implementation](implementation.md) owns evidence. Core `6b22f57` and plan `07b981a` were pushed before code. No host config was changed; actual model-host and budgeted live MCP validation are next. Old no-MCP/local-unpushed statements below are historical.

**25 November MCP plan:** source checkpoint `6b22f57` is pushed, with 194 tests and numerical evaluator gold separated into an ignored file. The user now authorizes planning/building the stdio MCP adapter. The [updated architecture](design/mcp-aggregation.md) defines 14 workflow tools over the current core. First publish the plan, then implement and test protocol/packaging with zero real provider/model calls. Old no-MCP instructions below are superseded.

**24 November completed finance repair:** 192 offline tests plus synthetic CLI/browser acceptance passed. Inventory is 13 retrieval, 15 local, nine company and ten review functions. Documented auto units, typed balance stocks, data readiness and new metric groups are delivered. Announcements now succeed with extraction false. HUL TTM works using reviewed duration metadata. Continuing-profit margin replaces the mixed-scope default; group/owners ratios stay partial when scope differs. Two fresh financial requests and 13 Drishti HTTP attempts used one estimated credit; final reprocessing used no more calls. See [current matrix](reference/function-validation.md) and [finance scope](design/finance-data-support.md). Earlier checkpoints below are historical.

**24 November unit follow-up:** current provider FAQ supports absolute INR for BharatStock statement amounts; Drishti HUL cells explicitly label crore/per-share units, while official examples show other issuers in lakhs. Eight saved-response consistency checks passed, but three revenue differences survive conversion. Runtime defaults remain unchanged. See [financial unit evidence](financial-analysis.md#unit-evidence-24-november-2026) and the private unit-audit supplement; original packets remain intact.

**24 November HINDUNILVR audit:** 167 offline tests passed, including 24 new per-operation orchestration checks. All 29 retrieval/finance functions are [mapped](reference/function-validation.md): 22 succeeded on real returned data, two TTM paths correctly stayed incomplete without quarter starts, announcements stayed schema-held, and four explicit-input valuation functions were not supplied invented company assumptions. Earnings detail succeeded using a discovered ID, superseding the earlier budget-blocked status below. Thirteen arithmetic recomputations matched. Actual HTTP attempts: BharatStock seven, Drishti twelve; eight estimated credits, debit unmeasured. Private responses/report/ZIP are under `reports/private/function-audit-HINDUNILVR-2026-11-24`. No original-source verification or new model-host evaluation is claimed.

**24 November core 0.2.0 implementation:** ten no-inference citation/sentiment handoff functions, retained-news source import, HTTP/CLI/workbench controls, simple --why recording, explicit source-path roots and consistent Drishti readiness are delivered. 143 offline tests plus CLI/browser acceptance passed. Real B10 succeeded; Drishti categories/news/earnings listing and host review over two real news summaries succeeded after quarantining an added unexposed native tool. Announcements remain schema-held, earnings detail was budget-blocked before dispatch, and real TTM lacks quarter starts. No original verification/independent sentiment gold is claimed. See [implementation](implementation.md) and [review workflows](review-workflows.md). MCP packaging is gated on the remaining core-validation review, not started.

**24 November planning checkpoint:** [active build plan](plan.md) restores citation and content-sentiment workflows, schedules a thin MCP adapter and a separate cross-model benchmark, and keeps simple tool-call/one-line decision trails. One shared citation protocol routes by declared host capabilities, not model name; missing semantic assessment stays unreviewed. No new runtime or provider/model calls in this planning revision. Dated frontend/pilot checkpoints below remain historical evidence.

**Frontend checkpoint — 16 November:** the local Function Lab now uses charcoal/violet styling and two views, Retrieval and Finance. The dedicated DCF tab/form is removed temporarily; backend functions stay intact. Full retrieval and local-calculation JSON testers, schemas and inspectable plan arguments support manual testing. The previous nonignored source is saved under ignored `reports/private/frontend-checkpoints/20261116-144155/`. Offline/browser checks passed without live provider calls; see [implementation](implementation.md#function-lab-frontend-16-november-2026). A synthetic frontend preview is running on port 8766 for this task; older “no server” statements below describe their own checkpoints.

16 November live-test checkpoint: separate 16-task RELIANCE/TCS runner and evaluator ZIPs are built locally; fresh live calls, DCF excluded, --why visible summaries and sanitized submission export. 126 offline tests and relocated synthetic package acceptance pass; first returned live agent pilot evaluated: 38/38 automatic checks with manual caveats (not an overall scientific score). See [live skill evaluation](live-skill-evaluation.md) for build/run instructions, actual preparation costs, source-key review status and limitations.

Latest extension: **16 November — portable skill bundle and visible-summary evaluation logging**. See [portable setup](portable-agent-bundle.md). A private ignored ZIP includes both trial keys in a separate credential file under explicit user authorization; no keys were added to source/Git/prompts/logs. All 29 functions are documented, and sessions record tool observations plus submitted decision/observation/limitation summaries and final answer. Notes are agent self-reports, not hidden reasoning. 117 offline tests and relocated-bundle fictional process acceptance pass; this extension used zero provider/model calls. Fresh installation across platforms/hosts and real-model evaluation remain pending. The installed global skill stays unrecorded; configure a labelled task session for evaluation. No server remains running.

Latest checkpoint: **16 November 2026 — pre-MCP agent access**. `margin-agent` JSON commands and an installed `margin-research` Codex skill call one shared backend without the browser. Functions remain importable modules in one Python package. Separate opt-in `research/pilot.py` records private observations/final answers; normal usage remains transient. 111 offline tests pass. Sixteen separate-command fictional acceptance checks passed; one real BharatStock annual request / zero Drishti calls verified RELIANCE margin and retained cash-flow/growth/CAGR reuse. No live pilot was retained, new subscription purchased, model experiment run, commit or push made. See [agent interface](agent-interface.md) for runnable setup and remaining evaluation gaps. No backend remains running.

Latest UX checkpoint: **15 November 2026 — unified tasks/preview/run/history**. One scoped unit control, stale company/preview isolation, recent local run history and consistent previewed execution are implemented. Latest offline count is 95; this UX pass used one additional BharatStock request and zero Drishti calls. See the latest implementation entry.

Current implementation checkpoint: **15 November 2026 — financial foundation and fresh source probes**. Product/research separation remains in effect; latest source inspection is now the bounded 15 November probe, distinct from the earlier user UI demonstration. [Implementation status](implementation.md) owns observed behavior; [delivery plan](plan.md) owns active scope. The [9 November short handoff](../HANDOFF.md) is a dated navigation snapshot.

## Current scope

Build the usable product first: reliable BharatStock REST + Drishti MCP retrieval, complete safe operation/receipt contracts, typed financial facts, deterministic comparisons and DCF integration through the local workbench. Package stable Python/MCP interfaces through a thin adapter as contracts stabilize. **Citation verification and content-sentiment protocols are active planned work under the 24 November plan.** Existing source locators, provenance, sanitization and unverified labels remain; manual financial/source review is not deferred.

The professor's proposal is a separate optional research workstream consuming the product's public contracts. It owns permissioned snapshots/replay, fixed tasks, independently verified answers, agent trajectories and study analysis. The note explicitly requires independent answer keys/evaluation; it does not require the research to be unrelated to Margin. Our architectural decision is that product usage/installation must not depend on experiment infrastructure, study company lists, gold, model keys or datasets. Product code must not import the optional top-level research project.

This supersedes the 7 November research-first product sequence. Preserve the [research audit](design/research-environment-review.md) for the optional harness and its rights/feasibility gates. The [finance/protocol design](design/analysis-and-protocols.md) retains detailed financial/protocol contracts and capability-routing design; its old release priorities are superseded by the current plan.

## Delivered state and evidence

`main` contains the installable `margin-research` package, thirteen core operations, provider guards, shared local allowances, sanitizer/receipts and temporary FastAPI/static workbench. The prior corpus/PDF implementation remains on pushed `d1` at `c77963d`; no old ingestion CLI is delivered on main. The financial fact layer and eleven local comparison/FCFF/DCF/sensitivity/scenario functions now exist, with workbench controls. Automatic fact loading and a source picker replace the hidden-button-only path. Five company financial workflows resolve retained reuse or one previewed financials request; all calculation functions can return ordinary result cards. DCF is explicit-input only; automatic provider-to-valuation preparation, capture/replay, agent runner, citation verifier, sentiment protocol and downstream Margin MCP server remain absent.

The 21 October RELIANCE export shows eight successful operations: snapshot, quarterly/annual financials, ratios, EOD prices, news, announcements and earnings discovery. It does not establish wider coverage, source accuracy or current charges. Reported news/earnings field variants and detail selection/envelopes, print wrapping and decorative-image source classification have now been repaired, with offline/browser coverage; a fresh end-to-end live UI exercise is still separate. Corporate actions and selected identity/directory operations still need bounded live validation. Earnings detail has earlier upstream evidence, not proof of the complete present UI path.

The 15 November implementation passes 91 offline tests plus Ruff/JS checks. Real source probes used three BharatStock attempts and 22 Drishti HTTP attempts, with six observed credits (975 → 969). These facts do not establish broad financial accuracy or a source-populated valuation. Fictional automated fixtures establish software behavior only; company research and live demonstrations must use real documented observations.

Known source issues include market-cap scales differing by JSON path, missing quarterly cash flows, stale numerical versus event periods and unresolved normalized/raw earnings differences. Four Reliance FY25 cells were checked against an issuer statement in the earlier trials; broader correctness is unverified. Use the [dated provider research](research/mcp-provider-feasibility.md) and [Drishti operation map](reference/drishti-functions.md), not inferred blanket coverage.

## Next implementation batch

1. Align Drishti live schema readiness across catalog, preview and execution; preserve guards.
2. Stabilize source references/path roots and packet/status contracts; retain definitions/unknowns.
3. Add bounded original-source resolution, passage extraction and host citation assessment round trips with deterministic-only fallbacks.
4. Independently validate remaining company wrappers/DCF and reconcile Advait's work when supplied; add bounded sentiment annotation/aggregation after evidence contracts.
5. Implement thin stdio MCP packaging and simple decision-log integration over the same core. Build independent gold/common model-runner conditions in the separate research project.

See [plan](plan.md) for batch acceptance, dependencies and model-capability boundaries.
The professor's evaluator remains separate from product citation judgments; current fresh
live testing preference is preserved. No hidden external verifier/model service is added.

## Operational constraints

Existing keys worked in the bounded 15 November probe; Drishti balance was 969 at its end, not a standing allowance. Other current account state and applicable research/public-serving rights remain unknown. Historical keys were BharatStock Free (25 requests/day) and Drishti trial (1,000 credits); the 986-credit figure dates to 9 October. Public rights/pricing inspected on 7 November are dated research findings, not current purchase/account advice. Check applicable access and scope before new bounded live runs. No purchase or provider contact is authorized by this plan.

The product remains on demand with bounded expiring results. A narrow explicitly installed observer/export seam may support an external permissioned recorder; it must not silently introduce persistent financial storage, a corpus or model calls. Local allowances reset on restart and do not restore account quota or measure all clients' spend.

Credentials/private responses remain ignored and out of Git. Old trial diagnostics have overdue manual review dates (22/23 October); this revision neither reuses/deletes them nor extends retention. The earlier planning revision made no calls; the subsequent implementation/source checkpoint above supersedes that runtime/access state. No purchase, external model call, commit or push occurred in this implementation.
