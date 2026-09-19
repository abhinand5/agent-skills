# agent-skills

Skills I use with Claude Code and Codex. Each skill is a folder under `skills/` with a
`SKILL.md` (instructions), optional reference docs, scripts, and templates.

## Skills

### [craft-book](skills/craft-book)

Write a personalised technical book — field guide, course companion, prerequisite
refresher — and ship it as a print PDF, a Kindle-ready EPUB, and portable Markdown from
one source. The skill first probes the reader's intent and *verified* skill level (a
grill-me-style interview plus a short diagnostic), keeps a self-evolving learner
profile across books, and enforces a QA gate that catches the silent conversion damage
pandoc and e-readers are prone to (flattened tables, un-backslashed control words in
maths, un-centred MathML, missing chapter titles).

Two buildable pipelines are included — Markdown-first (default) and LaTeX-first — with a
scaffold script, checkers for all three editions, a numeric-check runner, and contact
sheets for visual review. Requires pandoc ≥ 3, a TeX Live with LuaLaTeX, rsvg-convert,
poppler, python3, and optionally ImageMagick.

```sh
python3 ~/.agents/skills/craft-book/scripts/new_book.py --pipeline markdown \
  --dest my-book --title "The Probability Spine"
cd my-book && make && make verify && make pages
```

### [kindle-pdf-reflow](skills/kindle-pdf-reflow)

Convert PDF books into visually reflowed, Paperwhite-sized PDFs using a calibrated
Kindle size-3 profile. The workflow creates a representative 16-source-page trial,
waits for on-device approval, then builds and verifies the complete book while
preserving printed equations, figures, typography, searchable text, and bookmarks.

Requires Python 3, PyMuPDF, k2pdfopt 2.55 or compatible, and NumPy for deep
verification. The converter can be supplied with `--k2pdfopt`, `K2PDFOPT_BIN`,
`PATH`, or a project's `tools/vendor/k2pdfopt`.

### [autoresearch](skills/autoresearch)

Turn a planning conversation into a durable, resumable autonomous research loop, and a
finished loop into evidence its successor can trust. Three file-only workflows, selected
by where the conversation is: **init** (default) crystallises the plan into `GOAL.md`,
an optional `ADVISORY.md` task DAG, `STATE.template.md`, and the repo-root `AGENTS.md`
pointer; **`--close`** audits a finished loop (STATE all-terminal, every reported number
traceable through `CLAIMS.md`, `FINDINGS.md` present with a human-readable Summary and
the five-claim spot-check) and reports gaps without editing anything; **`--reset`** moves
the finished loop's one-line outcome into `AGENTS.md`'s Prior loops table and clears the
current pointer for the next loop.

Artifact templates live in `references/` and are the whole contract — every task carries
a checkable acceptance criterion, every number carries the artifact it came from plus a
command that recomputes it, and `NOT MEASURED — <reason>` is an expected, valuable
result. The skill never executes the loop's tasks, never writes `FINDINGS.md` itself,
and never commits.

### [teaching-assistant](skills/teaching-assistant)

A learning-focused TA stance for working through your own coursework or self-study.
Invoked by name, it asks once whether the work is graded or self-study, then explains
concepts fully, asks before answering, and gives progressive hints. In **graded** mode
it never completes graded work for you — pseudocode and minor localised fixes only,
holding the line even on insistence and offering an understanding check instead. In
**self-study** mode it stays Socratic-first but hands over real code and full solutions
once you have engaged or ask. The same rules map onto proofs, problem sets, and written
reports. Stateless: nothing is written to disk.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add abhinand5/agent-skills
```

Or by hand — clone and symlink the skills you want into your agent's skills directory:

```sh
git clone https://github.com/abhinand5/agent-skills ~/dev/agent-skills
ln -s ~/dev/agent-skills/skills/craft-book ~/.agents/skills/craft-book   # Codex / shared
ln -s ~/.agents/skills/craft-book ~/.claude/skills/craft-book             # Claude Code
ln -s ~/dev/agent-skills/skills/kindle-pdf-reflow ~/.agents/skills/kindle-pdf-reflow
ln -s ~/dev/agent-skills/skills/autoresearch ~/.agents/skills/autoresearch
ln -s ~/dev/agent-skills/skills/teaching-assistant ~/.agents/skills/teaching-assistant
```

## Licence

MIT — see [LICENSE](LICENSE).
