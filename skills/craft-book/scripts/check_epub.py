#!/usr/bin/env python3
"""Dependency-free structural, link, table, and math checker for a generated EPUB.

    check_epub.py BOOK.epub [--expect-tables N] [--min-math N] [--min-images N]
                            [--require-text "needle" ...] [--allow-bare WORD ...]

Fails (exit 1) on anything Kindle or a strict reader would choke on, plus the
classes of silent conversion damage seen in practice: tables flattened to prose,
LaTeX control words typeset as text because a backslash went missing, chapter
files titled after their filename, and broken internal links.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

CONTAINER = "META-INF/container.xml"
MIMETYPE = "application/epub+zip"
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "urn"}
KINDLE_XHTML_LIMIT = 30 * 1024 * 1024

# Control words that only make sense with a backslash. A bare token in an
# equation's TeX source means the LaTeX dropped one and it is now italic prose.
BARE_CONTROL_WORD = re.compile(
    r"(?<![\\A-Za-z])(?:qquad|quad|phi|Phi|gamma|alpha|delta|theta|lambda|sigma|"
    r"mu|pi|sum|prod|max|min|log|exp|top|cdot|mid|leq|geq|infty|sqrt|frac|"
    r"mathbb|mathcal|operatorname|nabla|partial|hat|widehat|bar|tilde)(?![A-Za-z])"
)
TEX_ANNOTATION = re.compile(r'<annotation encoding="application/x-tex">(.*?)</annotation>', re.DOTALL)
# Text-mode arguments legitimately contain words such as "arg\,max".
TEXT_ARGUMENT = re.compile(r"\\(?:mathrm|mathit|text|textrm|textbf|operatorname\*?|mathop)\{[^{}]*\}")
LEAKED_TABLE = re.compile(r"@\{\}|@l[lcrXYp]+@|\\(?:toprule|midrule|bottomrule|hline)")
LEAKED_LATEX = (r"\cite{", r"\begin{tikzpicture}", r"\begin{tabular", r"\ref{", r"\label{", r"\newpage")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def fail(message: str) -> None:
    raise SystemExit(f"EPUB check failed: {message}")


def resolve_link(source: str, link: str) -> tuple[str, str]:
    parsed = urlsplit(link)
    if parsed.scheme in EXTERNAL_SCHEMES:
        return "", ""
    if parsed.scheme:
        fail(f"unsupported link scheme in {source}: {link}")
    path = unquote(parsed.path)
    target = source if not path else posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
    return target, unquote(parsed.fragment)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epub")
    parser.add_argument("--expect-tables", type=int, default=None, help="exact number of <table> elements expected")
    parser.add_argument("--min-math", type=int, default=0)
    parser.add_argument("--min-images", type=int, default=0)
    parser.add_argument("--require-text", action="append", default=[], help="string that must appear somewhere in the book")
    parser.add_argument("--allow-bare", action="append", default=[], help="control word to exempt from the bare-word scan")
    args = parser.parse_args()

    bare_pattern = BARE_CONTROL_WORD
    if args.allow_bare:
        allowed = "|".join(re.escape(w) for w in args.allow_bare)
        bare_pattern = re.compile(r"(?!(?:" + allowed + r")(?![A-Za-z]))" + BARE_CONTROL_WORD.pattern)

    with zipfile.ZipFile(args.epub) as archive:
        infos = archive.infolist()
        if not infos or infos[0].filename != "mimetype":
            fail("mimetype must be the first ZIP entry")
        if infos[0].compress_type != zipfile.ZIP_STORED:
            fail("mimetype must be stored without compression")
        if archive.read("mimetype").decode("ascii") != MIMETYPE:
            fail("incorrect mimetype content")

        names = set(archive.namelist())
        if CONTAINER not in names:
            fail(f"missing {CONTAINER}")

        roots: dict[str, ET.Element] = {}
        for name in names:
            if PurePosixPath(name).suffix.lower() in {".xml", ".opf", ".ncx", ".xhtml", ".svg"}:
                try:
                    roots[name] = ET.fromstring(archive.read(name))
                except ET.ParseError as error:
                    fail(f"invalid XML in {name}: {error}")

        rootfiles = [e for e in roots[CONTAINER].iter() if local_name(e.tag) == "rootfile"]
        if len(rootfiles) != 1:
            fail("container.xml must identify exactly one package document")
        package_path = rootfiles[0].attrib.get("full-path", "")
        if package_path not in names:
            fail(f"package document does not exist: {package_path}")
        package = roots[package_path]
        package_dir = posixpath.dirname(package_path)

        manifest = {i.attrib.get("id", ""): i for i in package.iter() if local_name(i.tag) == "item"}
        if not manifest:
            fail("empty EPUB manifest")
        if sum("nav" in i.attrib.get("properties", "").split() for i in manifest.values()) != 1:
            fail("manifest must contain exactly one navigation document")
        if sum("cover-image" in i.attrib.get("properties", "").split() for i in manifest.values()) != 1:
            fail("manifest must contain exactly one cover image")
        for item in manifest.values():
            target = posixpath.normpath(posixpath.join(package_dir, unquote(item.attrib.get("href", ""))))
            if target not in names:
                fail(f"manifest target is missing: {target}")
        spine = [i.attrib.get("idref", "") for i in package.iter() if local_name(i.tag) == "itemref"]
        if not spine or any(s not in manifest for s in spine):
            fail("spine contains missing or invalid manifest references")

        xhtml = sorted(n for n in names if n.endswith(".xhtml"))
        if not xhtml or len(xhtml) >= 300:
            fail(f"unexpected XHTML file count: {len(xhtml)}")

        ids_by_file: dict[str, set[str]] = {}
        math_count = image_count = table_count = 0
        document_text = ""
        for name in xhtml:
            if archive.getinfo(name).file_size >= KINDLE_XHTML_LIMIT:
                fail(f"XHTML file exceeds Kindle's 30 MB limit: {name}")
            root = roots[name]
            ids_by_file[name] = {e.attrib["id"] for e in root.iter() if "id" in e.attrib}
            titles = [e.text or "" for e in root.iter() if local_name(e.tag) == "title"]
            if not titles or titles[0].strip().endswith(".xhtml") or not titles[0].strip():
                fail(f"chapter document has no readable title: {name}")
            for e in root.iter():
                tag = local_name(e.tag)
                if tag == "math":
                    math_count += 1
                elif tag == "img":
                    image_count += 1
                    if not e.attrib.get("alt"):
                        fail(f"image without alt text in {name}")
                elif tag == "table":
                    table_count += 1
                    widths = {
                        len([c for c in row if local_name(c.tag) in {"td", "th"}])
                        for row in e.iter() if local_name(row.tag) == "tr"
                    }
                    if len(widths) != 1 or widths == {0}:
                        fail(f"ragged table in {name}: row widths {sorted(widths)}")
            prose = " ".join(
                (e.text or "") + (e.tail or "")
                for e in root.iter() if local_name(e.tag) in {"p", "span", "li"}
            )
            if LEAKED_TABLE.search(prose):
                fail(f"LaTeX table markup leaked into prose in {name}")
            document_text += archive.read(name).decode("utf-8")

        for name in xhtml:
            for e in roots[name].iter():
                for attribute in ("href", "src"):
                    link = e.attrib.get(attribute)
                    if not link:
                        continue
                    target, fragment = resolve_link(name, link)
                    if not target:
                        continue
                    if target not in names:
                        fail(f"broken local link in {name}: {link}")
                    if fragment and target.endswith(".xhtml") and fragment not in ids_by_file.get(target, set()):
                        fail(f"broken fragment in {name}: {link}")

        for marker in LEAKED_LATEX:
            if marker in document_text:
                fail(f"raw LaTeX leaked into XHTML: {marker}")
        for annotation in TEX_ANNOTATION.findall(document_text):
            bare = bare_pattern.search(TEXT_ARGUMENT.sub("", annotation))
            if bare:
                fail(f"bare control word '{bare.group(0)}' in equation source (missing backslash?): "
                     f"{' '.join(annotation.split())[:80]}")
        for needle in args.require_text:
            if needle not in document_text:
                fail(f"required text not found: {needle!r}")
        if args.expect_tables is not None and table_count != args.expect_tables:
            fail(f"expected {args.expect_tables} tables, found {table_count}")
        if math_count < args.min_math:
            fail(f"expected at least {args.min_math} MathML expressions, found {math_count}")
        if image_count < args.min_images:
            fail(f"expected at least {args.min_images} images, found {image_count}")

    print(f"EPUB check: OK | {len(xhtml)} XHTML files | {math_count} MathML | {table_count} tables | "
          f"{image_count} images | {len(spine)} spine items")


if __name__ == "__main__":
    main()
