# Plan brief — <loop name>

Emitted in chat at the end of a plan-autoresearch session. Not written to disk. Sections
match `autoresearch` init's harvest list one-to-one so init can read it directly.

## Decision this loop feeds

<If the answer is X → we do A. If Y → we do B. One paragraph.>

## Mission

<One paragraph: what this loop is for, why now, what it builds on. Written for an agent
with no memory of this conversation.>

## Done when

- <checkable condition — a command, a file, a number with a denominator>
- <…>

## Known facts

| fact | artifact path | status |
|---|---|---|
| <number or claim> | `<path>` | verified / unverified |

## Prohibitions

- <do-not 1>
- <…>

## Environment (verified this session)

- <venv / model path / GPU constraint / DSN>

## Tasks

<Advisory mode: ordered table — id, what/why, deps, acceptance check, expected artifact.
Goal mode: one line on why tasks cannot be enumerated up front.>

## Out of scope

| item | why |
|---|---|
| <item> | <reason> |

## Stress-test verdicts

| test | verdict | note |
|---|---|---|
| Decidability | pass / waived | |
| Cheapest kill | | |
| Unwelcome result | | |
| Confounds & baselines | | |
| Evidence audit | | |
| Budget & stop rule | | |
| Scope fence | | |

## Failure modes

1. <trap specific to this loop, with a detection signal>
2. <overruled objection — "<the objection>; if <X> is observed, this is it materialising">
3. <trap carried from prior loop's FINDINGS>

## Recommendation

- **Mode:** goal / advisory — <reason>
- **Loop name:** `<short_lowercase>`
- **Next step:** run `/autoresearch <loop name>`
