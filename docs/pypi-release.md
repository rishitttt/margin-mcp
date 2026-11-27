# margin-mcp 0.10.1 publication record

**Published on PyPI on 27 November 2026, 16:48 IST (11:18 UTC).**
[PyPI project](https://pypi.org/project/margin-mcp/0.10.1/)

```sh
python -m pip install margin-mcp==0.10.1
# Optional local UI/API:
python -m pip install "margin-mcp[workbench]==0.10.1"
```

Python 3.12+, import margin, MIT. Authors in supplied order: Rishit Anand,
Advait Sharma, Arsalaan Alam, Tanvi Sanghai. No public email addresses were inferred.

## Source and commits

- [50c3131](https://github.com/rishitttt/margin-mcp/commit/50c3131f0b75e70d102217300f3cb434a2688faf): complete release preparation, metadata/license/authors, archive repair, public docs, checks and workflows.
- [4ef3d0e](https://github.com/rishitttt/margin-mcp/commit/4ef3d0eeb37a9e26fc48754c86b45016671d4f7a): optional TestPyPI route and hosted evidence. **The published files were built from this commit.**
- [6167d42](https://github.com/rishitttt/margin-mcp/commit/6167d429f25962be1f9b172e16f20a8d5a217160): correct post-upload job handling of skipped optional ancestors; add independent published-release verification. No package source/files were changed or re-uploaded.

All intended release source and documentation are committed. Credentials, local build
outputs and private evidence remain ignored. Existing 0.10.0 wheels/checksums and the
active development owner were not changed. The [local candidate review](pypi-package-review.md)
is separate from the final hosted/public artifact hashes below.

Release source tag: [v0.10.1](https://github.com/rishitttt/margin-mcp/tree/v0.10.1),
pointing to4ef3d0e. The workflow-only correction follows in6167d42.

## Observed validation and publication

| Check | Observed outcome |
| --- | --- |
| Local full regression | 654 passed in original and newly resolved release environments |
| Local extracted-source suite | 637 passed |
| Lint/format, isolated build, strict Twine and archive checks | Passed |
| [Product checks for50c3131](https://github.com/rishitttt/margin-mcp/actions/runs/45988193730) | Windows/Linux/macOS passed |
| [Non-publishing release rehearsal](https://github.com/rishitttt/margin-mcp/actions/runs/45988484694) | Build and the same hosted artifacts' three-platform installs passed; no upload |
| [Product checks for the published source4ef3d0e](https://github.com/rishitttt/margin-mcp/actions/runs/45988881853) | Windows/Linux/macOS passed |
| [Production release45988924022](https://github.com/rishitttt/margin-mcp/actions/runs/45988924022) | Build, all three installation gates and PyPI upload passed; TestPyPI skipped |
| [Product checks after the workflow correction](https://github.com/rishitttt/margin-mcp/actions/runs/45989712236) | Windows/Linux/macOS passed |
| [Independent published-release check45989748057](https://github.com/rishitttt/margin-mcp/actions/runs/45989748057) | Public wheel download/hash, both index artifact digests, fresh base and workbench installs passed |
| Public metadata | Exact name/version, Python requirement, MIT, ordered four-author field, README and two-file inventory verified |
| Public PyPI page | Browser review confirmed rendered install/configuration/feature sections and all four author credits |
| Exact configured-provider-secret check | Both known values checked against 177 hosted archive members; zero matches; values never printed |

Installed smoke checks cover actual console commands, pip check, package/server version,
all39 zero-allowance status, hypothetical DCF and optional static/HTTP CLI-client behavior.
No live-provider requests, account probes, model evaluations or owner restarts were needed.
Software checks do not authenticate financial facts or establish broader provider coverage.

## Published artifacts

Both PyPI-reported SHA256 values match the artifacts from the successful hosted build.

| Artifact | Bytes | SHA256 |
| --- | --- | --- |
| margin_mcp-0.10.1-py3-none-any.whl | 164225 | 0d2a59d53be34e124fa9a3556f6bbe93912a426d17e36a2de351fc22c611a6c7 |
| margin_mcp-0.10.1.tar.gz | 223021 | c6ec4798758069964fd692482905b45adefa4242402c695d60fea8632e87f8ad |

Exact hosted artifacts are also retained locally under dist/published-0.10.1. Ignored
reports/private/pypi-0.10.1 contains the hosted artifact report, public metadata, install
verification log and earlier local evidence. The earlier local candidate hashes differ
from the hosted build and are not the published checksums. Uploaded files stay immutable.

## Publishing configuration and TestPyPI

The owner registered the pending PyPI publisher. It created the project on the first
successful upload. GitHub environments pypi and testpypi are restricted to main; only
dedicated upload jobs receive id-token: write. No long-lived publishing token or financial
provider keys were added to CI.

TestPyPI is an optional upload rehearsal, not a PyPI prerequisite. This release used
direct production publishing after all build/platform-install gates. Setting testpypi=true
requires separate staging account/publisher setup and a successful staging check before
production. Build and upload use the same artifact bytes.

## Post-upload workflow correction

The first production upload succeeded, but GitHub skipped its dependent production-install
job because the optional staging ancestors were skipped. The job now explicitly requires
a successful PyPI job and a non-cancelled run. verify-published.yml independently downloads
the exact artifacts from a specified upload run, compares both digests to PyPI, and tests
public base/workbench installations. It passed for this release; no re-upload occurred.

For future releases, follow [release checks](release-checks.md), bump the single software
version, review the committed changes, run validation and publish new immutable artifacts.
