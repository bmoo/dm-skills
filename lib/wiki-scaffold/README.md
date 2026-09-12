# Your campaign wiki

The `setup` skill copies these files into your campaign repository to give you a
starting wiki for planning and running the campaign.

## Start here

- Put campaign facts in the appropriate page under `nodes/`, and use the
  `story/`, `sessions/`, and `players/` folders for their corresponding notes.
- Read `wiki-schema.md` for the wiki's page, frontmatter, link, callout, and
  log conventions.
- Set your campaign name in `scripts/okf_config.py` as `WIKI_TITLE`.
- Run `python3 scripts/okf-index.py` after adding or reorganising pages to
  refresh the generated catalog.
- Run `python3 scripts/okf-check.py` to check that the wiki follows its
  schema.

The seeded `*-seed-ideas.md` pages are inboxes: turn useful ideas into focused
pages as they become campaign facts.
