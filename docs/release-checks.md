# Release and installation checks

Version0.10.0 is a local wheel release. Public PyPI publication, hosted transport and
multi-user authorization are separate future actions; no external deployment/purchase
is implied. Old committed wheels/checksums remain immutable.

## Required local checks

```sh
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/pytest -q
.venv/bin/python -m build --wheel --no-isolation
```

SDK scripts exercise all39, optional profiles, typed/generic handoffs, quote/reference
guards and shared reconnects with fictional software fixtures only. Live data checks
are separate [bounded commands](api-testing.md). Unit/SDK success is not host semantic
accuracy, source authentication or entitlement for untested operations.

## True fresh-venv installation

Create a new venv without system-site packages, install the wheel and pinned runtime
dependencies, run pip check and scripts/check_installed_product.py with that interpreter
from outside the source tree. The script rejects editable/source imports, checks three
core CLI entrypoints, initializes standalone live/zero-budget MCP, checks all39/status
report and explicit hypothetical DCF. It loads no keys and makes no provider calls.
Workbench extra is optional and checked separately; Node is optional for DOM tests.

## Platform matrix

.github/workflows/product-smoke.yml builds/installs the wheel on Linux/macOS/Windows
with Python3.12. Standalone MCP is the portable path; shared Unix sockets are macOS/Linux
only. Cross-platform product-contract tests run everywhere and full suite on Unix.
Remote CI results must be observed before claiming a platform pass. The workflow uses
the official [checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) and
[setup-python](https://github.com/actions/setup-python/releases/tag/v7.1.0) actions.

## Evidence for this release

Final unit/SDK/DOM/clean-install/platform outcomes and artifact hash are recorded in the
current [implementation status](implementation.md) and ignored private product-release
report. Do not treat an added CI workflow as an observed remote pass. No financial keys
are passed to CI. Review host-reader/operator-assessment evidence is distinct from
automatic model behavior and the professor's excluded evaluation.

Observed local results: 647 offline tests, Ruff, browser/Node DOM, nine source and nine
installed-wheel SDK groups pass. True fresh-venv installation passed on macOS/Python3.12.10.
[Acceptance matrix](product-acceptance.md) separates live-provider/operator-reader/fixture
checks and remaining platform/model limits.
