"""Private, explicit PDF ingestion. Candidate extraction never publishes financial facts."""

import hashlib
import io
import json
import re
import sqlite3
from contextlib import closing, contextmanager
from datetime import UTC, date, datetime
from decimal import Decimal, localcontext
from importlib.metadata import version
from pathlib import Path

import pdfplumber

from margin_mcp.ingestion_models import DocumentManifest, ExtractionRecipe, Region, TextAnchor
from margin_mcp.storage import MarginError, _no_duplicate_keys

MAX_PDF_BYTES = 25 * 1024 * 1024
MAX_PAGES = 500
ARCHIVE_ID = 0x4D524749
ARCHIVE_VERSION = 1
EXTRACTOR_VERSION = "regions-v1"


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise MarginError("INVALID_MANIFEST: JSON exceeds 1 MiB")
    try:
        return json.loads(raw, object_pairs_hook=_no_duplicate_keys)
    except (ValueError, UnicodeDecodeError) as exc:
        raise MarginError("INVALID_MANIFEST: invalid or duplicate-key JSON") from exc


@contextmanager
def open_pdf(raw: bytes):
    if not raw.startswith(b"%PDF-") or len(raw) > MAX_PDF_BYTES:
        raise MarginError("INVALID_PDF: expected a PDF of at most 25 MiB")
    try:
        pdf = pdfplumber.open(io.BytesIO(raw))
    except Exception as exc:
        raise MarginError("INVALID_PDF: unable to open PDF (encrypted or corrupt)") from exc
    try:
        if pdf.doc.encryption:
            raise MarginError("INVALID_PDF: encrypted PDFs are unsupported")
        if not 1 <= len(pdf.pages) <= MAX_PAGES:
            raise MarginError("INVALID_PDF: expected 1 to 500 pages")
        yield pdf
    except MarginError:
        raise
    except Exception as exc:
        raise MarginError("PDF_PROCESSING_FAILED: unable to process PDF") from exc
    finally:
        pdf.close()


def parse_number(text: str) -> Decimal | None:
    """Exact decimal parsing; dashes are missing, never zero. No numeric guessing."""
    value = text.strip().replace("\u2212", "-")
    if value in {"", "-", "–", "—", "N/A", "NA"}:
        return None
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()
    elif value.startswith("-"):
        negative, value = True, value[1:]
    pattern = r"(?:\d+|\d{1,3}(?:,\d{3})+|\d{1,2}(?:,\d{2})*,\d{3})(?:\.\d+)?"
    if not re.fullmatch(pattern, value):
        raise MarginError("AMBIGUOUS_VALUE: region must contain exactly one plain number")
    number = Decimal(value.replace(",", ""))
    return number.copy_negate() if negative else number


def normalize_inr(value: Decimal | None, scale: int) -> str | None:
    if value is None:
        return None
    with localcontext() as context:
        context.prec = max(28, len(value.as_tuple().digits) + len(str(scale)))
        return str(value * scale)


def extract_region(pdf, region: Region) -> str:
    if region.page > len(pdf.pages):
        raise MarginError("INVALID_REGION: page is outside document")
    page = pdf.pages[region.page - 1]
    x0, top, x1, bottom = region.bbox
    bx0, btop, bx1, bbottom = page.bbox
    if x0 < bx0 or top < btop or x1 > bx1 or bottom > bbottom:
        raise MarginError("INVALID_REGION: bbox is outside page")
    text = page.within_bbox(region.bbox).extract_text() or ""
    if isinstance(region, TextAnchor):
        if " ".join(text.split()) != " ".join(region.expected_text.split()):
            raise MarginError("ANCHOR_MISMATCH: extracted source text differs from recipe")
    return text


