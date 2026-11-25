"""Fresh numerical workflows use fictional HTTP transports, not provider/model calls."""

import asyncio
import copy
import json
from decimal import Decimal

import httpx
import pytest

from margin.analysis import company
from margin.core.company_finance import RESPONSE_LIMIT
from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.server import MarginMCP


def row(end="2026-03-31", revenue=1000000000, period="annual", **fields):
    return {
        "period_end_date": end,
        "period_type": period,
        "consolidation_type": "consolidated",
        "revenue": revenue,
        "net_profit": 150000000,
        "profit_from_continuing_operations": 150000000,
        "net_profit_attributable_to_owners": 150000000,
        "operating_profit": 180000000,
        "ebitda": 200000000,
        "cash_flow_operating": 170000000,
        "capex": 30000000,
        "current_assets": 500000000,
        "current_liabilities": 250000000,
        "inventories": 100000000,
        "cash_and_cash_equivalents": 70000000,
        "borrowings_current": 50000000,
        "borrowings_non_current": 100000000,
        "total_equity": 800000000,
        "total_assets": 1200000000,
        "total_liabilities": 400000000,
        "equity_attributable_to_owners": 800000000,
        **fields,
    }


def rows():
    return [row(), row("2025-03-31", 800000000)]


@pytest.fixture
async def fresh_service():
    service = ResearchService(Settings(bharatstock_key="fictional-secret-only"))
    observed = []

    def response(request):
        observed.append(request)
        data = rows()
        if request.url.params["period_type"] == "quarterly":
            data = [
                row(
                    end,
                    250000000,
                    "quarterly",
                    quarter=q,
                    reported_period_days=None,
                    filed_period_days=None,
                )
                for end, q in [
                    ("2026-03-31", "Q4"),
                    ("2025-12-31", "Q3"),
                    ("2025-09-30", "Q2"),
                    ("2025-06-30", "Q1"),
                ]
            ]
        return httpx.Response(200, json={"data": data})

    await service.providers["bharatstock"].client.aclose()
    service.providers["bharatstock"].client = httpx.AsyncClient(
        base_url="https://bharatstockapi.com", transport=httpx.MockTransport(response)
    )
    try:
        yield service, observed
    finally:
        await service.close()


def args(function="margins", **more):
    return {
        "function": "finance.company_" + function,
        "ticker": "SYNTHA",
        "execute": True,
        "include_details": True,
        "idempotency_key": "fresh-test-" + function,
        **more,
    }


@pytest.mark.parametrize("function", list(company.FUNCTIONS))
async def test_all_nine_fresh_workflows_use_one_page_no_buffers(fresh_service, function):
    service, observed = fresh_service
    result = await service.company_finance(**args(function.removeprefix("finance.company_")))
    assert result["status"] == "success", result
    report = result["report"]
    assert "summary" not in report and "table_markdown" not in report
    if function.endswith("_data_readiness"):
        assert report["readiness"] and not report["rows"]
    else:
        calculated = [row for row in report["rows"] if row["kind"] == "result"]
        assert calculated and all(
            row["status"] == "success" and row["value"] is not None for row in calculated
        )
        assert all(row["display"] for row in calculated)
        assert all(
            row["unit"] in {"INR_crore", "INR_per_share", "percent", "ratio", "years"}
            for row in report["rows"]
        )
    assert len(observed) == 1
    assert result["usage"] == {
        "bharatstock_http_attempts": 1,
        "drishti_http_attempts": 0,
        "estimated_drishti_credits": 0,
        "uncertain_outcome": False,
    }
    assert not service._buffers and not service.runs and not service.plans
    assert not service.financial_sources()
    assert observed[0].url.path == "/v1/stocks/SYNTHA/financials"
    assert observed[0].url.params["page"] == "1"
    assert observed[0].url.params["page_size"] == ("8" if function.endswith("_ttm") else "2")
    assert encoded_result(result) <= RESPONSE_LIMIT
    assert "fictional-secret-only" not in json.dumps(result)
    assert "payload" not in result and "receipt" not in result


