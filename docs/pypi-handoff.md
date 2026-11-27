# First public PyPI release: handoff

User decision, 27 November 2026: use a separate chat in this project for PyPI packaging;
continue product development in the existing chat. This document records readiness and
publication preparation; it does not publish/upload anything or choose a license.

## Start here

Read [AGENTS](../AGENTS.md), [quick handoff](../HANDOFF.md), [current implementation](implementation.md),
[acceptance](product-acceptance.md), [release checks](release-checks.md), and
[local-user credentials](local-credentials.md). Inspect branch/worktree state before
changes; coordinate parallel chats using separate branches/worktrees when appropriate.

## Existing deliverable

- Distribution name margin-research, software version 0.10.0, Python >=3.12, all 39 default.
- Runtime metadata: [pyproject.toml](../pyproject.toml); core under src/margin.
- Wheel and SHA256SUMS: [releases/0.10.0](../releases/0.10.0/README.md). It is committed
  and immutable. Do not rebuild/replace that wheel under the same committed path.
- Installed entrypoints: margin-mcp, margin-backend, margin-agent, optional margin-workbench.
- Wheel installation, 647 offline tests, browser/DOM, nine installed SDK groups and hosted
  Windows/Ubuntu/macOS checks pass. See actual scopes in acceptance; Windows is standalone,
  shared Unix backend only on macOS/Linux. No automatic host-model accuracy guarantee.
- Selected real provider pass succeeded B2/DrHTTP10/estimated credits7. User host smoke
  later observed INFY growth B1/D0, HUL readiness preview instead of margin, and no DCF
  tool call. Broad catalog response was about 65k characters; small-context behavior is
  parked for now. Do not claim context is proven to be the only cause.
- Citation/sentiment are host-reported judgments over supplied/read passages, not an
  independent source-authentication or market-sentiment service. No Margin LLM/corpus.
- Private provider credentials and captures stay outside Git/distributions. Users bring
  their own keys with --credentials-file or environment; see linked credential guide.

## Work for the packaging chat

1. Confirm the public distribution name is available/appropriate on PyPI and any TestPyPI
   target. Availability has not been checked. Current name is margin-research, not a
   claim that it is already published. Decide the first public version with the user;
   it need not be 1.0 simply because it is the first public upload.
2. Obtain the intended software license from the owner. There is currently no LICENSE
   file or pyproject license declaration. Add accurate public metadata, description,
   repository/docs links and classifiers as appropriate; do not guess author/license.
3. Review README/public install and own-key onboarding, console commands, supported Python/
   OS scope and optional workbench extra. npm is not required for Margin itself.
4. Build new release artifacts from an identified clean commit. If content/version/metadata
   changes, use a new versioned local release directory and keep 0.10.0 intact. Align
   pyproject, MCP software VERSION, tests and public docs; contract margin.mcp.v1 is a
   separate identifier. Scan/checksum both wheel AND sdist; source-distribution contents
   have not been validated as part of the 0.10.0 wheel acceptance.
5. Validate metadata (for example twine check), inspect archives for unwanted private/
   licensed/research material, install from artifacts in a fresh environment, and rerun
   relevant CLI/SDK/platform checks. Test installability from the chosen staging index
   before public release. Use official current PyPA/PyPI guidance for the upload workflow.
6. Configure publication credentials/Trusted Publishing in the release workflow as
   appropriate. PyPI publishing credentials are separate from financial-provider keys;
   financial-provider keys must not enter public builds or CI. Record the actual release
   commit/version/artifact hashes/index URL and measured installation result.
7. Update current docs/status/handoff after publication. Keep product development and the
   optional professor evaluation independent; publishing is not remote hosting and does
   not introduce a shared provider account or public data redistribution service.

## Scope remaining for development

Product pilot is usable. Small-context catalog/tool selection and model report copying
remain observed limits, parked by the user; broader company/endpoint coverage needs a
new explicit live allocation. No new provider calls are authorized by this handoff.
Public PyPI upload, name reservation, license choice, remote deployment and active-owner
restart were not performed in the development chat.
