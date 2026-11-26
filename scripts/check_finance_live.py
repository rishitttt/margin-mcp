"""Explicit four-request real-data SDK check; never runs a model or changes active setup."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal, localcontext
from pathlib import Path
from types import SimpleNamespace

from check_finance_discovery import main as check_discovery
from jsonschema import Draft202012Validator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from margin.core.config import Settings
from margin.interfaces.agent.local_config import read_provider_env
from margin.interfaces.mcp.backend import Backend


async def main(args):
    if not args.confirm_live:
        raise ValueError("Pass --confirm-live only with a fresh four-request authorization.")
    root = Path(__file__).resolve().parents[1]
    output = args.output.expanduser().absolute()
    if subprocess.run(["git", "check-ignore", "-q", str(output)], cwd=root).returncode:
        raise ValueError("Use a new ignored reports/private output directory.")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    key = read_provider_env(args.credentials_file).get("BHARATSTOCK_API_KEY")
    if not key:
        raise ValueError("BharatStock key missing from the explicit private credentials file.")
    settings = Settings(
        mode="live",
        bharatstock_key=key,
        enabled_unverified=frozenset({"bharatstock.get_financials", "bharatstock.get_stock_quote"}),
        bharatstock_requests=4,
        drishti_requests=0,
        drishti_credits=0,
    )
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env["PYTHONPATH"] = str(root / "src")
    results, observations = [], []
    summary = {
        "kind": "real_data_operator_sdk_not_model_acceptance",
        "maximum_bharatstock_requests": 4,
        "model_calls": 0,
        "active_backend_changed": False,
    }
    try:
        with tempfile.TemporaryDirectory(
            prefix="margin-finance-",
            dir="/private/tmp" if Path("/private/tmp").exists() else "/tmp",
        ) as folder:
            socket = Path(folder) / "core.sock"
            async with Backend(socket, settings, record_dir=output / "logs") as backend:
                try:
                    await check_discovery(
                        SimpleNamespace(output=output / "discovery", backend_socket=socket)
                    )
                    params = StdioServerParameters(
                        command=sys.executable,
                        args=[
                            "-m",
                            "margin.interfaces.mcp",
                            "--backend-socket",
                            str(socket),
                            "--mode",
                            "live",
                            "--tool-profile",
                            "all",
                        ],
                        env=env,
                        cwd=folder,
                    )
                    with (output / "stderr.txt").open("w") as err:
                        async with stdio_client(params, errlog=err) as (read, write):
                            async with ClientSession(read, write) as client:
                                initialized = await client.initialize()
                                tools = {t.name: t for t in (await client.list_tools()).tools}

                                async def call(name, arguments=None):
                                    values = (arguments or {}) | {
                                        "why": "Operator authorized four-request finance check; not a model trial."
                                    }
                                    Draft202012Validator(tools[name].input_schema).validate(values)
                                    response = await client.call_tool(name, values)
                                    body = response.structured_content
                                    observations.append(
                                        {"tool": name, "arguments": values, "result": body}
                                    )
                                    (output / "observations.json").write_text(
                                        json.dumps(observations, indent=2) + "\n"
                                    )
                                    if response.is_error:
                                        raise ValueError(
                                            "MCP action rejected; inspect private capture, do not refetch."
                                        )
                                    return body

                                initial = await call("margin_status")
                                summary.update(
                                    package_version=initial["data"]["package_version"],
                                    frontend_version=initialized.server_info.version,
                                )
                                cases = [
                                    ("F01", "HINDUNILVR", "finance.company_margins"),
                                    ("F02", "INFY", "finance.company_growth"),
                                    ("F03", "INFY", "finance.company_data_readiness"),
                                ]
                                for case, ticker, function in cases:
                                    inputs = {
                                        "function": function,
                                        "ticker": ticker,
                                        "exchange": "NSE",
                                        "period_type": "annual",
                                        "basis": "consolidated",
                                        "execute": True,
                                        "idempotency_key": f"finance-discovery-{case}",
                                        "include_details": True,
                                    }
                                    answer = (await call("margin_company_finance", inputs))["data"]
                                    for _ in range(2):
                                        if answer["status"] != "running":
                                            break
                                        answer = (await call("margin_company_finance", inputs))[
                                            "data"
                                        ]
                                    if answer["status"] not in {"success", "partial", "incomplete"}:
                                        raise ValueError(
                                            "Provider/finance task did not succeed; stop without retrying data."
                                        )
                                    details = answer["details"]
                                    math = "not_applicable_readiness"
                                    if case in {"F01", "F02"} and answer["status"] == "success":
                                        values = details["values"]
                                        with localcontext() as context:
                                            context.prec = 34
                                            a, b = [
                                                Decimal(str(item["value"]))
                                                for item in details["inputs"]
                                            ]
                                            if case == "F01":
                                                assert (
                                                    Decimal(values["margin_percent"]) == a / b * 100
                                                )
                                            else:
                                                expected = (b - a) / a * 100
                                                assert (
                                                    Decimal(values["percentage_change"]) == expected
                                                )
                                                assert Decimal(values["absolute_change"]) == b - a
                                        math = "exact_decimal_check_passed"
                                    ledger = backend.service.ledger.snapshot()
                                    duplicate = (await call("margin_company_finance", inputs))[
                                        "data"
                                    ]
                                    assert (
                                        duplicate == answer
                                        and backend.service.ledger.snapshot() == ledger
                                    )
                                    results.append(
                                        {
                                            "case": case,
                                            "ticker": ticker,
                                            "function": function,
                                            "status": answer["status"],
                                            "report": answer["report"],
                                            "math_check": math,
                                            "same_key_repeat": "no_extra_http_attempt",
                                            "source_verification": "provider_only_unverified",
                                        }
                                    )
                                    print(
                                        json.dumps(
                                            {
                                                "case": case,
                                                "status": answer["status"],
                                                "math_check": math,
                                            }
                                        ),
                                        flush=True,
                                    )
                                exact = (
                                    await call(
                                        "margin_catalog",
                                        {
                                            "group": "retrieval",
                                            "name": "bharatstock.get_stock_quote",
                                            "include_schemas": True,
                                        },
                                    )
                                )["data"]["groups"]["retrieval"][0]
                                raw = {"ticker": "HINDUNILVR", "exchange": "NSE"}
                                Draft202012Validator(exact["schema"]).validate(raw)
                                plan = (
                                    await call(
                                        "margin_preview",
                                        {
                                            "operations": [
                                                {"operation": exact["operation"], "arguments": raw}
                                            ]
                                        },
                                    )
                                )["data"]
                                run = (
                                    await call(
                                        "margin_run",
                                        {
                                            "session_id": initial["session_id"],
                                            "plan_id": plan["plan_id"],
                                            "idempotency_key": "finance-discovery-F04",
                                        },
                                    )
                                )["data"]
                                for _ in range(6):
                                    if run["status"] not in {"queued", "running"}:
                                        break
                                    await asyncio.sleep(0.5)
                                    run = (
                                        await call(
                                            "margin_run_status",
                                            {"run_id": run["run_id"], "wait_seconds": 10},
                                        )
                                    )["data"]
                                result = (
                                    await call(
                                        "margin_result",
                                        {
                                            "run_id": run["run_id"],
                                            "operation_id": run["operations"][0]["operation_id"],
                                        },
                                    )
                                )["data"]
                                assert result["status"] == "success", (
                                    "Snapshot did not succeed; do not refetch."
                                )
                                results.append(
                                    {
                                        "case": "F04",
                                        "ticker": "HINDUNILVR",
                                        "operation": exact["operation"],
                                        "result": result,
                                        "source_verification": "provider_only_unverified",
                                    }
                                )
                                final = (await call("margin_status"))["data"]
                                assert final["ledger"]["http_attempts"] == {
                                    "bharatstock": 4,
                                    "drishti": 0,
                                }
                                summary.update(
                                    status="completed_four_requests",
                                    ledger=final["ledger"],
                                    cases=results,
                                )
                finally:
                    summary["ledger_on_exit"] = backend.service.ledger.snapshot()
    finally:
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        for path in output.rglob("*"):
            if path.is_file():
                path.chmod(0o600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--confirm-live", action="store_true")
    asyncio.run(main(parser.parse_args()))
