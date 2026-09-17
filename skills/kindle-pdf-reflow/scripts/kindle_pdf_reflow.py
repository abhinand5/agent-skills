#!/usr/bin/env python3
"""Create a sample-first, Paperwhite-sized visually reflowed PDF.

The default profile is calibrated to the user's approved Kindle size-3 reading
geometry. Run ``sample`` first, inspect it on device, then use ``build --approved``.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    import pymupdf
except ImportError as exc:  # pragma: no cover - environment guidance
    raise SystemExit("PyMuPDF is required. Run with: uv run --with pymupdf <script> ...") from exc


@dataclass(frozen=True)
class Segment:
    start: int
    end: int
    erase_vertical_lines: bool


def parse_page_set(spec: str | None, total: int) -> set[int]:
    if not spec:
        return set()
    result: set[int] = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            start, end = int(left), int(right)
        else:
            start = end = int(token)
        if start < 1 or end < start or end > total:
            raise ValueError(f"page range {token!r} is outside 1-{total}")
        result.update(range(start, end + 1))
    return result


def sample_range(spec: str, total: int) -> tuple[int, int]:
    if spec == "auto":
        length = min(16, total)
        start = max(1, min(total - length + 1, round(total * 0.085)))
        return start, start + length - 1
    if "-" not in spec:
        raise ValueError("sample pages must be a contiguous range such as 47-62 or 'auto'")
    left, right = spec.split("-", 1)
    start, end = int(left), int(right)
    if start < 1 or end < start or end > total:
        raise ValueError(f"sample range {spec!r} is outside 1-{total}")
    return start, end


def segments(start: int, end: int, special: set[int]) -> list[Segment]:
    result: list[Segment] = []
    run_start = start
    mode = start in special
    for page in range(start + 1, end + 1):
        page_mode = page in special
        if page_mode != mode:
            result.append(Segment(run_start, page - 1, mode))
            run_start, mode = page, page_mode
    result.append(Segment(run_start, end, mode))
    return result


def find_k2(explicit: str | None) -> Path:
    project_candidates = [
        root / "tools/vendor/k2pdfopt"
        for root in (Path.cwd(), *Path.cwd().parents)
    ]
    candidates = [
        Path(explicit).expanduser() if explicit else None,
        Path(os.environ["K2PDFOPT_BIN"]).expanduser() if os.environ.get("K2PDFOPT_BIN") else None,
        Path(found) if (found := shutil.which("k2pdfopt")) else None,
        *project_candidates,
    ]
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise SystemExit(
        "k2pdfopt was not found. Install it, pass --k2pdfopt PATH, or set K2PDFOPT_BIN."
    )


def default_output(source: Path, command: str, start: int, end: int) -> Path:
    suffix = (f"-kindle-sample-p{start}-{end}.pdf" if command == "sample"
              else "-kindle-size3.pdf")
    return source.with_name(source.stem + suffix)


def k2_command(args: argparse.Namespace, k2: Path, source: Path, seg: Segment, part: Path) -> list[str]:
    cmd = [
        str(k2), str(source), "-p", f"{seg.start}-{seg.end}",
        "-ui-", "-dev", "kp3",
        "-w", str(args.width), "-h", str(args.height), "-dpi", str(args.dpi),
        "-col", "1", "-fc-", "-fs", str(args.font_size),
        "-oml", f"{args.margin_left}s", "-omr", f"{args.margin_right}s",
        "-omt", f"{args.margin_top}s", "-omb", f"{args.margin_bottom}s",
        "-vls", str(args.line_spacing), "-bpc", str(args.bits),
        "-nt", str(args.threads), "-y", "-x", "-er", str(args.erode),
    ]
    if seg.erase_vertical_lines:
        cmd += ["-evl", "1"]
    cmd += ["-o", str(part)]
    return cmd


def assemble(source: Path, parts: list[Path], runs: list[Segment], output: Path, full: bool) -> None:
    source_doc = pymupdf.open(source)
    source_toc = source_doc.get_toc()
    docs = [pymupdf.open(part) for part in parts]
    part_tocs = [doc.get_toc() for doc in docs]

    merged = pymupdf.open()
    offsets: list[int] = []
    for doc in docs:
        offsets.append(merged.page_count)
        merged.insert_pdf(doc)

    if source_toc:
        signature = [(row[0], row[1]) for row in source_toc]
        if any([(row[0], row[1]) for row in toc] != signature for toc in part_tocs):
            raise RuntimeError("k2pdfopt outline no longer matches the source; refusing bad navigation")

        candidates: list[tuple[int, list[object]]] = list(enumerate(source_toc))
        if not full:
            first, last = runs[0].start, runs[-1].end
            chosen = [(index, row) for index, row in candidates if first <= row[2] <= last]
            if chosen:
                min_level = min(row[0] for _, row in chosen)
                candidates = [(index, [row[0] - min_level + 1, row[1], row[2]])
                              for index, row in chosen]
            else:
                candidates = []

        selected: list[list[object]] = []
        for index, row in candidates:
            level, title, source_page = row[:3]
            for part_index, run in enumerate(runs):
                if run.start <= source_page <= run.end:
                    target = offsets[part_index] + part_tocs[part_index][index][2]
                    selected.append([level, title, target])
                    break
        if selected:
            merged.set_toc(selected)

    metadata = source_doc.metadata.copy()
    metadata["creator"] = "Kindle PDF Reflow - approved size-3 profile"
    metadata["producer"] = "k2pdfopt + PyMuPDF assembly"
    merged.set_metadata(metadata)
    merged.save(output, garbage=3, deflate=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def basic_verify(output: Path, source: Path, expect_outline: bool) -> None:
    doc = pymupdf.open(output)
    src = pymupdf.open(source)
    if doc.page_count < 1:
        raise RuntimeError("output contains no pages")
    sizes = [(page.rect.width, page.rect.height) for page in doc]
    spread = (max(w for w, _ in sizes) - min(w for w, _ in sizes),
              max(h for _, h in sizes) - min(h for _, h in sizes))
    if spread[0] > 2 or spread[1] > 2:
        raise RuntimeError(f"output page geometry varies by {spread[0]:.1f} x {spread[1]:.1f} pt")
    blank = [i + 1 for i, page in enumerate(doc)
             if not page.get_text().strip() and not page.get_images(full=True)]
    if blank:
        raise RuntimeError(f"output has pages with neither text nor images: {blank[:12]}")
    if expect_outline and src.get_toc() and len(doc.get_toc()) != len(src.get_toc()):
        raise RuntimeError("output outline count does not match source")
    thin = [i + 1 for i, page in enumerate(doc) if len(page.get_text().strip()) < 40]
    print(f"output: {output}")
    print(f"pages: {doc.page_count} (source {src.page_count})")
    print(f"size: {output.stat().st_size / 1e6:.1f} MB")
    print(f"geometry: {doc[0].rect.width / 72:.2f} x {doc[0].rect.height / 72:.2f} in")
    print(f"outline: {len(doc.get_toc())} entries")
    print(f"thin pages requiring visual review: {thin[:20]}")
    print(f"sha256: {sha256(output)}")
    print("basic verification: pass")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sample", "build"):
        p = sub.add_parser(name)
        p.add_argument("input", type=Path)
        p.add_argument("-o", "--output", type=Path)
        p.add_argument("--special-pages", help="source pages needing local -evl 1, e.g. 61-62,190")
        p.add_argument("--k2pdfopt", help="path to k2pdfopt executable")
        p.add_argument("--width", type=int, default=1264)
        p.add_argument("--height", type=int, default=1680)
        p.add_argument("--dpi", type=int, default=300)
        p.add_argument("--font-size", type=float, default=7.75)
        p.add_argument("--line-spacing", type=float, default=1.55)
        p.add_argument("--margin-left", type=float, default=0.07)
        p.add_argument("--margin-right", type=float, default=0.07)
        p.add_argument("--margin-top", type=float, default=0.06)
        p.add_argument("--margin-bottom", type=float, default=0.10)
        p.add_argument("--bits", type=int, choices=(1, 2, 4), default=4)
        p.add_argument("--erode", type=int, choices=(0, 1, 2), default=1)
        p.add_argument("--threads", type=int, default=min(16, os.cpu_count() or 1))
        p.add_argument("--temp-dir", type=Path)
        p.add_argument("--keep-temp", action="store_true")
        p.add_argument("--force", action="store_true", help="overwrite an existing output")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--no-verify", action="store_true")
    sub.choices["sample"].add_argument("--pages", default="auto",
                                       help="contiguous source range or auto (default: auto)")
    sub.choices["build"].add_argument("--approved", action="store_true",
                                      help="confirm that a sample using this profile was approved")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"input PDF not found: {source}")
    if source.suffix.lower() != ".pdf":
        raise SystemExit("input must be a PDF")
    if args.command == "build" and not args.approved:
        raise SystemExit("full conversion requires --approved after an on-device sample review")

    source_doc = pymupdf.open(source)
    total = source_doc.page_count
    try:
        if args.command == "sample":
            start, end = sample_range(args.pages, total)
        else:
            start, end = 1, total
        special = parse_page_set(args.special_pages, total)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    runs = segments(start, end, special)
    output = (args.output.expanduser().resolve() if args.output
              else default_output(source, args.command, start, end))
    if output.exists() and not args.force and not args.dry_run:
        raise SystemExit(f"output already exists: {output} (use --force to replace it)")
    output.parent.mkdir(parents=True, exist_ok=True)
    k2 = find_k2(args.k2pdfopt)

    temp_root = Path(tempfile.mkdtemp(prefix="kindle-pdf-reflow-", dir=args.temp_dir))
    parts = [temp_root / f"part-{index + 1:03d}.pdf" for index in range(len(runs))]
    try:
        commands = [k2_command(args, k2, source, run, part)
                    for run, part in zip(runs, parts, strict=True)]
        active_special = sorted(special & set(range(start, end + 1)))
        print(f"source pages: {start}-{end} of {total}")
        print(f"segments: {len(runs)}; special pages: {active_special}")
        for command in commands:
            print("running:", " ".join(command))
            if not args.dry_run:
                subprocess.run(command, check=True)
        if args.dry_run:
            print(f"would write: {output}")
            return
        assemble(source, parts, runs, output, full=args.command == "build")
        if not args.no_verify:
            basic_verify(output, source, expect_outline=args.command == "build")
    finally:
        if args.keep_temp:
            print(f"kept temporary files: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
