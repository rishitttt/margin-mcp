import importlib.util
import json
import stat
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zipfile import ZipFile

import pytest

from margin.interfaces.agent.client import BridgeError

ROOT = Path(__file__).parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wheel(tmp_path, content="no credentials"):
    path = tmp_path / "margin_research-0.1.0-py3-none-any.whl"
    with ZipFile(path, "w") as archive:
        archive.writestr("margin/__init__.py", content)
    return path


def test_bundle_keeps_authorized_keys_only_in_private_file_and_has_no_machine_paths(tmp_path):
    module = load_module("bundle_builder", ROOT / "scripts/package_agent_bundle.py")
    path = tmp_path / "providers.env"
    keys = {
        "BHARATSTOCK_API_KEY": "fictional-bharat-bundle-credential",
        "DRISHTI_API_KEY": "fictional-drishti-bundle-credential",
    }
    path.write_text("".join(f"{k}={v}\n" for k, v in keys.items()))
    archive_path = tmp_path / "private-bundle.zip"
    result = module.build_bundle(
        ROOT, archive_path, wheel(tmp_path), include_keys=True, keys_file=path
    )
    assert result["provider_calls"] == 0 and result["contains_trial_credentials"]
    assert stat.S_IMODE(archive_path.stat().st_mode) == 0o600
    with ZipFile(archive_path) as archive:
        assert all(
            not name.startswith("/") and ".." not in Path(name).parts for name in archive.namelist()
        )
        assert "margin-agent-local/margin_local.py" in archive.namelist()
        assert not any(
            name.endswith("connection.json") or "events.jsonl" in name
            for name in archive.namelist()
        )
        for name in archive.namelist():
            data = archive.read(name)
            assert str(ROOT).encode() not in data
            for value in keys.values():
                assert (value.encode() in data) == name.endswith("private/providers.env")
        snapshot = json.loads(
            archive.read("margin-agent-local/margin-research/references/catalog.json")
        )
        assert [len(snapshot[k]) for k in ("retrieval", "calculations", "company_functions")] == [
            13,
            15,
            9,
        ]
        assert (
            stat.S_IMODE(
                archive.getinfo("margin-agent-local/private/providers.env").external_attr >> 16
            )
            == 0o600
        )


def test_keyless_bundle_and_existing_output_are_preserved(tmp_path):
    module = load_module("bundle_builder", ROOT / "scripts/package_agent_bundle.py")
    output = tmp_path / "bundle.zip"
    runtime = wheel(tmp_path)
    module.build_bundle(ROOT, output, runtime)
    original = output.read_bytes()
    with ZipFile(output) as archive:
        assert not any(name.endswith("providers.env") for name in archive.namelist())
    with pytest.raises(BridgeError, match="not overwritten"):
        module.build_bundle(ROOT, output, runtime)
    assert output.read_bytes() == original


def test_compressed_wheel_credential_spill_blocks_bundle(tmp_path):
    module = load_module("bundle_builder", ROOT / "scripts/package_agent_bundle.py")
    path = tmp_path / "providers.env"
    path.write_text("BHARATSTOCK_API_KEY=fictional-wheel-secret\nDRISHTI_API_KEY=fictional-d-key\n")
    output = tmp_path / "rejected.zip"
    with pytest.raises(BridgeError, match="runtime wheel"):
        module.build_bundle(
            ROOT,
            output,
            wheel(tmp_path, "fictional-wheel-secret"),
            include_keys=True,
            keys_file=path,
        )
    assert not output.exists()


def test_visible_summaries_are_linked_redacted_and_counted_without_network(tmp_path, capsys):
    pilot = load_module("pilot", ROOT / "research/pilot.py")
    task = tmp_path / "question.md"
    task.write_text("Evaluate the tool workflow using permitted observations.")
    credentials = tmp_path / "providers.env"
    credentials.write_text(
        "BHARATSTOCK_API_KEY=fictional-summary-key\nDRISHTI_API_KEY=fictional-other-key\n"
    )
    session = tmp_path / "session"
    base = ["--session", str(session)]
    until = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
    assert (
        pilot.main(
            base
            + [
                "init",
                "--task-file",
                str(task),
                "--mode",
                "synthetic",
                "--retention-until",
                until,
                "--redact-env-file",
                str(credentials),
                "--agent-label",
                "test-host-model",
            ]
        )
        == 0
    )
    note = tmp_path / "note.md"
    note.write_text(
        "The selected operation answers the requested metric. fictional-summary-key must be redacted."
    )
    assert pilot.main(base + ["note", "--kind", "decision", "--file", str(note)]) == 0
    assert (
        pilot.main(
            base
            + [
                "note",
                "--kind",
                "observation",
                "--file",
                str(note),
                "--run-id",
                "run-01",
                "--operation-id",
                "op-01",
            ]
        )
        == 0
    )
    log = (session / "events.jsonl").read_text()
    assert "fictional-summary-key" not in log and "[REDACTED]" in log
    events = [json.loads(line) for line in log.splitlines()]
    assert all(e["origin"] == "agent_self_report" and not e["is_hidden_reasoning"] for e in events)
    assert events[1]["run_id"] == "run-01" and events[1]["operation_id"] == "op-01"
    metadata = json.loads((session / "session.json").read_text())
    assert metadata["instrumentation"] == "visible-summaries-v1"
    assert metadata["agent_label"] == "test-host-model"
    note.write_text("x" * 4097)
    assert pilot.main(base + ["note", "--kind", "decision", "--file", str(note)]) == 2
    assert len((session / "events.jsonl").read_text().splitlines()) == 2
    answer = tmp_path / "final.md"
    answer.write_text("A final visible answer without a gold grade. fictional-summary-key")
    assert pilot.main(base + ["finish", "--answer-file", str(answer)]) == 0
    final = json.loads((session / "answer.json").read_text())
    assert final["log_counts"] == {"agent_summaries": 2, "tool_observations": 0}
    assert not final["warnings"] and "fictional-summary-key" not in json.dumps(final)
    assert "fictional-summary-key" not in capsys.readouterr().out


def test_skill_function_reference_covers_registry_and_analysis_catalog():
    from margin.analysis.company import FUNCTIONS
    from margin.analysis.service import SPECS
    from margin.core.config import Settings
    from margin.core.registry import Registry

    content = (ROOT / "skills/margin-research/references/functions.md").read_text()
    names = set(Registry(Settings()).specs) | set(SPECS) | set(FUNCTIONS)
    assert len(names) == 37
    assert all(f"`{name}`" in content for name in names)
