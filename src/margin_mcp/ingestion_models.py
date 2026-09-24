"""Local document provenance and explicit, hash-bound extraction recipes."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, HttpUrl, model_validator

from margin_mcp.models import Identifier, Record, Text

Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
PositiveInt = Annotated[int, Field(strict=True, ge=1)]
Coordinate = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Box = tuple[Coordinate, Coordinate, Coordinate, Coordinate]


class DocumentManifest(Record):
    schema_version: Literal[1] = 1
    company_id: Identifier
    issuer_name: Text
    filing_id: Identifier
    title: Text
    data_kind: Literal["synthetic", "real"]
    source_url: HttpUrl | None = None
    published_on: date
    acquired_at: AwareDatetime
    usage_basis: Text
    processing_scope: Literal["local_only"] = "local_only"

    @model_validator(mode="after")
    def check_provenance(self) -> Self:
        if self.data_kind == "real" and self.source_url is None:
            raise ValueError("Real documents require source_url")
        if self.acquired_at.date() < self.published_on:
            raise ValueError("Acquisition must not precede publication")
        return self


class Region(Record):
    page: PositiveInt
    bbox: Box

    @model_validator(mode="after")
    def check_box(self) -> Self:
        x0, top, x1, bottom = self.bbox
        if x0 >= x1 or top >= bottom:
            raise ValueError("bbox must have positive width and height")
        return self


class TextAnchor(Region):
    expected_text: Text


class FactMapping(Record):
    metric: Literal["revenue_from_operations", "profit_before_tax", "profit_for_period"]
    period_start: date
    period_end: date
    period_kind: Literal["quarter", "half_year", "year", "year_to_date"]
    reporting_basis: Literal["standalone", "consolidated"]
    accounting_standard: Literal["Ind AS", "IFRS"]
    currency: Literal["INR"] = "INR"
    source_scale: Literal["rupee", "lakh", "crore", "million"]
    label: TextAnchor
    value: Region
    # All context claims must have source text, not just a hand-entered semantic label.
    period_header: TextAnchor
    basis_header: TextAnchor
    unit_header: TextAnchor
    standard_header: TextAnchor

    @model_validator(mode="after")
    def check_period(self) -> Self:
        if self.period_start > self.period_end:
            raise ValueError("period_start must not follow period_end")
        return self


class ExtractionRecipe(Record):
    schema_version: Literal[1] = 1
    document_sha256: Digest
    mappings: Annotated[list[FactMapping], Field(min_length=1, max_length=100)]

    @model_validator(mode="after")
    def unique_facts(self) -> Self:
        keys = [
            (
                m.metric,
                m.period_start,
                m.period_end,
                m.period_kind,
                m.reporting_basis,
                m.accounting_standard,
            )
            for m in self.mappings
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate metric/context in recipe")
        return self
