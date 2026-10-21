"""Core records contain ordinary data, never web or MCP server response objects."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def now() -> str:
    return datetime.now(UTC).isoformat()


def encoded_size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, allow_nan=False).encode())


class DomainError(Exception):
    def __init__(self, code: str, message: str, *, uncertain: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.uncertain = uncertain


@dataclass(frozen=True)
class OperationRequest:
    operation: str
    arguments: dict[str, Any]


@dataclass
class ProviderOutcome:
    payload: Any
    kind: str
    is_error: bool = False
    http_status: int | None = None


@dataclass
class OperationResult:
    operation_id: str
    operation: str
    provider: str
    mode: str
    status: str
    payload: Any = None
    payload_kind: str | None = None
    warnings: list[str] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    receipt: dict = field(default_factory=dict)
    error: dict | None = None
