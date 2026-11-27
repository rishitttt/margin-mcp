# Current implementation and validation

Current source/public candidate margin-mcp0.10.1; prior local release0.10.0. Runtime: Python3.12+, BharatStock REST and upstream Drishti MCP, shared core calculations/review, local stdio MCP (all39), optional shared Unix backend/CLI/skill/workbench. No product LLM, market database or automatic forecast/source-authentication service.

## Public packaging candidate — 27 November 2026

margin-mcp0.10.1 adds MIT/four-author metadata, public own-key installation docs,
a self-contained sdist and dedicated Trusted Publishing workflows. Runtime financial
logic is unchanged; the software version is shared by metadata and MCP initialization.
The old margin-research distribution and new margin-mcp must use separate environments.

Local checks: 654 full repository tests pass in both development and newly resolved
release environments; 637 extracted-sdist product tests pass. Ruff passes (117 files),
isolated wheel/sdist build and strict Twine checks pass, and three new venvs pass
base-wheel/base-sdist/workbench installed-product checks (all39, actual CLI scripts,
pip check, hypothetical DCF and static/HTTP checks). Both archives pass metadata,
content/runtime parity, token-pattern and exact configured-provider-secret scans.
Both workflows pass actionlint. No provider calls or active-owner changes were made.

[Package review](pypi-package-review.md) records resolved findings, hashes and failed
first attempts. New hosted-platform validation, account/environment setup and actual
TestPyPI/PyPI uploads remain pending; previous hosted results below belong to0.10.0.

## Product changes in0.10.0

Status returns a deterministic local-allowance report; capacity/history/receipt diagnostics are opt-in in MCP. Ledger/provider/identity fields remain available; core status is unchanged. DCF returns exact labelled report rows, input definitions and deterministic Markdown while retaining raw math. Workbench renders canonical DCF rows directly. See [report contracts](product-reports.md).

## Actual live product pass — 27 November 2026

Approved cap B2/DrHTTP16/estimated credits8. Actual usage **B2/DrHTTP10/estimated credits7**, including Dr lifecycle/cleanup. No account probes, retries, pagination or user-owner changes. Account debits/balances were not measured. Source facts remain provider records, not independently verified filings.

| Check | Measured result |
| --- | --- |
| INFY annual consolidated typed readiness | success, one live financial request |
| Equivalent typed/generic key replay | same result, no additional request |
| HUL quarterly financials, bounded page1 | success, one live request |
| Nine company functions over those two responses | all success locally; not nine fresh wrapper executions |
| INFY Dr news/announcements/earnings list/detail | all success, four logical data calls |
| Local event-source import | five records imported; no attachment fetch |

A news result returned under the INFY filter described other issuers. Provider filters do not establish relevance; host annotations must exclude irrelevant content. Earnings list/detail can overlap and require deduplication. Unknown publication dates stay unknown.

Private evidence: reports/private/product-live-2026-11-27 (ignored). Credentials/identity/raw licensed data are not published. Historical0.9.5 app-chat evidence remains separate: typed selection/DCF math passed, quota/accounting prose did not. The new product reports reduce ambiguity; arbitrary model prose is not guaranteed.

## Prior0.10.0 software, review and installation acceptance

**647 offline tests pass**, Ruff passes (111 Python files), nine source SDK groups and
nine installed-wheel groups pass. Browser/Node DOM checks pass, including canonical
DCF rendering. A true fresh venv passes dependency/CLI/all39/DCF checks on macOS with
Python3.12.10. Review handoffs pass20 local calls using real passages and explicit host
judgments, including relevance and actual host-reader material. No product LLM is used.

