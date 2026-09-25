"""The development evaluator must fail on wrong context/values or missing inputs."""

import copy
import importlib.util
import json
import sqlite3
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("fault", [None, "value", "scale", "period", "basis", "missing", "error"])
def test_evaluator_detects_failures(tmp_path, fault):
    spec = importlib.util.spec_from_file_location(
        "evaluation", ROOT / "examples/evaluate_real_corpus.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    study = json.loads((ROOT / "examples/real-extraction/study.json").read_text())
    study["documents"] = study["documents"][:1]
    item = study["documents"][0]
    item["expected"] = item["expected"][:1]
    recipe = json.loads((ROOT / "examples/real-extraction" / item["recipe"]).read_text())
    recipe["mappings"] = recipe["mappings"][:1]
    (tmp_path / item["recipe"]).write_text(json.dumps(recipe))
    (tmp_path / "study.json").write_text(json.dumps(study))
    context = {
        key: value
        for key, value in recipe["mappings"][0].items()
        if key
        in (
            "metric",
            "period_start",
            "period_end",
            "period_kind",
            "source_scale",
            "reporting_basis",
            "accounting_standard",
            "currency",
        )
    }
    candidate = {
        "mapping_index": 0,
        "context": context,
        "source_value": "226973",
        "value_in_inr": "226973000000",
    }
    run = {
        "candidates": [copy.deepcopy(candidate)],
        "errors": [],
        "status": "needs_review",
        "run_id": "mock-run",
    }
    if fault == "value":
        run["candidates"][0]["source_value"] = "226974"
    if fault == "scale":
        run["candidates"][0]["value_in_inr"] = "2269730000000"
    if fault == "period":
        run["candidates"][0]["context"]["period_kind"] = "year"
    if fault == "basis":
        run["candidates"][0]["context"]["reporting_basis"] = "standalone"
    if fault == "error":
        run["errors"] = [{"mapping_index": 0, "error": "ANCHOR_MISMATCH"}]
        run["candidates"] = []
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE documents(id, sha, manifest, imported_at)")
        if fault != "missing":
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?)",
                (
                    "mock-document",
                    item["sha256"],
                    json.dumps({"filing_id": item["source_key"], "data_kind": "real"}),
                    "2026-09-25",
                ),
            )
        archive = SimpleNamespace(connect=lambda: nullcontext(connection), extract=lambda *_: run)
        result = module.evaluate(archive, tmp_path / "study.json")
    assert result["all_matched"] is (fault is None)
    assert result["matched_cells"] == (1 if fault is None else 0)
