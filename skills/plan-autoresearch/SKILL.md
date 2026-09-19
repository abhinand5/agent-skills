---
name: plan-autoresearch
description: "Research-planning conversation that precedes an autoresearch loop. Interviews the user about the question, stress-tests the plan against a fixed checklist (decidability, cheapest kill, unwelcome result, confounds, evidence audit, budget, scope), proposes alternatives, fills knowledge gaps from the repo's prior loops, and ends with an in-chat plan brief shaped exactly for `autoresearch` init. Writes no files. Use when the user wants to plan a research loop, asks whether a loop is worth running, wants a research plan stress-tested or grilled, or is about to start autoresearch on a plan that has not been examined; also with --quick to stress-test an existing plan without the interview."
argument-hint: "<what you want to find out> [--quick]"
---

# plan-autoresearch

An autoresearch loop is expensive and runs unattended, so it can only be as good as the
plan that goes in. This skill is the conversation before `autoresearch <name>`: it makes
the plan exist, makes it survive scrutiny, and hands it over in the shape init harvests.
It produces **no files** — the output is the conversation and a final plan brief in chat.

Two modes:

- **Full** (default) — ground, interview, stress-test, brief.
- **`--quick`** — the user already has a plan. Skip the interview; ground, run the stress
  tests against the plan as stated, report what fails, and emit the brief.

## 1. Ground yourself first

Before asking anything, read what the repo already knows. Explore instead of asking
whenever the answer is on disk:

- `AGENTS.md` at repo root — the Prior loops table and the Current loop pointer. An
  unreset pointer means a loop is still open; say so.
- Every prior `FINDINGS.md` those rows point at — especially the Summary and "what did
  not work" sections. The new loop must not re-run a settled question or repeat a
  recorded failure.
- Every artifact path the user cites. Confirm it exists. A number without a path is
  unverified and gets said so in the brief.

Web search only when a claim about the literature or a tool would change the plan's
direction — and say when you are doing it. The plan is grounded in the user's evidence,
not in generic search results.

## 2. Interview

One question at a time, each with your recommended answer and the reason. Walk the
decision tree; resolve dependencies in order. What the interview must establish — this is
what `autoresearch` init harvests:

1. **The decision this loop feeds.** If the answer is X, we do A; if Y, we do B. A loop
   whose outcome changes no decision is not worth running.
2. **Mission** — one paragraph, why now, what it builds on.
3. **Done-when** — checkable terminal conditions: a command, a file, a number with a
   denominator. Not "results look good".
4. **Known facts** — with artifact paths, or marked unverified.
5. **Prohibitions** — the do-not list. Absence of a prohibition is not a prohibition.
6. **Environment** — venvs, model paths, GPUs, DSNs; only what is verified.
7. **Tasks** — if the work can be enumerated (advisory mode) or why it cannot (goal mode).
8. **Out of scope** — what is deliberately excluded and why.

Along the way, do the work a good collaborator does: propose at least one alternative
approach and at least one cheaper experiment, and name concepts or prior results the
user seems not to have in view. Explain them; do not just cite them.

## 3. Stress tests

Every plan passes each of these, or the user explicitly waives it and the waiver is
recorded in the brief. Do not emit the brief until each has a verdict.

| Test | The question | Passes when |
|---|---|---|
| Decidability | Which decision changes on which outcome? | Both branches named, both actionable. |
| Cheapest kill | What is the smallest experiment that could falsify the idea? | It is the first task, or there is a reason it is not. |
| Unwelcome result | What happens if the answer is no, or null? | A plan exists for it; the loop is not designed to only confirm. |
| Confounds & baselines | What else could produce the same signal? What is it compared to? | Each confound has a control or is listed as a caveat; baseline named. |
| Evidence audit | Are the known facts actually verified? | Every number has a path that exists, or is marked unverified. |
| Budget & stop rule | Compute, time, cost cap? When is the loop abandoned early? | A cap and an abandon condition are stated. |
| Scope fence | What will the loop be tempted to do that it must not? | Out-of-scope table and prohibitions are populated. |

## 4. Disagreement

When you think the user is wrong, say so once, with the evidence, and give your
recommended alternative. If they hold their position, it is their call: comply, do not
re-litigate, do not hedge the rest of the plan around it. Record the overruled objection
in the brief's failure modes as a named risk with a detection signal — "if X is observed,
this is that objection materialising" — so the loop can catch it. The symmetric rule
applies: when you have no strong view, say so rather than manufacturing one.

## 5. The plan brief

When every stress test has a verdict and the user says the plan is settled, emit the
brief in chat following [references/plan-brief.md](./references/plan-brief.md). It
mirrors init's harvest list one-to-one, adds the stress-test verdicts and failure modes,
recommends goal vs advisory mode with a reason, and suggests a loop name.

Then stop and say: run `/autoresearch <name>` to crystallise it. In the same session init
reads the brief directly; in a new session the user pastes it.

## What this skill does not do

- **Write files.** No PLAN.md, no GOAL.md, no edits to AGENTS.md. That is init's job.
- **Invoke autoresearch.** The user reviews the brief and says go.
- **Run experiments** or execute anything from the plan.
- **Invent tasks silently.** Alternatives are proposed and labelled as yours; the user
  chooses what enters the plan.

## Failure modes to avoid

1. Asking what the repo already answers. Read AGENTS.md and prior FINDINGS first.
2. Emitting a brief with an untested plan. Every stress test gets a verdict or a waiver.
3. Re-litigating an overruled objection. Once, with evidence, then record it and move on.
4. Confirmatory design. If the plan has no path for an unwelcome result, it fails.
5. Brief drift. The brief's sections match init's harvest list; do not rename or merge them.
