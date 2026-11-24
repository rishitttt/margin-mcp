"""Installed launcher. connection.json contains local paths/origin only, never API keys."""

import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    try:
        config = json.loads((Path(__file__).parents[1] / "connection.json").read_text())
        python = config["python"]
        url = config["url"]
    except (OSError, ValueError, KeyError):
        print(
            "Margin skill is not configured. Run the repo's scripts/install_agent_skill.py.",
            file=sys.stderr,
        )
        return 2
    defaults = ["--expect-mode", config["expect_mode"]] if config.get("expect_mode") else []
    if sys.argv[1:2] in (["finish"], ["note"]) and not config.get("session"):
        print(
            json.dumps(
                {
                    "error": {
                        "code": "recording_not_configured",
                        "message": "This skill has no evaluation session. Configure one before recording summaries or a final answer.",
                    }
                }
            )
        )
        return 2
    if config.get("session"):
        command = [python, config["pilot_runner"], "--session", config["session"]]
        if sys.argv[1:2] in (["finish"], ["note"]):
            command += sys.argv[1:]
        else:
            command += ["call", "--url", url, *defaults, *sys.argv[1:]]
    else:
        command = [python, "-m", "margin.interfaces.agent", "--url", url, *defaults, *sys.argv[1:]]
    # Credentials stay in the separately running backend, even if this host inherited them.
    environment = {
        k: v for k, v in os.environ.items() if k not in {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}
    }
    return subprocess.run(command, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
