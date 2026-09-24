from datetime import date

import pytest
from pydantic import ValidationError

from margin_mcp.storage import MarginError

COMPANY = "demo-aarya-software"


@pytest.mark.parametrize("query", ["demoaaryasw", "  AARYA Software  ", "DEMO001"])
def test_lookup_resolves_names_and_listing_identifiers(service, query):
    result = service.lookup_company(query)
    assert result.status == "matched"
    assert result.candidates[0].company.company_id == COMPANY
    assert result.meta.data_kind == "synthetic"
    assert "SYNTHETIC" in result.meta.warnings[0]


def test_ambiguity_survives_truncation_and_exchange_can_disambiguate(service):
    result = service.lookup_company("Aarya", limit=1)
    assert result.status == "ambiguous"
    assert result.total_matches == 2
    assert len(result.candidates) == 1
    assert result.truncated
    narrowed = service.lookup_company("Aarya", exchange="NSE")
    assert narrowed.status == "matched"
    assert narrowed.candidates[0].company.company_id == COMPANY
    assert service.lookup_company("DEMO002", exchange="NSE").status == "not_found"


def test_partial_names_and_missing_matches(service):
    result = service.lookup_company("software")
    assert result.candidates[0].match_kind == "partial"
    assert service.lookup_company("Nonexistent Corporation").candidates == []
    with pytest.raises(MarginError, match="INVALID_QUERY"):
        service.lookup_company("  %_  ")


@pytest.mark.parametrize("limit", [0, 101, True, "10"])
def test_invalid_limits_cannot_bypass_service_validation(service, limit):
    with pytest.raises(ValidationError):
        service.lookup_company("Aarya", limit=limit)


def test_coverage_distinguishes_no_filings_from_unknown_company(service):
    result = service.get_coverage("demo-deccan-products")
    assert result.total_filings == 0
    assert result.companies[0].period_ends == []
    assert result.companies[0].latest_publication_in_corpus is None
    with pytest.raises(MarginError, match="COMPANY_NOT_FOUND"):
        service.get_coverage("unknown")
    overall = service.get_coverage()
    assert overall.total_companies == 3
    assert overall.total_filings == 5
    assert overall.meta.metadata_only


def test_filters_preserve_basis_and_use_publication_not_reporting_dates(service):
    result = service.list_filings(
        COMPANY, document_type="financial_results", reporting_basis="consolidated"
    )
    assert [f.filing_id for f in result.filings] == [
        "demo-aarya-fy26-q2-consolidated",
        "demo-aarya-fy26-q1-consolidated",
    ]
    same_day = service.list_filings(
        COMPANY, published_from=date(2025, 10, 20), published_to=date(2025, 10, 20)
    )
    assert same_day.total_matches == 2
    at_period_end = service.list_filings(COMPANY, published_to=date(2025, 9, 30))
    assert all(f.period_end != date(2025, 9, 30) for f in at_period_end.filings)
    assert service.list_filings(COMPANY, document_type="shareholding_pattern").total_matches == 0


def test_invalid_date_range_and_unknown_company_fail(service):
    with pytest.raises(MarginError, match="INVALID_DATE_RANGE"):
        service.list_filings(
            COMPANY, published_from=date(2026, 1, 1), published_to=date(2025, 1, 1)
        )
    with pytest.raises(MarginError, match="COMPANY_NOT_FOUND"):
        service.list_filings("unknown")


def test_pagination_is_stable_complete_and_revision_checked(service, store, corpus):
    first = service.list_filings(COMPANY, limit=1)
    ids = [first.filings[0].filing_id]
    offset = first.next_offset
    while offset is not None:
        page = service.list_filings(
            COMPANY, limit=1, offset=offset, corpus_revision=first.meta.corpus_revision
        )
        ids.extend(f.filing_id for f in page.filings)
        offset = page.next_offset
    assert len(ids) == len(set(ids)) == 4
    assert ids[:2] == ["demo-aarya-fy26-q2-consolidated", "demo-aarya-fy26-q2-standalone"]
    with pytest.raises(MarginError, match="REVISION_REQUIRED"):
        service.list_filings(COMPANY, offset=1)
    store.import_corpus(corpus.model_copy(update={"title": "New snapshot"}), replace=True)
    with pytest.raises(MarginError, match="CORPUS_CHANGED"):
        service.list_filings(COMPANY, offset=1, corpus_revision=first.meta.corpus_revision)


def test_coverage_pagination_reports_totals_for_whole_selection(service):
    first = service.get_coverage(limit=2)
    second = service.get_coverage(
        limit=2, offset=first.next_offset, corpus_revision=first.meta.corpus_revision
    )
    assert first.total_companies == second.total_companies == 3
    assert second.companies[0].company_id == "demo-deccan-products"
    assert second.next_offset is None


def test_filing_metadata_never_claims_document_content(service):
    result = service.get_filing("demo-aarya-fy26-q2-consolidated")
    assert result.content_available is False
    assert result.content_status == "metadata_only"
    assert result.filing.source_url is None
    with pytest.raises(MarginError, match="FILING_NOT_FOUND"):
        service.get_filing("missing")
