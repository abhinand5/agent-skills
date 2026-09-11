#!/usr/bin/env python3
"""Post-process the pandoc EPUB in place: give every chapter file a real <title>.

Pandoc names each chapter document after its file (``ch003.xhtml``); several
e-readers surface that string in their chapter switcher, so replace it with the
chapter's first heading. The archive is rewritten with ``mimetype`` first and
uncompressed, as EPUB requires.
"""

from __future__ import annotations

import html
import os
import re
import shutil
import sys
import tempfile
import zipfile

HEADING = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.DOTALL)
TITLE = re.compile(r"<title>.*?</title>", re.DOTALL)
TAGS = re.compile(r"<[^>]+>")


def heading_text(document: str) -> str | None:
    match = HEADING.search(document)
    if not match:
        return None
    text = html.unescape(TAGS.sub("", match.group(1)))
    return " ".join(text.split())


def polish(document: str) -> str:
    title = heading_text(document)
    if not title:
        return document
    return TITLE.sub(f"<title>{html.escape(title)}</title>", document, count=1)


def main(epub_path: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as handle:
        temp_path = handle.name
    with zipfile.ZipFile(epub_path) as source, zipfile.ZipFile(temp_path, "w") as target:
        infos = source.infolist()
        if not infos or infos[0].filename != "mimetype":
            raise SystemExit("polish_epub: mimetype must be the first entry")
        for info in infos:
            data = source.read(info.filename)
            if info.filename.startswith("EPUB/text/ch") and info.filename.endswith(".xhtml"):
                data = polish(data.decode("utf-8")).encode("utf-8")
            compression = zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED
            target.writestr(info, data, compress_type=compression)
    shutil.move(temp_path, epub_path)
    os.chmod(epub_path, 0o644)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: polish_epub.py BOOK.epub")
    main(sys.argv[1])
