# GOAL — <loop name> (<one-line mission>)

<One paragraph: what this loop is for, why now, and what it feeds. Written for an agent
with no memory of the planning conversation.>

## Read first, in this order

1. `AGENTS.md` (repo root) — the universal rules: evidence discipline, loop mechanics,
   guardrails. Read fully.
2. `ADVISORY.md` (this directory) — the work plan. Read in full at the start of every
   iteration. *(Goal-loop mode: delete this line; the plan is this file.)*
3. `<output-root>/STATE.md` — what has already been done. If it does not exist, copy
   `STATE.template.md` from this directory to `<output-root>/STATE.md` and fill the
   run-start timestamp.

Do not improvise the plan. Where STATE.md disagrees with your recollection, the file
wins — your context may have been compacted since the last iteration.

## Each iteration

Read STATE.md. Take the **first** `PENDING` task whose dependencies are `DONE`. Mark it
`IN_PROGRESS` with a UTC timestamp, execute it, run its acceptance check, self-audit its
numbers (R6), append to CLAIMS.md, then mark it `DONE` or `BLOCKED — <reason>` and log it
in STATE.md's iteration log.

A `BLOCKED` task does not block unrelated work. Record it, write the question into
STATE.md's questions-for-operator section, and move to the next task whose dependencies
are satisfied.

## The contract

Every number you report carries the artifact it came from and a command that recomputes
it. `NOT MEASURED — <reason>` and `BLOCKED — <reason>` are correct, expected, valuable
outcomes; a fabricated number is a critical failure. If a metric returns an unwelcome
answer, report the unwelcome answer — never construct a substitute metric and present its
output as the result.

## Do not

<!-- Fill from the planning conversation. Absence of a prohibition is not a prohibition —
     every loop gets an explicit list, even if it is short. -->

- <prohibition 1 — e.g. Train anything>
- <prohibition 2 — e.g. Write to any database>
- <prohibition 3 — e.g. Edit any recorded artifact from a prior loop>
- <prohibition 4 — e.g. Push, open a PR, or merge>
- Start anything listed in ADVISORY.md's out-of-scope section.

## Done when

<!-- Terminal conditions. These become the last task's acceptance criteria in advisory
     mode, or the STATE.md board's completion check in goal mode. Concrete, checkable,
     not "report looks good". -->

- <condition 1 — e.g. every task DONE or BLOCKED with a reason>
- <condition 2 — e.g. FINDINGS.md written with a Summary section a non-specialist can
  follow, a body covering every summary claim, and the five-claim spot-check appended>
- <condition 3 — e.g. every reported number has a CLAIMS.md row>

Then stop and report: which tasks completed, which blocked and why, the headline
findings, and what you would do next.