---
name: autoresearch
description: "Run long-horizon autonomous research/agent loops with durable memory and evidence discipline. Use when the user wants to: initialize a research loop, start a new loop, generate loop artifacts (GOAL.md, ADVISORY.md, STATE.md), draft a GOAL for a phase, write an advisory/task-DAG for a loop, close out a loop, write FINDINGS from CLAIMS, spot-check loop claims, or asks about agent loop mechanics. Not for executing the loop's tasks themselves."
argument-hint: "<loopName> [--close | --reset]"
---

# Autoresearch

Turns a planning conversation into a durable, resumable autonomous loop — and a finished
loop into evidence its successor can trust. Every loop's output includes a **Summary**
in FINDINGS.md: a detailed, easy-to-follow TL;DR any human can read instead of combing
through the full artifact set — never instead of it.

## What This Skill Does

Three workflows, selected by where the conversation is:

1. **Init** (default) — the user has been planning; they say go. You generate the loop's
   artifact set: `GOAL.md`, `ADVISORY.md` (optional — see Modes), `STATE.template.md`,
   and a placeholder `STATE.md`. The loop is then executable by any agent, including a
   fresh-context one, without re-reading this conversation.
2. **Close** (`--close`) — the loop's tasks are done. You verify the artifact set is
   complete and consistent (STATE all-terminal, CLAIMS covers reported numbers, FINDINGS
   exists with its spot-check), then surface closure to the user. You do not write
   FINDINGS for the agent — you check it and report gaps.
3. **Reset** (`--reset`) — the loop is closed and you are about to plan the next one.
   You move the finished loop's pointer into AGENTS.md's Prior loops table and clear the
   Current loop section, so the next init starts from a clean pointer. The only workflow
   that writes to AGENTS.md outside of init.

All three are file operations plus reading. None launches training, touches databases,
or executes the loop's tasks.

## When to Use

- "Start/init a new loop for X" / "set up the loop artifacts"
- "Write the GOAL/ADVISORY for what we just planned"
- "Spin up loop N with the tasks we discussed"
- "Close out this loop" / "check the loop is complete"
- "Reset the loop pointer" / "we're starting the next loop, clear the current one"
- "What does the loop need before an agent can run it unattended?"

## Modes

Two loop styles exist. Ask the user which, or infer from what they hand you:

| | Goal loop | Advisory loop |
|---|---|---|
| Trigger | user has a goal, no task breakdown | user has a goal *and* a task DAG |
| Artifacts | `GOAL.md`, `STATE.template.md` | `GOAL.md`, `ADVISORY.md`, `STATE.template.md` |
| Plan lives in | GOAL.md itself (mission + constraints + done-when) | ADVISORY.md (task table, per-task acceptance, prohibitions) |
| STATE board | filled from GOAL's done-when criteria | filled from ADVISORY's task table |
| Use when | work is exploratory, tasks can't be enumerated up front | work is known, tasks are orderable, acceptance is checkable |

If unsure, ask. Advisory loops are stronger when they fit; goal loops are stronger when
the work is genuinely open.

---

## Init Workflow

### Step 1 — Resolve the loop name

If the user passed `<loopName>`, use it. Otherwise infer from the conversation (a phase
name, a research question short-name) and **confirm with the user before writing**.

Convention: short, lowercase, no spaces — `rl_p7`, `fidelity_audit`, `retrieval_probe`.

### Step 2 — Read the current AGENTS.md pointers

`AGENTS.md` at repo root carries the universal rules and a **Current loop** pointer
section. Read it. If it doesn't exist, STOP and create it first from
[references/agents-template.md](./references/agents-template.md), filling the repo-specific
bits (loop root, output root, evidence rules) with the user — do not guess.

The pointer section in AGENTS.md must name this loop. If it names a different (older)
loop, that loop was never reset — offer `--reset` for it first (its outcome row belongs
in Prior loops), then proceed. If the user declines, overwrite the pointer and say so.

