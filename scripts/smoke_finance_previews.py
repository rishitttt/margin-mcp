"""Official-SDK finance discovery/preview guards at zero allowance; no real data/model."""

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
from mcp.shared.exceptions import MCPError


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
        MARGIN_BHARATSTOCK_REQUESTS="0",
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
            "finance",
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
                init = await client.initialize()
                tools = {t.name: t for t in (await client.list_tools()).tools}
                assert len(tools) == 4 and len(init.instructions.encode()) < 3600

                async def call(name, values=None):
                    values = values or {}
                    Draft202012Validator(tools[name].input_schema).validate(values)
                    response = await client.call_tool(name, values)
                    body = response.structured_content
                    Draft202012Validator(tools[name].output_schema).validate(body)
                    assert not response.is_error, body
                    assert json.loads(response.content[0].text) == body
                    observations.append({"tool": name, "arguments": values, "result": body})
                    return body["data"]

                initial = await call("margin_status")
                assert initial["tool_profile"] == "finance"
                rows = (await call("margin_catalog"))["groups"]["company"]
                assert len(rows) == 9
                for row in rows:
                    assert row["mcp_execution"]["tool"] == "margin_company_finance"
                    preview = await call(
                        "margin_company_finance",
                        {"function": row["function"], "ticker": "SYNTHA", "execute": False},
                    )
                    summary = preview["preview_summary"]
                    assert summary["status"] == "preview"
                    assert summary["next_tool_for_execution"] == "margin_company_finance"
                    assert summary["missing_fields_for_execution"] == ["idempotency_key"]
                    assert summary["missing_fields_for_preview"] == []
                    assert not summary["preview_authorizes_execution"]
                    assert summary["provider_requests_made"] == {"bharatstock": 0, "drishti": 0}
                # Deliberate software guard probe, not a model or preview-authorized action.
                values = {
                    "function": "finance.company_margins",
                    "ticker": "SYNTHA",
                    "execute": True,
                    "idempotency_key": "fictional-zero-budget",
                }
                blocked = await call("margin_company_finance", values)
                assert (
                    blocked["status"] == "blocked"
                    and blocked["error"]["scope"] == "local_process_allowance"
                )
                assert blocked["error"]["observed_account_balance"] is None
                assert await call("margin_company_finance", values) == blocked
                with_profile = (
                    await call(
                        "margin_catalog",
                        {
                            "group": "calculations",
                            "name": "finance.calculate_margins",
                            "include_schemas": True,
                        },
                    )
                )["groups"]["calculations"][0]
                assert with_profile["mcp_execution"]["tool"] == "margin_calculate"
                with_error = False
                try:
                    await client.call_tool("margin_run", {})
                except MCPError:
                    with_error = True
                assert with_error
                final = await call("margin_status")
                assert (
                    final["ledger"]["http_attempts"]
                    == final["ledger"]["http_limits"]
                    == {"bharatstock": 0, "drishti": 0}
                )
    events = [json.loads(line) for line in (output / "tools.jsonl").read_text().splitlines()]
    assert len(events) == 2 * len(observations)
    summary = {
        "status": "passed",
        "kind": "fictional_software_not_model_acceptance",
        "version": init.server_info.version,
        "tools": len(tools),
        "calls": len(observations),
        "recorded_events": len(events),
        "unrecorded_hidden_tool_rejections": 1,
        "real_provider_calls": 0,
        "fixture_provider_attempts": final["ledger"]["http_attempts"],
        "model_calls": 0,
        "instruction_bytes": len(init.instructions.encode()),
        "tool_definition_bytes": len(
            json.dumps([t.model_dump(by_alias=True) for t in tools.values()]).encode()
        ),
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
    asyncio.run(main(parser.parse_args()))
