# Margin 0.9.0

Two-step supplied-text claim review/content sentiment, internally bound references,
atomic transient sessions and optional three-tool review-simple profile. Existing
finance, retrieval and advanced review APIs remain. Host supplies judgments; no server
LLM, database or independent original verification.

[Wheel](margin_research-0.9.0-py3-none-any.whl) · [SHA-256](SHA256SUMS) ·
[Manual installation/test](../../docs/mcp.md#two-step-review-090) ·
[Validation/limits](../../docs/implementation.md).

470 offline tests and official SDK source/installed-wheel checks pass. No real API or
model calls for this build. Active installations are not automatically upgraded; a
backend restart loses prior transient IDs. Fresh model-host acceptance is still required.
