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
from margin.analysis.service import obj
from margin.core.contracts import DomainError, OperationRequest, encoded_size
from margin.core.validation import validation_summary
from margin.evidence.results import data_payload

RESPONSE_LIMIT = 32 * 1024
KEY = {"type": "string", "pattern": r"^[A-Za-z0-9_-]{8,100}$"}
SCHEMA = obj(
    {
        "function": {"enum": sorted(company.FUNCTIONS)},
        "ticker": copy.deepcopy(company.SCHEMA["properties"]["ticker"]),
        "exchange": {"enum": ["NSE", "BSE"], "default": "NSE"},
        "period_type": {"enum": ["annual", "quarterly"]},
        "basis": {"enum": ["consolidated", "standalone"], "default": "consolidated"},
        "metric": {"enum": list(FIELDS), "default": "revenue"},
        "execute": {"type": "boolean", "default": False},
        "idempotency_key": KEY,
        "wait_seconds": {"type": "integer", "minimum": 0, "maximum": 30, "default": 30},
    },
    ["function", "ticker"],
)
SCHEMA["allOf"] = [
    {
        "if": {"properties": {"execute": {"const": True}}, "required": ["execute"]},
        "then": {"required": ["idempotency_key"]},
    }
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
                "period_type", "quarterly" if arguments["function"].endswith("_ttm") else "annual"
            ),
            "metric": arguments.get("metric", "revenue"),
            "money_unit": "auto",
            "source_run_id": None,
            "source_operation_id": "fresh-request",
        }
        company.validate(args["function"], {k: v for k, v in args.items() if k != "function"})
        # Preserve the reviewed registry bounds; mixed bases can leave fewer
        # usable periods. Report that gap rather than fetching another page.
        size = 8 if args["period_type"] == "quarterly" else 2
        request = OperationRequest(
            "bharatstock.get_financials",
            {k: args[k] for k in ("ticker", "exchange", "period_type")}
            | {"page": 1, "page_size": size},
        )
        self.service.registry.validate(request)
        # Keys and selectors must not become a second channel for credentials.
        raw = json.dumps(arguments, allow_nan=False)
        if any(secret in raw for secret in self.service.sanitizer.secrets):
            raise DomainError("invalid_input", "Credentials cannot be supplied as finance inputs.")
        return args, request

    def preview(self, args, request):
        return {
            "status": "preview",
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
            "maximum_provider_requests": {"bharatstock": 1, "drishti": 0},
            "estimated_drishti_credits": 0,
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
            return self.preview(args, request)
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
            return copy.deepcopy(
                await asyncio.wait_for(
                    asyncio.shield(existing["task"]), arguments.get("wait_seconds", 30)
                )
            )
        except TimeoutError:
            return {
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
        output = self.service.sanitizer.clean(output)
        if encoded_size(output) > RESPONSE_LIMIT:
            output = {
                k: output[k] for k in ("request_id", "function", "usage", "idempotency_scope")
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
