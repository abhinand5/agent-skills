# craft-book: Markdown-first pipeline. One source, three editions.
#   make            -> PDF + EPUB + Markdown, each checked
#   make pdf | epub | md | check | pages | clean
#
# Requires: pandoc >= 3, lualatex (TeX Live), rsvg-convert, poppler (pdftoppm/pdfinfo),
#           python3, ImageMagick `montage` (for contact sheets only).

SHELL := /bin/sh
export TEXMFVAR := $(CURDIR)/.texmf-var
export TEXMFCACHE := $(CURDIR)/.texmf-var
export BUILD_DIR := build

SLUG      ?= book
SKILL     ?= $(HOME)/.agents/skills/craft-book
SCRIPTS   := $(SKILL)/scripts
SRC       := $(sort $(wildcard src/*.md))
ASSETS    := $(wildcard assets/*)
FILTERS   := filters/structure.lua filters/callouts.lua
OUT       := output
PDF       := $(OUT)/pdf/$(SLUG).pdf
EPUB      := $(OUT)/epub/$(SLUG).epub
MD        := $(OUT)/markdown/$(SLUG).md
COVER_PNG := build/cover.png
TITLEVARS := build/title-vars.tex

COMMON := --from=markdown+tex_math_dollars+fenced_divs+bracketed_spans+implicit_figures \
          --metadata-file=metadata.yaml --citeproc --csl=numeric.csl \
          --lua-filter=filters/structure.lua --lua-filter=filters/callouts.lua \
          --resource-path=.:src

.DELETE_ON_ERROR:
.PHONY: all pdf epub md check check-pdf check-epub check-md pages verify clean

all: pdf epub md

pdf: $(PDF)
epub: $(EPUB)
md: $(MD)

build:
	mkdir -p build

$(TITLEVARS): metadata.yaml | build
	printf '%s\n' '\providecommand{\booksubtitle}{$$subtitle$$}' '\providecommand{\booktagline}{$$tagline$$}' > build/title-vars.tpl
	pandoc -f markdown -t latex --metadata-file=metadata.yaml --template=build/title-vars.tpl -o $@ /dev/null

# PDF: pandoc writes LaTeX, LuaLaTeX runs twice so the TOC and links settle, and the
# log stays in build/ where check_pdf.py can read it.
$(PDF): $(SRC) $(ASSETS) metadata.yaml references.bib numeric.csl pdf/preamble.tex $(FILTERS) filters/svg-figures.lua $(TITLEVARS) | build
	mkdir -p $(OUT)/pdf
	pandoc $(SRC) $(COMMON) --lua-filter=filters/svg-figures.lua \
		--to=latex --standalone \
		-V documentclass=book -V classoption=openany -V fontsize=11pt \
		-V colorlinks=true -V linkcolor=navy -V citecolor=teal -V urlcolor=teal \
		-V secnumdepth=1 --top-level-division=chapter --number-sections --toc --toc-depth=1 \
		--include-in-header=$(TITLEVARS) --include-in-header=pdf/preamble.tex \
		--output=build/$(SLUG).tex
	lualatex -interaction=nonstopmode -halt-on-error -output-directory=build build/$(SLUG).tex >/dev/null
	lualatex -interaction=nonstopmode -halt-on-error -output-directory=build build/$(SLUG).tex >/dev/null
	cp build/$(SLUG).pdf $(PDF)
	python3 $(SCRIPTS)/check_pdf.py $(PDF) build/$(SLUG).log

$(COVER_PNG): assets/cover.svg | build
	rsvg-convert --width 1600 --height 2560 $< --output $@

$(EPUB): $(SRC) $(ASSETS) metadata.yaml references.bib numeric.csl epub/kindle.css $(FILTERS) $(COVER_PNG) | build
	mkdir -p $(OUT)/epub
	pandoc $(SRC) $(COMMON) \
		--to=epub3 --css=epub/kindle.css --epub-cover-image=$(COVER_PNG) \
		--epub-title-page=true --split-level=1 --toc --toc-depth=2 --math-method=mathml \
		--output=$(EPUB)
	python3 $(SCRIPTS)/polish_epub.py $(EPUB)
	python3 $(SCRIPTS)/check_epub.py $(EPUB) --expect-tables $$(python3 $(SCRIPTS)/count_tables.py $(SRC))

$(MD): $(SRC) $(ASSETS) metadata.yaml references.bib numeric.csl $(FILTERS) markdown/template.md | build
	mkdir -p $(OUT)/markdown/assets
	pandoc $(SRC) $(COMMON) \
		--to=gfm-tex_math_gfm+tex_math_dollars --wrap=none --toc --toc-depth=2 \
		--standalone --template=markdown/template.md \
		--output=$(MD)
	cp -f assets/*.svg $(OUT)/markdown/assets/ 2>/dev/null || true
	python3 $(SCRIPTS)/check_markdown.py $(MD)

check: check-pdf check-epub check-md

check-pdf: $(PDF)
	python3 $(SCRIPTS)/check_pdf.py $(PDF) build/$(SLUG).log

check-epub: $(EPUB)
	python3 $(SCRIPTS)/check_epub.py $(EPUB) --expect-tables $$(python3 $(SCRIPTS)/count_tables.py $(SRC))

check-md: $(MD)
	python3 $(SCRIPTS)/check_markdown.py $(MD)

# Page renders + contact sheets for a visual pass (build/pages/).
pages: $(PDF)
	sh $(SCRIPTS)/contact_sheet.sh $(PDF) build/pages

# Numeric spot-checks written alongside the book (checks/*.py), one assertion set per checkpoint.
verify:
	python3 $(SCRIPTS)/run_checks.py checks

clean:
	rm -rf build $(OUT)
