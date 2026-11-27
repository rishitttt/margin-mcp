"""Stable workflow tools; underlying financial/provider contracts stay in the core."""

import json
from copy import deepcopy

from mcp import types

from margin.analysis.company import FUNCTIONS, function_constraints, planning_capabilities
from margin.analysis.service import SPECS, obj
from margin.core.company_finance import SCHEMA as COMPANY_FINANCE_SCHEMA
from margin.core.config import Settings
from margin.core.registry import Registry
from margin.protocols.schemas import SCHEMAS

VERSION = "0.10.0"
CONTRACT = "margin.mcp.v1"
DIRECT_FUNCTIONS = {
    "margin_calculate_margins": "finance.calculate_margins",
    "margin_convert_units": "facts.convert_units",
    "margin_compare_periods": "finance.compare_periods",
    "margin_calculate_cashflow_metrics": "finance.calculate_cashflow_metrics",
    "margin_calculate_profitability": "finance.calculate_profitability",
    "margin_calculate_balance_sheet_metrics": "finance.calculate_balance_sheet_metrics",
    "margin_calculate_dcf": "finance.calculate_dcf",
}
DIRECT_COMPANY = {"margin_company_data_readiness": "finance.company_data_readiness"}
DIRECT_PREVIEWS = {
    "margin_preview_news": "drishti.get_news",
    "margin_preview_announcements": "drishti.get_announcements",
    "margin_preview_earnings": "drishti.list_earnings",
    "margin_preview_earnings_filing": "drishti.get_earnings_filing",
}
DIRECT_REVIEWS = {
    "margin_prepare_review": "review.prepare",
    "margin_submit_review": "review.submit",
    "margin_review_workflows": "protocols.list_workflows",
    "margin_register_sources": "evidence.register_sources",
    "margin_prepare_verification": "evidence.prepare_verification",
    "margin_submit_assessment": "evidence.submit_assessment",
    "margin_render_citations": "evidence.render_citations",
    "margin_audit_answer": "evidence.audit_answer",
    "margin_check_numeric_claim": "evidence.check_numeric_claim",
    "margin_prepare_sentiment": "sentiment.prepare_analysis",
    "margin_submit_annotations": "sentiment.submit_annotations",
    "margin_aggregate_sentiment": "sentiment.aggregate",
}
REVIEW_HELP = {
    "review.prepare": "PREFERRED supplied-text review entry point. Supply actual user text, metadata, ordered claim texts (or [] for sentiment only), separate record/publication dates and optional sentiment scope. Margin binds all source/passage/packet IDs internally and returns ONE review_id. Ask for missing input; never invent an example. No provider/LLM call.",
    "review.submit": "Complete a prepared review using ONLY its returned review_id. Supply ordered claim verdicts, exact quote substrings or null, rationales and sentiment annotation when prepared. No source IDs, packet IDs, hashes, numeric units or host_profile. Margin validates and atomically renders/audits/aggregates; preserve its complete report and limitations. No provider/LLM call.",
    "protocols.list_workflows": "Discover optional local citation/sentiment protocols, host source-reading steps and capability fallbacks. Ordinary retrieval/math does not require citation review.",
    "evidence.register_sources": "Register supplied source locators/passages. No document download; unknown dates stay unknown.",
    "evidence.prepare_verification": "Optional claim-to-passage review protocol, not automatic original verification. Prepare claims with existing source_ids; optional host_profile declares reading/assessment access. Follow citation_protocol for no-reader/no-text fallbacks. Do not supply passage fields, packet IDs or hashes here; preparation returns real packet refs and passages.",
    "evidence.submit_assessment": "Submit host reviewer and per-claim assessments/quotes using the actual returned packet_id/hash; run IDs and invented hashes are invalid.",
    "evidence.render_citations": "Render an existing citation packet with its actual packet_id/hash. Unreviewed claims remain not_reviewed.",
    "evidence.audit_answer": "Audit actual final claim_ids against an existing packet_id/hash; this is not preparation, a raw claim/URL verifier or arbitrary prose audit.",
    "evidence.check_numeric_claim": "Compare two supplied FINANCIAL facts with compatible financial units/context. Not for maturity/certification levels, ratings or arbitrary numbers in prose (for example CMMI Level 5); use passage-based claim review for those. Never invent a financial unit or reporting basis to fit. Does not authenticate original sources.",
    "sentiment.prepare_analysis": "Prepare from source_ids, issuer, aspect, flat from/to and date_basis. No text/window fields or packet refs. Returns actual packet refs; publication timing must be established separately.",
    "sentiment.submit_annotations": "Submit host reviewer and source-level annotations/quotes with actual packet_id/hash. This is sentiment annotation, not citation assessment.",
    "sentiment.aggregate": "Aggregate an existing sentiment packet using its actual packet_id/hash. Missing labels are not neutral; balance excludes mixed/unclear/missing/irrelevant. Not comprehensive investor sentiment.",
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


def fresh_company_schema(function=None):
    exact = deepcopy(COMPANY_FINANCE_SCHEMA)
    exact["properties"]["why"] = deepcopy(WHY)
    if function is not None:
        if function not in DIRECT_COMPANY.values():
            raise ValueError("Review the typed company projection before adding an alias.")
        exact["properties"].pop("function")
        exact["required"].remove("function")
        # Readiness has no TTM/CAGR period specialization; preserve the key guard.
        exact["allOf"] = [
            clause
            for clause in exact["allOf"]
            if "function" not in clause.get("if", {}).get("required", [])
        ]
    return exact


def preview_schema(operation, registry):
    """Project the reviewed core schema; never maintain a parallel provider contract."""
    exact = deepcopy(registry.spec(operation).schema)
    if "query" in exact["properties"]:
        query = exact["properties"]["query"]
        reference = query.get("$ref", "")
        if not reference.startswith("#/$defs/"):
            raise ValueError("Review the typed preview projection for the changed query contract.")
        inputs = deepcopy(exact["$defs"][reference.removeprefix("#/$defs/")])
        if '"$ref"' in json.dumps(inputs):
            inputs["$defs"] = deepcopy(exact["$defs"])
    else:
        inputs = exact
    inputs["additionalProperties"] = False
    inputs["properties"]["why"] = deepcopy(WHY)
    return inputs


def definitions():
    registry = Registry(Settings())
    operations = sorted(set(registry.specs) | set(SPECS))
    company = deepcopy(planning_capabilities()[0]["planning_schema"])
    company["properties"]["function"] = {"enum": sorted(FUNCTIONS)}
    company["properties"]["why"] = WHY
    company["allOf"] = function_constraints()
    fresh_company = fresh_company_schema()
    rows = [
        (
            "margin_status",
            "Inspect package_version (software, distinct from contract_version), mode, process/session ID, provider readiness and remaining process allowances. No connection or provider calls. Read this first; process counters are not account-wide balances.",
            schema(
                {
                    "include_diagnostics": {
                        "type": "boolean",
                        "default": False,
                        "description": "Show internal record capacities/receipt counts and stale historical snapshots under diagnostics; these are not current quotas or account credits.",
                    }
                }
            ),
            True,
            True,
            False,
        ),
        (
            "margin_catalog",
            "Discover function identifiers and routes. Ticker-based finance: inspect group=company first; company_execution_contract states provider, exact usage bounds, execution/key/allowance requirements and answer fields. fresh_mcp_execution uses fresh data; planning_schema is legacy. Annual growth compares periods; TTM sums quarters, not growth. Request one selected schema, not all schemas. Missing credentials do not prevent a catalog planning summary. Never invent values. Function identifiers are not tool names; use advertised routes. No provider calls.",
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
            "Generic preview of one to eight operations; executes nothing. You MUST obtain the selected exact operation schema from margin_catalog with include_schemas=true and preserve its nesting, including arguments.query where required. Do not infer fields from examples or upstream docs. Prefer typed margin_preview_news/announcements/earnings/earnings_filing when available; those take top-level fields. Submit the returned plan through margin_run only when wanted.",
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
            "For cross-group field support prefer margin_company_data_readiness. For other ticker-based finance: one fresh BharatStock request plus deterministic math, no previous facts/handles. Default execute=false previews; execute=true requires a stable idempotency_key. Supports nine company functions, no automatic DCF. Response v2 report.rows has matching value/unit/display: money INR_crore, EPS INR_per_share, percent/ratios distinct. Use report.rows[].display VERBATIM; do not rescale or invent facts/dates. Raw calculation fields are absent by default; include_details=true adds separate audit details using the SAME key, without another fetch. Repeat the SAME financial inputs/key to wait/read a pending/lost reply (30s max); new keys fetch again. Preserve holds and source caveats. Zero Drishti calls/credits. No margin_result/run_id is provided. Duplicate protection lasts only in this core process.",
            fresh_company,
            False,
            True,
            True,
        ),
        (
            "margin_company_preview",
            "LEGACY retained-source company workflow. Use margin_company_finance with execute=false for ordinary fresh-company previews; no retained data is needed there. This legacy path defaults to reusing retained data and fetch_missing=false; source_required does not mean fresh preview needs a fetch. Explicit fetch_missing=true can plan one request without executing it. Use only for retained-source/explicit generic-plan tasks, then margin_run with an actual returned plan ID.",
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
            "Import retained Drishti news, summary announcements, earnings-list or earnings-detail sources with explicit issuer attribution. Returns supplied summaries and locators, not attachment contents. No source fetch; publication/relevance/original authenticity remain unverified. Unknown shapes stay incomplete.",
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
    for name, operation in DIRECT_PREVIEWS.items():
        policy = (
            "Use an actual discovered earnings_id OR symbol plus discovered quarter."
            if operation.endswith("get_earnings_filing")
            else "Select one company. Use bounded lookback_days OR from/to, with page and limit; record ids override filters, so use ids alone."
        )
        if operation.endswith("get_announcements"):
            policy += " include_extracted_information must remain false."
        rows.append(
            (
                name,
                f"Typed local preview for {operation}; exact inputs are THIS tool's MCP tools/list inputSchema, generated from reviewed Registry contracts. Supply top-level fields, without query/arguments/operations wrappers; Margin constructs the binding. {policy} No connect, fetch or automatic refresh; readiness/holds apply. Execute the plan separately with margin_run. Never guess schemas from memory or provider documentation.",
                preview_schema(operation, registry),
                False,
                False,
                False,
            )
        )
    for name, function in DIRECT_REVIEWS.items():
        inputs = deepcopy(SCHEMAS[function])
        inputs["properties"]["why"] = deepcopy(WHY)
        readonly = function in {
            "protocols.list_workflows",
            "evidence.render_citations",
            "evidence.audit_answer",
            "evidence.check_numeric_claim",
            "sentiment.aggregate",
        }
        rows.append(
            (
                name,
                f"{REVIEW_HELP[function]} Use THIS advertised exact inputSchema at top level; no function/arguments wrapper. Follow next_steps and complete required host input. No provider/LLM call; semantic judgments are host reports, not original authentication.",
                inputs,
                readonly,
                readonly or function == "review.submit",
                False,
            )
        )
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
    for name, function in DIRECT_COMPANY.items():
        rows.append(
            (
                name,
                "Inspect WHICH fields/calculations are supported across profitability, cash conversion and liquidity in ONE company financial response. Prefer this for data availability/readiness questions; company_profitability only computes profitability measures. Fixed readiness workflow: no function selector. execute=false previews and STOPs without data calls. Later execute=true needs a stable idempotency_key plus user authorization and allowance; at most one BharatStock request, zero Drishti. No numeric readiness report.rows: read report.readiness and report.valuation_readiness. No forecasts, assumptions, imputation or source verification. DCF is separate margin_calculate_dcf with explicit inputs. Follow this tool's exact top-level schema and same-tool next_steps; no generic plan/run.",
                fresh_company_schema(function),
                False,
                True,
                True,
            )
        )
    return {
        name: types.Tool(
            name=name,
            description=(
                "Use only returned evidence or explicit user-supplied values; never fabricate data to recover from an error. "
                + description
                if name in DIRECT_FUNCTIONS
                or name in DIRECT_COMPANY
                or name
                in {
                    "margin_company_finance",
                    "margin_company_preview",
                    "margin_calculate",
                    "margin_facts",
                }
                else description
            ),
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
