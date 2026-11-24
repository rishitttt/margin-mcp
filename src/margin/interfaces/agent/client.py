"""Thin synchronous local HTTP client; no upstream credentials or provider clients."""

from __future__ import annotations

import hashlib
import json
import re
import time
from urllib.parse import urlsplit

import httpx

from margin.evidence.sanitize import Sanitizer

MAX_RESPONSE_BYTES = 4 * 1024 * 1024
ACTIVE = {"queued", "running"}


class BridgeError(Exception):
    def __init__(self, code, message, *, uncertain=False):
        self.code, self.message, self.uncertain = code, message, uncertain
        super().__init__(message)


def local_url(value):
    try:
        p = urlsplit(value)
        valid = (
            p.scheme == "http"
            and p.hostname in {"127.0.0.1", "localhost"}
            and not p.username
            and not p.password
            and p.path in {"", "/"}
            and not p.query
            and not p.fragment
            and (p.port is None or 1 <= p.port <= 65535)
        )
    except ValueError:
        valid = False
    if not valid:
        raise BridgeError(
            "invalid_url", "Use a loopback HTTP origin without credentials or a path."
        )
    return value.rstrip("/")


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise BridgeError("invalid_input", "Use a bounded run, operation or plan identifier.")
    return value


class AgentClient:
    def __init__(self, url="http://127.0.0.1:8765", *, http=None, expect_mode=None):
        self.url = local_url(url)
        self.http = http or httpx.Client(
            timeout=httpx.Timeout(60, connect=5), trust_env=False, follow_redirects=False
        )
        self.owns_http = http is None
        self.expect_mode = expect_mode
        self.backend_id = None
        self.mode = None
        self.nonce = None

    def close(self):
        if self.owns_http:
            self.http.close()

    def _request(self, method, path, body=None, params=None, *, may_spend=False):
        headers = {"X-Margin-Action": self.nonce} if method == "POST" else {}
        try:
            with self.http.stream(
                method, self.url + path, json=body, params=params, headers=headers
            ) as response:
                raw = bytearray()
                for chunk in response.iter_bytes():
                    raw.extend(chunk)
                    if len(raw) > MAX_RESPONSE_BYTES:
                        raise BridgeError(
                            "response_size",
                            "Local response exceeds 4 MiB; no retry was made.",
                            uncertain=may_spend,
                        )
                try:
                    data = json.loads(raw)
                except (ValueError, RecursionError):
                    raise BridgeError(
                        "invalid_response",
                        "Backend returned invalid JSON; no retry was made.",
                        uncertain=may_spend,
                    ) from None
                if not response.is_success:
                    error = data.get("error", {}) if isinstance(data, dict) else {}
                    raise BridgeError(
                        error.get("code", "http_error"),
                        error.get("message", "Local backend rejected the request."),
                        uncertain=may_spend and response.status_code >= 500,
                    )
                if not isinstance(data, dict):
                    raise BridgeError("invalid_response", "Expected a JSON object from Margin.")
                return data
        except httpx.HTTPError:
            raise BridgeError(
                "connection",
                "Cannot complete the local backend request. No automatic retry was made.",
                uncertain=may_spend,
            ) from None

    def status(self):
        data = self._request("GET", "/api/status")
        nonce = data.pop("action_nonce", None)
        if not isinstance(nonce, str) or not nonce or data.get("mode") not in {"live", "synthetic"}:
            raise BridgeError(
                "invalid_response", "This endpoint is not a supported Margin backend."
            )
        self.nonce = nonce
        self.backend_id = hashlib.sha256(nonce.encode()).hexdigest()[:24]
        self.mode = data["mode"]
        if self.expect_mode and self.mode != self.expect_mode:
            raise BridgeError(
                "mode_mismatch", "Backend mode differs from the explicitly required mode."
            )
        return data

    def envelope(self, data):
        return {
            "bridge_version": "1.0",
            "backend_id": self.backend_id,
            "mode": self.mode,
            "data": data,
        }

    def catalog(self, name=None):
        endpoints = {
            "retrieval": ("/api/capabilities", "operations"),
            "calculations": ("/api/analysis/functions", "functions"),
            "company_functions": ("/api/analysis/company-functions", "functions"),
        }
        groups = {
            key: self._request("GET", route)[field] for key, (route, field) in endpoints.items()
        }
        if name:
            groups = {
                key: [v for v in values if name in (v.get("operation") or v.get("function") or "")]
                for key, values in groups.items()
            }
            if not any(groups.values()):
                raise BridgeError("unknown_function", "No catalog entry matches that name.")
        else:
            groups = {
                key: [
                    {k: v for k, v in item.items() if k not in {"schema", "planning_schema"}}
                    for item in values
                ]
                for key, values in groups.items()
            }
        return groups

    def workflows(self, name=None):
        entries = self._request("GET", "/api/protocols")["functions"]
        if name:
            entries = [item for item in entries if name in item["function"]]
            if not entries:
                raise BridgeError("unknown_function", "No review function matches that name.")
        return {"functions": entries}

    def review(self, body):
        return self._request("POST", "/api/protocols/invoke", body)

    def review_sources(self, run_id, operation_id, issuer):
        return self._request(
            "POST",
            "/api/protocols/import-source",
            {
                "run_id": identifier(run_id),
                "operation_id": identifier(operation_id),
                "issuer": issuer,
            },
        )

    def preview(self, body, *, company=False):
        return self._request("POST", "/api/analysis/plans" if company else "/api/plans", body)

    def run(self, plan_id, key, backend_id):
        if backend_id != self.backend_id:
            raise BridgeError(
                "backend_changed",
                "Backend restarted or differs from the preview. Reconcile allowance and preview again.",
            )
        return self._request(
            "POST",
            "/api/runs",
            {"plan_id": identifier(plan_id), "idempotency_key": key},
            may_spend=True,
        )

    def run_status(self, run_id):
        return self._request("GET", f"/api/runs/{identifier(run_id)}")

    def wait(self, run_id, seconds):
        deadline = time.monotonic() + seconds
        while True:
            data = self.run_status(run_id)
            if data["status"] not in ACTIVE or time.monotonic() >= deadline:
                return data
            time.sleep(min(0.2, max(0, deadline - time.monotonic())))

    def result(self, run_id, operation_id, *, facts=False, money_unit=None):
        path = f"/api/runs/{identifier(run_id)}/operations/{identifier(operation_id)}"
        return self._request(
            "GET",
            path + ("/facts" if facts else ""),
            params={"money_unit": money_unit} if facts and money_unit else None,
        )

    def sources(self):
        return self._request("GET", "/api/analysis/sources")

    def runs(self):
        return self._request("GET", "/api/runs")

    def cancel(self, run_id):
        return self._request("POST", f"/api/runs/{identifier(run_id)}/cancel", {}, may_spend=True)

    def connect(self):
        return self._request("POST", "/api/provider-connections/drishti", {}, may_spend=True)


def public_output(value):
    """Defense in depth; configured secrets are removed at the backend boundary."""
    return Sanitizer().clean(value)
