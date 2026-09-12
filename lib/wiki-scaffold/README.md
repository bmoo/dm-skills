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
- Run `python3 scripts/okf-check.py --strict` to check that the wiki follows its
  schema.
- Use `/groom-wiki`, if installed, to apply mechanical fixes and place
  findings where prep reads them; `/groom-wiki --dry-run` writes nothing.
  The script alone, `python3 scripts/okf-groom.py`, reports mechanical
  findings; add `--fix` to apply its safe fixes. Catch-up invokes the skill
  after absorption when installed; otherwise run it on demand. The first
  run after a migration is on demand, starting with the skill's dry run.
- For a legacy bundle, configure `MIGRATION_*` in `scripts/okf_config.py`, then
  run `python3 scripts/okf-migrate.py`. It migrates metadata and existing local
  links in place, preserving broken targets and unrelated metadata. Re-running
  it changes nothing; regenerate the index and run the strict checker afterward.
  Migration is planned work, separate from routine grooming.
- Optionally set `SESSION_WEEKDAY` in `scripts/okf_config.py`; catch-up
  uses it to propose the next date. The schema owns the session horizon.

The seeded `*-seed-ideas.md` pages are inboxes: turn useful ideas into focused
pages as they become campaign facts.
