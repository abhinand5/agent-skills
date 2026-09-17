# FINDINGS — <loop name> (<one-line outcome>)

<!--
Written by the loop agent at closure — not by the autoresearch skill.
Structure: the Summary section is mandatory and comes first. Everything else is the
full-coverage body the summary compresses. If the summary and the body ever disagree,
the body wins and the summary is rewritten.
-->

## Summary (read this first)

<!--
Audience: a human — the operator, an SME, a successor agent's operator — who has read
nothing else from this loop and wants to understand what happened in a few minutes.

Rules for writing it:
- Crystal clear over complete: prose a non-specialist can follow; no unexplained
  acronyms; every number carries its denominator and its CLAIMS id in parentheses.
- Detailed, not vague: "tables improved" is not a finding; "table-value error rate fell
  from 17.8% to 9.1% of units (C142)" is.
- Honest in both directions: failures, blocked tasks, and surprising negatives belong
  here, not just wins.
- Faithful compression: every claim here must exist, with more detail, in the body
  below. The summary adds readability; it adds nothing else.
-->

**The question.** <One sentence: what this loop set out to answer, and why it mattered
now.>

**What we did.** <Two to four sentences, plain language: the main things that happened,
in order. Name the artifacts produced — where the detail lives.>

**What we found.** <The headline results, each in one sentence with its number, its
denominator, and its CLAIMS id. If a result contradicted the prior expectation, say so
here explicitly — contradictions are the most valuable thing a loop produces.>

**What it means.** <The decision this feeds and what changes now: what ships, what gets
built next, what the operator should decide. If nothing changes downstream, say that —
a measurement that changes nothing is still a result, but say so.>

**What did not work, and what is still open.** <Failed arms, fired tripwires, blocked
tasks, and the open questions carried forward — with where each is documented.>

---

<!--
The body below is the full record. Structure it so the summary's every claim is
findable: one section per major result or task group, in the order the summary presents
them. Every number: artifact path + recompute command + CLAIMS id (R1). End with the
five-claim spot-check.
-->

## 1. <First major result or task group>

<Full detail: method, numbers with denominators, artifacts, caveats.>

## N. Hypotheses (not measured)

<Prose, no numbers. What the loop believes but did not measure, and what would test it.>

## Open questions and what would answer them

<Carried forward from STATE.md's questions-for-operator plus new questions this loop
created. Each: the question, why it matters, the cheapest probe that would answer it.>

---

## Spot-check (five claims, re-run)

<!-- Pick five claims spanning the loop's major results (not five from one task).
     Re-run each recompute command in a fresh process. Record command + output + match
     verdict per claim. A failed re-run is a finding, not a embarrassment to bury:
     correct the claim and note the correction. -->

| claim | recompute command | result | matches? |
|---|---|---|---|
| | | | |