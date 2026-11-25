"""Private Unix IPC and real stdio reconnects with fictional upstreams only."""

import asyncio
import json
import os
import socket
import stat
import struct
import sys
import tempfile
from pathlib import Path

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import MCPError

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.backend import Backend
from margin.interfaces.mcp.bridge import (
    REQUEST_LIMIT,
    RESPONSE_LIMIT,
    RPC_VERSION,
    RemoteMCP,
    read_frame,
    rpc,
    write_frame,
)
from margin.interfaces.mcp.server import create_server

ROOT = Path(__file__).parents[1]
ORIGINAL_CONNECT = socket.socket.connect
ORIGINAL_CONNECT_EX = socket.socket.connect_ex
pytestmark = pytest.mark.skipif(os.name != "posix", reason="Optional shared mode uses Unix sockets")


@pytest.fixture(autouse=True)
def unix_only(monkeypatch):
    def connect(sock, address):
        assert sock.family == socket.AF_UNIX, "External TCP is forbidden in backend tests"
        return ORIGINAL_CONNECT(sock, address)

    def connect_ex(sock, address):
        assert sock.family == socket.AF_UNIX, "External TCP is forbidden in backend tests"
        return ORIGINAL_CONNECT_EX(sock, address)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)


@pytest.fixture
def address():
    # macOS Unix socket addresses are short; pytest's default path can exceed the limit.
    with tempfile.TemporaryDirectory(
        prefix="margin-test-", dir="/private/tmp" if Path("/private/tmp").exists() else "/tmp"
    ) as folder:
        yield str(Path(folder) / "s")


def client_params(path):
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_") and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}
    }
    env["PYTHONPATH"] = str(ROOT / "src")
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "margin.interfaces.mcp", "--backend-socket", path, "--mode", "synthetic"],
        env=env,
        cwd="/private/tmp" if Path("/private/tmp").exists() else "/tmp",
    )


async def test_real_stdio_preview_and_execution_survive_frontend_restarts(address, tmp_path):
    async with Backend(address, Settings(), record_dir=tmp_path / "logs") as backend:
        params = client_params(address)
        with (tmp_path / "stderr.txt").open("w") as err:
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    assert len((await client.list_tools()).tools) == 35
                    preview = (
                        await client.call_tool(
                            "margin_preview",
                            {
                                "operations": [
                                    {
                                        "operation": "bharatstock.get_financials",
                                        "arguments": {
                                            "ticker": "SYNTHA",
                                            "exchange": "NSE",
                                            "period_type": "annual",
                                            "page": 1,
                                            "page_size": 2,
                                        },
                                    }
                                ]
                            },
                        )
                    ).structured_content
            assert backend.service.ledger.requests["bharatstock"] == 0
            args = {
                "session_id": preview["session_id"],
                "plan_id": preview["data"]["plan_id"],
                "idempotency_key": "reconnect-once",
                "wait_seconds": 2,
            }
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    run = (await client.call_tool("margin_run", args)).structured_content["data"]
                    assert run["status"] == "completed"
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    again = (await client.call_tool("margin_run", args)).structured_content["data"]
                    assert again["run_id"] == run["run_id"]
                    ids = {
                        "run_id": run["run_id"],
                        "operation_id": run["operations"][0]["operation_id"],
                    }
                    result = (await client.call_tool("margin_result", ids)).structured_content
                    assert result["session_id"] == preview["session_id"]
                    assert result["data"]["financial_view"]["raw_statement_unit"] == "INR"
                    facts = (await client.call_tool("margin_facts", ids)).structured_content[
                        "data"
                    ]["facts"]
                    assert facts
            assert backend.service.ledger.requests["bharatstock"] == 1
            assert stat.S_IMODE(Path(address).stat().st_mode) == 0o600
        events = [
            json.loads(line)
            for p in (tmp_path / "logs").glob("*.jsonl")
            for line in p.read_text().splitlines()
        ]
        assert len({event["session_id"] for event in events}) == 1
    assert not Path(address).exists()


async def test_shared_proxy_never_creates_a_local_core(address):
    def forbidden(_):
        raise AssertionError("Proxy must not own a provider/core")

    async with Backend(address, Settings()):
        server = create_server(backend_socket=address, service_factory=forbidden)
        async with server.lifespan(server) as proxy:
            assert not (await proxy.call("margin_status", {})).is_error


