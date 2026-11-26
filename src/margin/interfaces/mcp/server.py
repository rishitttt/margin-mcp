"""A single-process stdio MCP adapter; no HTTP bridge or provider logic in handlers."""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import replace
from urllib.parse import unquote
from uuid import uuid4

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import MCPError

from margin.analysis.company import FUNCTIONS as COMPANY_FUNCTIONS
from margin.analysis.company import planning_capabilities
from margin.core.company_finance import execution_contract
from margin.core.config import Settings
from margin.core.contracts import DomainError, encoded_size
from margin.core.service import ResearchService
from margin.core.validation import validation_summary
from margin.interfaces.agent.client import BridgeError
from margin.interfaces.agent.local_config import read_provider_env
from margin.interfaces.mcp.policy import (
    DATA_INSTRUCTIONS,
    DATA_POLICY,
    FINANCIAL_RECOVERY,
    PLAN_RECOVERY,
)
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.tools import (
    CONTRACT,
    DIRECT_FUNCTIONS,
    DIRECT_PREVIEWS,
    DIRECT_REVIEWS,
    VERSION,
    definitions,
)

INSTRUCTIONS = (
    DATA_INSTRUCTIONS
    + """Margin provides Indian-company research tools over one process-local core.
For a ticker-based finance question discover group=company first, normally without
schemas; then inspect only the selected schema. Annual revenue growth uses
finance.company_growth (two periods), NOT company_ttm (four quarterly amounts).
Prefer each company entry's fresh_mcp_execution for fresh data; its typed tool schema
is distinct from legacy planning_schema. Do not load all calculation schemas to pick
a company workflow. When discovery is enough, stop with proposed inputs and call bounds.
Read company_execution_contract for exact provider, preview/execution controls,
request bounds and output fields. Do not speculate about Drishti or require session
IDs for the fresh company tool. A credential hold does not prevent a catalog summary.
Fresh-company previews create no plan_id; follow next_steps via the SAME company
tool with execute=true/key when already authorized, never margin_run. For which
fields support multiple metric groups choose company_data_readiness, one response.
Readiness uses report.readiness/valuation_readiness; report.rows may be empty.
DCF is an explicit-input calculator, not a company-finance selector. Preserve literal
labels and source-unverified scope; do not infer cash-conversion-cycle days or full
quick-ratio adjustments. Same-key replay is not a new workflow or fresh data.
For supplied-text claim/sentiment review prefer margin_prepare_review then
margin_submit_review: one review_id, internal source/packet/hash/date binding and one
final report. Ask for missing user material, never invent a task. Legacy primitives
remain for advanced use. review-simple exposes just status/prepare/submit.
Choose workflows from the user's goal; ordinary retrieval/math does not require citation
review. Citation is an optional host-side protocol. Search access does not establish
source-reading access. Declare only known host_profile capabilities, including optional
host_read_sources; missing means unknown, not inferred from model brand. Follow
citation_protocol guidance. A host without a reader can review supplied passages;
without passages return insufficient evidence/inventory. If originals are needed and
host reading tools exist, read them there, register exact original passages and prepare
a NEW packet. Never relabel summaries as originals or invent reader tools. Margin
does not browse, call an LLM or independently authenticate original documents.
margin_check_numeric_claim compares financial facts only. Certification/maturity levels
such as CMMI Level 5 need passage-based claim review; do not coerce them into financial
units or standalone/consolidated basis just because the statement contains a number.
For company finance questions, prefer margin_company_finance: ticker plus a company
function, execute=true and a stable idempotency_key fetch fresh data and return the
calculation internally. No prior result/fact handles are needed. Default execute=false
previews locally. At most one BharatStock request, zero Drishti calls/credits. Repeat
the SAME financial inputs/key to wait/read a pending/lost reply; never substitute a
new key. Company response v2 uses report.rows with matching value/unit/display;
use report.rows[].display verbatim. Amounts are INR_crore,
EPS INR_per_share, percentages and ratios distinct. Do not rescale these rows or
invent unsupported facts/dates. Raw inputs/values appear only with include_details=true
under separate details; it changes projection only and the SAME key makes no new fetch.
No run_id/margin_result path exists for this convenience response. Report copying
does not independently verify originals or guarantee the host's final prose.
Prefer the directly typed margin_calculate_margins, margin_convert_units,
margin_compare_periods, margin_calculate_cashflow_metrics, margin_calculate_profitability
and margin_calculate_balance_sheet_metrics tools when applicable. Their inputs are
top-level fields, not a nested arguments object. Use financial_view labels/displays from
financial results; do not manually rescale crore displays or relabel operating profit
as PBT/EBIT. Total, owners and continuing profit have distinct scopes.
Only tools/list names are callable MCP tools. Catalog entries such as
finance.calculate_margins are function identifiers, NOT tools. To calculate, call
margin_calculate with {"function":"finance.calculate_margins","arguments":{...}}.
Never replace dots with underscores or call a catalog function directly. Every catalog
entry includes mcp_execution with its tool, argument binding and input location.
Request one exact function's schema, not all schemas, when the function is known.
Never invent fact metadata to make a calculation succeed. If units, period, issuer or
basis are missing, ask for context or return the explicit incomplete result. An example
must be declared hypothetical with its assumptions, never presented as retrieved facts.
Use only declared input fields. Label a hypothetical example in why or fact.source;
do not add hypothetical or why flags inside a function's arguments. Validation errors
identify locations and allowed fields. Correct the indicated field instead of repeatedly
changing valid numeric strings to numbers or adding optional fields without evidence.
Start with margin_status, then margin_catalog for routes and exact schemas. Synthetic mode
contains fictional examples and must not answer real-company questions. Retrieval and
legacy company data dependencies require preview then margin_run. The explicit
execute=true fresh-company path performs bounded retrieval and math in one call.
Respect holds, process IDs,
budgets and idempotency; no automatic retries, source fallback or page exhaustion.
Calculations/review tools are local and may return partial/incomplete results. Preserve
units, periods, consolidation, continuing/total-profit scope and source caveats. DCF needs
explicit assumptions. Citation/sentiment semantics come from the host, not a Margin LLM;
supplied quotes and provider extracts are not authenticated originals. Optional why is a
brief visible tool-choice explanation, not hidden reasoning. Logging is opt-in and private.
For review material, margin_review_sources imports successful retained Drishti news,
announcements and earnings summaries/locators. It does not read attachments. Inspect
reported symbols and relevance in multi-company text; unknown publication dates stay
unknown. Host-read originals can be registered through margin_review. Obtain only the
needed review schema and retain the packet ID/hash; no automatic provider refetch.
Prefer margin_preview_news, margin_preview_announcements, margin_preview_earnings and
margin_preview_earnings_filing for event retrieval planning. Use the selected tool's
EXACT tools/list inputSchema: fields go at top level, without query/arguments/operations.
The host already advertises these typed schemas; tools/list is protocol discovery,
not another callable Margin tool. Do not invent a tools/list tool call.
Margin builds the core binding; these tools preview only, then use margin_run.
For generic margin_preview/margin_calculate/margin_review, obtain the selected exact
function schema from margin_catalog(include_schemas=true) before constructing inputs.
Preserve its required nesting; do not infer schemas from memory or provider docs.
Catalog direct_preview is an alternative flat tool route, not the generic operation
schema. Unknown/changed upstream contracts remain held. Status data.package_version
is the software version; envelope.contract_version names the protocol contract.
Prefer typed local review tools: margin_register_sources, margin_prepare_verification,
margin_submit_assessment, margin_render_citations, margin_audit_answer,
margin_check_numeric_claim, margin_prepare_sentiment, margin_submit_annotations,
margin_aggregate_sentiment and margin_review_workflows. Their exact fields are top-level,
without function/arguments wrappers. Generic margin_review remains a full-mode fallback.
Citation preparation takes claims/source_ids; sentiment preparation takes source_ids,
issuer/aspect and flat from/to/date_basis, not text/window. Packet IDs/hashes come from
preparation, never a data run or invented string. Follow next_steps.mcp_execution.tool;
merge bound_arguments with required host fields and validate the advertised schema.
The host still supplies judgments/quotes; partial bindings are not executable calls.
Use packet expires_at for expiry; original_document_verified concerns authenticity only.
The optional --tool-profile review advertises only local review/retained-result tools
over the same owner; switching only the frontend profile does not reset state/budgets.
"""
)


