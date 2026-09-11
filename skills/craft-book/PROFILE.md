# Profile evolution: the learner profile maintains itself

The profile at `~/.agents/books/learner-profile.md` is the skill's memory of the reader.
It evolves without being asked: every trigger below is an automatic `scripts/profile.py`
call, logged to `profile-log.md` next to it. The reader never has to maintain it, and
never has to think about it unless they want to.

## Triggers (do these without asking)

| Moment | Command |
|:--|:--|
| Intake reveals a background/format/style fact | `profile.py field "Key" "value"` |
| Reader states a level ("I'm rusty on X") | `profile.py level "X" shaky` |
| Diagnostic item scored | `profile.py level "X" working --verified --evidence "diagnostic 2/3, TITLE"` |
| Reader corrects you or states a standing preference | `profile.py pref "…"` |
| Book delivered | `profile.py book --title … --path … --pipeline … --assumes "…"` and one `level … --verified --evidence "finished TITLE"` per capability statement the book's checkpoints exercised |
| Self-test retaken later | `level … --verified` per topic with the new score |
| Reader says a topic no longer applies / was wrong | `profile.py forget "X"` |

Rules the script enforces: a verified level replaces the self-reported one for the same
topic; the newest entry wins; levels are `unknown | shaky | working | solid`.

## Decay

`profile.py show` and `profile.py stale` flag verified levels older than 180 days. At
the next intake, reconfirm each stale topic with a single diagnostic item instead of
trusting it; re-record the result. Nothing is deleted by time alone.

## What never goes in

Secrets, credentials, health or financial details, anything unrelated to how the reader
learns technical material. Keep the file short; it is read at the start of every book.

## Reader controls (honour immediately, for the current task)

- "Don't update my profile" / "leave the profile alone" → run everything with
  `CRAFT_BOOK_PROFILE=off` for this task and say nothing more about it.
- "Use a different profile for this" → `CRAFT_BOOK_PROFILE=path/to/file.md`.
- "Forget that I know X" / "Actually I'm solid at X" → `forget` / `level` as stated.
- "Show me what you know about me" → `profile.py show`; "what changed?" → `profile.py log`.
- The file is plain Markdown: the reader may edit it by hand at any time; the script
  merges around edits rather than overwriting them.

## In the delivery note

One line only: "Profile updated: N levels verified, M preferences recorded
(`profile.py log` to review)." Do not paste the profile.
