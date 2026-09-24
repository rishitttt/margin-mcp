"""One atomic, validated corpus snapshot for a deliberately small local pilot."""

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from margin_mcp.models import Corpus

APPLICATION_ID = 0x4D52474E
SCHEMA_VERSION = 1
MAX_CORPUS_BYTES = 5 * 1024 * 1024


class MarginError(ValueError):
    """A safe, actionable error suitable for a CLI or MCP caller."""


@dataclass(frozen=True)
class Snapshot:
    corpus: Corpus
    revision: str
    imported_at: datetime


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise MarginError(f"INVALID_CORPUS: duplicate JSON key {key}")
        result[key] = value
    return result


def load_manifest(path: Path) -> Corpus:
    with path.open("rb") as source:
        raw = source.read(MAX_CORPUS_BYTES + 1)
    if len(raw) > MAX_CORPUS_BYTES:
        raise MarginError("INVALID_CORPUS: manifest exceeds 5 MiB")
    try:
        payload = json.loads(raw, object_pairs_hook=_no_duplicate_keys)
        return Corpus.model_validate(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        if isinstance(exc, MarginError):
            raise
        raise MarginError(f"INVALID_CORPUS: {exc}") from exc


class CorpusStore:
    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()

    @staticmethod
    def _check_database(connection: sqlite3.Connection) -> None:
        if connection.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
            raise MarginError("INVALID_DATABASE: not a Margin database")
        if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
            raise MarginError("INVALID_DATABASE: unsupported Margin database version")

    def read(self) -> Snapshot:
        if not self.path.is_file():
            raise MarginError("CORPUS_NOT_LOADED: import a corpus into this database first")
        try:
            with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as connection:
                self._check_database(connection)
                row = connection.execute(
                    "SELECT payload, revision, imported_at FROM corpus WHERE singleton = 1"
                ).fetchone()
            if row is None:
                raise MarginError("CORPUS_NOT_LOADED: database contains no corpus")
            if hashlib.sha256(row[0].encode()).hexdigest() != row[1]:
                raise MarginError("INVALID_DATABASE: corpus checksum mismatch")
            return Snapshot(
                Corpus.model_validate_json(row[0]), row[1], datetime.fromisoformat(row[2])
            )
        except (sqlite3.Error, ValueError) as exc:
            if isinstance(exc, MarginError):
                raise
            raise MarginError("INVALID_DATABASE: cannot read a valid Margin corpus") from exc

    def import_corpus(self, corpus: Corpus, *, replace: bool = False) -> Snapshot:
        # Revalidate even an instance: callers can mutate nested lists on frozen models.
        corpus = Corpus.model_validate(corpus.model_dump(mode="json"))
        payload = json.dumps(corpus.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        if len(payload.encode()) > MAX_CORPUS_BYTES:
            raise MarginError("INVALID_CORPUS: serialized corpus exceeds 5 MiB")
        revision = hashlib.sha256(payload.encode()).hexdigest()
        imported_at = datetime.now(UTC)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Existing unrelated databases are never initialized or overwritten.
        existed = self.path.exists()
        try:
            with closing(sqlite3.connect(self.path, timeout=5)) as connection:
                connection.execute("BEGIN IMMEDIATE")
                if existed:
                    self._check_database(connection)
                else:
                    connection.execute(f"PRAGMA application_id = {APPLICATION_ID}")
                    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
                    connection.execute(
                        "CREATE TABLE corpus (singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                        "payload TEXT NOT NULL, revision TEXT NOT NULL, imported_at TEXT NOT NULL)"
                    )
                present = connection.execute("SELECT 1 FROM corpus WHERE singleton=1").fetchone()
                if present and not replace:
                    raise MarginError("CORPUS_EXISTS: use --replace to replace the entire corpus")
                connection.execute(
                    "INSERT OR REPLACE INTO corpus VALUES (1, ?, ?, ?)",
                    (payload, revision, imported_at.isoformat()),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise MarginError("IMPORT_FAILED: cannot write the Margin database") from exc
        return Snapshot(corpus, revision, imported_at)
