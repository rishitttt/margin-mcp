"""Installed/source shared-backend acceptance; fictional data and zero real API calls."""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(args):
    args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    output = args.output.resolve()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env.update(
        MARGIN_BHARATSTOCK_REQUESTS="2", MARGIN_DRISHTI_REQUESTS="0", MARGIN_DRISHTI_CREDITS="0"
    )
    if args.package_root:
        env["PYTHONPATH"] = str(args.package_root.resolve())
    observations = []
    with tempfile.TemporaryDirectory(
        prefix="margin-accept-", dir="/private/tmp" if Path("/private/tmp").exists() else "/tmp"
    ) as temp:
        address = str(Path(temp) / "s")
        with (
            (output / "backend-stderr.txt").open("w") as backend_stderr,
            (output / "frontend-stderr.txt").open("w") as stderr,
        ):
            process = subprocess.Popen(
                [
                    str(args.python),
                    "-m",
                    "margin.interfaces.mcp.backend",
                    "--socket",
                    address,
                    "--mode",
                    "synthetic",
                    "--record-dir",
                    str(output / "logs"),
                ],
                env=env,
                cwd=temp,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=backend_stderr,
            )
            try:
                for _ in range(200):
                    if Path(address).exists():
                        break
                    if process.poll() is not None:
                        raise AssertionError(
                            "Fictional backend failed to start; inspect private stderr."
                        )
                    await asyncio.sleep(0.05)
                else:
                    raise AssertionError("Fictional backend startup timed out.")
                params = StdioServerParameters(
                    command=str(args.python),
                    args=[
                        "-m",
                        "margin.interfaces.mcp",
                        "--backend-socket",
                        address,
                        "--mode",
                        "synthetic",
                    ],
                    env=env,
                    cwd=temp,
                )

                async def call(client, name, values=None, expect_error=False):
                    values = (values or {}) | {
                        "why": "Test fictional shared-state acceptance without real provider calls."
                    }
                    response = await client.call_tool(name, values)
                    assert response.is_error is expect_error, response.content
                    body = response.structured_content
                    assert body["mode"] == "synthetic"
                    observations.append({"tool": name, "arguments": values, "result": body})
                    return body

                async with stdio_client(params, errlog=stderr) as (read, write):
                    async with ClientSession(read, write) as client:
                        initialized = await client.initialize()
                        assert len((await client.list_tools()).tools) == 35
                        status = await call(client, "margin_status")
                        assert status["data"]["state_owner"] == "shared_backend_process"
                        assert not any(status["data"]["ledger"]["http_attempts"].values())
                        assert status["data"]["package_version"] == initialized.server_info.version
                        for tool in (
                            "margin_preview_news",
                            "margin_preview_announcements",
                            "margin_preview_earnings",
                            "margin_preview_earnings_filing",
                        ):
                            preview_arguments = (
                                {"earnings_id": "fictional-filing-001", "detailed": True}
                                if tool.endswith("filing")
                                else {
                                    "symbols": ["SYNTHA"],
                                    "lookback_days": 7,
                                    "page": 1,
                                    "limit": 1,
                                }
                            )
                            held = await call(client, tool, preview_arguments, expect_error=True)
                            assert held["error"]["code"] == "credit_budget"
                        preview = await call(
                            client,
                            "margin_preview",
                            {
                                "operations": [
                                    {
                                        "operation": "bharatstock.get_financials",
                                        "arguments": {
                                            "ticker": "SYNTHA",
                                            "exchange": "NSE",
                                            "period_type": "annual",
                                            "page": 1,
                                            "page_size": 2,
                                        },
                                    }
                                ]
                            },
                        )
                submission = {
                    "session_id": preview["session_id"],
                    "plan_id": preview["data"]["plan_id"],
                    "idempotency_key": "shared-installed-once",
                    "wait_seconds": 2,
                }
                async with stdio_client(params, errlog=stderr) as (read, write):
                    async with ClientSession(read, write) as client:
                        await client.initialize()
                        run = (await call(client, "margin_run", submission))["data"]
                        assert run["status"] == "completed"
                async with stdio_client(params, errlog=stderr) as (read, write):
                    async with ClientSession(read, write) as client:
                        await client.initialize()
                        again = (await call(client, "margin_run", submission))["data"]
                        assert again["run_id"] == run["run_id"]
                        ids = {
                            "run_id": run["run_id"],
                            "operation_id": run["operations"][0]["operation_id"],
                        }
                        result = (await call(client, "margin_result", ids))["data"]
                        metric = next(
                            m
                            for m in result["financial_view"]["rows"][0]["metrics"]
                            if m["metric"] == "revenue"
                        )
                        raw = result["payload"]["data"][0]["revenue"]
                        assert Decimal(metric["value"]) == Decimal(str(raw)) / Decimal(10000000)
                        facts = (await call(client, "margin_facts", ids))["data"]["facts"]
                        latest = max(f["period_end"] for f in facts if f["period_end"])
                        current = {f["metric"]: f for f in facts if f["period_end"] == latest}
                        await call(
                            client,
                            "margin_calculate_margins",
                            {"profit": current["net_profit"], "revenue": current["revenue"]},
                        )
                        await call(
                            client,
                            "margin_convert_units",
                            {"value": current["revenue"], "target_unit": "INR_crore"},
                        )
                        fresh_inputs = {
                            "function": "finance.company_margins",
                            "ticker": "SYNTHA",
                            "execute": True,
                            "idempotency_key": "shared-fresh-finance-once",
                        }
                        fresh = await call(client, "margin_company_finance", fresh_inputs)
                        assert fresh["data"]["status"] == "success"
                # A fourth frontend repeats the same direct request after disconnect.
                async with stdio_client(params, errlog=stderr) as (read, write):
                    async with ClientSession(read, write) as client:
                        await client.initialize()
                        duplicate = await call(client, "margin_company_finance", fresh_inputs)
                        assert duplicate["data"] == fresh["data"]
                        inspected = await call(
                            client,
                            "margin_company_finance",
                            fresh_inputs | {"include_details": True},
                        )
                        assert inspected["data"]["report"] == fresh["data"]["report"]
                        assert "details" in inspected["data"] and "details" not in fresh["data"]
                        final = await call(client, "margin_status")
                        assert final["session_id"] == status["session_id"]
                        assert final["data"]["ledger"]["http_attempts"] == {
                            "bharatstock": 2,
                            "drishti": 0,
                        }
            finally:
                if process.poll() is None:
                    stop = subprocess.run(
                        [
                            str(args.python),
                            "-m",
                            "margin.interfaces.mcp.backend",
                            "--socket",
                            address,
                            "--stop",
                        ],
                        cwd=temp,
                        env=env,
                        capture_output=True,
                        timeout=10,
                    )
                    if stop.returncode:
                        process.terminate()
                process.wait(timeout=10)
    logs = list((output / "logs").glob("*.jsonl"))
    events = [json.loads(line) for p in logs for line in p.read_text().splitlines()]
    assert len(logs) == 1 and len(events) == 2 * len(observations)
    summary = {
        "status": "passed",
        "mode": "fictional_software_fixtures",
        "version": initialized.server_info.version,
        "protocol": initialized.protocol_version,
        "stdio_frontends": 4,
        "tools": 35,
        "calls": len(observations),
        "recorded_events": len(events),
        "stable_backend_identity": True,
        "duplicate_dispatches": 0,
        "fictional_provider_attempts": 2,
        "real_provider_calls": 0,
        "model_calls": 0,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")
    for path in output.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
