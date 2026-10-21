"""Fictional, clearly labelled fixture data. No licensed provider payloads."""

import asyncio
from datetime import date, timedelta

import httpx

from margin.core.contracts import DomainError, ProviderOutcome
from margin.evidence.sanitize import SYNTHETIC_KEY

COMPANIES = [
    {
        "symbol": "SYNTHA",
        "company_name": "Fixture Industries",
        "exchange": "NSE",
        "isin": "SYNTHETIC001",
    },
    {
        "symbol": "SYNTHB",
        "company_name": "Example Software",
        "exchange": "BSE",
        "isin": "SYNTHETIC002",
    },
]
AS_OF = "2026-10-15"


def paged(rows, page, size):
    selected = rows[(page - 1) * size : page * size]
    return {
        "data": selected,
        "pagination": {
            "page": page,
            "page_size": size,
            "total_items": len(rows),
            "total_pages": (len(rows) + size - 1) // size,
        },
    }


def bharatstock_fixture(request: httpx.Request) -> httpx.Response:
    params = dict(request.url.params)
    path = request.url.path
    if path == "/v1/search":
        q = params.get("q", "").lower()
        return httpx.Response(
            200,
            json=[c for c in COMPANIES if q in (c["symbol"] + c["company_name"]).lower()][
                : int(params.get("limit", 5))
            ],
        )
    parts = path.split("/")
    company = next((c for c in COMPANIES if c["symbol"] == parts[3]), None)
    if company is None or params.get("exchange", company["exchange"]) != company["exchange"]:
        return httpx.Response(404, json={"detail": "Fictional listing not found"})
    symbol = company["symbol"]
    if len(parts) == 4:
        payload = company | {
            "sector": "Synthetic development fixtures",
            "market_cap": 1_420_000_000,
            "metrics": {"market_cap": 142, "pe_ratio": 18.2},
            "latest_price": {"trade_date": AS_OF, "close": 284, "volume": 12000},
        }
    elif parts[4] == "ratios":
        payload = {
            "symbol": symbol,
            "as_of_date": AS_OF,
            "market_cap": 1_420_000_000,
            "pe_ratio": 18.2,
            "roe": 12.1,
            "eps": 15.6,
            "reported_unit": "synthetic values only",
        }
    elif parts[4] == "financials":
        annual = params.get("period_type") == "annual"
        rows = [
            {
                "symbol": symbol,
                "period_end_date": end,
                "fiscal_year": "2026-27" if end >= "2026-04-01" else "2025-26",
                "quarter": None
                if annual
                else "Q1"
                if end.endswith("06-30")
                else "Q4"
                if end.endswith("03-31")
                else "Q3",
                "period_type": "annual" if annual else "quarterly",
                "consolidation_type": "consolidated",
                "revenue": revenue,
                "net_profit": profit,
                "eps": eps,
                "cash_flow_operating": 140_000_000 if annual else None,
                "reported_unit": "INR (fictional fixture only)",
            }
            for end, revenue, profit, eps in (
                [
                    ("2026-03-31", 1_280_000_000, 97_000_000, 19.4),
                    ("2025-03-31", 1_110_000_000, 82_000_000, 16.4),
                ]
                if annual
                else [
                    ("2026-06-30", 310_000_000, 24_000_000, 4.8),
                    ("2026-03-31", 300_000_000, 22_000_000, 4.4),
                    ("2025-12-31", 290_000_000, 21_000_000, 4.2),
                ]
            )
        ]
        payload = paged(rows, int(params.get("page", 1)), int(params.get("page_size", 2)))
    elif parts[4] == "prices":
        start = date.fromisoformat(params["from"])
        end = min(date.fromisoformat(params["to"]), date.fromisoformat(AS_OF))
        rows = []
        for i in range((end - start).days + 1):
            day = start + timedelta(days=i)
            if day.weekday() < 5:
                price = round(240 + i * 0.3 + (i % 7) * 1.5, 2)
                rows.append(
                    {
                        "trade_date": day.isoformat(),
                        "open": price - 1,
                        "high": price + 3,
                        "low": price - 2,
                        "close": price,
                        "adjusted_close": price,
                        "volume": 10000 + i * 51,
                    }
                )
        payload = paged(list(reversed(rows)), int(params["page"]), int(params["page_size"]))
    elif parts[4] == "corporate-actions":
        rows = [
            {
                "symbol": symbol,
                "action_type": "dividend",
                "ex_date": "2026-09-01",
                "subject": "Fictional dividend",
                "amount_per_share": 2,
            }
        ]
        rows = [
            r
            for r in rows
            if not params.get("action_type") or r["action_type"] == params["action_type"]
        ]
        payload = paged(rows, int(params["page"]), int(params["page_size"]))
    else:
        return httpx.Response(404)
    return httpx.Response(200, json=payload)