def encoded_result(result):
    return len(json.dumps(result).encode())


async def test_direct_answer_preserves_same_row_and_exact_units_without_dates(fresh_service):
    service, _ = fresh_service
    output = await service.company_finance(**args())
    assert output["details"]["values"]["margin_percent"] == "15.00"
    profit, revenue = output["details"]["inputs"]
    assert profit["period_start"] is None and revenue["period_start"] is None
    assert profit["row_reference"] == revenue["row_reference"]
    assert revenue["unit"] == "INR" and revenue["value"] == "1000000000"
    assert revenue["display"] == "₹100.00 crore"
    assert output["source"]["verification"] == "unverified"
    assert output["source"]["additional_pages_fetched"] is False


async def test_default_preview_is_local_and_normalizes_defaults(fresh_service):
    service, observed = fresh_service
    result = await service.company_finance(function="finance.company_ttm", ticker="syntha")
    assert result["status"] == "preview"
    assert result["selection"]["period_type"] == "quarterly"
    assert result["selection"]["ticker"] == "SYNTHA"
    assert result["maximum_provider_requests"] == {"bharatstock": 1, "drishti": 0}
    assert not observed and not service.company_finance_workflow.requests


async def test_default_report_and_optional_details_share_one_request(fresh_service):
    service, observed = fresh_service
    default = await service.company_finance(**args(include_details=False))
    assert default["response_version"] == "margin.company_finance.v2"
    assert "details" not in default and "inputs" not in default and "values" not in default
    revenue = next(row for row in default["report"]["rows"] if row["metric"] == "revenue")
    assert revenue["unit"] == "INR_crore" and Decimal(revenue["value"]) == 100
    assert revenue["display"] == "₹100.00 crore"
    inspected = await service.company_finance(**args(include_details=True))
    assert inspected["request_id"] == default["request_id"]
    assert inspected["report"] == default["report"]
    assert inspected["details"]["inputs"][1]["unit"] == "INR"
    assert inspected["details"]["values"]["margin_percent"] == "15.00"
    assert await service.company_finance(**args(include_details=False)) == default
    assert len(observed) == 1


async def test_provider_source_locators_are_preserved_without_verification(fresh_service):
    service, _ = fresh_service
    locator = "https://example.com/fictional-financial-statement.pdf"
    service.providers["bharatstock"].client._transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"data": [row(source_url=locator)]})
    )
    result = await service.company_finance(**args())
    assert result["status"] == "success"
    assert [c["locator"] for c in result["source"]["citations"]] == [locator]
    assert all(not c["verified"] for c in result["source"]["citations"])


@pytest.mark.parametrize(
    "bad",
    [
        {"execute": True, "idempotency_key": None},
        {"execute": True, "idempotency_key": "short"},
        {"function": "finance.calculate_dcf"},
        {"ticker": "../secret"},
        {"money_unit": "INR_crore"},
        {"source": {"run_id": "old"}},
        {"period_type": "ttm"},
        {"function": "finance.company_ttm", "period_type": "annual"},
        {"function": "finance.company_cagr", "period_type": "quarterly"},
        {"idempotency_key": "fictional-secret-only"},
    ],
)
async def test_bad_inputs_do_not_fetch_or_allocate_controls(fresh_service, bad):
    service, observed = fresh_service
    with pytest.raises(DomainError):
        await service.company_finance(**(args() | bad))
    assert not observed and not service.company_finance_workflow.requests


