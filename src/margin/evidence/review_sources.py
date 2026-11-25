"""Reviewed provider-text projections, never original-document extraction or fetching."""

from datetime import date

from margin.evidence.results import data_payload

LIST_OPERATIONS = {
    "drishti.get_news",
    "drishti.get_announcements",
    "drishti.list_earnings",
}
DETAIL_OPERATION = "drishti.get_earnings_filing"


def project_sources(result, issuer):
    operation = result["operation"]
    if operation not in LIST_OPERATIONS | {DETAIL_OPERATION}:
        return [], [], [{"reason": "unsupported_operation"}]
    native = data_payload(result["payload"], result["payload_kind"])
    data = native.get("data") if isinstance(native, dict) else None
    if operation == DETAIL_OPERATION and isinstance(data, dict):
        rows = [("data", data)]
    elif operation in LIST_OPERATIONS and isinstance(data, list):
        rows = [(f"data[{index}]", row) for index, row in enumerate(data[:12])]
    else:
        return [], [], [{"reason": "unsupported_shape"}]
    sources, provenance, skipped = [], [], []
    target = issuer.split(":")[-1]
    for path, row in rows:
        if not isinstance(row, dict):
            skipped.append({"path": path, "reason": "unsupported_row"})
            continue
        reported = row.get("symbol")
        symbols = reported.split(":") if isinstance(reported, str) else []
        if len(symbols) > 20 or any(not 1 <= len(symbol) <= 80 for symbol in symbols):
            skipped.append({"path": path, "reason": "unsupported_row_identity"})
            continue
        if (symbols and target not in symbols) or (operation == DETAIL_OPERATION and not symbols):
            skipped.append({"path": path, "reason": "row_identity_unresolved_or_mismatched"})
            continue
        url_fields = (
            ("link", "url", "source_url")
            if operation == "drishti.get_news"
            else ("attachment_url", "citation_url")
        )
        url_field = next(
            (key for key in url_fields if isinstance(row.get(key), str) and row[key].strip()),
            None,
        )
        citations = row.get("citation_urls")
        citation_pdf = citations.get("pdf") if isinstance(citations, dict) else None
        if (
            not url_field
            and operation != "drishti.get_news"
            and isinstance(citation_pdf, str)
            and citation_pdf.strip()
        ):
            url_field = "citation_urls.pdf"
        if not url_field:
            skipped.append({"path": path, "reason": "missing_supported_locator"})
            continue
        url = citation_pdf if url_field == "citation_urls.pdf" else row[url_field]
        requires_resolution = any(
            citation.get("locator") == url and citation.get("requires_resolution") is True
            for citation in result.get("citations", [])
            if isinstance(citation, dict)
        )
        title = next(
            (
                row[key]
                for key in ("title", "headline", "specific_title")
                if isinstance(row.get(key), str) and row[key].strip()
            ),
            f"{target} earnings {row.get('quarter', 'record')}"
            if operation != "drishti.get_news"
            else "Provider news record",
        )
        passages = [
            {"passage_id": key, "text": row[key][:6000], "locator": f"{path}.{key}"}
            for key in ("summary", "long_summary")
            if isinstance(row.get(key), str) and row[key].strip()
        ]
        value = row.get("published_at") or row.get("date")
        record_date = value[:10] if isinstance(value, str) else None
        try:
            if record_date:
                date.fromisoformat(record_date)
        except ValueError:
            record_date = None
        sources.append(
            {
                "issuer": issuer,
                "title": title[:400],
                "url": url,
                "kind": "provider_summary" if passages else "source_locator",
                "date": record_date,
                "date_kind": "published" if row.get("published_at") and record_date else "unknown",
                "passages": passages,
            }
        )
        provenance.append(
            {
                "row_path": path,
                "url_path": f"{path}.{url_field}",
                "reported_symbols": symbols,
                "issuer_attribution": "declared_target_not_semantic_relevance",
                "text_scope": "provider_summary_not_attachment_contents",
                "source_locator_requires_resolution": requires_resolution,
            }
        )
    return sources, provenance, skipped
