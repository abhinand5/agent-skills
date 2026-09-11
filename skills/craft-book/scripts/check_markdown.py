#!/usr/bin/env python3
"""Check the generated Markdown edition.

    check_markdown.py BOOK.md

Fails on raw LaTeX that leaked through (page breaks, environments, fenced-div
syntax), unresolved citations, unbalanced inline math delimiters, local links or
images that point at missing files, and a missing top-level structure.
"""

from __future__ import annotations

import os
import re
import sys

LEAKS = (r"\begin{", r"\end{", r"\appendix", r"\newpage", r"\clearpage", ":::", "[**???**]", "@{}")
LOCAL_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


def fail(message: str) -> None:
    raise SystemExit(f"Markdown check failed: {message}")


def main(path: str) -> None:
    text = open(path, encoding="utf-8").read()
    base = os.path.dirname(os.path.abspath(path))
    lines = text.splitlines()

    in_fence = False
    for number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for leak in LEAKS:
            if leak in line:
                fail(f"line {number}: leaked markup {leak!r}: {line.strip()[:100]}")
        dollars = len(re.findall(r"(?<!\\)\$", line.replace("$$", "")))
        if dollars % 2:
            fail(f"line {number}: unbalanced inline math delimiters: {line.strip()[:100]}")

    for match in LOCAL_LINK.finditer(text):
        target = match.group(1)
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        if not os.path.exists(os.path.join(base, target.split("#")[0])):
            fail(f"local link target missing: {target}")

    headings = [l for l in lines if l.startswith("# ")]
    if len(headings) < 2:
        fail("fewer than two top-level headings; is the structure filter running?")
    if not re.search(r"^#+ Chapter 1[. ]", text, re.MULTILINE):
        fail("chapter numbering missing (expected a heading starting 'Chapter 1')")

    words = len(re.findall(r"\b\w+\b", text))
    print(f"Markdown check: OK | {len(headings)} top-level headings | {words} words")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_markdown.py BOOK.md")
    main(sys.argv[1])
