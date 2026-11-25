"""MCP contracts and real stdio transport over fictional software data, no live APIs."""

import asyncio
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import MCPError

from margin.analysis.service import SPECS
from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.server import MarginMCP, create_server
from margin.interfaces.mcp.tools import CONTRACT, DIRECT_FUNCTIONS, VERSION, definitions

ROOT = Path(__file__).parents[1]


@pytest.fixture
async def adapter():
    service = ResearchService(Settings())
    value = MarginMCP(service)
    try:
        yield value
    finally:
        await service.close()


async def invoke(adapter, name, args=None, error=False):
    response = await adapter.call(name, args)
    assert response.is_error is error, response.content
    body = response.structured_content
    assert json.loads(response.content[0].text) == body
    assert body["contract_version"] == CONTRACT
    if name in adapter.tools:
        Draft202012Validator(adapter.tools[name].output_schema).validate(body)
    return body


def fcff():
    return {
        "function": "finance.calculate_fcff",
        "arguments": {
            "ebit": "100",
            "tax_rate": "0.25",
            "depreciation": "10",
            "capex": "20",
            "change_in_working_capital": "5",
            "amount_unit": "INR",
        },
    }


def test_static_catalog_has_25_tools_and_accurate_annotations():
    tools = definitions()
    assert len(tools) == 25
    for tool in tools.values():
        Draft202012Validator.check_schema(tool.input_schema)
        Draft202012Validator.check_schema(tool.output_schema)
        assert tool.input_schema["additionalProperties"] is False
        assert tool.annotations.destructive_hint is False
    assert tools["margin_calculate"].annotations.read_only_hint
    assert not tools["margin_run"].annotations.read_only_hint
    assert tools["margin_run"].annotations.open_world_hint
    assert tools["margin_run"].annotations.idempotent_hint
    assert not tools["margin_review"].annotations.open_world_hint


async def test_catalog_exposes_every_function_without_startup_or_listing_fetch(adapter):
    before = adapter.service.ledger.snapshot()
    status = await invoke(adapter, "margin_status")
    assert status["mode"] == "synthetic"
    catalog = (await invoke(adapter, "margin_catalog"))["data"]["groups"]
    assert [len(catalog[k]) for k in ["retrieval", "calculations", "company", "review"]] == [
        13,
        15,
        9,
        10,
    ]
    assert all(
        "schema" not in entry and "planning_schema" not in entry
        for rows in catalog.values()
        for entry in rows
    )
    exact = (
        await invoke(
            adapter,
            "margin_catalog",
            {"group": "calculations", "name": "calculate_dcf", "include_schemas": True},
        )
    )["data"]["groups"]["calculations"]
    assert len(exact) == 1 and "forecast_fcff" in exact[0]["schema"]["properties"]
    empty = await invoke(adapter, "margin_catalog", {"name": "not-a-function"}, error=True)
    assert empty["error"]["code"] == "unknown_function"
    assert adapter.service.ledger.snapshot() == before


@pytest.mark.parametrize(
    "name,args",
    [
        ("margin_status", {"unexpected": True}),
        ("margin_status", {"why": "\n"}),
        ("margin_status", {"why": " "}),
        ("margin_status", {"why": "x" * 281}),
        ("margin_status", []),
        ("margin_preview", {"operations": []}),
        (
            "margin_preview",
            {"operations": [{"operation": "drishti.execute_tool", "arguments": {}}]},
        ),
        ("margin_calculate", {"function": "finance.fetch_anything", "arguments": {}}),
        ("margin_run_status", {"run_id": "../file"}),
        ("margin_run_status", {"run_id": "example", "wait_seconds": 31}),
        (
            "margin_calculate",
            {"function": "finance.calculate_fcff", "arguments": {"ebit": float("nan")}},
        ),
        (
            "margin_calculate",
            {"function": "finance.calculate_fcff", "arguments": {"x": "x" * 65536}},
        ),
    ],
)
async def test_invalid_inputs_cannot_dispatch(adapter, name, args):
    before = adapter.service.ledger.snapshot()
    await invoke(adapter, name, args, error=True)
    assert adapter.service.ledger.snapshot() == before
    assert not adapter.service.runs


