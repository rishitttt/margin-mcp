import copy
import importlib.util
import json
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from margin_mcp.ingestion import DocumentArchive, normalize_inr, parse_number, read_json
from margin_mcp.ingestion_models import DocumentManifest, ExtractionRecipe
from margin_mcp.storage import MarginError


@pytest.fixture
def ingestion(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "demo", Path(__file__).parents[1] / "examples/make_ingestion_demo.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path, manifest, recipe = module.create_demo(tmp_path / "input")
    archive = DocumentArchive(tmp_path / "archive")
    return archive, path, manifest, recipe


def register(ingestion):
    archive, path, manifest, recipe = ingestion
    result = archive.import_document(path, DocumentManifest.model_validate(manifest))
    return archive, result, ExtractionRecipe.model_validate(recipe)


def test_import_inspect_extract_replay(ingestion):
    archive, result, recipe = register(ingestion)
    assert result["pages"] == 1 and not result["duplicate"]
    assert archive.import_document(ingestion[1], DocumentManifest(**ingestion[2]))["duplicate"]
    page = archive.inspect(result["document_id"], 1)
    assert page["status"] == "text_available"
    assert page["words"][0]["text"] == "SYNTHETIC"
    run = archive.extract(result["document_id"], recipe)
    assert run["status"] == "needs_review"
    assert run == archive.extract(result["document_id"], recipe)
    a, b, c = run["candidates"]
    assert a["source_value"] == "1234.50"
    assert Decimal(a["value_in_inr"]) == Decimal("12345000000")
    assert b["source_value"] == "-120.25"
    assert c["source_value"] is None and c["missing_reason"]
    assert a["evidence"]["value"]["page"] == 1
    assert a["evidence"]["value"]["text"] == "1,234.50"
    assert a["context"]["reporting_basis"] == "consolidated"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0", "0"),
        ("1,23,456.78", "123456.78"),
        ("1,234,567", "1234567"),
        ("(25.5)", "-25.5"),
        ("−12", "-12"),
        ("—", None),
        ("", None),
    ],
)
def test_number_semantics(raw, expected):
    assert parse_number(raw) == (Decimal(expected) if expected is not None else None)


@pytest.mark.parametrize("raw", ["12 34", "1,23", "12%", "1\n2", "NaN", "(1)-", "1.2.3"])
def test_ambiguous_values_are_not_guessed(raw):
    with pytest.raises(MarginError, match="AMBIGUOUS_VALUE"):
        parse_number(raw)


def test_no_query_side_effects(tmp_path):
    archive = DocumentArchive(tmp_path / "absent")
    with pytest.raises(MarginError, match="ARCHIVE_NOT_FOUND"):
        archive.inspect("x", 1)
    assert not archive.path.parent.exists()


def test_invalid_pdf_does_not_create_archive(ingestion):
    archive, path, manifest, _ = ingestion
    path.write_bytes(b"%PDF-this-is-corrupt")
    with pytest.raises(MarginError, match="INVALID_PDF"):
        archive.import_document(path, DocumentManifest(**manifest))
    assert not archive.path.exists()


def test_unrelated_database_preserved(ingestion):
    archive, path, manifest, _ = ingestion
    archive.path.parent.mkdir()
    with sqlite3.connect(archive.path) as db:
        db.execute("CREATE TABLE unrelated(value TEXT)")
    with pytest.raises(MarginError, match="INVALID_ARCHIVE"):
        archive.import_document(path, DocumentManifest(**manifest))
    with sqlite3.connect(archive.path) as db:
        assert db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [
            ("unrelated",)
        ]


def test_same_bytes_new_provenance_and_changed_bytes_preserved(ingestion):
    archive, result, _ = register(ingestion)
    manifest = {**ingestion[2], "title": "Another source observation"}
    second = archive.import_document(ingestion[1], DocumentManifest(**manifest))
    assert second["document_id"] != result["document_id"]
    assert second["sha256"] == result["sha256"]
    original = ingestion[1].read_bytes()
    ingestion[1].write_bytes(original + b"\n%new-version\n")
    third = archive.import_document(ingestion[1], DocumentManifest(**manifest))
    assert third["sha256"] != second["sha256"]
    assert archive.read_document(result["document_id"])[0] == original
    with sqlite3.connect(archive.path) as db:
        assert db.execute("SELECT count(*) FROM blobs").fetchone()[0] == 2


def test_tampered_bytes_rejected(ingestion):
    archive, result, recipe = register(ingestion)
    with sqlite3.connect(archive.path) as db:
        db.execute("UPDATE blobs SET data=?", (b"bad",))
    with pytest.raises(MarginError, match="CORRUPT_DOCUMENT"):
        archive.extract(result["document_id"], recipe)


