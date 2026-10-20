#!/usr/bin/env python3
"""Check ZIP rules, package resources, navigation, and internal EPUB links."""

from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZIP_STORED
import argparse
import json
import posixpath
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"opf": "http://www.idpf.org/2007/opf", "x": "http://www.w3.org/1999/xhtml",
      "dc": "http://purl.org/dc/elements/1.1/"}


def validate(path):
    issues = []
    with ZipFile(path) as z:
        names = set(z.namelist())
        first = z.infolist()[0]
        if first.filename != "mimetype" or first.compress_type != ZIP_STORED:
            issues.append("mimetype must be first and uncompressed")
        if z.read("mimetype") != b"application/epub+zip":
            issues.append("invalid mimetype content")
        if z.testzip():
            issues.append("ZIP CRC failure")
        container = ET.fromstring(z.read("META-INF/container.xml"))
        package_path = next(e.attrib["full-path"] for e in container.iter()
                            if e.tag.endswith("rootfile"))
        package = ET.fromstring(z.read(package_path))
        base = posixpath.dirname(package_path)
        manifest = package.findall("opf:manifest/opf:item", NS)
        by_id = {e.attrib["id"]: e for e in manifest}
        for item in manifest:
            resource = posixpath.normpath(posixpath.join(base, unquote(item.attrib["href"])))
            if resource not in names:
                issues.append("missing manifest resource: " + resource)
        spine = package.findall("opf:spine/opf:itemref", NS)
        for entry in spine:
            if entry.attrib["idref"] not in by_id:
                issues.append("unresolved spine item")
        documents = {}
        for name in sorted(names):
            if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                try:
                    documents[name] = ET.fromstring(z.read(name))
                except ET.ParseError as err:
                    issues.append(name + ": " + str(err))
        ids = {name: {e.attrib["id"] for e in tree.iter() if "id" in e.attrib}
               for name, tree in documents.items()}
        internal_links = 0
        for name, tree in documents.items():
            for node in tree.iter():
                for attr in ("href", "src"):
                    ref = node.attrib.get(attr)
                    if not ref:
                        continue
                    u = urlsplit(ref)
                    if u.scheme or u.netloc:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name),
                                                             unquote(u.path))) if u.path else name
                    if target not in names:
                        issues.append(name + ": missing link " + ref)
                    elif u.fragment and target in ids and unquote(u.fragment) not in ids[target]:
                        issues.append(name + ": missing anchor " + ref)
                    internal_links += 1
        nav = next((i for i in manifest if "nav" in i.attrib.get("properties", "").split()), None)
        if nav is None:
            issues.append("missing EPUB 3 navigation document")
        if not any("cover-image" in i.attrib.get("properties", "").split() for i in manifest):
            issues.append("missing cover-image property")
        language = package.find("opf:metadata/dc:language", NS)
        if language is None or language.text != "zh-CN":
            issues.append("book language should be zh-CN")
        for name, tree in documents.items():
            if not name.endswith(".xhtml"):
                continue
            text = "".join(tree.itertext())
            if "```mermaid" in text or "/Users/aias/" in text or "/tmp/agent-memory" in text:
                issues.append(name + ": unconverted diagram or local path")
            for img in tree.findall(".//x:img", NS):
                if not img.attrib.get("alt"):
                    issues.append(name + ": image lacks alt text")
        report = {"file": path.name, "bytes": path.stat().st_size,
                  "package_version": package.attrib.get("version"),
                  "manifest_items": len(manifest), "spine_items": len(spine),
                  "xml_documents": len(documents), "internal_links_checked": internal_links,
                  "errors": issues}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/package-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", type=Path)
    validate(parser.parse_args().epub)