class MarginMCP:
    def __init__(self, service, recorder=None, *, state_owner="stdio_process"):
        self.service = service
        self.session_id = uuid4().hex
        self.recorder = recorder or ToolRecorder()
        self.tools = definitions()
        self.state_owner = state_owner

    def _envelope(self, name, why=None, call_id=None):
        output = {
            "contract_version": CONTRACT,
            "session_id": self.session_id,
            "call_id": call_id or uuid4().hex,
            "mode": self.service.settings.mode,
            "tool": self.service.sanitizer.text(name),
        }
        if why:
            output["decision_summary"] = self.service.sanitizer.text(why)
        return output

    async def call(self, name, arguments):
        if not isinstance(name, str) or name not in self.tools:
            route = self.function_route(name)
            message = "Unknown MCP tool. Only tools/list names can be called; do not rename catalog functions."
            if route:
                message += " Use " + json.dumps(route, ensure_ascii=False) + "."
            else:
                message += (
                    " Use margin_catalog to discover the function and its mcp_execution route."
                )
            raise MCPError(code=-32602, message=message)
        base = self._envelope(
            name if isinstance(name, str) and len(name) <= 100 else "invalid_tool"
        )
        event = None
        request_logged = False
        try:
            if arguments is None:
                arguments = {}
            if not isinstance(arguments, dict) or encoded_size(arguments) > 64 * 1024:
                raise DomainError("invalid_input", "Use a finite JSON object of at most 64 KiB.")
            problem = validation_summary(self.tools[name].input_schema, arguments)
            if problem:
                raise DomainError(
                    "invalid_input",
                    "Arguments do not match the selected MCP tool schema. " + problem,
                )
            why = arguments.get("why")
            if why is not None and not why.strip():
                raise DomainError(
                    "invalid_input", "why must be a nonempty one-line visible summary."
                )
            base = self._envelope(name, why, base["call_id"])
            raw = json.dumps(arguments, allow_nan=False)
            for _ in range(3):
                raw = unquote(raw)
            if any(secret in raw for secret in self.service.sanitizer.secrets):
                raise DomainError(
                    "invalid_input", "Credentials cannot be supplied as tool arguments."
                )
            event = {
                "call_id": base["call_id"],
                "session_id": self.session_id,
                "mode": self.service.settings.mode,
                "tool": name,
            }
            self.recorder.append(
                self.service.sanitizer.clean(
                    event
                    | {
                        "phase": "request",
                        "arguments": arguments,
                        "explanation_kind": "visible_agent_self_report",
                    }
                )
            )
            request_logged = True
            args = copy.deepcopy(arguments)
            args.pop("why", None)
            data = await self.dispatch(name, args)
            data = self.workflow_handoffs(data)
            body = self.service.sanitizer.clean(base | {"data": data})
            if encoded_size(body) > self.service.settings.max_result_bytes + 64 * 1024:
                raise DomainError(
                    "oversize_output",
                    "Tool output exceeded the adapter bound; retained data has not been refetched.",
                )
            error = False
        except DomainError as exc:
            body = self.service.sanitizer.clean(
                base
                | {
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "uncertain_outcome": exc.uncertain,
                    }
                }
            )
            error = True
        except (ValueError, TypeError, RecursionError):
            body = base | {
                "error": {
                    "code": "invalid_input",
                    "message": "Use bounded finite JSON input; no implicit coercion.",
                    "uncertain_outcome": False,
                }
            }
            error = True
        except asyncio.CancelledError:
            if event:
                try:
                    self.recorder.append(
                        event
                        | {
                            "phase": "waiter_cancelled",
                            "note": "Submitted runs remain accessible by their existing plan/idempotency key; use explicit run cancellation.",
                        }
                    )
                except DomainError:
                    pass
            raise
        except Exception:
            # SDK/provider exception text can contain credentials; never serialize it.
            body = base | {
                "error": {
                    "code": "internal_error",
                    "message": "The tool failed unexpectedly. Inspect run status before any new submission; raw diagnostics withheld.",
                    "uncertain_outcome": True,
                }
            }
            error = True
        if error and (
            name in DIRECT_FUNCTIONS
            or name
            in {
                "margin_company_finance",
                "margin_company_preview",
                "margin_calculate",
                "margin_facts",
            }
        ):
            body["error"]["recovery_guidance"] = FINANCIAL_RECOVERY
        if (
            error
            and name == "margin_run"
            and body["error"]["code"] in {"plan_unavailable", "plan_expired"}
        ):
            body["error"]["recovery_guidance"] = PLAN_RECOVERY
        if event and request_logged:
            try:
                self.recorder.append(
                    self.service.sanitizer.clean(
                        event | {"phase": "response", "is_error": error, "result": body}
                    )
                )
            except DomainError:
                body.setdefault("warnings", []).append(
                    "Post-action logging failed. This result is still returned; an action may already have executed. Do not resubmit with a new key."
                )
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text", text=json.dumps(body, ensure_ascii=False, allow_nan=False)
                )
            ],
            structured_content=body,
            is_error=error,
        )

    @staticmethod
    def execution_route(group, name):
        direct = next(
            (tool for tool, function in DIRECT_FUNCTIONS.items() if function == name), None
        )
        if group == "calculations" and direct:
            return {"tool": direct, "bind": {}, "inputs_at": "top_level"}
        if group == "calculations":
            return {
                "tool": "margin_calculate",
                "bind": {"function": name},
                "inputs_at": "arguments",
            }
        if group == "review":
            direct_review = next(
                (tool for tool, function in DIRECT_REVIEWS.items() if function == name), None
            )
            if direct_review:
                return {"tool": direct_review, "bind": {}, "inputs_at": "top_level"}
            return {
                "tool": "margin_review",
                "bind": {"function": name},
                "inputs_at": "arguments",
            }
        if group == "company":
            return {
                "tool": "margin_company_preview",
                "bind": {"function": name},
                "inputs_at": "top_level",
                "then": "margin_run",
            }
        return {
            "tool": "margin_preview",
            "bind": {"operations[0].operation": name},
            "inputs_at": "operations[0].arguments",
            "then": "margin_run",
        }

    def function_route(self, name):
        if not isinstance(name, str):
            return None
        for kind, names in (
            (
                "calculations",
                self.tools["margin_calculate"].input_schema["properties"]["function"]["enum"],
            ),
            ("review", self.tools["margin_review"].input_schema["properties"]["function"]["enum"]),
            (
                "company",
                self.tools["margin_company_preview"].input_schema["properties"]["function"]["enum"],
            ),
        ):
            if name in names:
                return self.execution_route(kind, name)
        return None

    def catalog(self, group="all", name=None, include_schemas=False):
        groups = {
            "retrieval": self.service.capabilities,
            "calculations": self.service.calculation_capabilities,
            "company": planning_capabilities,
            "review": self.service.review_capabilities,
        }
        selected = groups if group == "all" else {group: groups[group]}
        result = {}
        for kind, getter in selected.items():
            rows = copy.deepcopy(getter())
            if name:
                rows = [
                    row
                    for row in rows
                    if name in (row.get("operation") or row.get("function") or "")
                ]
            for row in rows:
                identifier = row.get("operation") or row.get("function")
                row["mcp_execution"] = self.execution_route(kind, identifier)
                if kind == "review":
                    row["generic_mcp_execution"] = {
                        "tool": "margin_review",
                        "bind": {"function": identifier},
                        "inputs_at": "arguments",
                    }
                direct_preview = next(
                    (
                        tool
                        for tool, operation in DIRECT_PREVIEWS.items()
                        if operation == identifier
                    ),
                    None,
                )
                if kind == "retrieval" and direct_preview:
                    row["direct_preview"] = {
                        "tool": direct_preview,
                        "inputs_at": "top_level",
                        "schema_source": "Use this tool's exact MCP tools/list inputSchema; it is a flat projection, not this entry's nested operation schema.",
                        "core_inputs_at": "arguments.query"
                        if "query" in self.service.registry.spec(identifier).schema["properties"]
                        else "arguments",
                        "then": "margin_run",
                    }
                if kind == "company":
                    row["fresh_mcp_execution"] = {
                        "tool": "margin_company_finance",
                        "bind": {"function": identifier},
                        "inputs_at": "top_level",
                        "execution": "execute=true plus a stable idempotency_key performs one fresh fetch and returns a compact calculation. No retained source needed.",
                        "provider": "bharatstock",
                        "maximum_provider_requests": execution_contract()["execution"][
                            "maximum_provider_requests"
                        ],
                        "execution_contract_ref": "company_execution_contract",
                    }
            if not include_schemas:
                rows = [
                    {
                        key: value
                        for key, value in row.items()
                        if key not in {"schema", "planning_schema"}
                    }
                    for row in rows
                ]
            result[kind] = rows
        if name and not any(result.values()):
            raise DomainError(
                "unknown_function", "No catalog entry matches the requested name/group."
            )
        output = {
            "groups": result,
            "routing_notice": "Catalog function identifiers are not callable MCP tools. Use each entry's mcp_execution.tool and bind; place inputs at inputs_at. Never replace dots with underscores. why is a top-level MCP argument.",
            "schema_lookup": "Generic calls MUST request one name/group with include_schemas=true and preserve that exact operation/function schema and nesting. Typed direct calls use their own MCP tools/list inputSchema, not the generic nested schema. Both originate from reviewed core contracts; do not guess from examples/provider docs. Unknown context stays unknown.",
            "availability_is_not_source_verification": True,
            "data_policy": copy.deepcopy(DATA_POLICY),
        }
        if "company" in result:
            output["company_execution_contract"] = execution_contract()
        return output

    def require_session(self, supplied):
        if supplied != self.session_id:
            raise DomainError(
                "session_changed",
                "The core process differs from the preview/status. Reconcile allowances and preview again before dispatch.",
            )

    async def wait(self, run_id, seconds=0):
        deadline = time.monotonic() + seconds
        state = self.service.get_run(run_id)
        while state["status"] in {"queued", "running"} and time.monotonic() < deadline:
            await asyncio.sleep(min(0.05, max(0, deadline - time.monotonic())))
            state = self.service.get_run(run_id)
        return state

    async def dispatch(self, name, args):
        if name in DIRECT_REVIEWS:
            return self.service.review(DIRECT_REVIEWS[name], args)
        if name in DIRECT_PREVIEWS:
            operation = DIRECT_PREVIEWS[name]
            arguments = (
                {"query": args}
                if "query" in self.service.registry.spec(operation).schema["properties"]
                else args
            )
            return self.service.create_plan([{"operation": operation, "arguments": arguments}])
        if name in DIRECT_FUNCTIONS:
            return self.service.calculate(DIRECT_FUNCTIONS[name], args)
        if name == "margin_status":
            return self.service.status() | {
                "package_version": VERSION,
                "data_policy": copy.deepcopy(DATA_POLICY),
                "state_owner": self.state_owner,
                "state_lifetime": "Source TTL/eviction applies; stopping the state owner invalidates handles and does not renew upstream quota.",
                "recording_enabled": self.recorder.path is not None,
                "decision_trails": "Optional visible why summaries only; not hidden reasoning.",
            }
        if name == "margin_catalog":
            return self.catalog(**args)
        if name == "margin_preview":
            return self.service.create_plan(args["operations"])
        if name == "margin_company_preview":
            return self.service.plan_financial(**args)
        if name == "margin_company_finance":
            return await self.service.company_finance(**args)
        if name == "margin_run":
            self.require_session(args["session_id"])
            run = await self.service.start_run(args["plan_id"], args["idempotency_key"])
            return await self.wait(run["run_id"], args.get("wait_seconds", 0))
        if name == "margin_run_status":
            return await self.wait(args["run_id"], args.get("wait_seconds", 0))
        if name == "margin_result":
            return self.service.get_result(**args)
        if name == "margin_sources":
            return {"sources": self.service.financial_sources()}
        if name == "margin_facts":
            return self.service.prepare_facts(**args)
        if name == "margin_calculate":
            return self.service.calculate(args["function"], args["arguments"])
        if name == "margin_cancel":
            return await self.service.cancel(args["run_id"])
        if name == "margin_connect_drishti":
            self.require_session(args["session_id"])
            return await self.service.connect_drishti()
        if name == "margin_review":
            return self.service.review(args["function"], args["arguments"])
        return self.service.import_review_sources(**args)

    @classmethod
    def workflow_handoffs(cls, data):
        if not isinstance(data, dict) or not (
            data.get("next_steps")
            or data.get("company_execution_contract")
            or isinstance(data.get("report"), dict)
            and data["report"].get("valuation_readiness")
        ):
            return data
        data = copy.deepcopy(data)
        if data.get("company_execution_contract"):
            valuation = data["company_execution_contract"].get("valuation", {})
            if valuation.get("explicit_function") == "finance.calculate_dcf":
                valuation["mcp_execution"] = cls.execution_route(
                    "calculations", valuation["explicit_function"]
                )
        valuation = data.get("report", {}).get("valuation_readiness", {})
        if valuation.get("explicit_function") == "finance.calculate_dcf":
            valuation["mcp_execution"] = cls.execution_route(
                "calculations", valuation["explicit_function"]
            )
        for action in data.get("next_steps", []):
            tool = next(
                (
                    name
                    for name, function in DIRECT_REVIEWS.items()
                    if function == action["function"]
                ),
                None,
            )
            if (
                action.get("kind") == "execute_fresh_company_finance"
                and action["function"] in COMPANY_FUNCTIONS
            ):
                tool = "margin_company_finance"
                action["do_not_use_tools"] = ["margin_run"]
            if tool:
                action["mcp_execution"] = {"tool": tool, "inputs_at": "top_level"}
                action["schema_source"] = (
                    "Use the named tool's exact host-advertised inputSchema. Merge bound_arguments with required host fields; do not invent references or judgments."
                )
        for workflow in data.get("workflows", []):
            workflow["mcp_steps"] = [
                {"function": function, "tool": tool, "inputs_at": "top_level"}
                for function in workflow.get("functions", [])
                for tool, target in DIRECT_REVIEWS.items()
                if target == function
            ]
        return data


