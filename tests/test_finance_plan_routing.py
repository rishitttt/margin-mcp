"""Generic plan identity/TTL errors must not cause convenience-preview refetches."""

import time

import pytest

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.server import MarginMCP


@pytest.fixture
async def owner():
    service = ResearchService(Settings())
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def test_unissued_plan_is_unavailable_not_expired_and_dispatches_nothing(owner):
    before = owner.service.ledger.snapshot()
    result = await owner.call(
        "margin_run",
        {
            "session_id": owner.session_id,
            "plan_id": "unissued-plan-id",
            "idempotency_key": "plan-routing-test",
        },
    )
    assert result.is_error
    error = result.structured_content["error"]
    assert error["code"] == "plan_unavailable" and "expired" not in error["message"]
    assert "creates NO generic plan_id" in error["recovery_guidance"]
    assert not error["uncertain_outcome"]
    assert not owner.service.plans and not owner.service.runs
    assert owner.service.ledger.snapshot() == before


async def preview(owner):
    result = await owner.call(
        "margin_preview",
        {
            "operations": [
                {
                    "operation": "bharatstock.get_stock_quote",
                    "arguments": {"ticker": "SYNTHA", "exchange": "NSE"},
                }
            ]
        },
    )
    assert not result.is_error
    return result.structured_content["data"]


async def test_real_expired_generic_plan_keeps_expiry_code_without_fetch(owner):
    plan = await preview(owner)
    owner.service.plans[plan["plan_id"]] = (time.monotonic() - 601, plan)
    before = owner.service.ledger.snapshot()
    result = await owner.call(
        "margin_run",
        {
            "session_id": owner.session_id,
            "plan_id": plan["plan_id"],
            "idempotency_key": "expired-routing-test",
        },
    )
    assert result.is_error and result.structured_content["error"]["code"] == "plan_expired"
    assert not owner.service.runs and owner.service.ledger.snapshot() == before


async def test_valid_generic_submission_and_same_key_replay_survive_diagnostic_change(owner):
    plan = await preview(owner)
    values = {
        "session_id": owner.session_id,
        "plan_id": plan["plan_id"],
        "idempotency_key": "valid-routing-test",
    }
    result = await owner.call("margin_run", values)
    assert not result.is_error
    run = result.structured_content["data"]
    finished = await owner.wait(run["run_id"], 2)
    assert finished["status"] == "completed"
    before = owner.service.ledger.snapshot()
    owner.service.plans[plan["plan_id"]] = (time.monotonic() - 601, plan)
    replay = await owner.call("margin_run", values)
    assert not replay.is_error and replay.structured_content["data"]["run_id"] == run["run_id"]
    assert owner.service.ledger.snapshot() == before
