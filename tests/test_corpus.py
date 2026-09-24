import json
import sqlite3

import pytest
from pydantic import ValidationError

from margin_mcp.cli import main
from margin_mcp.models import Corpus
from margin_mcp.storage import CorpusStore, MarginError, load_manifest


@pytest.mark.parametrize("field", ["company_id", "filing_id", "security_id", "listing"])
def test_duplicate_identities_are_rejected(payload, field):
    if field == "company_id":
        payload["companies"].append(payload["companies"][0])
    elif field == "filing_id":
        payload["filings"].append(payload["filings"][0])
    elif field == "security_id":
        payload["companies"][1]["securities"][0]["security_id"] = payload["companies"][0][
            "securities"
        ][0]["security_id"]
    else:
        payload["companies"][1]["securities"][0]["listings"][0]["symbol"] = "demoaaryasw"
    with pytest.raises(ValidationError, match="Duplicate"):
        Corpus.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("company_id", "missing-company"),
        ("reporting_basis", "combined"),
        ("period_end", None),
        ("period_start", "2026-01-01"),
        ("published_at", "2025-06-20T10:00:00"),
        ("observed_at", "2020-01-01T00:00:00Z"),
        ("source_url", "file:///etc/passwd"),
        ("invented_field", "not allowed"),
    ],
)
def test_bad_filing_context_is_rejected(payload, field, value):
    payload["filings"][0][field] = value
    with pytest.raises(ValidationError):
        Corpus.model_validate(payload)


def test_real_corpus_requires_identity_and_filing_provenance(payload):
    payload["data_kind"] = "real"
    with pytest.raises(ValidationError, match="identity source"):
        Corpus.model_validate(payload)
    for company in payload["companies"]:
        company["identity_source_url"] = "https://example.org/identity"
        company["identity_observed_at"] = "2026-09-23T12:00:00Z"
    with pytest.raises(ValidationError, match="source_url"):
        Corpus.model_validate(payload)
    for filing in payload["filings"]:
        filing["source_url"] = "https://example.org/filing"
    # This only tests required provenance fields, not real-data correctness or permissions.
    assert Corpus.model_validate(payload).data_kind == "real"
    payload["metadata_usage_basis"] = "   "
    with pytest.raises(ValidationError):
        Corpus.model_validate(payload)


def test_manifest_rejects_duplicate_json_keys(tmp_path):
    manifest = tmp_path / "bad.json"
    manifest.write_text('{"schema_version":1,"schema_version":2}')
    with pytest.raises(MarginError, match="duplicate JSON key"):
        load_manifest(manifest)


def test_read_does_not_create_missing_database(tmp_path):
    path = tmp_path / "not-created" / "missing.sqlite3"
    with pytest.raises(MarginError, match="CORPUS_NOT_LOADED"):
        CorpusStore(path).read()
    assert not path.parent.exists()


def test_import_requires_replace_and_preserves_old_snapshot(store, corpus):
    before = store.read()
    modified = corpus.model_copy(update={"title": "Changed title"})
    with pytest.raises(MarginError, match="CORPUS_EXISTS"):
        store.import_corpus(modified)
    assert store.read() == before
    after = store.import_corpus(modified, replace=True)
    assert after.revision != before.revision
    assert store.read().corpus.title == "Changed title"


def test_invalid_cli_replacement_leaves_existing_corpus_intact(store, payload, tmp_path, capsys):
    before = store.read()
    payload["filings"][0]["company_id"] = "nonexistent"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload))
    assert main(["import-corpus", str(path), "--db", str(store.path), "--replace"]) == 2
    assert "INVALID_CORPUS" in capsys.readouterr().err
    assert store.read() == before


def test_unrelated_database_cannot_be_overwritten(tmp_path, corpus):
    path = tmp_path / "unrelated.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE important_data (value TEXT)")
        connection.execute("INSERT INTO important_data VALUES ('keep me')")
    with pytest.raises(MarginError, match="not a Margin database"):
        CorpusStore(path).import_corpus(corpus, replace=True)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT value FROM important_data").fetchone()[0] == "keep me"


def test_tampered_snapshot_is_detected(store):
    with sqlite3.connect(store.path) as connection:
        connection.execute("UPDATE corpus SET payload='{}'")
    with pytest.raises(MarginError, match="checksum mismatch"):
        store.read()


def test_unsupported_database_version_is_rejected(store):
    with sqlite3.connect(store.path) as connection:
        connection.execute("PRAGMA user_version=99")
    with pytest.raises(MarginError, match="unsupported"):
        store.read()


def test_corpus_schema_is_machine_readable(capsys):
    assert main(["schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["additionalProperties"] is False
    assert "metadata_usage_basis" in schema["required"]
