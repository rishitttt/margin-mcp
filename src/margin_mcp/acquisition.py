"""Bounded acquisition of explicitly curated public PDFs, outside the MCP query path."""

import hashlib
import json
import subprocess
import tempfile
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import HttpUrl, model_validator

from margin_mcp.ingestion import MAX_PDF_BYTES, open_pdf
from margin_mcp.ingestion_models import Digest, DocumentManifest
from margin_mcp.models import Identifier, Record, Text
from margin_mcp.storage import MarginError


class AcquisitionSource(Record):
    """A curated, hash-pinned document; metadata is reviewed before adding a source."""

    company_id: Identifier
    issuer_name: Text
    filing_id: Identifier
    title: Text
    source_url: HttpUrl
    discovery_url: HttpUrl
    published_on: date
    expected_sha256: Digest

    @model_validator(mode="after")
    def https_only(self):
        for url in (self.source_url, self.discovery_url):
            if url.scheme != "https" or url.username or url.password:
                raise ValueError("Sources require HTTPS without URL credentials")
        return self


def acquire_pdf(source: AcquisitionSource, output: Path) -> dict:
    # A fresh directory preserves older acquisitions, including changed bytes at the same URL.
    if output.exists():
        raise MarginError("OUTPUT_EXISTS: choose a new acquisition directory")
    with tempfile.TemporaryDirectory(prefix="margin-acquire-") as temporary:
        response = Path(temporary) / "response"
        try:
            result = subprocess.run(
                [
                    "curl",
                    "--disable",
                    "--silent",
                    "--show-error",
                    "--proto",
                    "=https",
                    "--connect-timeout",
                    "10",
                    "--max-time",
                    "30",
                    "--max-filesize",
                    str(MAX_PDF_BYTES),
                    "--output",
                    str(response),
                    "--write-out",
                    "%{json}",
                    str(source.source_url),
                ],
                capture_output=True,
                text=True,
                timeout=35,
            )
        except FileNotFoundError as exc:
            raise MarginError("CURL_NOT_FOUND: install system curl to run this probe") from exc
        except subprocess.TimeoutExpired as exc:
            raise MarginError("DOWNLOAD_TIMEOUT: curl exceeded its process deadline") from exc
        if result.returncode:
            raise MarginError(
                f"DOWNLOAD_FAILED: curl exit {result.returncode}: {result.stderr.strip()}"
            )
        try:
            receipt = json.loads(result.stdout)
            status = receipt["http_code"]
            required = ("ssl_verify_result", "content_type", "http_version", "time_total")
            if any(key not in receipt for key in required):
                raise ValueError("missing curl fields")
        except (ValueError, KeyError, TypeError) as exc:
            raise MarginError("INVALID_RECEIPT: curl did not return transfer metadata") from exc
        if status != 200:
            raise MarginError(
                f"HTTP_{status}: no PDF saved; inspect the source/access route before retrying"
            )
        if receipt["ssl_verify_result"] != 0:
            raise MarginError("TLS_FAILED: certificate verification failed")
        with response.open("rb") as stream:
            raw = stream.read(MAX_PDF_BYTES + 1)
        with open_pdf(raw) as pdf:
            pages = len(pdf.pages)
        sha256 = hashlib.sha256(raw).hexdigest()
        if sha256 != source.expected_sha256:
            raise MarginError(
                "SOURCE_CHANGED: PDF hash differs from the reviewed source; "
                "inspect the new document before updating its catalog entry"
            )
        acquired_at = datetime.now(UTC).isoformat()
        metadata = {
            "source_url": str(source.source_url),
            "discovery_url": str(source.discovery_url),
            "acquired_at": acquired_at,
            "http_status": status,
            "content_type": receipt["content_type"],
            "bytes": len(raw),
            "pages": pages,
            "sha256": sha256,
            "expected_sha256_matched": True,
            "tls_verified": True,
            "http_version": receipt["http_version"],
            "elapsed_seconds": receipt["time_total"],
            "client": "system curl",
            "scope": "Private local research; hosting/redistribution rights not established",
        }
        manifest = {
            "schema_version": 1,
            "company_id": source.company_id,
            "issuer_name": source.issuer_name,
            "filing_id": source.filing_id,
            "title": source.title,
            "data_kind": "real",
            "source_url": str(source.source_url),
            "published_on": source.published_on.isoformat(),
            "acquired_at": acquired_at,
            "processing_scope": "local_only",
            "usage_basis": (
                "User-directed private research experiment on an official public filing; "
                "commercial/shared reuse not established"
            ),
        }
        DocumentManifest.model_validate(manifest)
        output.mkdir(parents=True, exist_ok=False)
        (output / "results.pdf").write_bytes(raw)
        (output / "acquisition.json").write_text(json.dumps(metadata, indent=2) + "\n")
        (output / "document.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return metadata
