"""Real CLI-process acceptance against a fresh fictional backend; never live providers."""

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

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8794)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    url = f"http://127.0.0.1:{args.port}"
    environment = {
        k: v
        for k, v in os.environ.items()
        if k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "MARGIN_EXPECT_MODE"}
        and not k.startswith("MARGIN_")
    }
    with httpx.Client(trust_env=False, timeout=1) as http:
        try:
            http.get(url + "/api/status")
        except httpx.HTTPError:
            pass
        else:
            raise SystemExit("Test port is occupied. Select another port; no calls were made.")
    # An exec-based child gives the existing workbench CLI a clean sys.argv.
    server = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "from margin.interfaces.workbench.app import main; main()",
            "--mode",
            "synthetic",
            "--port",
            str(args.port),
        ],
        cwd=root,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(trust_env=False, timeout=1) as http:
            for _ in range(100):
                if server.poll() is not None:
                    raise RuntimeError("Fictional test backend failed to start.")
                try:
                    if http.get(url + "/api/status").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.05)
            else:
                raise RuntimeError("Fictional backend startup timed out.")
        with tempfile.TemporaryDirectory(prefix="margin-agent-smoke-") as tmp:
            tmp = Path(tmp)

            def execute(command):
                return subprocess.run(
                    command,
                    cwd=tmp,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=65,
                )

            question = tmp / "task.txt"
            question.write_text(
                "Software acceptance using fictional SYNTHA; not financial research."
            )
            session = tmp / "session"
            pilot = root / "research/pilot.py"
            until = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
            execute(
                [
                    sys.executable,
                    str(pilot),
                    "--session",
                    str(session),
                    "init",
                    "--task-file",
                    str(question),
                    "--mode",
                    "synthetic",
                    "--retention-until",
                    until,
                ]
            )
            skill = tmp / ".agents/skills/margin-research"
            execute(
                [
                    sys.executable,
                    str(root / "scripts/install_agent_skill.py"),
                    "--target",
                    str(skill),
                    "--url",
                    url,
                    "--session",
                    str(session),
                ]
            )
            launcher = skill / "scripts/margin.py"

            def call(*command):
                return json.loads(execute([sys.executable, str(launcher), *command]).stdout)

            status = call("status")
            assert status["mode"] == "synthetic"
            assert status["data"]["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}
            assert len(call("catalog")["data"]["retrieval"]) == 13
            assert call("catalog", "--name", "finance.calculate_dcf")["data"]["calculations"][0][
                "schema"
            ]
            body = {
                "function": "finance.company_margins",
                "ticker": "SYNTHA",
                "exchange": "NSE",
                "money_unit": "INR",
                "fetch_missing": True,
            }

            def submit(body, key):
                preview = call("company-preview", "--json", json.dumps(body))
                plan = preview["data"]
                run_args = [
                    "run",
                    plan["plan_id"],
                    "--key",
                    key,
                    "--backend-id",
                    preview["backend_id"],
                ]
                run = call(*run_args)["data"]
                assert call(*run_args)["data"]["run_id"] == run["run_id"]
                finished = call("wait", run["run_id"], "--seconds", "10")["data"]
                assert finished["status"] == "completed", finished["status"]
                result = call(
                    "result", finished["run_id"], finished["operations"][-1]["operation_id"]
                )
                assert result["data"]["payload"]["status"] == "success"
                return plan, finished

            first, run = submit(body, "smoke-agent-first")
            assert first["data_operations"]["bharatstock"] == 1
            assert call("facts", run["run_id"], run["operations"][0]["operation_id"])["data"][
                "facts"
            ]
            assert len(call("sources")["data"]["sources"]) == 1
            second, _ = submit(body | {"fetch_missing": False}, "smoke-agent-reuse")
            assert second["data_operations"] == {"bharatstock": 0, "drishti": 0}
            assert len(call("workflows")["data"]["functions"]) == 10

            def review(function, arguments):
                return call(
                    "--why",
                    "Exercise the fictional local " + function + " contract.",
                    "review",
                    "--json",
                    json.dumps({"function": function, "arguments": arguments}),
                )["data"]

            source = review(
                "evidence.register_sources",
                {
                    "sources": [
                        {
                            "issuer": "NSE:SYNTHA",
                            "title": "Fictional software acceptance source",
                            "url": "https://example.invalid/fictional",
                            "kind": "provider_summary",
                            "date": "2026-10-15",
                            "date_kind": "published",
                            "passages": [
                                {
                                    "passage_id": "P1",
                                    "text": "Fictional demand improved.",
                                    "locator": "fixture paragraph",
                                }
                            ],
                        }
                    ]
                },
            )["sources"][0]["source_id"]
            packet = review(
                "evidence.prepare_verification",
                {
                    "claims": [
                        {
                            "claim_id": "C1",
                            "text": "Fictional demand improved.",
                            "source_ids": [source],
                        }
                    ]
                },
            )
            ref = {k: packet[k] for k in ("packet_id", "packet_hash")}
            quote = {"source_id": source, "passage_id": "P1", "quote": "Fictional demand improved."}
            reviewer = {
                "host": "process-smoke",
                "model": "fictional annotations, no model inference",
            }
            review(
                "evidence.submit_assessment",
                ref
                | {
                    "reviewer": reviewer,
                    "assessments": [
                        {
                            "claim_id": "C1",
                            "verdict": "supported",
                            "quotes": [quote],
                            "rationale": "Fictional software test.",
                        }
                    ],
                },
            )
            assert not review("evidence.render_citations", ref)["citations"][0][
                "original_document_verified"
            ]
            assert (
                review("evidence.audit_answer", ref | {"claim_ids": ["C1"]})["status"] == "success"
            )
            packet = review(
                "sentiment.prepare_analysis",
                {
                    "source_ids": [source],
                    "issuer": "NSE:SYNTHA",
                    "aspect": "fictional demand",
                    "from": "2026-10-01",
                    "to": "2026-10-31",
                    "date_basis": "published",
                },
            )
            ref = {k: packet[k] for k in ("packet_id", "packet_hash")}
            review(
                "sentiment.submit_annotations",
                ref
                | {
                    "reviewer": reviewer,
                    "annotations": [
                        {
                            "source_id": source,
                            "relevant": True,
                            "label": "positive",
                            "quotes": [quote],
                            "rationale": "Fictional software test.",
                        }
                    ],
                },
            )
            assert review("sentiment.aggregate", ref)["balance"] == "1"
            final_status = call("status")
            assert final_status["backend_id"] == status["backend_id"]
            assert final_status["data"]["ledger"]["http_attempts"] == {
                "bharatstock": 1,
                "drishti": 0,
            }
            answer = tmp / "final.txt"
            answer.write_text("Fictional software acceptance passed. No real company conclusions.")
            assert call("finish", "--answer-file", str(answer))["status"] == "finished"
            log = (session / "events.jsonl").read_text()
            assert "action_nonce" not in log and "synthetic-private-key-never-forward" not in log
            events = len(log.splitlines())
            assert (session / "answer.json").exists()
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "mode": "synthetic",
                        "separate_command_processes": events,
                        "shared_backend": True,
                        "simulated_attempts": {"bharatstock": 1, "drishti": 0},
                        "live_provider_requests": 0,
                        "temporary_pilot_removed_on_exit": True,
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
