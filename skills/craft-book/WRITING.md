# Writing: how a chapter is built and what makes it trustworthy

## Sources first

- Before drafting a chapter, list the primary sources it rests on (textbook chapters,
  original papers, official docs, lecture notes) in the workspace `RESOURCES.md` or
  `references.bib`. Fetch current docs with the documentation tools when a library or
  API is involved. Do not derive a stated theorem from memory alone; check it against
  a source and cite it.
- Cite with `[@key]` (Markdown-first) or `\cite{key}` (LaTeX-first). Every chapter ends
  with a *Read deeper* line pointing at 1–3 sources with chapter/section numbers.

## Chapter anatomy (in this order, most chapters)

1. **Opening paragraph** — what question this chapter answers and why it persists
   beyond any single algorithm/tool.
2. **Mental model** callout — the one picture to carry.
3. **Development** — definitions with conditions, then the central derivation. Prefer
   the shortest honest derivation; when a full proof would defeat the compact purpose,
   state the result, its conditions, and where the proof lives.
4. **Worked example** callout — small, concrete numbers computed to the end. Every
   chapter that introduces a formula has at least one. Each number gets a line in
   `checks/`.
5. **Failure mode** callout — how this idea breaks in practice and what evidence
   distinguishes the failure from neighbouring ones.
6. **Algorithm** callout when a procedure is the point — inputs, loop, stopping rule.
7. **Checkpoint** — 2–4 exercises: one recall, one derivation, one judgement. Answers go
   in the back matter in full, not as hints.
8. **What survives** callout — three sentences the reader should be able to reproduce.
9. **Read deeper** line.

Appendices (refreshers) use the same anatomy but lead with intuition and a visual only
where geometry genuinely clarifies; if a visual becomes hard, drop it.

## The conditions rule

Every identity, theorem, or "always/never" statement carries its conditions in the same
sentence or display: finite/infinite, discounted/undiscounted, bounded, i.i.d., on-policy,
tabular vs approximate, etc. Refuse slogans ("X has lower variance") unless qualified.
Where a common belief is false, say so with the smallest counterexample.

## The residue rule

The reader never sees your notes, earlier drafts, or the book you are improving on.
Never write "not a counterexample", "unlike the earlier claim", or refute an error the
text never stated. State the correct thing positively, with the pitfall named.

## Numbers are code

For each worked example and each numeric checkpoint answer, add a few lines to
`checks/NN-topic.py` that recompute the value and `assert` it (see the template). If a
number changes in the prose, the check must change; `make verify` runs them all.

## Voice and typography

- Second person sparingly, first person plural for shared derivations, no hype.
- British or American spelling per the brief; be consistent (the `lang` field).
- Bold for defined terms at first use; italics for emphasis; small caps only in macros.
- One idea per paragraph; paragraphs ≤ 6 lines on a 7×10 page.
- Tables: pipe tables (Markdown) or `tabularx` with `l/c/r/p/X` columns (LaTeX).
- Figures: SVG in `assets/` with real alt text. LaTeX-first: TikZ for print + SVG twin
  inside `\begin{epubonly}`.
- Maths: `$…$` / `$$…$$` in Markdown; `\[ \]` and `align*` in LaTeX. The preamble
  defines `\E \Var \argmax \argmin \R \Prob \norm \abs`; add project macros there, not inline.

## Page budget discipline

Track pages per chapter against the brief after every build (`make pdf` prints the
count). When over budget, cut whole subsections rather than compressing prose into
density; move detail to *Read deeper*.

## Revision mode

When asked to revise an existing book: re-read `BOOK-BRIEF.md` and the profile, ask
only what changed, edit the source, rebuild all editions, re-run `make verify`, and add
a dated line to `ERRATA.md` for any corrected error. Keep `identifier` stable so Kindle
treats it as the same book.
