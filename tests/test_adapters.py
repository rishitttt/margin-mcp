import json
from contextlib import asynccontextmanager

import httpx
import httpx2
import pytest
from mcp import types
from mcp.server import Server

from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest
from margin.core.registry import DRISHTI, NATIVE, Registry
from margin.policy.ledger import Ledger
from margin.providers.bharatstock import BharatStockAdapter
from margin.providers.drishti import DrishtiAdapter
from margin.providers.synthetic import drishti_payload


async def test_bharatstock_exact_route_headers_query_and_one_page():
    seen = []

    async def handler(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "data": [{"revenue": 123, "cash_flow": None}],
                "pagination": {"page": 1, "total_pages": 8},
            },
        )

    ledger = Ledger({"bharatstock": 3, "drishti": 30}, 20, paced=False)
    adapter = BharatStockAdapter(ledger, "fake-header-key", transport=httpx.MockTransport(handler))
    try:
        request = OperationRequest(
            "bharatstock.get_financials",
            {
                "ticker": "RELIANCE",
                "exchange": "NSE",
                "period_type": "quarterly",
                "page": 1,
                "page_size": 2,
            },
        )
        spec = Registry(Settings()).validate(request)
        result = await adapter.execute(spec, request.arguments)
        assert len(seen) == 1
        assert seen[0].url.path == "/v1/stocks/RELIANCE/financials"
        assert seen[0].url.params["period_type"] == "quarterly"
        assert seen[0].headers["X-API-Key"] == "fake-header-key"
        assert not seen[0].headers.get("authorization")
        assert result.payload["data"][0]["cash_flow"] is None
        assert result.payload["pagination"]["total_pages"] == 8
        assert ledger.requests["bharatstock"] == 1
    finally:
        await adapter.close()


@pytest.mark.parametrize(
    "status,expected",
    [
        (302, "upstream_error"),
        (401, "invalid_credentials"),
        (403, "forbidden_product"),
        (429, "rate_limit"),
    ],
)
async def test_rest_errors_do_not_follow_or_retry_or_echo_bodies(status, expected):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(
            status,
            headers={"Location": "https://attacker.invalid/"},
            text="sensitive response body",
        )

    ledger = Ledger({"bharatstock": 5, "drishti": 30}, 20, paced=False)
    adapter = BharatStockAdapter(ledger, "fake", transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(DomainError) as exc:
            await adapter.execute(
                Registry(Settings()).spec("bharatstock.get_stock_quote"),
                {"ticker": "RELIANCE", "exchange": "NSE"},
            )
        assert exc.value.code == expected and "sensitive" not in str(exc.value)
        assert len(seen) == ledger.requests["bharatstock"] == 1
    finally:
        await adapter.close()


async def test_rest_stream_is_bounded_before_json_decode():
    adapter = BharatStockAdapter(
        Ledger({"bharatstock": 3, "drishti": 30}, 20, paced=False),
        "fake",
        transport=httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * 1024)),
        max_bytes=100,
    )
    try:
        with pytest.raises(DomainError, match="byte bound"):
            await adapter.execute(
                Registry(Settings()).spec("bharatstock.get_stock_quote"),
                {"ticker": "RELIANCE", "exchange": "NSE"},
            )
    finally:
        await adapter.close()


@asynccontextmanager
async def fake_drishti(*, changed=None):
    calls = []

    async def list_tools(ctx, params):
        return types.ListToolsResult(
            tools=[
                types.Tool(
                    name=name,
                    input_schema=entry["inputSchema"],
                    output_schema=entry["outputSchema"],
                )
                for name, entry in NATIVE.items()
            ]
        )

    async def call_tool(ctx, params):
        calls.append(params.name)
        if params.name == "describe_tools":
            tools = []
            for name in params.arguments["names"]:
                schema = (
                    DRISHTI[name]["inputSchema"]
                    if name != changed
                    else {"type": "object", "required": ["a_new_field"]}
                )
                tools.append({"name": name, "input_schema": schema})
            data = {"tools": tools}
        elif params.name == "execute_tool":
            data = drishti_payload(params.arguments["name"], params.arguments["arguments"])
        else:
            data = {"message": "fixture routing metadata"}
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(data))], structured_content=data
        )

    server = Server("synthetic-drishti-upstream", on_list_tools=list_tools, on_call_tool=call_tool)
    app = server.streamable_http_app(json_response=True, stateless_http=True)
    async with app.router.lifespan_context(app):
        yield httpx2.ASGITransport(app=app), calls


async def test_real_sdk_session_against_synthetic_mcp_not_provider():
    settings = Settings(mode="live", drishti_key="fake-sdk-key")
    ledger = Ledger({"bharatstock": 20, "drishti": 30}, 20, paced=False)
    async with fake_drishti() as (transport, calls):
        adapter = DrishtiAdapter(
            ledger, settings, transport=transport, endpoint="http://127.0.0.1:8769/mcp"
        )
        try:
            status = await adapter.connect()
            assert status["state"] == "connected" and len(status["verified_operations"]) == 7
            assert ledger.requests["drishti"] >= 4  # SDK lifecycle + catalog + descriptions.
            request = OperationRequest(
                "drishti.get_earnings_filing", {"earnings_id": "synthetic-record"}
            )
            spec = Registry(settings).validate(request)
            result = await adapter.execute(spec, request.arguments)
            assert not result.is_error
            assert result.payload["structuredContent"]["earnings_id"] == "synthetic-record"
            assert calls.count("execute_tool") == 1
            assert "describe_tools" in calls
        finally:
            await adapter.close()
        assert adapter._task.done()


async def test_schema_drift_quarantines_only_changed_nested_operation():
    settings = Settings(mode="live", drishti_key="fake-sdk-key")
    ledger = Ledger({"bharatstock": 20, "drishti": 30}, 20, paced=False)
    async with fake_drishti(changed="get_news") as (transport, calls):
        adapter = DrishtiAdapter(
            ledger, settings, transport=transport, endpoint="http://127.0.0.1:8769/mcp"
        )
        try:
            status = await adapter.connect()
            assert status["schema_changed_operations"] == ["get_news"]
            adapter.assert_ready(Registry(settings).spec("drishti.get_earnings_filing"))
            with pytest.raises(DomainError, match="not approved"):
                adapter.assert_ready(Registry(settings).spec("drishti.get_news"))
            adapter.refreshed = 0
            with pytest.raises(DomainError, match="Refresh"):
                adapter.assert_ready(Registry(settings).spec("drishti.get_earnings_filing"))
            assert "execute_tool" not in calls
        finally:
            await adapter.close()
