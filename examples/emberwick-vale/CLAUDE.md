# The Emberwick Vale — campaign guide

An example campaign for the dm-skills library: a small, fully-wired
campaign repo you can clone and play, or read as living documentation of
what the installed skills look for. Everything here is invented for this
example; rules content is SRD 5.2.1 only.

# Campaign wiki

This repo is an agent-maintained campaign wiki: an OKF bundle of markdown
concepts with YAML frontmatter, a generated catalog (`index.md`), and a
chronological log (`log.md`). **`wiki-schema.md` is the schema** — concept
categories, frontmatter rules, granularity and seed promotion, the rebuild
test, link conventions, callouts, tokens, and log conventions. Read it
before creating or restructuring concepts.

- The DM states a fact → file it on the appropriate concept immediately. The DM
  asks a question → search the wiki first; answer with citations to local
  files. New information always lands on a concept; it never disappears into
  chat history.
- Log meaningful operations in `log.md` per the schema's Log conventions.
- Regenerate the catalog after every batch of wiki changes —
  `python3 scripts/okf-index.py`. It is built from frontmatter, so it is
  never hand-edited; keep each concept's `title` and `description` current.
- Check before committing — `python3 scripts/okf-check.py --strict`.
- Groom after session absorption, or on demand: `/groom-wiki` if installed
  applies mechanical fixes and places findings per `wiki-schema.md`.
  `/groom-wiki --dry-run` writes nothing. The script-only entry point is
  `python3 scripts/okf-groom.py` (reports); `--fix` applies mechanical fixes.
  Catch-up owns the after-absorption invocation, so do not invoke it twice.
- For a planned migration of an existing bundle, use `scripts/okf-migrate.py`
  with the migration plan; it is separate from routine maintenance. The first
  groom after migration is on demand, starting with `/groom-wiki --dry-run`.

## Where things live — answers for the installed skills

The skills discover this campaign by reading this guide. The slots they
probe for, answered:

- **Method handbook** — `wiki-schema.md` holds the wiki conventions; the
  planning method (nodes, clue webs, revelations) follows the library's
  defaults with no house variations.
- **Live layer + progress marker** — `story/campaign-status.md`. Its
  **Progress marker** line is the canonical marker of how far the campaign
  has advanced.
- **Session records / prep home** — `sessions/`, one prep sheet per
  session, played or in prep.
- **Player pages / party cache** — pages under `players/`; the synced party
  cache is `players/party.json`.
- **Session transcripts** — not kept.
- **Reward economy** — gold, plus favors owed by named NPCs; both are
  tracked on the node pages that owe them.
- **Approved-items list** — `story/approved-items.md`. Items on it may be
  placed silently; anything else needs the DM's yes first.
- **Combat evidence** — no structured combat log; use the encounter-meta
  `Spotlight:` lines on played prep sheets, with catch-up's fired/denied
  marks beside them.
- **Media dir + style anchor** — `media/`; no style anchor image yet.
- **Sync camp** — direct to main. No PR flow.