See the [acceptance matrix](product-acceptance.md) for evidence/limits and failed first
attempts. Hosted Windows, Ubuntu and macOS wheel/install/standalone checks [all passed](https://github.com/rishitttt/margin-mcp/actions/runs/45976665943). Portable contract tests run on all three; the full647 suite also passes on both Unix runners.
The source skill validates. These are product checks, not automatic model benchmark or
source-authentication results. [Release checks](release-checks.md) document reproducible
installation and software checks.

## Operating state and limits

The user manually upgraded mtest to0.10.0. New logs are under logs, older logs~ remain. [Observed host smoke](product-acceptance.md#user-host-smoke-after-upgrade): INFY growth succeeded B1/D0; HUL stopped at readiness preview; no DCF call appears in the two inspected logs. Codex did not restart/configure the owner or make new provider calls while checking them. Current product keys worked for the selected live pass; broader endpoint/company/entitlement coverage is not established. Additional live checks need a new remaining allocation. Public publishing/deployment is not performed.

[Install/upgrade](mcp.md), [active plan](plan.md), [full historical evidence](archive/2026-11-27-docs-implementation.md).

## Historical section links

<a id="implementation-and-validation-status"></a>[Historical: Implementation and validation status](archive/2026-11-27-docs-implementation.md#implementation-and-validation-status)

<a id="actual-095all39-app-chat-readiness-and-dcf-27-november-2026-ist"></a>[Historical: Actual 0.9.5/all39 app-chat readiness and DCF: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#actual-095all39-app-chat-readiness-and-dcf-27-november-2026-ist)

<a id="095-typed-readinessdcf-repair-27-november-2026-ist"></a>[Historical: 0.9.5 typed readiness/DCF repair: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#095-typed-readinessdcf-repair-27-november-2026-ist)

<a id="actual-lm-studio-094all37-previews-27-november-2026-ist"></a>[Historical: Actual LM Studio 0.9.4/all37 previews: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#actual-lm-studio-094all37-previews-27-november-2026-ist)

<a id="094-compact-finance-surface-27-november-2026-ist"></a>[Historical: 0.9.4 compact finance surface: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#094-compact-finance-surface-27-november-2026-ist)

<a id="guided-093-margin-preview-follow-up-27-november-2026-ist"></a>[Historical: Guided 0.9.3 margin preview follow-up: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#guided-093-margin-preview-follow-up-27-november-2026-ist)

<a id="actual-093-zero-request-model-previews-27-november-2026-ist"></a>[Historical: Actual 0.9.3 zero-request model previews: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#actual-093-zero-request-model-previews-27-november-2026-ist)

<a id="093-finance-workflow-repairs-27-november-2026-ist"></a>[Historical: 0.9.3 finance workflow repairs: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#093-finance-workflow-repairs-27-november-2026-ist)

<a id="guided-092-readiness-completion-27-november-2026-ist"></a>[Historical: Guided 0.9.2 readiness completion: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#guided-092-readiness-completion-27-november-2026-ist)

<a id="actual-092-live-model-batch-27-november-2026-ist"></a>[Historical: Actual 0.9.2 live-model batch: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#actual-092-live-model-batch-27-november-2026-ist)

<a id="092-explicit-execution-contract-27-november-2026-ist"></a>[Historical: 0.9.2 explicit execution contract: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#092-explicit-execution-contract-27-november-2026-ist)

<a id="coached-091-planning-follow-up-27-november-2026-ist"></a>[Historical: Coached 0.9.1 planning follow-up: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#coached-091-planning-follow-up-27-november-2026-ist)

<a id="user-led-091-discovery-retry-27-november-2026-ist"></a>[Historical: User-led 0.9.1 discovery retry: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-091-discovery-retry-27-november-2026-ist)

<a id="091-guidance-and-function-safety-repairs-27-november-2026-ist"></a>[Historical: 0.9.1 guidance and function-safety repairs: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#091-guidance-and-function-safety-repairs-27-november-2026-ist)

<a id="finance-discovery-and-live-sdk-checks-27-november-2026-ist"></a>[Historical: Finance discovery and live SDK checks: 27 November 2026 IST](archive/2026-11-27-docs-implementation.md#finance-discovery-and-live-sdk-checks-27-november-2026-ist)

<a id="user-led-090-completed-review-26-november-2026-ist"></a>[Historical: User-led 0.9.0 completed review: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-090-completed-review-26-november-2026-ist)

<a id="090-review-flow-repair-26-november-2026-ist"></a>[Historical: 0.9.0 review-flow repair: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#090-review-flow-repair-26-november-2026-ist)

<a id="professor-demo-client-26-november-2026-ist"></a>[Historical: Professor demo client: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#professor-demo-client-26-november-2026-ist)

<a id="user-led-082-preset-assisted-trials-26-november-2026-ist"></a>[Historical: User-led 0.8.2 preset-assisted trials: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-082-preset-assisted-trials-26-november-2026-ist)

<a id="anchor-registration-and-review-robustness-repair-26-november-2026-082"></a>[Historical: Anchor registration and review robustness repair: 26 November 2026, 0.8.2](archive/2026-11-27-docs-implementation.md#anchor-registration-and-review-robustness-repair-26-november-2026-082)

<a id="user-led-complete-infy-task-incomplete-protocol-26-november-2026-ist"></a>[Historical: User-led complete INFY task, incomplete protocol: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-complete-infy-task-incomplete-protocol-26-november-2026-ist)

<a id="user-led-081-missing-task-trial-26-november-2026-ist"></a>[Historical: User-led 0.8.1 missing-task trial: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-081-missing-task-trial-26-november-2026-ist)

<a id="user-led-081-first-unguided-attempt-26-november-2026-ist"></a>[Historical: User-led 0.8.1 first unguided attempt: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-081-first-unguided-attempt-26-november-2026-ist)

<a id="optional-capability-aware-citation-protocol-26-november-2026-081"></a>[Historical: Optional capability-aware citation protocol: 26 November 2026, 0.8.1](archive/2026-11-27-docs-implementation.md#optional-capability-aware-citation-protocol-26-november-2026-081)

<a id="user-led-080-completed-review-acceptance-26-november-2026-ist"></a>[Historical: User-led 0.8.0 completed review acceptance: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-080-completed-review-acceptance-26-november-2026-ist)

<a id="user-led-080-preparation-acceptance-26-november-2026-ist"></a>[Historical: User-led 0.8.0 preparation acceptance: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-080-preparation-acceptance-26-november-2026-ist)

<a id="typed-review-and-focused-profile-26-november-2026-080"></a>[Historical: Typed review and focused profile: 26 November 2026, 0.8.0](archive/2026-11-27-docs-implementation.md#typed-review-and-focused-profile-26-november-2026-080)

<a id="user-led-070-review-failure-26-november-2026-ist"></a>[Historical: User-led 0.7.0 review failure: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-070-review-failure-26-november-2026-ist)

<a id="user-led-070-retrieval-acceptance-26-november-2026-ist"></a>[Historical: User-led 0.7.0 retrieval acceptance: 26 November 2026 IST](archive/2026-11-27-docs-implementation.md#user-led-070-retrieval-acceptance-26-november-2026-ist)

<a id="typed-event-previews-and-schema-feedback-25-november-2026-070"></a>[Historical: Typed event previews and schema feedback: 25 November 2026, 0.7.0](archive/2026-11-27-docs-implementation.md#typed-event-previews-and-schema-feedback-25-november-2026-070)

<a id="first-user-led-062-preview-25-november-2026"></a>[Historical: First user-led 0.6.2 preview: 25 November 2026](archive/2026-11-27-docs-implementation.md#first-user-led-062-preview-25-november-2026)

<a id="drishti-to-review-repair-25-november-2026-062"></a>[Historical: Drishti-to-review repair: 25 November 2026, 0.6.2](archive/2026-11-27-docs-implementation.md#drishti-to-review-repair-25-november-2026-062)

<a id="versioned-wheel-committed-25-november-2026"></a>[Historical: Versioned wheel committed: 25 November 2026](archive/2026-11-27-docs-implementation.md#versioned-wheel-committed-25-november-2026)

<a id="user-led-061-acceptance-25-november-2026"></a>[Historical: User-led 0.6.1 acceptance: 25 November 2026](archive/2026-11-27-docs-implementation.md#user-led-061-acceptance-25-november-2026)

<a id="060-live-findings-and-061-formula-patch-25-november-2026"></a>[Historical: 0.6.0 live findings and 0.6.1 formula patch: 25 November 2026](archive/2026-11-27-docs-implementation.md#060-live-findings-and-061-formula-patch-25-november-2026)

<a id="canonical-structured-rows-25-november-2026-060"></a>[Historical: Canonical structured rows: 25 November 2026, 0.6.0](archive/2026-11-27-docs-implementation.md#canonical-structured-rows-25-november-2026-060)

<a id="user-led-050-live-acceptance-25-november-2026"></a>[Historical: User-led 0.5.0 live acceptance: 25 November 2026](archive/2026-11-27-docs-implementation.md#user-led-050-live-acceptance-25-november-2026)

<a id="fresh-fetch-company-finance-25-november-2026-050"></a>[Historical: Fresh-fetch company finance: 25 November 2026, 0.5.0](archive/2026-11-27-docs-implementation.md#fresh-fetch-company-finance-25-november-2026-050)

<a id="financial-fidelity-and-shared-local-state-25-november-2026-040"></a>[Historical: Financial fidelity and shared local state: 25 November 2026, 0.4.0](archive/2026-11-27-docs-implementation.md#financial-fidelity-and-shared-local-state-25-november-2026-040)

<a id="lm-studio-live-financial-retrieval-25-november-2026"></a>[Historical: LM Studio live financial retrieval: 25 November 2026](archive/2026-11-27-docs-implementation.md#lm-studio-live-financial-retrieval-25-november-2026)

<a id="repeated-host-launches-and-recording-25-november-2026-033"></a>[Historical: Repeated host launches and recording: 25 November 2026, 0.3.3](archive/2026-11-27-docs-implementation.md#repeated-host-launches-and-recording-25-november-2026-033)

<a id="financial-schema-feedback-repair-25-november-2026-032"></a>[Historical: Financial schema-feedback repair: 25 November 2026, 0.3.2](archive/2026-11-27-docs-implementation.md#financial-schema-feedback-repair-25-november-2026-032)

<a id="mcp-catalog-routing-repair-25-november-2026-031"></a>[Historical: MCP catalog-routing repair: 25 November 2026, 0.3.1](archive/2026-11-27-docs-implementation.md#mcp-catalog-routing-repair-25-november-2026-031)

<a id="local-stdio-mcp-alpha-25-november-2026"></a>[Historical: Local stdio MCP alpha: 25 November 2026](archive/2026-11-27-docs-implementation.md#local-stdio-mcp-alpha-25-november-2026)

<a id="financedata-repair-completion-24-november-2026"></a>[Historical: Finance/data repair completion: 24 November 2026](archive/2026-11-27-docs-implementation.md#financedata-repair-completion-24-november-2026)

<a id="new-ticker-function-audit-24-november-2026"></a>[Historical: New-ticker function audit: 24 November 2026](archive/2026-11-27-docs-implementation.md#new-ticker-function-audit-24-november-2026)

<a id="core-review-workflows-and-readiness-24-november-2026"></a>[Historical: Core review workflows and readiness: 24 November 2026](archive/2026-11-27-docs-implementation.md#core-review-workflows-and-readiness-24-november-2026)

<a id="function-lab-frontend-16-november-2026"></a>[Historical: Function Lab frontend: 16 November 2026](archive/2026-11-27-docs-implementation.md#function-lab-frontend-16-november-2026)

<a id="branch-transition"></a>[Historical: Branch transition](archive/2026-11-27-docs-implementation.md#branch-transition)

<a id="validation"></a>[Historical: Validation](archive/2026-11-27-docs-implementation.md#validation)

<a id="portable-local-bundle-and-visible-summaries-16-november-2026"></a>[Historical: Portable local bundle and visible summaries: 16 November 2026](archive/2026-11-27-docs-implementation.md#portable-local-bundle-and-visible-summaries-16-november-2026)

<a id="pre-mcp-agent-interface-16-november-2026"></a>[Historical: Pre-MCP agent interface: 16 November 2026](archive/2026-11-27-docs-implementation.md#pre-mcp-agent-interface-16-november-2026)

<a id="unified-workbench-flow-15-november-2026"></a>[Historical: Unified workbench flow: 15 November 2026](archive/2026-11-27-docs-implementation.md#unified-workbench-flow-15-november-2026)

<a id="financial-workflow-repair-and-company-operations-15-november-2026"></a>[Historical: Financial workflow repair and company operations: 15 November 2026](archive/2026-11-27-docs-implementation.md#financial-workflow-repair-and-company-operations-15-november-2026)

<a id="financial-foundation-and-fresh-source-checkpoint-15-november-2026"></a>[Historical: Financial foundation and fresh-source checkpoint: 15 November 2026](archive/2026-11-27-docs-implementation.md#financial-foundation-and-fresh-source-checkpoint-15-november-2026)

<a id="productresearch-boundary-planning-15-november-2026"></a>[Historical: Product/research boundary planning: 15 November 2026](archive/2026-11-27-docs-implementation.md#productresearch-boundary-planning-15-november-2026)

<a id="documentation-handoff-9-november-2026"></a>[Historical: Documentation handoff: 9 November 2026](archive/2026-11-27-docs-implementation.md#documentation-handoff-9-november-2026)

<a id="research-direction-audit-7-november-2026"></a>[Historical: Research-direction audit: 7 November 2026](archive/2026-11-27-docs-implementation.md#research-direction-audit-7-november-2026)

<a id="public-endpoint-checkpoint"></a>[Historical: Public endpoint checkpoint](archive/2026-11-27-docs-implementation.md#public-endpoint-checkpoint)

<a id="repository-checks"></a>[Historical: Repository checks](archive/2026-11-27-docs-implementation.md#repository-checks)

<a id="authenticated-trial-checkpoint"></a>[Historical: Authenticated trial checkpoint](archive/2026-11-27-docs-implementation.md#authenticated-trial-checkpoint)

<a id="remaining-gates"></a>[Historical: Remaining gates](archive/2026-11-27-docs-implementation.md#remaining-gates)

<a id="selected-operation-checkpoint-9-october-2026"></a>[Historical: Selected operation checkpoint: 9 October 2026](archive/2026-11-27-docs-implementation.md#selected-operation-checkpoint-9-october-2026)

<a id="function-reference-checkpoint-9-october-2026"></a>[Historical: Function reference checkpoint: 9 October 2026](archive/2026-11-27-docs-implementation.md#function-reference-checkpoint-9-october-2026)

<a id="architecture-refinement-checkpoint-9-october-2026"></a>[Historical: Architecture refinement checkpoint: 9 October 2026](archive/2026-11-27-docs-implementation.md#architecture-refinement-checkpoint-9-october-2026)

<a id="transport-correction-9-october-2026"></a>[Historical: Transport correction: 9 October 2026](archive/2026-11-27-docs-implementation.md#transport-correction-9-october-2026)

<a id="final-build-baseline-9-october-2026"></a>[Historical: Final build baseline: 9 October 2026](archive/2026-11-27-docs-implementation.md#final-build-baseline-9-october-2026)

<a id="core-firstworkbench-planning-checkpoint-20-october-2026"></a>[Historical: Core-first/workbench planning checkpoint: 20 October 2026](archive/2026-11-27-docs-implementation.md#core-firstworkbench-planning-checkpoint-20-october-2026)

<a id="first-coreworkbench-build-checkpoint"></a>[Historical: First core/workbench build checkpoint](archive/2026-11-27-docs-implementation.md#first-coreworkbench-build-checkpoint)

<a id="manual-live-mode-setup-21-october-2026"></a>[Historical: Manual live-mode setup: 21 October 2026](archive/2026-11-27-docs-implementation.md#manual-live-mode-setup-21-october-2026)

<a id="first-user-live-run-and-displayconfiguration-repair-21-october-2026"></a>[Historical: First user live run and display/configuration repair: 21 October 2026](archive/2026-11-27-docs-implementation.md#first-user-live-run-and-displayconfiguration-repair-21-october-2026)

<a id="connect-feedback-and-duplicate-attempt-repair-21-october-2026"></a>[Historical: Connect feedback and duplicate-attempt repair: 21 October 2026](archive/2026-11-27-docs-implementation.md#connect-feedback-and-duplicate-attempt-repair-21-october-2026)

<a id="combined-live-run-pdf-review-21-october-2026"></a>[Historical: Combined live-run PDF review: 21 October 2026](archive/2026-11-27-docs-implementation.md#combined-live-run-pdf-review-21-october-2026)

<a id="implemented-operation-inventory"></a>[Historical: Implemented operation inventory](archive/2026-11-27-docs-implementation.md#implemented-operation-inventory)

<a id="review-findings-and-next-work"></a>[Historical: Review findings and next work](archive/2026-11-27-docs-implementation.md#review-findings-and-next-work)
