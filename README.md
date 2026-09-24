# agent-skills

Skills I use with Claude Code and Codex. Each skill is a folder under `skills/` with a
`SKILL.md` (instructions), optional reference docs, scripts, and templates.

## Available skills

| Skill | What it does | Reach for it when |
| --- | --- | --- |
| [craft-book](skills/craft-book) | Writes a personalised technical book for one named reader and ships it as print PDF, Kindle EPUB, and Markdown from a single source, behind a conversion QA gate. | You want a book, textbook, study guide, refresher, or "something I can read on my Kindle" — or want existing notes turned into one. |
| [kindle-pdf-reflow](skills/kindle-pdf-reflow) | Reflows a PDF book into a Paperwhite-sized PDF using a device-approved size-3 profile, preserving equations, figures, typography, searchable text, and bookmarks. | An existing PDF is painful to read on a Kindle and you want a 16-page trial before converting the whole book. |
| [plan-autoresearch](skills/plan-autoresearch) | The planning conversation before an autoresearch loop: interviews you, stress-tests the plan against seven fixed checks, proposes cheaper alternatives, and ends with an in-chat plan brief. Writes no files. | You want a research loop planned, or an existing plan grilled — `--quick` skips the interview. |
| [autoresearch](skills/autoresearch) | Turns a plan into a durable, resumable autonomous loop (`GOAL.md`, `ADVISORY.md`, `STATE.md`, `AGENTS.md`) and audits or resets a finished loop (`--close`, `--reset`). | You are starting a loop, closing one out, or resetting for the next one. It never runs the loop's tasks itself. |
| [virtual-ta](skills/virtual-ta) | A learning-focused TA stance: explains concepts fully, asks before answering, gives progressive hints, and withholds graded solutions entirely in graded mode. | You are working through your own coursework or self-study and want to understand it, not have it done for you. |

## Skill details

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

### [plan-autoresearch](skills/plan-autoresearch)

The conversation before an autoresearch loop. Grounds itself in the repo first
(`AGENTS.md` prior loops, earlier `FINDINGS.md`, every cited artifact path), then
interviews you one question at a time to establish exactly what `autoresearch` init
harvests — the decision the loop feeds, mission, checkable done-when, known facts with
paths, prohibitions, environment, tasks, out-of-scope. Every plan must pass (or you must
explicitly waive) seven stress tests: decidability, cheapest kill, unwelcome result,
confounds & baselines, evidence audit, budget & stop rule, scope fence. It proposes
alternatives and cheaper experiments, states disagreement once with evidence and then
complies, recording the overruled objection as a named risk. Ends with an in-chat plan
brief and a mode/loop-name recommendation; writes no files. `--quick` skips the
interview and just stress-tests a plan you already have.

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

#### Using the two together on a research project

The pair is a loop lifecycle. One loop answers one question; the program's memory is the
chain of `FINDINGS.md` files linked from `AGENTS.md`.

1. **Plan** — `/plan-autoresearch <question>`. Answer the interview, let it read your
   prior loops, and do not skip the stress tests: *cheapest kill* and *unwelcome result*
   are the two that save the most GPU-hours. If you already have a plan, `--quick`.
2. **Init** — `/autoresearch <loop_name>` in the same session (or paste the brief). Take
   advisory mode when the tasks are enumerable and each has a checkable acceptance;
   goal mode when the work is genuinely exploratory. Read the generated `ADVISORY.md`
   failure-modes section before running — it is the part that stops loop N+1 repeating
   loop N's mistakes.
3. **Run** — start a fresh agent session in the repo and tell it to read `AGENTS.md` and
   begin. Iterations are file-driven, so context compaction and restarts are safe: the
   agent re-reads `STATE.md`, takes the first `PENDING` task whose deps are `DONE`, and
   continues. Check `STATE.md`'s questions-for-operator section between wakes.
4. **Close** — `/autoresearch <loop_name> --close` when the board is all `DONE` /
   `BLOCKED`. It audits; it does not finish for the agent. Gaps go back to the loop.
5. **Reset, then plan the next one** — `/autoresearch <loop_name> --reset` moves the
   outcome into Prior loops. The next `/plan-autoresearch` reads that row and the
   FINDINGS it points at, so each loop starts where the last one ended.

Habits that keep AI/ML loops honest: gate every training or GPU task behind an explicit
acceptance check on the cheaper task before it; make the baseline a task, not an
assumption; write `NOT MEASURED — <reason>` rather than a substitute metric; keep
`AGENTS.md` and `temp/` out of git.

### [virtual-ta](skills/virtual-ta)

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
ln -s ~/dev/agent-skills/skills/plan-autoresearch ~/.agents/skills/plan-autoresearch
ln -s ~/dev/agent-skills/skills/autoresearch ~/.agents/skills/autoresearch
ln -s ~/dev/agent-skills/skills/virtual-ta ~/.agents/skills/virtual-ta
```

## Licence

MIT — see [LICENSE](LICENSE).
