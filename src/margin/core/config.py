from __future__ import annotations

import os
from dataclasses import dataclass, field

from margin.core.contracts import DomainError


@dataclass(frozen=True)
class Settings:
    mode: str = "synthetic"
    bharatstock_key: str = field(default="", repr=False)
    drishti_key: str = field(default="", repr=False)
    enabled_unverified: frozenset[str] = frozenset()
    bharatstock_requests: int = 20
    drishti_requests: int = 30
    drishti_credits: int = 20
    call_timeout: float = 45
    queue_timeout: float = 30
    metadata_ttl: float = 300
    result_ttl: float = 1800
    max_result_bytes: int = 2 * 1024 * 1024
    max_buffer_bytes: int = 20 * 1024 * 1024
    max_records: int = 200
    max_payload_runs: int = 5
    # Deterministic synthetic faults, never accepted from a live request.
    synthetic_fault: str = "none"
    synthetic_delay: float = 0.02

    def __post_init__(self):
        if self.mode not in {"synthetic", "live"}:
            raise DomainError("invalid_config", "MARGIN_MODE must be synthetic or live.")
        if self.synthetic_fault not in {
            "none",
            "drishti_unavailable",
            "empty_news",
            "unsafe_output",
        }:
            raise DomainError("invalid_config", "Unknown synthetic scenario.")
        if self.mode == "live" and self.synthetic_fault != "none":
            raise DomainError("invalid_config", "Synthetic faults cannot be used in live mode.")
        if min(self.bharatstock_requests, self.drishti_requests, self.drishti_credits) < 0:
            raise DomainError("invalid_config", "Allowances must be nonnegative.")

    @classmethod
    def from_env(cls) -> Settings:
        # Deliberately no .env or historical credential-text-file auto-loading.
        try:
            return cls(
                mode=os.getenv("MARGIN_MODE", "synthetic"),
                bharatstock_key=os.getenv("BHARATSTOCK_API_KEY", ""),
                drishti_key=os.getenv("DRISHTI_API_KEY", ""),
                enabled_unverified=frozenset(
                    filter(None, os.getenv("MARGIN_ENABLE_OPERATIONS", "").split(","))
                ),
                bharatstock_requests=int(os.getenv("MARGIN_BHARATSTOCK_REQUESTS", "20")),
                drishti_requests=int(os.getenv("MARGIN_DRISHTI_REQUESTS", "30")),
                drishti_credits=int(os.getenv("MARGIN_DRISHTI_CREDITS", "20")),
                synthetic_fault=os.getenv("MARGIN_SYNTHETIC_SCENARIO", "none"),
            )
        except ValueError:
            raise DomainError(
                "invalid_config", "Request/credit allowances must be integers."
            ) from None
