"""Invented source shapes regress real import failures; no live data/ground truth."""

import copy

import pytest

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.evidence.review_sources import project_sources
from margin.interfaces.mcp.server import MarginMCP


def record(operation="drishti.get_earnings_filing", data=None):
    return {
        "operation": operation,
        "status": "success",
        "mode": "synthetic",
        "payload_kind": "rest_json",
        "payload": {
            "data": data
            if data is not None
            else {
                "symbol": "EXAMPLE",
                "quarter": "q2_27",
                "date": "2026-11-20T10:00:00+00:00",
                "summary": "Example demand improved; operating profit increased.",
                "attachment_url": "https://example.invalid/report.pdf",
            }
        },
        "receipt": {"arguments": {}},
    }


@pytest.mark.parametrize(
    "operation,object_shape",
    [
        ("drishti.get_news", False),
        ("drishti.get_announcements", False),
        ("drishti.list_earnings", False),
        ("drishti.get_earnings_filing", True),
    ],
)
async def test_import_four_reviewed_shapes_through_mcp_without_fetch(
    monkeypatch, operation, object_shape
):
    result = record(operation)
    row = result["payload"]["data"]
    result["citations"] = [{"locator": row["attachment_url"], "requires_resolution": True}]
    if operation.endswith("get_news"):
        row["link"] = row.pop("attachment_url")
        row["symbol"] = "OTHER:EXAMPLE"
    if not object_shape:
        result["payload"]["data"] = [row]
    service = ResearchService(Settings())
    monkeypatch.setattr(service, "get_result", lambda *args: copy.deepcopy(result))
    before = service.ledger.snapshot()
    try:
        response = await MarginMCP(service).call(
            "margin_review_sources",
            {"run_id": "test-run", "operation_id": "test-op", "issuer": "NSE:EXAMPLE"},
        )
        assert not response.is_error
        imported = response.structured_content["data"]
        source = imported["sources"][0]
        assert source["origin"] == "retained_provider"
        assert source["kind"] == "provider_summary"
        assert source["date_kind"] == "unknown"
        assert not source["original_document_verified"]
        assert source["requires_resolution"]
        root = "data" if object_shape else "data[0]"
        assert source["passages"][0]["locator"] == f"{root}.summary"
        assert source["provenance"]["row_path"] == root
        assert "EXAMPLE" in source["provenance"]["reported_symbols"]
        assert source["provenance"]["text_scope"] == "provider_summary_not_attachment_contents"
        assert service.ledger.snapshot() == before
    finally:
        await service.close()


@pytest.mark.parametrize(
    "operation,data,reason",
    [
        ("drishti.get_symbols", [{}], "unsupported_operation"),
        ("drishti.get_news", {}, "unsupported_shape"),
        ("drishti.get_earnings_filing", [], "unsupported_shape"),
        (
            "drishti.get_earnings_filing",
            {"symbol": "OTHER"},
            "row_identity_unresolved_or_mismatched",
        ),
        ("drishti.get_earnings_filing", {}, "row_identity_unresolved_or_mismatched"),
        ("drishti.get_earnings_filing", {"symbol": "EXAMPLE:" * 21}, "unsupported_row_identity"),
        ("drishti.get_announcements", ["unexpected"], "unsupported_row"),
        ("drishti.get_announcements", [{"symbol": "EXAMPLE"}], "missing_supported_locator"),
    ],
)
def test_unknown_shapes_and_wrong_entities_are_explicit_holds(operation, data, reason):
    sources, provenance, skipped = project_sources(record(operation, data), "NSE:EXAMPLE")
    assert sources == provenance == []
    assert skipped[0]["reason"] == reason


async def test_protected_locator_no_original_text_and_atomic_invalid_mapping(monkeypatch):
    service = ResearchService(Settings(drishti_key="fixture-secret"))
    result = record()
    row = result["payload"]["data"]
    row.pop("attachment_url")
    row.pop("summary")
    row["citation_url"] = "https://developers.manasija.in/filing?api_key=fixture-secret"
    monkeypatch.setattr(service, "get_result", lambda *args: copy.deepcopy(result))
    try:
        imported = service.import_review_sources("run", "op", "NSE:EXAMPLE")
        source = imported["sources"][0]
        assert source["kind"] == "source_locator" and source["passages"] == []
        assert source["requires_resolution"]
        assert "fixture-secret" not in str(imported)
        assert "api_key" not in source["url"]
        before = copy.deepcopy(service.reviews.sources)
        result["operation"] = "drishti.get_announcements"
        result["payload"]["data"] = [
            row,
            row | {"citation_url": "https://example.invalid/logo.svg"},
        ]
        with pytest.raises(DomainError, match="Decorative"):
            service.import_review_sources("run", "op", "NSE:EXAMPLE")
        assert service.reviews.sources == before
    finally:
        await service.close()


def test_unknown_date_empty_text_and_mixed_company_rows_keep_limitations():
    row = record()["payload"]["data"]
    result = record(
        "drishti.get_announcements",
        [row | {"symbol": "OTHER"}, row | {"date": "not-a-date", "summary": " "}],
    )
    sources, provenance, skipped = project_sources(result, "NSE:EXAMPLE")
    assert len(sources) == 1 and skipped[0]["path"] == "data[0]"
    assert sources[0]["date"] is None and sources[0]["date_kind"] == "unknown"
    assert sources[0]["kind"] == "source_locator"
    assert provenance[0]["row_path"] == "data[1]"


def test_earnings_citation_pdf_fallback_does_not_mistake_page_metadata_for_text():
    result = record()
    row = result["payload"]["data"]
    row.pop("attachment_url")
    row["citation_urls"] = {
        "pdf": "https://developers.manasija.in/v1/citations/open",
        "pages": [{"page": 18, "url": "https://example.invalid/page"}],
    }
    sources, provenance, skipped = project_sources(result, "NSE:EXAMPLE")
    assert not skipped
    assert sources[0]["url"] == row["citation_urls"]["pdf"]
    assert provenance[0]["url_path"] == "data.citation_urls.pdf"
    assert len(sources[0]["passages"]) == 1
    assert sources[0]["passages"][0]["locator"] == "data.summary"
