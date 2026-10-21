from urllib.parse import quote

import httpx

from margin.core.contracts import DomainError, ProviderOutcome
from margin.policy.ledger import Ledger


class BharatStockAdapter:
    def __init__(self, ledger: Ledger, key: str, *, transport=None, max_bytes=2 * 1024 * 1024):
        self.ledger = ledger
        self.max_bytes = max_bytes
        self.client = httpx.AsyncClient(
            base_url="https://bharatstockapi.com",
            headers={"X-API-Key": key},
            timeout=httpx.Timeout(45, connect=15),
            follow_redirects=False,
            trust_env=False,
            transport=transport if transport is not None else httpx.AsyncHTTPTransport(retries=0),
        )

    async def execute(self, spec, arguments):
        params = {k: v for k, v in arguments.items() if k != "ticker"}
        path = spec.path.replace("{ticker}", quote(arguments.get("ticker", ""), safe=""))
        await self.ledger.http_attempt("bharatstock")
        try:
            async with self.client.stream("GET", path, params=params) as response:
                if not 200 <= response.status_code < 300:
                    code = {
                        401: "invalid_credentials",
                        403: "forbidden_product",
                        404: "not_found",
                        429: "rate_limit",
                    }.get(response.status_code, "upstream_error")
                    raise DomainError(
                        code,
                        f"BharatStock returned HTTP {response.status_code}; no automatic retry.",
                    )
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > self.max_bytes:
                        raise DomainError(
                            "oversize_output",
                            "BharatStock response exceeded the byte bound.",
                            uncertain=True,
                        )
                import json

                payload = json.loads(chunks)
                return ProviderOutcome(payload, "rest_json", http_status=response.status_code)
        except DomainError:
            raise
        except (httpx.HTTPError, ValueError):
            raise DomainError(
                "upstream_error",
                "BharatStock request failed; outcome/billing may be uncertain.",
                uncertain=True,
            ) from None

    async def close(self):
        await self.client.aclose()
