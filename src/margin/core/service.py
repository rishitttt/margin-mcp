"""Framework-independent operation, plan and run services."""

from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import time
from dataclasses import asdict
from datetime import date, timedelta
from urllib.parse import unquote
from uuid import uuid4

import httpx

from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest, OperationResult, encoded_size, now
from margin.core.registry import Registry, schema_hash
from margin.evidence.results import inspect_result
from margin.evidence.sanitize import Sanitizer
from margin.policy.ledger import Ledger
from margin.providers.bharatstock import BharatStockAdapter
from margin.providers.drishti import DrishtiAdapter
from margin.providers.synthetic import SyntheticDrishti, bharatstock_fixture


class ResearchService:
    def __init__(self, settings: Settings, *, bharatstock=None, drishti=None):
        self.settings = settings
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
            "note": "No network is performed by status. Process restart resets the local ledger.",
        }

    def capabilities(self):
        return self.registry.capabilities()

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
            # Credentials must never be used as a search/filter value.
            supplied = json.dumps(request.arguments)
            for _ in range(3):
                supplied = unquote(supplied)
            if any(secret in supplied for secret in self.sanitizer.secrets):
                raise DomainError(
                    "invalid_input", "Credential-like data cannot be passed as operation arguments."
                )
            spec = self.registry.validate(request)
            credits = self.registry.estimate(request)
            estimated_credits += credits
            expected[spec.provider] += 1
            clean_ops.append(
                {
                    "operation": request.operation,
                    "arguments": request.arguments,
                    "estimated_credits": credits,
                    "schema_hash": schema_hash(spec.schema),
                    "operation_id": uuid4().hex,
                }
            )
        if estimated_credits > self.settings.drishti_credits:
            raise DomainError(
                "credit_budget", "The plan exceeds the configured process credit allowance."
            )
        plan = {
            "plan_id": uuid4().hex,
            "created_at": now(),
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
        if sum(not t.done() for t in self._tasks.values()) >= 5:
            raise DomainError("capacity", "Too many active runs; wait or cancel an existing run.")
        run_id = uuid4().hex
        run = {
            "run_id": run_id,
            "plan_id": plan_id,
            "mode": self.settings.mode,
            "status": "queued",
            "created_at": now(),
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
        return copy.deepcopy(stored[1])

    async def cancel(self, run_id):
        self.get_run(run_id)
        task = self._tasks[run_id]
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            if self.runs[run_id]["status"] == "queued":
                self.runs[run_id]["status"] = "cancelled"
                self.runs[run_id]["finished_at"] = now()
                for state in self.runs[run_id]["operations"]:
                    state["status"] = "cancelled"
        return self.get_run(run_id)

    async def _room(self, run_id):
        self._expire()
        current_runs = {key[0] for key in self._buffers}
        size = sum(encoded_size(v[1]) for v in self._buffers.values())
        while (
            size + self._reserved_buffer_bytes + self.settings.max_result_bytes
            > self.settings.max_buffer_bytes
            or (run_id not in current_runs and len(current_runs) >= self.settings.max_payload_runs)
        ):
            victim = next(
                (
                    k[0]
                    for k in self._buffers
                    if self.runs[k[0]]["status"] not in {"queued", "running"}
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
                    if all(s in {"success", "empty"} for s in states)
                    else "partial"
                    if any(s in {"success", "empty"} for s in states)
                    else "failed"
                )
            run["finished_at"] = now()

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
                "retrieved_at": now(),
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
        tasks = [t for t in self._tasks.values() if not t.done()]
        if self._connection_task and not self._connection_task.done():
            tasks.append(self._connection_task)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for provider in self.providers.values():
            await provider.close()
        self._buffers.clear()


def overview_operations(symbol: str, exchange: str, modules: list[str], *, start=None, end=None):
    """Small explicit preset, no live lookup or implicit identity enrichment."""
    today = date.today()
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