### Step 3 — Harvest the planning conversation

Extract from the conversation (or ask the user for):

- **Mission** — one paragraph, what this loop is for and why now.
- **Done-when** — the conditions under which the loop stops. These become GOAL's done-when
  and, in advisory mode, the last task's acceptance criteria.
- **Known facts** — measured numbers, verified paths, prior-loop conclusions the loop
  builds on. Each must carry its artifact (file path) or be marked unverified.
- **Prohibitions** — what the loop must not do (no training, no DB writes, read-only
  paths, out-of-scope axes).
- **Environment** — venv paths, model paths, GPU constraints, DB DSNs the loop needs.
  Only include what's verified this session.

### Step 4 — Generate artifacts

Write to the loop root (default `temp/<loopName>/`; confirm if the repo uses a different
convention):

**GOAL.md** — from [references/goal-template.md](./references/goal-template.md). Mission,
read-first order, per-iteration ritual, the contract (evidence rules pointer + the
non-negotiables restated in one paragraph), do-not list, done-when.

**ADVISORY.md** (advisory mode only) — from
[references/advisory-template.md](./references/advisory-template.md). The task DAG with
per-task: id, what/why, GPU cost, dependencies, acceptance criteria, expected artifact
paths. The **final task is always the findings-and-closure task**, which writes
FINDINGS.md. Include the failure-modes section — it is the highest-leverage part of the
document and the most often skipped.