@pytest.mark.parametrize(
    "name", ["finance.calculate_margins", "finance_calculate_margins", "not_a_tool"]
)
async def test_catalog_identifiers_are_not_mcp_tools_and_unknown_is_protocol_error(adapter, name):
    before = adapter.service.ledger.snapshot()
    with pytest.raises(MCPError) as failure:
        await adapter.call(name, {})
    assert failure.value.error.code == -32602
    assert "do not rename" in failure.value.error.message
    if name == "finance.calculate_margins":
        assert "margin_calculate" in failure.value.error.message
    assert adapter.service.ledger.snapshot() == before and not adapter.service.runs


async def test_every_catalog_entry_has_an_explicit_callable_mcp_route(adapter):
    catalog = (await invoke(adapter, "margin_catalog"))["data"]
    assert "not callable MCP tools" in catalog["routing_notice"]
    for group, rows in catalog["groups"].items():
        for row in rows:
            route = row["mcp_execution"]
            assert route["tool"] in adapter.tools
            name = row.get("function") or row.get("operation")
            assert name in route["bind"].values() or DIRECT_FUNCTIONS.get(route["tool"]) == name
            if group in {"calculations", "review"}:
                assert route["inputs_at"] in {"arguments", "top_level"} and "then" not in route
            elif group == "company":
                assert route["inputs_at"] == "top_level" and route["then"] == "margin_run"
            else:
                assert route["inputs_at"] == "operations[0].arguments"
                assert route["then"] == "margin_run"


