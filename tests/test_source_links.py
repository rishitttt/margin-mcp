import pytest

from margin_mcp.source_links import document_links


def test_links_preserve_provenance_and_deduplicate_fragments_without_fetching():
    links = document_links(
        """
    <a href="/results.pdf#page=2">Results <span>2025</span></a>
    <a href="/results.pdf#page=3">Notes</a>
    <a href="https://exchange.example/viewer?file=report.pdf">Transcript</a>
    <a href="javascript:evil.pdf">Bad</a><a href="http://old.example/a.pdf">Old</a>
    <a href="https://secret:password@example.com/a.pdf">Credentials</a>
    <script>fetch('https://example.com/hidden.pdf')</script>
    """,
        "https://issuer.example/investors/",
    )
    assert len(links) == 2
    assert links[0]["source_url"] == "https://issuer.example/results.pdf"
    assert links[0]["labels"] == ["Results 2025", "Notes"]
    assert len(links[0]["observed_links"]) == 2
    assert links[1]["status"] == "discovered_not_downloaded"
    assert not links[1]["identity_verified"]


def test_discovery_bounds_and_empty_result_are_not_coverage_claims():
    assert document_links("<p>No static links</p>", "https://issuer.example/") == []
    with pytest.raises(ValueError):
        document_links("a" * (2 * 1024 * 1024 + 1), "https://issuer.example/")
    with pytest.raises(ValueError):
        document_links("", "file:///tmp/local.html")
