#!/usr/bin/env python3
"""Check a LuaLaTeX-built PDF and its log.

    check_pdf.py BOOK.pdf BOOK.log [--max-overfull-pt 5] [--max-pages N] [--min-pages N]

Fails on undefined references or citations, missing glyphs, overfull boxes wider
than the tolerance, and page counts outside the requested range. Prints pdfinfo.
"""

from __future__ import annotations

import argparse
import re
import subprocess

OVERFULL = re.compile(r"Overfull \\[hv]box \(([\d.]+)pt too wide")


def fail(message: str) -> None:
    raise SystemExit(f"PDF check failed: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("log")
    parser.add_argument("--max-overfull-pt", type=float, default=5.0)
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--min-pages", type=int, default=1)
    args = parser.parse_args()

    log = open(args.log, encoding="utf-8", errors="replace").read()
    problems: list[str] = []
    for needle, label in (
        ("There were undefined references", "undefined references"),
        ("There were undefined citations", "undefined citations"),
        ("LaTeX Warning: Reference `", "undefined reference"),
        ("LaTeX Warning: Citation `", "undefined citation"),
        ("Missing character:", "missing glyph in the chosen fonts"),
        ("! ", "TeX error"),
    ):
        if needle in log:
            line = next(l for l in log.splitlines() if needle in l)
            problems.append(f"{label}: {line.strip()[:120]}")
    for match in OVERFULL.finditer(log):
        width = float(match.group(1))
        if width > args.max_overfull_pt:
            context = log[match.start(): match.start() + 160].splitlines()[0]
            problems.append(f"overfull box {width}pt: {context}")
    if problems:
        fail("\n  " + "\n  ".join(problems[:20]))

    info = subprocess.run(["pdfinfo", args.pdf], capture_output=True, text=True, check=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    if pages < args.min_pages:
        fail(f"only {pages} pages")
    if args.max_pages is not None and pages > args.max_pages:
        fail(f"{pages} pages exceeds the agreed budget of {args.max_pages}")
    print("\n".join(l for l in info.splitlines() if l.split(":")[0] in {"Title", "Author", "Pages", "Page size"}))
    print(f"PDF check: OK | {pages} pages | overfull tolerance {args.max_overfull_pt}pt")


if __name__ == "__main__":
    main()
