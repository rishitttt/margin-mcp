"""Run the selected real-cell development study against a private, pre-imported archive.

No downloads and no fact publication. Expectations were visually transcribed during
recipe development, not labelled by an independent reviewer or held out from development.
"""

import argparse
import json
from decimal import Decimal
from pathlib import Path

from margin_mcp.ingestion import DocumentArchive, read_json
from margin_mcp.ingestion_models import ExtractionRecipe
from margin_mcp.storage import MarginError


def evaluate(archive: DocumentArchive, study_path: Path) -> dict:
    study = read_json(study_path)
    with archive.connect() as connection:
        records = connection.execute(
            "SELECT id, sha, manifest FROM documents ORDER BY imported_at DESC, id"
        ).fetchall()
    results = []
    for item in study["documents"]:
        selected = next(
            (
                row
                for row in records
                if row[1] == item["sha256"]
                and json.loads(row[2])["filing_id"] == item["source_key"]
                and json.loads(row[2])["data_kind"] == "real"
            ),
            None,
        )
        record = {
            "source_key": item["source_key"],
            "selected_cells": len(item["expected"]),
            "matched_cells": 0,
            "checks": [],
        }
        if selected is None:
            record.update(status="document_missing", errors=["Import the catalog document first."])
            results.append(record)
            continue
        recipe_path = (study_path.parent / item["recipe"]).resolve()
        if not recipe_path.is_relative_to(study_path.parent.resolve()):
            raise ValueError("Recipe must be inside the study directory")
        recipe = ExtractionRecipe.model_validate(read_json(recipe_path))
        if len(recipe.mappings) != len(item["expected"]):
            raise ValueError("Expected cells must cover every mapping")
        run = archive.extract(selected[0], recipe)
        by_index = {c["mapping_index"]: c for c in run["candidates"]}
        scale = {"million": 1000000, "crore": 10000000}[item["source_scale"]]
        for index, expected in enumerate(item["expected"]):
            candidate = by_index.get(index)
            matched = candidate is not None and all(
                candidate["context"][key] == expected[key]
                for key in ("metric", "period_start", "period_end", "period_kind")
            )
            matched = matched and all(
                candidate["context"][key] == value
                for key, value in {
                    "source_scale": item["source_scale"],
                    "currency": "INR",
                    "reporting_basis": "consolidated",
                    "accounting_standard": "Ind AS",
                }.items()
            )
            matched = matched and candidate["source_value"] == expected["source_value"]
            matched = matched and Decimal(candidate["value_in_inr"]) == (
                Decimal(expected["source_value"]) * scale
            )
            record["checks"].append(
                {
                    **expected,
                    "mapping_index": index,
                    "matched": bool(matched),
                    "actual_source_value": candidate["source_value"] if candidate else None,
                    "value_in_inr": candidate["value_in_inr"] if candidate else None,
                }
            )
            record["matched_cells"] += int(bool(matched))
        record.update(
            status="matched"
            if record["matched_cells"] == record["selected_cells"] and not run["errors"]
            else "mismatch_or_failure",
            extraction_status=run["status"],
            run_id=run["run_id"],
            document_id=selected[0],
            errors=run["errors"],
        )
        results.append(record)
    return {
        "purpose": study["purpose"],
        "review_status": study["review_status"],
        "selected_cells": sum(r["selected_cells"] for r in results),
        "matched_cells": sum(r["matched_cells"] for r in results),
        "all_matched": bool(results) and all(r["status"] == "matched" for r in results),
        "documents": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument(
        "--study", type=Path, default=Path(__file__).parent / "real-extraction/study.json"
    )
    args = parser.parse_args()
    try:
        result = evaluate(DocumentArchive(args.archive), args.study)
    except (MarginError, ValueError, OSError) as exc:
        parser.exit(2, f"{exc}\n")
    print(json.dumps(result, indent=2))
    return 0 if result["all_matched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
