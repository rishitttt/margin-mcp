"""Host-facing provenance rules; guidance is not source authentication."""

DATA_INSTRUCTIONS = """Never fabricate company data, financial values, dates, units, quotes or source provenance.
Use only actual tool-returned evidence or values explicitly supplied by the user.
Hypothetical examples are allowed only when the user requests/supplies them; label
their assumptions and never present them as retrieved company facts. Missing data,
held access, invalid inputs or a failed tool call are NOT permission to invent inputs
for a calculator. Ask for missing context or report unavailable/incomplete. For a
discovery-only task inspect capabilities/propose inputs; do not create financial values.
Preserve actual periods/basis/definitions/displays; do not invent dates to pass validation.
Do not expand financial labels into unsupported accounting inclusions/exclusions or
describe normalized report units as raw provider units. Readiness is field eligibility,
not source authentication; empty numeric rows are intentional. A finished same-key
request replays its result, not refreshed data or a different workflow.
These rules guide the host; Margin does not authenticate arbitrary caller-supplied facts.
"""

DATA_POLICY = {
    "version": "margin.data_policy.v1",
    "fabricated_company_data_allowed": False,
    "allowed_inputs": ["actual_tool_returned_evidence", "explicit_user_supplied_values"],
    "hypotheticals": "Only user-requested/supplied examples, explicitly labelled; never retrieved facts.",
    "on_missing_or_failed_data": "Ask for context or report unavailable; never invent calculator inputs, dates, units or sources.",
    "discovery_only": "Inspect capabilities and proposed inputs, not financial values or new retrieval.",
    "source_authentication": "Caller inputs and provider records are not independently authenticated originals.",
    "reporting": "Preserve exact returned financial definitions/units; do not invent accounting inclusions/exclusions. Readiness success is not source verification; same-key replay is not refreshed data.",
}

FINANCIAL_RECOVERY = (
    "This error is not financial evidence. Correct the requested workflow/inputs using its exact schema, "
    "or report missing data/access. Never invent replacement values, dates or metadata for a calculator. "
    "Annual growth compares annual periods; TTM sums four eligible quarters and is not growth. "
    "Do not retry a possibly dispatched request with a new key."
)

PLAN_RECOVERY = (
    "Use only a plan_id actually returned by margin_preview or margin_company_preview in this owner. "
    "A margin_company_finance preview creates NO generic plan_id: follow its next_steps to the SAME "
    "margin_company_finance tool with execute=true and a stable idempotency_key within authorization. "
    "Do not invent references, infer TTL expiry from an unavailable ID, or refetch to rescue a bad reference."
)
