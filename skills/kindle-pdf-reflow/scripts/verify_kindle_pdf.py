#!/usr/bin/env python3
"""Deep structural and text-layer verification for a visually reflowed PDF."""

from __future__ import annotations

import argparse
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pymupdf

LIGATURES = str.maketrans({
    "ﬃ": "ffi", "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬄ": "ffl",
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
})


def norm(text: str) -> str:
    text = text.replace("\u00ad", "").translate(LIGATURES)
    text = re.sub(r"-\s*\n\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    folded = text.replace("\u00ad", "").translate(LIGATURES)
    folded = re.sub(r"[-\u2010]\s*\n\s*", "", folded)
    folded = re.sub(r"[-\u2010]", "", folded)
    return [word.strip(".,;:!?()[]{}'\"\u2019\u201c\u201d—–") for word in folded.split()]


def ink_fraction(doc: pymupdf.Document, dpi: int = 200) -> float:
    total_ink = total_pixels = 0
    for page in doc:
        pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        image = np.frombuffer(pix.samples, dtype=np.uint8)
        total_ink += int((image < 160).sum())
        total_pixels += image.size
    return total_ink / total_pixels


def edge_ink(page: pymupdf.Page, margin: int = 3) -> dict[str, int]:
    pix = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY)
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = image < 160
    corner = min(40, pix.width // 10, pix.height // 10)
    return {
        "top": int(ink[:margin, corner:-corner].sum()),
        "bottom": int(ink[-margin:, corner:-corner].sum()),
        "left": int(ink[corner:-corner, :margin].sum()),
        "right": int(ink[corner:-corner, -margin:].sum()),
        "interior": int(ink[margin:-margin, margin:-margin].sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("converted", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--rare-max", type=int, default=4)
    parser.add_argument("--rare-len", type=int, default=9)
    args = parser.parse_args()

    failures: list[str] = []
    doc = pymupdf.open(args.converted)
    source = pymupdf.open(args.source)
    pages = doc.page_count
    rng = random.Random(0)

    rects = Counter((round(page.rect.width, 1), round(page.rect.height, 1)) for page in doc)
    sizes = [(page.rect.width, page.rect.height) for page in doc]
    spread = (max(width for width, _ in sizes) - min(width for width, _ in sizes),
              max(height for _, height in sizes) - min(height for _, height in sizes))
    if spread[0] > 2 or spread[1] > 2:
        failures.append(f"page geometry varies by {spread[0]:.1f} x {spread[1]:.1f} pt")

    bitmaps: Counter[tuple[int, int]] = Counter()
    depths: Counter[int] = Counter()
    bitmap_bytes = 0
    for page in doc:
        for xref, *_ in page.get_images(full=True):
            info = doc.extract_image(xref)
            bitmaps[(info["width"], info["height"])] += 1
            depths[info["bpc"]] += 1
            bitmap_bytes += len(info["image"])

    texts = [norm(page.get_text()) for page in doc]
    thin = [index + 1 for index, text in enumerate(texts) if len(text) < 40]
    outline = doc.get_toc()
    if any(not 1 <= entry[2] <= pages for entry in outline):
        failures.append("outline contains an out-of-range destination")

    source_words = sum(len(norm(page.get_text()).split()) for page in source)
    output_words = sum(len(text.split()) for text in texts)
    source_counts = Counter(word for page in source for word in words(page.get_text()))
    rare = {word for word, count in source_counts.items()
            if count <= args.rare_max and len(word) >= args.rare_len and word.isalpha()}
    output_counts = Counter(word for text in texts for word in words(text))
    joined = " ".join(texts)

    def present(word: str) -> bool:
        middle = len(word) // 2
        pattern = re.escape(word[:middle]) + r"[\s\u00ad-]*" + re.escape(word[middle:])
        return re.search(pattern, joined, re.IGNORECASE) is not None

    missing = sorted(word for word in rare if word not in output_counts and not present(word))

    source_ink, output_ink = ink_fraction(source), ink_fraction(doc)
    source_area = sum(page.rect.width * page.rect.height for page in source)
    output_area = sum(page.rect.width * page.rect.height for page in doc)
    source_ink_per_word = source_ink * source_area / max(source_words, 1)
    output_ink_per_word = output_ink * output_area / max(output_words, 1)

    blank = [index + 1 for index in rng.sample(range(pages), min(40, pages))
             if len(texts[index]) < 40 and not doc[index].get_images(full=True)]
    edge_totals: Counter[str] = Counter()
    for index in rng.sample(range(pages), min(60, pages)):
        for side, count in edge_ink(doc[index]).items():
            edge_totals[side] += count
    edge_ratio = sum(edge_totals[side] for side in ("top", "bottom", "left", "right")) \
        / max(edge_totals["interior"], 1)

    page_width, page_height = doc[0].rect.width / 72, doc[0].rect.height / 72
    print(f"converted: {args.converted}")
    print(f"  pages            {pages} (source {source.page_count})")
    print(f"  file size        {args.converted.stat().st_size / 1e6:.1f} MB")
    print(f"  page geometry    {rects.most_common(1)[0][0]} pt = {page_width:.2f} x {page_height:.2f} in")
    print(f"  page bitmaps     {bitmaps.most_common(1)[0] if bitmaps else None}")
    print(f"  bit depth        {depths.most_common(1)[0] if depths else None}"
          f" (bitmap data {bitmap_bytes / 1e6:.1f} MB)")
    print(f"  words            {output_words} out vs {source_words} in"
          f" ({output_words / max(source_words, 1) * 100:.1f}%)")
    print(f"  text coverage    {pages - len(thin)}/{pages}; thin pages: {thin[:20]}")
    print(f"  outline          {len(outline)} entries, first={outline[0] if outline else None}")
    print(f"  rare words       {len(rare) - len(missing)}/{len(rare)} present as text")
    if missing:
        print(f"  rare-word misses {missing[:20]}")
    print(f"  ink per word     {output_ink_per_word:.2e} vs {source_ink_per_word:.2e}")
    print(f"  sampled blanks   {blank}")
    print(f"  edge ink         {edge_ratio:.3%} of interior ink")

    if len(missing) > len(rare) * 0.02:
        failures.append(f"{len(missing)}/{len(rare)} rare source words missing")
    if not 0.7 <= output_ink_per_word / source_ink_per_word <= 1.7:
        failures.append("ink per word differs too much from source")
    if blank:
        failures.append(f"sampled pages are blank: {blank}")
    if edge_ratio > 0.01:
        failures.append(f"ink touches page edges ({edge_ratio:.2%})")

    print("\nRESULT:", "FAIL" if failures else "pass")
    for failure in failures:
        print("  -", failure)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
