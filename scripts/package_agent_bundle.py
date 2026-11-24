"""Build a private portable test ZIP; credentials are included only with --include-keys."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from margin.analysis.company import planning_capabilities
from margin.analysis.service import capabilities
from margin.core.config import Settings
from margin.core.registry import Registry
from margin.interfaces.agent.client import BridgeError
from margin.interfaces.agent.local_config import read_provider_env
from margin.protocols.service import ReviewService


def bundle_guide():
    until = (datetime.now(UTC) + timedelta(days=14)).date().isoformat()
    return f"""# Margin local agent test bundle

This private bundle may contain working trial provider keys in `private/providers.env`.
Keep it local/private. It has no API keys in SKILL.md, source code or agent prompts.
The keys are loaded as data by the backend; the same file supplies recorder redaction.
No company dataset, prior run output or answer key is bundled.

Requires Python >=3.12, shell execution, loopback HTTP and internet access for initial
dependency installation/live provider calls. Tested on macOS/Python 3.12; cross-platform
dependency resolution and every agent host are not validated. For a host supporting Agent
Skills, install the skill in its supported location; otherwise explicitly provide SKILL.md
and permit shell execution. A text-only chat cannot execute these tools on its own.

1. Extract this ZIP. Write the actual evaluation question into `question.md`.
2. From the extracted folder, configure an isolated workspace and recorded session:

```sh
python3.12 margin_local.py setup --task-file question.md --retention-until {until} --agent-label codex-pilot-01
```

Choose an appropriate review date. Setup opts into private local recording for that task;
it does not establish provider licensing rights. It creates a local venv, installs the
included wheel with constrained dependencies, and copies the skill to
`workspace/.agents/skills/margin-research`. To use another host's directory, add
`--target /absolute/path/to/that/host/skills/margin-research`. `--no-recording` explicitly
disables the evaluation log instead of supplying a task. Setup never starts a provider call.
Use a separate extracted copy/session per agent; label the actual host/model yourself.

3. In a backend terminal, start the shared server:

```sh
python3.12 margin_local.py serve --bharatstock-requests 1 --drishti-requests 0 --drishti-credits 0
```

The default is LIVE, one BharatStock attempt and zero Drishti calls. No browser required.
For selected Drishti tests, set an adequate HTTP/credit ceiling and explicit reviewed
operation names, for example `--drishti-requests 30 --drishti-credits 6
--enable-operations drishti.get_news,drishti.get_announcements,drishti.list_earnings,drishti.get_earnings_filing`.
Connection/metadata traffic also consumes HTTP allowance. Do not restart to replenish
quota: all copies/agents using these trial keys share actual account limits (historically
BharatStock Free 25/day and Drishti 1,000 one-off trial credits). Local process counters do
not coordinate across machines or measure remaining account allowance.

4. Open a fresh agent chat in `workspace`, explicitly select its installed skill, and
give the question and authorized call budget. For Codex, invoke `$margin-research`.
If another global skill has the same name, specify this workspace's SKILL.md path so
recorded calls use this session. The agent should log concise visible decision summaries,
use the helper for tools, and submit its final answer with `finish`.

You can also exercise the interface directly:

```sh
python3.12 margin_local.py agent status
python3.12 margin_local.py agent catalog
python3.12 margin_local.py agent catalog --name finance.calculate_dcf
python3.12 margin_local.py agent note --kind decision --file workspace/decision.md
python3.12 margin_local.py agent note --kind observation --file workspace/observation.md --run-id RUN_ID --operation-id OPERATION_ID
python3.12 margin_local.py agent finish --answer-file workspace/final.md
```

Notes are brief visible summaries supplied by the agent, not hidden chain of thought.
The log cannot prove their faithfulness or capture notes a host never emits. Full host
transcripts and host-provided reasoning summaries need a separate host integration.

`private/sessions/<session>/` holds task/host labels, backend pin, chronological events.jsonl
(tool observations + agent summaries), and answer.json. Finished/expired sessions reject
new work; expiration does not delete retained files. Review/delete logs manually. Provider
credentials are redacted from these outputs. Recordings and keys are not product data.

