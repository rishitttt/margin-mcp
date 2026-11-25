"""Framework-independent operation, plan and run services."""

from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import time
from dataclasses import asdict
from datetime import UTC, date, datetime, timedelta
from urllib.parse import unquote
from uuid import uuid4

import httpx
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from margin.analysis import company
from margin.analysis.facts import prepare_financial_facts
from margin.analysis.presentation import financial_view
from margin.analysis.service import SPECS, calculate
from margin.analysis.service import capabilities as analysis_capabilities
from margin.core.company_finance import CompanyFinance
from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest, OperationResult, encoded_size, now
from margin.core.registry import Registry, schema_hash
from margin.evidence.results import inspect_result
from margin.evidence.review_sources import project_sources
from margin.evidence.sanitize import Sanitizer
from margin.policy.ledger import Ledger
from margin.protocols.service import ReviewService
from margin.providers.bharatstock import BharatStockAdapter
from margin.providers.drishti import DrishtiAdapter
from margin.providers.synthetic import SyntheticDrishti, bharatstock_fixture


class ResearchService:
    def __init__(self, settings: Settings, *, bharatstock=None, drishti=None, clock=now):
        self.settings = settings
        self.clock = clock
        self.registry = Registry(settings)
        self.sanitizer = Sanitizer((settings.bharatstock_key, settings.drishti_key))
        self.ledger = Ledger(
            {"bharatstock": settings.bharatstock_requests, "drishti": settings.drishti_requests},
            settings.drishti_credits,
            paced=settings.mode == "live",
        )
        if bharatstock is None:
            transport = (
                httpx.MockTransport(bharatstock_fixture) if settings.mode == "synthetic" else None
            )
            bharatstock = BharatStockAdapter(
                self.ledger,
                settings.bharatstock_key if settings.mode == "live" else "fixture-only",
                transport=transport,
                max_bytes=settings.max_result_bytes,
            )
        self.providers = {
            "bharatstock": bharatstock,
            "drishti": drishti
            if drishti is not None
            else (
                SyntheticDrishti(self.ledger, settings)
                if settings.mode == "synthetic"
                else DrishtiAdapter(self.ledger, settings)
            ),
        }
        self._locks = {p: asyncio.Lock() for p in self.providers}
        self._uncertain_providers = set()
        self.plans = {}
        self.runs = {}
        self._idempotency = {}
        self._tasks = {}
        self._buffers = {}
        self._retention_lock = asyncio.Lock()
        self._reserved_buffer_bytes = 0
        self._receipts = []
        self._connection_task = None
        self.company_finance_workflow = CompanyFinance(self)
        self.reviews = ReviewService(
            sanitizer=self.sanitizer,
            mode=settings.mode,
            ttl=settings.result_ttl,
            max_records=settings.max_records,
            max_bytes=settings.max_buffer_bytes,
        )

    def status(self):
        return {
            "mode": self.settings.mode,
            "synthetic_scenario": self.settings.synthetic_fault
            if self.settings.mode == "synthetic"
            else None,
            "accounting_kind": "simulated attempts and estimated credits"
            if self.settings.mode == "synthetic"
            else "observed HTTP attempts; credit estimates, not measured account debits",
            "ledger": self.ledger.snapshot(),
            "providers": {
                "bharatstock": {
                    "configured": bool(self.settings.bharatstock_key)
                    or self.settings.mode == "synthetic",
                    "transport": "REST",
                    "live_auth_verified_this_process": any(
                        r["provider"] == "bharatstock" and r["status"] in {"success", "empty"}
                        for r in self._receipts
                    )
                    and self.settings.mode == "live",
                },
                "drishti": self.providers["drishti"].status(),
            },
            "uncertain_providers": sorted(self._uncertain_providers),
            "last_historical_balance": {"date": "2026-10-09", "credits": 986, "current": False},
            "receipt_count": len(self._receipts),
            "company_finance_requests": {
                "used": len(self.company_finance_workflow.requests),
                "limit": self.company_finance_workflow.capacity,
                "retention": "Compact answers and duplicate-control keys only; no raw financial source buffers. Process lifetime only.",
            },
            "note": "No network is performed by status. Process restart resets the local ledger.",
        }

    def _assert_metadata(self, operation):
        if self.settings.mode == "live" and operation.startswith("drishti."):
            self.providers["drishti"].assert_ready(self.registry.spec(operation))

    def capabilities(self):
        entries = self.registry.capabilities()
        for item in entries:
            if item["enabled"]:
                try:
                    self._assert_metadata(item["operation"])
                except DomainError as error:
                    item.update(enabled=False, held_reason=error.message, held_code=error.code)
        return entries

    def review_capabilities(self):
        return self.reviews.capabilities()

    def review(self, function, arguments):
        return self.reviews.invoke(function, arguments)

    def import_review_sources(self, run_id, operation_id, issuer):
        """Copy bounded retained provider text to the review store; no request/refetch."""
        if (
            not isinstance(issuer, str)
            or not 1 <= len(issuer) <= 100
            or self.sanitizer.text(issuer) != issuer
        ):
            raise DomainError(
                "invalid_input", "Supply a bounded issuer identifier, without credentials."
            )
        result = self.get_result(run_id, operation_id)
        if result["status"] not in {"success", "empty"}:
            raise DomainError(
                "source_unavailable", "Import only successful retained provider data."
            )
        supplied_ticker = result.get("receipt", {}).get("arguments", {}).get("ticker")
        supplied_exchange = result.get("receipt", {}).get("arguments", {}).get("exchange")
        if supplied_ticker and issuer != f"{supplied_exchange}:{supplied_ticker}":
            raise DomainError(
                "incompatible_source", "Issuer does not match the financial source receipt."
            )
        selected_symbols = (
            result.get("receipt", {}).get("arguments", {}).get("query", {}).get("symbols", [])
        )
        if selected_symbols and issuer.split(":")[-1] not in selected_symbols:
            raise DomainError(
                "incompatible_source", "Declared issuer does not match the requested symbol filter."
            )
        if result["operation"] == "bharatstock.get_financials":
            # Table evidence stays an attributed provider record, not an issuer filing.
            return {
                "status": "incomplete",
                "sources": [],
                "note": "Use reviewed financial facts for numeric checks; no original-document locator was supplied by this result.",
            }
        sources, record_provenance, skipped = project_sources(result, issuer)
        if not sources:
            return {
                "status": "incomplete" if skipped else "empty",
                "sources": [],
                "skipped": skipped,
                "note": "No supported source-bearing rows; no fetch was attempted.",
            }
        # Same schema validation as host registration, with provider origin assigned internally.
        from jsonschema import Draft202012Validator

        from margin.protocols.schemas import SCHEMAS as REVIEW_SCHEMAS

        try:
            Draft202012Validator(
                REVIEW_SCHEMAS["evidence.register_sources"], format_checker=FormatChecker()
            ).validate({"sources": sources})
        except ValidationError:
            raise DomainError(
                "unsupported_mapping", "Provider rows do not fit the source handoff contract."
            ) from None
        imported = self.reviews.register_sources(
            sources,
            origin="retained_provider",
            record_provenance=record_provenance,
            provenance={
                "run_id": run_id,
                "operation_id": operation_id,
                "path_root": "decoded_provider_payload",
                "issuer_origin": "caller_declared_filter_target",
                "mode": result["mode"],
                "operation": result["operation"],
            },
        )
        imported["skipped"] = skipped
        imported["warnings"] = [
            "Imported text is a provider summary, not extracted attachment contents or original-source verification.",
            "Issuer attribution follows the declared target; multi-company text still requires host relevance review.",
            "Provider date is not treated as publication date without an explicit published_at field.",
        ]
        if skipped:
            imported["status"] = "partial"
        return imported

    def calculation_capabilities(self):
        return analysis_capabilities()

    def calculate(self, operation, arguments):
        try:
            supplied = json.dumps(arguments, allow_nan=False)
        except (ValueError, TypeError, RecursionError):
            raise DomainError(
                "invalid_input", "Calculation arguments must be bounded finite JSON data."
            ) from None
        for _ in range(3):
            supplied = unquote(supplied)
        if any(secret in supplied for secret in self.sanitizer.secrets):
            raise DomainError(
                "invalid_input", "Credentials cannot be passed as calculation inputs."
            )
        if encoded_size(arguments) > 64 * 1024:
            raise DomainError("invalid_input", "Calculation inputs exceed 64 KiB.")
        output = calculate(operation, arguments)
        if encoded_size(output) > self.settings.max_result_bytes:
            raise DomainError("oversize_output", "Calculation output exceeded the byte bound.")
        return self.sanitizer.clean(output)

    def prepare_facts(self, run_id, operation_id, money_unit="auto"):
        result = self.get_result(run_id, operation_id)
        return prepare_financial_facts(result, money_unit)

    async def company_finance(self, **arguments):
        """Self-contained fresh financials retrieval and deterministic calculation."""
        return await self.company_finance_workflow.call(arguments)

    def financial_sources(self):
        """Local retained financial responses only; no discovery/refetch."""
        self._expire()
        return [
            {
                "run_id": run_id,
                "operation_id": op_id,
                "arguments": copy.deepcopy(value["receipt"]["arguments"]),
                "retrieved_at": value["receipt"]["retrieved_at"],
                "status": value["status"],
            }
            for (run_id, op_id), (_, value) in reversed(list(self._buffers.items()))
            if value["operation"] == "bharatstock.get_financials"
            and value["status"] in {"success", "empty"}
        ]

    def plan_financial(
        self,
        function,
        ticker,
        exchange,
        period_type="annual",
        basis="consolidated",
        money_unit="auto",
        metric="revenue",
        source=None,
        fetch_missing=False,
    ):
        """Resolve reuse versus one data dependency before paid intent is submitted."""
        if self.settings.mode == "live" and money_unit not in (None, "auto", "INR"):
            raise DomainError(
                "unit_conflict",
                "Live BharatStock financials use documented INR. Choose auto/INR and convert prepared facts separately.",
            )
        arguments = {
            "ticker": ticker,
            "exchange": exchange,
            "period_type": period_type,
            "basis": basis,
            "money_unit": money_unit,
            "metric": metric,
            "source_operation_id": "$financials",
            "source_run_id": None,
        }
        company.validate(function, arguments)
        if not isinstance(fetch_missing, bool):
            raise DomainError("invalid_input", "fetch_missing must be boolean.")
        sources = self.financial_sources()
        if source is not None:
            if not isinstance(source, dict) or set(source) != {"run_id", "operation_id"}:
                raise DomainError("invalid_input", "Select a retained run/operation reference.")
            if not all(isinstance(v, str) and 1 <= len(v) <= 100 for v in source.values()):
                raise DomainError("invalid_input", "Source references must be bounded string IDs.")
            # Explicit expired/wrong sources must never trigger replacement data calls.
            self.get_result(source["run_id"], source["operation_id"])
            matches = [s for s in sources if all(s[k] == source[k] for k in source)]
            if not matches:
                raise DomainError(
                    "incompatible_source", "Choose a successful retained financial result."
                )
            selected = matches[0]
            if any(
                selected["arguments"].get(k) != arguments[k]
                for k in ("ticker", "exchange", "period_type")
            ):
                raise DomainError(
                    "incompatible_source", "Source does not match the selected listing/period type."
                )
        else:
            selected = next(
                (
                    s
                    for s in sources
                    if all(
                        s["arguments"].get(k) == arguments[k]
                        for k in ("ticker", "exchange", "period_type")
                    )
                ),
                None,
            )
        operations = []
        if selected:
            arguments.update(
                source_run_id=selected["run_id"], source_operation_id=selected["operation_id"]
            )
        elif fetch_missing:
            operations.append(
                {
                    "operation": "bharatstock.get_financials",
                    "arguments": {
                        "ticker": ticker,
                        "exchange": exchange,
                        "period_type": period_type,
                        "page": 1,
                        "page_size": 4 if period_type == "quarterly" else 2,
                    },
                }
            )
        else:
            raise DomainError(
                "source_required",
                "No matching retained financials. Allow one financials request and preview again, or retrieve financials first.",
            )
        operations.append({"operation": function, "arguments": arguments})
        return self.create_plan(operations)

    def plan_company(self, symbol, exchange, modules, *, start=None, end=None):
        plan = self.create_plan(
            overview_operations(
                symbol,
                exchange,
                modules,
                start=start,
                end=end,
                as_of=date.fromisoformat(self.clock()[:10]),
            )
        )
        plan["guidance"] = [
            "Confirm the listing identity.",
            "Inspect returned periods, missing fields, basis and units.",
            "Select compatible facts before calculations; unresolved context stays incomplete.",
            "Source locators are unverified; no automatic citation verification or sentiment protocol runs.",
        ]
        return plan

    async def connect_drishti(self):
        if self._connection_task and not self._connection_task.done():
            # Tabs/repeated submissions share an existing metadata attempt.
            return await asyncio.shield(self._connection_task)
        if self._tasks and any(not t.done() for t in self._tasks.values()):
            raise DomainError(
                "run_active", "Wait for active runs before refreshing provider metadata."
            )
        if "drishti" in self._uncertain_providers:
            raise DomainError(
                "uncertain_outcome",
                "Reconcile remote allowance before restarting an uncertain session.",
            )
        status = self.providers["drishti"].status()
        if status.get("metadata_fresh"):
            return status

        async def connect_once():
            async with self._locks["drishti"]:
                return await self.providers["drishti"].connect()

        self._connection_task = asyncio.create_task(connect_once(), name="margin-connect")
        # A disconnected HTTP waiter must not cancel/replay metadata work or log exceptions.
        self._connection_task.add_done_callback(
            lambda task: None if task.cancelled() else task.exception()
        )
        return await asyncio.shield(self._connection_task)

    def create_plan(self, operations: list[dict]) -> dict:
        if not 1 <= len(operations) <= 8:
            raise DomainError(
                "invalid_input", "A plan must contain one to eight explicit operations."
            )
        if len(self.plans) >= self.settings.max_records:
            raise DomainError(
                "capacity",
                "Plan capacity reached; finish/restart deliberately after reconciling allowance.",
            )
        clean_ops = []
        estimated_credits = 0
        expected = {"bharatstock": 0, "drishti": 0}
        for item in operations:
            if (
                not isinstance(item, dict)
                or set(item) != {"operation", "arguments"}
                or not isinstance(item["arguments"], dict)
            ):
                raise DomainError(
                    "invalid_input", "Each operation needs only operation and arguments."
                )
            request = OperationRequest(item["operation"], copy.deepcopy(item["arguments"]))
            if (
                not isinstance(request.operation, str)
                or encoded_size(request.arguments) > 64 * 1024
            ):
                raise DomainError("invalid_input", "Supply a function name and bounded arguments.")
            # Credentials must never be used as a search/filter value.
            supplied = json.dumps(request.arguments)
            for _ in range(3):
                supplied = unquote(supplied)
            if any(secret in supplied for secret in self.sanitizer.secrets):
                raise DomainError(
                    "invalid_input", "Credential-like data cannot be passed as operation arguments."
                )
            local = request.operation in SPECS or request.operation in company.FUNCTIONS
            if local:
                schema = (
                    SPECS[request.operation][1] if request.operation in SPECS else company.SCHEMA
                )
                try:
                    Draft202012Validator(schema, format_checker=FormatChecker()).validate(
                        request.arguments
                    )
                except ValidationError:
                    raise DomainError(
                        "invalid_input", "Check the financial function schema."
                    ) from None
                if request.operation in company.FUNCTIONS:
                    company.validate(request.operation, request.arguments)
                    if self.settings.mode == "live" and request.arguments["money_unit"] not in {
                        None,
                        "auto",
                        "INR",
                    }:
                        raise DomainError(
                            "unit_conflict",
                            "Live BharatStock financials use documented INR. Choose auto/INR before any data dispatch.",
                        )
                    if request.arguments["source_operation_id"] == "$financials":
                        if (
                            not clean_ops
                            or clean_ops[-1]["operation"] != "bharatstock.get_financials"
                        ):
                            raise DomainError(
                                "invalid_input", "Missing explicit financials dependency."
                            )
                        request.arguments["source_operation_id"] = clean_ops[-1]["operation_id"]
                credits = 0
            else:
                spec = self.registry.validate(request)
                self._assert_metadata(request.operation)
                schema = spec.schema
                credits = self.registry.estimate(request)
                expected[spec.provider] += 1
            estimated_credits += credits
            clean_ops.append(
                {
                    "operation": request.operation,
                    "arguments": request.arguments,
                    "estimated_credits": credits,
                    "schema_hash": schema_hash(schema),
                    "execution_kind": "local_calculation" if local else "provider",
                    "operation_id": uuid4().hex,
                }
            )
        if estimated_credits > self.settings.drishti_credits:
            raise DomainError(
                "credit_budget", "The plan exceeds the configured process credit allowance."
            )
        plan = {
            "plan_id": uuid4().hex,
            "created_at": self.clock(),
            "mode": self.settings.mode,
            "operations": clean_ops,
            "estimated_credits": estimated_credits,
            "data_operations": expected,
            "expires_after_seconds": 600,
            "warnings": [
                "Provider operation costs are estimates; MCP lifecycle/implicit discovery add HTTP requests.",
                "The plan is local and has made no provider calls.",
            ],
        }
        self.plans[plan["plan_id"]] = (time.monotonic(), copy.deepcopy(plan))
        return plan

    async def start_run(self, plan_id: str, idempotency_key: str) -> dict:
        if (
            not isinstance(idempotency_key, str)
            or not 8 <= len(idempotency_key) <= 100
            or not all(c.isalnum() or c in "-_" for c in idempotency_key)
        ):
            raise DomainError("invalid_input", "Use a unique 8–100 character idempotency key.")
        if idempotency_key in self._idempotency:
            previous_plan, run_id = self._idempotency[idempotency_key]
            if previous_plan != plan_id:
                raise DomainError(
                    "idempotency_conflict", "That submission key already belongs to another plan."
                )
            return self.get_run(run_id)
        if len(self.runs) >= self.settings.max_records:
            raise DomainError(
                "capacity", "Run/control-record capacity reached; no paid intent was dispatched."
            )
        record = self.plans.get(plan_id)
        if not record or time.monotonic() - record[0] > 600:
            raise DomainError("plan_expired", "Create a new local plan; no automatic refetch.")
        plan = copy.deepcopy(record[1])
        # Metadata can expire/change after preview. Reject before publishing paid intent.
        for operation in plan["operations"]:
            self._assert_metadata(operation["operation"])
        if sum(not t.done() for t in self._tasks.values()) >= 5:
            raise DomainError("capacity", "Too many active runs; wait or cancel an existing run.")
        run_id = uuid4().hex
        run = {
            "run_id": run_id,
            "plan_id": plan_id,
            "mode": self.settings.mode,
            "status": "queued",
            "created_at": self.clock(),
            "finished_at": None,
            "operations": [
                {
                    "operation_id": op["operation_id"],
                    "operation": op["operation"],
                    "status": "queued",
                    "receipt": None,
                    "error": None,
                }
                for op in plan["operations"]
            ],
        }
        # No await before publishing intent: repeated concurrent POSTs share one task.
        self._idempotency[idempotency_key] = (plan_id, run_id)
        self.runs[run_id] = run
        self._tasks[run_id] = asyncio.create_task(
            self._run(run_id, plan), name=f"margin-run-{run_id[:8]}"
        )
        return self.get_run(run_id)

    def get_run(self, run_id):
        if run_id not in self.runs:
            raise DomainError("not_found", "Unknown run ID.")
        return copy.deepcopy(self.runs[run_id])

    def recent_runs(self):
        """Bounded local control history; never returns/refetches provider payloads."""
        records = []
        for run in reversed(list(self.runs.values())[-20:]):
            plan = self.plans.get(run["plan_id"])
            ops = plan[1]["operations"] if plan else []
            listing = next(
                (
                    {"symbol": op["arguments"]["ticker"], "exchange": op["arguments"]["exchange"]}
                    for op in ops
                    if "ticker" in op["arguments"] and "exchange" in op["arguments"]
                ),
                None,
            )
            records.append(
                {
                    "run_id": run["run_id"],
                    "status": run["status"],
                    "created_at": run["created_at"],
                    "listing": listing,
                    "operations": [op["operation"] for op in ops],
                }
            )
        return self.sanitizer.clean(records)

    def _expire(self):
        clock = time.monotonic()
        for key, (stored, _) in list(self._buffers.items()):
            if clock - stored > self.settings.result_ttl:
                del self._buffers[key]

    def get_result(self, run_id, operation_id):
        run = self.get_run(run_id)
        if not any(op["operation_id"] == operation_id for op in run["operations"]):
            raise DomainError("not_found", "Unknown operation for this run.")
        self._expire()
        stored = self._buffers.get((run_id, operation_id))
        if not stored:
            raise DomainError(
                "result_unavailable",
                "Result is not ready or has expired/been evicted. It has not been refetched.",
            )
        result = copy.deepcopy(stored[1])
        display = financial_view(result)
        if display is not None:
            result["financial_view"] = display
        return result

    async def cancel(self, run_id):
        self.get_run(run_id)
        task = self._tasks[run_id]
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            if self.runs[run_id]["status"] == "queued":
                self.runs[run_id]["status"] = "cancelled"
                self.runs[run_id]["finished_at"] = self.clock()
                for state in self.runs[run_id]["operations"]:
                    state["status"] = "cancelled"
        return self.get_run(run_id)

    async def _room(self, run_id):
        self._expire()
        # A derived run must not evict the very source it is about to read.
        # Only active runs pin dependencies; TTL and total memory bounds still apply.
        pinned = set()
        for active in self.runs.values():
            if active["status"] not in {"queued", "running"}:
                continue
            record = self.plans.get(active["plan_id"])
            if record:
                for operation in record[1]["operations"]:
                    if operation["operation"] in company.FUNCTIONS:
                        source_run = operation["arguments"].get("source_run_id")
                        if source_run:
                            pinned.add(source_run)
        current_runs = {key[0] for key in self._buffers}
        size = sum(encoded_size(v[1]) for v in self._buffers.values())
        while (
            size + self._reserved_buffer_bytes + self.settings.max_result_bytes
            > self.settings.max_buffer_bytes
            or (run_id not in current_runs and len(current_runs) >= self.settings.max_payload_runs)
        ):
            # Prefer evicting derived result cards before financial source runs.
            # Repeated local calculations should not force a paid refetch.
            financial_runs = {
                key[0]
                for key, (_, value) in self._buffers.items()
                if value["operation"] == "bharatstock.get_financials"
            }
            victim = next(
                (
                    k[0]
                    for k in sorted(self._buffers, key=lambda key: key[0] in financial_runs)
                    if self.runs[k[0]]["status"] not in {"queued", "running"} and k[0] not in pinned
                ),
                None,
            )
            if victim is None:
                raise DomainError("capacity", "No safe result-buffer headroom; nothing dispatched.")
            for key in list(self._buffers):
                if key[0] == victim:
                    del self._buffers[key]
            current_runs.discard(victim)
            size = sum(encoded_size(v[1]) for v in self._buffers.values())

    async def _run(self, run_id, plan):
        run = self.runs[run_id]
        run["status"] = "running"
        try:
            # Sequential across a run for inspectability; independent runs share provider locks.
            for op in plan["operations"]:
                state = next(
                    s for s in run["operations"] if s["operation_id"] == op["operation_id"]
                )
                state["status"] = "running"
                async with self._retention_lock:
                    await self._room(run_id)
                    self._reserved_buffer_bytes += self.settings.max_result_bytes
                try:
                    if op.get("execution_kind") == "local_calculation":
                        result = self._execute_calculation(run_id, op)
                    else:
                        result = await self.execute(
                            OperationRequest(op["operation"], op["arguments"]), op["operation_id"]
                        )
                    value = asdict(result)
                    async with self._retention_lock:
                        self._buffers[(run_id, op["operation_id"])] = (time.monotonic(), value)
                finally:
                    self._reserved_buffer_bytes -= self.settings.max_result_bytes
                state.update(status=result.status, receipt=result.receipt, error=result.error)
                if result.status in {"unknown", "cancelled"}:
                    break
        except asyncio.CancelledError:
            # execute() records active uncertain spend before propagating cancellation.
            for state in run["operations"]:
                if state["status"] in {"queued", "running"}:
                    receipt = next(
                        (
                            r
                            for r in reversed(self._receipts)
                            if r["call_id"] == state["operation_id"]
                        ),
                        None,
                    )
                    state.update(
                        status=receipt["status"] if receipt else "cancelled", receipt=receipt
                    )
            run["status"] = "cancelled"
        except DomainError as e:
            for state in run["operations"]:
                if state["status"] in {"queued", "running"}:
                    state.update(status="blocked", error={"code": e.code, "message": e.message})
        except Exception:
            for state in run["operations"]:
                if state["status"] in {"queued", "running"}:
                    state.update(
                        status="failed",
                        error={
                            "code": "internal_error",
                            "message": "Internal execution failure; raw details withheld.",
                        },
                    )
        finally:
            for state in run["operations"]:
                if state["status"] in {"queued", "running"}:
                    state["status"] = "cancelled"
            if run["status"] != "cancelled":
                states = [s["status"] for s in run["operations"]]
                run["status"] = (
                    "completed"
                    if all(s in {"success", "empty", "not_meaningful"} for s in states)
                    else "partial"
                    if any(s in {"success", "empty", "partial"} for s in states)
                    else "failed"
                )
            run["finished_at"] = self.clock()

    def _execute_calculation(self, run_id, op):
        started = time.monotonic()
        requested_at = self.clock()
        arguments = copy.deepcopy(op["arguments"])
        result = OperationResult(
            op["operation_id"],
            op["operation"],
            "margin",
            self.settings.mode,
            "failed",
            payload_kind="analysis",
        )
        try:
            if op["operation"] in company.FUNCTIONS:
                source_run = arguments["source_run_id"] or run_id
                source = self.get_result(source_run, arguments["source_operation_id"])
                arguments["source_run_id"] = source_run
                output = company.calculate_company(op["operation"], arguments, source)
            else:
                output = self.calculate(op["operation"], arguments)
            if encoded_size(output) > self.settings.max_result_bytes - 8192:
                raise DomainError(
                    "oversize_output", "Financial output exceeds the retained result bound."
                )
            result.payload = self.sanitizer.clean(output)
            result.status = output["status"]
            result.warnings = output.get("warnings", [])
        except DomainError as e:
            result.status = "incomplete"
            result.error = {"code": e.code, "message": e.message}
        result.receipt = {
            "call_id": op["operation_id"],
            "operation": op["operation"],
            "provider": "margin",
            "mode": self.settings.mode,
            "status": result.status,
            "contract_version": "1.1",
            "requested_at": requested_at,
            "retrieved_at": self.clock(),
            "arguments": self.sanitizer.clean(arguments),
            "effective_arguments": self.sanitizer.clean(arguments),
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "http_attempts": 0,
            "estimated_credits": 0,
            "uncertain_outcome": False,
        }
        return result

    async def execute(self, request: OperationRequest, call_id=None) -> OperationResult:
        """Also callable directly by tests and the later MCP adapter."""
        call_id = call_id or uuid4().hex
        request = OperationRequest(request.operation, copy.deepcopy(request.arguments))
        supplied = json.dumps(request.arguments)
        for _ in range(3):
            supplied = unquote(supplied)
        if any(secret in supplied for secret in self.sanitizer.secrets):
            raise DomainError(
                "invalid_input", "Credentials cannot be passed as operation arguments."
            )
        spec = self.registry.validate(request)
        provider, credits = spec.provider, self.registry.estimate(request)
        result = OperationResult(
            call_id, request.operation, provider, self.settings.mode, "blocked"
        )
        reserved = acquired = dispatched = uncertain = False
        before = self.ledger.requests[provider]
        started = time.monotonic()
        cancellation = None
        requested_at = self.clock()
        try:
            if provider in self._uncertain_providers:
                raise DomainError(
                    "uncertain_outcome",
                    "Provider has an unresolved previous outcome; reconcile before restart.",
                )
            await asyncio.wait_for(self._locks[provider].acquire(), self.settings.queue_timeout)
            acquired = True
            before = self.ledger.requests[provider]
            if provider in self._uncertain_providers:
                raise DomainError(
                    "uncertain_outcome",
                    "A preceding call became uncertain while this call was queued; reconcile first.",
                )
            if provider == "drishti":
                self.providers[provider].assert_ready(spec)
            await self.ledger.reserve(provider, credits)
            reserved = True
            async with asyncio.timeout(self.settings.call_timeout):
                outcome = await self.providers[provider].execute(spec, request.arguments)
            dispatched = self.ledger.requests[provider] > before
            payload = self.sanitizer.clean(outcome.payload)
            if encoded_size(payload) > self.settings.max_result_bytes - 8192:
                raise DomainError(
                    "oversize_output",
                    "Result exceeded safe payload/receipt bounds; narrow the request.",
                )
            _, warnings, coverage, empty = inspect_result(payload, outcome.kind, spec.key)
            result.payload, result.payload_kind = payload, outcome.kind
            coverage["requested_arguments"] = self.sanitizer.clean(copy.deepcopy(request.arguments))
            result.warnings, result.coverage = warnings, coverage
            result.citations = self.sanitizer.citations(outcome.payload, payload)
            result.status = "failed" if outcome.is_error else "empty" if empty else "success"
            if outcome.is_error:
                result.error = {
                    "code": "upstream_tool_error",
                    "message": "Provider returned a sanitized tool execution error.",
                }
        except asyncio.CancelledError as e:
            cancellation = e
            dispatched = acquired and self.ledger.requests[provider] > before
            uncertain = dispatched
            result.status = "unknown" if dispatched else "cancelled"
            result.error = {
                "code": "uncertain_outcome" if dispatched else "cancelled",
                "message": "Cancelled; dispatched remote work may still consume quota.",
            }
        except TimeoutError:
            dispatched = acquired and self.ledger.requests[provider] > before
            uncertain = dispatched
            result.status = "unknown" if dispatched else "blocked"
            result.error = {
                "code": "uncertain_outcome" if dispatched else "queue_timeout",
                "message": "Deadline exceeded; no automatic retry or credit refund.",
            }
        except DomainError as e:
            dispatched = acquired and self.ledger.requests[provider] > before
            uncertain = e.uncertain and dispatched
            result.status = "unknown" if uncertain else "failed" if dispatched else "blocked"
            result.error = {"code": e.code, "message": e.message}
            result.payload = None
        except Exception:
            dispatched = acquired and self.ledger.requests[provider] > before
            uncertain = dispatched
            result.status = "unknown" if dispatched else "failed"
            result.payload = None
            result.error = {
                "code": "upstream_error",
                "message": "Unexpected provider/output failure; unsafe details withheld.",
            }
        finally:
            if reserved:
                await self.ledger.settle(credits, dispatched=dispatched, uncertain=uncertain)
            if acquired:
                self._locks[provider].release()
            if uncertain:
                self._uncertain_providers.add(provider)
            selectors = {
                k: v
                for k, v in request.arguments.items()
                if k
                in {
                    "ticker",
                    "exchange",
                    "period_type",
                    "from",
                    "to",
                    "page",
                    "page_size",
                    "symbol",
                    "quarter",
                    "earnings_id",
                }
            }
            result.receipt = {
                "call_id": call_id,
                "operation": spec.key,
                "provider": provider,
                "mode": self.settings.mode,
                "status": result.status,
                "contract_version": "1.1",
                "requested_at": requested_at,
                "retrieved_at": self.clock(),
                "arguments": self.sanitizer.clean(copy.deepcopy(request.arguments)),
                "effective_arguments": self.sanitizer.clean(copy.deepcopy(request.arguments)),
                "argument_resolution": "Explicit arguments sent unchanged; provider-side defaults are unknown.",
                "clock_policy": "UTC receipt clock; relative query windows are evaluated by the provider.",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "http_attempts": max(0, self.ledger.requests[provider] - before) if acquired else 0,
                "http_count_kind": "simulated" if self.settings.mode == "synthetic" else "observed",
                "estimated_credits": credits if dispatched else 0,
                "observed_credit_debit": None,
                "uncertain_outcome": uncertain,
                "selectors": self.sanitizer.clean(selectors),
                "schema_hash": schema_hash(spec.schema),
            }
            self._receipts.append(result.receipt)
            self._receipts[:] = self._receipts[-200:]
        if not cancellation and encoded_size(asdict(result)) > self.settings.max_result_bytes:
            result.payload = None
            result.citations = []
            result.coverage = {}
            result.warnings = []
            result.status = "failed"
            result.error = {
                "code": "oversize_output",
                "message": "Complete result with evidence exceeded the byte bound; withheld.",
            }
            result.receipt["status"] = result.status
        if cancellation:
            raise cancellation
        return result

    async def close(self):
        await self.company_finance_workflow.close()
        tasks = [t for t in self._tasks.values() if not t.done()]
        if self._connection_task and not self._connection_task.done():
            tasks.append(self._connection_task)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for provider in self.providers.values():
            await provider.close()
        self._buffers.clear()
        self.reviews.close()


