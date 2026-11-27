# First public PyPI release plan

Reviewed 27 November 2026 against clean `main` commit
`80182334f5020d309fbb18476b46e46e079520c4` and current official packaging guidance.
This is the preparation plan requested by the owner. Implementation was authorized after this review. See release-checks.md for current
preparation results and remaining account/publishing steps; no upload is implied.

## Decisions and recommendations

| Item | Decision / recommendation |
| --- | --- |
| Software license | **MIT**, selected by the owner in this chat |
| Authors, in order | **Rishit Anand, Advait Sharma, Arsalaan Alam, Tanvi Sanghai** |
| Public email addresses | None supplied; names-only author metadata |
| Distribution name | **margin-mcp**, selected for the public MCP distribution |
| Python import | Keep **margin** |
| Main installed command | Keep **margin-mcp** |
| First public version | **0.10.1**, a new packaging release after local 0.10.0 |
| Build backend | Retain setuptools and the existing src layout |
| Artifacts | One pure-Python wheel plus one source distribution |
| Publishing | GitHub Actions Trusted Publishing; direct PyPI by default, optional TestPyPI rehearsal |

The public name was changed to margin-mcp during implementation: it matches the repo
and primary console command. margin-research remains the separate host-skill name.
There is no requirement to call a first public upload 1.0.0. The previously committed
0.10.0 wheel and checksum must stay immutable.

