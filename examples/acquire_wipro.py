"""Compatibility command for the original Wipro acquisition experiment."""

import argparse
import json
from pathlib import Path

from margin_mcp.acquisition import AcquisitionSource, acquire_pdf
from margin_mcp.ingestion import read_json
from margin_mcp.storage import MarginError


def acquire(output: Path) -> dict:
    catalog = read_json(Path(__file__).with_name("public-document-sources.json"))
    return acquire_pdf(AcquisitionSource.model_validate(catalog["wipro-q2-fy26-reg33"]), output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(acquire(args.output), indent=2))
    except (MarginError, OSError, ValueError) as exc:
        parser.exit(2, f"acquisition: {exc}\n")
