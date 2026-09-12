# Campaign wiki vocabulary sweep

Edit list for [Sweep skill text and the glossary for the page-to-concept vocabulary shift](https://github.com/bmoo/dm-skills/issues/69),
to be included in [Assemble the ready-for-agent spec](https://github.com/bmoo/dm-skills/issues/66).
This document specifies the edits; it does not apply the v0.2 upgrade.

The inventory uses dm-skills tree `4da6bc8729e6260ee183f9911abb70088375927f`.
Apply [The v0.2 campaign wiki schema](https://github.com/bmoo/dm-skills/issues/60)
and [Groomer skill and schema text handoff](https://github.com/bmoo/dm-skills/blob/4c8ddd438d9b6480630c3237ab22a2e0b69cc5b3/docs/plans/groomer-text-edits.md)
first, then this wording sweep. The final tool filenames are those from
[Checker and index generator design for v0.2](https://github.com/bmoo/dm-skills/issues/61).

## Boundary

Use **concept** when describing the OKF unit: its frontmatter, identity,
catalog entry, promotion from a seed, or membership in a bundle. Use
**bundle** for the configured wiki tree, **bundle root** for its path origin,
and **concept id** for a concept's path within that tree without `.md`.

Keep **session page**, **player page**, **node page**, and **prep sheet** for
the documents the DM reads and the skills build or edit. A session page in
an OKF bundle is a concept; calling it a page remains useful when talking
about its scenes, layout, or filing. Skills still discover non-OKF campaign
records, so their ordinary instructions to read or update a page do not
impose YAML frontmatter or a bundle on every campaign.

Keep **page** for a rendered PDF page, a browser page, a reference document,
and prose referring to the current file. Keep **wiki** for the campaign's
knowledge workspace and the user-facing name of the scaffold. Keep ordinary
“concept art”; change “session concepts” meaning unbuilt ideas to **session
ideas** in the seed inbox, where the collision is real.

An inbox file is a concept; each seed heading inside it is not a separate
concept. Reserved indexes and logs belong to the bundle but are not concepts,
including the root index that carries `okf_version` frontmatter. A filesystem
link with `.md`, a same-file heading anchor, and the party cache's player
basename are not interchangeable with a concept id.

## Shipped scaffold prose

The source of `skills/setup/wiki-scaffold` is `lib/wiki-scaffold`; edit that
canonical directory once and preserve the symlink.

### wiki-schema.md

The drafted schema already replaces generic wiki-page language with concept
and defines bundle, bundle root, and concept id. Keep its specific “session
page”, “prep and recap pages”, and the explanatory bridge to “page”. Refine
the opening definition to exclude the frontmatter-bearing reserved index.
Replace its paragraph beginning `OKF's words are used throughout` with:

```markdown
OKF's words are used throughout: a **concept** is a non-reserved markdown
document with YAML frontmatter (what the skills have called a page), and the
**bundle** is this directory tree, whose **bundle root** is the repo root in
this scaffold. A concept's **id** is its path within the bundle without the
`.md` suffix. Reserved indexes and logs belong to the bundle, not its set of
concepts.
```

The migration plans adapt the schema's layout and bundle location for their
targets. The generic tooling reads `BUNDLE_ROOT`; “bundle root” does not
globally mean “repository root”. The groomer handoff's new sections already
use concept for cross-file findings and page/sheet for session products.

### README.md

In `lib/wiki-scaffold/README.md`, retain `# Your campaign wiki` and its first
paragraph. Apply these exact phrase replacements to the existing bullets:

| Existing wording | Replacement |
|---|---|
| `appropriate page under` | `appropriate node concept under` |
| `the wiki's page, frontmatter, link, callout, and` | `the bundle's concept, frontmatter, link, callout, and` |
| `after adding or reorganising pages` | `after adding or reorganising concepts` |

Replace the closing seed paragraph with:

```markdown
The seeded `*-seed-ideas.md` concepts are inboxes: turn useful seeds into
focused concepts when they meet the schema's promotion rule.
```

Keep the groomer handoff's script names, commands, and new bullets. The schema
holds the definition of concept; this README points there rather than
defining it again.

### claude-md-block.md

Retain `# Campaign wiki`. Replace the opening paragraph with:

```markdown
This repo is an agent-maintained campaign wiki: an OKF bundle of markdown
concepts with YAML frontmatter, a generated catalog (`index.md`), and a
chronological log (`log.md`). **`wiki-schema.md` is the schema** — concept
categories, frontmatter rules, granularity and seed promotion, the rebuild
test, link conventions, callouts, tokens, and log conventions. Read it
before creating or restructuring concepts.
```

In the first bullet, replace `appropriate page` with `appropriate concept`
and `always lands on a page` with `always lands on a concept`. Keep “search
the wiki first”. The groomer handoff already supplies “concept” for the
catalog metadata bullet; use that replacement instead of editing the old
bullet independently.

### Seed inboxes

In each of these six files under `lib/wiki-scaffold/template/`, replace
`earned their own pages` in `description` with `earned their own concepts`,
and `promote it to its own page` in the body with
`promote it to its own concept`:

- `nodes/events/events-seed-ideas.md`
- `nodes/factions/factions-seed-ideas.md`
- `nodes/locations/locations-seed-ideas.md`
- `nodes/npcs/npcs-seed-ideas.md`
- `players/players-seed-ideas.md`
- `story/story-seed-ideas.md`

In `sessions/sessions-seed-ideas.md`, set `description` to:

```yaml
description: Inbox of session ideas that have not yet been built into prep pages.
```

Replace the italic body paragraph with:

```markdown
*Session ideas land here until they are built into a prep page. Each seed
is an `## H2` section; promote it to its own session page once it crosses
the granularity threshold in `wiki-schema.md`.*
```

Keep all seven filenames, H1 titles, and `type: seed-ideas`. The v0.2
metadata migration is separate from these noun changes. Keep `log.md` as a
reserved log, and retain its drafted header from the schema decision.

## Tool text

Apply these edits as part of the already-specified tool rewrite, using its
final `okf-*` filenames. They affect docstrings, comments, help, or generated
prose; they do not introduce another API rename.

| Final file and location | Final wording or operation |
|---|---|
| `template/scripts/okf_bundle.py`, opening sentence | `Shared concept discovery and frontmatter parsing for the OKF tooling.` |
| Same module, boundary paragraph | Describe `BUNDLE_DIRS`, `ROOT_CONCEPTS`, and `EXCLUDED` as the configured concept inventory under `BUNDLE_ROOT`; reserved indexes/logs are traversed separately. Remove the old “repo root” assumption and optional-PyYAML claim as part of the checker rewrite. |
| Same module, `RESERVED` comment | `Reserved filenames — bundle members, never concepts (see wiki-schema.md — Layout).` |
| Same module, concept-path enumeration docstring | `Every candidate concept path in the configured bundle, sorted; reserved files excluded.` Discovery must include a file with missing/broken frontmatter so the checker can report it. |
| Same module, reserved-path and load docstrings | Name bundle membership for reserved files; name the actual path base used by the rewritten loader. Keep repository-root and bundle-root helpers distinct if both exist. |
| `template/scripts/okf-check.py`, first numbered condition | `Every concept has a parseable YAML frontmatter block.` The error/warning split and remaining conditions come from the checker design. |
| Same script, count summary | Replace `{pages} wiki pages` with `{pages} concepts` (or the corresponding local counter name after implementation); retain the separate reserved-file count. |
| `template/scripts/okf-index.py`, opening sentence | `Generate the bundle's index layer from concept frontmatter.` |
| Same script, following description | `Writes the bundle-root index.md and the configured directory indexes. Concept entries use the target's title and description; regenerate after a batch of concept changes.` Preserve Markdown backticks around code names in the docstring if desired. |
| Same script, directory enumeration docstring | `Concepts directly inside directory (not its subdirectories).` |
| Same script, directory-index docstring | `Index for one directory: subdirectories first, then its concepts.` |
| Same script, root-index docstring | `The root catalog — concepts grouped by configured directory.` |
| Same script, generated mixed-directory heading | If the existing `# <label> — pages` heading remains, change only the suffix to `— concepts`. |
| Same script, old generated `<count> page/pages in ...` subdirectory text | The checker/index design replaces it with configured group descriptions. Remove this old text with that change; if a count appears elsewhere, its nouns are `concept` / `concepts`. |
| `template/scripts/okf_config.py`, root-file comment | `Concepts at the bundle root.` |
| Same config, exclusion comment | `Directories never walked for concepts, at any depth.` |
| Same config, directory comments | Describe `BUNDLE_DIRS` relative to the bundle root and `BUNDLE_ROOT` relative to the repository root, following the resolved config design. |

Replace the default `WIKI_INTRO` with:

```python
WIKI_INTRO = (
    "This catalog lists the bundle's concepts and is generated from their"
    " frontmatter by `scripts/okf-index.py` — edit the concepts, not this file."
)
```

The wording covers a catalog that also links generated subdirectory indexes;
it does not claim every linked file is a concept. `WIKI_TITLE`, `WIKI_INTRO`,
“Campaign Wiki”, and “wiki-schema.md” keep their established names.

No vocabulary-only rename of `page_paths`, `pages_in`, local `pages` variables,
parser types, or check ids is required. The tool rewrite may choose internal
names consistently, but it must update callers together. The already-resolved
module/config renames remain required. These are distinct from renaming
user-facing terms.

## Shipped skills: edit or retain

| Skill or procedure | Disposition |
|---|---|
| `setup/SKILL.md`, Phase 2 | Change `facts → pages` to `facts → concepts`, and `wiki-schema.md still governs pages` to `wiki-schema.md still governs concepts`. Its wiki bootstrap offer and repo-root preflight stay: setup creates this particular default layout. The copied guide block supplies the OKF vocabulary. |
| `build-session/SKILL.md` | Keep session page, full page, lean sheet, node page, page-owned checks, and the ordinary discovery list's page categories. The groomer handoff uses concept for schema metadata/findings and keeps session page for the build. No further noun replacement is needed. |
| `build-session/node-deepening.md` | Keep seed, thin page, new page, node page, and references to reading/writing the page in this campaign-agnostic procedure. In Step 5, replace `Frontmatter matches the page's directory and status conventions` with `Frontmatter follows the campaign's schema and status conventions`; replace `The repo's page catalog updated` with `The repo's catalog updated`. These route metadata and indexing through the discovered schema without a second OKF definition. |
| `catch-up/SKILL.md` | Keep “Directly impacted pages”, player page, played page, session page, and neighboring/owning pages: those describe the absorption rings across whatever record the campaign keeps. The groomer handoff adds precise concept terminology for metadata and paired findings. |
| `party-sync/SKILL.md` | Keep player page, roster page, and page basename, including the `player` JSON key and its join rule. A basename such as `dan` is not the OKF concept id `players/dan`; no key or data migration follows from this vocabulary sweep. |
| `seed-clues/SKILL.md` | Keep the pages clues touch and the existing pages mined for clues. The procedure works from campaign records without requiring OKF. |
| `campaign-art/SKILL.md` | Keep campaign page, reference pages, page basename, and “read the whole page”: these name the source document and image pairing. The link-origin correction below uses bundle root only when the discovered schema does. |
| `combat-generator/SKILL.md` and `complications.md` | Keep location/node page, session page, page text around a block, and creature reference/stat-block page. These distinguish encounter filing destinations and rules references, not generic OKF units. |
| `review-rewards/SKILL.md`, `state-format.md` | Keep the localhost review page, page restore control, and “this page” meaning the format document. Keep wiki/site bundle for the exclusion boundary and schema-controlled page furniture for the approved pool. The review UI and JSON state are not concepts. |
| `to-session-brief/SKILL.md` | Keep “finished page” and “does the page enact it”: the brief describes the session output. The tracker issue itself is not a wiki concept. |

### Link-origin wording found during the sweep

`campaign-art/SKILL.md` Step 5 currently unconditionally emits a path relative
to the target page. The resolved `/`-link rule needs that writer to honor the
discovered schema. Replace item 2 with:

```markdown
2. **Report the embed snippet** for the DM to paste, in standard Markdown
   image syntax with alt text and the campaign schema's link form. In an
   OKF bundle, use a path from the bundle root, for example
   `![Silver Fox](/Media/images/silver-fox.png)` when that is the image's
   location in the bundle. Otherwise follow the repo's documented link
   convention; without one, use a path relative to the target page.
```

This applies the existing link decision to an overlooked authoring sentence;
it changes neither image placement nor the skill's filing permission. Media
need not be a concept to be a link target in the bundle tree.

## CONTEXT.md additions

Append the following section to `CONTEXT.md` when the v0.2 schema and skill
edits land. No existing glossary entry is renamed. The introductory use of
“concept” in “two words … for one concept” remains ordinary prose.

```markdown
## Campaign wiki

**Concept**:
A non-reserved Markdown document with YAML frontmatter in the campaign's
OKF bundle. Session pages, player pages, node pages, and seed inboxes are
concepts when they belong to that bundle.
_Avoid_: page as the generic unit in schema or tooling rules; specific
document names such as “session page” remain in use.

**Bundle**:
The campaign wiki tree governed by its OKF schema: concepts, reserved
catalogs and logs, and supporting files within its boundary.
_Avoid_: repository when referring specifically to the wiki boundary.

**Bundle root**:
The directory from which the bundle's `/`-form links and concept ids are
interpreted; it may be the repository root or a directory beneath it.
_Avoid_: repo root unless those directories actually coincide.

**Concept id**:
A concept's path within its bundle without the `.md` suffix, such as
`nodes/npcs/maren-tallow`. The link to that concept is
`/nodes/npcs/maren-tallow.md`.
_Avoid_: title, basename, URL, or heading anchor as synonyms for the id.

**Seed**:
A topic recorded as a heading section in a seed inbox, before it earns its
own concept. The inbox is one concept; its seeds are not separate concepts.

**Groomer**:
The campaign wiki maintenance skill, `groom-wiki`, combining mechanical
maintenance with a judgement pass that places unresolved findings where
the next reader will meet them.
```

The existing **Fresh check** and **Self-heal** entries retain their defined
meanings. A groomer's judgement pass authors findings; a fresh check grades
an artifact. Groomer maintenance is not a synonym for the generator's
verification loop. No scheduling rules, callout grammar, or tool procedures
belong in this glossary; those remain in the schema and skills.

## Retained library language and coupling

The campaign contract's *Must move in the same commit* table was checked.
The following uses are intentional and require no noun sweep:

- `lib/encounter-meta-format.md`, `lib/verification.md`, and
  `lib/mechanical-checker/{README.md,self-heal-loop.md}` describe page
  output, filing, and checks. Keep their page wording and stable ids.
- `lib/spotlight-doctrine.md` and `lib/class-patterns.md` name player pages
  and profiles; keep them and their symlinked copies in the consuming skills.
- `build-session/{session-page-format.md,dungeon.md,spotlight.md,map-render.md}`
  distinguish session outputs, durable node pages, and in-page sections.
  Keep those names, filenames, headings, links, and the `page-break` callout.
- `build-session/render.md` and its Python/CSS/template files also use page
  for a printed page. `review-rewards` scripts/templates use it for a browser
  page. Neither is renamed to concept. Fixture narration and external rule
  source references retain page in the same senses.
- Root `README.md` and `docs/campaign-contract.md` keep page types, session
  pages, and player pages in the campaign-agnostic discovery contract. Their
  only v0.2 coupling additions are already supplied by the groomer handoff.

The vocabulary edits introduce no new serialized shape, parser key, or
mechanical check id. Keep `session-page-format.md`, `session_parser.py`,
`build-session/location-uses-page-keys`, existing callout names, and party
cache field names. The existing coupled format rows therefore need no
additional changes for this sweep. Apply tool prose and config output with
the checker/index rewrite, and the skill prose with the schema/groomer edits.

Generated `index.md` files are regenerated, not hand-edited for vocabulary.
[Rewrite the emberwick-vale example to the v0.2 schema](https://github.com/bmoo/dm-skills/issues/67)
already recopies the seven seed inboxes, schema, and scripts byte-identically
and regenerates indexes. Do that after this sweep; retain the example's
session/player/node page names and its campaign-specific content.

## Verification and handoff

The inventory covered the tracked skill Markdown, canonical library
Markdown, scaffold scripts and seed files, glossary, campaign contract,
and root README. Symlink targets were reviewed at their canonical locations;
generated catalogs, mechanical fixture narration, renderer/UI source, and
external rules assets were classified by their existing document meanings.

When implementing, search for whole-word `page`/`pages` and
`concept`/`concepts` across those sources. Review remaining occurrences
against the boundary above, rather than applying a global replacement.
Check the old scaffold boilerplate and “session concepts” are gone, the
catalog/checker output says concepts, and the link writer uses the discovered
origin. Regenerate catalogs and run the existing content gate:
`pytest checks/ lib/mechanical-checker skills/build-session/scripts/`.
Existing runtime fixtures move only if the combined v0.2 tool change alters
their output; add no tests over this maintenance document or glossary prose.

This handoff was checked against the named source spans and with
`git diff --check`. It adds no executable code and claims no runtime test
result. No further decision or investigation is required by this sweep.
