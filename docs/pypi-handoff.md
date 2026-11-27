# First public PyPI release: handoff

The owner authorized implementation of the [release plan](pypi-release-plan.md) on
27 November 2026 and selected MIT. Authors, in order: Rishit Anand, Advait Sharma,
Arsalaan Alam, Tanvi Sanghai. Public emails were not supplied.

The public candidate is **margin-mcp 0.10.1**, retaining Python import margin and the
margin-mcp/margin-backend/margin-agent/margin-workbench commands. margin-mcp matches
the repository and primary interface. margin-research remains the host-skill name and
legacy local distribution name. Use a fresh environment when migrating distributions.

Metadata/license, public onboarding, source-distribution separation, artifact validation,
fresh-install checks and manual Trusted Publishing workflows are implemented. See
[release checks](release-checks.md) for exact commands, publisher fields and pending
account setup; [implementation](implementation.md) records measured local results.
No upload or new hosted CI pass is implied by this handoff.

Existing 0.10.0 wheels/checksums stay immutable. The user's active mtest owner remains
0.10.0 and is not restarted/upgraded. Prior live product evidence and small-context/model
limits are unchanged; no provider requests are authorized or needed for packaging.
Research evaluation and private-bundle material stay out of the public sdist/runtime.
Users supply their own keys; [credential guide](local-credentials.md).

Before publishing, commit/review the intended source, observe the new hosted validation,
complete the two pending-publisher/environment setups, and use the release workflow.
Record release commit, artifact hashes, index URLs and actual production installation.
