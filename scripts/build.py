#!/usr/bin/env python3
"""Build the editable manuscript into EPUB 3 and a browser preview."""

from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Agent记忆：从概念到可落地的工程设计"


def main():
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("Pandoc is required. Install it, then run python3 scripts/build.py.")
    chapters = sorted((ROOT / "manuscript").glob("*.md"))
    if len(chapters) != 7:
        raise SystemExit("Expected preface, five chapters, and the source appendix.")
    for asset in ["cover.png", "memory-lifecycle.png", "memory-architecture.png"]:
        if not (ROOT / "assets" / asset).is_file():
            raise SystemExit("Missing asset: " + asset)
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    (ROOT / "dist").mkdir(exist_ok=True)
    manuscript = build / "book.md"
    manuscript.write_text("\n\n".join(p.read_text().strip() for p in chapters) + "\n")
    common = [
        pandoc, str(manuscript), "--from=markdown", "--standalone",
        "--metadata-file=metadata.yaml", "--toc", "--toc-depth=2",
        "--resource-path=.", "--css=styles/book.css", "--wrap=none",
        "--no-highlight", "--fail-if-warnings",
    ]
    epub = ROOT / "dist" / (TITLE + ".epub")
    subprocess.run(common + [
        "--to=epub3", "--epub-chapter-level=1", "--epub-cover-image=assets/cover.png",
        "--output=" + str(epub),
    ], cwd=ROOT, check=True)
    subprocess.run(common + [
        "--to=html5", "--self-contained", "--output=dist/reading-preview.html",
    ], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/validate_epub.py", str(epub)], cwd=ROOT, check=True)
    checksum = hashlib.sha256(epub.read_bytes()).hexdigest()
    (ROOT / "reports/epub-sha256.txt").write_text(checksum + "  " + epub.name + "\n")
    subprocess.run([sys.executable, "scripts/build_site.py"], cwd=ROOT, check=True)
    print("EPUB:", epub)


if __name__ == "__main__":
    main()
