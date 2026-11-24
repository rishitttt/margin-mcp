"""Optional private tool-observation recorder. The product never imports this module."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
from contextlib import contextmanager
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import uuid4

from margin.evidence.sanitize import Sanitizer
from margin.interfaces.agent.cli import main as agent_main
from margin.interfaces.agent.client import AgentClient, BridgeError
from margin.interfaces.agent.local_config import read_provider_env

MAX_LOG_BYTES = 50 * 1024 * 1024


def timestamp():
    return datetime.now(UTC).isoformat()


def write_private(path, data):
    with path.open("x", encoding="utf-8") as stream:
        path.chmod(0o600)
        json.dump(data, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


@contextmanager
def locked_session(directory):
    # Serialize pilot calls without changing the backend's own cross-client ledger.
    if not (directory / "session.json").is_file():
        raise BridgeError("session_missing", "Initialize this private session first.")
    with (directory / ".lock").open("a") as lock:
        (directory / ".lock").chmod(0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        metadata = json.loads((directory / "session.json").read_text())
        if date.fromisoformat(metadata["retention_until"]) < datetime.now(UTC).date():
            raise BridgeError(
                "retention_expired",
                "Pilot retention has expired; review/delete the private artifacts.",
            )
        if (directory / "answer.json").exists():
            raise BridgeError(
                "session_finished", "This pilot is finished; start a separate session."
            )
        log = directory / "events.jsonl"
        # Reserve enough space for one maximum bridge response before any action.
        if log.exists() and log.stat().st_size > MAX_LOG_BYTES - 5 * 1024 * 1024:
            raise BridgeError("recording_capacity", "Private pilot observation capacity reached.")
        yield metadata


class Session:
    def __init__(self, directory, metadata):
        self.directory, self.metadata = directory, metadata
        credentials = (
            read_provider_env(metadata["redaction_env_file"])
            if metadata.get("redaction_env_file")
            else {}
        )
        self.sanitizer = Sanitizer(credentials.values())

    def check_backend(self, client):
        if client.mode != self.metadata["mode"]:
            raise BridgeError("mode_mismatch", "Pilot mode differs from the running backend.")
        path = self.directory / "backend.json"
        if path.exists():
            if json.loads(path.read_text())["backend_id"] != client.backend_id:
                raise BridgeError(
                    "backend_changed",
                    "Pilot backend changed. Reconcile budgets and start a new session.",
                )
        else:
            write_private(path, {"backend_id": client.backend_id, "mode": client.mode})

    def observe(self, command, response, exit_code):
        event = {
            "event_version": "1.1",
            "event_type": "tool_observation",
            "event_id": uuid4().hex,
            "observed_at": timestamp(),
            "command": command,
            "exit_code": exit_code,
            "response": self.sanitizer.clean(response),
        }
        self.append(event)

    def append(self, event):
        event = self.sanitizer.clean(event)
        path = self.directory / "events.jsonl"
        descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def note(self, kind, text, run_id=None, operation_id=None, command=None):
        if not text.strip() or len(text.encode()) > 4096:
            raise BridgeError("note_size", "Supply a nonempty visible summary of at most 4 KiB.")
        from margin.interfaces.agent.client import identifier

        event = {
            "event_version": "1.1",
            "event_id": uuid4().hex,
            "event_type": "agent_summary",
            "summary_kind": kind,
            "origin": "agent_self_report",
            "observed_at": timestamp(),
            "summary": self.sanitizer.text(text),
            "is_hidden_reasoning": False,
        }
        if run_id:
            event["run_id"] = identifier(run_id)
        if command:
            event["command"] = command
        if operation_id:
            if not run_id:
                raise BridgeError("invalid_input", "An operation reference needs its run ID.")
            event["operation_id"] = identifier(operation_id)
        self.append(event)
        return {
            "status": "recorded",
            "event_id": event["event_id"],
            "summary_kind": kind,
            "origin": "agent_self_report",
        }

    def client(self, url, **kwargs):
        session = self

        class PinnedClient(AgentClient):
            def status(self):
                result = super().status()
                session.check_backend(self)
                return result

        return PinnedClient(url, **kwargs)

    def decision(self, command, summary):
        return self.note("decision", summary, command=command)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--session", required=True, type=Path)
    commands = p.add_subparsers(dest="action", required=True)
    init = commands.add_parser("init")
    init.add_argument("--task-file", type=Path, required=True)
    init.add_argument("--mode", choices=["live", "synthetic"], required=True)
    init.add_argument("--retention-until", type=date.fromisoformat, required=True)
    init.add_argument(
        "--redact-env-file", type=Path, help="Local provider-key file used only for redaction"
    )
    init.add_argument(
        "--agent-label",
        default="unspecified",
        help="Operator-supplied host/model label, not independently verified",
    )
    init.add_argument(
        "--allow-live-recording",
        action="store_true",
        help="Explicitly authorize private retention for this scoped pilot; does not establish provider rights",
    )
    commands.add_parser("call", add_help=False)
    note = commands.add_parser(
        "note", help="Record a brief visible explanation, not hidden reasoning"
    )
    note.add_argument("--kind", choices=["decision", "observation", "limitation"], required=True)
    note.add_argument("--file", type=Path, required=True)
    note.add_argument("--run-id")
    note.add_argument("--operation-id")
    finish = commands.add_parser("finish")
    finish.add_argument("--answer-file", type=Path, required=True)
    args, remaining = p.parse_known_args(argv)
    directory = args.session.expanduser().absolute()
    try:
        if args.action == "init":
            if remaining:
                p.error("Unexpected initialization arguments.")
            if args.mode == "live" and not args.allow_live_recording:
                raise BridgeError(
                    "recording_scope",
                    "Live recording needs explicit --allow-live-recording after applicable scope checks.",
                )
            if args.retention_until < datetime.now(UTC).date():
                raise BridgeError("retention_expired", "Choose an unexpired retention review date.")
            task = args.task_file.read_text(encoding="utf-8")
            if len(task.encode()) > 64 * 1024:
                raise BridgeError("task_size", "Task text exceeds 64 KiB.")
            redaction_path = (
                args.redact_env_file.expanduser().resolve() if args.redact_env_file else None
            )
            credentials = read_provider_env(redaction_path) if redaction_path else {}
            sanitizer = Sanitizer(credentials.values())
            if len(args.agent_label.encode()) > 256:
                raise BridgeError("invalid_input", "Agent label exceeds 256 bytes.")
            directory.mkdir(parents=True, exist_ok=False, mode=0o700)
            directory.chmod(0o700)
            write_private(
                directory / "session.json",
                {
                    "session_version": "1.1",
                    "instrumentation": "visible-summaries-v1",
                    "agent_label": sanitizer.text(args.agent_label),
                    "redaction_env_file": str(redaction_path) if redaction_path else None,
                    "created_at": timestamp(),
                    "mode": args.mode,
                    "retention_until": args.retention_until.isoformat(),
                    "live_recording_authorized": args.allow_live_recording,
                    "task": sanitizer.text(task),
                    "scope": "Private pilot observations, not frozen replay or independently graded evaluation",
                },
            )
            print(json.dumps({"session": str(directory), "mode": args.mode}))
            return 0
        with locked_session(directory) as metadata:
            session = Session(directory, metadata)
            if args.action == "call":
                return agent_main(
                    remaining,
                    client_factory=session.client,
                    observer=session.observe,
                    decision_observer=session.decision,
                    output_filter=session.sanitizer.clean,
                )
            if args.action == "note":
                if remaining:
                    p.error("Unexpected summary arguments.")
                with args.file.open("r", encoding="utf-8") as stream:
                    text = stream.read(4097)
                print(json.dumps(session.note(args.kind, text, args.run_id, args.operation_id)))
                return 0
            if remaining:
                p.error("Unexpected finish arguments.")
            answer = args.answer_file.read_text(encoding="utf-8")
            if len(answer.encode()) > 64 * 1024:
                raise BridgeError("answer_size", "Final answer exceeds 64 KiB.")
            log = directory / "events.jsonl"
            counts = {"agent_summaries": 0, "tool_observations": 0}
            if log.exists():
                with log.open() as stream:
                    for line in stream:
                        event = json.loads(line)
                        counts[
                            "agent_summaries"
                            if event.get("event_type") == "agent_summary"
                            else "tool_observations"
                        ] += 1
            warnings = (
                []
                if counts["agent_summaries"]
                else [
                    "No visible agent summaries were submitted; reasoning-summary coverage is missing."
                ]
            )
            write_private(
                directory / "answer.json",
                {
                    "finished_at": timestamp(),
                    "answer": session.sanitizer.text(answer),
                    "independently_graded": False,
                    "log_counts": counts,
                    "warnings": warnings,
                    "coverage": "Instrumented tool observations and submitted summaries; not a full host transcript or hidden reasoning.",
                },
            )
            print(
                json.dumps(
                    {
                        "status": "finished",
                        "independently_graded": False,
                        "log_counts": counts,
                        "warnings": warnings,
                    }
                )
            )
            return 0
    except (OSError, ValueError, KeyError):
        print(
            json.dumps(
                {
                    "error": {
                        "code": "session_io",
                        "message": "Cannot read/write this pilot session; no automatic retry.",
                    }
                }
            )
        )
        return 2
    except BridgeError as e:
        print(
            json.dumps({"error": {"code": e.code, "message": e.message, "uncertain": e.uncertain}})
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
