"""Export only the answer/report and sanitized session log; never export credentials."""

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from margin.evidence.sanitize import Sanitizer
from margin.interfaces.agent.local_config import read_provider_env


def export(root, output):
    config = json.loads((root / "local.json").read_text())
    connection = json.loads((Path(config["skill"]) / "connection.json").read_text())
    session = Path(connection["session"])
    if not session.resolve().is_relative_to((root / "private/sessions").resolve()):
        raise ValueError("Use this test bundle's configured session")
    credentials = (
        read_provider_env(root / "private/providers.env")
        if (root / "private/providers.env").exists()
        else {}
    )
    sanitizer = Sanitizer(credentials.values())
    answer_path = root / "workspace/answers.json"
    if answer_path.stat().st_size > 65536:
        raise ValueError("answers.json exceeds 64 KiB")
    answers = sanitizer.clean(json.loads(answer_path.read_text()))
    final = sanitizer.clean(json.loads((session / "answer.json").read_text()))
    if json.loads(final["answer"]) != answers:
        raise ValueError(
            "Run finish with the exact answers.json before export; recorded answer differs"
        )
    metadata = sanitizer.clean(json.loads((session / "session.json").read_text()))
    metadata.pop("redaction_env_file", None)
    report_path = root / "workspace/report.md"
    if report_path.stat().st_size > 65536:
        raise ValueError("report.md exceeds 64 KiB")
    files = {
        "answers.json": json.dumps(answers, indent=2).encode(),
        "report.md": sanitizer.text(report_path.read_text()).encode(),
        "session/session.json": json.dumps(metadata, indent=2).encode(),
        "session/answer.json": json.dumps(final, indent=2).encode(),
    }
    backend = session / "backend.json"
    if backend.exists():
        files["session/backend.json"] = json.dumps(
            sanitizer.clean(json.loads(backend.read_text()))
        ).encode()
    event_path = session / "events.jsonl"
    if event_path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("Session log exceeds its bound")
    with event_path.open() as stream:
        lines = [
            json.dumps(sanitizer.clean(json.loads(line)), ensure_ascii=False)
            for line in stream
            if line.strip()
        ]
    files["session/events.jsonl"] = ("\n".join(lines) + "\n").encode()
    manifest = {
        "submission_version": "1.0",
        "benchmark_id": answers.get("benchmark_id"),
        "exported_at": datetime.now(UTC).isoformat(),
        "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        "hash_limit": "Checks integrity since export, not authenticity of local host events",
        "contains_credentials": False,
        "contains_hidden_reasoning": False,
    }
    files["submission-manifest.json"] = json.dumps(manifest, indent=2).encode()
    if any(key.encode() in value for value in files.values() for key in credentials.values()):
        raise ValueError("Credential content detected; export withheld")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_EXCL | os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream, ZipFile(stream, "w", ZIP_DEFLATED) as archive:
            for name, data in files.items():
                archive.writestr(name, data)
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"submission": str(output), "files": sorted(files), "contains_credentials": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    output = args.output.expanduser().absolute() if args.output else root / "submission.zip"
    try:
        print(json.dumps(export(root, output)))
        return 0
    except (OSError, ValueError, KeyError):
        print(
            json.dumps(
                {
                    "error": "export_failed",
                    "message": "Check that answers/report and the matching finished session exist; no file was overwritten.",
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
