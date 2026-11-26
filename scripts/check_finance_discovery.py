"""Inspect real MCP discovery and previews; never executes a provider operation."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(args):
    root = Path(__file__).resolve().parents[1]
    output = args.output.expanduser().absolute()
    if subprocess.run(["git", "check-ignore", "-q", str(output)], cwd=root, check=False).returncode:
        raise ValueError("Choose an ignored reports/private output directory.")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("MARGIN_")
        and key not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env["PYTHONPATH"] = str(root / "src")
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "margin.interfaces.mcp",
            "--backend-socket",
            str(args.backend_socket),
            "--mode",
            "live",
            "--tool-profile",
            "all",
        ],
        env=env,
        cwd="/private/tmp" if Path("/private/tmp").exists() else "/tmp",
    )
    observations = []
    with (output / "stderr.txt").open("w") as err:
        (output / "stderr.txt").chmod(0o600)
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                tools = {t.name: t for t in (await client.list_tools()).tools}

                async def call(name, arguments=None):
                    values = (arguments or {}) | {
                        "why": "Operator discovery audit: schema/preview only; not a model trial or data execution."
                    }
                    assert name in {
                        "margin_status",
                        "margin_catalog",
                        "margin_company_finance",
                        "margin_preview",
                    }
                    assert values.get("execute", False) is False
                    Draft202012Validator(tools[name].input_schema).validate(values)
                    result = await client.call_tool(name, values)
                    body = result.structured_content
                    observations.append({"tool": name, "arguments": values, "result": body})
                    # Preserve failures before stopping, without printing raw payloads.
                    (output / "observations.json").write_text(
                        json.dumps(observations, indent=2) + "\n"
                    )
                    (output / "observations.json").chmod(0o600)
                    if result.is_error:
                        raise ValueError(
                            "Discovery/preview rejected; inspect private observations."
                        )
                    return body["data"]

                before = await call("margin_status")
                assert before["mode"] == "live" and before["tool_profile"] == "all"
                catalog = await call("margin_catalog", {"group": "company"})
                company = catalog["groups"]["company"]
                selectors = set(
                    tools["margin_company_finance"].input_schema["properties"]["function"]["enum"]
                )
                assert selectors == {row["function"] for row in company}
                matrix = []
                for row in company:
                    route = row["fresh_mcp_execution"]
                    assert (
                        route["tool"] == "margin_company_finance"
                        and route["inputs_at"] == "top_level"
                    )
                    function = row["function"]
                    period = "quarterly" if function.endswith("_ttm") else "annual"
                    ticker = "HINDUNILVR" if function.endswith("_margins") else "INFY"
                    preview = await call(
                        route["tool"],
                        route["bind"]
                        | {
                            "ticker": ticker,
                            "exchange": "NSE",
                            "period_type": period,
                            "basis": "consolidated",
                            "execute": False,
                        },
                    )
                    assert preview["status"] == "preview"
                    assert preview["maximum_provider_requests"] == {"bharatstock": 1, "drishti": 0}
                    request = preview["data_operation"]
                    assert request["operation"] == "bharatstock.get_financials"
                    assert request["arguments"]["page_size"] == (8 if period == "quarterly" else 2)
                    matrix.append(
                        {
                            "function": function,
                            "description": row["description"],
                            "preview": "passed",
                            "live_execution": "not_tested_this_run",
                            "ticker": ticker,
                            "period_type": period,
                            "maximum_bharatstock_requests": 1,
                        }
                    )
                retrieval = await call(
                    "margin_catalog",
                    {"group": "retrieval", "name": "bharatstock.", "include_schemas": True},
                )
                raw_rows = retrieval["groups"]["retrieval"]
                for row in raw_rows:
                    assert row["mcp_execution"]["tool"] in tools
                financials = next(
                    row for row in raw_rows if row["operation"] == "bharatstock.get_financials"
                )
                arguments = {
                    "ticker": "INFY",
                    "exchange": "NSE",
                    "period_type": "annual",
                    "page": 1,
                    "page_size": 1,
                }
                Draft202012Validator(financials["schema"]).validate(arguments)
                plan = await call(
                    "margin_preview",
                    {
                        "operations": [
                            {"operation": financials["operation"], "arguments": arguments}
                        ]
                    },
                )
                assert plan["plan_id"]
                after = await call("margin_status")
                assert before["ledger"] == after["ledger"]
                assert before["company_finance_requests"] == after["company_finance_requests"]
                summary = {
                    "status": "passed",
                    "kind": "operator_sdk_discovery_and_preview_not_model_acceptance",
                    "package_version": before["package_version"],
                    "frontend_version": initialized.server_info.version,
                    "profile": "all",
                    "advertised_tools": len(tools),
                    "company_functions": matrix,
                    "raw_bharatstock_operations": [r["operation"] for r in raw_rows],
                    "tool_calls": len(observations),
                    "provider_attempt_delta": {
                        key: after["ledger"]["http_attempts"][key] - value
                        for key, value in before["ledger"]["http_attempts"].items()
                    },
                    "bharatstock_configured": before["providers"]["bharatstock"]["configured"],
                    "configured_http_limits": before["ledger"]["http_limits"],
                    "model_calls": 0,
                    "source_verification": False,
                }
                (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
                print(json.dumps({k: v for k, v in summary.items() if k != "company_functions"}))
    for path in output.iterdir():
        path.chmod(0o600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-socket", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    asyncio.run(main(parser.parse_args()))
