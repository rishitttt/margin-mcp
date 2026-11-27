# PyPI package review — margin-mcp 0.10.1

Reviewed locally on 27 November 2026, macOS arm64 / Python 3.12.10. These are local
candidate results. Index publication and the new hosted three-platform workflow
have not been observed.

## Review result

No unresolved packaging defect was found in the reviewed local candidate. The wheel
and source archive install independently of the checkout, share identical runtime
files, and expose the intended commands and 39-tool default. The release still needs
an identified reviewed commit, hosted validation and owner-side publisher setup before
an observed TestPyPI/PyPI release can be recorded.

## Findings resolved

| Finding | Resolution and evidence |
| --- | --- |
| No software license or author metadata | Standard MIT LICENSE, SPDX/license-files metadata and all four names in supplied order; archive metadata checked |
| Legacy distribution name obscured the MCP entrypoint | Public name margin-mcp; Python import margin and skill name margin-research retained; fresh-environment migration documented |
| Duplicate version constants and stale egg-info | Single margin.__version__ used by metadata and MCP; clean staging; only margin in top_level.txt |
| Incomplete source archive test dependencies | Repository-only study/bundle tests separated; required product helpers included; extracted sdist passes 637 tests |
| Risk of losing regression coverage during moves | AST comparison found no removed test functions; full repository has 654 passing cases, including seven new archive-guard cases |
| Relative PyPI README links and developer-specific onboarding | Public HTTPS documentation links, complete MCP config, own-key setup and migration guidance; local/repository targets checked |
| Ambiguous optional workbench dependency boundary | FastAPI remains optional; direct Starlette dependency declared; base and workbench installations checked separately |
| Untested release-file selection and accidental private content | Exact archive name/metadata/resource checks, runtime file-set/byte parity, forbidden paths, token-pattern scan and exact comparison against the two locally configured provider secrets; no matches |
| Publishing authentication and artifact drift | Dedicated OIDC-only publishing jobs, SHA-pinned official actions, non-publishing default, main restriction, staging/production wheel checks and both archive hashes checked against index metadata |
| Private bundle builders selecting the old wheel name | New builds select margin_mcp wheels; relocatable helper still accepts an explicitly supplied legacy wheel; no private bundle or evaluation run was performed |

Financial calculation, provider-admission, quote/reference and reporting logic were
not changed. Runtime source changes are the shared software version and its import.
The protocol contract remains margin.mcp.v1. Dependency versions were resolved in a
separate release-tools environment and captured in requirements-dev.lock; neither
existing user environments nor the active 0.10.0 owner were upgraded/restarted.

## Observed checks

| Check | Result |
| --- | --- |
| Full repo suite, original development environment | 654 passed |
| Full repo suite, newly resolved release environment | 654 passed |
| Ruff lint / formatting | Passed; 117 Python files |
| Final isolated build | Wheel and sdist built successfully; wheel built from sdist |
| Twine check --strict, both final archives | Passed |
| Archive metadata, contents and runtime parity | Passed; 65 wheel members / 112 sdist files |
| Exact locally configured provider-key scan | Both values checked across 177 archive members; zero matches; no values printed |
| Fresh wheel/base environment | Entry scripts, pip check, all39/status, version and hypothetical DCF passed; no FastAPI |
| Fresh sdist/base environment | Independent isolated build/install; same installed-product smoke passed |
| Fresh wheel/workbench environment | Four console commands, UI/static assets and HTTP CLI-client contract passed |
| Extracted source archive product suite | 637 passed with the fresh workbench environment |
| Workflow validation | actionlint 1.7.12 passed for both workflows |
| Documentation targets / git whitespace | Checked; no missing local/repository targets or whitespace errors |
| Existing committed release artifacts | No changes |

The MCP SDK installs uvicorn transitively even for a base installation. The first
minimal-install check incorrectly assumed uvicorn would be absent; this checker and
the docs were corrected, and final fresh-install checks passed. A transient version
re-export mistake was also caught by collection and fixed before the successful
regressions/build. No runtime guard was relaxed. Earlier restricted-sandbox socket
failures are separate from code defects; the suite passed with local socket access.

## Local candidate artifacts

Artifacts are under dist/pypi-0.10.1. They were built from a clean temporary staging
copy of the reviewed working files based on commit
80182334f5020d309fbb18476b46e46e079520c4, before the release preparation was committed
as 50c3131. See [publication record](pypi-release.md) for current hosted/index status. Input hashes,
install reports, the failed first install log and final build/validation logs are
retained under ignored reports/private/pypi-0.10.1. The hosted workflow must build and
validate its own artifacts from the eventual reviewed commit; those hashes can differ
from this local candidate. The same built bytes pass validation and upload; when staging is selected, they are
promoted unchanged between TestPyPI and PyPI.

| Artifact | SHA256 |
| --- | --- |
| margin_mcp-0.10.1-py3-none-any.whl | b76be395b0238964458a016deb9db7c9e2a4de535f9b45bad21fd0ba9733d7f9 |
| margin_mcp-0.10.1.tar.gz | c0d601a3090fbf699157f5225bd53565a1de02e262860885d3d49db8d99d36fe |

## Remaining release gates

- Review/commit the intended source and observe the new hosted workflow. The older
  0.10.0 hosted results do not establish a 0.10.1 hosted pass.
- Configure the PyPI pending publisher; TestPyPI setup is optional. Follow the exact [release-check fields](release-checks.md#one-time-account-setup).
- Run the publishing workflow and observe the requested index installations and pages.
  Do not mark an unobserved upload complete or reuse a filename for changed artifacts.

No live provider requests, model evaluations, source-authentication claims or provider
redistribution rights follow from these packaging checks. Public email addresses and
PyPI collaborator access were not inferred from the author list.
