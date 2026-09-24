"""Run a real subprocess MCP workflow using the explicitly imported synthetic corpus."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def demonstrate(db_path: Path) -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "margin_mcp", "serve", "--db", str(db_path.resolve())],
    )
    async with Client(parameters) as client:
        tools = await client.list_tools()
        print("Discovered tools:", ", ".join(tool.name for tool in tools.tools))
        for tool, arguments in [
            ("get_coverage", {}),
            ("lookup_company", {"query": "Aarya"}),
            ("lookup_company", {"query": "DEMOAARYASW", "exchange": "NSE"}),
            (
                "list_filings",
                {
                    "company_id": "demo-aarya-software",
                    "document_type": "financial_results",
                    "reporting_basis": "consolidated",
                },
            ),
            ("get_filing", {"filing_id": "demo-aarya-fy26-q2-consolidated"}),
        ]:
            result = await client.call_tool(tool, arguments, read_timeout_seconds=15)
            if result.is_error:
                raise RuntimeError(f"{tool} failed: {result.content}")
            print(f"\n{tool}")
            print(json.dumps(result.structured_content, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    arguments = parser.parse_args()
    asyncio.run(demonstrate(arguments.db))
