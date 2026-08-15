# The Emberwick Vale — campaign guide

An example campaign for the dm-skills library: a small, fully-wired
campaign repo you can clone and play, or read as living documentation of
what the installed skills look for. Everything here is invented for this
example; rules content is SRD 5.2.1 only.

## Campaign wiki

This repo is an agent-maintained campaign wiki: markdown pages with YAML
frontmatter, a generated catalog (`index.md`), and a chronological log
(`log.md`). **`wiki-schema.md` is the schema** — page categories, frontmatter
rules, granularity and seed promotion, the rebuild test, link conventions,
callouts, tokens, and log conventions. Read it before creating or
restructuring pages.

- The DM states a fact → file it on the appropriate page immediately. The DM
  asks a question → search the wiki first; answer with citations to local
  files. New information always lands on a page; it never disappears into
  chat history.
- Log meaningful operations in `log.md` per the schema's Log conventions.
- Regenerate the catalog after every batch of wiki changes —
  `python3 scripts/wiki-index.py`. It is built from page frontmatter, so it
  is never hand-edited; keep each page's `title`/`description`/`status`
  current instead.
- Check before committing — `python3 scripts/wiki-check.py --warnings`.

## Where things live — answers for the installed skills

The skills discover this campaign by reading this guide. The slots they
probe for, answered:

- **Method handbook** — `wiki-schema.md` holds the wiki conventions; the
  planning method (nodes, clue webs, revelations) follows the library's
  defaults with no house variations.
- **Live layer + progress marker** — `story/campaign-status.md`. Its
  **Progress marker** line is the canonical marker of how far the campaign
  has advanced.
- **Session records / prep home** — `sessions/`, one page per session,
  played or in prep.
- **Player pages / party cache** — pages under `players/`; the synced party
  cache is `players/party.json`.
- **Session transcripts** — not kept.
- **Reward economy** — gold, plus favors owed by named NPCs; both are
  tracked on the node pages that owe them.
- **Approved-items list** — `story/approved-items.md`. Items on it may be
  placed silently; anything else needs the DM's yes first.
- **Combat evidence** — no structured combat log; use the encounter-meta
  `Spotlight:` lines on played session pages.
- **Media dir + style anchor** — `media/`; no style anchor image yet.
- **Sync camp** — direct to main. No PR flow.
