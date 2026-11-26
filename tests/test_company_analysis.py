"""Company dependency execution: fictional transport data, real service/run contracts."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.interfaces.workbench.app import create_app


async def finish(service, plan, key):
    run = await service.start_run(plan["plan_id"], key)
    await service._tasks[run["run_id"]]
    return service.get_run(run["run_id"])


@pytest.mark.asyncio
async def test_company_function_fetches_once_then_reuses_for_different_calculations():
    service = ResearchService(Settings(max_payload_runs=2))
    try:
        plan = service.plan_financial(
            "finance.company_margins", "SYNTHA", "NSE", money_unit="INR", fetch_missing=True
        )
        assert service.ledger.requests["bharatstock"] == 0
        assert plan["data_operations"] == {"bharatstock": 1, "drishti": 0}
        run = await finish(service, plan, "company-first")
        result = service.get_result(run["run_id"], run["operations"][-1]["operation_id"])
        assert result["status"] == "success"
        assert result["payload_kind"] == "analysis"
        assert Decimal(result["payload"]["values"]["margin_percent"]) > 0
        assert result["receipt"]["http_attempts"] == 0
        assert service.ledger.requests["bharatstock"] == 1
        duplicate = await service.start_run(plan["plan_id"], "company-first")
        assert duplicate["run_id"] == run["run_id"]
        for function in ("finance.company_growth", "finance.company_cagr"):
            reused = service.plan_financial(function, "SYNTHA", "NSE", money_unit="INR")
            assert len(reused["operations"]) == 1
            assert reused["data_operations"]["bharatstock"] == 0
            r = await finish(service, reused, function.replace(".", "-"))
            assert (
                service.get_result(r["run_id"], r["operations"][0]["operation_id"])["status"]
                == "success"
            )
        # Repeated standalone calculations must evict derived cards first, not
        # the financial data a subsequent company function could reuse.
        for index in range(5):
            local = service.create_plan(
                [
                    {
                        "operation": "finance.calculate_fcff",
                        "arguments": {
                            "ebit": "100",
                            "tax_rate": "0.25",
                            "depreciation": "10",
                            "capex": "20",
                            "change_in_working_capital": "5",
                            "amount_unit": "INR",
                        },
                    }
                ]
            )
            await finish(service, local, f"repeat-local-{index}")
        final = service.plan_financial("finance.company_margins", "SYNTHA", "NSE", money_unit="INR")
        assert final["data_operations"]["bharatstock"] == 0
        assert service.ledger.requests["bharatstock"] == 1
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_missing_context_expired_sources_and_wrong_company_never_silently_refetch():
    service = ResearchService(Settings())
    try:
        with pytest.raises(DomainError, match="No matching retained"):
            service.plan_financial("finance.company_margins", "SYNTHA", "NSE")
        plan = service.plan_financial(
            "finance.company_margins", "SYNTHA", "NSE", money_unit=None, fetch_missing=True
        )
        run = await finish(service, plan, "unknown-unit")
        output = service.get_result(run["run_id"], run["operations"][-1]["operation_id"])
        assert output["status"] == "incomplete"
        assert "Unknown unit." in output["payload"]["issues"]
        source = service.financial_sources()[0]
        ref = {k: source[k] for k in ("run_id", "operation_id")}
        with pytest.raises(DomainError, match="does not match"):
            service.plan_financial(
                "finance.company_growth", "SYNTHB", "BSE", source=ref, fetch_missing=True
            )
        planned = service.plan_financial(
            "finance.company_growth", "SYNTHA", "NSE", money_unit="INR", source=ref
        )
        service._buffers.clear()
        expired = await finish(service, planned, "expired-source")
        error = service.get_result(expired["run_id"], expired["operations"][0]["operation_id"])
        assert error["error"]["code"] == "result_unavailable"
        assert service.ledger.requests["bharatstock"] == 1
    finally:
        await service.close()


def test_financial_http_plans_and_local_functions_return_standard_result_cards():
    with TestClient(create_app(Settings()), base_url="http://127.0.0.1") as client:
        headers = {"X-Margin-Action": client.get("/api/status").json()["action_nonce"]}
        assert client.get("/api/analysis/sources").json() == {"sources": []}
        bad = client.post(
            "/api/analysis/plans",
            json={
                "function": "finance.company_ttm",
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "period_type": "annual",
                "fetch_missing": True,
            },
            headers=headers,
        )
        assert bad.status_code == 400
        assert len(client.get("/api/analysis/company-functions").json()["functions"]) == 9
        ttm = client.post(
            "/api/analysis/plans",
            json={
                "function": "finance.company_ttm",
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "fetch_missing": True,
            },
            headers=headers,
        )
        assert ttm.status_code == 200
        assert ttm.json()["operations"][0]["arguments"]["period_type"] == "quarterly"
        # An ordinary local FCFF function also uses preview/run/result retention.
        plan = client.post(
            "/api/plans",
            headers=headers,
            json={
                "operations": [
                    {
                        "operation": "finance.calculate_fcff",
                        "arguments": {
                            "ebit": "100",
                            "tax_rate": "0.25",
                            "depreciation": "10",
                            "capex": "20",
                            "change_in_working_capital": "5",
                            "amount_unit": "INR",
                        },
                    }
                ]
            },
        ).json()
        assert sum(plan["data_operations"].values()) == 0
        response = client.post(
            "/api/runs",
            headers=headers,
            json={"plan_id": plan["plan_id"], "idempotency_key": "local-fcff-test"},
        )
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        # TestClient loop executes background work between requests.
        for _ in range(50):
            run = client.get(f"/api/runs/{run_id}").json()
            if run["status"] not in {"queued", "running"}:
                break
        result = client.get(
            f"/api/runs/{run_id}/operations/{run['operations'][0]['operation_id']}"
        ).json()
        assert result["payload"]["values"]["fcff"] == "60.00"
        assert result["provider"] == "margin"
        assert client.get("/api/status").json()["ledger"]["http_attempts"] == {
            "bharatstock": 0,
            "drishti": 0,
        }


@pytest.mark.asyncio
async def test_history_keeps_listing_context_after_eviction_without_fetching_or_exposing_payloads():
    service = ResearchService(Settings())
    try:
        plan = service.plan_financial(
            "finance.company_margins", "SYNTHA", "NSE", money_unit="INR", fetch_missing=True
        )
        run = await finish(service, plan, "history-scope")
        before = service.ledger.snapshot()
        service._buffers.clear()
        history = service.recent_runs()
        assert history[0]["run_id"] == run["run_id"]
        assert history[0]["listing"] == {"symbol": "SYNTHA", "exchange": "NSE"}
        assert "payload" not in history[0] and "arguments" not in history[0]
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_all_five_company_wrappers_use_one_bounded_source_each_without_extra_fetch():
    """Fictional complete periods exercise success paths, not real-company truth."""
    import httpx

    from margin.policy.ledger import Ledger
    from margin.providers.bharatstock import BharatStockAdapter

    def handler(request):
        annual = request.url.params.get("period_type") == "annual"
        rows = [
            {
                "period_type": "annual" if annual else "quarterly",
                "period_start_date": start,
                "period_end_date": end,
                "consolidation_type": "consolidated",
                "revenue": revenue,
                "net_profit": revenue / 10,
                "cash_flow_operating": 60,
                "capex": 20,
            }
            for start, end, revenue in (
                [("2025-04-01", "2026-03-31", 120), ("2024-04-01", "2025-03-31", 100)]
                if annual
                else [
                    ("2026-07-01", "2026-09-30", 40),
                    ("2026-04-01", "2026-06-30", 30),
                    ("2026-01-01", "2026-03-31", 20),
                    ("2025-10-01", "2025-12-31", 10),
                ]
            )
        ]
        return httpx.Response(200, json={"data": rows})

    ledger = Ledger({"bharatstock": 2, "drishti": 0}, 0, paced=False)
    adapter = BharatStockAdapter(ledger, "fictional", transport=httpx.MockTransport(handler))
    service = ResearchService(Settings(), bharatstock=adapter)
    expected = {
        "finance.company_margins": ("margin_percent", "10"),
        "finance.company_cashflow_metrics": ("cfo_minus_capex", "40"),
        "finance.company_growth": ("percentage_change", "20"),
        "finance.company_cagr": ("cagr_percent", None),
        "finance.company_ttm": ("total", "100"),
    }
    try:
        for index, (function, (field, value)) in enumerate(expected.items()):
            plan = service.plan_financial(
                function,
                "SYNTHA",
                "NSE",
                money_unit="INR",
                period_type="quarterly" if function.endswith("ttm") else "annual",
                fetch_missing=True,
            )
            run = await finish(service, plan, f"all-wrappers-{index}")
            result = service.get_result(run["run_id"], run["operations"][-1]["operation_id"])
            assert result["status"] == "success", result
            if value is not None:
                assert Decimal(result["payload"]["values"][field]) == Decimal(value)
        assert ledger.requests["bharatstock"] == 2
    finally:
        await service.close()
