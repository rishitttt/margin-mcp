"""Typed previews use fictional inputs/transports; never live source verification."""

import copy

import pytest
from jsonschema import Draft202012Validator

from margin.core.config import Settings
from margin.core.registry import Registry
from margin.core.service import ResearchService
from margin.interfaces.mcp.server import MarginMCP
from margin.interfaces.mcp.tools import CONTRACT, DIRECT_PREVIEWS, VERSION, definitions


def args(tool):
    if tool.endswith("filing"):
        return {"earnings_id": "fictional-discovered-id", "detailed": True}
    return {
        "symbols": ["SYNTHA"],
        "from": "2026-11-10",
        "to": "2026-11-25",
        "page": 1,
        "limit": 1,
    }


@pytest.fixture
async def adapter():
    service = ResearchService(Settings())
    try:
        yield MarginMCP(service)
    finally:
        await service.close()


async def call(adapter, name, arguments, error=False):
    result = await adapter.call(name, arguments)
    assert result.is_error is error, result.structured_content
    Draft202012Validator(adapter.tools[name].output_schema).validate(result.structured_content)
    return result.structured_content


@pytest.mark.parametrize("tool,operation", DIRECT_PREVIEWS.items())
async def test_typed_and_generic_plans_share_core_contract_without_network(
    adapter, tool, operation
):
    inputs = args(tool)
    original = copy.deepcopy(inputs)
    before = adapter.service.ledger.snapshot()
    typed = (await call(adapter, tool, inputs | {"why": "Fictional local preview."}))["data"]
    generic_args = {"query": inputs} if not tool.endswith("filing") else inputs
    generic = (
        await call(
            adapter,
            "margin_preview",
            {"operations": [{"operation": operation, "arguments": generic_args}]},
        )
    )["data"]
    for field in ("arguments", "operation", "estimated_credits", "schema_hash", "execution_kind"):
        assert typed["operations"][0][field] == generic["operations"][0][field]
    assert typed["data_operations"] == {"bharatstock": 0, "drishti": 1}
    assert typed["estimated_credits"] == generic["estimated_credits"]
    assert "why" not in typed["operations"][0]["arguments"]
    assert inputs == original and adapter.service.ledger.snapshot() == before
    assert not adapter.service.runs and not adapter.service._tasks
    if tool.endswith("announcements"):
        assert (
            typed["operations"][0]["arguments"]["query"]["include_extracted_information"] is False
        )


@pytest.mark.parametrize("tool,operation", DIRECT_PREVIEWS.items())
def test_typed_schema_is_generated_from_reviewed_contract_and_isolation(tool, operation):
    registry = Registry(Settings())
    exact = registry.spec(operation).schema
    projected = definitions()[tool].input_schema
    if "query" in exact["properties"]:
        name = exact["properties"]["query"]["$ref"].split("/")[-1]
        source = exact["$defs"][name]
    else:
        source = exact
    assert {k: v for k, v in projected["properties"].items() if k != "why"} == source["properties"]
    assert projected.get("required", []) == source.get("required", [])
    assert projected["additionalProperties"] is False
    Draft202012Validator(projected).validate(args(tool))
    projected["properties"].clear()
    assert definitions()[tool].input_schema["properties"]
    assert registry.spec(operation).schema == exact


@pytest.mark.parametrize("wrapper", ["query", "arguments", "operations", "private-caller-field"])
async def test_typed_schema_rejects_wrappers_without_echo_or_provider_call(adapter, wrapper):
    before = adapter.service.ledger.snapshot()
    result = await call(
        adapter,
        "margin_preview_announcements",
        {wrapper: "private-caller-value"},
        error=True,
    )
    message = result["error"]["message"]
    assert "allowed fields" in message
    assert "private-caller" not in message
    assert adapter.service.ledger.snapshot() == before and not adapter.service.plans


