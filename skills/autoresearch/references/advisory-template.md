# ADVISORY — <loop name>: <one-line work plan>

**Read `AGENTS.md` first** (repo root). It carries the evidence rules, guardrails, and
loop mechanics. This document is the work plan. Read it in full at the start of every
loop iteration.

**Status:** authored <UTC date> from the planning conversation with the operator.
Supersedes nothing / supersedes <prior artifact>, which is retained as read-only evidence.

---

## 1. Where things stand

<Paragraph(s): what the prior loop(s) concluded, what is solid, what is contested, what
this loop builds on. Every number carries its artifact path. What is unverified says so.>

## 2. The question this loop answers

<One paragraph. The decision this loop's output feeds. If the answer were X the next
step would be A; if Y, the next step would be B. This is what makes the loop's output
actionable rather than merely interesting.>

## 3. Ground rules specific to this loop

- <Read-only paths / write paths>
- <Resource constraints: GPU, DB, external services>
- <Sampling/measurement protocol constraints if any>
- <Anything the operator gated>

## 4. Tasks

Each task: run it, meet the acceptance check, self-audit (R6), append claims, update
STATE.md. Do not reorder unless the dependency table says otherwise. The **final task**
is always the findings-and-closure task (pattern below) — it writes FINDINGS.md, whose
Summary section is the loop's human-readable record.

### <TN> — Findings and closure (<GPU | no GPU>, <estimate>)

**Why:** the loop's output is only as good as its record. This task writes the artifact
the next loop and the operator actually read.

**Do:** write `FINDINGS.md` following [the FINDINGS structure](./findings-template.md).
The **Summary** section is mandatory and comes first: the question, what we did, what
we found, what it means, what did not work — plain language, every number with its
denominator and CLAIMS id, honest about failures and blocked tasks. It compresses the
body; it does not replace it. Every summary claim must exist, with more detail, in the
body. Then re-verify: pick five claims spanning the loop's major results, re-run their
recompute commands, and record the results at the end of FINDINGS.md.

**Acceptance:** FINDINGS.md exists with (1) a Summary section a non-specialist can
follow, (2) a body whose sections cover every summary claim, (3) the five-claim
spot-check table appended with actual re-run outputs.

*(Other tasks follow the same pattern: Why / Do / Acceptance. Place them before the
closure task.)*

## 5. Definition of done

- STATE.md — every task `DONE` or `BLOCKED` with a reason.
- CLAIMS.md — every reported number, with artifact and recompute command.
- FINDINGS.md — written per the closing task, following
  [the FINDINGS structure](./findings-template.md): a mandatory **Summary** section
  first (the question, what we did, what we found, what it means, what did not work —
  written so a human who reads nothing else still understands the loop), then the
  full-coverage body, then the five-claim spot-check appended.
- Per-task directories under `<output-root>/` with reports and artifacts.

## 6. Task table (seed STATE.md with this)

| id | task | GPU | deps | status |
|---|---|---|---|---|
| T0 | <bootstrap> | no | — | PENDING |
| … | | | | |

<One line on which dependencies matter and why. Everything else may proceed as soon as
its dependency is DONE. A blocked task never blocks unrelated work.>

## 7. Explicitly out of scope

Do not spend time on these. Each is deliberately excluded.

| item | why |
|---|---|
| <item> | <reason — prior evidence, operator decision, or missing prerequisite> |

## 8. Failure modes to avoid

<!-- The highest-leverage section. Seed from: (a) this loop's specific traps, (b) the
     prior loop's FINDINGS "what went wrong", (c) the universal patterns below. -->

1. <trap specific to this loop — e.g. "the metric conflates A and B; check which
   population a number describes before citing it">
2. <trap from prior loop's failure>
3. <universal: relabelling an unwelcome result — R4>
4. <universal: citing artifacts that do not exist — R2>
5. <universal: impossible arithmetic — R5>

## 9. If you finish early

<In priority order: optional extensions that add value without scope creep. "Do not
start anything from §7" restated here.>