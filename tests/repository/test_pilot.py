import importlib.util
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from margin.interfaces.agent.client import BridgeError


def load_pilot():
    path = Path(__file__).parents[2] / "research/pilot.py"
    spec = importlib.util.spec_from_file_location("margin_pilot", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_private_pilot_retention_scope_pinning_observations_and_finish(tmp_path, capsys):
    pilot = load_pilot()
    task = tmp_path / "question.txt"
    task.write_text("Test the CLI using fictional fixtures; no company research.")
    directory = tmp_path / "session"
    until = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
    base = ["--session", str(directory)]
    assert (
        pilot.main(
            base + ["init", "--task-file", str(task), "--mode", "live", "--retention-until", until]
        )
        == 2
    )
    assert not directory.exists()
    assert (
        pilot.main(
            base
            + ["init", "--task-file", str(task), "--mode", "synthetic", "--retention-until", until]
        )
        == 0
    )
    with pilot.locked_session(directory) as metadata:
        session = pilot.Session(directory, metadata)

        class Backend:
            mode = "synthetic"
            backend_id = "first-backend"

        session.check_backend(Backend())
        session.observe(
            "preview", {"data": {"url": "https://example.com/file?api_key=never-record"}}, 0
        )
        Backend.backend_id = "restarted-backend"
        with pytest.raises(BridgeError, match="backend changed"):
            session.check_backend(Backend())
    log = (directory / "events.jsonl").read_text()
    assert "never-record" not in log and "api_key=" not in log
    assert (directory / "session.json").stat().st_mode & 0o777 == 0o600
    answer = tmp_path / "answer.txt"
    answer.write_text("Software test complete; no independently verified company claims.")
    assert pilot.main(base + ["finish", "--answer-file", str(answer)]) == 0
    assert pilot.main(base + ["call", "status"]) == 2
    assert "session_finished" in capsys.readouterr().out


def test_private_pilot_expired_retention_blocks_before_execution(tmp_path):
    pilot = load_pilot()
    directory = tmp_path / "session"
    directory.mkdir()
    (directory / "session.json").write_text(json.dumps({"retention_until": "2000-01-01"}))
    with pytest.raises(BridgeError, match="retention has expired"):
        with pilot.locked_session(directory):
            pytest.fail("Expired session was admitted")