def create_server(
    settings=None,
    *,
    service_factory=ResearchService,
    record_file=None,
    record_dir=None,
    backend_socket=None,
    expected_mode=None,
    tool_profile="all",
):
    from margin.interfaces.mcp.profiles import REVIEW_INSTRUCTIONS, SIMPLE_INSTRUCTIONS, ToolView

    if tool_profile not in {"all", "review", "review-simple"}:
        raise ValueError("Unknown MCP tool profile.")
    if not backend_socket:
        settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(_):
        if backend_socket:
            from margin.interfaces.mcp.bridge import RemoteMCP

            if record_file or record_dir:
                raise ValueError("Shared-mode recording belongs to the backend.")
            yield ToolView(await RemoteMCP.connect(backend_socket, expected_mode), tool_profile)
            return
        recorder = ToolRecorder(record_file, directory=record_dir)
        service = None
        try:
            service = service_factory(settings)
            yield ToolView(MarginMCP(service, recorder), tool_profile)
        finally:
            try:
                if service is not None:
                    await service.close()
            finally:
                recorder.close()

    async def list_tools(ctx, params):
        if params and params.cursor:
            raise ValueError("This bounded tool list has no continuation cursor.")
        return types.ListToolsResult(tools=list(ctx.lifespan_context.tools.values()))

    async def call_tool(ctx, params):
        return await ctx.lifespan_context.call(params.name, params.arguments)

    return Server(
        "margin",
        version=VERSION,
        title="Margin Indian financial research",
        instructions={
            "all": INSTRUCTIONS,
            "review": REVIEW_INSTRUCTIONS,
            "review-simple": SIMPLE_INSTRUCTIONS,
        }[tool_profile],
        lifespan=lifespan,
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


async def serve(
    settings,
    record_file=None,
    record_dir=None,
    backend_socket=None,
    expected_mode=None,
    tool_profile="all",
):
    server = create_server(
        settings,
        record_file=record_file,
        record_dir=record_dir,
        backend_socket=backend_socket,
        expected_mode=expected_mode,
        tool_profile=tool_profile,
    )
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the local Margin MCP server over stdio; stdout is reserved for protocol messages."
    )
    parser.add_argument("--mode", choices=["synthetic", "live"])
    parser.add_argument("--tool-profile", choices=["all", "review", "review-simple"], default="all")
    parser.add_argument(
        "--backend-socket",
        help="Connect to an explicitly started private local backend; never autostart or retry",
    )
    parser.add_argument(
        "--credentials-file",
        help="Optional operator-owned provider env file; never pass key values as arguments",
    )
    recording = parser.add_mutually_exclusive_group()
    recording.add_argument(
        "--record-file", help="Optional NEW private JSONL file; logging is disabled by default"
    )
    recording.add_argument(
        "--record-dir",
        help="Optional private directory; create a unique JSONL file on each process launch",
    )
    args = parser.parse_args(argv)
    # The SDK may log raw RPC data at debug/error levels; suppress those diagnostics.
    for name in ("mcp", "httpx", "httpx2", "httpcore", "httpcore2"):
        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        logger.setLevel(logging.CRITICAL + 1)
    try:
        if args.backend_socket:
            if args.credentials_file or args.record_file or args.record_dir:
                raise ValueError("Configure credentials and recording on the shared backend only.")
            asyncio.run(
                serve(
                    None,
                    backend_socket=args.backend_socket,
                    expected_mode=args.mode,
                    tool_profile=args.tool_profile,
                )
            )
            return 0
        settings = Settings.from_env()
        keys = read_provider_env(args.credentials_file) if args.credentials_file else {}
        settings = replace(
            settings,
            mode=args.mode or settings.mode,
            bharatstock_key=keys.get("BHARATSTOCK_API_KEY", settings.bharatstock_key),
            drishti_key=keys.get("DRISHTI_API_KEY", settings.drishti_key),
        )
        print(
            f"Margin MCP {VERSION}: {settings.mode.upper()} mode; process allowances are not account quotas.",
            file=sys.stderr,
        )
        asyncio.run(
            serve(settings, args.record_file, args.record_dir, tool_profile=args.tool_profile)
        )
        return 0
    except (DomainError, BridgeError, OSError, ValueError):
        print(
            "Margin MCP could not start. Check local mode/configuration and a new writable recording path; private details withheld.",
            file=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        return 0
    except Exception:
        print(
            "Margin MCP stopped unexpectedly; raw diagnostics withheld. Reconcile any earlier process allowance before restarting.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
