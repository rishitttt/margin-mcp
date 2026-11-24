"""Actionable schema feedback must not quote sensitive caller data."""

from margin.analysis.service import SPECS
from margin.core.validation import validation_summary


def test_unexpected_property_names_and_values_are_not_reflected():
    schema = SPECS["finance.calculate_margins"][1]
    message = validation_summary(schema, {"private-key-name": "private-secret-value"})
    assert "/: unexpected fields; allowed fields: profit, revenue." in message
    assert "missing required fields: profit, revenue" in message
    assert "private-key-name" not in message and "private-secret-value" not in message


def test_nested_missing_fields_and_object_types_are_actionable():
    schema = SPECS["finance.calculate_margins"][1]
    message = validation_summary(schema, {"profit": {}, "revenue": "private-data"})
    assert "/profit: missing required fields: issuer, metric" in message
    assert "/revenue: expected type: object." in message
    assert "private-data" not in message


def test_dynamic_property_path_is_hidden_and_feedback_is_bounded():
    schema = {
        "type": "object",
        "properties": {"items": {"type": "object", "additionalProperties": {"type": "integer"}}},
    }
    message = validation_summary(schema, {"items": {"private-field": "private-value"}})
    assert "/items/[entry]: expected type: integer." == message
    assert "private-field" not in message and "private-value" not in message
    assert len(message) <= 1800


def test_valid_inputs_still_pass_and_date_formats_are_checked():
    schema = {"type": "string", "format": "date"}
    assert validation_summary(schema, "2026-03-31") is None
    assert validation_summary(schema, "2026-02-30") == "/: expected format: date."
