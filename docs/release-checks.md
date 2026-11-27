# Release and installation checks

The first public release is **margin-mcp 0.10.1**, Python 3.12+, MIT. The Python
import remains margin and the default MCP profile remains all39. Old local wheels
under releases/ are immutable. Hosted product checks passed on all three platforms and public-index installs passed;
see the [publication record](pypi-release.md) for exact source, runs and hashes.

## Local preparation

Use a new environment; do not upgrade the active 0.10.0 development owner as a release
check. Do not install legacy margin-research and margin-mcp into the same environment,
since they own the same import and commands.

```sh
python3.12 -m venv .release-venv
.release-venv/bin/python -m pip install -c requirements-dev.lock ".[dev,workbench,release]"
.release-venv/bin/python -m ruff check src tests scripts
.release-venv/bin/python -m ruff format --check src tests scripts
.release-venv/bin/python -m pytest -q
.release-venv/bin/python -m build
.release-venv/bin/python -m twine check --strict dist/*
.release-venv/bin/python scripts/check_distributions.py --version 0.10.1
.release-venv/bin/python scripts/check_release_install.py --version 0.10.1
```

Use a clean checkout/staging tree and empty dist/ for a new artifact build. On Windows
use Scripts/python.exe and run the portable tests from product-smoke.yml; the full
suite contains Unix-socket contracts. No build should read a provider credential file.
A release venv may be placed outside the checkout; .release-venv is ignored locally.

check_distributions.py checks metadata, four authors, MIT files, entrypoints, exact
version, JSON/static assets, runtime parity between archives, forbidden paths and known
credential patterns. Review provider-specific secrets and licensed content separately.
The sdist deliberately excludes research, private-bundle tooling, skills and historical
release artifacts. Product tests and their helper scripts remain self-contained;
repository-only research/bundle tests remain under tests/repository and run in the
full repository regression.

check_release_install.py creates three venvs **without system-site packages** and runs
from outside the checkout: wheel/base, sdist/base (isolated wheel build), and
wheel/workbench. It verifies actual installed console scripts, package/server version,
pip check, all39 zero-allowance live-mode status and hypothetical DCF. Base environments
must have no FastAPI; uvicorn can be installed transitively by the MCP SDK. Workbench checks include its entrypoint, static assets and
CLI-client HTTP contract using fictional data. The extracted sdist's product suite runs
in the workbench venv (portable subset on Windows). Provider keys and MARGIN_* values
are removed from child environments. No live-provider smoke is part of this process.

## GitHub workflows

product-smoke.yml runs on PRs/main/manual dispatch and builds both artifacts. It checks
portable contracts on Windows/Linux/macOS, full regression on Unix, metadata/archive
validation and all three fresh installation routes.

release.yml is manual. Run it first with version=0.10.1 and **publish=false**. It builds
once on Linux, stores the two distribution files and hashes, and checks those exact
artifacts on all three operating systems. Nothing is uploaded to an index in this mode.
The official actions are pinned to verified release commit hashes. For an already
published version, verify-published.yml accepts its version and successful source-run ID
and checks public hashes/installations without uploading again.

With publish=true, only a run from main can enter the index-publishing jobs. The
default route is build → three-platform installation → main-restricted PyPI environment
→ production artifact hashes and installed smoke. TestPyPI is optional: testpypi=true
adds a staging upload and exact staging-wheel hash/installed smoke before production.
A failed requested staging check prevents production publication. A cancelled run does
not publish. No rebuild occurs between validation and upload or between indexes. The production smoke checks base and workbench
installations. Build/test jobs have no OIDC publishing permissions; only the dedicated
index-upload jobs receive id-token: write.

If a staging upload or later gate fails, preserve the failed run and artifacts. Investigate
before rerunning; the same filename cannot be replaced on the index. Bump the candidate
version if artifact content changes. No publishing retries or skip-existing behavior
conceal a mismatched candidate.

## One-time account setup

Before the first publish=true run, configure the PyPI pending publisher. Configure
TestPyPI only if using the optional testpypi=true route; it has a separate account.
Use these exact fields and the index account's required security:

| Field | TestPyPI | PyPI |
| --- | --- | --- |
| Project name | margin-mcp | margin-mcp |
| GitHub owner | rishitttt | rishitttt |
| Repository | margin-mcp | margin-mcp |
| Workflow filename | release.yml | release.yml |
| GitHub environment | testpypi | pypi |

- [TestPyPI publishing settings](https://test.pypi.org/manage/account/publishing/)
- [PyPI publishing settings](https://pypi.org/manage/account/publishing/)
- [GitHub environment settings](https://github.com/rishitttt/margin-mcp/settings/environments)

The pypi and testpypi GitHub environments are configured with main-only branch policies.
Only pypi is required for a direct release. Add an appropriate release approval rule to pypi where available. A pending
publisher does not reserve the project name. No long-lived PyPI API token is needed.
Author metadata does not invite collaborators or grant account access.

TestPyPI dependency installation uses production PyPI separately; the staged wheel is
fetched with --no-deps and --only-binary=:all:. Do not combine indexes with
--extra-index-url. Index installation and rendering must be observed before marking
publication complete; both were observed for0.10.1. The production-install job uses an
explicit successful-upload/non-cancelled condition so optional staging skips do not
suppress it. The independent published-release workflow provides recovery verification. README installation commands describe the public interface;
current publication status is recorded here and in implementation.md.

## Evidence and limits

[Implementation status](implementation.md) records the candidate's actual local checks.
The [0.10.0 acceptance matrix](product-acceptance.md) is prior product evidence, including
[the old hosted run](https://github.com/rishitttt/margin-mcp/actions/runs/45976665943).
It is not a platform result for the new name/version/workflows. No new provider budget
has been allocated or spent by packaging. Host-model accuracy and broader company or
provider coverage remain separate from installation acceptance.

[Packaging plan](pypi-release-plan.md),
[official Trusted Publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/),
[TestPyPI guidance](https://packaging.python.org/en/latest/guides/using-testpypi/).
