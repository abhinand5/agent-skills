# grill-research checklist

The exit condition for a grilling session. Every item that applies to the mode gets a
verdict: pass, fail, waived, or n/a. Order of questioning follows dependencies, not this
list, though the list is roughly in dependency order.

Modes: **P** plan · **R** result · **C** claim.

| # | Item | Modes |
|---|---|---|
| 1 | Question sharpness | P R C |
| 2 | Stakes | P R C |
| 3 | Prediction on record | P R |
| 4 | Construct validity | P R C |
| 5 | Baseline & comparison | P R C |
| 6 | Confounds & alternative explanations | P R C |
| 7 | Identification | P R C |
| 8 | Variance, power & forking paths | P R C |
| 9 | Evidence audit | R C |
| 10 | Cheapest kill | P R |
| 11 | Unwelcome result | P R |
| 12 | Generalization | P R C |
| 13 | Prior work | P C |
| 14 | Skeptical reviewer | P R C |
| 15 | Claim–evidence fit | C (R when the user states a conclusion) |

---

## 1. Question sharpness

**Ask:** What exactly is the question? What unit, population, intervention, comparison,
and outcome? What answer would count as "yes"?

**Passes when:** it can be written as one sentence whose answer is a yes/no or a number,
and both the user and you would agree on which answer a given result gives.

**Fails as:** "does X help?" (help what, measured how, against what?); a question that
is really three; a question whose answer is already known from the setup.

## 2. Stakes

**Ask:** If the answer is yes, what do you believe or do differently? If no?

**Passes when:** both branches change a belief, a decision, or what gets built next.

**Fails as:** every outcome leads to the same next step, so the work is decoration.

## 3. Prediction on record

**Ask:** Before looking (or, for a result: before you looked), what did you expect, and
how big? What result would surprise you?

**Passes when:** a direction and rough magnitude were stated before the data, or the
user admits they were not and the analysis is treated as exploratory.

**Fails as:** the hypothesis was written after the result; "any improvement" as the
prediction; exploratory analysis reported as confirmatory.

## 4. Construct validity

**Ask:** Does the metric measure the thing you care about, or a stand-in for it? Where
do they come apart? Could the number go up while the real thing gets worse?

**Passes when:** the gap between proxy and target is named and either shown small (a
correlation, a manual check of samples) or listed as a caveat.

**Fails as:** benchmark score treated as capability; loss treated as quality;
LLM-judge scores never checked against human judgement; a metric the method was tuned
on (Goodhart).

## 5. Baseline & comparison

**Ask:** Compared to what? Is that the strongest reasonable alternative? Did it get the
same tuning budget, data, and compute as the proposed method?

**Passes when:** the baseline is the one a skeptic would pick, tuned with comparable
effort, and run in the same harness.

**Fails as:** comparing to a default-hyperparameter baseline; to a number copied from a
paper with a different setup; no "do nothing" or "simple heuristic" control; ablations
missing, so the component credited is not isolated.

## 6. Confounds & alternative explanations

**Ask:** What else would produce the same signal? List them. For each: how is it ruled
out?

**Passes when:** each named alternative has a control, an ablation, or an explicit
caveat. You have added at least one the user had not raised.

**Fails as:** train/test leakage or benchmark contamination; different data or compute
between arms; selection effects; regression to the mean; implementation differences
masquerading as method differences; the eval harness itself changing.

## 7. Identification

**Ask:** Is the claim causal or correlational? Does the design support that?

**Passes when:** causal language is backed by an intervention or a controlled
comparison where only the variable of interest differs; otherwise the claim is worded
as association.

**Fails as:** "X causes Y" from observational data; changing two things at once and
crediting one; post-hoc subgroup stories.

## 8. Variance, power & forking paths

**Ask:** How many seeds, samples, or runs? What is the spread? Is the effect larger than
the noise? How many things were tried before this one was reported?

**Passes when:** the effect is reported with a spread (CI, std over seeds, bootstrap)
and clearly exceeds it; n was fixed in advance or the stopping rule is stated; the
number of variants tried is known and accounted for.

**Fails as:** single seed; effect smaller than seed-to-seed variance; best-of-N
reported as typical; many metrics or subsets checked and the good one reported; tuning
on the test set.

## 9. Evidence audit

**Ask:** Where does each number come from? Show me the file, log, or command.

**Passes when:** every number has a path that exists and, where cheap, you have
re-derived it read-only. Numbers without a source are marked unverified.

**Fails as:** numbers from memory; a table that does not match the logs; a plot whose
underlying data is gone; units or denominators unclear.

## 10. Cheapest kill

**Ask:** What is the smallest, fastest experiment that could show this is wrong?

**Passes when:** it is named, and it is either run first or there is a stated reason
it is not.

**Fails as:** the expensive experiment is first; no experiment in the plan could
produce a no.

## 11. Unwelcome result

**Ask:** What happens if the answer is no, null, or the opposite? Would you report it?

**Passes when:** a null is a reportable, useful outcome with a named next step, and the
design can actually produce one.

**Fails as:** the plan only has a path for success; a null would be explained away
("needs more tuning") with no rule for when to stop.

## 12. Generalization

**Ask:** The evidence covers which datasets, scales, domains, populations? The claim
covers which?

**Passes when:** the scope of the claim is no wider than the scope of the evidence, or
the extrapolation is stated as such.

**Fails as:** one dataset, general claim; small-scale result, claim about scale; one
model family, claim about "LLMs".

## 13. Prior work

**Ask:** Has this been done? What is actually new? What pitfalls did prior attempts
hit?

**Passes when:** the closest prior work is named and the delta is stated in one
sentence. Search the literature if it could change this verdict.

**Fails as:** rediscovering a known result; missing the paper that already refuted it;
novelty that is only a renaming.

## 14. Skeptical reviewer

**Ask:** What is the single strongest objection a hostile, competent reviewer would
raise? Is it answered?

**Passes when:** you have stated the strongest objection you can construct (steelman
the critic), and the work answers it or the claim is narrowed to survive it.

**Fails as:** only weak objections are considered; the strongest one is dismissed
without evidence.

## 15. Claim–evidence fit

**Ask:** For each sentence that asserts something: which evidence supports it, and is
the wording no stronger than that evidence?

**Passes when:** every claim maps to a specific result; strength words ("shows",
"demonstrates", "significantly", "state of the art", "robust") are earned; negative and
mixed results that bear on the claim are reported.

**Fails as:** abstract stronger than results; cherry-picked examples presented as
typical; "significant" without a test; omitted runs that went the other way.
