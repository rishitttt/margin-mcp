import json
from urllib.parse import quote

import pytest

from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest
from margin.core.registry import Registry
from margin.evidence.sanitize import REDACTED, Sanitizer


@pytest.mark.parametrize(
    "operation,arguments",
    [
        ("drishti.execute_anything", {}),
        ("drishti.get_news", {"query": "all companies"}),
        (
            "drishti.get_news",
            {"query": {"symbols": ["SYNTHA"], "limit": "2", "page": 1, "lookback_days": 7}},
        ),
        (
            "drishti.get_news",
            {
                "query": {
                    "symbols": ["SYNTHA"],
                    "limit": 2,
                    "page": 1,
                    "lookback_days": 7,
                    "ignore_filters": True,
                }
            },
        ),
        (
            "drishti.get_news",
            {"query": {"symbols": ["NIFTY"], "limit": 2, "page": 1, "lookback_days": 7}},
        ),
        (
            "drishti.get_news",
            {"query": {"symbols": ["SYNTHA", "SYNTHB"], "limit": 2, "page": 1, "lookback_days": 7}},
        ),
        (
            "drishti.get_news",
            {
                "query": {
                    "symbols": ["SYNTHA"],
                    "limit": 2,
                    "page": 1,
                    "lookback_days": 7,
                    "from": "2026-01-01",
                }
            },
        ),
        ("drishti.get_news", {"query": {"ids": ["record1"], "symbols": ["SYNTHA"]}}),
        ("drishti.get_news", {"query": {"symbols": ["SYNTHA"], "limit": 2, "page": 1}}),
        ("drishti.get_earnings_filing", {}),
        (
            "drishti.get_earnings_filing",
            {"earnings_id": "rec", "symbol": "SYNTHA", "quarter": "q2_27"},
        ),
        (
            "bharatstock.get_financials",
            {
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "period_type": "annual",
                "page": 1,
                "page_size": 8,
            },
        ),
        (
            "bharatstock.get_stock_prices",
            {
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "page": 1,
                "page_size": 300,
                "from": "2024-01-01",
                "to": "2026-01-01",
            },
        ),
        (
            "bharatstock.get_stock_prices",
            {
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "page": 1,
                "page_size": 300,
                "from": "2026-02-30",
                "to": "2026-04-01",
            },
        ),
    ],
)
def test_broad_or_malformed_requests_are_rejected(operation, arguments):
    with pytest.raises(DomainError):
        Registry(Settings()).validate(OperationRequest(operation, arguments))


def test_price_and_earnings_discovery_are_not_subject_to_news_cap():
    registry = Registry(Settings())
    registry.validate(
        OperationRequest(
            "bharatstock.get_stock_prices",
            {
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "page": 1,
                "page_size": 300,
                "from": "2025-10-20",
                "to": "2026-10-20",
            },
        )
    )
    registry.validate(
        OperationRequest(
            "drishti.list_earnings",
            {"query": {"symbols": ["SYNTHA"], "lookback_days": 365, "page": 1, "limit": 2}},
        )
    )
    registry.validate(
        OperationRequest(
            "drishti.get_earnings_filing", {"earnings_id": "known-record-1", "detailed": True}
        )
    )


def test_live_mode_does_not_equate_key_presence_with_untested_access():
    registry = Registry(
        Settings(mode="live", bharatstock_key="fake-bharat-key", drishti_key="fake-drishti-key")
    )
    with pytest.raises(DomainError, match="untested"):
        registry.validate(
            OperationRequest(
                "drishti.get_news",
                {"query": {"symbols": ["RELIANCE"], "lookback_days": 7, "page": 1, "limit": 2}},
            )
        )
    with pytest.raises(DomainError, match="Fictional"):
        registry.validate(
            OperationRequest("bharatstock.get_stock_quote", {"ticker": "SYNTHA", "exchange": "NSE"})
        )
    registry.validate(
        OperationRequest("bharatstock.get_stock_quote", {"ticker": "RELIANCE", "exchange": "NSE"})
    )


def test_known_secret_and_private_url_redaction_covers_all_surfaces():
    secret = "a-private-test-credential-987654321"
    url = "https://developers.manasija.in/v1/earnings/citations/record/pdf?api_key=" + secret
    source = {
        "content": [{"type": "text", "text": json.dumps({"citation": url, "error": secret})}],
        "structuredContent": {"api_key": secret, "url": url},
        "meta": {"error": quote(quote(secret, safe=""), safe="")},
    }
    sanitizer = Sanitizer([secret])
    clean = sanitizer.clean(source)
    wire = json.dumps(clean)
    assert secret not in wire and "api_key=" not in wire
    assert clean["structuredContent"]["api_key"] == REDACTED
    citations = sanitizer.citations(source, clean)
    assert citations and all(c["requires_resolution"] for c in citations)
    assert secret not in json.dumps(citations)


@pytest.mark.parametrize(
    "url",
    [
        "https://host.invalid/file?api%255fkey=unknown-sensitive-value",
        "https://user:password@host.invalid/file",
        "https://host.invalid/file?X-Amz-Signature=unknown-sensitive-value&Expires=999",
    ],
)
def test_unknown_query_credentials_and_url_userinfo_are_removed(url):
    safe, private = Sanitizer().url(url)
    assert private and "?" not in safe and "@" not in safe


def test_secret_in_path_is_not_reintroduced_by_citation_creation():
    s = Sanitizer(["private-path-value"])
    payload = {"url": "https://example.invalid/private-path-value/file.pdf"}
    assert "private-path-value" not in json.dumps(s.clean(payload))
    assert "private-path-value" not in json.dumps(s.citations(payload, s.clean(payload)))


def test_opaque_binary_is_withheld():
    with pytest.raises(DomainError, match="binary"):
        Sanitizer().clean({"content": [{"type": "image", "data": "base64blob"}]})
