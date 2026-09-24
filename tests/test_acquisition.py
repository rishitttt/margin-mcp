import hashlib
import io
import json
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError
from reportlab.pdfgen import canvas

from margin_mcp import acquisition as probe
from margin_mcp.ingestion_models import DocumentManifest
from margin_mcp.storage import MarginError


@pytest.fixture
def pdf_bytes():
    stream = io.BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.drawString(40, 40, "SYNTHETIC")
    pdf.save()
    return stream.getvalue()


@pytest.fixture
def source(pdf_bytes):
    return probe.AcquisitionSource(
        company_id="test-issuer",
        issuer_name="Synthetic Test Issuer",
        filing_id="test-filing",
        title="Synthetic acquisition test document",
        source_url="https://example.com/filing.pdf",
        discovery_url="https://example.com/filings",
        published_on="2025-10-16",
        expected_sha256=hashlib.sha256(pdf_bytes).hexdigest(),
    )


def fake_curl(monkeypatch, pdf_bytes, *, status=200, tls=0, html=False):
    def run(args, **kwargs):
        assert args[:2] == ["curl", "--disable"]
        assert "--insecure" not in args and "-k" not in args
        assert "--location" not in args and "-L" not in args
        assert args[args.index("--max-time") + 1] == "30"
        assert kwargs["timeout"] == 35
        path = Path(args[args.index("--output") + 1])
        path.write_bytes(b"<html>Access denied</html>" if html else pdf_bytes)
        receipt = {
            "http_code": status,
            "ssl_verify_result": tls,
            "content_type": "application/octet-stream",
            "http_version": "2",
            "time_total": 1.0,
        }
        return subprocess.CompletedProcess(args, 0, json.dumps(receipt), "")

    monkeypatch.setattr(probe.subprocess, "run", run)


def test_acquisition_validates_pdf_and_preserves_provenance(
    source, pdf_bytes, monkeypatch, tmp_path
):
    fake_curl(monkeypatch, pdf_bytes)
    out = tmp_path / "acquisition"
    result = probe.acquire_pdf(source, out)
    assert result["pages"] == 1 and result["tls_verified"]
    assert result["expected_sha256_matched"]
    assert result == json.loads((out / "acquisition.json").read_text())
    manifest = DocumentManifest.model_validate_json((out / "document.json").read_text())
    assert manifest.source_url == source.source_url
    assert manifest.company_id == source.company_id
    before = (out / "results.pdf").read_bytes()
    with pytest.raises(MarginError, match="OUTPUT_EXISTS"):
        probe.acquire_pdf(source, out)
    assert (out / "results.pdf").read_bytes() == before


@pytest.mark.parametrize("status", [403, 302, 404, 429])
def test_http_errors_do_not_publish_files(source, pdf_bytes, monkeypatch, tmp_path, status):
    fake_curl(monkeypatch, pdf_bytes, status=status)
    out = tmp_path / "acquisition"
    with pytest.raises(MarginError, match=f"HTTP_{status}"):
        probe.acquire_pdf(source, out)
    assert not out.exists()


def test_html_and_tls_failures_do_not_publish_files(source, pdf_bytes, monkeypatch, tmp_path):
    for options, error in [({"html": True}, "INVALID_PDF"), ({"tls": 1}, "TLS_FAILED")]:
        fake_curl(monkeypatch, pdf_bytes, **options)
        with pytest.raises(MarginError, match=error):
            probe.acquire_pdf(source, tmp_path / "acquisition")
        assert not (tmp_path / "acquisition").exists()


def test_timeout_is_actionable(source, monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("curl", 35)

    monkeypatch.setattr(probe.subprocess, "run", timeout)
    with pytest.raises(MarginError, match="DOWNLOAD_TIMEOUT"):
        probe.acquire_pdf(source, tmp_path / "acquisition")


def test_changed_pdf_requires_review(source, pdf_bytes, monkeypatch, tmp_path):
    fake_curl(monkeypatch, pdf_bytes)
    changed = source.model_copy(update={"expected_sha256": "0" * 64})
    with pytest.raises(MarginError, match="SOURCE_CHANGED"):
        probe.acquire_pdf(changed, tmp_path / "acquisition")
    assert not (tmp_path / "acquisition").exists()


@pytest.mark.parametrize(
    "returncode,stdout,error", [(92, "", "DOWNLOAD_FAILED"), (0, "{}", "INVALID_RECEIPT")]
)
def test_failed_transfer_or_receipt(source, monkeypatch, tmp_path, returncode, stdout, error):
    monkeypatch.setattr(
        probe.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, returncode, stdout, "transfer failed"),
    )
    with pytest.raises(MarginError, match=error):
        probe.acquire_pdf(source, tmp_path / "acquisition")
    assert not (tmp_path / "acquisition").exists()


def test_catalog_is_valid_and_has_distinct_documents():
    catalog = json.loads(
        (Path(__file__).parents[1] / "examples/public-document-sources.json").read_text()
    )
    for key, value in catalog.items():
        assert probe.AcquisitionSource.model_validate(value).filing_id == key
    assert len({value["expected_sha256"] for value in catalog.values()}) == len(catalog)
    assert "/AttachHis/" in catalog["hcltech-q2-fy26-results"]["source_url"]


@pytest.mark.parametrize(
    "url", ["http://example.com/file.pdf", "https://user:password@example.com/file.pdf"]
)
def test_sources_require_verified_https_without_credentials(source, url):
    with pytest.raises(ValidationError):
        probe.AcquisitionSource.model_validate({**source.model_dump(), "source_url": url})
