#!/usr/bin/env python3
"""Deterministic edits to the learner profile, with an append-only change log.

    profile.py show [--stale-days 180]
    profile.py field "Key" "value"                      # a "- Key:" line in any section
    profile.py level "Topic" LEVEL [--evidence "..."] [--verified] [--date YYYY-MM-DD]
    profile.py forget "Topic"                           # remove a topic from both level tables
    profile.py pref "Standing preference or correction"
    profile.py book --title T --path P --pipeline markdown|latex --assumes "..."
    profile.py stale [--days 180]                       # verified rows older than N days
    profile.py log [--tail 20]

Profile: $CRAFT_BOOK_PROFILE or ~/.agents/books/learner-profile.md (created from the
template on first use). Log: <profile dir>/profile-log.md. Set CRAFT_BOOK_PROFILE=off to
make every command a no-op that prints "profile updates disabled".
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import re
import shutil
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "templates" / "profile" / "learner-profile.md"
LEVELS = ("unknown", "shaky", "working", "solid")
VERIFIED_HEADER = "## Verified levels"
SELF_HEADER = "## Self-reported levels"
BOOKS_HEADER = "## Books built"
PREFS_HEADER = "## Standing preferences"


def profile_path() -> pathlib.Path | None:
    setting = os.environ.get("CRAFT_BOOK_PROFILE", "")
    if setting.lower() == "off":
        return None
    return pathlib.Path(setting).expanduser() if setting else pathlib.Path.home() / ".agents" / "books" / "learner-profile.md"


def load(path: pathlib.Path) -> list[str]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(TEMPLATE, path)
    return path.read_text(encoding="utf-8").splitlines()


def save(path: pathlib.Path, lines: list[str], entry: str) -> None:
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    log = path.parent / "profile-log.md"
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with log.open("a", encoding="utf-8") as handle:
        if log.stat().st_size == 0:
            handle.write("# Learner profile change log\n\nAppend-only. One line per automatic or requested change.\n\n")
        handle.write(f"- {stamp} — {entry}\n")


def section_bounds(lines: list[str], header_prefix: str) -> tuple[int, int]:
    start = next((i for i, l in enumerate(lines) if l.startswith(header_prefix)), None)
    if start is None:
        raise SystemExit(f"profile: section not found: {header_prefix}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def table_rows(lines: list[str], start: int, end: int) -> tuple[int, list[int]]:
    """Return (index of the separator row, indices of data rows) for the table in a section."""
    sep = next((i for i in range(start, end) if re.match(r"^\|\s*:?-+", lines[i])), None)
    if sep is None:
        raise SystemExit("profile: table missing in section " + lines[start])
    rows = [i for i in range(sep + 1, end) if lines[i].startswith("|")]
    return sep, rows


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_placeholder(line: str) -> bool:
    first = cells(line)[0] if cells(line) else ""
    return first == "" or first.startswith("(")


def upsert_row(lines: list[str], header: str, key: str, row: str) -> str:
    start, end = section_bounds(lines, header)
    sep, rows = table_rows(lines, start, end)
    for i in rows:
        if is_placeholder(lines[i]):
            lines[i] = row
            return "added"
        if cells(lines[i])[0].lower() == key.lower():
            lines[i] = row
            return "updated"
    insert_at = rows[-1] + 1 if rows else sep + 1
    lines.insert(insert_at, row)
    return "added"


def remove_row(lines: list[str], header: str, key: str) -> bool:
    start, end = section_bounds(lines, header)
    _, rows = table_rows(lines, start, end)
    for i in rows:
        if cells(lines[i])[0].lower() == key.lower():
            del lines[i]
            return True
    return False


def cmd_show(lines: list[str], args: argparse.Namespace) -> None:
    print("\n".join(lines))
    stale = stale_rows(lines, args.stale_days)
    if stale:
        print(f"\n[stale: {len(stale)} verified level(s) older than {args.stale_days} days — reconfirm with one diagnostic item each]")
        for row in stale:
            print("  " + row)


def stale_rows(lines: list[str], days: int) -> list[str]:
    start, end = section_bounds(lines, VERIFIED_HEADER)
    _, rows = table_rows(lines, start, end)
    cutoff = dt.date.today() - dt.timedelta(days=days)
    out = []
    for i in rows:
        c = cells(lines[i])
        if is_placeholder(lines[i]) or len(c) < 4:
            continue
        try:
            when = dt.date.fromisoformat(c[3][:10])
        except ValueError:
            continue
        if when < cutoff:
            out.append(lines[i])
    return out


def cmd_field(lines: list[str], args: argparse.Namespace) -> str:
    pattern = re.compile(r"^- " + re.escape(args.key) + r"\s*(?:/[^:]*)?:", re.IGNORECASE)
    for i, line in enumerate(lines):
        if pattern.match(line):
            label = line.split(":", 1)[0]
            lines[i] = f"{label}: {args.value}"
            return f"field {args.key!r} -> {args.value!r}"
    _, end = section_bounds(lines, "## Identity")
    lines.insert(end, f"- {args.key}: {args.value}")
    return f"field {args.key!r} added -> {args.value!r}"


def cmd_level(lines: list[str], args: argparse.Namespace) -> str:
    if args.level not in LEVELS:
        raise SystemExit(f"profile: level must be one of {LEVELS}")
    date = args.date or dt.date.today().isoformat()
    if args.verified:
        row = f"| {args.topic} | {args.level} | {args.evidence or 'diagnostic'} | {date} |"
        action = upsert_row(lines, VERIFIED_HEADER, args.topic, row)
        remove_row(lines, SELF_HEADER, args.topic)
        return f"verified level {action}: {args.topic} = {args.level} ({args.evidence or 'diagnostic'})"
    row = f"| {args.topic} | {args.level} | {args.evidence or ''} |"
    action = upsert_row(lines, SELF_HEADER, args.topic, row)
    return f"self-reported level {action}: {args.topic} = {args.level}"


def cmd_forget(lines: list[str], args: argparse.Namespace) -> str:
    removed = remove_row(lines, VERIFIED_HEADER, args.topic) | remove_row(lines, SELF_HEADER, args.topic)
    if not removed:
        raise SystemExit(f"profile: no level entry for {args.topic!r}")
    return f"forgot level entries for {args.topic}"


def cmd_pref(lines: list[str], args: argparse.Namespace) -> str:
    start, end = section_bounds(lines, PREFS_HEADER)
    date = dt.date.today().isoformat()
    body = [i for i in range(start + 1, end) if lines[i].startswith("- ")]
    if body and lines[body[0]].startswith("- (dated lines"):
        lines[body[0]] = f"- {date}: {args.text}"
    else:
        lines.insert((body[-1] + 1) if body else end, f"- {date}: {args.text}")
    return f"preference recorded: {args.text}"


def cmd_book(lines: list[str], args: argparse.Namespace) -> str:
    date = dt.date.today().isoformat()
    row = f"| {args.title} | {args.path} | {date} | {args.pipeline} | {args.assumes} |"
    action = upsert_row(lines, BOOKS_HEADER, args.title, row)
    return f"book {action}: {args.title} ({args.path})"


def cmd_log(path: pathlib.Path, args: argparse.Namespace) -> None:
    log = path.parent / "profile-log.md"
    if not log.exists():
        print("no changes logged yet")
        return
    print("\n".join(log.read_text(encoding="utf-8").splitlines()[-args.tail:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("show"); p.add_argument("--stale-days", type=int, default=180)
    p = sub.add_parser("field"); p.add_argument("key"); p.add_argument("value")
    p = sub.add_parser("level"); p.add_argument("topic"); p.add_argument("level"); p.add_argument("--evidence"); p.add_argument("--verified", action="store_true"); p.add_argument("--date")
    p = sub.add_parser("forget"); p.add_argument("topic")
    p = sub.add_parser("pref"); p.add_argument("text")
    p = sub.add_parser("book"); p.add_argument("--title", required=True); p.add_argument("--path", required=True); p.add_argument("--pipeline", choices=("markdown", "latex"), required=True); p.add_argument("--assumes", required=True)
    p = sub.add_parser("stale"); p.add_argument("--days", type=int, default=180)
    p = sub.add_parser("log"); p.add_argument("--tail", type=int, default=20)
    args = parser.parse_args()

    path = profile_path()
    if path is None:
        print("profile updates disabled (CRAFT_BOOK_PROFILE=off)")
        return
    if args.command == "log":
        cmd_log(path, args)
        return
    lines = load(path)
    if args.command == "show":
        cmd_show(lines, args)
        return
    if args.command == "stale":
        rows = stale_rows(lines, args.days)
        print("\n".join(rows) if rows else f"no verified levels older than {args.days} days")
        return
    entry = {"field": cmd_field, "level": cmd_level, "forget": cmd_forget, "pref": cmd_pref, "book": cmd_book}[args.command](lines, args)
    save(path, lines, entry)
    print(entry)


if __name__ == "__main__":
    main()
