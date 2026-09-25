"""Offline discovery leads from saved HTML. Never fetch or trust linked documents."""

from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlsplit


def document_links(html: str, discovery_url: str) -> list[dict]:
    """Extract observed HTTPS PDF/viewer links, preserving labels and provenance.

    Only anchor hrefs are inspected: JS, redirects and data attributes are not resolved.
    Link text/filenames do not establish issuer, period, type or successful acquisition.
    """
    base = urlsplit(discovery_url)
    if base.scheme != "https" or not base.hostname or base.username or base.password:
        raise ValueError("Discovery URL must be HTTPS without credentials")
    if len(html.encode("utf-8")) > 2 * 1024 * 1024:
        raise ValueError("Saved HTML exceeds 2 MiB")

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.href = None
            self.label = []
            self.items = {}

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.href = dict(attrs).get("href")
                self.label = []

        def handle_data(self, text):
            if self.href:
                self.label.append(text)

        def handle_endtag(self, tag):
            if tag != "a" or not self.href:
                return
            observed = urljoin(discovery_url, self.href)
            self.href = None
            try:
                parts = urlsplit(observed)
                if (
                    parts.scheme != "https"
                    or not parts.hostname
                    or parts.username
                    or parts.password
                    or ".pdf" not in (parts.path + parts.query).lower()
                ):
                    return
            except ValueError:
                return
            url = urldefrag(observed)[0]
            item = self.items.setdefault(
                url,
                {
                    "source_url": url,
                    "discovery_url": discovery_url,
                    "observed_links": [],
                    "labels": [],
                    "status": "discovered_not_downloaded",
                    "identity_verified": False,
                },
            )
            label = " ".join(" ".join(self.label).split())
            if observed not in item["observed_links"]:
                item["observed_links"].append(observed)
            if label and label not in item["labels"]:
                item["labels"].append(label)

    parser = Links()
    parser.feed(html)
    return list(parser.items.values())
