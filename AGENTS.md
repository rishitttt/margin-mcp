# Working on Margin

## Start here

Read [README](README.md), [context](docs/context.md), [implementation status](docs/implementation.md) and the [documentation index](docs/README.md). Inspect branch/worktree state and preserve unrelated changes. Current work is product completion; professor evaluation is excluded. Historical agent notes are [archived](docs/archive/2026-11-27-agents.md), not current instructions.

## Scope and engineering

- `main` delivers provider aggregation, deterministic finance, host-side review protocols, local stdio MCP, optional shared backend, CLI/skill and temporary workbench. Corpus/PDF work remains on `d1` at c77963d; do not restore a warehouse or rewrite history.
- Python>=3.12. BharatStock uses REST; Drishti uses the guarded upstream MCP client. Handlers call shared core services. No product LLM, hidden browser, automatic forecasting or public remote service.
- Keep all39 as supported default; finance6/review16/review-simple3 are optional frontend views, not authorization boundaries. Core functions are independent of MCP/web. Never change the user's profile to rescue a failed trial.
- Preserve strict schemas, known units/provenance, raw values, reporting periods/basis, stock/flow distinction, unknown/null fields and accounting-scope holds. Never call CFO-minus-capex FCFF, total liabilities debt, or a limited inventory-adjusted ratio a fully reviewed quick ratio.
- Local allowances are not account balances/daily quotas. No hidden retries, redirects, fallback sources, pagination, broad backfills or automatic owner restarts. Lost replies use the SAME intent/key; changed intent conflicts. Restart loses transient handles/duplicate protection, not upstream usage.
- Current authorized product pass was B2/DrHTTP16/estimated credits8, isolated from the user's owner. It completed at B2/DrHTTP10/estimated credits7. Do not repeat the spent pass or probe accounts. Additional live work needs a newly allocated remaining budget.
- User manually upgraded mtest to0.10.0; latest records are in `mtest/logs` (older `logs~` preserved). Host smoke observed INFY B1/D0 and HUL preview B0/D0; current remaining account/process allowance is not inferred. Do not upgrade/restart/reset it automatically. New package version is0.10.0; keep versioned wheels immutable, scan/checksum before commit.
- Credentials/account identities/raw licensed responses/signed URLs stay out of Git/prompts/public reports. Read ignored env as data, never source it. Sanitize before model/log output; Drishti locators can embed keys. Private test captures are not a corpus or independently verified source truth.
- Citation/sentiment judgments come from the host. Preserve hashes, exact quote/reference checks, atomic immutable submit, TTL/capacity and no-refetch fallbacks. Host search is not source reading; missing capability is unknown. Provider issuer filters do not establish semantic relevance or investor sentiment.
- Product status/DCF canonical reports are deterministic. Host prose can still be wrong; don't weaken calculations or add instructions endlessly to manufacture a model pass. Raw math remains distinct from display rounding/source authenticity.
- Keep protocol stdout separate from diagnostics; suppress unsafe SDK/provider exception text. Shared Unix sockets are optional macOS/Linux; standalone is the portable route. No provider purchases/contact/public publication/deployment implied.

## Documentation and validation

- [Docs index](docs/README.md) assigns ownership. Current setup belongs in docs/mcp.md; actual evidence/limits in docs/implementation.md; priorities in docs/plan.md; concise state in docs/context.md/HANDOFF.md. Put chronological history in docs/archive, not repeated preambles.
- [Product plan](docs/product-completion.md) owns this pass. Update [API tests](docs/api-testing.md), [report contracts](docs/product-reports.md) and [release checks](docs/release-checks.md) with measured results. Keep Drishti Markdown/JSON mapping synchronized with actual reviewed schemas; metadata is not entitlement.
- Run `.venv/bin/ruff check src tests scripts`, `.venv/bin/ruff format --check src tests scripts`, `.venv/bin/pytest -q`. Default tests block external sockets; live checks are separate, explicitly bounded. Use SDK/install/DOM checks appropriate to changed paths. Dependency pin changes require requirements-dev.lock update.
- Source skill changes require skill validation; never silently install globally or attach an evaluation session. Portable private-key bundles were user-authorized locally, not for Git. Review packaging/scripts before changing them.
- Separate unit/SDK/live-provider/host-reader/clean-install/platform results. Record actual HTTP attempts/estimated credits without asserting account charges. Preserve failed first attempts and private evidence; no hidden reasoning/debug capture.
- For doc-only changes check links/anchors, stale commands and git diff --check. Never modify an old release wheel/checksum or publish private captures.

## Separate optional research

Normal src/margin code must not import research tasks, gold, model runners or study capture. The professor harness is independent of product installation/release. Do not expand this product-only task into benchmark/model comparisons or gold creation. Provider capture/redistribution and external-model processing rights remain scoped; no public raw-data service follows from an API subscription.

## Historical section links

<a id="separate-optional-research-harness"></a>[Historical: Separate optional research harness](docs/archive/2026-11-27-agents.md#separate-optional-research-harness)
