"""Explicit single-user state owner for reconnecting stdio clients on macOS/Linux."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import stat
import sys
from dataclasses import replace
from pathlib import Path

from mcp.shared.exceptions import MCPError

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.agent.local_config import read_provider_env
from margin.interfaces.mcp.bridge import (
    REQUEST_LIMIT,
    RESPONSE_LIMIT,
    RPC_VERSION,
    read_frame,
    rpc,
    write_frame,
)
from margin.interfaces.mcp.recording import ToolRecorder
from margin.interfaces.mcp.server import MarginMCP
from margin.interfaces.mcp.tools import VERSION


class Backend:
    def __init__(self, path, settings, *, record_dir=None, service_factory=ResearchService):
        self.path = Path(path).absolute()
        self.settings, self.record_dir, self.service_factory = settings, record_dir, service_factory
        self.lock = self.server = self.service = self.recorder = None
        self.owned_socket = False
        self.handlers = set()
        self.stop = asyncio.Event()

    async def __aenter__(self):
        if os.name != "posix" or not hasattr(asyncio, "start_unix_server"):
            raise ValueError("Shared backend mode requires Unix sockets; use standalone mode here.")
        import fcntl

        if len(os.fsencode(self.path)) > 100:
            raise ValueError("Choose a shorter local socket path.")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        folder = self.path.parent.lstat()
        if (
            not stat.S_ISDIR(folder.st_mode)
            or folder.st_uid != os.getuid()
            or folder.st_mode & 0o077
        ):
            raise ValueError("The socket requires an owner-only directory, not a symlink.")
        try:
            self.lock = os.open(
                str(self.path) + ".lock",
                os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
                0o600,
            )
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if self.path.exists() or self.path.is_symlink():
                if not stat.S_ISSOCK(self.path.lstat().st_mode):
                    raise ValueError("The socket path contains an unrelated file.")
                try:
                    _, writer = await asyncio.wait_for(
                        asyncio.open_unix_connection(str(self.path)), 0.5
                    )
                except (ConnectionRefusedError, FileNotFoundError):
                    self.path.unlink()  # The acquired lock excludes a cooperative live owner.
                else:
                    writer.close()
                    await writer.wait_closed()
                    raise ValueError("A listener already owns this address.")
            self.recorder = ToolRecorder(directory=self.record_dir)
            self.service = self.service_factory(self.settings)
            self.adapter = MarginMCP(
                self.service, self.recorder, state_owner="shared_backend_process"
            )
            self.server = await asyncio.start_unix_server(
                self.handle, str(self.path), limit=REQUEST_LIMIT + 4
            )
            self.owned_socket = True
            self.socket_inode = self.path.stat().st_ino
            self.path.chmod(0o600)
            return self
        except BaseException:
            await self.close()
            raise

    async def __aexit__(self, *_):
        await self.close()

    def info(self):
        return {
            "version": VERSION,
            "session_id": self.adapter.session_id,
            "mode": self.settings.mode,
            "pid": os.getpid(),
            "state_lifetime": "backend process; source TTL/eviction still apply",
            "recording_enabled": self.recorder.path is not None,
        }

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        if len(self.handlers) >= 16:
            writer.close()
            return
        self.handlers.add(task)
        shutdown = False
        try:
            async with asyncio.timeout(90):
                request = await read_frame(reader, REQUEST_LIMIT)
                if not isinstance(request, dict) or request.get("rpc_version") != RPC_VERSION:
                    raise ValueError
                method = request.get("method")
                fields = {
                    "info": {"rpc_version", "method"},
                    "stop": {"rpc_version", "method", "session_id"},
                    "call": {"rpc_version", "method", "session_id", "name", "arguments"},
                }
                if method not in fields or set(request) != fields[method]:
                    raise ValueError
                if method == "info":
                    result = self.info()
                else:
                    if request["session_id"] != self.adapter.session_id:
                        raise MCPError(
                            -32000,
                            "Backend identity changed. Reconnect, reconcile allowance and preview again; old handles are not reusable.",
                            {"uncertain_outcome": False},
                        )
                    if method == "stop":
                        shutdown, result = (
                            True,
                            {
                                "stopping": True,
                                "note": "Reconcile provider allowance before any future restart.",
                            },
                        )
                    else:
                        result = (
                            await self.adapter.call(request["name"], request["arguments"])
                        ).model_dump(mode="json", by_alias=True)
                reply = {"rpc_version": RPC_VERSION, "result": result}
                await write_frame(writer, reply, RESPONSE_LIMIT)
        except MCPError as exc:
            try:
                await write_frame(
                    writer,
                    {
                        "rpc_version": RPC_VERSION,
                        "error": {"code": exc.code, "message": exc.message, "data": exc.data},
                    },
                    RESPONSE_LIMIT,
                )
            except (OSError, ValueError):
                pass
        except (
            ValueError,
            TypeError,
            KeyError,
            RecursionError,
            TimeoutError,
            OSError,
            asyncio.IncompleteReadError,
        ):
            # Do not reflect raw frames, credential values or exception diagnostics.
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
            self.handlers.discard(task)
            if shutdown:
                self.stop.set()

    async def close(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        for task in tuple(self.handlers):
            task.cancel()
        if self.handlers:
            await asyncio.gather(*tuple(self.handlers), return_exceptions=True)
        if self.service:
            await self.service.close()
        if self.recorder:
            self.recorder.close()
        if self.owned_socket:
            try:
                if self.path.lstat().st_ino == self.socket_inode:
                    self.path.unlink()
            except FileNotFoundError:
                pass
            self.owned_socket = False
        if self.lock is not None:
            os.close(self.lock)
            self.lock = None


async def run(args):
    if args.status or args.stop:
        info = await rpc(args.socket, {"method": "info"})
        if args.stop:
            info = await rpc(args.socket, {"method": "stop", "session_id": info["session_id"]})
        print(json.dumps(info))
        return
    settings = Settings.from_env()
    keys = read_provider_env(args.credentials_file) if args.credentials_file else {}
    settings = replace(
        settings,
        mode=args.mode or settings.mode,
        bharatstock_key=keys.get("BHARATSTOCK_API_KEY", settings.bharatstock_key),
        drishti_key=keys.get("DRISHTI_API_KEY", settings.drishti_key),
    )
    async with Backend(args.socket, settings, record_dir=args.record_dir) as backend:
        loop = asyncio.get_running_loop()
        for value in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(value, backend.stop.set)
        print(
            f"Margin backend {VERSION}: {settings.mode.upper()}; state and allowances live until this backend stops.",
            file=sys.stderr,
            flush=True,
        )
        await backend.stop.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Explicit local Margin state owner; no public HTTP listener or automatic restart."
    )
    parser.add_argument("--socket", required=True)
    parser.add_argument("--mode", choices=["synthetic", "live"])
    parser.add_argument("--credentials-file")
    parser.add_argument("--record-dir")
    controls = parser.add_mutually_exclusive_group()
    controls.add_argument("--status", action="store_true")
    controls.add_argument("--stop", action="store_true")
    args = parser.parse_args(argv)
    # Apply the same suppression as the stdio entry point without raw RPC diagnostics.
    import logging

    for name in ("mcp", "httpx", "httpx2", "httpcore", "httpcore2"):
        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        logger.setLevel(logging.CRITICAL + 1)
    try:
        asyncio.run(run(args))
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception:
        print(
            "Margin backend action failed. Check the private socket directory, existing owner, version and configuration. No automatic restart or retry; private diagnostics withheld.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
