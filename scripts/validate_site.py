#!/usr/bin/env python3
"""Validate local Pages links and document accessibility basics."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.issues = set(), [], []
        self.has_main = False
        self.language = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.issues.append("duplicate ID: " + attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "main":
            self.has_main = True
        if tag == "img" and not attrs.get("alt"):
            self.issues.append("image missing alt text")


def main():
    documents, errors, checked = {}, [], 0
    for path in SITE.glob("*.html"):
        doc = Document()
        text = path.read_text()
        doc.feed(text)
        if doc.language != "zh-CN" or not doc.has_main:
            doc.issues.append("missing Chinese language or main landmark")
        if "/Users/aias/" in text or "```mermaid" in text:
            doc.issues.append("local path or unrendered diagram")
        documents[path] = doc
        errors.extend(path.name + ": " + e for e in doc.issues)
    for path, doc in documents.items():
        for ref in doc.links:
            u = urlsplit(ref)
            if u.scheme or u.netloc:
                continue
            target = path.parent / unquote(u.path) if u.path else path
            if not target.exists():
                errors.append(path.name + ": missing target " + ref)
            elif u.fragment and target in documents and unquote(u.fragment) not in documents[target].ids:
                errors.append(path.name + ": missing anchor " + ref)
            checked += 1
    report = {"pages": len(documents), "local_links_checked": checked, "errors": errors}
    (ROOT / "reports/site-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
