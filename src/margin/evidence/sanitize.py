"""One redaction path for provider metadata, results and diagnostics."""

from __future__ import annotations

import json
import re
from urllib.parse import parse_qsl, unquote, urlsplit, urlunsplit

from margin.core.contracts import DomainError

PRIVATE = re.compile(
    r"^(api[_-]?key|key|token|access[_-]?token|authorization|password|secret|sig(nature)?|x-amz-.+|x-goog-.+|awsaccesskeyid|policy|key-pair-id|credential)$",
    re.I,
)
URL = re.compile(r"https?://[^\s\"'<>\\]+", re.I)
REDACTED = "[REDACTED]"
SYNTHETIC_KEY = "synthetic-private-key-never-forward"


class Sanitizer:
    def __init__(self, secrets=()):
        self.secrets = tuple(s for s in (*secrets, SYNTHETIC_KEY) if s)

    def url(self, value: str) -> tuple[str, bool]:
        try:
            p = urlsplit(value)
            if p.scheme not in {"https", "http"} or not p.hostname:
                raise ValueError
            # A locator with credentials/signatures is not a working public citation.
            decoded = value
            decoded_query = p.query
            for _ in range(3):
                decoded = unquote(decoded)
                decoded_query = unquote(decoded_query)
            private = bool(p.username or p.password) or any(
                PRIVATE.match(k) for k, _ in parse_qsl(decoded_query)
            )
            private |= any(s in decoded for s in self.secrets)
            host = p.hostname
            if ":" in host:
                host = f"[{host}]"
            if p.port:
                host += f":{p.port}"
            safe = urlunsplit((p.scheme, host, p.path, "" if private else p.query, ""))
            if any(s in unquote(safe) for s in self.secrets):
                return REDACTED, True
            return safe, private
        except ValueError:
            return REDACTED, True

    def clean(self, value):
        if isinstance(value, dict):
            if value.get("type") in {"image", "audio", "resource"}:
                raise DomainError(
                    "unsafe_output",
                    "Embedded binary/resource output is not supported in this slice.",
                )
            out = {}
            for key, item in value.items():
                safe_key = self.text(str(key))
                out[safe_key] = REDACTED if PRIVATE.match(str(key)) else self.clean(item)
            return out
        if isinstance(value, list):
            return [self.clean(v) for v in value]
        if isinstance(value, str):
            return self.text(value)
        if value is None or isinstance(value, (bool, int, float)):
            return value
        raise DomainError("unsafe_output", "Non-JSON provider output was withheld.")

    def text(self, value: str) -> str:
        # Native MCP often embeds the same structured JSON in a text block.
        if value.lstrip().startswith(("{", "[")):
            try:
                obj = json.loads(value)
                if isinstance(obj, (dict, list)):
                    return json.dumps(self.clean(obj), ensure_ascii=False, allow_nan=False)
            except (ValueError, RecursionError):
                pass
        decoded = value
        for _ in range(3):
            decoded = unquote(decoded)
        if any(s in decoded for s in self.secrets):
            value = decoded
        value = URL.sub(lambda m: self.url(m.group(0))[0], value)
        value = re.sub(
            r"(?i)(api[_-]?key|access[_-]?token|authorization|password|secret)\s*[:=]\s*[^\s,;]+",
            lambda m: m[1] + "=" + REDACTED,
            value,
        )
        for secret in self.secrets:
            value = value.replace(secret, REDACTED)
        return value

    def citations(self, original, safe) -> list[dict]:
        found = {}

        def visit(item):
            if isinstance(item, dict):
                for v in item.values():
                    visit(v)
            elif isinstance(item, list):
                for v in item:
                    visit(v)
            elif isinstance(item, str):
                for match in URL.finditer(item):
                    url, private = self.url(match.group())
                    if url == REDACTED:
                        continue
                    requires = private or "developers.manasija.in" == urlsplit(url).hostname
                    old = found.get(url, {})
                    requires |= old.get("requires_resolution", False)
                    found[url] = {
                        "locator": url,
                        "requires_resolution": requires,
                        "evidence_level": "source_locator",
                        "verified": False,
                    }

        visit(original)
        return list(found.values())[:30]
