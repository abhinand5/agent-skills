# Pipelines: one source, three editions

Both templates produce `output/pdf/SLUG.pdf`, `output/epub/SLUG.epub`, and
`output/markdown/SLUG.md` (+ `assets/`) from one source, run the same checkers, and
share `checks/` for numeric verification. Tooling: pandoc ≥ 3, LuaLaTeX (TeX Live),
rsvg-convert, poppler, python3, ImageMagick `montage` (contact sheets only).

## Choosing the pipeline (decide per book, record the reason in the brief)

Default to **Markdown-first**. Choose **LaTeX-first** only when *all* of these hold:

- PDF is the primary edition and the reader mostly prints or annotates;
- the book needs constructs Markdown cannot express well: numbered theorem
  environments, TikZ diagrams, multi-line `align` with `\intertext`, custom page
  layout; and
- the reader does not plan to edit the source in Obsidian/GitHub.

Otherwise Markdown-first: it is the only option where the Markdown edition is
lossless, and it avoids the whole class of "pandoc's LaTeX reader silently dropped
this" failures.

## Markdown-first (`templates/markdown-first/`)

```
metadata.yaml   src/NN-*.md   assets/*.svg   references.bib   numeric.csl   checks/*.py
pdf/preamble.tex   epub/kindle.css   markdown/template.md   filters/{structure,callouts,svg-figures}.lua
```

- Source: pandoc Markdown with `$…$` maths, pipe tables, `::: class` fenced divs for
  callouts (`mentalmodel failuremode checkpoint takeaway example algorithm`, optional
  `title="…"`), `[@key]` citations, `![caption](assets/x.svg)` figures.
- Structure: level-1 headings are chapters; `{.unnumbered}` for front/back matter; a
  raw `\appendix` line switches to Appendix A/B/C; `\newpage` is honoured in PDF only.
- Edition-only content: `::: printonly`, `::: epubonly`, `::: mdonly`.
- PDF: pandoc → LaTeX → LuaLaTeX ×2, 7×10 in, EB Garamond if installed else TeX Gyre
  Pagella; boxes are tcolorbox; title page from metadata (`title`, `subtitle`, `tagline`).
- EPUB: MathML maths, SVG figures, numbered headings via filter, `[n]` linked references,
  cover from `assets/cover.svg` (1600×2560).
- Markdown: GFM with `$…$` maths, blockquote callouts, plain image links, flattened
  reference list, minimal YAML front matter.
- Bib titles: protect capitalisation with braces in `references.bib` (`{An Introduction}`).

## LaTeX-first (`templates/latex-first/`)

```
book.tex  style.tex  frontmatter.tex  chapters/*.tex  backmatter/*.tex
epub/{metadata.yaml,kindle.css,assets/*.svg,filters/{book,markdown}.lua}   checks/*.py
```

- Print is hand-set; `pandoc --from=latex` derives EPUB and Markdown through
  `epub/filters/book.lua`, which numbers headings from `\label{ch:…}`/`\label{app:…}`,
  links `\cite` to `\bibitem` entries (keys read from `backmatter/bibliography.tex`),
  and titles the boxes.
- **Survives pandoc:** `tabularx` with `l c r p X` columns, `booktabs` rules, the
  tcolorbox environments in `style.tex`, `\practice{…}`, `\reading{…}`, `\intuition{…}`,
  `\href`, amsmath displays, `\begin{epubonly}` blocks.
- **Does not survive:** custom column types (`\newcolumntype`), TikZ (give every figure
  an SVG twin in `epubonly`), `\newcommand` with complex bodies used inside maths
  (keep macros simple: pandoc expands `\newcommand` but not `\DeclareMathOperator`
  tricks — test with `make epub` early), `\input` inside chapters.

## Kindle contract (binding when EPUB is requested)

1. Reflowable EPUB 3; MathML for maths; SVG or PNG images with alt text; no fonts
   embedded; cover 1600×2560 PNG; every XHTML < 30 MB; stable `identifier`.
2. CSS: no `display:block` on `math`, no `overflow-x`, no fixed widths; tables are
   plain `width:100%` with borders on rows; callouts are bordered divs with a bold
   title line; `page-break-inside: avoid` on boxes.
3. Tables must be real `<table>`s: `check_epub.py --expect-tables N` compares against
   the source count (`count_tables.py`).
4. Chapter files carry real `<title>`s (`polish_epub.py`), headings are numbered, TOC
   depth 2, one navigation document, linked citations.
5. Verify in a browser at 600 px and 400 px (Playwright or a local server + screenshot)
   and, when possible, on the reader's device via Send to Kindle. If the device does not
   render MathML, fall back to pre-rendered SVG maths (pandoc `--webtex` is not
   acceptable — it needs a network) and say so in the delivery note.

## Adding a construct

When the book needs something the template lacks (a new box, a theorem environment, a
code listing style), add it in *all three* places — preamble/style, EPUB CSS + filter,
Markdown mapping — and extend the sample chapter so the next build exercises it.
