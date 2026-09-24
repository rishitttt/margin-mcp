"""Versioned metadata contracts; no extracted financial facts in milestone 1."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")]
Text = Annotated[str, Field(min_length=1, max_length=1000)]
Exchange = Literal["NSE", "BSE"]
DocumentType = Literal["financial_results", "annual_report", "announcement", "shareholding_pattern"]
ReportingBasis = Literal["standalone", "consolidated", "not_applicable", "unknown"]
Limit = Annotated[int, Field(strict=True, ge=1, le=100)]
Offset = Annotated[int, Field(strict=True, ge=0)]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class Listing(Record):
    exchange: Exchange
    symbol: Text | None = None
    exchange_code: Text | None = None

    @model_validator(mode="after")
    def require_identifier(self) -> Self:
        if self.symbol is None and self.exchange_code is None:
            raise ValueError("A listing needs a symbol or exchange_code")
        return self


class Security(Record):
    security_id: Identifier
    isin: Annotated[str, Field(pattern=r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")] | None = None
    listings: Annotated[list[Listing], Field(min_length=1)]


class Company(Record):
    company_id: Identifier
    legal_name: Text
    aliases: list[Text] = Field(default_factory=list)
    cin: Annotated[str, Field(pattern=r"^[A-Z0-9]{21}$")] | None = None
    securities: Annotated[list[Security], Field(min_length=1)]
    identity_source_url: HttpUrl | None = None
    identity_observed_at: AwareDatetime | None = None


class Filing(Record):
    filing_id: Identifier
    company_id: Identifier
    title: Text
    document_type: DocumentType
    reporting_basis: ReportingBasis
    period_start: date | None = None
    period_end: date | None = None
    published_at: AwareDatetime
    observed_at: AwareDatetime
    publisher: Text
    source_url: HttpUrl | None = None

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if self.period_start and not self.period_end:
            raise ValueError("period_start requires period_end")
        if self.period_start and self.period_start > self.period_end:
            raise ValueError("period_start must not follow period_end")
        if self.observed_at < self.published_at:
            raise ValueError("observed_at must not precede published_at")
        if self.period_end and self.period_end > self.published_at.date():
            raise ValueError("period_end must not follow publication")
        if self.document_type in {"financial_results", "annual_report", "shareholding_pattern"}:
            if self.period_end is None:
                raise ValueError("Periodic filings require period_end")
        return self


class Corpus(Record):
    schema_version: Literal[1]
    corpus_id: Identifier
    title: Text
    data_kind: Literal["synthetic", "real"]
    metadata_usage_basis: Text
    coverage_notes: Annotated[list[Text], Field(min_length=1)]
    companies: Annotated[list[Company], Field(min_length=1, max_length=1000)]
    filings: Annotated[list[Filing], Field(max_length=10000)]

    @model_validator(mode="after")
    def check_references(self) -> Self:
        company_ids = [c.company_id for c in self.companies]
        if len(set(company_ids)) != len(company_ids):
            raise ValueError("Duplicate company_id")
        filing_ids = [f.filing_id for f in self.filings]
        if len(set(filing_ids)) != len(filing_ids):
            raise ValueError("Duplicate filing_id")
        securities: set[str] = set()
        isins: set[str] = set()
        listings: set[tuple[str, str, str]] = set()
        cins: set[str] = set()
        for company in self.companies:
            if self.data_kind == "real" and (
                company.identity_source_url is None or company.identity_observed_at is None
            ):
                raise ValueError("Real company metadata requires identity source and observed time")
            if company.cin:
                if company.cin in cins:
                    raise ValueError("Duplicate CIN")
                cins.add(company.cin)
            for security in company.securities:
                if security.security_id in securities:
                    raise ValueError("Duplicate security_id")
                securities.add(security.security_id)
                if security.isin:
                    if security.isin in isins:
                        raise ValueError("Duplicate ISIN")
                    isins.add(security.isin)
                for listing in security.listings:
                    for field in ("symbol", "exchange_code"):
                        value = getattr(listing, field)
                        if value:
                            key = (listing.exchange, field, value.casefold())
                            if key in listings:
                                raise ValueError(f"Duplicate listing identifier: {key}")
                            listings.add(key)
        for filing in self.filings:
            if filing.company_id not in company_ids:
                raise ValueError(f"Unknown filing company_id: {filing.company_id}")
            if self.data_kind == "real" and filing.source_url is None:
                raise ValueError("Real filing metadata requires source_url")
        return self


class ResultMeta(Record):
    schema_version: Literal[1] = 1
    corpus_id: str
    corpus_revision: str
    data_kind: Literal["synthetic", "real"]
    imported_at: AwareDatetime
    metadata_only: Literal[True] = True
    warnings: list[str]


class CompanyMatch(Record):
    company: Company
    match_kind: Literal["exact", "partial"]
    matched_on: list[str]


class LookupResult(Record):
    meta: ResultMeta
    status: Literal["matched", "ambiguous", "not_found"]
    total_matches: int
    truncated: bool
    candidates: list[CompanyMatch]


class CompanyCoverage(Record):
    company_id: str
    legal_name: str
    filing_count: int
    document_types: list[DocumentType]
    period_ends: list[date]
    latest_publication_in_corpus: AwareDatetime | None


class CoverageResult(Record):
    meta: ResultMeta
    coverage_notes: list[str]
    metadata_usage_basis: str
    total_companies: int
    total_filings: int
    offset: int
    next_offset: int | None
    companies: list[CompanyCoverage]


class FilingListResult(Record):
    meta: ResultMeta
    total_matches: int
    offset: int
    next_offset: int | None
    filings: list[Filing]


class FilingResult(Record):
    meta: ResultMeta
    filing: Filing
    content_available: Literal[False] = False
    content_status: Literal["metadata_only"] = "metadata_only"
