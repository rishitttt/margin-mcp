"""Stable workflow tools; underlying financial/provider contracts stay in the core."""

from copy import deepcopy

from mcp import types

from margin.analysis.company import FUNCTIONS, planning_capabilities
from margin.analysis.service import SPECS, obj
from margin.core.company_finance import SCHEMA as COMPANY_FINANCE_SCHEMA
from margin.core.config import Settings
from margin.core.registry import Registry
from margin.protocols.schemas import SCHEMAS

VERSION = "0.6.0"
CONTRACT = "margin.mcp.v1"
DIRECT_FUNCTIONS = {
    "margin_calculate_margins": "finance.calculate_margins",
    "margin_convert_units": "facts.convert_units",
    "margin_compare_periods": "finance.compare_periods",
    "margin_calculate_cashflow_metrics": "finance.calculate_cashflow_metrics",
    "margin_calculate_profitability": "finance.calculate_profitability",
    "margin_calculate_balance_sheet_metrics": "finance.calculate_balance_sheet_metrics",
}
ID = {"type": "string", "pattern": r"^[A-Za-z0-9_-]{1,100}$"}
WAIT = {"type": "integer", "minimum": 0, "maximum": 30, "default": 0}
WHY = {
    "type": "string",
    "minLength": 1,
    "maxLength": 280,
    "pattern": r"^[^\r\n]+$",
    "description": "Optional visible one-line tool-choice summary; not hidden reasoning.",
}
ARGS = {
    "type": "object",
    "description": "Exact arguments from margin_catalog for the selected function; the core validates its full schema.",
}
OUTPUT = obj(
    {
        "contract_version": {"const": CONTRACT},
        "session_id": ID,
        "call_id": ID,
        "mode": {"enum": ["synthetic", "live"]},
        "tool": {"type": "string"},
        "data": {},
        "error": {"type": "object"},
        "decision_summary": {"type": "string"},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    ["contract_version", "session_id", "call_id", "mode", "tool"],
)


def schema(properties=None, required=()):
    return obj((properties or {}) | {"why": WHY}, list(required))


def definitions():
    operations = sorted(set(Registry(Settings()).specs) | set(SPECS))
    company = deepcopy(planning_capabilities()[0]["planning_schema"])
    company["properties"]["function"] = {"enum": sorted(FUNCTIONS)}
    company["properties"]["why"] = WHY
    fresh_company = deepcopy(COMPANY_FINANCE_SCHEMA)
    fresh_company["properties"]["why"] = WHY
    rows = [
        (
            "margin_status",
            "Inspect mode, process/session ID, provider readiness and remaining process allowances. No connection or provider calls. Read this first; process counters are not account-wide balances.",
            schema(),
            True,
            True,
            False,
        ),
        (
            "margin_catalog",
            "Discover function identifiers and their mcp_execution routes. Catalog functions are NOT callable MCP tool names: finance.calculate_margins must be passed to margin_calculate. Never rename dots to underscores. Request one function by name/group with include_schemas=true to avoid loading every schema. No provider calls.",
            schema(
                {
                    "group": {
                        "enum": ["all", "retrieval", "calculations", "company", "review"],
                        "default": "all",
                    },
                    "name": {"type": "string", "minLength": 1, "maxLength": 100},
                    "include_schemas": {"type": "boolean", "default": False},
                }
            ),
            True,
            True,
            False,
        ),
        (
            "margin_preview",
            "Validate and preview one to eight whitelisted retrieval/calculation operations, costs and holds. Executes nothing. Discover nested argument schemas with margin_catalog. Submit the returned plan through margin_run only when its data work is wanted.",
            schema(
                {
                    "operations": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 8,
                        "items": obj({"operation": {"enum": operations}, "arguments": ARGS}),
                    }
                },
                ["operations"],
            ),
            False,
            False,
            False,
        ),
        (
            "margin_company_finance",
            "Preferred for ticker-based finance: one fresh BharatStock request plus deterministic math, no previous facts/handles. Default execute=false previews; execute=true requires a stable idempotency_key. Supports nine company functions, no automatic DCF. Response v2 report.rows has matching value/unit/display: money INR_crore, EPS INR_per_share, percent/ratios distinct. Use report.rows[].display VERBATIM; do not rescale or invent facts/dates. Raw calculation fields are absent by default; include_details=true adds separate audit details using the SAME key, without another fetch. Repeat the SAME financial inputs/key to wait/read a pending/lost reply (30s max); new keys fetch again. Preserve holds and source caveats. Zero Drishti calls/credits. No margin_result/run_id is provided. Duplicate protection lasts only in this core process.",
            fresh_company,
            False,
            True,
            True,
        ),
        (
            "margin_company_preview",
            "Preview one company finance workflow; defaults to reusing retained data and fetch_missing=false. Explicit fetch_missing=true can add one financials request, shown before execution. Use finance.company_data_readiness when field support is uncertain. No provider calls at preview.",
            company,
            False,
            False,
            False,
        ),
        (
            "margin_run",
            "Submit a previewed plan once with the same session ID and a unique idempotency key. May consume provider quota/credits. Repeat a lost submission only with the SAME plan/key; never retry an uncertain provider operation with a new key. Returns run/operation IDs; inspect with margin_run_status and margin_result.",
            schema(
                {
                    "session_id": ID,
                    "plan_id": ID,
                    "idempotency_key": {"type": "string", "pattern": r"^[A-Za-z0-9_-]{8,100}$"},
                    "wait_seconds": WAIT,
                },
                ["session_id", "plan_id", "idempotency_key"],
            ),
            False,
            True,
            True,
        ),
        (
            "margin_run_status",
            "Read a run or wait at most 30 seconds. Starts no additional data work. Cancelling a waiter leaves the already submitted run active; margin_cancel is the explicit cancellation action.",
            schema({"run_id": ID, "wait_seconds": WAIT}, ["run_id"]),
            True,
            True,
            False,
        ),
        (
            "margin_result",
            "Read one retained sanitized operation result and receipt. For financials, financial_view supplies deterministic exact crore values, ready-to-report displays, EPS per share, metric labels and scope warnings: use it for reporting without rescaling or renaming metrics. Raw provider payload remains for inspection. Expired/evicted results stay unavailable; never refetches.",
            schema({"run_id": ID, "operation_id": ID}, ["run_id", "operation_id"]),
            True,
            True,
            False,
        ),
        (
            "margin_sources",
            "List retained financial source handles for company workflows and fact preparation. No discovery/fetch.",
            schema(),
            True,
            True,
            False,
        ),
        (
            "margin_facts",
            "Prepare typed facts from one retained financial response. Auto units use dated provider documentation; unknown/null preserves unknown units. Stocks and flows remain distinct; quarter derivation retains evidence. No provider calls or source verification.",
            schema(
                {
                    "run_id": ID,
                    "operation_id": ID,
                    "money_unit": {
                        "enum": [
                            "auto",
                            "unknown",
                            None,
                            "INR",
                            "INR_thousand",
                            "INR_lakh",
                            "INR_crore",
                        ],
                        "default": "auto",
                    },
                },
                ["run_id", "operation_id"],
            ),
            True,
            True,
            False,
        ),
        (
            "margin_calculate",
            'Generic calculator for functions without a preferred direct tool. Prefer margin_calculate_margins for margins and margin_convert_units for conversions; the catalog identifies other direct tools. Otherwise pass {"function":"<catalog identifier>","arguments":{...}} after requesting that exact schema. Use only declared fields; put why outside arguments. Never invent context or insert hypothetical flags. Numeric strings are supported. No provider calls; incomplete outputs are valid. DCF needs explicit assumptions.',
            schema(
                {"function": {"enum": sorted(SPECS)}, "arguments": ARGS}, ["function", "arguments"]
            ),
            True,
            True,
            False,
        ),
        (
            "margin_cancel",
            "Explicitly cancel a submitted run. A dispatched request may already be billed; uncertain receipts are preserved. No automatic retry or refund claim.",
            schema({"run_id": ID}, ["run_id"]),
            False,
            True,
            False,
        ),
        (
            "margin_connect_drishti",
            "Explicitly connect/refresh upstream Drishti metadata using shared HTTP allowance. No paid data tool is executed, but lifecycle requests count. Fresh metadata is reused; unknown/changed operations stay held. Requires current session ID.",
            schema({"session_id": ID}, ["session_id"]),
            False,
            False,
            True,
        ),
        (
            "margin_review",
            "Call this MCP tool for a review catalog function: pass its exact identifier as function and its inputs as arguments. The catalog function is NOT a separate MCP tool. Host supplies passages and semantic judgments. Margin checks supplied quotes/references/numbers and aggregates; no browsing, PDF fetch, LLM inference or independent original verification.",
            schema(
                {"function": {"enum": sorted(SCHEMAS)}, "arguments": ARGS},
                ["function", "arguments"],
            ),
            False,
            False,
            False,
        ),
        (
            "margin_review_sources",
            "Import a successful retained provider news result into the local review store with explicit issuer attribution. No source fetch; provider text is not authenticated original evidence.",
            schema(
                {
                    "run_id": ID,
                    "operation_id": ID,
                    "issuer": {"type": "string", "minLength": 1, "maxLength": 100},
                },
                ["run_id", "operation_id", "issuer"],
            ),
            False,
            False,
            False,
        ),
    ]
    for name, function in DIRECT_FUNCTIONS.items():
        inputs = deepcopy(SPECS[function][1])
        inputs["properties"]["why"] = WHY
        rows.append(
            (
                name,
                f"Direct strictly typed {function} calculation. Supply these schema fields at the top level; no function selector or arguments wrapper. Local arithmetic only, no provider calls. Preserve supplied fact provenance, units, periods and basis; never invent context. Missing/incompatible facts remain incomplete; source validity is not independently verified.",
                inputs,
                True,
                True,
                False,
            )
        )
    return {
        name: types.Tool(
            name=name,
            description=description,
            inputSchema=inputs,
            outputSchema=deepcopy(OUTPUT),
            annotations=types.ToolAnnotations(
                readOnlyHint=readonly,
                destructiveHint=False,
                idempotentHint=idempotent,
                openWorldHint=openworld,
            ),
        )
        for name, description, inputs, readonly, idempotent, openworld in rows
    }
