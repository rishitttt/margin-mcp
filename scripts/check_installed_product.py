"""Portable installed-wheel smoke: live mode, zero allowance, no keys or provider calls."""

from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import margin


async def main(args):
    root = Path(margin.__file__).resolve().parents[1]
    if "site-packages" not in str(root):
        raise ValueError("Run with the clean installed wheel, not an editable/source import.")
    version = importlib.metadata.version("margin-research")
    if args.expected_version and version != args.expected_version:
        raise ValueError("Installed version differs from requested release.")
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    env.update(
        MARGIN_BHARATSTOCK_REQUESTS="0", MARGIN_DRISHTI_REQUESTS="0", MARGIN_DRISHTI_CREDITS="0"
    )
    for module in (
        "margin.interfaces.mcp",
        "margin.interfaces.agent.cli",
        "margin.interfaces.mcp.backend",
    ):
        completed = subprocess.run(
            [sys.executable, "-m", module, "--help"], env=env, capture_output=True, timeout=20
        )
        if completed.returncode:
            raise ValueError("Installed entrypoint help failed; raw output withheld.")
    with tempfile.TemporaryDirectory(prefix="margin-installed-") as tmp:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "margin.interfaces.mcp", "--mode", "live", "--tool-profile", "all"],
            env=env,
            cwd=tmp,
        )
        with open(Path(tmp) / "stderr.txt", "w") as err:
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as client:
                    initialized = await client.initialize()
                    assert initialized.server_info.version == version
                    assert len((await client.list_tools()).tools) == 39
                    status = (await client.call_tool("margin_status", {})).structured_content[
                        "data"
                    ]
                    assert status["package_version"] == version and status["tool_profile"] == "all"
                    assert (
                        status["ledger"]["http_attempts"]
                        == status["ledger"]["http_limits"]
                        == {"bharatstock": 0, "drishti": 0}
                    )
                    assert (
                        "diagnostics" not in status
                        and status["report"]["rows"][-1]["status"] == "unknown"
                    )
                    dcf = await client.call_tool(
                        "margin_calculate_dcf",
                        {
                            "forecast_fcff": [10, 10, 10],
                            "wacc": 0.1,
                            "terminal_growth": 0,
                            "debt": 20,
                            "cash": 5,
                            "other_equity_adjustments": -2,
                            "diluted_shares": 10,
                            "amount_unit": "INR",
                            "valuation_date": "2026-11-27",
                            "company_type": "non_financial",
                        },
                    )
                    assert not dcf.is_error
                    rows = {
                        r["metric"]: r for r in dcf.structured_content["data"]["report"]["rows"]
                    }
                    assert rows["enterprise_value"]["display"] == "₹100.00"
                    assert rows["terminal_value"]["display"] == "₹100.00"
                    assert rows["terminal_present_value"]["display"] == "₹75.13"
    subprocess.run(
        [sys.executable, "-m", "pip", "check"], env=env, check=True, capture_output=True, timeout=30
    )
    summary = {
        "status": "passed",
        "version": version,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "package_root": str(root),
        "tools": 39,
        "provider_requests": 0,
        "entrypoints": "help passed",
        "pip_check": "passed",
    }
    if args.output:
        args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version")
    parser.add_argument("--output", type=Path)
    asyncio.run(main(parser.parse_args()))
