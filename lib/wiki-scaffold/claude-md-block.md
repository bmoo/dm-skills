# Campaign wiki

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