async def test_shared_profile_switch_keeps_prepared_packet_without_provider_calls(
    address, tmp_path
):
    async with Backend(
        address, Settings(bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    ) as backend:
        params = client_params(address)
        with (tmp_path / "profile-stderr.txt").open("w") as err:
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    status = (await client.call_tool("margin_status", {})).structured_content
                    source = {
                        "issuer": "NSE:EXAMPLE",
                        "title": "Fictional profile source",
                        "url": "https://example.invalid/profile",
                        "kind": "provider_summary",
                        "date": None,
                        "date_kind": "unknown",
                        "passages": [
                            {"passage_id": "P1", "text": "Demand improved.", "locator": "summary"}
                        ],
                    }
                    registered = (
                        await client.call_tool("margin_register_sources", {"sources": [source]})
                    ).structured_content
                    sid = registered["data"]["sources"][0]["source_id"]
                    prepared = (
                        await client.call_tool(
                            "margin_prepare_verification",
                            {
                                "claims": [
                                    {
                                        "claim_id": "C1",
                                        "text": "Demand improved.",
                                        "source_ids": [sid],
                                    }
                                ],
                            },
                        )
                    ).structured_content["data"]
            params = client_params(address)
            params.args += ["--tool-profile", "review"]
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    initialized = await client.initialize()
                    assert "local review profile" in initialized.instructions
                    assert len((await client.list_tools()).tools) == 14
                    current = (await client.call_tool("margin_status", {})).structured_content
                    assert (
                        current["session_id"] == status["session_id"] == backend.adapter.session_id
                    )
                    assert current["data"]["tool_profile"] == "review"
                    rendered = (
                        await client.call_tool(
                            "margin_render_citations",
                            {k: prepared[k] for k in ("packet_id", "packet_hash")},
                        )
                    ).structured_content
                    assert rendered["data"]["citations"][0]["semantic_review"] == "not_reviewed"
                    before = backend.recorder.sequence
                    with pytest.raises(MCPError) as caught:
                        await client.call_tool("margin_run", {})
                    assert caught.value.error.code == -32602
                    assert backend.recorder.sequence == before
        assert backend.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


async def test_backend_restart_rejects_old_epoch_and_plan(address):
    async with Backend(address, Settings()):
        old = await RemoteMCP.connect(address)
        preview = (
            await old.call(
                "margin_preview",
                {
                    "operations": [
                        {
                            "operation": "bharatstock.get_financials",
                            "arguments": {
                                "ticker": "SYNTHA",
                                "exchange": "NSE",
                                "period_type": "annual",
                                "page": 1,
                                "page_size": 1,
                            },
                        }
                    ]
                },
            )
        ).structured_content
    async with Backend(address, Settings()) as backend:
        with pytest.raises(MCPError, match="identity changed"):
            await old.call("margin_status", {})
        new = await RemoteMCP.connect(address)
        failed = (
            await new.call(
                "margin_run",
                {
                    "session_id": preview["session_id"],
                    "plan_id": preview["data"]["plan_id"],
                    "idempotency_key": "stale-not-paid",
                },
            )
        ).structured_content
        assert failed["error"]["code"] == "session_changed"
        assert not any(backend.service.ledger.requests.values())


async def test_single_owner_and_mode_version_checks(address):
    async with Backend(address, Settings()) as backend:
        with pytest.raises(OSError):
            async with Backend(address, Settings()):
                pytest.fail("Duplicate owner admitted")
        assert Path(address).exists()
        with pytest.raises(ValueError, match="mode differs"):
            await RemoteMCP.connect(address, "live")
        backend.info = lambda: {"version": "incompatible", "mode": "synthetic"}
        with pytest.raises(ValueError, match="version"):
            await RemoteMCP.connect(address)


@pytest.mark.parametrize("kind", ["oversize", "invalid_json", "unknown_method"])
async def test_malformed_private_frames_cannot_dispatch(address, kind):
    async with Backend(address, Settings()) as backend:
        reader, writer = await asyncio.open_unix_connection(address)
        raw = (
            b"not-json"
            if kind == "invalid_json"
            else json.dumps({"rpc_version": RPC_VERSION, "method": "arbitrary"}).encode()
        )
        writer.write(
            struct.pack("!I", REQUEST_LIMIT + 1)
            if kind == "oversize"
            else struct.pack("!I", len(raw)) + raw
        )
        await writer.drain()
        assert await asyncio.wait_for(reader.read(), 2) == b""
        writer.close()
        await writer.wait_closed()
        assert not any(backend.service.ledger.requests.values()) and not backend.service.runs


async def test_unavailable_backend_and_explicit_stop(address):
    with pytest.raises(MCPError) as failure:
        await rpc(address, {"method": "info"})
    assert failure.value.data["uncertain_outcome"] is False
    async with Backend(address, Settings()) as backend:
        info = await rpc(address, {"method": "info"})
        result = await rpc(address, {"method": "stop", "session_id": info["session_id"]})
        assert result["stopping"]
        await asyncio.wait_for(backend.stop.wait(), 1)


async def test_private_directory_and_non_socket_file_are_not_overwritten(address):
    path = Path(address)
    path.write_text("preserve")
    with pytest.raises(ValueError):
        async with Backend(address, Settings()):
            pytest.fail("File replaced")
    assert path.read_text() == "preserve"
    path.unlink()
    path.parent.chmod(0o755)
    with pytest.raises(ValueError, match="owner-only"):
        async with Backend(address, Settings()):
            pytest.fail("Unsafe directory accepted")
    path.parent.chmod(0o700)


async def test_lost_rpc_reply_is_uncertain_and_not_retried(address):
    received = []

    async def disconnect(reader, writer):
        received.append(await read_frame(reader, REQUEST_LIMIT))
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_unix_server(disconnect, address)
    Path(address).chmod(0o600)
    try:
        with pytest.raises(MCPError) as failure:
            await rpc(
                address,
                {"method": "call", "name": "margin_run", "session_id": "test", "arguments": {}},
            )
        assert failure.value.data["uncertain_outcome"] is True
        assert len(received) == 1
    finally:
        server.close()
        await server.wait_closed()


async def test_backend_keys_never_reach_proxy_info_or_recordings(address, tmp_path):
    secret = "fictional-private-provider-key"
    async with Backend(address, Settings(bharatstock_key=secret), record_dir=tmp_path / "logs"):
        proxy = await RemoteMCP.connect(address)
        assert secret not in json.dumps(proxy.info)
        answer = await proxy.call("margin_status", {"why": secret})
        assert answer.is_error and secret not in answer.model_dump_json()
    assert all(secret not in path.read_text() for path in (tmp_path / "logs").glob("*.jsonl"))


async def test_running_work_survives_stdio_frontend_exit(address, tmp_path):
    entered, release = asyncio.Event(), asyncio.Event()

    async def response(_):
        entered.set()
        await release.wait()
        return httpx.Response(200, json={"data": []})

    service = ResearchService(Settings())
    await service.providers["bharatstock"].client.aclose()
    service.providers["bharatstock"].client = httpx.AsyncClient(
        base_url="https://bharatstockapi.com", transport=httpx.MockTransport(response)
    )
    async with Backend(address, Settings(), service_factory=lambda _: service):
        params = client_params(address)
        with (tmp_path / "stderr.txt").open("w") as err:
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    preview = (
                        await client.call_tool(
                            "margin_preview",
                            {
                                "operations": [
                                    {
                                        "operation": "bharatstock.get_financials",
                                        "arguments": {
                                            "ticker": "SYNTHA",
                                            "exchange": "NSE",
                                            "period_type": "annual",
                                            "page": 1,
                                            "page_size": 1,
                                        },
                                    }
                                ]
                            },
                        )
                    ).structured_content
                    run = (
                        await client.call_tool(
                            "margin_run",
                            {
                                "session_id": preview["session_id"],
                                "plan_id": preview["data"]["plan_id"],
                                "idempotency_key": "survive-frontend-exit",
                            },
                        )
                    ).structured_content["data"]
                    await asyncio.wait_for(entered.wait(), 2)
            assert service.get_run(run["run_id"])["status"] == "running"
            release.set()
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    done = (
                        await client.call_tool(
                            "margin_run_status", {"run_id": run["run_id"], "wait_seconds": 2}
                        )
                    ).structured_content["data"]
                    assert done["status"] == "completed"
                    assert service.ledger.requests["bharatstock"] == 1


async def test_invalid_backend_result_withholds_validation_diagnostics(address):
    async def invalid_result(reader, writer):
        await read_frame(reader, REQUEST_LIMIT)
        await write_frame(
            writer,
            {"rpc_version": RPC_VERSION, "result": {"content": "private-source-text"}},
            RESPONSE_LIMIT,
        )
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_unix_server(invalid_result, address)
    Path(address).chmod(0o600)
    try:
        with pytest.raises(MCPError) as error:
            await RemoteMCP(address, {"session_id": "fixture"}).call("margin_status", {})
        assert "private-source-text" not in str(error.value)
        assert error.value.data["uncertain_outcome"] is True
    finally:
        server.close()
        await server.wait_closed()