async def test_fresh_requests_ignore_retained_sources_and_duplicate_keys_join(fresh_service):
    service, observed = fresh_service
    plan = service.plan_financial("finance.company_margins", "SYNTHA", "NSE", fetch_missing=True)
    run = await service.start_run(plan["plan_id"], "old-source-key")
    await service._tasks[run["run_id"]]
    assert service.financial_sources()
    existing_buffers = copy.deepcopy(service._buffers)
    first, second = await asyncio.gather(
        service.company_finance(**args()), service.company_finance(**args())
    )
    assert first == second and len(observed) == 2
    # Explicit defaults and waiting policy are not a different financial intent.
    third = await service.company_finance(
        **args(
            ticker="syntha",
            exchange="NSE",
            period_type="annual",
            basis="consolidated",
            wait_seconds=1,
        )
    )
    assert first == third and len(observed) == 2
    third["details"]["values"].clear()
    assert (await service.company_finance(**args()))["details"]["values"]
    assert service._buffers == existing_buffers
    await service.company_finance(**args(idempotency_key="fresh-second-key"))
    assert len(observed) == 3
    with pytest.raises(DomainError) as exc:
        await service.company_finance(**args(ticker="SYNTHB"))
    assert exc.value.code == "idempotency_conflict" and len(observed) == 3


@pytest.mark.parametrize(
    "http_status,code",
    [(401, "invalid_credentials"), (403, "forbidden_product"), (429, "rate_limit")],
)
async def test_provider_errors_are_not_retried(fresh_service, http_status, code):
    service, observed = fresh_service

    def respond(request):
        observed.append(request)
        return httpx.Response(http_status)

    service.providers["bharatstock"].client._transport = httpx.MockTransport(respond)
    first = await service.company_finance(**args())
    assert first["status"] == "failed" and first["error"]["code"] == code
    assert await service.company_finance(**args()) == first
    assert len(observed) == 1 and first["usage"]["bharatstock_http_attempts"] == 1


async def test_uncertain_provider_timeout_does_not_retry(fresh_service):
    service, observed = fresh_service

    def respond(request):
        observed.append(request)
        raise httpx.ReadTimeout("fictional-private-diagnostic")

    service.providers["bharatstock"].client._transport = httpx.MockTransport(respond)
    result = await service.company_finance(**args())
    assert result["status"] == "unknown" and result["usage"]["uncertain_outcome"]
    assert "fictional-private-diagnostic" not in json.dumps(result)
    assert await service.company_finance(**args()) == result and len(observed) == 1
    blocked = await service.company_finance(**args(idempotency_key="after-unknown-key"))
    assert blocked["status"] == "blocked" and len(observed) == 1


@pytest.mark.parametrize("data", [[], [row(consolidation_type="standalone")], [row(capex=None)]])
async def test_empty_basis_and_null_remain_incomplete_without_extra_pages(fresh_service, data):
    service, observed = fresh_service

    def respond(request):
        observed.append(request)
        return httpx.Response(200, json={"data": data})

    service.providers["bharatstock"].client._transport = httpx.MockTransport(respond)
    result = await service.company_finance(**args("cashflow_metrics"))
    assert result["status"] == "incomplete" and result["issues"]
    assert len(observed) == 1 and not result["details"]["values"]


async def test_continuing_profit_and_component_scope_holds_survive(fresh_service):
    service, _ = fresh_service
    service.providers["bharatstock"].client._transport = httpx.MockTransport(
        lambda _: httpx.Response(
            200,
            json={"data": [row(net_profit=300000000, profit_from_continuing_operations=100000000)]},
        )
    )
    margin = await service.company_finance(**args())
    assert Decimal(margin["details"]["values"]["margin_percent"]) == Decimal("10")
    assert margin["details"]["inputs"][0]["metric"] == "profit_from_continuing_operations"
    group = await service.company_finance(**args("profitability"))
    assert group["status"] == "partial"
    assert (
        group["details"]["components"]["net_profit_margin_percent"]["status"]
        == "needs_scope_review"
    )
    assert "net_profit_margin_percent" not in group["details"]["values"]


async def test_waiter_cancellation_and_pending_rejoin_do_not_duplicate(fresh_service):
    service, observed = fresh_service
    entered, release = asyncio.Event(), asyncio.Event()

    async def respond(request):
        observed.append(request)
        entered.set()
        await release.wait()
        return httpx.Response(200, json={"data": rows()})

    service.providers["bharatstock"].client._transport = httpx.MockTransport(respond)
    waiter = asyncio.create_task(service.company_finance(**args()))
    await entered.wait()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    pending = await service.company_finance(**args(wait_seconds=0))
    assert pending["status"] == "running"
    release.set()
    result = await service.company_finance(**args())
    assert result["status"] == "success" and len(observed) == 1
    assert result["request_id"] == pending["request_id"]