async def test_declared_margin_example_routes_from_catalog_without_provider_calls():
    # Explicit fictional context for a software test, never issuer/provider ground truth.
    service = ResearchService(
        Settings(mode="live", bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    adapter = MarginMCP(service)
    before = service.ledger.snapshot()
    try:
        entry = (
            await invoke(
                adapter,
                "margin_catalog",
                {
                    "group": "calculations",
                    "name": "finance.calculate_margins",
                    "include_schemas": True,
                },
            )
        )["data"]["groups"]["calculations"][0]
        common = {
            "issuer": "HYPOTHETICAL_USER_EXAMPLE",
            "unit": "INR",
            "period_type": "annual",
            "period_start": "2025-04-01",
            "period_end": "2026-03-31",
            "basis": "standalone",
            "source": {"kind": "user_declared_hypothetical"},
        }
        inputs = {
            "profit": common
            | {"metric": "net_profit", "definition": "User-declared net profit", "value": 150},
            "revenue": common
            | {"metric": "revenue", "definition": "User-declared revenue", "value": 1000},
        }
        Draft202012Validator(entry["schema"]).validate(inputs)
        route = entry["mcp_execution"]
        value = await invoke(
            adapter,
            route["tool"],
            inputs | {"why": "Calculate a declared hypothetical margin without provider access."},
        )
        assert value["data"]["status"] == "success"
        assert value["data"]["values"]["margin_percent"] == "15.00"
        # Preserve the guard: missing start/context must not turn into a calculated fact.
        for item in inputs.values():
            item.pop("period_start")
        partial = await invoke(adapter, route["tool"], inputs)
        assert partial["data"]["status"] == "incomplete"
        assert "margin_percent" not in partial["data"]["values"]
        assert any("period_start" in issue for issue in partial["data"]["issues"])
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


@pytest.mark.parametrize("profit,revenue", [(150, 1000), ("150", "1000")])
async def test_reported_extra_flag_error_guides_recovery_without_changing_context(
    adapter, profit, revenue
):
    # Reproduces the public input shape described by the user; all values are hypothetical.
    common = {
        "issuer": "EXAMPLE_ONLY",
        "unit": "INR",
        "period_type": "annual",
        "period_end": "2026-03-31",
        "basis": "standalone",
    }
    inputs = {
        "profit": common
        | {"metric": "net_profit", "definition": "Hypothetical net profit", "value": profit},
        "revenue": common
        | {"metric": "revenue", "definition": "Hypothetical revenue", "value": revenue},
        "hypothetical": True,
    }
    before = adapter.service.ledger.snapshot()
    call = {"function": "finance.calculate_margins", "arguments": inputs}
    failed = await invoke(adapter, "margin_calculate", call, error=True)
    assert "unexpected fields; allowed fields: profit, revenue" in failed["error"]["message"]
    inputs.pop("hypothetical")
    partial = await invoke(adapter, "margin_calculate", call)
    assert partial["data"]["status"] == "incomplete"
    assert any("period_start" in issue for issue in partial["data"]["issues"])
    for item in inputs.values():
        item["period_start"] = "2025-04-01"
    result = await invoke(adapter, "margin_calculate", call)
    assert result["data"]["status"] == "success"
    assert result["data"]["values"]["margin_percent"] == "15.00"
    assert adapter.service.ledger.snapshot() == before


async def test_direct_typed_margins_validate_without_wrapper_and_preserve_period_guards(adapter):
    common = {
        "issuer": "EXAMPLE_ONLY",
        "unit": "INR",
        "period_type": "annual",
        "period_start": "2025-04-01",
        "period_end": "2026-03-31",
        "basis": "standalone",
    }
    inputs = {
        "profit": common
        | {"metric": "net_profit", "definition": "Hypothetical net profit", "value": 150},
        "revenue": common
        | {"metric": "revenue", "definition": "Hypothetical revenue", "value": 1000},
    }
    before = adapter.service.ledger.snapshot()
    answer = await invoke(adapter, "margin_calculate_margins", inputs)
    assert answer["data"]["values"]["margin_percent"] == "15.00"
    extra = await invoke(
        adapter, "margin_calculate_margins", inputs | {"hypothetical": True}, error=True
    )
    assert "allowed fields: profit, revenue, why" in extra["error"]["message"]
    inputs["profit"]["period_type"] = "quarterly"
    inputs["profit"]["period_start"] = "2026-01-01"
    held = await invoke(adapter, "margin_calculate_margins", inputs)
    assert held["data"]["status"] == "incomplete" and held["data"]["values"] == {}
    assert adapter.service.ledger.snapshot() == before
    for name, function in DIRECT_FUNCTIONS.items():
        schema = adapter.tools[name].input_schema
        assert set(schema["properties"]) == set(SPECS[function][1]["properties"]) | {"why"}
        assert "arguments" not in schema["properties"] and "function" not in schema["properties"]


async def test_direct_conversion_preserves_exact_value_and_rejects_eps_conversion(adapter):
    fact = {
        "issuer": "EXAMPLE_ONLY",
        "metric": "revenue",
        "definition": "Hypothetical revenue",
        "value": "12345678900",
        "unit": "INR",
        "period_type": "annual",
        "period_end": "2026-03-31",
        "basis": "standalone",
    }
    answer = await invoke(
        adapter, "margin_convert_units", {"value": fact, "target_unit": "INR_crore"}
    )
    assert answer["data"]["fact"]["value"] == "1234.56789"
    assert fact["unit"] == "INR"
    fact.update(metric="eps", unit="INR_per_share")
    held = await invoke(
        adapter, "margin_convert_units", {"value": fact, "target_unit": "INR_crore"}, error=True
    )
    assert held["error"]["code"] == "incompatible_units"


async def test_company_preview_run_reuse_results_and_facts(adapter):
    preview = await invoke(
        adapter,
        "margin_company_preview",
        {
            "function": "finance.company_data_readiness",
            "ticker": "SYNTHA",
            "exchange": "NSE",
            "money_unit": "auto",
            "fetch_missing": True,
        },
    )
    assert adapter.service.ledger.requests["bharatstock"] == 0
    assert preview["data"]["data_operations"] == {"bharatstock": 1, "drishti": 0}
    args = {
        "session_id": preview["session_id"],
        "plan_id": preview["data"]["plan_id"],
        "idempotency_key": "mcp-company-once",
        "wait_seconds": 2,
    }
    first = (await invoke(adapter, "margin_run", args))["data"]
    duplicate = (await invoke(adapter, "margin_run", args))["data"]
    assert duplicate["run_id"] == first["run_id"]
    assert adapter.service.ledger.requests["bharatstock"] == 1
    operation = first["operations"][-1]["operation_id"]
    output = (
        await invoke(
            adapter, "margin_result", {"run_id": first["run_id"], "operation_id": operation}
        )
    )["data"]
    assert output["payload"]["status"] == "success"
    assert output["payload"]["values"]["valuation_readiness"]["status"] == "needs_explicit_inputs"
    source = (await invoke(adapter, "margin_sources"))["data"]["sources"][0]
    ref = {k: source[k] for k in ["run_id", "operation_id"]}
    facts = (await invoke(adapter, "margin_facts", ref))["data"]["facts"]
    assert all(f["unit_origin"] == "provider_documentation" for f in facts)
    unknown = (await invoke(adapter, "margin_facts", ref | {"money_unit": None}))["data"]["facts"]
    assert all(f["unit"] is None for f in unknown)
    reuse = (
        await invoke(
            adapter,
            "margin_company_preview",
            {"function": "finance.company_margins", "ticker": "SYNTHA", "exchange": "NSE"},
        )
    )["data"]
    assert reuse["data_operations"]["bharatstock"] == 0
    adapter.service._buffers.clear()  # Simulate TTL eviction; adapter only uses public accessors.
    gone = await invoke(adapter, "margin_result", ref, error=True)
    assert gone["error"]["code"] == "result_unavailable"
    assert adapter.service.ledger.requests["bharatstock"] == 1


async def test_local_functions_and_incomplete_outcomes_are_not_transport_errors(adapter):
    output = await invoke(
        adapter,
        "margin_calculate",
        fcff() | {"why": "Calculate explicit test inputs without fetching."},
    )
    assert output["data"]["values"]["fcff"] == "60.00"
    assert output["decision_summary"].startswith("Calculate explicit")
    bad = fcff()
    bad["arguments"]["capex"] = "-20"
    await invoke(adapter, "margin_calculate", bad, error=True)
    fact = {
        "issuer": "NSE:EXAMPLE",
        "metric": "revenue",
        "definition": "Fictional revenue",
        "value": None,
        "unit": "INR",
        "period_type": "annual",
        "period_end": "2026-03-31",
        "basis": "consolidated",
    }
    incomplete = await invoke(
        adapter,
        "margin_calculate",
        {
            "function": "facts.convert_units",
            "arguments": {"value": fact, "target_unit": "INR_crore"},
        },
    )
    assert incomplete["data"]["status"] == "incomplete"
    assert not any(adapter.service.ledger.requests.values())


async def test_live_process_session_guard_blocks_run_and_connection_before_network():
    service = ResearchService(
        Settings(
            mode="live",
            bharatstock_key="fictional-secret-key",
            drishti_key="another-fictional-key",
            bharatstock_requests=0,
            drishti_requests=0,
            drishti_credits=0,
        )
    )
    adapter = MarginMCP(service)
    try:
        before = service.ledger.snapshot()
        for name, args in [
            (
                "margin_run",
                {
                    "session_id": "old-session",
                    "plan_id": "old-plan",
                    "idempotency_key": "old-key-123",
                },
            ),
            ("margin_connect_drishti", {"session_id": "old-session"}),
        ]:
            body = await invoke(adapter, name, args, error=True)
            assert body["error"]["code"] == "session_changed"
        secret = await invoke(
            adapter, "margin_status", {"why": "Inspect fictional-secret-key"}, error=True
        )
        assert "fictional-secret-key" not in json.dumps(secret)
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


async def test_explicit_cancellation_and_cancelled_waiter_preserve_run_identity():
    service = ResearchService(Settings(synthetic_delay=0.3))
    adapter = MarginMCP(service)
    started = asyncio.Event()

    async def handler(request):
        started.set()
        await asyncio.Event().wait()

    await service.providers["bharatstock"].client.aclose()
    service.providers["bharatstock"].client = httpx.AsyncClient(
        base_url="https://bharatstockapi.com", transport=httpx.MockTransport(handler)
    )
    try:
        plan = (
            await invoke(
                adapter,
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
        )["data"]
        args = {
            "session_id": adapter.session_id,
            "plan_id": plan["plan_id"],
            "idempotency_key": "cancelled-waiter-key",
        }
        run = (await invoke(adapter, "margin_run", args))["data"]
        await asyncio.wait_for(started.wait(), 1)
        waiter = asyncio.create_task(
            adapter.call("margin_run_status", {"run_id": run["run_id"], "wait_seconds": 5})
        )
        await asyncio.sleep(0.01)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        duplicate = (await invoke(adapter, "margin_run", args))["data"]
        assert duplicate["run_id"] == run["run_id"]
        cancelled = (await invoke(adapter, "margin_cancel", {"run_id": run["run_id"]}))["data"]
        assert cancelled["status"] == "cancelled"
        assert service.ledger.requests["bharatstock"] <= 1
    finally:
        await service.close()


async def test_review_roundtrip_and_retained_news_import_use_shared_store(adapter):
    before = adapter.service.ledger.snapshot()
    src = {
        "issuer": "NSE:SYNTHA",
        "title": "Fictional document",
        "url": "https://example.invalid/report",
        "kind": "original_document",
        "date": "2026-11-01",
        "date_kind": "published",
        "passages": [{"passage_id": "P1", "text": "Demand improved.", "locator": "page 1"}],
    }
    registered = (
        await invoke(
            adapter,
            "margin_review",
            {"function": "evidence.register_sources", "arguments": {"sources": [src]}},
        )
    )["data"]
    sid = registered["sources"][0]["source_id"]
    packet = (
        await invoke(
            adapter,
            "margin_review",
            {
                "function": "evidence.prepare_verification",
                "arguments": {
                    "claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}]
                },
            },
        )
    )["data"]
    ref = {k: packet[k] for k in ["packet_id", "packet_hash"]}
    rendered = (
        await invoke(
            adapter, "margin_review", {"function": "evidence.render_citations", "arguments": ref}
        )
    )["data"]
    assert rendered["citations"][0]["semantic_review"] == "not_reviewed"
    assert adapter.service.ledger.snapshot() == before
    await invoke(adapter, "margin_connect_drishti", {"session_id": adapter.session_id})
    plan = (
        await invoke(
            adapter,
            "margin_preview",
            {
                "operations": [
                    {
                        "operation": "drishti.get_news",
                        "arguments": {
                            "query": {
                                "symbols": ["SYNTHA"],
                                "lookback_days": 7,
                                "page": 1,
                                "limit": 1,
                            }
                        },
                    }
                ]
            },
        )
    )["data"]
    run = (
        await invoke(
            adapter,
            "margin_run",
            {
                "session_id": adapter.session_id,
                "plan_id": plan["plan_id"],
                "idempotency_key": "mcp-news-review",
                "wait_seconds": 2,
            },
        )
    )["data"]
    used = adapter.service.ledger.snapshot()
    imported = (
        await invoke(
            adapter,
            "margin_review_sources",
            {
                "run_id": run["run_id"],
                "operation_id": run["operations"][0]["operation_id"],
                "issuer": "NSE:SYNTHA",
            },
        )
    )["data"]
    assert imported["sources"] and adapter.service.ledger.snapshot() == used


async def test_optional_logging_is_private_and_failure_before_dispatch_blocks(tmp_path):
    path = tmp_path / "tools.jsonl"
    recorder = ToolRecorder(path)
    service = ResearchService(Settings())
    adapter = MarginMCP(service, recorder)
    try:
        result = await invoke(
            adapter, "margin_calculate", fcff() | {"why": "Use the deterministic calculator."}
        )
        events = [json.loads(line) for line in path.read_text().splitlines()]
        assert [e["phase"] for e in events] == ["request", "response"]
        assert [e["sequence"] for e in events] == [1, 2]
        assert events[0]["arguments"]["why"] == "Use the deterministic calculator."
        assert events[0]["call_id"] == result["call_id"] == events[1]["result"]["call_id"]
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        recorder.maximum = recorder.size
        result = await invoke(
            adapter,
            "margin_preview",
            {
                "operations": [
                    {
                        "operation": "bharatstock.get_stock_quote",
                        "arguments": {"ticker": "SYNTHA", "exchange": "NSE"},
                    }
                ]
            },
            error=True,
        )
        assert result["error"]["code"] == "recording"
        assert "warnings" not in result and not service.plans
        assert not any(service.ledger.requests.values())
    finally:
        await service.close()
        recorder.close()
    with pytest.raises(FileExistsError):
        ToolRecorder(path)


async def test_post_action_log_failure_returns_existing_result_with_warning(adapter):
    class Recorder:
        def __init__(self):
            self.n = 0
            self.path = "fictional"

        def append(self, event):
            self.n += 1
            if self.n == 2:
                raise DomainError("recording", "Fictional failed disk")

    adapter.recorder = Recorder()
    result = await invoke(adapter, "margin_calculate", fcff())
    assert result["data"]["values"]["fcff"] == "60.00"
    assert any("Post-action" in w for w in result["warnings"])


def test_directory_recording_generates_unique_private_files_without_overwrite(tmp_path):
    folder = tmp_path / "private-logs"
    for i in range(3):
        recorder = ToolRecorder(directory=folder)
        recorder.append({"phase": "test", "index": i})
        recorder.close()
    logs = sorted(folder.glob("margin-*.jsonl"))
    assert len(logs) == 3
    assert {json.loads(p.read_text())["index"] for p in logs} == {0, 1, 2}
    assert all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in logs)
    assert stat.S_IMODE(folder.stat().st_mode) == 0o700
    with pytest.raises(ValueError):
        ToolRecorder(tmp_path / "another.jsonl", directory=folder)
    assert not (tmp_path / "another.jsonl").exists()


def test_record_directory_cannot_be_an_existing_file(tmp_path):
    path = tmp_path / "preserve"
    path.write_text("existing-data")
    with pytest.raises(FileExistsError):
        ToolRecorder(directory=path)
    assert path.read_text() == "existing-data"


async def test_stdio_restarts_with_same_record_directory_preserve_prior_launch(tmp_path):
    config = subprocess_config()
    folder = tmp_path / "sessions"
    config.args += ["--record-dir", str(folder)]
    previous = {}
    sessions = []
    for _ in range(2):
        with (tmp_path / "stderr.txt").open("a") as stderr:
            async with stdio_client(config, errlog=stderr) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    status = (await client.call_tool("margin_status", {})).structured_content
                    assert status["data"]["recording_enabled"]
                    assert not any(status["data"]["ledger"]["http_attempts"].values())
                    sessions.append(status["session_id"])
        for path, content in previous.items():
            assert path.read_bytes() == content
        previous = {path: path.read_bytes() for path in folder.glob("*.jsonl")}
    assert len(previous) == 2 and len(set(sessions)) == 2
    for content in previous.values():
        events = [json.loads(line) for line in content.decode().splitlines()]
        assert [e["sequence"] for e in events] == [1, 2]
        assert [e["phase"] for e in events] == ["request", "response"]


def subprocess_config():
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_") and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}
    }
    env.update(
        PYTHONPATH=str(ROOT / "src"),
        MARGIN_BHARATSTOCK_REQUESTS="2",
        MARGIN_DRISHTI_REQUESTS="8",
        MARGIN_DRISHTI_CREDITS="4",
    )
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "margin.interfaces.mcp", "--mode", "synthetic"],
        env=env,
        cwd=str(ROOT),
    )


