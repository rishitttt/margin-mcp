"""Download one hash-pinned public filing from the reviewed example catalog."""

import argparse
import json
from pathlib import Path

from margin_mcp.acquisition import AcquisitionSource, acquire_pdf
from margin_mcp.ingestion import read_json
from margin_mcp.storage import MarginError

CATALOG = Path(__file__).with_name("public-document-sources.json")


def main():
    sources = read_json(CATALOG)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=sorted(sources))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        source = AcquisitionSource.model_validate(sources[args.source])
        print(json.dumps(acquire_pdf(source, args.output), indent=2))
    except (MarginError, OSError, ValueError) as exc:
        parser.exit(2, f"acquisition: {exc}\n")


if __name__ == "__main__":
    main()
