"""Small-corpus operations, independent of MCP and any language model."""

from datetime import date
from typing import Annotated

from pydantic import Field, validate_call

from margin_mcp.models import (
    Company,
    CompanyCoverage,
    CompanyMatch,
    CoverageResult,
    DocumentType,
    Exchange,
    FilingListResult,
    FilingResult,
    Identifier,
    Limit,
    LookupResult,
    Offset,
    ReportingBasis,
    ResultMeta,
)
from margin_mcp.storage import CorpusStore, MarginError, Snapshot

Query = Annotated[str, Field(min_length=1, max_length=200)]


def _normalize(value: str) -> str:
    return " ".join("".join(c if c.isalnum() else " " for c in value.casefold()).split())


def _meta(snapshot: Snapshot) -> ResultMeta:
    warnings = [
        "Metadata only; original document contents and financial facts are not available.",
        "Coverage reflects this imported corpus, not all filings or current exchange coverage.",
    ]
    if snapshot.corpus.data_kind == "synthetic":
        warnings.insert(0, "SYNTHETIC DATA: fictional companies and filings for software testing.")
    else:
        warnings.append("Source provenance and metadata usage basis were declared by the importer.")
    return ResultMeta(
        corpus_id=snapshot.corpus.corpus_id,
        corpus_revision=snapshot.revision,
        data_kind=snapshot.corpus.data_kind,
        imported_at=snapshot.imported_at,
        warnings=warnings,
    )


def _company(snapshot: Snapshot, company_id: str) -> Company:
    for company in snapshot.corpus.companies:
        if company.company_id == company_id:
            return company
    raise MarginError("COMPANY_NOT_FOUND: call lookup_company to obtain a valid company_id")


def _check_page(snapshot: Snapshot, offset: int, corpus_revision: str | None) -> None:
    if offset and corpus_revision is None:
        raise MarginError("REVISION_REQUIRED: use the corpus_revision returned on the first page")
    if corpus_revision is not None and corpus_revision != snapshot.revision:
        raise MarginError("CORPUS_CHANGED: restart pagination at offset 0 without a revision")


def _next_offset(offset: int, limit: int, total: int) -> int | None:
    return offset + limit if offset + limit < total else None


class ResearchService:
    def __init__(self, store: CorpusStore):
        self.store = store

    @validate_call
    def lookup_company(
        self, query: Query, exchange: Exchange | None = None, limit: Limit = 10
    ) -> LookupResult:
        normalized = _normalize(query)
        if not normalized:
            raise MarginError(
                "INVALID_QUERY: provide a name or identifier containing letters/digits"
            )
        snapshot = self.store.read()
        exact: list[CompanyMatch] = []
        partial: list[CompanyMatch] = []
        for company in snapshot.corpus.companies:
            eligible = [
                (security, listing)
                for security in company.securities
                for listing in security.listings
                if exchange is None or listing.exchange == exchange
            ]
            if not eligible:
                continue
            fields = [("company_id", company.company_id), ("legal_name", company.legal_name)]
            fields.extend(("alias", alias) for alias in company.aliases)
            if company.cin:
                fields.append(("cin", company.cin))
            for security, listing in eligible:
                if security.isin:
                    fields.append(("isin", security.isin))
                fields.append(("security_id", security.security_id))
                for field in ("symbol", "exchange_code"):
                    if value := getattr(listing, field):
                        fields.append((f"{listing.exchange}.{field}", value))
            exact_fields = sorted(
                {field for field, value in fields if _normalize(value) == normalized}
            )
            partial_fields = sorted(
                {
                    field
                    for field, value in fields
                    if field in {"legal_name", "alias"} and normalized in _normalize(value)
                }
            )
            if exact_fields:
                exact.append(
                    CompanyMatch(company=company, match_kind="exact", matched_on=exact_fields)
                )
            elif partial_fields:
                partial.append(
                    CompanyMatch(company=company, match_kind="partial", matched_on=partial_fields)
                )
        matches = sorted(exact or partial, key=lambda item: item.company.company_id)
        total = len(matches)
        return LookupResult(
            meta=_meta(snapshot),
            status="not_found" if not total else "matched" if total == 1 else "ambiguous",
            total_matches=total,
            truncated=total > limit,
            candidates=matches[:limit],
        )

    @validate_call
    def get_coverage(
        self,
        company_id: Identifier | None = None,
        limit: Limit = 20,
        offset: Offset = 0,
        corpus_revision: str | None = None,
    ) -> CoverageResult:
        snapshot = self.store.read()
        _check_page(snapshot, offset, corpus_revision)
        companies = [_company(snapshot, company_id)] if company_id else snapshot.corpus.companies
        companies = sorted(companies, key=lambda company: company.company_id)
        selected = {company.company_id for company in companies}
        filings = [f for f in snapshot.corpus.filings if f.company_id in selected]
        rows = []
        for company in companies[offset : offset + limit]:
            available = [f for f in filings if f.company_id == company.company_id]
            rows.append(
                CompanyCoverage(
                    company_id=company.company_id,
                    legal_name=company.legal_name,
                    filing_count=len(available),
                    document_types=sorted({f.document_type for f in available}),
                    period_ends=sorted({f.period_end for f in available if f.period_end}),
                    latest_publication_in_corpus=max(
                        (f.published_at for f in available), default=None
                    ),
                )
            )
        return CoverageResult(
            meta=_meta(snapshot),
            coverage_notes=snapshot.corpus.coverage_notes,
            metadata_usage_basis=snapshot.corpus.metadata_usage_basis,
            total_companies=len(companies),
            total_filings=len(filings),
            offset=offset,
            next_offset=_next_offset(offset, limit, len(companies)),
            companies=rows,
        )

    @validate_call
    def list_filings(
        self,
        company_id: Identifier,
        document_type: DocumentType | None = None,
        reporting_basis: ReportingBasis | None = None,
        published_from: date | None = None,
        published_to: date | None = None,
        limit: Limit = 20,
        offset: Offset = 0,
        corpus_revision: str | None = None,
    ) -> FilingListResult:
        if published_from and published_to and published_from > published_to:
            raise MarginError("INVALID_DATE_RANGE: published_from must not follow published_to")
        snapshot = self.store.read()
        _check_page(snapshot, offset, corpus_revision)
        _company(snapshot, company_id)
        filings = [
            f
            for f in snapshot.corpus.filings
            if f.company_id == company_id
            and (document_type is None or f.document_type == document_type)
            and (reporting_basis is None or f.reporting_basis == reporting_basis)
            and (published_from is None or f.published_at.date() >= published_from)
            and (published_to is None or f.published_at.date() <= published_to)
        ]
        # Stable tie breaker: ID ascending within publication timestamp descending.
        filings.sort(key=lambda f: f.filing_id)
        filings.sort(key=lambda f: f.published_at, reverse=True)
        return FilingListResult(
            meta=_meta(snapshot),
            total_matches=len(filings),
            offset=offset,
            next_offset=_next_offset(offset, limit, len(filings)),
            filings=filings[offset : offset + limit],
        )

    @validate_call
    def get_filing(self, filing_id: Identifier) -> FilingResult:
        snapshot = self.store.read()
        for filing in snapshot.corpus.filings:
            if filing.filing_id == filing_id:
                return FilingResult(meta=_meta(snapshot), filing=filing)
        raise MarginError("FILING_NOT_FOUND: call list_filings to obtain a valid filing_id")