Read-only JSON API checks returned HTTP 404 for both `margin-research` and `margin-mcp`
on both PyPI and TestPyPI. That means no project was returned at review time; it is
not a reservation or a guarantee that either index will accept registration. Recheck
the selected name immediately before publication. Normalized spellings do not create
different projects. A pending publisher also does not reserve a name.
[Name normalization](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#name),
[pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

## What the product is

Margin runs on the user's machine. It combines BharatStock REST and upstream Drishti
MCP access with deterministic finance calculations and host-supplied citation and
content-sentiment review. It has no product LLM, market corpus or automatic forecasting
service. Users supply their own provider credentials and allowances.

| Repository area | Role and distribution implications |
| --- | --- |
| `src/margin/core` | Configuration, strict schemas, operation registry, plans/runs, transient results and company-finance orchestration |
| `src/margin/providers` | BharatStock REST, guarded Drishti MCP transport and fictional offline fixtures |
| `src/margin/policy` | Process-local request/estimated-credit admission; not account balances |
| `src/margin/analysis`, `finance` | Financial facts, units, scope/period checks, ratios, reporting, FCFF and explicit-assumption DCF |
| `src/margin/evidence`, `protocols` | Sanitization, source/passages, immutable review packets, exact quote/reference validation and host judgments |
| `src/margin/interfaces/mcp` | Portable stdio server, 39-tool default, optional profiles and optional Unix-socket state owner |
| `src/margin/interfaces/agent` | JSON CLI for the local HTTP workbench API, credential-file parser and optional private-bundle launcher |
| `src/margin/interfaces/workbench` | Optional FastAPI/uvicorn local HTTP interface and packaged static assets |
| `src/margin/resources` | Reviewed Drishti schema snapshot loaded through importlib.resources; required in every wheel |
| `skills` | Repo-maintained host skill, currently outside the installed wheel |
| `scripts`, `tests` | Software checks, bounded live checks, private bundle helpers and mixed product/research tests |
| `research`, `packaging` | Separate study/private-bundle consumers; not product runtime dependencies |
| `docs`, `releases`, `.github` | User/developer guides, immutable old wheels and existing installation CI |

The public install should work without a Git checkout. Standalone MCP is the primary
route on Windows, Linux and macOS. The Unix shared backend is macOS/Linux only.
The CLI uses HTTP through the optional workbench, whereas `margin-backend` owns the
MCP Unix socket: these are different interfaces and must be described accurately.

## Repository and build checks

The review inventoried 215 tracked files, parsed all 54 runtime Python modules and
checked imports, resources, entrypoints, version references, test/helper dependencies,
CI, docs and existing artifacts. No product import depends on research or packaging
helpers. No provider calls or active-backend changes were made.

| Check performed in this review | Result / qualification |
| --- | --- |
| Git state before review | Clean main, tracking origin/main |
| Ruff lint | Passed |
| Ruff formatting | All 111 checked Python files already formatted |
| Repository regression | **647 passed** after allowing temporary local Unix sockets |
| Initial sandbox regression | 632 passed; 15 Unix-socket tests failed with Operation not permitted; preserved as an environment limitation, not a code fix |
| Existing environment dependency consistency | pip check passed |
| Public dependency metadata | All 11 exact runtime/optional/dev dependency versions returned HTTP 200 on PyPI |
| Trial artifact build | sdist and wheel built successfully from a temporary git-archive snapshot; wheel built from the sdist |
| Trial build environment | Existing development interpreter, build 1.6.1, setuptools 84.2.0, no build isolation |
| Wheel contents | 54 Python files, required Drishti JSON, four workbench assets and distribution metadata |
| Missing wheel metadata | Authors, license, project URLs and classifiers absent |
| Source archive | 164 files; includes research/pilot.py and private-bundle helpers, plus an incomplete set of scripts needed by its tests |
| Source archive test collection | **Fails**: missing scripts/check_drishti_review.py and scripts/demo_mcp_review.py; evaluation modules are also omitted despite evaluation tests being included |
| Credential-shaped archive paths | No .env, providers.env, connection.json, private/log directories or database files found; a full content/secret audit remains a release gate |
| Twine metadata/readme validation | Not run; Twine is not installed in the development environment |
| New clean-install/platform/index smoke | Not rerun here; prior 0.10.0 evidence is in product-acceptance.md, and final public artifacts need their own checks |

The temporary wheel differs from the committed wheel only in top_level.txt and the
corresponding RECORD. The committed wheel advertises an obsolete `margin_mcp` top-level
name even though its package files are under `margin`. Clean staging avoids carrying
stale egg-info into the public build. No old artifact was overwritten.

Trial artifacts/logs are under the local temporary directory
`/var/folders/x2/10xdwkwd71j_wtx1zw8b9v080000gn/T/margin-pypi-review-yqd7a_m8`.
They are diagnostic 0.10.0 builds, not approved upload artifacts.

The implemented workflow makes TestPyPI optional. Direct publication still requires
all build/platform gates; selecting staging requires its successful completion before
production. See [publication record](pypi-release.md) for the owner-confirmed publisher.

## Implementation sequence

### 1. Complete metadata and licensing

Add the standard MIT LICENSE text with the correct project copyright attribution.
Credit the authors in README and pyproject metadata in the exact supplied order:

```toml
authors = [
  {name = "Rishit Anand"},
  {name = "Advait Sharma"},
  {name = "Arsalaan Alam"},
  {name = "Tanvi Sanghai"},
]
license = "MIT"
license-files = ["LICENSE"]
```

Raise the minimum setuptools build requirement from 75 to at least 77.0.3 for modern
SPDX/license-files support. Add repository, documentation and issue-tracker URLs;
use accurate keywords and supported Python/OS/topic classifiers. Do not add the
deprecated license classifier in place of the SPDX field. Keep maintainer metadata
for actual ongoing maintainers; author credit does not grant PyPI account access.
[Metadata guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/),
[license metadata examples](https://packaging.python.org/en/latest/guides/licensing-examples-and-user-scenarios/).

MIT allows broad reuse, including commercial modification and redistribution, while
requiring retention of its copyright and permission notice. The software license
does not license upstream financial data or grant provider subscriptions.
[MIT license](https://opensource.org/license/mit).

### 2. Set the public version and dependency policy

Use 0.10.1 unless the owner chooses another public version. Align pyproject.toml,
the MCP software VERSION, the version assertion in test_typed_previews.py, installed
smoke expectations and current release docs. Keep protocol identifiers such as
margin.mcp.v1 independent from software versioning. A version-equality check should
catch future metadata/server drift.

Retain the tested exact runtime pins for the first upload. Both httpx and httpx2 are
intentional: the REST/CLI paths use httpx, and the Drishti SDK adapter uses httpx2.
Keep FastAPI/uvicorn under the workbench extra. Review the direct Starlette import
against its dependency declaration, and document that margin-workbench needs the extra.
Build/check/publish tools belong in development/release tooling, not runtime dependencies.
Update requirements-dev.lock whenever declared pinned dependencies change. Its current
macOS/Python 3.12 snapshot is not a cross-platform reproducibility guarantee.

### 3. Write public installation and usage documentation

Rewrite the README for a new user: product purpose, Python requirement, installation,
complete MCP host configuration, own-key setup, zero-allowance verification, optional
workbench/CLI, platform limits, license and authors. Use public absolute HTTPS links
for docs and images so the PyPI description works independently of GitHub's renderer.
Remove development-machine upgrade instructions from current public onboarding and
retain historical material in the archive.

Planned commands after publication:

```sh
python -m pip install margin-mcp
margin-mcp --help
python -m pip install "margin-mcp[workbench]"
margin-workbench --help
```

Use a virtual environment and the platform's installed executable path in host config.
State that default mode is synthetic; show explicit live mode and explicit process
allowances for own-key usage. No provider key is needed for the release smoke.
`margin-agent` needs a running local HTTP backend; installing its command alone does
not start that backend. Explain the skill's separate installation route; do not imply
that pip installs or activates a host skill. No global skill installation is part of
this release.
[PyPI README guide](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/).

### 4. Make the source distribution deliberate and self-contained

Keep runtime source, required data/static assets, license, README, metadata, relevant
public docs and a runnable product test set. Exclude research evaluation/task material,
private-bundle tooling and personal configuration from public artifacts. Keep old wheels
in the repo if desired, but do not nest them in the new source archive.

Fix the mixed test/helper boundary instead of shipping a test directory that cannot
collect. Identify product tests versus repository-only research/private-bundle tests,
including pilot-dependent cases inside test_agent.py and mixed cases in test_evaluation.py.
Include helpers required by retained tests. Preserve repository coverage when separating
these tests; the public sdist suite can have a different documented count.

Revise MANIFEST.in and narrow setuptools discovery to intended margin packages.
Ensure retained public documentation links resolve within the distribution or use public
URLs. Build from clean staging so cached build/egg-info cannot affect selection.
[Setuptools file-selection guidance](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html).

### 5. Add artifact validation to CI

Extend the existing product-smoke workflow and add a dedicated release workflow.
The release gates are:

1. Repository Ruff/format and all offline regressions pass.
2. An isolated `python -m build` produces a wheel and sdist from the intended clean commit.
3. `python -m twine check --strict dist/*` passes, with manual public README/link review.
4. Both archives pass content/secret checks, including required assets and license files;
   no provider credentials, private captures, licensed response dumps or study artifacts.
5. The extracted sdist builds a wheel and its documented product tests collect and pass.
6. Fresh environments without system-site packages install the wheel and sdist-derived
   wheel from outside the checkout; pip check, actual console entrypoints, all39 status
   and explicit hypothetical DCF pass. Clear provider credentials and use zero allowances.
7. Test the minimal base installation separately from [workbench]; verify static assets
   and HTTP/CLI behavior with the extra. Base MCP must not need FastAPI installed.
8. Check final artifacts on Windows, Linux and macOS with Python 3.12. Add newer Python
   versions only with observed results and accurate claims. Shared Unix checks run on Unix.
9. Record commit, version, wheel/sdist SHA256 hashes, environment and actual test outcomes.

Use the existing synthetic/SDK tests; do not repeat the spent live-provider allocation.
The first no-isolation trial build in this review is not a replacement for isolated
release builds or fresh dependency resolution.
[Build/distribution tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

### 6. Configure accounts and Trusted Publishing

Set up the owner's PyPI and separate TestPyPI accounts, verified email and required
account security. Configure matching pending publishers for owner `rishitttt`, repository
`margin-mcp`, the chosen project name, exact release workflow filename and separate
`testpypi` / `pypi` GitHub environments.

Use the official pypa/gh-action-pypi-publish action. Build/test in jobs without publishing
permissions; allow `id-token: write` only in dedicated publishing jobs. These jobs
download previously validated artifacts. Keep production publishing on an intentional
release trigger with environment controls; ordinary main pushes and pull requests must
not publish. Use verified action versions/SHAs when implementing the workflow.

A pending publisher supports the first upload, so a permanent broad API token or manual
bootstrap upload is unnecessary. Provider keys do not belong in build/publishing CI.
[PyPA publishing workflow](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/),
[first-project Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

### 7. Stage and publish the same validated artifacts

Upload the final candidate to TestPyPI, inspect its rendered page, and install its exact
wheel in a fresh environment. Install dependencies separately from production PyPI;
then install the exact TestPyPI package with `--no-deps --only-binary=:all:`. Do not mix
indexes with --extra-index-url. Run installed-product smoke again and verify hashes.
[TestPyPI guide](https://packaging.python.org/en/latest/guides/using-testpypi/).

Promote the same validated wheel/sdist bytes to production PyPI after the owner is ready
to make the public release. Do not rebuild between the staging and production jobs.
If staged content changes, produce a new candidate version and repeat validation.
An rc rehearsal and a final version are different artifacts; the final artifacts must
also be checked. Upload only the two intended distribution files, not an entire historical
release directory.

After upload, install the exact production version from PyPI into a new environment and
repeat minimal CLI/MCP/DCF and optional-workbench smoke. Save index links and downloaded
artifact hashes. Only then mark public release complete in current docs/handoff.

### 8. Record maintenance and recovery

Add release notes for the public version with installation requirements and known limits.
If an uploaded release is broken, publish a corrected version; where appropriate yank
the broken release with a reason. Yanking is non-destructive and exact pins can still
select a yanked version.
[PyPI yanking](https://docs.pypi.org/project-management/yanking/).

Author metadata/README credit is separate from PyPI collaborator access. No collaborator
invitations are implied by adding the four names. Record account ownership separately
if the team later wants multiple people to maintain releases.

## Planned file changes

| File / area | Intended change |
| --- | --- |
| LICENSE | Standard MIT text and accurate copyright attribution |
| pyproject.toml | Version, four authors, SPDX/license-files, URLs/classifiers, backend minimum and intended package discovery |
| README.md, docs/mcp.md, docs/local-credentials.md | Public pip installation, working onboarding links/config and interface/extra distinctions |
| MANIFEST.in | Deliberate public sdist contents and exclusions |
| tests and necessary helper scripts | Self-contained distributed product tests; preserve repo-only research/private tests |
| src/margin/interfaces/mcp/tools.py | Aligned software version; no financial behavior change intended |
| requirements-dev.lock / release tooling | Consistent build/metadata-validation dependencies if declarations change |
| .github/workflows/product-smoke.yml | Wheel plus sdist and minimal/extra install validation |
| .github/workflows/release.yml | Dedicated build, staging, smoke and Trusted Publishing jobs |
| docs/release-checks.md, implementation.md, handoff | Actual release evidence, limits, hashes and public install status |

## Completion criteria

The release is complete when metadata and MIT attribution are accurate, both archives
are public-safe and self-contained, final artifact checks pass, the staging install
passes, and the exact published production version installs and passes its documented
smoke checks. Planning, a successful build, or an unobserved CI run alone does not meet
that standard.