class DocumentArchive:
    """Separate versioned SQLite archive; leaves the milestone-1 corpus schema unchanged.

    PDF blobs and registration records commit in one transaction. IDs bind content to provenance.
    This small private archive is not an untrusted-upload service or a hosted entitlement system.
    """

    def __init__(self, directory: Path):
        self.path = directory.expanduser().resolve() / "documents.sqlite3"

    @contextmanager
    def connect(self, *, write: bool = False):
        if not write and not self.path.is_file():
            raise MarginError("ARCHIVE_NOT_FOUND: import a document first")
        if write:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        uri = self.path.as_uri() + ("?mode=rwc" if write else "?mode=ro")
        try:
            with closing(sqlite3.connect(uri, uri=True, timeout=5)) as connection:
                connection.execute("PRAGMA foreign_keys=ON")
                if write:
                    connection.execute("BEGIN IMMEDIATE")
                app_id = connection.execute("PRAGMA application_id").fetchone()[0]
                tables = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                schema = connection.execute("PRAGMA user_version").fetchone()[0]
                if write and app_id == 0 and schema == 0 and not tables:
                    connection.execute(f"PRAGMA application_id={ARCHIVE_ID}")
                    connection.execute(f"PRAGMA user_version={ARCHIVE_VERSION}")
                    connection.execute(
                        "CREATE TABLE blobs (sha TEXT PRIMARY KEY, data BLOB NOT NULL, "
                        "pages INTEGER NOT NULL)"
                    )
                    connection.execute(
                        "CREATE TABLE documents (id TEXT PRIMARY KEY, sha TEXT NOT NULL "
                        "REFERENCES blobs(sha), manifest TEXT NOT NULL, imported_at TEXT NOT NULL)"
                    )
                    connection.execute(
                        "CREATE TABLE runs (id TEXT PRIMARY KEY, document_id TEXT NOT NULL "
                        "REFERENCES documents(id), payload TEXT NOT NULL)"
                    )
                elif app_id != ARCHIVE_ID or schema != ARCHIVE_VERSION:
                    raise MarginError("INVALID_ARCHIVE: unrelated or unsupported database")
                try:
                    yield connection
                    if write:
                        connection.commit()
                except Exception:
                    if write:
                        connection.rollback()
                    raise
        except sqlite3.Error as exc:
            raise MarginError("ARCHIVE_ERROR: cannot read/write document archive") from exc

    def import_document(self, path: Path, manifest: DocumentManifest) -> dict:
        manifest = DocumentManifest.model_validate(manifest.model_dump(mode="json"))
        with path.open("rb") as stream:
            raw = stream.read(MAX_PDF_BYTES + 1)
        with open_pdf(raw) as pdf:
            pages = len(pdf.pages)
        sha = digest(raw)
        payload = canonical(manifest.model_dump(mode="json"))
        document_id = digest((sha + payload).encode())
        with self.connect(write=True) as connection:
            existing = connection.execute("SELECT data FROM blobs WHERE sha=?", (sha,)).fetchone()
            if existing is not None and digest(existing[0]) != sha:
                raise MarginError("CORRUPT_DOCUMENT: stored bytes failed checksum")
            duplicate = (
                connection.execute("SELECT 1 FROM documents WHERE id=?", (document_id,)).fetchone()
                is not None
            )
            connection.execute("INSERT OR IGNORE INTO blobs VALUES (?, ?, ?)", (sha, raw, pages))
            connection.execute(
                "INSERT OR IGNORE INTO documents VALUES (?, ?, ?, ?)",
                (document_id, sha, payload, datetime.now(UTC).isoformat()),
            )
        return {
            "document_id": document_id,
            "sha256": sha,
            "pages": pages,
            "duplicate": duplicate,
            "data_kind": manifest.data_kind,
        }

    def read_document(self, document_id: str) -> tuple[bytes, dict]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT d.sha, d.manifest, d.imported_at, b.data, b.pages "
                "FROM documents d JOIN blobs b ON b.sha=d.sha WHERE d.id=?",
                (document_id,),
            ).fetchone()
        if row is None:
            raise MarginError("DOCUMENT_NOT_FOUND: use the ID returned by import-document")
        sha, payload, imported_at, raw, pages = row
        if digest(raw) != sha or digest((sha + payload).encode()) != document_id:
            raise MarginError("CORRUPT_DOCUMENT: stored bytes or provenance failed checksum")
        manifest = DocumentManifest.model_validate_json(payload)
        return raw, {
            "document_id": document_id,
            "sha256": sha,
            "pages": pages,
            "imported_at": imported_at,
            "manifest": manifest.model_dump(mode="json"),
        }

    def inspect(self, document_id: str, page_number: int) -> dict:
        raw, metadata = self.read_document(document_id)
        with open_pdf(raw) as pdf:
            if not 1 <= page_number <= len(pdf.pages):
                raise MarginError("INVALID_PAGE: use a physical page number starting at 1")
            page = pdf.pages[page_number - 1]
            words = [
                {k: word[k] for k in ("text", "x0", "top", "x1", "bottom")}
                for word in page.extract_words()
            ]
            return {
                **metadata,
                "page": page_number,
                "bbox": page.bbox,
                "text": page.extract_text() or "",
                "words": words,
                "status": "text_available" if words else "ocr_required",
            }

    def extract(self, document_id: str, recipe: ExtractionRecipe) -> dict:
        recipe = ExtractionRecipe.model_validate(recipe.model_dump(mode="json"))
        raw, metadata = self.read_document(document_id)
        if recipe.document_sha256 != metadata["sha256"]:
            raise MarginError("DOCUMENT_MISMATCH: recipe is bound to different PDF bytes")
        parser = {
            "name": "pdfplumber",
            "version": version("pdfplumber"),
            "extractor": EXTRACTOR_VERSION,
            "pdfminer_version": version("pdfminer.six"),
        }
        identity = {
            "document_id": document_id,
            "recipe": recipe.model_dump(mode="json"),
            "parser": parser,
        }
        run_id = digest(canonical(identity).encode())
        with self.connect() as connection:
            existing = connection.execute(
                "SELECT payload FROM runs WHERE id=?", (run_id,)
            ).fetchone()
        if existing:
            return json.loads(existing[0])
        candidates = []
        errors = []
        with open_pdf(raw) as pdf:
            for index, mapping in enumerate(recipe.mappings):
                try:
                    if mapping.period_end > date.fromisoformat(
                        metadata["manifest"]["published_on"]
                    ):
                        raise MarginError("INVALID_PERIOD: reporting period follows publication")
                    evidence = {}
                    for key in (
                        "label",
                        "period_header",
                        "basis_header",
                        "unit_header",
                        "standard_header",
                        "value",
                    ):
                        region = getattr(mapping, key)
                        evidence[key] = {
                            **region.model_dump(mode="json"),
                            "text": extract_region(pdf, region),
                        }
                    value = parse_number(evidence["value"]["text"])
                    scale = {"rupee": 1, "lakh": 100000, "crore": 10000000, "million": 1000000}[
                        mapping.source_scale
                    ]
                    candidates.append(
                        {
                            "mapping_index": index,
                            "context": mapping.model_dump(
                                mode="json",
                                exclude={
                                    "label",
                                    "value",
                                    "period_header",
                                    "basis_header",
                                    "unit_header",
                                    "standard_header",
                                },
                            ),
                            "source_value": str(value) if value is not None else None,
                            "value_in_inr": normalize_inr(value, scale),
                            "missing_reason": "blank_or_missing_marker" if value is None else None,
                            "evidence": evidence,
                            "status": "needs_review",
                        }
                    )
                except MarginError as exc:
                    errors.append({"mapping_index": index, "error": str(exc)})
        result = {
            "run_id": run_id,
            **identity,
            "document": metadata,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "failed" if errors else "needs_review",
            "candidates": candidates,
            "errors": errors,
            "warnings": [
                "Context is operator-mapped, not independently inferred.",
                "Unreviewed extraction; not available through MCP fact tools.",
            ],
        }
        with self.connect(write=True) as connection:
            connection.execute(
                "INSERT OR IGNORE INTO runs VALUES (?, ?, ?)",
                (run_id, document_id, canonical(result)),
            )
            saved = connection.execute("SELECT payload FROM runs WHERE id=?", (run_id,)).fetchone()
        return json.loads(saved[0])
