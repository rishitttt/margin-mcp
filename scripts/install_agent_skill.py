"""Install the repo-maintained skill with machine-local, credential-free connection settings."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from margin.interfaces.agent.client import local_url


def main():
    root = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--target",
        type=Path,
        default=Path(os.getenv("CODEX_HOME", Path.home() / ".codex")) / "skills/margin-research",
    )
    p.add_argument("--url", default="http://127.0.0.1:8765")
    p.add_argument("--session", type=Path, help="Existing optional private pilot session")
    args = p.parse_args()
    url = local_url(args.url)
    target = args.target.expanduser().absolute()
    source = root / "skills/margin-research"
    if target.resolve() == source.resolve() or target.exists():
        p.error("Choose a new installation directory; existing skills are not overwritten.")
    config = {"python": sys.executable, "url": url}
    if args.session:
        session = args.session.expanduser().resolve()
        if not (session / "session.json").is_file():
            p.error("Initialize the private pilot session first.")
        config.update(session=str(session), pilot_runner=str(root / "research/pilot.py"))
    shutil.copytree(source, target)
    path = target / "connection.json"
    path.write_text(json.dumps(config, indent=2) + "\n")
    path.chmod(0o600)
    print(f"Installed Margin skill: {target}")


if __name__ == "__main__":
    main()
