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
  `python3 scripts/wiki-index.py`. It is built from page frontmatter, so it
  is never hand-edited; keep each page's `title`/`description`/`status`
  current instead.
- Check before committing — `python3 scripts/wiki-check.py --warnings`.
