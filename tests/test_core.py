import asyncio
import json
import time
from dataclasses import asdict

import pytest

from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest
from margin.core.service import ResearchService, overview_operations


async def wait(service, run):
    await service._tasks[run["run_id"]]
    return service.get_run(run["run_id"])


async def test_bounded_overview_retains_context_and_no_plan_side_effects():
    service = ResearchService(Settings())
    try:
        plan = service.create_plan(
            overview_operations(
                "SYNTHA",
                "NSE",
                ["snapshot", "quarterly", "prices", "news", "announcements", "earnings"],
            )
        )
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
        run = await wait(service, await service.start_run(plan["plan_id"], "overview-0001"))
        assert run["status"] == "completed"
        assert service.ledger.requests == {"bharatstock": 3, "drishti": 3}
        assert service.ledger.completed_estimated_credits == 4
        assert service.ledger.reserved_credits == 0
        results = {
            o["operation"]: service.get_result(run["run_id"], o["operation_id"])
            for o in run["operations"]
        }
        financials = results["bharatstock.get_financials"]["payload"]["data"]
        assert financials[0]["cash_flow_operating"] is None
        assert financials[0]["period_end_date"] == "2026-06-30"
        earnings = results["drishti.list_earnings"]["payload"]["structuredContent"]["data"]
        assert (
            earnings[0]["quarter"] == "q2_27"
        )  # Preserved, not merged into the older numeric quarter.
    finally:
        await service.close()


async def test_same_submission_is_idempotent_even_after_result_eviction():
    service = ResearchService(Settings(result_ttl=0.001))
    try:
        plan = service.create_plan(overview_operations("SYNTHA", "NSE", ["snapshot"]))
        a, b = await asyncio.gather(
            *(service.start_run(plan["plan_id"], "double-click-01") for _ in range(2))
        )
        assert a["run_id"] == b["run_id"]
        run = await wait(service, a)
        service._buffers.clear()
        again = await service.start_run(plan["plan_id"], "double-click-01")
        assert again["run_id"] == run["run_id"]
        assert service.ledger.requests["bharatstock"] == 1
        with pytest.raises(DomainError, match="not ready"):
            service.get_result(run["run_id"], run["operations"][0]["operation_id"])
        other = service.create_plan(overview_operations("SYNTHB", "BSE", ["snapshot"]))
        with pytest.raises(DomainError, match="another plan"):
            await service.start_run(other["plan_id"], "double-click-01")
    finally:
        await service.close()


async def test_plan_return_is_not_a_mutable_execution_contract():
    service = ResearchService(Settings())
    try:
        plan = service.create_plan(overview_operations("SYNTHA", "NSE", ["snapshot"]))
        plan["operations"][0]["arguments"]["ticker"] = "NOT_THE_APPROVED_COMPANY"
        run = await wait(service, await service.start_run(plan["plan_id"], "frozen-plan-01"))
        result = service.get_result(run["run_id"], run["operations"][0]["operation_id"])
        assert result["payload"]["symbol"] == "SYNTHA"
    finally:
        await service.close()


async def test_partial_failure_does_not_turn_live_or_failed_sections_into_fixtures():
    service = ResearchService(Settings(synthetic_fault="drishti_unavailable"))
    try:
        run = await wait(
            service,
            await service.start_run(
                service.create_plan(overview_operations("SYNTHA", "NSE", ["news", "snapshot"]))[
                    "plan_id"
                ],
                "partial-run-01",
            ),
        )
        assert run["status"] == "partial"
        assert [o["status"] for o in run["operations"]] == ["failed", "success"]
        assert all(o["receipt"]["mode"] == "synthetic" for o in run["operations"])
    finally:
        await service.close()


async def test_timeout_retains_estimate_and_blocks_dependent_replay():
    service = ResearchService(Settings(synthetic_delay=0.1, call_timeout=0.01))
    try:
        request = OperationRequest(
            "drishti.get_earnings_filing", {"earnings_id": "synthetic-record"}
        )
        first = await service.execute(request)
        assert first.status == "unknown"
        assert service.ledger.reserved_credits == 0
        assert service.ledger.completed_estimated_credits == 3
        assert service.ledger.uncertain_credits == 3
        second = await service.execute(request)
        assert second.status == "blocked"
        assert service.ledger.requests["drishti"] == 1
    finally:
        await service.close()


async def test_credit_and_request_limits_fail_before_network_attempt():
    service = ResearchService(Settings(drishti_credits=2, bharatstock_requests=0))
    try:
        with pytest.raises(DomainError, match="exceeds"):
            service.create_plan(
                [{"operation": "drishti.get_earnings_filing", "arguments": {"earnings_id": "rec"}}]
            )
        result = await service.execute(
            OperationRequest("bharatstock.get_stock_quote", {"ticker": "SYNTHA", "exchange": "NSE"})
        )
        assert result.status == "blocked" and service.ledger.requests["bharatstock"] == 0
    finally:
        await service.close()


