"""JSON CLI shared by humans, skills and an optional external pilot observer."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from margin.core.contracts import DomainError
from margin.interfaces.agent.client import AgentClient, BridgeError, public_output


def parser():
    p = argparse.ArgumentParser(
        description="Call a running local Margin backend; JSON output only."
    )
    p.add_argument("--url", default=os.getenv("MARGIN_BACKEND_URL", "http://127.0.0.1:8765"))
    p.add_argument(
        "--why",
        help="One-line visible explanation of this tool choice (1–280 characters); not hidden reasoning",
    )
    p.add_argument(
        "--expect-mode", choices=["live", "synthetic"], default=os.getenv("MARGIN_EXPECT_MODE")
    )
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Local status and shared allowances; no provider calls")
    catalog = commands.add_parser("catalog", help="Schemas, availability and estimated costs")
    catalog.add_argument("--name", help="Filter by operation/function name substring")
    workflows = commands.add_parser(
        "workflows", help="Local citation/sentiment review schemas; no provider calls"
    )
    workflows.add_argument("--name")
    imported = commands.add_parser(
        "review-sources", help="Import retained provider text; never fetch"
    )
    imported.add_argument("run_id")
    imported.add_argument("operation_id")
    imported.add_argument("--issuer", required=True)
    for name in ("preview", "company-preview", "review"):
        sub = commands.add_parser(name, help="Validate a JSON plan without provider calls")
        group = sub.add_mutually_exclusive_group(required=True)
        group.add_argument("--json", dest="inline_json")
        group.add_argument("--file", help="Read a JSON object; '-' reads stdin")
    run = commands.add_parser("run", help="Submit a previously previewed plan once")
    run.add_argument("plan_id")
    run.add_argument("--key", required=True, help="Unique 8–100 character idempotency key")
    run.add_argument("--backend-id", required=True, help="Use the backend_id returned by preview")
    for name in ("run-status", "wait", "cancel"):
        sub = commands.add_parser(name)
        sub.add_argument("run_id")
        if name == "wait":
            sub.add_argument(
                "--seconds", type=int, choices=range(0, 61), default=20, metavar="0..60"
            )
    for name in ("result", "facts"):
        sub = commands.add_parser(name, help="Read retained output; never refetch")
        sub.add_argument("run_id")
        sub.add_argument("operation_id")
        if name == "facts":
            sub.add_argument(
                "--money-unit",
                choices=["auto", "unknown", "INR", "INR_thousand", "INR_lakh", "INR_crore"],
                default="auto",
            )
    commands.add_parser("sources", help="List retained financial sources")
    commands.add_parser("runs", help="Recent local control records")
    commands.add_parser(
        "connect-drishti", help="Explicit upstream metadata connection; may consume HTTP allowance"
    )
    return p


def body(args):
    try:
        if args.inline_json is not None:
            raw = args.inline_json.encode()
        elif args.file == "-":
            raw = sys.stdin.buffer.read(65537)
        else:
            with Path(args.file).open("rb") as f:
                raw = f.read(65537)
        if len(raw) > 65536:
            raise ValueError

        def invalid(_):
            raise ValueError

        value = json.loads(raw, parse_constant=invalid)
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (OSError, ValueError, RecursionError):
        raise BridgeError(
            "invalid_input", "Supply a finite JSON object of at most 64 KiB."
        ) from None


def dispatch(client, args, status):
    c = args.command
    if c == "status":
        return status
    if c == "catalog":
        return client.catalog(args.name)
    if c == "workflows":
        return client.workflows(args.name)
    if c == "review":
        return client.review(body(args))
    if c == "review-sources":
        return client.review_sources(args.run_id, args.operation_id, args.issuer)
    if c in {"preview", "company-preview"}:
        return client.preview(body(args), company=c == "company-preview")
    if c == "run":
        return client.run(args.plan_id, args.key, args.backend_id)
    if c == "run-status":
        return client.run_status(args.run_id)
    if c == "wait":
        return client.wait(args.run_id, args.seconds)
    if c in {"result", "facts"}:
        return client.result(
            args.run_id,
            args.operation_id,
            facts=c == "facts",
            money_unit=getattr(args, "money_unit", None),
        )
    if c == "sources":
        return client.sources()
    if c == "runs":
        return client.runs()
    if c == "cancel":
        return client.cancel(args.run_id)
    return client.connect()


def main(
    argv=None,
    *,
    client_factory=AgentClient,
    observer=None,
    output=None,
    decision_observer=None,
    output_filter=public_output,
):
    args = parser().parse_args(argv)
    client = None
    code = 0
    why = None
    decision_id = None
    try:
        if args.why is not None:
            if not args.why.strip() or len(args.why) > 280 or any(ord(c) < 32 for c in args.why):
                raise BridgeError(
                    "invalid_summary", "Supply one nonempty line of at most 280 characters."
                )
            why = output_filter({"decision_summary": args.why.strip()})["decision_summary"]
            if decision_observer:
                try:
                    decision_id = decision_observer(args.command, why)["event_id"]
                except OSError:
                    raise BridgeError(
                        "recording",
                        "Cannot record the decision summary; action was not dispatched.",
                    ) from None
            print(f"Why: {why}", file=sys.stderr)
        client = client_factory(args.url, expect_mode=args.expect_mode)
        status = client.status()
        result = client.envelope(dispatch(client, args, status))
    except (BridgeError, DomainError) as e:
        code = 2
        result = {
            "bridge_version": "1.0",
            "backend_id": client.backend_id if client else None,
            "mode": client.mode if client else None,
            "error": {"code": e.code, "message": e.message, "uncertain": e.uncertain},
        }
    finally:
        if client:
            client.close()
    if why is not None:
        result["decision_summary"] = why
    if decision_id is not None:
        result["decision_event_id"] = decision_id
    try:
        result = output_filter(result)
    except DomainError:
        code = 2
        result = {"error": {"code": "unsafe_output", "message": "Local output was withheld."}}
    if observer:
        # Deliberately excludes raw CLI input: rejected requests can contain credentials.
        # Successful preview responses already contain full backend-validated arguments.
        try:
            observer(args.command, result, code)
        except (OSError, BridgeError):
            # Preserve the actual result if recording fails after dispatch. Never repeat it.
            print(
                "Pilot recording failed after the command. Inspect the result; do not resubmit automatically.",
                file=sys.stderr,
            )
            code = 3
    print(json.dumps(result, ensure_ascii=False, allow_nan=False), file=output or sys.stdout)
    return code
