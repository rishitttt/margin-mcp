"""Fictional offline fixtures test contracts/export validation, never company truth."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from margin.evidence.sanitize import Sanitizer
from margin.interfaces.agent.cli import main
from margin.interfaces.agent.client import BridgeError

ROOT = Path(__file__).parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(
        "eval_" + name, ROOT / "research/evaluation" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("why", ["", " ", "line\nbreak", "x" * 281])
def test_invalid_why_stops_before_client_creation(why):
    def factory(*args, **kwargs):
        raise AssertionError("No client allowed for an invalid summary")

    output = io.StringIO()
    assert main(["--why", why, "status"], client_factory=factory, output=output) == 2
    assert json.loads(output.getvalue())["error"]["code"] == "invalid_summary"


def test_why_is_redacted_recorded_before_dispatch_and_remains_json(capsys):
    sequence = []
    secret = "fictional-private-key-123456789"
    sanitizer = Sanitizer([secret])

    def decision(command, why):
        sequence.append("decision")
        assert secret not in why
        return {"event_id": "fictional-event"}

    def factory(*args, **kwargs):
        sequence.append("client")
        raise BridgeError("unavailable", "Fictional offline test")

    output = io.StringIO()
    assert (
        main(
            ["--why", "Inspect " + secret, "status"],
            client_factory=factory,
            decision_observer=decision,
            output_filter=sanitizer.clean,
            output=output,
        )
        == 2
    )
    value = json.loads(output.getvalue())
    assert sequence == ["decision", "client"]
    assert value["decision_event_id"] == "fictional-event"
    assert secret not in capsys.readouterr().err + output.getvalue()


def test_preexecution_log_failure_stops_client():
    def decision(*args):
        raise OSError("Fictional full disk")

    def factory(*args, **kwargs):
        raise AssertionError("No dispatch after recording failure")

    output = io.StringIO()
    assert (
        main(
            ["--why", "Inspect readiness.", "status"],
            client_factory=factory,
            decision_observer=decision,
            output=output,
        )
        == 2
    )
    assert json.loads(output.getvalue())["error"]["code"] == "recording"


def test_template_does_not_pass_as_completed_live_evaluation():
    spec, grade = load("spec"), load("grade")
    answers = spec.template()
    gold = {
        "benchmark_id": spec.BENCHMARK_ID,
        "as_of": spec.AS_OF,
        "task_ids": [item[0] for item in spec.TASKS],
        "review_status": "fictional fixture",
        "expected": {"REUSE": {"additional_provider_attempts": {"value": 0, "numeric": True}}},
        "forbidden_operations": spec.FORBIDDEN,
        "in_scope_operations": [],
        "manual_review": [],
    }
    result = grade.evaluate(answers, [], gold)
    assert result["passed_checks"] == result["attempted_tasks"] == 0
    assert any("live" in flag for flag in result["flags"])
    assert not result["hidden_reasoning_captured"]
    answers["answers"][1]["task_id"] = answers["answers"][0]["task_id"]
    with pytest.raises(ValueError, match="duplicate"):
        grade.evaluate(answers, [], gold)


def test_numeric_check_requires_units_basis_and_period():
    grade = load("grade")
    expected = {
        "value": "10",
        "numeric": True,
        "unit": "INR_crore",
        "basis": "consolidated",
        "period_end": "2026-03-31",
    }
    actual = dict(expected)
    assert grade.compare_field(actual, expected)[0]
    for key in ["unit", "basis", "period_end"]:
        assert not grade.compare_field(actual | {key: "wrong"}, expected)[0]
    assert not grade.compare_field(actual | {"value": "NaN"}, expected)[0]


def test_builder_requires_private_gold_before_creating_any_package(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    build = load("build")
    with pytest.raises(ValueError, match="separately retained"):
        build.build(ROOT, tmp_path / "output", tmp_path / "unused.whl", tmp_path / "absent.json")
    assert not (tmp_path / "output").exists()


def test_private_gold_contract_is_checked_with_fictional_inputs(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    build, spec = load("build"), load("spec")
    path = tmp_path / "fictional-gold.json"
    key = {
        "benchmark_id": spec.BENCHMARK_ID,
        "as_of": spec.AS_OF,
        "task_ids": [task[0] for task in spec.TASKS],
        "expected": {"REUSE": {"additional_provider_attempts": {"value": 0}}},
    }
    path.write_text(json.dumps(key))
    assert build.gold_key(path) == key
    key["benchmark_id"] = "mismatched"
    path.write_text(json.dumps(key))
    with pytest.raises(ValueError, match="does not match"):
        build.gold_key(path)


def test_submission_hashes_and_recorded_final_are_checked(tmp_path):
    grade = load("grade")
    answer = {"fictional": True}
    files = {
        "answers.json": json.dumps(answer).encode(),
        "report.md": b"fictional test",
        "session/session.json": b"{}",
        "session/answer.json": json.dumps({"answer": json.dumps(answer)}).encode(),
        "session/events.jsonl": b"",
    }
    manifest = {
        "sha256": {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}
    }
    files["submission-manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "fictional.zip"

    def write():
        with ZipFile(path, "w", ZIP_DEFLATED) as archive:
            for name, value in files.items():
                archive.writestr(name, value)

    write()
    assert grade.read_submission(path) == (answer, [])
    files["answers.json"] = b"{}"
    write()
    with pytest.raises(ValueError, match="checksum"):
        grade.read_submission(path)