**STATE.template.md** — from
[references/state-template.md](./references/state-template.md). Task board matching the
ADVISORY task table (or GOAL's done-when criteria in goal mode), key-values table,
checklist section, iteration log (whose per-task Headline lines are the raw material
the closure summary is written from), blocked-items table, questions-for-operator
section, deviations section, and a closure-summary-feed table filled at loop end.

**FINDINGS structure** — [references/findings-template.md](./references/findings-template.md),
referenced by the closure task in ADVISORY.md (advisory mode) or the done-when in
GOAL.md (goal mode). The loop agent writes FINDINGS.md at closure following it; the
skill does not write the file itself.

### Step 5 — Verify the set is self-sufficient

Read back what you wrote and answer, honestly:

- Could an agent with **no memory of this conversation** pick up STATE.md and make
  progress? If any task depends on context that lives only in this chat, it's not written
  down yet — fix that before finishing.
- Does every task have an acceptance check? (Not "looks good" — a command, a file
  existence check, a number with a denominator.)
- Does every measured number the loop builds on carry its artifact path?
- Are the prohibitions explicit? (Absence of a prohibition is not a prohibition.)
- Does the artifact set carry the summary requirement? — the closure task (or
  goal-mode done-when) names the FINDINGS Summary section, and STATE's iteration-log
  headline guidance + closure-summary-feed table exist so the summary can be written
  from evidence rather than memory at loop end.

If any answer is no, fix it or flag it to the user — do not ship a half-specified loop.

---

## Close Workflow (`--close`)

Run only when the user says the loop's work is done. You are auditing, not finishing:

1. **STATE.md terminal check** — every task is `DONE` or `BLOCKED — <reason>`. No
   `IN_PROGRESS` (a wake-completion that wasn't logged), no `PENDING` (a task that was
   silently dropped).
2. **CLAIMS.md coverage** — every number in FINDINGS.md (if it exists) or the final
   report traces to a CLAIMS row with artifact + recompute command.
3. **FINDINGS.md exists with a human-readable Summary** — the file opens with a Summary
   section (the question, what we did, what we found, what it means, what did not work)
   that a person who reads nothing else can follow; every summary claim exists in more
   detail in the body; the five-claim spot-check is appended (five claims, re-run
   commands, results). If missing or hollow — a summary that names no numbers, or body
   claims absent from the summary — report it as a gap; do not write it yourself.
4. **Blocked items resolved or escalated** — every BLOCKED task either has a follow-up
   owner or is a question the user still owes an answer on.
5. **Questions-for-operator answered** — STATE.md's questions-for-operator items either
   answered in the conversation or carried forward explicitly.

Report: what's complete, what's gapped, what carries forward. Do not edit the loop's
artifacts — the loop owns them; you audit them.

**`--close` does not reset AGENTS.md.** The Close audit reads the loop's artifacts and
reports; it never writes. Resetting the pointer for the next loop is a separate step —
see the Reset workflow below — because the two have different preconditions: close can
run on a messy loop (that is when it is most useful), reset runs only on a finished one.

---

## Reset Workflow (`--reset`)

Run when a loop is finished and you are about to plan the next one. This is the only
workflow that writes to AGENTS.md outside of init.

**Precondition: the loop is actually closed.** Run `--close` first (or satisfy yourself
the loop is done). Resetting a half-finished loop orphans its state — the next agent
reads AGENTS.md, finds no pointer to the running loop, and starts over. If `--close`
was not run, ask whether to run it first.

**What it does:**

1. **Move the finished loop's pointer into Prior loops.** Append one row to AGENTS.md's
   Prior loops table: loop name, one-sentence outcome (from FINDINGS.md's Summary if it
   exists — that is what it is for), and the path to its FINDINGS.md. Append-only; the
   table is the program's memory across loops.
2. **Clear the Current loop section.** Replace the pointer with the unset placeholder:
   loop name `<none>`, mission `<none>`, artifacts/run-state/outputs/claims pointing at
   the placeholder shapes, style `<none>`, started `<none>`.
3. **Leave everything else untouched.** Universal rules stay. Prior loops stay. The
   finished loop's artifacts under `temp/` stay exactly where they are — reset changes
   the pointer, never the artifacts.

**After reset:** AGENTS.md shows no active loop. The next `autoresearch <loopName>`
init fills the Current loop section fresh.

**What reset does NOT do:**

- **Delete or archive anything.** The finished loop's artifacts stay on disk. Cleanup
  (tarballs, S3, deletion) is the operator's call, made explicitly, never a side effect.
- **Modify the finished loop's artifacts.** FINDINGS.md, STATE.md, CLAIMS.md are
  read-only to this workflow — same rule as `--close`.
- **Start the next loop.** Reset is preparation; init is a separate, user-driven step.

---

## What This Skill Does NOT Do

- **Execute the loop.** Running tasks, training models, querying databases — that's the
  loop agent's job, not this skill's.
- **Write FINDINGS.md.** The loop agent writes it; this skill audits it.
- **Set research direction.** The user plans; this skill crystallizes the plan into
  artifacts. If the plan is unclear, ask — do not invent tasks.
- **Commit anything.** Artifacts under `temp/` are typically gitignored; AGENTS.md is
  never committed (it's the operator's local pointer file). Leave VCS state alone unless
  the user explicitly asks.

## Failure Modes to Avoid

1. **Inventing tasks the user didn't plan.** The skill crystallizes; it doesn't design.
   If the DAG has a hole, ask.
2. **Unverified environment facts.** Every path, venv, model path in the generated
   artifacts either was verified this session or is marked unverified. Carry-forward from
   a prior loop counts only if the prior loop's artifact is cited.
3. **Skipping the prohibitions section.** Every loop needs an explicit do-not list. The
   failure mode it prevents (silent scope creep, DB writes, training without a gate) is
   the most expensive one.
4. **Acceptance criteria that can't be checked.** "Report looks good" is not acceptance.
   Force a command, a file, or a number with a denominator.
5. **Losing the failure-modes section.** ADVISORY's failure-modes section is what
   makes loop N+1 better than loop N. Generate it from the planning conversation's
   known risks, or from the prior loop's FINDINGS "what went wrong" section.
6. **Resetting an unreset pointer at init.** If init finds AGENTS.md pointing at an
   old loop, that loop's outcome row never made it into Prior loops — offer `--reset`
   first, so the program's memory table stays complete. Overwriting the pointer without
   asking loses that row permanently.