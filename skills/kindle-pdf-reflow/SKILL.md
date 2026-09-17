---
name: kindle-pdf-reflow
description: Convert PDF books into visually reflowed, Paperwhite-sized PDFs using the device-approved Kindle size-3 profile. Use when a user wants a PDF made comfortable for Kindle/Paperwhite reading, wants a 16-page trial before full conversion, or needs an existing Kindle PDF recipe applied to another book. Do not use for EPUB creation or ordinary PDF compression.
---

# Kindle PDF Reflow

Produce a fixed-layout PDF that preserves the source's printed equations, figures,
algorithms, and typography while rewrapping prose for a narrow Kindle screen. The
default profile is the one approved on a 7-inch, 1264 x 1680, 300 ppi Paperwhite:

```text
-fs 7.75 -vls 1.55
-oml 0.07s -omr 0.07s -omt 0.06s -omb 0.10s
-bpc 4 -er 1
```

This is visual reflow, not true ebook reflow. Kindle font controls will not resize it.

## Workflow

1. Inspect the input's page count, geometry, outline, and representative content.
2. Create a contiguous 16-source-page trial with `scripts/kindle_pdf_reflow.py sample`.
   If the user did not nominate pages, `--pages auto` selects a window near 8.5% of
   the book, which usually avoids front matter while remaining early enough to review.
3. Render every trial page at 1264 x 1680 and inspect prose, equations, figures,
   captions, boxed algorithms, and page edges. Freeze and ask for on-device approval.
4. Do not run the full conversion until the user approves the sample, unless they
   explicitly waive the trial. Full conversion requires the CLI's `--approved` flag.
5. Build with `scripts/kindle_pdf_reflow.py build`, then run
   `scripts/verify_kindle_pdf.py`, render contact sheets for every page, and inspect
   representative native-resolution pages. Deliver only after both structural and
   visual checks pass.

Read [references/qa.md](references/qa.md) when selecting trial pages, handling broken
vertical-rule pages, or interpreting verifier warnings.

## Commands

Run these commands from this workspace's root. `k2pdfopt` is discovered from
`--k2pdfopt`, `K2PDFOPT_BIN`, `PATH`, or the workspace's vendored executable.

```bash
python3 .agents/skills/kindle-pdf-reflow/scripts/kindle_pdf_reflow.py \
  sample input.pdf --pages auto

python3 .agents/skills/kindle-pdf-reflow/scripts/kindle_pdf_reflow.py \
  build input.pdf --approved -o input-kindle-size3.pdf

uv run --with pymupdf --with numpy \
  .agents/skills/kindle-pdf-reflow/scripts/verify_kindle_pdf.py \
  input-kindle-size3.pdf --source input.pdf
```

Use `--special-pages 61-62,190` only for source pages proven to slice incorrectly
because of tall vertical rules. It applies `-evl 1` only to those pages, segments the
conversion safely, rejoins the result, and restores outline destinations. Never apply
`-evl 1` globally: it can erase legitimate vertical shapes in plots.

Use `--help` for profile overrides. Preserve the approved defaults unless the user asks
for a different device or reading size.

## Output contract

- Preserve all visible content; do not rewrite or OCR-retypeset the book.
- Keep 4-bit greyscale unless file size is a stated priority.
- Preserve or rebuild the source outline when it exists.
- Treat thin continuation pages as suspicious but not automatically defective.
- Report page count, decimal file size, outline count, verification result, and any
  known text-layer limitations.
