"""Atomic process-local admission. No claim to account-wide or observed billing."""

import asyncio
import time

from margin.core.contracts import DomainError


class Ledger:
    def __init__(self, request_limits: dict[str, int], credits: int, *, paced: bool = True):
        self.limits = request_limits
        self.requests = {p: 0 for p in request_limits}
        self.credit_limit = credits
        self.reserved_credits = 0
        self.completed_estimated_credits = 0
        self.uncertain_credits = 0
        self.logical_calls = {p: 0 for p in request_limits}
        self._lock = asyncio.Lock()
        self._pace_locks = {p: asyncio.Lock() for p in request_limits}
        self._last = {p: 0.0 for p in request_limits}
        self.paced = paced

    async def reserve(self, provider: str, credits: int):
        async with self._lock:
            if provider == "drishti" and self.requests[provider] >= max(
                0, self.limits[provider] - 2
            ):
                raise DomainError(
                    "request_budget",
                    "Drishti allowance is reserved for cleanup; start no more operations.",
                )
            if (
                self.reserved_credits + self.completed_estimated_credits + credits
                > self.credit_limit
            ):
                raise DomainError(
                    "credit_budget", "Local estimated credit allowance would be exceeded."
                )
            self.reserved_credits += credits
            self.logical_calls[provider] += 1

    async def settle(self, credits: int, *, dispatched: bool, uncertain: bool = False):
        async with self._lock:
            self.reserved_credits -= credits
            if dispatched:
                self.completed_estimated_credits += credits
                if uncertain:
                    self.uncertain_credits += credits

    async def http_attempt(self, provider: str, *, seconds: float | None = None):
        interval = seconds if seconds is not None else (60 / 9 if provider == "drishti" else 0.5)
        async with self._pace_locks[provider]:
            if self.paced:
                await asyncio.sleep(max(0, interval - (time.monotonic() - self._last[provider])))
            async with self._lock:
                if self.requests[provider] >= self.limits[provider]:
                    raise DomainError(
                        "request_budget", f"Local {provider} HTTP allowance exhausted."
                    )
                self.requests[provider] += 1
                self._last[provider] = time.monotonic()

    def snapshot(self) -> dict:
        return {
            "scope": "process; restarts reset counters, other clients are not accounted for",
            "http_attempts": dict(self.requests),
            "http_limits": dict(self.limits),
            "logical_calls": dict(self.logical_calls),
            "estimated_credit_limit": self.credit_limit,
            "reserved_credits": self.reserved_credits,
            "completed_estimated_credits": self.completed_estimated_credits,
            "uncertain_estimated_credits": self.uncertain_credits,
            "observed_account_balance": None,
        }
