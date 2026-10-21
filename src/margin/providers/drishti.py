"""A single owner task enters, uses and exits the SDK contexts.

The SDK's async contexts must not be entered in a browser-request task and
closed by another request. No downstream Margin MCP server is involved here.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from contextlib import AsyncExitStack

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from margin.core.contracts import DomainError, ProviderOutcome
from margin.core.registry import DRISHTI, NATIVE, schema_hash


class CappedStream(httpx2.AsyncByteStream):
    def __init__(self, stream, maximum):
        self.stream, self.maximum = stream, maximum

    async def __aiter__(self):
        total = 0
        async for chunk in self.stream:
            total += len(chunk)
            if total > self.maximum:
                raise DomainError(
                    "oversize_output", "MCP HTTP response exceeded the byte bound.", uncertain=True
                )
            yield chunk

    async def aclose(self):
        await self.stream.aclose()


class GuardedTransport(httpx2.AsyncBaseTransport):
    def __init__(self, inner, ledger, endpoint, maximum):
        self.inner, self.ledger = inner, ledger
        self.endpoint, self.maximum = httpx2.URL(endpoint), maximum

    async def handle_async_request(self, request):
        target = request.url
        if (
            (target.scheme, target.host, target.port, target.path.rstrip("/"))
            != (
                self.endpoint.scheme,
                self.endpoint.host,
                self.endpoint.port,
                self.endpoint.path.rstrip("/"),
            )
            or target.query
            or target.userinfo
        ):
            raise DomainError(
                "unsafe_transport", "MCP request attempted to leave its configured endpoint."
            )
        if "last-event-id" in request.headers:
            raise DomainError(
                "uncertain_outcome", "Automatic stream resumption is disabled.", uncertain=True
            )
        if request.method not in {"POST", "GET", "DELETE"}:
            raise DomainError("unsafe_transport", "Unsupported MCP transport method.")
        await self.ledger.http_attempt("drishti")
        response = await self.inner.handle_async_request(request)
        response.stream = CappedStream(response.stream, self.maximum)
        return response

    async def aclose(self):
        await self.inner.aclose()


def result_data(result):
    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured
    for block in getattr(result, "content", []):
        if getattr(block, "type", None) == "text":
            try:
                value = json.loads(block.text)
                if isinstance(value, dict):
                    return value
            except ValueError:
                pass
    raise DomainError("schema_changed", "Metadata result shape was not recognized; withheld.")


class DrishtiAdapter:
    ENDPOINT = "https://mcp.drishti.manasija.in"

    def __init__(self, ledger, settings, *, transport=None, endpoint=None):
        self.ledger, self.settings = ledger, settings
        # Endpoint injection exists for synthetic upstream tests, never an env/UI option.
        self.endpoint = endpoint or self.ENDPOINT
        self.transport = transport
        self._queue = asyncio.Queue(maxsize=10)
        self._task = None
        self.state = "disconnected"
        self.verified = set()
        self.changed = set()
        self.refreshed = 0.0

    def status(self):
        return {
            "state": self.state,
            "verified_operations": sorted(self.verified),
            "schema_changed_operations": sorted(self.changed),
            "metadata_fresh": self.state == "connected"
            and time.monotonic() - self.refreshed <= self.settings.metadata_ttl,
            "live_access_verified": False,
            "note": "Metadata approval is not data entitlement or a current account balance.",
        }

    def assert_ready(self, spec):
        if self.state != "connected":
            raise DomainError("not_connected", "Use the explicit Connect/refresh action first.")
        if spec.name not in self.verified:
            raise DomainError("schema_changed", "The selected operation's schema is not approved.")
        if time.monotonic() - self.refreshed > self.settings.metadata_ttl:
            raise DomainError(
                "metadata_expired", "Refresh metadata explicitly before another live operation."
            )

    async def connect(self):
        if not self.settings.drishti_key:
            raise DomainError(
                "invalid_credentials", "Configure DRISHTI_API_KEY in the backend environment."
            )
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._owner(), name="margin-drishti-owner")
        return await self._submit("connect", None, None)

    async def execute(self, spec, arguments):
        self.assert_ready(spec)
        return await self._submit("execute", spec, arguments)

    async def _submit(self, action, spec, arguments):
        future = asyncio.get_running_loop().create_future()
        try:
            self._queue.put_nowait((action, spec, arguments, future))
        except asyncio.QueueFull:
            raise DomainError("queue_full", "Drishti command queue is full.") from None
        return await future

    async def _open(self, stack):
        # The SDK can log raw RPC messages/errors. No transport debug logging with keys.
        for name in ("mcp", "httpx2", "httpcore2"):
            logger = logging.getLogger(name)
            logger.addHandler(logging.NullHandler())
            logger.propagate = False
            logger.setLevel(logging.CRITICAL + 1)
        inner = self.transport or httpx2.AsyncHTTPTransport(retries=0)
        guarded = GuardedTransport(
            inner, self.ledger, self.endpoint, self.settings.max_result_bytes
        )
        client = await stack.enter_async_context(
            httpx2.AsyncClient(
                transport=guarded,
                headers={"Authorization": "Bearer " + self.settings.drishti_key},
                follow_redirects=False,
                max_redirects=0,
                trust_env=False,
                timeout=httpx2.Timeout(45, connect=15),
            )
        )
        read, write = await stack.enter_async_context(
            streamable_http_client(self.endpoint, http_client=client)
        )
        session = await stack.enter_async_context(
            ClientSession(read, write, read_timeout_seconds=self.settings.call_timeout)
        )
        await session.initialize()
        return session

    async def _refresh(self, session):
        catalog = await session.list_tools()
        if catalog.next_cursor:
            raise DomainError("schema_changed", "Native catalog exceeds the reviewed bounded page.")
        tools = {t.name: t for t in catalog.tools}
        if set(tools) != set(NATIVE):
            raise DomainError(
                "schema_changed", "Native routing catalog changed; manual review required."
            )
        for name, approved in NATIVE.items():
            live = tools[name]
            if schema_hash(live.input_schema) != schema_hash(
                approved["inputSchema"]
            ) or schema_hash(live.output_schema or {}) != schema_hash(
                approved["outputSchema"] or {}
            ):
                raise DomainError(
                    "schema_changed", "A native routing contract changed; manual review required."
                )
        result = await session.call_tool("describe_tools", {"names": sorted(DRISHTI)})
        if getattr(result, "is_error", True):
            raise DomainError("metadata_failed", "Operation descriptions could not be refreshed.")
        described = result_data(result).get("tools")
        if not isinstance(described, list):
            raise DomainError(
                "schema_changed", "Unknown description envelope; no operations approved."
            )
        approved, changed = set(), set(DRISHTI)
        for item in described:
            name = item.get("name")
            if name in DRISHTI and schema_hash(item.get("input_schema", {})) == schema_hash(
                DRISHTI[name]["inputSchema"]
            ):
                approved.add(name)
                changed.discard(name)
        self.verified, self.changed = approved, changed
        self.refreshed = time.monotonic()
        self.state = "connected"
        return self.status()

    async def _owner(self):
        session = None
        active = None
        try:
            async with AsyncExitStack() as stack:
                while True:
                    active = await self._queue.get()
                    action, spec, args, future = active
                    if future.cancelled():
                        continue
                    try:
                        async with asyncio.timeout(
                            60 if action == "connect" else self.settings.call_timeout
                        ):
                            if action == "connect":
                                self.verified.clear()
                                self.state = "connecting"
                                if session is None:
                                    session = await self._open(stack)
                                value = await self._refresh(session)
                            else:
                                self.assert_ready(spec)
                                result = await session.call_tool(
                                    "execute_tool", {"name": spec.name, "arguments": args}
                                )
                                if not hasattr(result, "is_error"):
                                    raise DomainError(
                                        "unsafe_output",
                                        "Interactive/extension results are not supported.",
                                        uncertain=True,
                                    )
                                value = ProviderOutcome(
                                    result.model_dump(mode="json", by_alias=True),
                                    "mcp_result",
                                    result.is_error,
                                )
                        if not future.done():
                            future.set_result(value)
                    except Exception as error:
                        self.failure_type = type(error).__name__
                        if not future.done():
                            future.set_exception(
                                error
                                if isinstance(error, DomainError)
                                else DomainError(
                                    "upstream_error",
                                    "Drishti metadata/execution failed; no automatic replay. Inspect allowance before retrying.",
                                    uncertain=action == "execute",
                                )
                            )
                        break
        except asyncio.CancelledError:
            raise
        except Exception:
            # Never expose SDK exception repr, headers, body or URLs.
            pass
        finally:
            self.state = "disconnected"
            self.verified.clear()
            if active and not active[3].done():
                active[3].set_exception(
                    DomainError(
                        "provider_unavailable", "Drishti connection closed.", uncertain=True
                    )
                )
            while not self._queue.empty():
                future = self._queue.get_nowait()[3]
                if not future.done():
                    future.set_exception(
                        DomainError(
                            "provider_unavailable", "Drishti connection closed before dispatch."
                        )
                    )

    async def close(self):
        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
