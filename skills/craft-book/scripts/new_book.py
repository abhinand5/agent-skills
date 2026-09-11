#!/usr/bin/env python3
"""Scaffold a book workspace from one of the skill's templates.

    new_book.py --pipeline markdown|latex --dest DIR --title "..." [--subtitle "..."]
                [--author "..."] [--slug book] [--lang en-GB]

Copies the template, fills in title/subtitle/author/date/identifier everywhere they
appear (metadata, cover SVG, LaTeX title page, hyperref metadata), and leaves the
sample chapters in place as living examples of every construct the pipeline
supports. Replace them chapter by chapter; do not start from an empty file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import shutil
import uuid

SKILL = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = {"markdown": SKILL / "templates" / "markdown-first", "latex": SKILL / "templates" / "latex-first"}


def replace_in(path: pathlib.Path, pairs: dict[str, str]) -> None:
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    original = text
    for old, new in pairs.items():
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")


def cover_lines(title: str) -> list[str]:
    """Split a title into <= 4 lines of <= 14 characters for the 132px cover type."""
    words, lines, current = title.upper().split(), [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) > 14 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:4]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", choices=TEMPLATES, required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="One-line subtitle")
    parser.add_argument("--author", default="Prepared for the reader")
    parser.add_argument("--slug", default="book")
    parser.add_argument("--lang", default="en-GB")
    args = parser.parse_args()

    dest = pathlib.Path(args.dest)
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"refusing to scaffold into a non-empty directory: {dest}")
    shutil.copytree(TEMPLATES[args.pipeline], dest, dirs_exist_ok=True)

    today = dt.date.today()
    pairs = {
        "BOOK TITLE": args.title,
        "Book\\\\Title": args.title.replace(": ", ":\\\\"),
        "One-line subtitle": args.subtitle,
        "Prepared for LEARNER": args.author,
        "Prepared for the reader": args.author,
        "REPLACE-WITH-UUID": str(uuid.uuid4()),
        "YYYY-MM-DD": today.isoformat(),
        "YYYY-MM": today.strftime("%Y-%m"),
        "MONTH YEAR": today.strftime("%B %Y"),
        "en-GB": args.lang,
        "SLUG      ?= book": f"SLUG      ?= {args.slug}",
        "SLUG     ?= book": f"SLUG     ?= {args.slug}",
    }
    for path in dest.rglob("*"):
        if path.suffix in {".md", ".tex", ".yaml", ".svg", ".css", ".lua", ".bib", ".py", ".csl"} or path.name == "Makefile":
            replace_in(path, pairs)

    # Cover: rewrite the two placeholder title lines into up to four fitted lines.
    cover = next(dest.rglob("cover.svg"))
    text = cover.read_text(encoding="utf-8")
    lines = cover_lines(args.title)
    start_y = 1085 - 185 * (len(lines) - 1) // 2
    new_lines = "\n".join(
        f'  <text x="800" y="{start_y + 185 * i}" fill="#f7f2e8" font-family="Georgia, serif" '
        f'font-size="132" letter-spacing="7" text-anchor="middle">{line}</text>'
        for i, line in enumerate(lines)
    )
    import re
    text = re.sub(r'  <text x="800" y="900".*?>BOOK</text>\n  <text x="800" y="1085".*?>TITLE</text>',
                  new_lines, text, flags=re.DOTALL)
    text = text.replace(f'>{args.title}</text>', f'>{args.title}</text>')
    cover.write_text(text, encoding="utf-8")

    (dest / "checks").mkdir(exist_ok=True)
    print(f"scaffolded {args.pipeline}-first book in {dest}")
    print("next: edit metadata, replace the sample chapters, then `make` and `make pages`")


if __name__ == "__main__":
    main()
