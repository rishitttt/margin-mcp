"""Fresh-fetch company finance with compact, process-local duplicate protection."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from dataclasses import asdict
from uuid import uuid4

from margin.analysis import company
from margin.analysis.facts import FIELDS
from margin.analysis.presentation import metric_entry
from margin.analysis.reporting import company_report
from margin.analysis.service import obj
from margin.core.contracts import DomainError, OperationRequest, encoded_size
from margin.core.validation import validation_summary
from margin.evidence.results import data_payload

RESPONSE_LIMIT = 32 * 1024
RESPONSE_VERSION = "margin.company_finance.v2"
EXECUTION_CONTRACT = {
    "version": "margin.company_execution.v1",
    "scope": "Fresh-company convenience workflow, not the legacy retained-source plan/run route.",
    "provider": "bharatstock",
    "workflow_selection": {
        "field_support_across_metric_groups": "finance.company_data_readiness",
        "purpose": "Inspect profitability, cash-conversion, liquidity and other eligibility in one financial response; previews contain no fetched facts.",
    },
    "valuation": {
        "explicit_function": "finance.calculate_dcf",
        "valid_company_selector": False,
        "requires_explicit_assumptions": True,
    },
    "preview": {
        "execute": False,
        "maximum_provider_requests": {"bharatstock": 0, "drishti": 0},
        "may_be_held_by_configuration": True,
    },
    "execution": {
        "execute": True,
        "idempotency_key_required": True,
        "session_id_required": False,
        "maximum_provider_requests": {"bharatstock": 1, "drishti": 0},
        "estimated_drishti_credits": 0,
        "prerequisites": [
            "BharatStock key loaded in backend",
            "remaining process allowance and provider entitlement",
            "supported inputs and enough compatible returned periods/fields",
        ],
        "auth_note": "A configured key may be unverified until the first actual request; status alone is not a failed authentication.",
    },
    "bounds": {
        "page": 1,
        "rows": {"annual": 2, "quarterly": 8},
        "automatic_extra_pages": False,
        "automatic_retries": False,
        "account_wide_quota_enforcement": False,
    },
    "replay": "Repeat identical financial inputs and key to wait/read without another fetch in this owner process; a new key is new retrieval. Restart loses duplicate control, not account usage.",
    "answer_fields": {
        "ordinary": "report.rows",
        "data_readiness": ["report.readiness", "report.valuation_readiness"],
        "presentation": "Preserve returned displays, periods, units, definitions and holds; data can remain incomplete.",
        "source_authentication": "Provider values are not independently verified originals.",
    },
}


def execution_contract():
    return copy.deepcopy(EXECUTION_CONTRACT)


KEY = {"type": "string", "pattern": r"^[A-Za-z0-9_-]{8,100}$"}
SCHEMA = obj(
    {
        "function": {
            "enum": sorted(company.FUNCTIONS),
            "description": "Choose by the user's goal. Annual growth is company_growth, not company_ttm. "
            + "; ".join(
                f"{name}: {description}" for name, description in company.FUNCTIONS.items()
            ),
        },
        "ticker": copy.deepcopy(company.SCHEMA["properties"]["ticker"]),
        "exchange": {"enum": ["NSE", "BSE"], "default": "NSE"},
        "period_type": {"enum": ["annual", "quarterly"]},
        "basis": {"enum": ["consolidated", "standalone"], "default": "consolidated"},
        "metric": {
            "enum": list(FIELDS),
            "default": "revenue",
            "description": "Selected metric for growth/CAGR/TTM and readiness checks; other metric groups return their defined components. TTM cannot sum balance-sheet stocks.",
        },
        "execute": {"type": "boolean", "default": False},
        "idempotency_key": KEY,
        "wait_seconds": {"type": "integer", "minimum": 0, "maximum": 30, "default": 30},
        "include_details": {
            "type": "boolean",
            "default": False,
            "description": "Return raw-unit calculation inputs/values separately from the canonical report; same inputs/key do not fetch again.",
        },
    },
    ["function", "ticker"],
)
SCHEMA["allOf"] = [
    {
        "if": {"properties": {"execute": {"const": True}}, "required": ["execute"]},
        "then": {"required": ["idempotency_key"]},
    },
    *company.function_constraints(),
]


def selected_input(item):
    """Preserve used values/context without shipping duplicate full source objects."""
    record = {
        key: copy.deepcopy(item.get(key))
        for key in (
            "issuer",
            "metric",
            "definition",
            "value",
            "unit",
            "unit_origin",
            "period_type",
            "period_start",
            "period_end",
            "basis",
            "adjustment",
        )
    }
    source = item.get("source", {})
    record["source_path"] = source.get("field_path")
    record["row_reference"] = source.get("row_reference")
    record["period_start_origin"] = source.get("period_start_origin")
    if item.get("unit") in {"INR", "INR_per_share"}:
        view = metric_entry(
            item["metric"],
            item["definition"],
            item.get("value"),
            source.get("field_path"),
            per_share=item["unit"] == "INR_per_share",
        )
        record["display"] = view["display"]
    return record


class CompanyFinance:
    """No retained raw financial sources; only bounded request controls and answers."""

    def __init__(self, service):
        self.service = service
        self.requests = {}
        self.capacity = min(200, service.settings.max_records)
        self.closed = False

    def prepare(self, arguments):
        problem = validation_summary(SCHEMA, arguments)
        if problem:
            raise DomainError("invalid_input", "Check company finance inputs. " + problem)
        args = {
            "function": arguments["function"],
            "ticker": arguments["ticker"].upper(),
            "exchange": arguments.get("exchange", "NSE"),
            "basis": arguments.get("basis", "consolidated"),
            "period_type": arguments.get(
                "period_type", company.default_period(arguments["function"])
            ),
            "metric": arguments.get("metric", "revenue"),
            "money_unit": "auto",
            "source_run_id": None,
            "source_operation_id": "fresh-request",
        }
        company.validate(args["function"], {k: v for k, v in args.items() if k != "function"})
        # Preserve the reviewed registry bounds; mixed bases can leave fewer
        # usable periods. Report that gap rather than fetching another page.
        size = EXECUTION_CONTRACT["bounds"]["rows"][args["period_type"]]
        request = OperationRequest(
            "bharatstock.get_financials",
            {k: args[k] for k in ("ticker", "exchange", "period_type")}
            | {"page": EXECUTION_CONTRACT["bounds"]["page"], "page_size": size},
        )
        self.service.registry.validate(request)
        # Keys and selectors must not become a second channel for credentials.
        raw = json.dumps(arguments, allow_nan=False)
        if any(secret in raw for secret in self.service.sanitizer.secrets):
            raise DomainError("invalid_input", "Credentials cannot be supplied as finance inputs.")
        return args, request

    def preview(self, args, request, submitted=None):
        submitted = submitted or {}
        bindings = {
            key: copy.deepcopy(value) for key, value in args.items() if key in SCHEMA["properties"]
        }
        bindings.update(
            {
                key: copy.deepcopy(submitted[key])
                for key in ("idempotency_key", "include_details", "wait_seconds")
                if key in submitted
            }
        )
        bindings["execute"] = True
        required = [] if "idempotency_key" in bindings else ["idempotency_key"]
        return {
            "response_version": RESPONSE_VERSION,
            "status": "preview",
            "preview_summary": {
                "status": "preview",
                "data_fetched": False,
                "financial_readiness_assessed": False,
                "result_fields_after_execution": (
                    ["report.readiness", "report.valuation_readiness"]
                    if args["function"] == "finance.company_data_readiness"
                    else ["report.rows"]
                ),
                "provider_requests_made": {"bharatstock": 0, "drishti": 0},
                "planned_execution_maximum_provider_requests": copy.deepcopy(
                    EXECUTION_CONTRACT["execution"]["maximum_provider_requests"]
                ),
                "missing_fields_for_preview": [],
                "missing_fields_for_execution": required.copy(),
                "execution_input_complete": not required,
                "preview_authorizes_execution": False,
                "instruction": "Preview is complete. Stop here for a preview-only task. Execution is a separate authorized action with remaining allowance.",
            },
            "function": args["function"],
            "selection": {
                k: v
                for k, v in args.items()
                if k not in {"function", "source_run_id", "source_operation_id"}
            },
            "data_operation": {
                "operation": request.operation,
                "method": "GET",
                "endpoint": "/v1/stocks/{ticker}/financials",
                "arguments": copy.deepcopy(request.arguments),
            },
            "maximum_provider_requests": copy.deepcopy(
                EXECUTION_CONTRACT["execution"]["maximum_provider_requests"]
            ),
            "estimated_drishti_credits": EXECUTION_CONTRACT["execution"][
                "estimated_drishti_credits"
            ],
            "company_execution_contract": execution_contract(),
            "creates_plan_id": False,
            "next_steps": [
                {
                    "kind": "execute_fresh_company_finance",
                    "function": args["function"],
                    "bound_arguments": bindings,
                    "required_host_fields": required,
                    "is_complete_input": not required,
                    "requires_execution_authorization": True,
                    "creates_plan_id": False,
                    "schema_source": "Fresh company-finance input schema. Bindings are input-ready only after required fields are supplied; schema completeness is not execution permission.",
                    "purpose": "Execute this same workflow only within existing user authorization and remaining allowance. This preview is not a generic plan; no plan ID or additional provider request has been created.",
                }
            ],
            "warnings": [
                "No provider call has occurred. Set execute=true with a stable idempotency_key to fetch and calculate.",
                "A new executed request fetches fresh page 1 only, even if other sources are retained. Enough usable rows are not guaranteed.",
                "Reporting basis is selected locally; missing fields or periods remain incomplete. DCF requires separate explicit assumptions.",
            ],
        }

    async def call(self, arguments):
        if self.closed:
            raise DomainError(
                "unavailable", "The finance service is closing; no new work accepted."
            )
        args, request = self.prepare(arguments)
        if not arguments.get("execute", False):
            return self.preview(args, request, arguments)
        key = arguments["idempotency_key"]
        fingerprint = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()
        existing = self.requests.get(key)
        if existing:
            if existing["fingerprint"] != fingerprint:
                raise DomainError(
                    "idempotency_conflict",
                    "That key belongs to different financial inputs. Do not replace a lost request with a new key.",
                )
        else:
            if len(self.requests) >= self.capacity:
                raise DomainError(
                    "capacity",
                    "Finance request-control capacity reached; no new data request dispatched. Reconcile before restarting.",
                )
            existing = {"fingerprint": fingerprint, "request_id": uuid4().hex}
            # No await between lookup and insertion: concurrent calls join one task.
            self.requests[key] = existing
            existing["task"] = asyncio.create_task(
                self._execute(args, request, existing["request_id"]), name="margin-company-finance"
            )
        try:
            response = copy.deepcopy(
                await asyncio.wait_for(
                    asyncio.shield(existing["task"]), arguments.get("wait_seconds", 30)
                )
            )
            if not arguments.get("include_details", False):
                response.pop("details", None)
            return response
        except TimeoutError:
            return {
                "response_version": RESPONSE_VERSION,
                "status": "running",
                "request_id": existing["request_id"],
                "function": args["function"],
                "next_action": "Repeat margin_company_finance with the SAME financial inputs and idempotency_key to wait/read. Do not use a new key.",
                "idempotency_scope": "This core process only; restart loses duplicate protection and does not renew provider quota.",
            }

    async def _execute(self, args, request, request_id):
        output = {
            "request_id": request_id,
            "function": args["function"],
            "selection": {
                k: v
                for k, v in args.items()
                if k not in {"function", "source_run_id", "source_operation_id"}
            },
            "status": "failed",
            "values": {},
            "inputs": [],
            "issues": [],
            "warnings": [
                "Provider values are unverified; a correct calculation does not authenticate the original filing."
            ],
            "idempotency_scope": "This core process only; restart loses duplicate protection and does not renew provider quota.",
        }
        operation_id = uuid4().hex
        receipt = {}
        try:
            result = await self.service.execute(request, operation_id)
            receipt = result.receipt
            output["source"] = {
                "provider": "bharatstock",
                "operation_id": operation_id,
                "endpoint": "/v1/stocks/{ticker}/financials",
                "arguments": copy.deepcopy(request.arguments),
                "requested_at": receipt.get("requested_at"),
                "retrieved_at": receipt.get("retrieved_at"),
                "verification": "unverified",
                "citations": copy.deepcopy(result.citations),
                "additional_pages_fetched": False,
            }
            if result.status not in {"success", "empty"}:
                output.update(status=result.status, error=result.error)
            else:
                data = data_payload(result.payload, result.payload_kind)
                rows = data.get("data") if isinstance(data, dict) else None
                output["source"]["rows_returned"] = len(rows) if isinstance(rows, list) else None
                args["source_operation_id"] = operation_id
                calculation = company.calculate_company(
                    args["function"],
                    {k: v for k, v in args.items() if k != "function"},
                    asdict(result),
                )
                output.update(
                    {
                        k: copy.deepcopy(v)
                        for k, v in calculation.items()
                        if k
                        in {
                            "status",
                            "values",
                            "issues",
                            "components",
                            "amount_unit",
                            "precision",
                            "calculation_function",
                            "function_version",
                        }
                    }
                )
                output["inputs"] = [selected_input(item) for item in calculation.get("inputs", [])]
                output["warnings"] = list(
                    dict.fromkeys(
                        [*output["warnings"], *result.warnings, *calculation.get("warnings", [])]
                    )
                )
        except asyncio.CancelledError:
            receipt = next(
                (r for r in reversed(self.service._receipts) if r["call_id"] == operation_id), {}
            )
            output.update(
                status="unknown" if receipt.get("uncertain_outcome") else "cancelled",
                error={
                    "code": "cancelled",
                    "message": "Core shutdown interrupted this request; reconcile dispatched usage before another attempt.",
                },
            )
        except DomainError as exc:
            output.update(
                status="incomplete",
                issues=[exc.message],
                error={"code": exc.code, "message": exc.message},
            )
        except Exception:
            output.update(
                status="failed",
                error={
                    "code": "internal_error",
                    "message": "Finance processing failed; unsafe diagnostics withheld. Do not resubmit with a new key.",
                },
            )
        output["usage"] = {
            "bharatstock_http_attempts": receipt.get("http_attempts", 0),
            "drishti_http_attempts": 0,
            "estimated_drishti_credits": 0,
            "uncertain_outcome": receipt.get("uncertain_outcome", False),
        }
        if output.get("error", {}).get("code") == "request_budget":
            output["error"]["scope"] = "local_process_allowance"
            output["error"]["observed_account_balance"] = None
            output["error"]["recovery_guidance"] = (
                "This local execution allowance is not the provider account balance. "
                "Do not buy credits or reset limits to complete a preview: use execute=false. "
                "Preview-only tasks must stop without execution. A later live trial needs an operator-allocated remaining allowance."
            )
        output = self.service.sanitizer.clean(output)
        details = {
            key: output.pop(key)
            for key in (
                "values",
                "inputs",
                "components",
                "amount_unit",
                "precision",
                "calculation_function",
                "function_version",
            )
            if key in output
        }
        output["response_version"] = RESPONSE_VERSION
        output["request_lifecycle"] = {
            "state": "finished",
            "success_is_reported_by": "status and component statuses; finished alone is not financial success",
            "same_key_action": "Read this existing request result; not refreshed data or another workflow.",
            "another_analysis_requires_separate_authorized_intent": True,
        }
        try:
            output["report"] = company_report(output, details)
            if args["function"] == "finance.company_data_readiness":
                output["report"]["valuation_readiness"].update(
                    copy.deepcopy(EXECUTION_CONTRACT["valuation"])
                )
        except Exception:
            # Complete the task with a bounded answer, not an exception traceback
            # retaining local provider data or inviting another charged request.
            return {
                **{
                    key: output[key]
                    for key in (
                        "response_version",
                        "request_id",
                        "function",
                        "usage",
                        "idempotency_scope",
                        "request_lifecycle",
                    )
                },
                "status": "failed",
                "error": {
                    "code": "reporting_error",
                    "message": "Report formatting failed; unsafe diagnostics withheld. The provider request may already have been charged. Reuse the same key; do not fetch again to repair reporting.",
                },
            }
        output["details"] = details
        if encoded_size(output) > RESPONSE_LIMIT:
            output = {
                k: output[k]
                for k in (
                    "response_version",
                    "request_id",
                    "function",
                    "usage",
                    "idempotency_scope",
                    "request_lifecycle",
                )
            }
            output.update(
                status="failed",
                error={
                    "code": "oversize_output",
                    "message": "Compact finance answer exceeded 32 KiB and was withheld. The provider request may already have been charged; do not retry with a new key.",
                },
            )
        return output

    async def close(self):
        self.closed = True
        tasks = [record["task"] for record in self.requests.values() if not record["task"].done()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.requests.clear()