def drishti_payload(name: str, args: dict):
    q = args.get("query", {})
    value = args.get("symbol") or q.get("symbols") or "SYNTHA"
    symbol = value[0] if isinstance(value, list) else value
    if name == "resolve_symbols":
        return {"matches": COMPANIES[:1]}
    if name == "get_symbols":
        return {
            "data": [c | {"scrip_code": "SYNTH001"} for c in COMPANIES if c["symbol"] == symbol]
        }
    if name == "get_announcement_categories":
        return {"categories": ["financial_results", "business_update"]}
    if name == "get_news":
        return {
            "data": [
                {
                    "id": "synth-news-1",
                    "symbol": symbol,
                    "published_at": "2026-10-15T08:00:00+00:00",
                    "headline": "Fictional company announces capacity project",
                    "sentiment": "positive",
                    "summary": "Synthetic news tone, not a measure of investor sentiment.",
                    "url": "https://example.invalid/fictional-news",
                }
            ]
        }
    if name == "get_announcements":
        return {
            "data": [
                {
                    "id": "synth-ann-1",
                    "symbol": symbol,
                    "date": "2026-10-14T09:00:00+00:00",
                    "headline": "Fictional operational update",
                    "category": "business_update",
                    "summary": "Synthetic provider summary. Date denotes ingestion.",
                }
            ]
        }
    if name == "list_earnings":
        return {
            "data": [
                {
                    "earnings_id": "synth-earnings-1",
                    "symbol": symbol,
                    "quarter": "q2_27",
                    "date": "2026-10-15T12:00:00+00:00",
                    "headline": "Fictional Q2 results",
                }
            ]
        }
    if name == "get_earnings_filing":
        return {
            "earnings_id": args.get("earnings_id", "synth-earnings-1"),
            "symbol": symbol,
            "quarter": args.get("quarter", "q2_27"),
            "date": "2026-10-15T12:00:00",
            "consolidated": {
                "revenue": 32,
                "revenue_from_operations_raw": {"current_period_value": 35},
                "profit_after_tax": 3,
                "eps": None,
                "reported_unit": "Rs crore (fictional fixture only)",
            },
            "citation_url": "https://developers.manasija.in/v1/earnings/citations/synth-earnings-1/pdf?api_key="
            + SYNTHETIC_KEY,
            "page_citation_url": "https://developers.manasija.in/v1/earnings/citations/synth-earnings-1/page/9?api_key="
            + SYNTHETIC_KEY,
        }
    raise DomainError("unknown_operation", "No fixture for this operation.")


class SyntheticDrishti:
    def __init__(self, ledger, settings):
        self.ledger = ledger
        self.settings = settings
        self.state = "synthetic"

    def status(self):
        return {
            "state": self.state,
            "metadata": "reviewed local fixture contracts",
            "live_access_verified": False,
        }

    def assert_ready(self, _):
        return None

    async def connect(self):
        return self.status()

    async def execute(self, spec, arguments):
        await self.ledger.http_attempt("drishti")
        await asyncio.sleep(self.settings.synthetic_delay)
        if self.settings.synthetic_fault == "drishti_unavailable":
            raise DomainError("provider_unavailable", "Synthetic scenario: Drishti unavailable.")
        if self.settings.synthetic_fault == "unsafe_output":
            return ProviderOutcome({"content": [{"type": "image", "data": "opaque"}]}, "mcp_result")
        payload = drishti_payload(spec.name, arguments)
        if self.settings.synthetic_fault == "empty_news" and spec.name == "get_news":
            payload = {"data": []}
        import json

        return ProviderOutcome(
            {
                "content": [{"type": "text", "text": json.dumps(payload)}],
                "structuredContent": payload,
                "isError": False,
            },
            "mcp_result",
        )

    async def close(self):
        pass
