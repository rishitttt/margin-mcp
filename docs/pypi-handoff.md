# First public PyPI release: handoff

The owner authorized implementation of the [release plan](pypi-release-plan.md) on
27 November 2026 and selected MIT. Authors, in order: Rishit Anand, Advait Sharma,
Arsalaan Alam, Tanvi Sanghai. Public emails were not supplied.

The published public release is **margin-mcp 0.10.1**, retaining Python import margin and the
margin-mcp/margin-backend/margin-agent/margin-workbench commands. margin-mcp matches
the repository and primary interface. margin-research remains the host-skill name and
legacy local distribution name. Use a fresh environment when migrating distributions.

Published via Trusted Publishing on 27 November 2026 from4ef3d0e. Hosted platform
checks passed and independent public-index base/workbench installations passed.
See the [publication record](pypi-release.md) for exact commits, run links, hashes and
the corrected post-upload job condition. [Release checks](release-checks.md) describe
future releases; TestPyPI staging is optional.

Existing 0.10.0 wheels/checksums stay immutable. The user's active mtest owner remains
0.10.0 and is not restarted/upgraded. Prior live product evidence and small-context/model
limits are unchanged; no provider requests are authorized or needed for packaging.
Research evaluation and private-bundle material stay out of the public sdist/runtime.
Users supply their own keys; [credential guide](local-credentials.md).

For future changes, bump the software version, commit/review the source and follow
the release workflow. Never replace uploaded files or old committed wheels. Both
GitHub release environments are restricted to main.
