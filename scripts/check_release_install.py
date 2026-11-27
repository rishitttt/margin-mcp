"""Install final artifacts into separate fresh venvs; make no provider calls."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tarfile
import tempfile
import tomllib
import venv
from pathlib import Path


def check(args):
    dist = args.dist_dir.resolve()
    wheel = dist / f"margin_mcp-{args.version}-py3-none-any.whl"
    source = dist / f"margin_mcp-{args.version}.tar.gz"
    script = Path(__file__).with_name("check_installed_product.py").resolve()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MARGIN_")
        and k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY", "PYTHONPATH"}
    }
    results = {}
    with tempfile.TemporaryDirectory(prefix="margin-release-install-") as tmp:
        root = Path(tmp)

        def run(command, cwd=root):
            subprocess.run([str(x) for x in command], cwd=cwd, env=env, check=True)

        for label, artifact, extra in (
            ("wheel-base", wheel, ""),
            ("sdist-base", source, ""),
            ("wheel-workbench", wheel, "[workbench]"),
        ):
            location = root / label
            venv.EnvBuilder(with_pip=True).create(location)
            python = location / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "--isolated",
                    "install",
                    "--index-url",
                    "https://pypi.org/simple",
                    str(artifact) + extra,
                ]
            )
            smoke = root / f"{label}.json"
            command = [python, "-I", script, "--expected-version", args.version, "--output", smoke]
            if extra:
                command.append("--workbench")
            run(command)
            results[label] = json.loads(smoke.read_text())
            if extra:
                with tarfile.open(source) as archive:
                    archive.extractall(root / "sdist", filter="data")
                extracted = root / "sdist" / f"margin_mcp-{args.version}"
                config = tomllib.loads((extracted / "pyproject.toml").read_text())
                deps = [
                    d
                    for d in config["project"]["optional-dependencies"]["dev"]
                    if d.startswith(("pytest==", "pytest-asyncio=="))
                ]
                run(
                    [
                        python,
                        "-m",
                        "pip",
                        "--isolated",
                        "install",
                        "--index-url",
                        "https://pypi.org/simple",
                        *deps,
                    ]
                )
                tests = (
                    ["tests"]
                    if os.name != "nt"
                    else [
                        "tests/test_network_guard.py",
                        "tests/test_core.py",
                        "tests/test_finance.py",
                        "tests/test_protocols.py",
                        "tests/test_product_reports.py",
                        "tests/test_typed_readiness_dcf.py",
                        "tests/test_workbench_views.py",
                        "tests/test_distributions.py",
                        "tests/test_local_config.py",
                    ]
                )
                run([python, "-m", "pytest", "-q", *tests], cwd=extracted)
                results["sdist-tests"] = "passed" if os.name != "nt" else "portable subset passed"
    return {"version": args.version, "status": "passed", "results": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(check(args), indent=2) + "\n"
    if args.output:
        args.output.write_text(report)
    print(report, end="")