def test_hash_bound_recipe_and_anchor_errors(ingestion):
    archive, result, recipe = register(ingestion)
    wrong = recipe.model_dump(mode="json")
    wrong["document_sha256"] = "0" * 64
    with pytest.raises(MarginError, match="DOCUMENT_MISMATCH"):
        archive.extract(result["document_id"], ExtractionRecipe(**wrong))
    changed = recipe.model_dump(mode="json")
    changed["mappings"][0]["basis_header"]["expected_text"] = "Standalone"
    failed = archive.extract(result["document_id"], ExtractionRecipe(**changed))
    assert failed["status"] == "failed" and "ANCHOR_MISMATCH" in failed["errors"][0]["error"]
    successful = archive.extract(result["document_id"], recipe)
    assert successful["status"] == "needs_review"
    assert failed["run_id"] != successful["run_id"]


@pytest.mark.parametrize("field,value", [("page", 2), ("bbox", [0, 0, 999, 999])])
def test_regions_fail_explicitly(ingestion, field, value):
    archive, result, recipe = register(ingestion)
    data = recipe.model_dump(mode="json")
    data["mappings"][0]["value"][field] = value
    run = archive.extract(result["document_id"], ExtractionRecipe(**data))
    assert run["status"] == "failed" and "INVALID_REGION" in run["errors"][0]["error"]


def test_manifest_context_and_json_validation(ingestion, tmp_path):
    manifest = {**ingestion[2], "data_kind": "real"}
    with pytest.raises(ValidationError, match="source_url"):
        DocumentManifest(**manifest)
    recipe = copy.deepcopy(ingestion[3])
    recipe["mappings"].append(recipe["mappings"][0])
    with pytest.raises(ValidationError, match="Duplicate"):
        ExtractionRecipe(**recipe)
    path = tmp_path / "duplicate.json"
    path.write_text('{"x":1,"x":2}')
    with pytest.raises(MarginError):
        read_json(path)


def test_cli_end_to_end_and_failed_exit(ingestion):
    archive, path, _, _ = ingestion

    def cli(*args):
        return subprocess.run(
            [sys.executable, "-m", "margin_mcp", *args], capture_output=True, text=True, timeout=15
        )

    imported = cli(
        "import-document",
        str(path),
        "--manifest",
        str(path.parent / "document.json"),
        "--archive",
        str(archive.path.parent),
    )
    assert imported.returncode == 0, imported.stderr
    identifier = json.loads(imported.stdout)["document_id"]
    extracted = cli(
        "extract-document",
        identifier,
        "--recipe",
        str(path.parent / "recipe.json"),
        "--archive",
        str(archive.path.parent),
    )
    assert extracted.returncode == 0, extracted.stderr
    assert json.loads(extracted.stdout)["status"] == "needs_review"
    invalid = cli(
        "inspect-document", identifier, "--page", "0", "--archive", str(archive.path.parent)
    )
    assert invalid.returncode == 2 and "INVALID_PAGE" in invalid.stderr


def test_exact_decimal_beyond_default_precision():
    value = parse_number("(123456789012345678901234567890.123)")
    assert str(value) == "-123456789012345678901234567890.123"
    assert normalize_inr(value, 10000000) == "-1234567890123456789012345678901230000.000"


def test_blank_page_reports_ocr_and_encrypted_pdf_rejected(ingestion):
    from reportlab.lib.pdfencrypt import StandardEncryption
    from reportlab.pdfgen import canvas

    archive, path, manifest, _ = ingestion
    blank = canvas.Canvas(str(path))
    blank.showPage()
    blank.save()
    result = archive.import_document(path, DocumentManifest(**manifest))
    assert archive.inspect(result["document_id"], 1)["status"] == "ocr_required"
    encrypted = canvas.Canvas(str(path), encrypt=StandardEncryption("secret"))
    encrypted.drawString(40, 40, "private")
    encrypted.save()
    with pytest.raises(MarginError, match="INVALID_PDF"):
        archive.import_document(path, DocumentManifest(**manifest))


def test_limits_and_period_errors(ingestion, monkeypatch):
    from margin_mcp import ingestion as module

    archive, result, recipe = register(ingestion)
    data = recipe.model_dump(mode="json")
    data["mappings"][0]["period_end"] = "2027-09-30"
    failed = archive.extract(result["document_id"], ExtractionRecipe(**data))
    assert "INVALID_PERIOD" in failed["errors"][0]["error"]
    monkeypatch.setattr(module, "MAX_PDF_BYTES", 10)
    with pytest.raises(MarginError, match="INVALID_PDF"):
        archive.import_document(ingestion[1], DocumentManifest(**ingestion[2]))
