import subprocess
import sys

import anyio
import jsonschema
import pytest
from mcp import Client, StdioServerParameters


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["auto", "legacy"])
async def test_real_stdio_workflow_and_errors(store, mode):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "margin_mcp", "serve", "--db", str(store.path)],
        cwd=str(store.path.parent),  # Installed package must work outside the repository cwd.
    )
    with anyio.fail_after(30):
        async with Client(params, mode=mode) as client:
            discovered = await client.list_tools()
            tools = {tool.name: tool for tool in discovered.tools}
            assert set(tools) == {
                "lookup_company",
                "get_coverage",
                "list_filings",
                "get_filing",
                "get_discovery_plan",
            }
            for tool in tools.values():
                assert tool.annotations.read_only_hint is True
                assert tool.output_schema is not None
            for name, arguments in [
                ("get_coverage", {}),
                ("lookup_company", {"query": "Aarya", "limit": 1}),
                (
                    "list_filings",
                    {
                        "company_id": "demo-aarya-software",
                        "reporting_basis": "consolidated",
                        "published_from": "2025-10-20",
                        "published_to": "2025-10-20",
                    },
                ),
                ("get_filing", {"filing_id": "demo-aarya-fy26-q2-consolidated"}),
            ]:
                result = await client.call_tool(name, arguments, read_timeout_seconds=10)
                assert not result.is_error, result.content
                data = result.structured_content
                jsonschema.validate(data, tools[name].output_schema)
                assert data["meta"]["data_kind"] == "synthetic"
                assert data["meta"]["metadata_only"] is True
                if name == "lookup_company":
                    assert data["status"] == "ambiguous"
                    assert data["total_matches"] == 2
                if name == "list_filings":
                    assert data["total_matches"] == 1
                if name == "get_filing":
                    assert data["content_available"] is False
            missing = await client.call_tool("get_filing", {"filing_id": "unknown"})
            assert missing.is_error
            assert "FILING_NOT_FOUND" in str(missing.content)
            invalid = await client.call_tool("lookup_company", {"query": "Aarya", "limit": 0})
            assert invalid.is_error
            # Guidance is available outside repo cwd and never poses as corpus evidence.
            plan = await client.call_tool(
                "get_discovery_plan",
                {
                    "company_query": "Infosys",
                    "period_end": "2025-09-30",
                },
            )
            assert not plan.is_error
            data = plan.structured_content
            jsonschema.validate(data, tools["get_discovery_plan"].output_schema)
            assert data["network_performed"] is False
            assert data["issuer_identity_verified"] is False
            assert any("infosys.com" in source["url"] for source in data["sources"])
            resources = await client.list_resources()
            assert "margin://workflows/filing-discovery" in {
                str(resource.uri) for resource in resources.resources
            }
            workflow = await client.read_resource("margin://workflows/filing-discovery")
            assert "Missing is not zero" in workflow.contents[0].text
            prompts = await client.list_prompts()
            assert "discover_filings" in {prompt.name for prompt in prompts.prompts}
            prompt = await client.get_prompt(
                "discover_filings",
                {
                    "company_query": "Infosys",
                    "period_end": "2025-09-30",
                },
            )
            assert "needs_review" in prompt.messages[0].content.text
            invalid = await client.call_tool(
                "get_discovery_plan",
                {
                    "company_query": "Infosys",
                    "period_end": "not-a-date",
                },
            )
            assert invalid.is_error


def test_missing_database_startup_fails_without_stdout_or_creation(tmp_path):
    path = tmp_path / "missing.sqlite3"
    result = subprocess.run(
        [sys.executable, "-m", "margin_mcp", "serve", "--db", str(path)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "CORPUS_NOT_LOADED" in result.stderr
    assert not path.exists()
