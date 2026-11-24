"""Relocate a private bundle and test its setup, backend and visible logs with fictional data only."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zipfile import ZipFile

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--port", type=int, default=8796)
    args = parser.parse_args()
    environment = {
        k: v
        for k, v in os.environ.items()
        if k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"} and not k.startswith("MARGIN_")
    }
    url = f"http://127.0.0.1:{args.port}"
    with httpx.Client(trust_env=False, timeout=1) as http:
        try:
            http.get(url + "/api/status")
        except httpx.HTTPError:
            pass
        else:
            raise SystemExit("Test port occupied; no calls made.")
    with tempfile.TemporaryDirectory(prefix="margin-portable-smoke-") as temporary:
        temp = Path(temporary)
        with ZipFile(args.archive) as archive:
            for item in archive.infolist():
                parts = Path(item.filename).parts
                if (
                    not parts
                    or parts[0] != "margin-agent-local"
                    or ".." in parts
                    or Path(item.filename).is_absolute()
                    or item.external_attr >> 28 == 0xA
                ):
                    raise RuntimeError("Unexpected bundle archive path/type.")
            archive.extractall(temp)
        original = temp / "margin-agent-local"
        bundle = temp / "relocated folder with spaces"
        original.rename(bundle)
        credentials = bundle / "private/providers.env"
        if credentials.exists():
            credentials.chmod(0o600)
        entry = bundle / "margin_local.py"

        def execute(*command):
            output = subprocess.run(
                [sys.executable, str(entry), *command],
                cwd=temp,
                env=environment,
                capture_output=True,
                text=True,
                timeout=65,
                check=False,
            )
            if output.returncode:
                # Never echo captured private output as part of a failing shell-command exception.
                raise RuntimeError("Portable test command failed; output withheld.")
            return json.loads(output.stdout.splitlines()[-1])

        question = bundle / "question.md"
        question.write_text(
            "Fictional software acceptance for portable tools and visible summaries, not company research."
        )
        until = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
        configured = execute(
            "setup",
            "--python",
            sys.executable,
            "--skip-install",
            "--task-file",
            str(question),
            "--retention-until",
            until,
            "--agent-label",
            "portable-process-acceptance",
            "--mode",
            "synthetic",
            "--port",
            str(args.port),
        )
        assert configured["recording"]
        server = subprocess.Popen(
            [
                sys.executable,
                str(entry),
                "serve",
                "--bharatstock-requests",
                "1",
                "--drishti-requests",
                "0",
                "--drishti-credits",
                "0",
            ],
            cwd=temp,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            with httpx.Client(trust_env=False, timeout=1) as http:
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError("Portable backend failed to start.")
                    try:
                        if http.get(url + "/api/status").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.05)
                else:
                    raise RuntimeError("Portable backend did not start.")
            status = execute(
                "agent", "--why", "Inspect the fictional backend before tool selection.", "status"
            )
            assert status["decision_summary"].startswith("Inspect")
            assert status["mode"] == "synthetic"
            catalog = execute("agent", "catalog")
            assert [len(v) for v in catalog["data"].values()] == [13, 11, 5]
            note = bundle / "workspace/decision.md"
            note.write_text(
                "Use the company-margin function to test shared retrieval and local calculation."
            )
            assert (
                execute("agent", "note", "--kind", "decision", "--file", str(note))["status"]
                == "recorded"
            )
            preview = execute(
                "agent",
                "company-preview",
                "--json",
                json.dumps(
                    {
                        "function": "finance.company_margins",
                        "ticker": "SYNTHA",
                        "exchange": "NSE",
                        "money_unit": "INR",
                        "fetch_missing": True,
                    }
                ),
            )
            run_args = [
                "agent",
                "run",
                preview["data"]["plan_id"],
                "--backend-id",
                preview["backend_id"],
                "--key",
                "portable-smoke-only",
            ]
            run = execute(*run_args)["data"]
            assert execute(*run_args)["data"]["run_id"] == run["run_id"]
            finished = execute("agent", "wait", run["run_id"], "--seconds", "10")["data"]
            assert finished["status"] == "completed"
            operation = finished["operations"][-1]["operation_id"]
            result = execute("agent", "result", run["run_id"], operation)
            assert result["data"]["payload"]["status"] == "success"
            note.write_text(
                "The fictional calculation completed; source units were caller-declared, not verified."
            )
            assert (
                execute(
                    "agent",
                    "note",
                    "--kind",
                    "observation",
                    "--file",
                    str(note),
                    "--run-id",
                    run["run_id"],
                    "--operation-id",
                    operation,
                )["status"]
                == "recorded"
            )
            final = execute("agent", "status")
            assert final["data"]["ledger"]["http_attempts"] == {"bharatstock": 1, "drishti": 0}
            evaluation_bundle = (bundle / "runtime/submit.py").exists()
            answer = bundle / (
                "workspace/answers.json" if evaluation_bundle else "workspace/final.md"
            )
            if not evaluation_bundle:
                answer.write_text(
                    "Fictional acceptance passed; no real financial conclusion or independent grade."
                )
            done = execute("agent", "finish", "--answer-file", str(answer))
            assert done["log_counts"]["agent_summaries"] == 3 and not done["warnings"]
            config = json.loads((Path(configured["skill"]) / "connection.json").read_text())
            session = Path(config["session"])
            log = (session / "events.jsonl").read_text()
            assert "agent_self_report" in log and "action_nonce" not in log
            if credentials.exists():
                from margin.interfaces.agent.local_config import read_provider_env

                assert all(value not in log for value in read_provider_env(credentials).values())
            assert (session / "answer.json").is_file()
            if evaluation_bundle:
                exported = execute("submit")
                assert not exported["contains_credentials"]
                with ZipFile(exported["submission"]) as submission:
                    assert "answers.json" in submission.namelist()
                    assert not any("providers.env" in name for name in submission.namelist())
                import importlib.util

                grading_spec = importlib.util.spec_from_file_location(
                    "eval_grade", Path(__file__).parents[1] / "research/evaluation/grade.py"
                )
                grader = importlib.util.module_from_spec(grading_spec)
                grading_spec.loader.exec_module(grader)
                answers, events = grader.read_submission(Path(exported["submission"]))
                assert grader.trace_index(events)["modes"] == {"synthetic"}
                assert grader.trace_index(events)["why_count"] == 1
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "relocated_before_setup": True,
                        "workspace_path_has_spaces": True,
                        "runtime_install": "existing_interpreter_skip_install",
                        "summary_events": done["log_counts"]["agent_summaries"],
                        "tool_events": done["log_counts"]["tool_observations"],
                        "live_provider_requests": 0,
                        "temporary_private_copy_removed_on_exit": True,
                    }
                )
            )
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    main()
