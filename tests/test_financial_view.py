"""Fictional numbers test deterministic presentation, not issuer financial truth."""

from copy import deepcopy

from margin.analysis.presentation import financial_view


def result(row):
    return {
        "operation": "bharatstock.get_financials",
        "payload_kind": "rest_json",
        "payload": {"data": [row]},
        "receipt": {"arguments": {"ticker": "FICTIONAL", "exchange": "NSE"}},
    }


def test_exact_crore_conversion_and_labels_preserve_original_fields():
    source = result(
        {
            "revenue": 12345678900,
            "operating_profit": 30000000,
            "profit_before_tax": 20000000,
            "ebitda": 40000000,
            "eps": 12.34,
            "net_profit": 9000000,
            "profit_from_continuing_operations": 7000000,
            "consolidation_type": "consolidated",
            "period_end_date": "2026-03-31",
            "period_type": "annual",
            "unknown_amount": 500000000,
        }
    )
    original = deepcopy(source)
    view = financial_view(source)
    row = view["rows"][0]
    metrics = {m["metric"]: m for m in row["metrics"]}
    assert source == original
    assert metrics["revenue"]["value"] == "1234.56789"
    assert metrics["revenue"]["display"] == "₹1,234.57 crore"
    assert metrics["revenue"]["raw_value"] == 12345678900
    assert metrics["revenue"]["source_path"] == "data[0].revenue"
    assert metrics["eps"]["value"] == "12.34" and metrics["eps"]["unit"] == "INR_per_share"
    assert metrics["operating_profit"]["value"] == "3"
    assert metrics["profit_before_tax"]["value"] == "2"
    assert "interest, taxes, depreciation" in metrics["ebitda"]["label"]
    assert "unknown_amount" not in metrics
    assert row["continuing_profit_differs"] and len(row["warnings"]) == 2
    assert row["period_start"] is None
    assert view["unit_origin"] == "provider_documentation"


def test_missing_invalid_and_zero_are_distinct():
    view = financial_view(
        result({"revenue": 0, "cash_flow_operating": None, "net_profit": "bad-value"})
    )
    assert view["status"] == "partial"
    metrics = {m["metric"]: m for m in view["rows"][0]["metrics"]}
    assert metrics["revenue"]["value"] == "0" and metrics["revenue"]["status"] == "success"
    assert metrics["cash_flow_operating"]["value"] is None
    assert metrics["cash_flow_operating"]["status"] == "missing"
    assert metrics["net_profit"]["status"] == "invalid" and metrics["net_profit"]["value"] is None


def test_unknown_shape_empty_and_row_bounds():
    assert financial_view({"operation": "drishti.get_news"}) is None
    assert financial_view(result({}) | {"payload": {"data": []}})["status"] == "empty"
    assert financial_view(result({}) | {"payload": {"other": 1}})["status"] == "unavailable"
    bounded = financial_view(result({}) | {"payload": {"data": [{"revenue": 1}] * 9}})
    assert len(bounded["rows"]) == 8 and bounded["rows_omitted"] == 1


def test_segments_are_converted_separately_and_bounded():
    view = financial_view(
        result(
            {
                "segment_revenue": [{"segment": "Fictional products", "value": 123000000}] * 21,
                "segment_results": [{"segment": "Fictional products", "value": -2000000}],
            }
        )
    )
    row = view["rows"][0]
    assert len(row["segments"]) == 21 and row["segments_omitted"] == 1
    assert row["segments"][0]["value"] == "12.3"
    assert row["segments"][-1]["value"] == "-0.2"
    assert row["segments"][0]["source_path"] == "data[0].segment_revenue[0].value"
