# wiki-scaffold — the consumer wiki bootstrap's template assets

The committed template tree the `setup` skill's wiki-bootstrap phase copies
into a consumer's fresh campaign repo, plus the block it appends to the
consumer's `CLAUDE.md`. It bootstraps a planning wiki in the consumer's campaign
repo.

## What ships, and how

- **`template/`** — copied verbatim into the consumer repo **root**:
  - `wiki-schema.md` — the self-contained schema doc: frontmatter rules,
    granularity + seed promotion, the rebuild test, link conventions,
    callout grammar, reference tokens, log conventions.
  - `scripts/` — the catalog and check tooling, dependency-free:
    `wiki_config.py` (every campaign-specific constant — directories, group
    labels, root-catalog title and prose), `wiki_bundle.py` (page discovery +
    frontmatter parsing), `wiki-check.py` (schema conformance),
    `wiki-index.py` (generated index layer).
  - The directory skeleton — `nodes/{locations,factions,npcs,events}`,
    `story/`, `sessions/`, `players/` — each seeded with its seed-ideas
    inbox, plus `log.md` with its conventions header.
- **`claude-md-block.md`** — appended to the consumer's `CLAUDE.md` **with
  their consent**, never copied as a file. It carries the wiki's default
  behavior (facts → pages, questions → wiki-first, log, regenerate, check).

After copying, the setup skill sets `WIKI_TITLE` in
`template/scripts/wiki_config.py`'s copy to the consumer's campaign name and
runs `python3 scripts/wiki-index.py` once to generate the initial catalog —
index files are generated, so none ship here.

This library lives under `lib/` for the same reason `mechanical-checker` and
`judgement-checker` do: it is canonical source the consuming skill
materialises, not skill prose. The `setup` skill reaches this directory the
same way the generators reach those — the relative symlink
`skills/setup/wiki-scaffold`, dereferenced into a real copy at install; the
pair sits on `lib/test_symlink_integrity.py`'s roster.

## Provenance and boundaries

The scripts are genericized from a private campaign repo's wiki tooling
(structure preserved; campaign constants extracted into `wiki_config.py`;
spec section-number citations replaced with schema-doc references). The
schema doc's prose is written fresh for this library. Per the map's standing
decisions:

- **No external-spec branding.** The conventions are this library's own
  self-contained schema; the schema doc carries a one-line
  pattern-inspiration credit and nothing else tracks the external spec.
- **Never ships:** prep-method prose, publishing machinery, and any private
  campaign content. The template's pages are empty inboxes and conventions
  only.

## Verifier chain

These templates are consumer scaffold content, not skill text, so nothing here
is graded by the harness's model tiers. But the setup skill's bootstrap phase
makes two promises *about* this template that are true or false the moment it
is committed: that a fresh copy comes up clean, and that the phase's preflight
names every top-level path the copy would land. Both are inventory rows —
`lint/wiki-scaffold-starts-green` and
`lint/wiki-scaffold-preflight-covers-template`, under *Static lints* in
`docs/eval-assertion-inventory.md` — and `lib/wiki_scaffold_lint.py` is derived
from them, resolving the question the original implementation left open.

**So editing this template is a `pytest lib/` matter.** A seed page the schema
rejects, or a new top-level file the skill's preflight list never learns about,
fails the gate here instead of on a consumer's first run. An edit that changes
what the *skill* promises still follows CLAUDE.md's chain: inventory row first,
this lint second.