def overview_operations(
    symbol: str,
    exchange: str,
    modules: list[str],
    *,
    start=None,
    end=None,
    as_of: date | None = None,
):
    """Small explicit preset, no live lookup or implicit identity enrichment."""
    today = as_of or datetime.now(UTC).date()
    dates = {
        "from": start or (today - timedelta(days=90)).isoformat(),
        "to": end or today.isoformat(),
    }
    base = {"ticker": symbol, "exchange": exchange}
    requests = []
    choices = {
        "snapshot": ("bharatstock.get_stock_quote", base),
        "quarterly": (
            "bharatstock.get_financials",
            base | {"period_type": "quarterly", "page": 1, "page_size": 4},
        ),
        "annual": (
            "bharatstock.get_financials",
            base | {"period_type": "annual", "page": 1, "page_size": 2},
        ),
        "ratios": ("bharatstock.get_stock_fundamentals", base),
        "prices": ("bharatstock.get_stock_prices", base | dates | {"page": 1, "page_size": 100}),
        "actions": ("bharatstock.get_corporate_actions", base | {"page": 1, "page_size": 5}),
        "news": (
            "drishti.get_news",
            {"query": {"symbols": [symbol], "lookback_days": 7, "page": 1, "limit": 2}},
        ),
        "announcements": (
            "drishti.get_announcements",
            {
                "query": {
                    "symbols": [symbol],
                    "lookback_days": 30,
                    "page": 1,
                    "limit": 2,
                    "detailed": False,
                }
            },
        ),
        "earnings": (
            "drishti.list_earnings",
            {
                "query": {
                    "symbols": [symbol],
                    "lookback_days": 365,
                    "page": 1,
                    "limit": 2,
                    "detailed": False,
                }
            },
        ),
    }
    if len(modules) != len(set(modules)):
        raise DomainError("invalid_input", "Select each module once.")
    for module in modules:
        if module not in choices:
            raise DomainError("invalid_input", "Unknown overview module.")
        op, args = choices[module]
        requests.append({"operation": op, "arguments": copy.deepcopy(args)})
    return requests
