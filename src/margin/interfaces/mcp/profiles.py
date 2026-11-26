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
FINANCE_TOOLS = frozenset(
    {"margin_status", "margin_catalog", "margin_company_finance", "margin_calculate"}
)
FINANCE_INSTRUCTIONS = (
    DATA_INSTRUCTIONS
    + """Margin finance has four tools. For ticker questions choose a company function
from margin_catalog(group=company). Use margin_company_finance: execute=false is a
local preview, not a generic plan. No retained source is needed. For a preview-only
request STOP after preview; quote preview_summary.display without expanding it into
unfetched financial facts. A single profit margin uses company_margins; company_profitability
returns multiple profitability measures. missing_fields_for_preview
and missing_fields_for_execution are different. A later execution uses the SAME
margin_company_finance tool, execute=true and a stable idempotency_key, only when the
user actually requested execution and allowance remains. Do not call margin_run or
invent plan IDs: neither is part of this profile. A zero local allowance is not the
provider account balance and does not prevent a configured fresh-company preview.
Annual growth compares two annual periods; TTM sums four eligible monetary quarters.
For available-field support across profitability/cash-conversion/liquidity, choose
finance.company_data_readiness once. Read report.readiness and valuation_readiness;
empty numeric rows are intentional and computability does not verify source facts.
For results copy report.rows displays, exact dates, definitions, units and partial holds.
Same inputs/key read the existing result, not fresh data/new analysis; no new key retry
after an uncertain dispatch. include_details is projection only with that same key.
margin_calculate is local explicit-input math, not a ticker fetch. Discover one exact
calculation schema before calling it; do not fabricate facts to rescue missing data.
DCF requires explicit forecasts/assumptions here, never automatic company valuation.
Provider keys/positive allowance are needed only as declared by execution preflight;
never reset budgets/restart or ask to buy credits to finish a local preview.
Optional why is a brief visible tool-choice summary, not hidden reasoning. Profiles
change advertised tools/projection only; they do not grant execution authorization.
"""
)
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
        if profile not in {"all", "review", "review-simple", "finance"}:
            raise ValueError("Unknown MCP tool profile.")
        self.inner, self.profile = inner, profile
        self.tools = {
            name: copy.deepcopy(tool)
            for name, tool in inner.tools.items()
            if profile == "all"
            or name
            in {"review": REVIEW_TOOLS, "review-simple": SIMPLE_TOOLS, "finance": FINANCE_TOOLS}[
                profile
            ]
        }
        if profile == "finance":
            catalog = self.tools["margin_catalog"]
            catalog.input_schema["properties"]["group"] = {
                "enum": ["all", "company", "calculations"],
                "default": "company",
            }
            catalog.description = "Discover company functions (default) or one explicit calculation schema. all means company and calculations only. Follow mcp_execution; company schemas are the fresh tool inputs, never retained-source planning. No requests."
            for tool in self.tools.values():
                for key in ("session_id", "call_id"):
                    tool.output_schema["required"].remove(key)
            self.tools[
                "margin_company_finance"
            ].description = "Ticker-based finance. execute=false previews without fetching or retained data; STOP for preview-only tasks and copy preview_summary.display. Preview needs no idempotency_key; later execution requires it. execute=true performs at most one BharatStock request, zero Drishti, only within user authorization/allowance. No generic plan or margin_run. Use report.rows displays verbatim; readiness uses report.readiness/valuation_readiness. Same inputs/key read the same result without refetch; preserve definitions/holds and source-unverified scope."
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
                else (
                    " Use margin_company_finance for company data; margin_calculate for explicit supplied inputs."
                    if self.profile == "finance"
                    else " Use the tools advertised in this profile; prepare a high-level review with actual user material."
                )
            )
            raise MCPError(-32602, f"Tool is not exposed in the {self.profile} profile." + hint)
        forwarded = arguments
        if self.profile in {"review", "finance"} and name == "margin_catalog":
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
                raise MCPError(
                    -32602, f"{self.profile}-profile catalog arguments are invalid. " + problem
                )
            if self.profile == "review":
                forwarded["group"] = "review"
            elif forwarded.get("group", "company") == "all":
                # all is projected after one local catalog lookup; no data work.
                forwarded["group"] = "all"
            else:
                forwarded.setdefault("group", "company")
        result = await self.inner.call(name, forwarded)
        if self.profile == "finance":
            return self.finance_result(name, result, forwarded or {})
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

    def finance_result(self, name, result, arguments):
        if not isinstance(result.structured_content, dict):
            return result
        body = copy.deepcopy(result.structured_content)
        body.pop("session_id", None)
        body.pop("call_id", None)
        data = body.get("data", {})
        if name == "margin_status" and not result.is_error:
            data.update(tool_profile="finance", advertised_tools=len(self.tools))
        elif name == "margin_catalog" and not result.is_error:
            data["groups"] = {
                k: v for k, v in data["groups"].items() if k in {"company", "calculations"}
            }
            if arguments.get("name") and not any(data["groups"].values()):
                raise MCPError(-32602, "No matching function in the finance profile.")
            for kind, rows in data["groups"].items():
                for row in rows:
                    if kind == "company":
                        row.pop("planning_schema", None)
                        row.pop("legacy_mcp_execution", None)
                        row.pop("legacy_defaults", None)
                        row.pop("legacy_note", None)
                        row.pop("fresh_mcp_execution", None)
                        row["schema_source"] = "margin_company_finance advertised inputSchema"
                        if arguments.get("include_schemas"):
                            row["schema"] = copy.deepcopy(
                                self.tools["margin_company_finance"].input_schema
                            )
                    else:
                        row["mcp_execution"] = {
                            "tool": "margin_calculate",
                            "bind": {"function": row["function"]},
                            "inputs_at": "arguments",
                        }
            data.pop("company_execution_contract", None)
            data["tool_profile"] = "finance"
            data["schema_lookup"] = (
                "Company uses the advertised margin_company_finance schema; calculations use the selected row's exact schema inside margin_calculate.arguments."
            )
        elif name == "margin_company_finance" and data.get("status") == "preview":
            body["data"] = {
                key: data[key]
                for key in (
                    "response_version",
                    "status",
                    "function",
                    "selection",
                    "preview_summary",
                    "data_operation",
                    "creates_plan_id",
                    "next_steps",
                    "warnings",
                )
                if key in data
            }
            for step in body["data"]["next_steps"]:
                step.pop("purpose", None)
                step.pop("schema_source", None)
        elif name == "margin_company_finance" and "report" in data:
            valuation = data["report"].get("valuation_readiness", {})
            if valuation.get("explicit_function") == "finance.calculate_dcf":
                valuation["mcp_execution"] = {
                    "tool": "margin_calculate",
                    "bind": {"function": "finance.calculate_dcf"},
                    "inputs_at": "arguments",
                }
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(body, allow_nan=False))],
            structured_content=body,
            is_error=result.is_error,
        )