async def test_quota_capacity_and_closed_service_do_not_dispatch():
    service = ResearchService(Settings(bharatstock_requests=0, max_records=1))
    try:
        held = await service.company_finance(**args())
        assert held["status"] == "blocked" and held["usage"]["bharatstock_http_attempts"] == 0
        assert await service.company_finance(**args()) == held
        with pytest.raises(DomainError) as exc:
            await service.company_finance(**args(idempotency_key="new-over-capacity"))
        assert exc.value.code == "capacity"
        assert service.ledger.requests["bharatstock"] == 0
    finally:
        await service.close()
    with pytest.raises(DomainError) as exc:
        await service.company_finance(**args())
    assert exc.value.code == "unavailable"


async def test_shutdown_cancels_dispatched_work_with_uncertain_accounting(fresh_service):
    service, observed = fresh_service
    entered = asyncio.Event()

    async def respond(request):
        observed.append(request)
        entered.set()
        await asyncio.Event().wait()

    service.providers["bharatstock"].client._transport = httpx.MockTransport(respond)
    waiter = asyncio.create_task(service.company_finance(**args()))
    await entered.wait()
    await service.close()
    result = await waiter
    assert result["status"] == "unknown" and result["usage"]["uncertain_outcome"]
    assert len(observed) == 1 and not service.company_finance_workflow.requests


async def test_compact_limit_withholds_oversize_without_retry(fresh_service, monkeypatch):
    service, observed = fresh_service
    monkeypatch.setattr(
        company,
        "calculate_company",
        lambda *a: {"status": "success", "values": {"oversized": "x" * RESPONSE_LIMIT}},
    )
    result = await service.company_finance(**args())
    assert result["status"] == "failed" and result["error"]["code"] == "oversize_output"
    assert "values" not in result and encoded_result(result) < RESPONSE_LIMIT
    assert await service.company_finance(**args()) == result and len(observed) == 1


async def test_formatter_failure_is_bounded_cached_and_does_not_retain_exception(
    fresh_service, monkeypatch
):
    service, observed = fresh_service

    def broken(*_):
        raise RuntimeError("fictional-private-diagnostic")

    monkeypatch.setattr("margin.core.company_finance.company_report", broken)
    first = await service.company_finance(**args())
    assert first["status"] == "failed" and first["error"]["code"] == "reporting_error"
    assert "fictional-private-diagnostic" not in json.dumps(first)
    assert "details" not in first and "report" not in first
    assert await service.company_finance(**args()) == first and len(observed) == 1
    assert all(
        record["task"].exception() is None
        for record in service.company_finance_workflow.requests.values()
    )


async def test_mcp_exact_schema_execution_and_private_recording(fresh_service, tmp_path):
    service, observed = fresh_service
    recorder = ToolRecorder(directory=tmp_path)
    try:
        adapter = MarginMCP(service, recorder)
        bad = await adapter.call(
            "margin_company_finance",
            {"function": "finance.company_margins", "ticker": "SYNTHA", "execute": True},
        )
        assert bad.is_error and not observed
        result = await adapter.call(
            "margin_company_finance",
            args() | {"why": "Compute the company's margin from one fresh financials response."},
        )
        assert not result.is_error
        assert result.structured_content["data"]["details"]["values"]["margin_percent"] == "15.00"
        preview = await adapter.call(
            "margin_company_finance", {"function": "finance.company_margins", "ticker": "SYNTHA"}
        )
        assert preview.structured_content["data"]["status"] == "preview"
        assert len(observed) == 1
        text = recorder.path.read_text()
        assert "fictional-secret-only" not in text and '"payload"' not in text
        assert "Compute the company's margin" in text
    finally:
        recorder.close()