def test_startup_refuses_existing_log_without_overwrite_or_raw_trace(tmp_path):
    path = tmp_path / "existing.jsonl"
    path.write_text("preserve-existing-data\n")
    config = subprocess_config()
    result = subprocess.run(
        [config.command, *config.args, "--record-file", str(path)],
        env=config.env,
        cwd=ROOT,
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2 and result.stdout == ""
    assert "Traceback" not in result.stderr
    assert path.read_text() == "preserve-existing-data\n"


async def test_real_stdio_live_mode_can_inspect_and_calculate_with_zero_allowance(tmp_path):
    config = subprocess_config()
    config.args = ["-m", "margin.interfaces.mcp", "--mode", "live"]
    config.env.update(
        MARGIN_BHARATSTOCK_REQUESTS="0",
        MARGIN_DRISHTI_REQUESTS="0",
        MARGIN_DRISHTI_CREDITS="0",
        BHARATSTOCK_API_KEY="fictional-live-key-never-dispatched",
        DRISHTI_API_KEY="fictional-events-key-never-dispatched",
    )
    with (tmp_path / "stderr.txt").open("w") as stderr:
        async with stdio_client(config, errlog=stderr) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                status = (await session.call_tool("margin_status", {})).structured_content
                assert status["mode"] == "live"
                await session.call_tool("margin_catalog", {})
                output = (await session.call_tool("margin_calculate", fcff())).structured_content
                assert output["data"]["values"]["fcff"] == "60.00"
                stopped = await session.call_tool(
                    "margin_connect_drishti", {"session_id": "old-process"}
                )
                assert stopped.is_error
                final = (await session.call_tool("margin_status", {})).structured_content
                assert final["data"]["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}
                assert "fictional-live-key" not in json.dumps(final)


async def test_real_stdio_sdk_handshake_run_finance_and_shutdown(tmp_path):
    with (tmp_path / "stderr.txt").open("w") as stderr:
        async with stdio_client(subprocess_config(), errlog=stderr) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                assert (
                    initialized.server_info.name == "margin"
                    and initialized.server_info.version == VERSION
                )
                tools = (await session.list_tools()).tools
                assert len(tools) == 25
                status = (await session.call_tool("margin_status", {})).structured_content
                assert status["mode"] == "synthetic" and status["data"]["ledger"][
                    "http_attempts"
                ] == {"bharatstock": 0, "drishti": 0}
                response = await session.call_tool(
                    "margin_company_preview",
                    {
                        "function": "finance.company_margins",
                        "ticker": "SYNTHA",
                        "exchange": "NSE",
                        "fetch_missing": True,
                    },
                )
                plan = response.structured_content
                args = {
                    "session_id": plan["session_id"],
                    "plan_id": plan["data"]["plan_id"],
                    "idempotency_key": "stdio-single-request",
                    "wait_seconds": 2,
                }
                run = (await session.call_tool("margin_run", args)).structured_content["data"]
                output = await session.call_tool(
                    "margin_result",
                    {
                        "run_id": run["run_id"],
                        "operation_id": run["operations"][-1]["operation_id"],
                    },
                )
                assert (
                    not output.is_error
                    and output.structured_content["data"]["payload"]["status"] == "success"
                )
                assert json.loads(output.content[0].text) == output.structured_content
                await session.call_tool("margin_run", args)
                status = (await session.call_tool("margin_status", {})).structured_content
                assert status["data"]["ledger"]["http_attempts"]["bharatstock"] == 1
                value = await session.call_tool("margin_calculate", fcff())
                assert value.structured_content["data"]["values"]["fcff"] == "60.00"
                invalid = await session.call_tool(
                    "margin_calculate", {"function": "unknown", "arguments": {}}
                )
                assert invalid.is_error
                with pytest.raises(MCPError) as missing:
                    await session.call_tool("finance.calculate_margins", {})
                assert missing.value.error.code == -32602
                assert "margin_calculate" in missing.value.error.message
                assert not (await session.call_tool("margin_status", {})).is_error
    assert "SYNTHETIC" in (tmp_path / "stderr.txt").read_text()


async def test_server_lifespan_closes_core_and_optional_log():
    services = []

    class Tracked(ResearchService):
        async def close(self):
            await super().close()
            self.closed = True

    def factory(settings):
        service = Tracked(settings)
        services.append(service)
        return service

    server = create_server(Settings(), service_factory=factory)
    async with server.lifespan(server) as adapter:
        await invoke(adapter, "margin_status")
        assert not any(adapter.service.ledger.requests.values())
    assert services[0].closed and not services[0]._buffers
