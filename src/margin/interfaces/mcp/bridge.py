"""Private local RPC, independent of MCP wire sessions; never retries dispatch."""

from __future__ import annotations

import asyncio
import json
import os
import stat
import struct
from pathlib import Path

from mcp import types
from mcp.shared.exceptions import MCPError

from margin.interfaces.mcp.tools import VERSION, definitions

RPC_VERSION = "margin.local.v1"
REQUEST_LIMIT = 70 * 1024
RESPONSE_LIMIT = 8 * 1024 * 1024  # SDK result carries both JSON text and structured JSON.


async def read_frame(reader, maximum):
    size = struct.unpack("!I", await reader.readexactly(4))[0]
    if size > maximum:
        raise ValueError("Local frame exceeds its bound.")
    raw = await reader.readexactly(size)

    def invalid(_):
        raise ValueError("Nonfinite JSON is forbidden.")

    return json.loads(raw, parse_constant=invalid)


async def write_frame(writer, value, maximum):
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
    if len(raw) > maximum:
        raise ValueError("Local frame exceeds its bound.")
    writer.write(struct.pack("!I", len(raw)) + raw)
    await writer.drain()


async def rpc(path, request):
    writer = None
    sent = False
    try:
        async with asyncio.timeout(90):
            reader, writer = await asyncio.wait_for(asyncio.open_unix_connection(path), 3)
            # Once written, a lost reply may hide a completed mutation/paid submission.
            sent = True
            await write_frame(writer, {"rpc_version": RPC_VERSION, **request}, REQUEST_LIMIT)
            reply = await read_frame(reader, RESPONSE_LIMIT)
            if not isinstance(reply, dict) or reply.get("rpc_version") != RPC_VERSION:
                raise ValueError("Unrecognized local backend.")
            if "error" in reply:
                error = reply["error"]
                raise MCPError(code=error["code"], message=error["message"], data=error.get("data"))
            return reply["result"]
    except MCPError:
        raise
    except (
        OSError,
        TimeoutError,
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        asyncio.IncompleteReadError,
    ):
        raise MCPError(
            code=-32000,
            message="Local Margin backend unavailable or reply lost. No automatic restart/retry was made. Inspect the existing plan/key before any new submission.",
            data={"uncertain_outcome": sent},
        ) from None
    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass


class RemoteMCP:
    def __init__(self, path, info):
        self.path, self.info = path, info
        self.tools = definitions()

    @classmethod
    async def connect(cls, path, expected_mode=None):
        folder = Path(path).parent.lstat()
        target = Path(path).lstat()
        if (
            os.name != "posix"
            or not stat.S_ISDIR(folder.st_mode)
            or folder.st_uid != os.getuid()
            or folder.st_mode & 0o077
            or not stat.S_ISSOCK(target.st_mode)
            or target.st_uid != os.getuid()
            or target.st_mode & 0o077
        ):
            raise ValueError("Connect only to an owner-only local backend socket.")
        info = await rpc(path, {"method": "info"})
        if info.get("version") != VERSION or info.get("mode") not in {"live", "synthetic"}:
            raise ValueError("Backend package version is incompatible.")
        if expected_mode and info["mode"] != expected_mode:
            raise ValueError("Backend mode differs from the required mode.")
        return cls(path, info)

    async def call(self, name, arguments):
        result = await rpc(
            self.path,
            {
                "method": "call",
                "session_id": self.info["session_id"],
                "name": name,
                "arguments": arguments,
            },
        )
        try:
            return types.CallToolResult.model_validate(result)
        except (ValueError, TypeError):
            raise MCPError(
                -32000,
                "Local backend returned an unsupported result; raw diagnostics withheld. Do not resubmit an uncertain action.",
                {"uncertain_outcome": True},
            ) from None
