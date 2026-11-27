"""Relocatable entry point copied into a private test bundle as margin_local.py."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from uuid import uuid4


def clean_environment():
    return {
        k: v
        for k, v in os.environ.items()
        if k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"} and not k.startswith("MARGIN_")
    }


def write_config(path, data):
    with path.open("x", encoding="utf-8") as stream:
        path.chmod(0o600)
        json.dump(data, stream, indent=2)
        stream.write("\n")


def setup(root, arguments):
    parser = argparse.ArgumentParser(
        description="Install a local runtime/skill. --task-file opts into private pilot logging."
    )
    parser.add_argument(
        "--python",
        type=Path,
        help="Existing Python interpreter; default creates .venv with current Python >=3.12",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Testing/managed runtime only: interpreter already has margin-mcp[workbench]",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Host-specific skill directory; default workspace/.agents/skills/margin-research",
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--mode", choices=["live", "synthetic"], default="live")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--task-file", type=Path)
    group.add_argument("--no-recording", action="store_true")
    parser.add_argument("--retention-until", help="Required with --task-file: YYYY-MM-DD")
    parser.add_argument("--agent-label", default="unspecified")
    args = parser.parse_args(arguments)
    if sys.version_info < (3, 12):  # noqa: UP036 -- standalone bootstrap can run before installation
        parser.error("Run setup with Python 3.12 or newer.")
    if not 1 <= args.port <= 65535:
        parser.error("Use a valid local TCP port.")
    if args.task_file and not args.retention_until:
        parser.error("--task-file requires an explicit --retention-until review date.")
    if args.skip_install and not args.python:
        parser.error("--skip-install requires an existing --python interpreter.")
    if (root / "local.json").exists():
        parser.error(
            "This copy is already configured. Use a separate extracted copy/workspace for another agent."
        )
    target = (
        args.target.expanduser().absolute()
        if args.target
        else root / "workspace/.agents/skills/margin-research"
    )
    if target.exists() or target.resolve().is_relative_to((root / "margin-research").resolve()):
        parser.error("Choose a new skill destination outside the source skill directory.")
    environment = clean_environment()
    if args.python:
        python = args.python.expanduser().absolute()
    else:
        location = root / ".venv"
        venv.EnvBuilder(with_pip=True).create(location)
        python = location / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not args.skip_install:
        wheels = list((root / "runtime").glob("margin_mcp-*.whl")) + list(
            (root / "runtime").glob("margin_research-*.whl")
        )
        if len(wheels) != 1:
            parser.error("Bundle must contain exactly one Margin runtime wheel.")
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "-c",
                str(root / "runtime/requirements.lock"),
                str(wheels[0]) + "[workbench]",
            ],
            env=environment,
            check=True,
        )
    # Ensure an explicitly selected runtime really has both adapters before configuring paths.
    subprocess.run(
        [str(python), "-c", "import margin.interfaces.agent.cli, margin.interfaces.workbench.app"],
        env=environment,
        check=True,
    )
    config = {
        "python": str(python),
        "url": f"http://127.0.0.1:{args.port}",
        "expect_mode": args.mode,
    }
    if args.task_file:
        session = root / "private/sessions" / uuid4().hex[:12]
        pilot = root / "runtime/pilot.py"
        init = [
            str(python),
            str(pilot),
            "--session",
            str(session),
            "init",
            "--task-file",
            str(args.task_file.expanduser().absolute()),
            "--mode",
            args.mode,
            "--retention-until",
            args.retention_until,
            "--agent-label",
            args.agent_label,
        ]
        if args.mode == "live":
            init.append("--allow-live-recording")
        if (root / "private/providers.env").exists():
            init += ["--redact-env-file", str(root / "private/providers.env")]
        subprocess.run(init, env=environment, check=True)
        config.update(session=str(session), pilot_runner=str(pilot))
    shutil.copytree(root / "margin-research", target)
    write_config(target / "connection.json", config)
    write_config(
        root / "local.json",
        {"python": str(python), "skill": str(target), "port": args.port, "mode": args.mode},
    )
    print(
        json.dumps(
            {
                "status": "configured",
                "skill": str(target),
                "workspace": str(root / "workspace"),
                "recording": bool(args.task_file),
            }
        )
    )
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parent
    if not args or args[0] not in {"setup", "serve", "agent", "submit"}:
        print("Usage: python3 margin_local.py setup|serve|agent|submit ...", file=sys.stderr)
        return 2
    try:
        if args[0] == "setup":
            return setup(root, args[1:])
        config = json.loads((root / "local.json").read_text())
        environment = clean_environment()
        if args[0] == "submit":
            command = [
                config["python"],
                str(root / "runtime/submit.py"),
                "--bundle-root",
                str(root),
                *args[1:],
            ]
        elif args[0] == "agent":
            command = [
                config["python"],
                str(Path(config["skill"]) / "scripts/margin.py"),
                *args[1:],
            ]
        else:
            command = [
                config["python"],
                "-m",
                "margin.interfaces.agent.backend",
                "--port",
                str(config["port"]),
                "--mode",
                config["mode"],
            ]
            credentials = root / "private/providers.env"
            if credentials.exists():
                command += ["--credentials-file", str(credentials)]
            command += args[1:]
            # Replace the wrapper so Ctrl-C and process termination reach the actual backend.
            os.execve(config["python"], command, environment)
        return subprocess.run(command, env=environment, check=False).returncode
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        print(
            "Local setup/command failed. Check configuration and dependencies; no automatic retry.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
