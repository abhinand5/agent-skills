# Intake: probe intent and level before writing a word

The intake produces two artefacts: an updated **learner profile** (global, reused across
books) and an approved **BOOK-BRIEF.md** (per book). Everything downstream is derived
from them, so this phase is where most of the personalisation happens.

## 0. Load what is already known

- `python3 ~/.agents/skills/craft-book/scripts/profile.py show` (creates the profile
  from the template on first use and flags stale verified levels).
- If the workspace has `MISSION.md`, `NOTES.md`, `RESOURCES.md`, or `learning-records/`
  (the `teach` skill's layout), read them; they answer several questions below.
- Skip any question the profile already answers with a **verified** entry. Confirm
  self-reported entries briefly rather than re-asking from scratch. Reconfirm stale
  verified entries with one diagnostic item each.
- Record facts as they arrive (`profile.py field/level/pref`), per [PROFILE.md](PROFILE.md);
  do not batch them for a manual write-up at the end.

## 1. Interview (grill-me style, one question at a time)

Ask one question per turn, give your recommended answer with it, and walk the branches
in dependency order. Use `AskUserQuestion` when the choice is discrete. Stop when every
branch below has a decision. Typical run: 8–14 questions.

**Mission**
- What is the book for, concretely? (a course, an exam, a job, "understand X for life")
  Name the course/lectures/deadline if there is one.
- What should the reader be able to *do* afterwards that they cannot do now?
  Write these as 3–5 capability statements; they become the reader's contract.
- What is explicitly out of scope, and what is assumed (frameworks, languages, maths)?

**Reader**
- Background: degree/field, years, what they build, what they have already studied.
- Which parts of the topic feel solid, which feel shaky, which are unknown?
- Preferred learning style: derivation-first, intuition-first (3B1B), code-first,
  problem-first? Visuals wanted or a distraction?
- Spelling/locale (en-GB vs en-US), notation conventions they already use.

**Shape**
- Length budget in pages or reading hours. Recommend compact (40–60 pp) unless the
  mission is reference-heavy.
- Structure: chapters that follow the course order, or the concept order that lasts?
- Depth per topic: proofs in full, proofs sketched with conditions, or results only?
- Exercises: checkpoints with answers (recommended), none, or a separate self-test?
- Refreshers/appendices needed for prerequisites?

**Formats and delivery**
- Which editions: PDF, EPUB (Kindle), Markdown (Obsidian/GitHub), any subset.
  Ask which device the EPUB will be read on; that decides the Kindle contract.
- Print size preference (default 7×10 in), font taste, colour vs greyscale boxes.
- Reading plan: how many weeks, which chapters must land before which lecture.

If a question can be answered by reading the workspace or the profile, read instead.

## 2. Diagnostic (5–8 items, calibrated, quick)

Self-reports drift; the diagnostic anchors the starting depth. Design it *after* the
interview so it targets the topics the book will lean on.

- Mix three kinds: **recall** (state a definition/identity with its conditions),
  **derivation** (two-line proof or computation with a number), **judgement**
  (which method/assumption applies and why).
- Each item names the topic it probes. Aim for the reader to get ~60% — too easy
  teaches nothing, too hard demoralises.
- Deliver as a numbered list in one message; score with a short rubric; report the
  result per topic, not as a total.
- Record each scored item: `profile.py level "Topic" LEVEL --verified --evidence "diagnostic i/n"`
  — this is what lets the next book skip re-probing.
- Offer to save the diagnostic as `SELF-TEST-00.md` in the workspace; readers like
  re-taking it after finishing the book.

## 3. Write BOOK-BRIEF.md and get approval

Fill `templates/BOOK-BRIEF.md`: mission, capability statements, reader snapshot,
assumptions, chapter map with page budgets, style decisions, formats, reading plan,
sources to cite, and the pipeline choice with its reason. Present it; iterate until
the user approves. The brief is the contract for the writing phase and the checklist
for QA.

## 4. Profile

Nothing to do by hand: if steps 1–3 followed the triggers in [PROFILE.md](PROFILE.md),
the profile already reflects this intake. Run `profile.py log --tail 15` to confirm and
mention in one line what was recorded.
