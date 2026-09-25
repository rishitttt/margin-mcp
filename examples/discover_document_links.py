"""Turn a saved source page into unverified document leads; performs no network requests."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from margin_mcp.source_links import document_links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()
    try:
        with args.html.open("rb") as stream:
            raw = stream.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("Saved HTML exceeds 2 MiB")
        links = document_links(raw.decode("utf-8"), args.source_url)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"{exc}\n")
    print(
        json.dumps(
            {
                "schema_version": 1,
                "source_html_sha256": hashlib.sha256(raw).hexdigest(),
                "parsed_at": datetime.now(UTC).isoformat(),
                "network_performed": False,
                "candidate_count": len(links),
                "candidates": links,
                "limitations": (
                    "Only anchor links; not complete coverage or verified document identity. "
                    "parsed_at is not page acquisition time. Preserve its receipt separately."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
