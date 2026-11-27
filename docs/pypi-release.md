# margin-mcp 0.10.1 publication record

The owner authorized committing all release preparation and publishing on
27 November 2026. The public distribution is margin-mcp, import margin, software
version 0.10.1, MIT. Authors: Rishit Anand, Advait Sharma, Arsalaan Alam, Tanvi Sanghai.

## Prepared release

The [package review](pypi-package-review.md) records the code/archive review, local
candidate hashes, 654 repository tests, 637 source-archive tests and three fresh-install
routes. Provider keys/private captures remain ignored and excluded. The existing
0.10.0 wheels and active development owner are unchanged.

All release source, tests, metadata, license, public setup docs and workflows are
being committed together. Local artifacts under dist/pypi-0.10.1 and private evidence
under reports/private/pypi-0.10.1 are deliberately excluded from Git. The hosted release
workflow builds artifacts from the committed source and records their own hashes.

## Publication status

- Release preparation commit: [50c3131](https://github.com/rishitttt/margin-mcp/commit/50c3131f0b75e70d102217300f3cb434a2688faf), pushed to main.
- Hosted Windows/Linux/macOS validation: [product checks passed on Windows/Linux/macOS](https://github.com/rishitttt/margin-mcp/actions/runs/45988193730); [non-publishing release rehearsal running](https://github.com/rishitttt/margin-mcp/actions/runs/45988484694).
- GitHub environments: pypi and testpypi created, each restricted to main; no API tokens or provider secrets added. The owner confirmed that the PyPI pending publisher is saved. TestPyPI is optional and was not requested for this first production upload.
- PyPI upload: not performed yet. TestPyPI will be skipped for this release.
- Public-index installation checks and final artifact hashes: pending upload.

The owner has a PyPI account and offered to complete website steps. Website setup
registers the pending publisher; the GitHub workflow performs the actual upload.
See [exact publisher settings and release procedure](release-checks.md).

Update this record with the observed commit/run/index links and hashes. Never infer
publication or a platform pass from adding a workflow. No new live-provider allocation
is required or consumed by packaging/publication checks.

## Direct publication decision

TestPyPI is a useful upload rehearsal, not a PyPI prerequisite. After the owner
confirmed the production publisher, the release workflow was adjusted to support
direct publication after all build/platform-install gates. The optional testpypi input
retains staging for later use and enforces a successful staging check when selected.
Production checks still compare both archive hashes against index metadata and verify
base/workbench installations from the published wheel.
