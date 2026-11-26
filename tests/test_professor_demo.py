"""Fictional inputs verify the demo client, not financial or semantic ground truth."""

import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.mcp.profiles import ToolView
from margin.interfaces.mcp.server import MarginMCP

module = importlib.util.spec_from_file_location(
    "professor_demo", Path(__file__).parents[1] / "scripts/demo_mcp_review.py"
)
demo = importlib.util.module_from_spec(module)
module.loader.exec_module(demo)


def specification():
    return {
        "judgment_origin": "operator_supplied",
        "source": {
            "issuer": "NSE:EXAMPLE",
            "title": "Fictional demo fixture",
            "url": "https://example.invalid/source",
            "kind": "provider_summary",
            "date": "2026-11-20",
            "date_kind": "unknown",
            "passages": [
                {"passage_id": "summary", "text": "Demand improved.", "locator": "summary"}
            ],
        },
        "claims": [
            {
                "claim_id": "C1",
                "text": "Demand improved.",
                "verdict": "supported",
                "quote": "Demand improved.",
                "rationale": "Fictional operator annotation.",
            },
            {
                "claim_id": "C2",
                "text": "Investors became bullish.",
                "verdict": "insufficient_evidence",
                "rationale": "No investor reaction in fictional supplied text.",
            },
        ],
        "sentiment": {
            "aspect": "demand",
            "from": "2026-11-10",
            "to": "2026-11-25",
            "date_basis": "record_date",
            "label": "positive",
            "quote": "Demand improved.",
            "rationale": "Fictional operator annotation.",
        },
    }


class Client:
    def __init__(self, service):
        self.view = ToolView(MarginMCP(service), "review")
        self.calls = []

    async def list_tools(self):
        return SimpleNamespace(tools=list(self.view.tools.values()))

    async def call_tool(self, name, arguments):
        self.calls.append(name)
        return await self.view.call(name, arguments)


@pytest.fixture
async def service():
    owner = ResearchService(Settings(bharatstock_requests=0, drishti_requests=0, drishti_credits=0))
    try:
        yield owner
    finally:
        await owner.close()


async def test_demo_reuses_actual_refs_and_preserves_unsupported_claim(service):
    client = Client(service)
    lines = []
    result = await demo.run_demo(
        client, specification(), expected_mode="synthetic", emit=lines.append
    )
    assert result["audit"]["status"] == "incomplete"
    assert result["audit"]["assessment_coverage"]["status"] == "host_assessed"
    assert result["audit"]["assessment_counts"] == {"supported": 1, "insufficient_evidence": 1}
    assert result["sentiment"]["counts"]["positive"] == 1
    assert result["sentiment"]["investor_sentiment"] is False
    assert result["provider_attempt_delta"] == 0
    assert len(client.calls) == 10
    assert any("operator" in line for line in lines)
    assert "margin_connect_drishti" not in client.calls


async def test_wrong_quote_stops_demo_before_sentiment_or_false_completion(service):
    client = Client(service)
    spec = copy.deepcopy(specification())
    spec["claims"][0]["quote"] = "Invented quote."
    with pytest.raises(demo.DemoError, match="quote_mismatch"):
        await demo.run_demo(client, spec, expected_mode="synthetic", emit=lambda _: None)
    assert "margin_prepare_sentiment" not in client.calls
    assert all(packet[1]["assessment"] is None for packet in service.reviews.packets.values())


async def test_missing_task_input_never_creates_demo_data(service):
    client = Client(service)
    with pytest.raises(demo.DemoError, match="operator_supplied"):
        await demo.run_demo(client, {}, expected_mode="synthetic", emit=lambda _: None)
    assert not client.calls and not service.reviews.sources


async def test_demo_requires_zero_provider_allowance(service):
    client = Client(service)
    service.ledger.limits["bharatstock"] = 1
    with pytest.raises(demo.DemoError, match="zero provider"):
        await demo.run_demo(client, specification(), expected_mode="synthetic", emit=lambda _: None)
    assert client.calls == ["margin_status"]
    assert not service.reviews.sources


def test_sdk_exception_group_keeps_safe_demo_failure_message():
    error = ExceptionGroup(
        "SDK context",
        [demo.DemoError("margin_submit_assessment: quote_mismatch; stopped without retry.")],
    )
    assert "quote_mismatch" in demo.failure_message(error)
    assert demo.failure_message(ValueError("private text")) == "ValueError"
