# agent-skills

Skills I use with Claude Code and Codex. Each skill is a folder under `skills/` with a
`SKILL.md` (instructions), optional reference docs, scripts, and templates.

## Skills

### [craft-book](skills/craft-book)

Write a personalised technical book — field guide, course companion, prerequisite
refresher — and ship it as a print PDF, a Kindle-ready EPUB, and portable Markdown from
one source. The skill first probes the reader's intent and *verified* skill level (a
grill-me-style interview plus a short diagnostic), keeps a self-evolving learner
profile across books, and enforces a QA gate that catches the silent conversion damage
pandoc and e-readers are prone to (flattened tables, un-backslashed control words in
maths, un-centred MathML, missing chapter titles).

Two buildable pipelines are included — Markdown-first (default) and LaTeX-first — with a
scaffold script, checkers for all three editions, a numeric-check runner, and contact
sheets for visual review. Requires pandoc ≥ 3, a TeX Live with LuaLaTeX, rsvg-convert,
poppler, python3, and optionally ImageMagick.

```sh
python3 ~/.agents/skills/craft-book/scripts/new_book.py --pipeline markdown \
  --dest my-book --title "The Probability Spine"
cd my-book && make && make verify && make pages
```

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add abhinand5/agent-skills
```

Or by hand — clone and symlink the skills you want into your agent's skills directory:

```sh
git clone https://github.com/abhinand5/agent-skills ~/dev/agent-skills
ln -s ~/dev/agent-skills/skills/craft-book ~/.agents/skills/craft-book   # Codex / shared
ln -s ~/.agents/skills/craft-book ~/.claude/skills/craft-book             # Claude Code
```

## Licence

MIT — see [LICENSE](LICENSE).