async def test_earnings_citations_and_conflicting_values_are_both_visible_safely():
    service = ResearchService(Settings())
    try:
        result = await service.execute(
            OperationRequest("drishti.get_earnings_filing", {"earnings_id": "synth-earnings-1"})
        )
        wire = json.dumps(asdict(result))
        assert "synthetic-private-key-never-forward" not in wire
        assert "api_key=" not in wire
        assert all(c["requires_resolution"] and not c["verified"] for c in result.citations)
        fields = result.payload["structuredContent"]["consolidated"]
        assert (
            fields["revenue"] == 32
            and fields["revenue_from_operations_raw"]["current_period_value"] == 35
        )
        assert any("differ" in w for w in result.warnings)
    finally:
        await service.close()


async def test_cancelled_active_call_preserves_uncertain_receipt_and_cancels_queued_work():
    service = ResearchService(Settings(synthetic_delay=0.3))
    try:
        plan = service.create_plan(overview_operations("SYNTHA", "NSE", ["news", "announcements"]))
        run = await service.start_run(plan["plan_id"], "cancel-run-01")
        for _ in range(100):
            if service.ledger.requests["drishti"]:
                break
            await asyncio.sleep(0.001)
        cancelled = await service.cancel(run["run_id"])
        assert cancelled["status"] == "cancelled"
        assert cancelled["operations"][0]["status"] == "unknown"
        assert cancelled["operations"][0]["receipt"]["uncertain_outcome"]
        assert cancelled["operations"][1]["status"] == "cancelled"
        assert service.ledger.requests["drishti"] == 1
    finally:
        await service.close()


async def test_insufficient_buffer_room_blocks_before_dispatch():
    service = ResearchService(Settings(max_buffer_bytes=100))
    try:
        plan = service.create_plan(overview_operations("SYNTHA", "NSE", ["snapshot"]))
        run = await wait(service, await service.start_run(plan["plan_id"], "buffer-test-01"))
        assert run["status"] == "failed" and service.ledger.requests["bharatstock"] == 0
    finally:
        await service.close()


async def test_credential_in_direct_core_arguments_is_rejected():
    secret = "test-secret-long-enough"
    service = ResearchService(Settings(bharatstock_key=secret))
    try:
        with pytest.raises(DomainError, match="Credentials"):
            await service.execute(
                OperationRequest("bharatstock.search_stocks", {"q": secret, "limit": 2})
            )
        assert service.ledger.requests["bharatstock"] == 0
    finally:
        await service.close()


async def test_expired_plan_cannot_be_dispatched():
    service = ResearchService(Settings())
    try:
        plan = service.create_plan(overview_operations("SYNTHA", "NSE", ["snapshot"]))
        service.plans[plan["plan_id"]] = (time.monotonic() - 601, service.plans[plan["plan_id"]][1])
        with pytest.raises(DomainError, match="new local plan"):
            await service.start_run(plan["plan_id"], "expired-plan-01")
        assert service.ledger.requests["bharatstock"] == 0
    finally:
        await service.close()


async def test_queued_call_rechecks_uncertain_provider_after_acquiring_lock():
    service = ResearchService(Settings(synthetic_delay=0.1, call_timeout=0.01))
    try:
        request = OperationRequest("drishti.get_earnings_filing", {"earnings_id": "synth-record"})
        first, second = await asyncio.gather(service.execute(request), service.execute(request))
        assert first.status == "unknown" and second.status == "blocked"
        assert service.ledger.requests["drishti"] == 1
        assert service.ledger.completed_estimated_credits == 3
    finally:
        await service.close()


async def test_connect_is_shared_across_waiters_and_reuses_fresh_metadata():
    service = ResearchService(Settings())
    entered, release = asyncio.Event(), asyncio.Event()
    calls = 0
    fresh = False

    async def connect():
        nonlocal calls, fresh
        calls += 1
        entered.set()
        await release.wait()
        fresh = True
        return {"state": "connected", "metadata_fresh": True}

    provider = service.providers["drishti"]
    provider.connect = connect
    provider.status = lambda: {
        "state": "connected" if fresh else "disconnected",
        "metadata_fresh": fresh,
    }
    try:
        first = asyncio.create_task(service.connect_drishti())
        await entered.wait()
        second = asyncio.create_task(service.connect_drishti())
        await asyncio.sleep(0)
        first.cancel()  # Closing one tab cannot cancel shared metadata work.
        with pytest.raises(asyncio.CancelledError):
            await first
        release.set()
        assert (await second)["metadata_fresh"]
        assert (await service.connect_drishti())["metadata_fresh"]
        assert calls == 1
        assert service.ledger.requests == {"bharatstock": 0, "drishti": 0}
    finally:
        await service.close()


async def test_shared_connect_failure_is_visible_and_retry_is_explicit():
    service = ResearchService(Settings())
    calls = 0

    async def fail():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.01)
        raise DomainError("metadata_failed", "Safe connection failure.")

    service.providers["drishti"].connect = fail
    try:
        outcomes = await asyncio.gather(
            service.connect_drishti(), service.connect_drishti(), return_exceptions=True
        )
        assert all(isinstance(outcome, DomainError) for outcome in outcomes)
        assert calls == 1
        assert service.providers["drishti"].status()["state"] == "synthetic"
        assert service._connection_task.done()
    finally:
        await service.close()
