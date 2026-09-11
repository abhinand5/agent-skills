# craft-book: LaTeX-first pipeline. Hand-set LaTeX for print; EPUB + Markdown derived by pandoc.
#   make            -> PDF + EPUB + Markdown, each checked
#   make pdf | epub | md | check | pages | verify | clean
#
# LaTeX constructs that survive pandoc: tabularx with l/c/r/p/X columns (NOT custom
# column types), tcolorbox environments declared in style.tex, \cite, \href, amsmath.
# TikZ does not: give every TikZ figure an SVG twin inside \begin{epubonly}.

SHELL := /bin/sh
export TEXMFVAR := $(CURDIR)/.texmf-var
export TEXMFCACHE := $(CURDIR)/.texmf-var

SLUG     ?= book
SKILL    ?= $(HOME)/.agents/skills/craft-book
SCRIPTS  := $(SKILL)/scripts
SOURCES  := book.tex style.tex frontmatter.tex $(wildcard chapters/*.tex) $(wildcard backmatter/*.tex)
OUT      := output
PDF      := $(OUT)/pdf/$(SLUG).pdf
EPUB     := $(OUT)/epub/$(SLUG).epub
MD       := $(OUT)/markdown/$(SLUG).md
COVER    := build/cover.png

.DELETE_ON_ERROR:
.PHONY: all pdf epub md check check-pdf check-epub check-md pages verify clean

all: pdf epub md
pdf: $(PDF)
epub: $(EPUB)
md: $(MD)

build:
	mkdir -p build

$(PDF): $(SOURCES) | build
	lualatex -interaction=nonstopmode -halt-on-error -output-directory=build -jobname=$(SLUG) book.tex >/dev/null
	lualatex -interaction=nonstopmode -halt-on-error -output-directory=build -jobname=$(SLUG) book.tex >/dev/null
	mkdir -p $(OUT)/pdf
	cp build/$(SLUG).pdf $(PDF)
	python3 $(SCRIPTS)/check_pdf.py $(PDF) build/$(SLUG).log

$(COVER): epub/assets/cover.svg | build
	rsvg-convert --width 1600 --height 2560 $< --output $@

$(EPUB): $(SOURCES) epub/metadata.yaml epub/kindle.css epub/filters/book.lua $(wildcard epub/assets/*.svg) $(COVER) | build
	mkdir -p $(OUT)/epub
	pandoc book.tex --from=latex --to=epub3 --output=$(EPUB) \
		--metadata-file=epub/metadata.yaml --css=epub/kindle.css \
		--lua-filter=epub/filters/book.lua --epub-cover-image=$(COVER) \
		--epub-title-page=true --split-level=1 --toc --toc-depth=2 \
		--math-method=mathml --resource-path=.
	python3 $(SCRIPTS)/polish_epub.py $(EPUB)
	python3 $(SCRIPTS)/check_epub.py $(EPUB) --expect-tables $$(python3 $(SCRIPTS)/count_tables.py $(SOURCES))

$(MD): $(SOURCES) epub/metadata.yaml epub/filters/book.lua | build
	mkdir -p $(OUT)/markdown/assets
	pandoc book.tex --from=latex --to=gfm-tex_math_gfm+tex_math_dollars --wrap=none \
		--metadata-file=epub/metadata.yaml --lua-filter=epub/filters/book.lua \
		--lua-filter=$(SKILL)/templates/latex-first/epub/filters/markdown.lua \
		--toc --toc-depth=2 --standalone --template=$(SKILL)/templates/markdown-first/markdown/template.md \
		--resource-path=. --output=$(MD)
	cp -f epub/assets/*.svg $(OUT)/markdown/assets/ 2>/dev/null || true
	python3 $(SCRIPTS)/check_markdown.py $(MD)

check: check-pdf check-epub check-md
check-pdf: $(PDF)
	python3 $(SCRIPTS)/check_pdf.py $(PDF) build/$(SLUG).log
check-epub: $(EPUB)
	python3 $(SCRIPTS)/check_epub.py $(EPUB) --expect-tables $$(python3 $(SCRIPTS)/count_tables.py $(SOURCES))
check-md: $(MD)
	python3 $(SCRIPTS)/check_markdown.py $(MD)

pages: $(PDF)
	sh $(SCRIPTS)/contact_sheet.sh $(PDF) build/pages

verify:
	python3 $(SCRIPTS)/run_checks.py checks

clean:
	rm -rf build $(OUT)
