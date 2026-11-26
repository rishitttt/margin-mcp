"""Frontend tool views over the same state owner; not an authorization boundary."""

from __future__ import annotations

import copy
import json

from mcp import types
from mcp.shared.exceptions import MCPError

from margin.core.contracts import encoded_size
from margin.core.validation import validation_summary
from margin.interfaces.mcp.policy import DATA_INSTRUCTIONS
from margin.interfaces.mcp.tools import DIRECT_REVIEWS

REVIEW_TOOLS = frozenset(DIRECT_REVIEWS) | {
    "margin_status",
    "margin_catalog",
    "margin_result",
    "margin_review_sources",
}
SIMPLE_TOOLS = frozenset({"margin_status", "margin_prepare_review", "margin_submit_review"})
SIMPLE_INSTRUCTIONS = (
    DATA_INSTRUCTIONS
    + """Margin review-simple exposes only status, prepare and submit.
Use the actual user's source text and task. If text, claims or required dates are
missing, ASK the user; do not invent an example company/document or run a sample.
Call margin_prepare_review with supplied text/metadata, ordered claim texts (or [] for
sentiment only) and optional scope. Keep record_date separate from publication_date;
unknown publication is null, not an unknown record date. Margin registers passages
and binds all source/passage/packet references internally. Preparation is NOT completion.
Read the returned text, assess claims in its order and annotate content sentiment
only for the requested scope. Submit exact quote substrings without ellipses, verdicts
and rationales with the ONE returned review_id via margin_submit_review. No URLs or
invented IDs in that field. No financial numeric checker is needed for maturity levels.
Submit sentiment exactly when prepared. Report only the final returned rows/counts,
complete flag and source limits. A completed review may find insufficient/contradicted
evidence; its support audit can be incomplete without missing assessments. No Margin
LLM/browser/provider call or original authentication. Host judgments are unverified.
Unknown/expired reviews stop; never restart, reset budgets or refetch to rescue them.
Optional why is a visible brief action summary, not hidden reasoning.
"""
)
REVIEW_INSTRUCTIONS = (
    DATA_INSTRUCTIONS
    + """Margin local review profile exposes only its advertised tools.
Prefer margin_prepare_review then margin_submit_review for supplied-text tasks; Margin
binds dates/source/packet references and returns one report. Legacy tools are advanced.
Citation review is optional, not a prerequisite for ordinary retrieval/math. The
citation_protocol response distinguishes supplied-text review, host source-reading
handoff and insufficient-evidence/inventory fallback. host_profile.host_read_sources
is a caller declaration; search alone does not imply reading, and missing is unknown.
If originals are needed, use actually available host tools, register exact passages
actually read and prepare a new packet. Never relabel summaries as originals or infer
authentication from capability. Margin does no source reading or LLM inference.
margin_check_numeric_claim compares financial facts, not maturity/certification levels
or ratings. Use passage-based claim review for CMMI Level 5; never invent a financial
unit or reporting basis to fit a number in prose.
Use margin_status to inspect software version, interface profile and shared-owner state.
Use typed review tools with their EXACT host-advertised inputSchema at top level;
no function/arguments wrapper. tools/list is protocol discovery, not a callable tool.
Evidence/sentiment function identifiers are labels, not tool names. margin_review is
not exposed in this profile. Catalog discovery is scoped to review functions only.
Register supplied source text/locators or import existing retained results. No attachment
download, provider connection, data execution or Margin-side LLM is exposed here.
Citation preparation takes claims with source_ids. Sentiment preparation takes source_ids,
issuer, aspect, flat from/to and date_basis, not text/window. Preparation returns actual
packet_id/hash; never use a run ID or invent a hash. Follow next_steps.mcp_execution.tool,
merge bound_arguments with every required_host_field, then validate against that tool's
schema. Partial bindings are not executable until the host supplies missing fields.
Citation uses submit_assessment; sentiment uses submit_annotations. The host supplies
reviewer metadata, semantic judgments and exact supporting quotes; Margin validates
references/quotes and aggregates without independently authenticating originals.
original_document_verified is source authenticity, not TTL. expires_at concerns packet
expiry; an expired source/packet must not cause a hidden fetch, restart or budget reset.
Changing frontend profiles does not renew allowance or replace the shared state owner.
Optional why is one brief visible summary, never hidden reasoning. Recording belongs
to the operator's backend; its logs do not capture host parser failures/final prose or
this frontend's profile projection. Record the profile in experiment configuration.
"""
)


class ToolView:
    def __init__(self, inner, profile="all"):
        if profile not in {"all", "review", "review-simple"}:
            raise ValueError("Unknown MCP tool profile.")
        self.inner, self.profile = inner, profile
        self.tools = {
            name: copy.deepcopy(tool)
            for name, tool in inner.tools.items()
            if profile == "all" or name in (REVIEW_TOOLS if profile == "review" else SIMPLE_TOOLS)
        }
        if profile == "review-simple":
            self.tools[
                "margin_status"
            ].description = "Inspect package/profile and recording. Supplied-text review works locally without provider keys or credits; disconnected providers do not block it. Requires actual user text/task, no Margin LLM or browser."
        if profile == "review":
            catalog = self.tools["margin_catalog"]
            catalog.input_schema["properties"]["group"] = {
                "enum": ["all", "review"],
                "default": "review",
            }
            catalog.description = "Discover exact local review function schemas and typed routes only. all means all review functions in this profile. Use each typed tool's advertised inputSchema, top-level; function identifiers are not callable tools. No provider calls."

    async def call(self, name, arguments):
        if self.profile != "all" and (not isinstance(name, str) or name not in self.tools):
            target = next(
                (tool for tool, function in DIRECT_REVIEWS.items() if function == name), None
            )
            hint = (
                f" Use {target} with its top-level advertised schema."
                if target in self.tools
                else " Use the tools advertised in this profile; prepare a high-level review with actual user material."
            )
            raise MCPError(-32602, "Tool is not exposed in the review profile." + hint)
        forwarded = arguments
        if self.profile == "review" and name == "margin_catalog":
            forwarded = copy.deepcopy(arguments) if arguments is not None else {}
            try:
                if not isinstance(forwarded, dict) or encoded_size(forwarded) > 65536:
                    raise ValueError
            except (ValueError, TypeError, RecursionError):
                raise MCPError(
                    -32602, "Use a finite catalog argument object within 64 KiB."
                ) from None
            problem = validation_summary(self.tools[name].input_schema, forwarded)
            if problem:
                raise MCPError(-32602, "Review-profile catalog arguments are invalid. " + problem)
            forwarded["group"] = "review"
        result = await self.inner.call(name, forwarded)
        if result.is_error or not isinstance(result.structured_content, dict):
            return result
        if name not in {"margin_status", "margin_catalog"}:
            return result
        body = copy.deepcopy(result.structured_content)
        if name == "margin_status":
            body["data"].update(tool_profile=self.profile, advertised_tools=len(self.tools))
            if self.profile == "review-simple":
                body["data"]["review_readiness"] = {
                    "local": True,
                    "provider_auth_required": False,
                    "server_llm_required": False,
                    "user_material_required": True,
                }
        elif self.profile == "review":
            for row in body["data"]["groups"].get("review", []):
                row.pop("generic_mcp_execution", None)
            body["data"]["schema_lookup"] = (
                "Use the selected typed review tool's exact host-advertised inputSchema at top level. These schemas derive from reviewed core contracts; no generic wrapper is exposed in this profile."
            )
            body["data"]["tool_profile"] = "review"
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(body, allow_nan=False))],
            structured_content=body,
            is_error=result.is_error,
        )
