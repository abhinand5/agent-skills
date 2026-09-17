# AGENTS.md template

Created at repo root by the autoresearch skill when the repo has no `AGENTS.md`. Filled
interactively with the operator — the bracketed sections need repo-specific answers that
the skill must not guess.

Never committed. This file is the operator's local pointer file: it tells any agent
(which loop is active, where its artifacts live) and carries the universal loop rules.

---

# AGENTS.md — autoresearch pointer file

> **What this file is:** the repo-root pointer the autoresearch skill reads and updates.
> It carries (1) the universal loop rules, (2) which loop is currently active and where
> its artifacts live. It is **never committed**.
>
> **How to update:** when a new loop starts, replace only the "Current loop" section.
> The universal rules change rarely — when they do, the change should trace to a
> specific failure, not a preference.

---

## Current loop

- **Loop:** `<loopName>`
- **Mission:** <one sentence>
- **Artifacts:** `<loop-root>/<loopName>/` (GOAL.md, ADVISORY.md, STATE.template.md)
- **Run state:** `<output-root>/<loopName>/STATE.md`
- **Outputs:** `<output-root>/<loopName>/<task-id>/`
- **Claims:** `<output-root>/<loopName>/CLAIMS.md`
- **Style:** <advisory | goal>
- **Started:** <UTC date>

---

## Universal rules

<The evidence-discipline (R1–R10), loop-mechanics, guardrails, and "when you are unsure"
sections, verbatim from the skill's agents-template.md. Do not paraphrase — the rules
carry their history in their exact wording.>

---

## Prior loops

| loop | outcome | findings |
|---|---|---|
| | | |

---

## Fill-in checklist (delete this section once filled)

- [ ] Loop root confirmed with operator (default `temp/<loopName>/`)
- [ ] Output root confirmed with operator (default `temp/outputs/<loopName>/`)
- [ ] Any repo-specific guardrails captured (prod DBs, GPU constraints, gated paths)
- [ ] Operator confirmed AGENTS.md stays uncommitted (add to .gitignore if desired)