async def test_generic_missing_query_feedback_identifies_required_nesting_safely(adapter):
    before = adapter.service.ledger.snapshot()
    result = await call(
        adapter,
        "margin_preview",
        {
            "operations": [
                {
                    "operation": "drishti.get_announcements",
                    "arguments": args("margin_preview_announcements")
                    | {"private-field-name": "private-field-value"},
                }
            ]
        },
        error=True,
    )
    message = result["error"]["message"]
    assert "missing required fields: query" in message
    assert "allowed fields: query" in message and "margin_catalog" in message
    assert "private-field" not in message and len(message) < 2100
    assert adapter.service.ledger.snapshot() == before and not adapter.service.plans


async def test_disallowed_extraction_and_conflicting_detail_selectors_stay_held(adapter):
    before = adapter.service.ledger.snapshot()
    await call(
        adapter,
        "margin_preview_announcements",
        args("margin_preview_announcements") | {"include_extracted_information": True},
        error=True,
    )
    await call(
        adapter,
        "margin_preview_earnings_filing",
        args("margin_preview_earnings_filing") | {"symbol": "SYNTHA", "quarter": "q2_27"},
        error=True,
    )
    assert adapter.service.ledger.snapshot() == before and not adapter.service.plans


async def test_typed_preview_respects_live_readiness_without_refreshing():
    service = ResearchService(
        Settings(
            mode="live",
            drishti_key="fictional-key-not-used",
            enabled_unverified=frozenset({"drishti.get_announcements"}),
            bharatstock_requests=0,
            drishti_requests=0,
            drishti_credits=1,
        )
    )
    try:
        before = service.ledger.snapshot()
        result = await call(
            MarginMCP(service),
            "margin_preview_announcements",
            args("margin_preview_announcements") | {"symbols": ["INFY"]},
            error=True,
        )
        assert result["error"]["code"] == "not_connected"
        assert service.ledger.snapshot() == before and service._connection_task is None
    finally:
        await service.close()


async def test_catalog_keeps_generic_schema_and_explains_flat_alternative(adapter):
    result = await call(
        adapter,
        "margin_catalog",
        {"name": "drishti.get_announcements", "include_schemas": True},
    )
    row = result["data"]["groups"]["retrieval"][0]
    assert row["schema"]["required"] == ["query"]
    assert row["mcp_execution"]["inputs_at"] == "operations[0].arguments"
    assert row["direct_preview"]["tool"] == "margin_preview_announcements"
    assert row["direct_preview"]["inputs_at"] == "top_level"
    assert "tools/list" in row["direct_preview"]["schema_source"]
    assert "preserve" in result["data"]["schema_lookup"]


async def test_status_distinguishes_package_version_from_contract_without_network(adapter):
    before = adapter.service.ledger.snapshot()
    status = await call(adapter, "margin_status", {})
    assert status["data"]["package_version"] == VERSION == "0.10.0"
    assert status["contract_version"] == CONTRACT == "margin.mcp.v1"
    assert adapter.service.ledger.snapshot() == before


async def test_typed_news_preview_runs_only_after_submission_and_imports_existing_result(adapter):
    plan = (await call(adapter, "margin_preview_news", args("margin_preview_news")))["data"]
    assert adapter.service.ledger.requests["drishti"] == 0
    run = (
        await call(
            adapter,
            "margin_run",
            {
                "session_id": adapter.session_id,
                "plan_id": plan["plan_id"],
                "idempotency_key": "typed-preview-fictional-001",
                "wait_seconds": 2,
            },
        )
    )["data"]
    before = adapter.service.ledger.snapshot()
    imported = (
        await call(
            adapter,
            "margin_review_sources",
            {
                "run_id": run["run_id"],
                "operation_id": run["operations"][0]["operation_id"],
                "issuer": "NSE:SYNTHA",
            },
        )
    )["data"]
    assert imported["sources"][0]["origin"] == "retained_provider"
    assert not imported["sources"][0]["original_document_verified"]
    assert before["http_attempts"] == {"bharatstock": 0, "drishti": 1}
    assert adapter.service.ledger.snapshot() == before
