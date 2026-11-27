"""Goal-only local-model preview probe over an isolated zero-allowance MCP session.

Uses an already loaded LM Studio model. Records native tool calls/final prose, not
hidden reasoning. This API harness is a distinct condition from LM Studio's chat UI.
No real credentials are loaded and no provider requests are allowed.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import MCPError

TASKS = {
    "margins": "Use the connected Margin MCP to preview HINDUNILVR (NSE) annual consolidated profit margin. Do not execute or fetch data. Explain the exact next tool, bound inputs and missing requirements. Do not invent a plan ID or financial values.",
    "readiness": "Use Margin MCP to preview one annual consolidated INFY financial response that would determine which profitability, cash-conversion and liquidity calculations the returned fields support. Do not fetch or calculate values yet. Explain how the later readiness result and valuation prerequisites would be read.",
}


def public_content(value):
    """Drop tagged reasoning; never store reasoning_content or raw HTTP responses."""
    text = value if isinstance(value, str) else ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    if "<think>" in text:
        text = text.split("<think>", 1)[0]
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[-1]
    return text.strip()


async def main(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    # Refuse auto-loading or changing the model. Local API metadata is read-only.
    async with httpx.AsyncClient(base_url="http://127.0.0.1:1234", timeout=150) as api:
        models = (await api.get("/api/v1/models")).raise_for_status().json()["models"]
        model = next((m for m in models if m.get("key") == args.model), None)
        if not model or not model.get("loaded_instances"):
            raise ValueError("Requested model must already be loaded; no model change was made.")
        instance = model["loaded_instances"][0]
        package = (args.package_root or Path(__file__).resolve().parents[1] / "src").resolve()
        env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("MARGIN_")
            and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
        }
        env.update(
            PYTHONPATH=str(package),
            BHARATSTOCK_API_KEY="local-preview-probe-not-a-real-key",
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
                "live",
                "--tool-profile",
                args.tool_profile,
                "--record-file",
                str(output / "tools.jsonl"),
            ],
            env=env,
            cwd="/private/tmp" if Path("/private/tmp").exists() else "/tmp",
        )
        cases = {}
        with (output / "stderr.txt").open("w") as err:
            async with stdio_client(params, errlog=err) as (read, write):
                async with ClientSession(read, write) as mcp:
                    init = await mcp.initialize()
                    advertised = (await mcp.list_tools()).tools
                    assert len(advertised) == (39 if args.tool_profile == "all" else 6)
                    tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": t.name,
                                "description": t.description,
                                "parameters": t.input_schema,
                            },
                        }
                        for t in advertised
                    ]
                    for name, task in TASKS.items():
                        messages = [
                            {"role": "system", "content": init.instructions},
                            {"role": "user", "content": task},
                        ]
                        case = {"prompt": task, "turns": [], "status": "turn_limit", "final": None}
                        cases[name] = case
                        for turn in range(6):
                            response = await api.post(
                                "/v1/chat/completions",
                                json={
                                    "model": instance["id"],
                                    "messages": messages,
                                    "tools": tools,
                                    "tool_choice": "auto",
                                    "temperature": 0,
                                    "max_tokens": 2400,
                                },
                            )
                            if response.status_code != 200:
                                case.update(
                                    status="model_http_error", http_status=response.status_code
                                )
                                break  # no raw error body or automatic retry
                            raw = response.json()
                            choice = raw["choices"][0]
                            message = choice["message"]
                            content = public_content(message.get("content"))
                            calls = message.get("tool_calls") or []
                            trace = {
                                "turn": turn + 1,
                                "usage": raw.get("usage"),
                                "finish_reason": choice.get("finish_reason"),
                                "calls": [],
                            }
                            case["turns"].append(trace)
                            if not calls:
                                case.update(
                                    status="finished"
                                    if choice.get("finish_reason") != "length"
                                    else "generation_limit",
                                    final=content,
                                )
                                break
                            if len(calls) > 4:
                                case["status"] = "call_limit"
                                break
                            messages.append(
                                {"role": "assistant", "content": None, "tool_calls": calls}
                            )
                            for call in calls:
                                function = call["function"]
                                raw_args = function.get("arguments", "{}")
                                try:
                                    values = json.loads(raw_args)
                                except (ValueError, TypeError):
                                    values = None
                                if values is None:
                                    result = {
                                        "error": {
                                            "code": "host_parse_error",
                                            "message": "Tool arguments must be valid JSON.",
                                        }
                                    }
                                else:
                                    try:
                                        returned = await mcp.call_tool(function["name"], values)
                                        result = returned.structured_content or {
                                            "error": {"code": "missing_structured_result"}
                                        }
                                    except MCPError:
                                        result = {
                                            "error": {
                                                "code": "host_tool_rejected",
                                                "message": "Call rejected by the advertised MCP interface. Use only its exact names and schemas.",
                                            }
                                        }
                                trace["calls"].append(
                                    {
                                        "tool": function["name"],
                                        "arguments": values,
                                        "result": result,
                                    }
                                )
                                messages.append(
                                    {
                                        "role": "tool",
                                        "tool_call_id": call["id"],
                                        "content": json.dumps(result),
                                    }
                                )
                            print(
                                json.dumps(
                                    {
                                        "case": name,
                                        "turn": turn + 1,
                                        "tools": [c["tool"] for c in trace["calls"]],
                                    }
                                ),
                                flush=True,
                            )
                            (output / f"{name}.json").write_text(json.dumps(case, indent=2) + "\n")
                        (output / f"{name}.json").write_text(json.dumps(case, indent=2) + "\n")
                        print(json.dumps({"case": name, "status": case["status"]}), flush=True)
                    # Operator status is deliberately outside the model cohort.
                    final = (await mcp.call_tool("margin_status", {})).structured_content["data"]
                    assert final["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}
        summary = {
            "kind": "actual_local_model_API_harness_not_chat_UI_replication",
            "model": args.model,
            "loaded_config": instance.get("config"),
            "version": init.server_info.version,
            "profile": args.tool_profile,
            "tools": len(tools),
            "app_chat_preset": "not supplied; initialization instructions only",
            "temperature": 0,
            "maximum_output_tokens_per_turn": 2400,
            "maximum_turns_per_case": 6,
            "provider_attempts": final["ledger"]["http_attempts"],
            "provider_limits": final["ledger"]["http_limits"],
            "hidden_reasoning_recorded": False,
            "active_backend_changed": False,
            "case_statuses": {k: v["status"] for k, v in cases.items()},
            "model_requests": sum(len(v["turns"]) for v in cases.values()),
        }
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        for path in output.iterdir():
            path.chmod(0o600)
        print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--tool-profile", choices=["all", "finance"], default="all")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--package-root", type=Path)
    asyncio.run(main(parser.parse_args()))
