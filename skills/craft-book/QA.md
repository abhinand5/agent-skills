# QA: what "flawless" means before delivery

Run in this order. Automated gates first; they are cheap and catch the silent
conversion damage. Then the human-style passes; they catch what checkers cannot.

## 1. Automated gates (`make`, `make verify`)

| Gate | Catches |
|:--|:--|
| `check_pdf.py` | TeX errors, undefined refs/citations, missing glyphs, overfull boxes > 5 pt, page budget (`--max-pages`) |
| `check_epub.py` | container/manifest/spine validity, broken links and fragments, images without alt, tables flattened to prose, ragged tables, filename `<title>`s, bare control words in maths (a missing backslash), leaked LaTeX, table count vs source, Kindle size limit |
| `check_markdown.py` | leaked LaTeX or fenced-div syntax, unresolved citations, unbalanced `$`, missing local link targets, missing chapter numbering |
| `run_checks.py` | every number in worked examples and answers, recomputed |

Add `--max-pages` from the brief to the PDF check in the Makefile once the budget is
agreed. Add `--require-text` needles for anything that must survive (a specific link,
the answer-key heading). Do not weaken a gate to get green; fix the source.

## 2. Visual pass (mandatory)

`make pages` renders every PDF page and tiles contact sheets into `build/pages/`.
View every sheet, then open at full size: the title page, the contents, the first
page of each chapter, every page with a table, figure, or long display equation, and
the answer key. Look for: text in the margin, a box split awkwardly across pages, a
figure pushed to a page of its own, orphaned headings, `phi`-style literal control
words, wrong small caps, ugly line breaks in headings.

For the EPUB: unpack it, serve it (`python3 -m http.server`), and screenshot two or
three chapters at 600 px and 400 px — one with tables, one with figures, one with long
maths. Check display maths is centred, tables have all their columns, boxes have
titles, headings are numbered, nothing scrolls horizontally.

For Markdown: open the file in the reader's tool (Obsidian, GitHub preview). Check
maths renders with `$…$`, callouts are blockquotes with bold titles, images resolve.

## 3. Correctness pass

Re-read every displayed identity against its stated conditions and its cited source.
Recompute every worked example by hand or in `checks/`. Do every checkpoint and compare
with the answer key: the answer must be complete, not a hint. Confirm no residue
sentences (see WRITING.md). Confirm terminology matches the glossary/notation page.

## 4. Reader-fit pass

Against `BOOK-BRIEF.md`: every capability statement has at least one chapter that
builds it and one checkpoint that tests it; nothing assumed that the profile marks as
unknown without a refresher; page budget met; chapter order matches the reading plan;
spelling/locale consistent.

## 5. Delivery note

State plainly: which editions were built, page count, what was verified and how, what
could not be verified (e.g. no on-device Kindle test), and any known limitations.
Then run the delivery triggers from [PROFILE.md](PROFILE.md) (`profile.py book …` and
one verified `level` per exercised capability) and, if the workspace uses the `teach`
layout, add a learning record.
