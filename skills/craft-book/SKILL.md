---
name: craft-book
description: Write a personalised technical book (field guide, course companion, prerequisite refresher, study spine) and ship it as a print PDF, a Kindle-ready EPUB, and portable Markdown from one source, after probing the reader's intent and verified skill level. Use when the user asks for a book, textbook, study guide, companion, refresher, field guide, "something I can read on my Kindle", or wants existing notes turned into a proper book; also for revising or re-exporting a book built with this skill.
---

# craft-book

Books built here are for one named reader. Their purpose is transferable judgement,
not coverage: short enough to finish, correct enough to trust, and shaped by what the
reader already knows. The stateful artefacts are the learner profile
(`~/.agents/books/learner-profile.md`), a `BOOK-BRIEF.md` in the workspace, and the
book source itself.

## Workflow

1. **Probe** — follow [INTAKE.md](INTAKE.md). `scripts/profile.py show` first and only
   probe the delta (reconfirm anything flagged stale). Interview one question at a time
   with a recommended answer, run the short diagnostic, then write `BOOK-BRIEF.md` and
   get it approved. Do not write chapters before the brief is approved.
2. **Scaffold** — pick the pipeline with the rule in [PIPELINES.md](PIPELINES.md)
   (default Markdown-first), then
   `python3 ~/.agents/skills/craft-book/scripts/new_book.py --pipeline markdown --dest DIR --title "..."`.
   The sample chapters show every supported construct; replace them, never start blank.
3. **Write** — follow [WRITING.md](WRITING.md): the chapter anatomy, the conditions
   rule, worked numbers, and the residue rule. Gather sources first; cite primary ones.
   Write `checks/NN-topic.py` for every number in a worked example or answer.
4. **Build and verify** — `make` builds and checks all requested editions;
   `make verify` runs the numeric checks; `make pages` renders contact sheets. Then do
   the visual and correctness passes in [QA.md](QA.md). Nothing ships on a green
   checker alone: look at the pages.
5. **Deliver** — hand over the requested files from `output/`, a `READING-PLAN.md`
   keyed to the reader's timeline, and record the book and its verified levels with
   `profile.py`. Offer a Send-to-Kindle test and the self-test companion.

## Quick start

```sh
python3 ~/.agents/skills/craft-book/scripts/new_book.py --pipeline markdown \
  --dest my-book --title "The Probability Spine" --author "Prepared for Sam"
cd my-book && make && make verify && make pages
```

## Non-negotiables

- One source, every edition. Never hand-edit an output file.
- Every identity states its conditions; every number has a check; no claim rests on
  parametric memory alone when a primary source is available.
- Page budget is part of the brief (default 40–60 pages of 7×10 in). Cutting is the
  writer's job, not the reader's.
- Callouts are the six defined classes only: mentalmodel, failuremode, checkpoint,
  takeaway, example, algorithm. Answers to every checkpoint live in the back matter.
- The Kindle contract in [PIPELINES.md](PIPELINES.md) is binding whenever EPUB is requested.
- Read every page render before delivery; fix what the checkers cannot see.
- The learner profile evolves itself: apply the triggers in [PROFILE.md](PROFILE.md)
  through `scripts/profile.py` (never by rewriting the file), silently, and honour
  "leave my profile alone" for a task via `CRAFT_BOOK_PROFILE=off`.

## Files

- `scripts/` — `new_book.py` scaffold; `profile.py` (learner-profile edits + log);
  `check_pdf.py`, `check_epub.py`, `check_markdown.py`, `polish_epub.py`,
  `count_tables.py`, `contact_sheet.sh`, `run_checks.py` (shared by both pipelines).
- `templates/markdown-first/`, `templates/latex-first/` — complete, buildable sample books.
- `templates/profile/learner-profile.md`, `templates/BOOK-BRIEF.md`, `templates/READING-PLAN.md`.