Move the folder BEFORE setup. The ZIP contains no workstation-specific configuration;
setup generates local paths. If you later move it, use a fresh extracted/configured copy.
Our MCP adapter, frozen replay, independent gold/grading, citation verification and sentiment
protocols are not implemented. DCF uses explicit assumptions; provider output stays unverified.
"""


def build_bundle(root, output, wheel, *, include_keys=False, keys_file=None):
    output = output.expanduser().absolute()
    if output.exists():
        raise BridgeError(
            "bundle_exists", "Choose a new ZIP path; existing bundles are not overwritten."
        )
    if include_keys and output.resolve().is_relative_to(root.resolve()):
        ignored = subprocess.run(["git", "check-ignore", "-q", str(output)], cwd=root, check=False)
        if ignored.returncode:
            raise BridgeError(
                "private_output",
                "Credential-bearing bundles must be outside Git or in an ignored private directory.",
            )
    credentials = read_provider_env(keys_file or root / ".env") if include_keys else {}
    if include_keys and set(credentials) != {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}:
        raise BridgeError(
            "credential_file", "Both trial provider keys are required for this private bundle."
        )
    with ZipFile(wheel) as archive:
        for name in archive.namelist():
            if any(value.encode() in archive.read(name) for value in credentials.values()):
                raise BridgeError(
                    "credential_spill",
                    "Credential content found in the runtime wheel; bundle withheld.",
                )
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    created = False
    try:
        with tempfile.TemporaryDirectory(prefix="margin-package-", dir=output.parent) as temporary:
            bundle = Path(temporary) / "margin-agent-local"
            bundle.mkdir(mode=0o700)
            shutil.copytree(
                root / "skills/margin-research",
                bundle / "margin-research",
                ignore=shutil.ignore_patterns("connection.json", "__pycache__", "*.pyc"),
            )
            runtime = bundle / "runtime"
            runtime.mkdir()
            shutil.copy2(wheel, runtime / wheel.name)
            shutil.copy2(root / "research/pilot.py", runtime / "pilot.py")
            shutil.copy2(root / "requirements-dev.lock", runtime / "requirements.lock")
            shutil.copy2(root / "packaging/local_bundle.py", bundle / "margin_local.py")
            (bundle / "GETTING_STARTED.md").write_text(bundle_guide())
            (bundle / "private").mkdir(mode=0o700)
            if credentials:
                path = bundle / "private/providers.env"
                path.write_text(
                    "".join(f"{name}={value}\n" for name, value in sorted(credentials.items()))
                )
                path.chmod(0o600)
            snapshot = {
                "note": "Build-time offline contracts, not current entitlements or proof of live execution. Runtime catalog is authoritative.",
                "retrieval": Registry(Settings(mode="live")).capabilities(),
                "calculations": capabilities(),
                "company_functions": planning_capabilities(),
                "review_functions": ReviewService().capabilities(),
            }
            (bundle / "margin-research/references/catalog.json").write_text(
                json.dumps(snapshot, indent=2) + "\n"
            )
            manifest = {
                "bundle_version": "1.0",
                "built_at": datetime.now(UTC).isoformat(),
                "wheel": wheel.name,
                "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                "contains_trial_credentials": bool(credentials),
                "contains_prior_observations": False,
                "review_function_count": 10,
                "instrumentation": "visible-summaries-v1",
                "capability_counts": [
                    len(snapshot[key]) for key in ("retrieval", "calculations", "company_functions")
                ],
            }
            (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            # Scan all files except the explicitly requested credential file, without exposing values.
            for path in bundle.rglob("*"):
                if path.is_file() and path != bundle / "private/providers.env":
                    if any(value.encode() in path.read_bytes() for value in credentials.values()):
                        raise BridgeError(
                            "credential_spill",
                            "Credential content found outside the designated private file; bundle withheld.",
                        )
            # Create the final archive restrictively from the first byte, not after writing secrets.
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
            with (
                os.fdopen(descriptor, "wb") as stream,
                ZipFile(stream, "w", ZIP_DEFLATED) as archive,
            ):
                for path in sorted(bundle.rglob("*")):
                    if path.is_file():
                        archive.write(
                            path, str(Path("margin-agent-local") / path.relative_to(bundle))
                        )
        return {
            "archive": str(output),
            "contains_trial_credentials": bool(credentials),
            "provider_calls": 0,
        }
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=root / "reports/private/packages/margin-agent-local.zip"
    )
    parser.add_argument("--include-keys", action="store_true")
    parser.add_argument("--keys-file", type=Path)
    parser.add_argument(
        "--wheel", type=Path, help="Use an already-built wheel instead of building one"
    )
    args = parser.parse_args()
    try:
        if args.wheel:
            wheel = args.wheel.expanduser().resolve()
        else:
            environment = {
                k: v
                for k, v in os.environ.items()
                if k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}
            }
            subprocess.run(
                [sys.executable, "-m", "build", "--wheel", "--no-isolation"],
                cwd=root,
                env=environment,
                stdout=subprocess.DEVNULL,
                check=True,
            )
            wheels = sorted(
                (root / "dist").glob("margin_research-*.whl"), key=lambda p: p.stat().st_mtime
            )
            wheel = wheels[-1]
        print(
            json.dumps(
                build_bundle(
                    root,
                    args.output,
                    wheel,
                    include_keys=args.include_keys,
                    keys_file=args.keys_file,
                )
            )
        )
        return 0
    except (OSError, subprocess.CalledProcessError, BridgeError) as error:
        print(
            json.dumps(
                {
                    "error": {
                        "code": getattr(error, "code", "bundle_failed"),
                        "message": getattr(error, "message", "Cannot build the local bundle."),
                    }
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
