"""Validate the two public release archives without importing Margin or using the network."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import tarfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

NAME = "margin-mcp"
AUTHORS = "Rishit Anand, Advait Sharma, Arsalaan Alam, Tanvi Sanghai"
ASSETS = {
    "margin/resources/drishti-contracts.json",
    *{
        "margin/interfaces/workbench/static/" + name
        for name in ("app.js", "favicon.svg", "index.html", "style.css")
    },
}
SECRET_PATTERNS = (
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"\bpypi-[A-Za-z0-9_-]{40,}",
    rb"\bgh[pousr]_[A-Za-z0-9]{30,}",
    rb"\bgithub_pat_[A-Za-z0-9_]{40,}",
    rb"\bAKIA[A-Z0-9]{16}\b",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_paths(files, *, wheel=False):
    for name, data in files.items():
        path = PurePosixPath(name)
        require(
            not path.is_absolute() and ".." not in path.parts and "\\" not in name,
            f"Unsafe archive path: {name}",
        )
        require(
            not any(
                part
                in {
                    "research",
                    "packaging",
                    "reports",
                    "releases",
                    "skills",
                    ".git",
                    ".github",
                    "private",
                    "logs",
                    "repository",
                    "__pycache__",
                    ".venv",
                }
                for part in path.parts
            ),
            f"Repository-only content in public archive: {name}",
        )
        require(
            not path.name.startswith(".env")
            and path.name not in {"providers.env", "connection.json", ".DS_Store"}
            and path.suffix not in {".pyc", ".pyo", ".pem", ".key", ".db", ".sqlite", ".sqlite3"},
            f"Private/generated file in public archive: {name}",
        )
        require(
            not any(re.search(pattern, data) for pattern in SECRET_PATTERNS),
            f"Potential credential in archive member; content withheld: {name}",
        )
        if wheel:
            require(
                name.startswith("margin/") or re.match(r"^margin_mcp-[^/]+\.dist-info/", name),
                f"Unexpected wheel member: {name}",
            )


def metadata(data, version):
    meta = BytesParser().parsebytes(data)
    for field, value in {
        "Name": NAME,
        "Version": version,
        "Requires-Python": ">=3.12",
        "License-Expression": "MIT",
        "Author": AUTHORS,
        "Description-Content-Type": "text/markdown",
    }.items():
        require(meta[field] == value, f"Incorrect or missing {field} metadata")
    require(meta.get_all("License-File") == ["LICENSE"], "Missing LICENSE metadata")
    urls = meta.get_all("Project-URL", [])
    require(any(url.startswith("Repository, ") for url in urls), "Missing repository URL")
    return meta


def validate(dist, version):
    wheels, sources = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    require(
        len(wheels) == len(sources) == 1, "Use a clean directory containing one wheel and one sdist"
    )
    wheel, source = wheels[0], sources[0]
    require(wheel.name == f"margin_mcp-{version}-py3-none-any.whl", "Unexpected wheel name/tag")
    require(source.name == f"margin_mcp-{version}.tar.gz", "Unexpected sdist name")
    with ZipFile(wheel) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), "Duplicate wheel members")
        wheel_files = {
            name: archive.read(name) for name in archive.namelist() if not name.endswith("/")
        }
    with tarfile.open(source) as archive:
        members = [m for m in archive.getmembers() if not m.isdir()]
        require(all(m.isfile() for m in members), "Source archive contains non-regular files")
        require(len({m.name for m in members}) == len(members), "Duplicate sdist members")
        prefix = f"margin_mcp-{version}/"
        require(all(m.name.startswith(prefix) for m in members), "Unexpected sdist root")
        source_files = {m.name.removeprefix(prefix): archive.extractfile(m).read() for m in members}
    check_paths(wheel_files, wheel=True)
    check_paths(source_files)
    info = f"margin_mcp-{version}.dist-info"
    metadata(wheel_files[f"{info}/METADATA"], version)
    metadata(source_files["PKG-INFO"], version)
    require(ASSETS <= wheel_files.keys(), "Missing runtime JSON/static assets")
    require(
        source_files["LICENSE"] == wheel_files[f"{info}/licenses/LICENSE"], "License files differ"
    )
    require(
        wheel_files[f"{info}/top_level.txt"].strip() == b"margin", "Unexpected top-level import"
    )
    entries = wheel_files[f"{info}/entry_points.txt"].decode()
    for command in ("margin-mcp", "margin-backend", "margin-agent", "margin-workbench"):
        require(f"{command} = " in entries, f"Missing console entrypoint: {command}")
    tree = ast.parse(wheel_files["margin/__init__.py"])
    versions = [
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in n.targets)
    ]
    require(versions == [version], "Code and distribution versions differ")
    source_runtime = {
        name.removeprefix("src/") for name in source_files if name.startswith("src/margin/")
    }
    wheel_runtime = {name for name in wheel_files if name.startswith("margin/")}
    require(source_runtime == wheel_runtime, "Wheel/sdist runtime file sets differ")
    for name, data in wheel_files.items():
        if name.startswith("margin/"):
            require(
                source_files.get("src/" + name) == data, f"Wheel/sdist runtime mismatch: {name}"
            )
    require("scripts/check_drishti_review.py" in source_files, "Missing distributed-test helper")
    require("tests/conftest.py" in source_files, "Missing offline test network guard")
    require(
        b"https://github.com/rishitttt/margin-mcp" in source_files["README.md"],
        "Missing public docs links",
    )
    return {
        "status": "passed",
        "distribution": NAME,
        "version": version,
        "files": {
            p.name: {
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "bytes": p.stat().st_size,
            }
            for p in (wheel, source)
        },
        "wheel_members": len(wheel_files),
        "sdist_members": len(source_files),
        "credential_scan": "known token/private-key patterns; review provider-specific secrets separately",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = validate(args.dist_dir, args.version)
    encoded = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
