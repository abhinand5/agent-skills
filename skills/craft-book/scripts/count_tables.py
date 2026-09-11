#!/usr/bin/env python3
"""Count the tables in Markdown sources (pipe, grid, and simple tables) or in
LaTeX sources (tabular/tabularx environments), so check_epub.py can demand the
same number in the EPUB. Prints one integer.

    count_tables.py src/*.md      |      count_tables.py chapters/*.tex
"""

from __future__ import annotations

import re
import sys

PIPE_HEADER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
GRID_TOP = re.compile(r"^\s*\+(-+\+)+\s*$")
LATEX_TABLE = re.compile(r"\\begin\{(?:tabular|tabularx|longtable|tabulary)\}")


def count_markdown(text: str) -> int:
    count = 0
    lines = text.splitlines()
    in_fence = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith("```") or line.lstrip().startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if PIPE_HEADER.match(line) and index > 0 and "|" in lines[index - 1]:
            count += 1
        elif GRID_TOP.match(line) and (index == 0 or not GRID_TOP.match(lines[index - 1])
                                       and not lines[index - 1].lstrip().startswith("|")):
            count += 1
    return count


def main() -> None:
    total = 0
    for path in sys.argv[1:]:
        text = open(path, encoding="utf-8").read()
        if path.endswith(".tex"):
            total += len(LATEX_TABLE.findall(text))
        else:
            total += count_markdown(text)
    print(total)


if __name__ == "__main__":
    main()
