"""Official-SDK finance handoff/readiness regression with fictional fixtures only."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    root = Path(__file__).resolve().parents[1]
    package = (args.package_root or root / "src").resolve()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env.update(
        PYTHONPATH=str(package),
        MARGIN_BHARATSTOCK_REQUESTS="1",
        MARGIN_DRISHTI_REQUESTS="0",
        MARGIN_DRISHTI_CREDITS="0",
    )
    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "margin.interfaces.mcp",
            "--mode",
            "synthetic",
            "--tool-profile",
            args.tool_profile,
            "--record-file",
            str(output / "tools.jsonl"),
        ],
        env=env,
        cwd="/private/tmp" if Path("/private/tmp").exists() else "/tmp",
    )
    observations = []
    with (output / "stderr.txt").open("w") as err:
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                tools = {t.name: t for t in (await client.list_tools()).tools}

                async def call(name, values=None, error=False):
                    values = (values or {}) | {
                        "why": "Fictional SDK finance handoff test, no real provider/model calls."
                    }
                    Draft202012Validator(tools[name].input_schema).validate(values)
                    response = await client.call_tool(name, values)
                    body = response.structured_content
                    Draft202012Validator(tools[name].output_schema).validate(body)
                    assert response.is_error is error and body["mode"] == "synthetic"
                    observations.append({"tool": name, "arguments": values, "result": body})
                    return body

                initial = await call("margin_status")
                company_tool = (
                    "margin_company_data_readiness" if args.typed else "margin_company_finance"
                )
                preview = (
                    await call(
                        company_tool,
                        {"ticker": "SYNTHA"}
                        if args.typed
                        else {"function": "finance.company_data_readiness", "ticker": "SYNTHA"},
                    )
                )["data"]
                step = preview["next_steps"][0]
                assert preview["creates_plan_id"] is False and "plan_id" not in preview
                assert step["mcp_execution"]["tool"] == company_tool
                assert step["required_host_fields"] == ["idempotency_key"]
                assert step["requires_execution_authorization"] and not step["is_complete_input"]
                assert step["do_not_use_tools"] == ["margin_run"]
                inputs = step["bound_arguments"] | {
                    "idempotency_key": "fictional-readiness-handoff"
                }
                result = (await call(step["mcp_execution"]["tool"], inputs))["data"]
                assert (
                    result["status"] == "success"
                    and result["request_lifecycle"]["state"] == "finished"
                )
                report = result["report"]
                assert not report["rows"] and report["readiness"]
                assert report["readiness_scope"]["source_facts_verified"] is False
                assert report["readiness_scope"]["numeric_rows_expected"] is False
                valuation = report["valuation_readiness"]
                assert (
                    not valuation["valid_company_selector"]
                    and valuation["requires_explicit_assumptions"]
                )
                assert valuation["mcp_execution"]["tool"] == "margin_calculate_dcf"
                assert (await call(company_tool, inputs))["data"] == result
                if args.typed:
                    assert (
                        await call(
                            "margin_company_finance",
                            inputs | {"function": "finance.company_data_readiness"},
                        )
                    )["data"] == result
                    dcf = (
                        await call(
                            "margin_calculate_dcf",
                            {
                                "forecast_fcff": ["10", "10", "10"],
                                "wacc": "0.1",
                                "terminal_growth": "0",
                                "debt": "20",
                                "cash": "5",
                                "other_equity_adjustments": "-2",
                                "diluted_shares": "10",
                                "amount_unit": "INR",
                                "valuation_date": "2026-11-27",
                                "company_type": "non_financial",
                            },
                        )
                    )["data"]
                    assert abs(float(dcf["values"]["enterprise_value"]) - 100) < 1e-10
                    assert abs(float(dcf["values"]["equity_value"]) - 83) < 1e-10
                if args.tool_profile == "all":
                    rejected = await call(
                        "margin_run",
                        {
                            "session_id": initial["session_id"],
                            "plan_id": "deliberately-unissued-plan",
                            "idempotency_key": "fictional-unknown-plan",
                        },
                        error=True,
                    )
                    assert rejected["error"]["code"] == "plan_unavailable"
                    assert "creates NO generic plan_id" in rejected["error"]["recovery_guidance"]
                else:
                    assert set(tools) == {
                        "margin_status",
                        "margin_catalog",
                        "margin_company_data_readiness",
                        "margin_calculate_dcf",
                        "margin_company_finance",
                        "margin_calculate",
                    }
                    assert "session_id" not in initial
                final = (await call("margin_status"))["data"]
                assert final["ledger"]["http_attempts"] == {"bharatstock": 1, "drishti": 0}
    events = [json.loads(line) for line in (output / "tools.jsonl").read_text().splitlines()]
    assert len(events) == 2 * len(observations)
    summary = {
        "status": "passed",
        "kind": "fictional_software_fixtures_not_model_acceptance",
        "version": initialized.server_info.version,
        "tools": len(tools),
        "tool_profile": args.tool_profile,
        "typed_readiness_and_dcf": args.typed,
        "calls": len(observations),
        "recorded_events": len(events),
        "fixture_http_attempts": final["ledger"]["http_attempts"],
        "real_provider_calls": 0,
        "model_calls": 0,
        "package_root": str(package),
    }
    (output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for path in output.iterdir():
        path.chmod(0o600)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--tool-profile", choices=["all", "finance"], default="all")
    parser.add_argument("--typed", action="store_true")
    asyncio.run(main(parser.parse_args()))
