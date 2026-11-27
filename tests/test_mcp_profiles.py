"""Local frontend profiles share one core and expose no provider execution in review."""

import copy
import json

import pytest
from mcp.shared.exceptions import MCPError

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import REVIEW_TOOLS, ToolView
from margin.interfaces.mcp.server import MarginMCP, create_server
from margin.interfaces.mcp.tools import DIRECT_REVIEWS


@pytest.fixture
async def owner():
    service = ResearchService(
        Settings(bharatstock_requests=0, drishti_requests=0, drishti_credits=0)
    )
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def call(view, name, values=None):
    result = await view.call(name, values or {})
    assert not result.is_error, result.structured_content
    assert json.loads(result.content[0].text) == result.structured_content
    return result.structured_content


def test_invalid_profile_is_rejected_before_any_startup():
    with pytest.raises(ValueError, match="profile"):
        create_server(Settings(), tool_profile="invented")


async def test_review_profile_is_small_local_and_catalog_only_advertises_callable_routes(owner):
    full, review = ToolView(owner), ToolView(owner, "review")
    assert len(full.tools) == 39 and set(review.tools) == REVIEW_TOOLS and len(review.tools) == 16
    assert "margin_review" not in review.tools and "margin_run" not in review.tools
    assert set(DIRECT_REVIEWS) <= set(review.tools)
    before = owner.service.ledger.snapshot()
    result = await call(review, "margin_catalog", {"group": "all", "include_schemas": True})
    assert set(result["data"]["groups"]) == {"review"}
    rows = result["data"]["groups"]["review"]
    assert len(rows) == 12
    assert all(row["mcp_execution"]["tool"] in review.tools for row in rows)
    assert all("generic_mcp_execution" not in row for row in rows)
    assert full.tools["margin_catalog"].input_schema["properties"]["group"]["enum"] == [
        "all",
        "retrieval",
        "calculations",
        "company",
        "review",
    ]
    assert owner.service.ledger.snapshot() == before


@pytest.mark.parametrize(
    "name,values",
    [
        ("margin_run", {}),
        ("margin_connect_drishti", {}),
        ("margin_company_finance", {}),
        ("margin_review", {}),
        ("sentiment.prepare_analysis", {}),
        ([], {}),
        ("margin_catalog", {"group": "retrieval"}),
    ],
)
async def test_hidden_or_out_of_profile_catalog_calls_never_forward(
    owner, monkeypatch, name, values
):
    view = ToolView(owner, "review")
    calls = []
    original = owner.call

    async def observe(*args):
        calls.append(args)
        return await original(*args)

    monkeypatch.setattr(owner, "call", observe)
    with pytest.raises(MCPError) as caught:
        await view.call(name, values)
    assert caught.value.error.code == -32602 and calls == []
    if name == "sentiment.prepare_analysis":
        assert "margin_prepare_sentiment" in caught.value.error.message
    assert owner.service.ledger.requests == {"bharatstock": 0, "drishti": 0}


async def test_switching_frontend_view_preserves_sources_packets_and_identity(owner):
    full = ToolView(owner)
    source = {
        "issuer": "NSE:EXAMPLE",
        "title": "Fictional review source",
        "url": "https://example.invalid/source",
        "kind": "provider_summary",
        "date": None,
        "date_kind": "unknown",
        "passages": [{"passage_id": "P1", "text": "Demand improved.", "locator": "summary"}],
    }
    registered = await call(full, "margin_register_sources", {"sources": [source]})
    sid = registered["data"]["sources"][0]["source_id"]
    prepared = await call(
        full,
        "margin_prepare_verification",
        {"claims": [{"claim_id": "C1", "text": "Demand improved.", "source_ids": [sid]}]},
    )
    packet = prepared["data"]
    before = copy.deepcopy(owner.service.reviews.packets)
    review = ToolView(owner, "review")
    status = await call(review, "margin_status")
    assert status["session_id"] == prepared["session_id"] == owner.session_id
    assert status["data"]["tool_profile"] == "review" and status["data"]["advertised_tools"] == 16
    rendered = await call(
        review, "margin_render_citations", {k: packet[k] for k in ("packet_id", "packet_hash")}
    )
    assert rendered["data"]["citations"][0]["semantic_review"] == "not_reviewed"
    assert owner.service.reviews.packets == before
    assert (await call(full, "margin_status"))["data"]["tool_profile"] == "all"


async def test_profile_catalog_errors_do_not_echo_unknown_values(owner):
    view = ToolView(owner, "review")
    with pytest.raises(MCPError) as caught:
        await view.call("margin_catalog", {"private-field": "private-value"})
    assert (
        "private-field" not in caught.value.error.message
        and "private-value" not in caught.value.error.message
    )
