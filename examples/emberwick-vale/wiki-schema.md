---
type: schema
title: Campaign Wiki Schema
description: The conventions this wiki runs on — page categories, frontmatter, granularity, links, callouts, tokens, and the log.
tags: [meta, schema, conventions]
status: active
---

# Campaign Wiki Schema

This repo is an agent-maintained campaign wiki: markdown pages with YAML
frontmatter, a catalog generated from that frontmatter, and a chronological
log. This file is the schema — the conventions every page follows and every
agent maintaining the wiki obeys. It is self-contained: nothing here tracks an
external spec. (The frontmatter-plus-generated-catalog kernel is
pattern-inspired by the Open Knowledge Format.)

## Layout

| Path               | Purpose                                                          |
| ------------------ | ---------------------------------------------------------------- |
| `nodes/`           | The node web — everything the players can investigate            |
| `nodes/locations/` | Places the campaign can visit                                    |
| `nodes/factions/`  | Organizations and groups                                         |
| `nodes/npcs/`      | Non-player characters                                            |
| `nodes/events/`    | Events and time-based phenomena                                  |
| `story/`           | The meta-campaign layer — arcs, campaign status, open questions  |
| `players/`         | Player characters                                                |
| `sessions/`        | Per-session prep and recap pages                                 |
| `scripts/`         | The wiki tooling — catalog generator and conformance check       |

`index.md` is the generated page catalog. `log.md` is the chronological
operation log. Both are **reserved filenames** at every level — never use
either name for a wiki page. Index files are generated, never hand-edited,
and carry no frontmatter.

## Frontmatter

Every wiki page opens with a YAML frontmatter block. One field is required:

- `type:` — non-empty, and it **matches the page's immediate directory**:
  `nodes/npcs/` → `type: npc`, `nodes/locations/` → `type: location`,
  `story/` → `type: story`, `players/` → `type: player`,
  `sessions/` → `type: session`. The seed-idea inboxes use
  `type: seed-ideas` wherever they live, and this file uses `type: schema`.

Four more are expected on every new page:

- `title:` — the page's display name; the catalog prints it.
- `description:` — **one plain sentence with no markdown links.** The catalog
  prints it verbatim in more than one directory, so a relative link inside it
  resolves in one place and breaks in another.
- `tags:` — a short inline list, e.g. `[npc, recurring]`.
- `status:` — the page's lifecycle state. Suggested vocabulary: `stub`,
  `active`, `canon`, `retired`.

A `timestamp:` (ISO 8601) is welcome on pages where recency matters.

Run `python3 scripts/wiki-check.py --warnings` before committing — it fails
on a missing frontmatter block or an empty `type`, and warns on missing
recommended fields. Run `python3 scripts/wiki-index.py` after any batch of
page changes — the catalog is built from frontmatter, so keeping `title`,
`description`, and `status` current is how the catalog stays true.

## Granularity and seed promotion

Each category directory has a seed-ideas inbox (e.g.
`nodes/npcs/npcs-seed-ideas.md`) — the catch-all for stubs that haven't yet
earned their own page. A seed lives as an `## H2` section in the inbox.

A topic earns its own page when any of these holds:

- it has grown past roughly 150 words,
- three or more other pages reference it,
- the DM says so.

Promote the seed by moving its content to a new page in the same directory
(frontmatter per the rules above) and leaving no copy behind in the inbox.

**Session-bound content never earns its own node page, regardless of size.**
A character or location that exists only inside one session's events is
inlined on that session page. It gets a node page (or a seed) only when it
has life beyond the session that introduced it — other nodes reference it,
it is due to recur, or it anchors an investigation thread.

## The rebuild test

The inverse discipline: session-scoped content never lands on a node page
ahead of play, even when the node itself is legitimate. The test — **if this
session were rebuilt from scratch against this node, would this content be
rebuilt too?** If yes, it is session output and belongs only on the session
page while that session is unplayed. A node holds what a rebuild would
*read*, not what a rebuild would *produce*.

- **Rebuilt every time — session page only, while unplayed:** encounter
  rosters and XP budgets, party size and level, named PCs, resource arcs,
  route pacing, contingency lists, boxed text written for one table.
- **Read every time — node page, regardless of play status:** the site's
  layout and topology, its keyed areas, the map, the fiction and faction
  stakes, what is on offer as reward and how it is earned.

This is a pre-play discipline, not a permanent ban. Once a session is played,
history is free to flow back onto the nodes it touched — what actually
happened is history, not a rebuild spec, so it cannot go stale. Where an
*unplayed* node must gesture at the rebuilt layer, it states what the
situation *rewards* — a reach front-liner, a tool-user, a control caster —
never who plays it or what it costs them.

## Link conventions

- **Page links:** `[Display Text](relative/path/to/file.md)` — repo-relative
  paths. Keep basenames globally unique so paths stay unambiguous.
- **Display text:** a human-readable label; a title-cased basename is fine
  when it reads naturally.
- **Image embeds:** `![Alt text](relative/path/to/image.ext)`.
- **Heading anchors:** `[text](path.md#heading-slug)`, or `[text](#heading-slug)`
  same-file. Slug rules: lowercase, spaces become hyphens, other punctuation
  drops.
- **Node pages never link into an unplayed session's page.** A session page
  is regenerable until played (the rebuild test above) — a node that
  hard-links into it inherits that fragility. Describe the material in prose
  instead; once the session is played, link it like any other page. `story/`
  pages are not the node web and may point at a live session build freely.

## Callouts

Callouts are Obsidian-style blockquotes: `> [!kind]` on the first line,
content on the following `>` lines. They are conventions, not syntax — a
renderer that knows them can style them, and anywhere else they read as
ordinary quoted text. Kinds:

- `read-aloud` — boxed text to read at the table. Player-facing only:
  immediate sensory description, visible writing, heard dialogue,
  written in plain spoken language an ordinary reader delivers
  comfortably. Interpretation and hidden causes stay in the adjacent
  DM prose.
- `dm-sidebar` — DM-only staging notes.
- `encounter-meta` — a combat's vitals block (party, enemies, budget,
  terrain, spotlight, objective).
- `warning` — a hazard or a rules gotcha the DM must not miss.
- `map` — a map embed with its caption.
- `art` — an image embed plus a caption line, with float variants
  `art-left` / `art-right`.

## Reference tokens

Rules entities in page prose are marked with reference tokens:
`{monster:Name}`, `{spell:Name}`, `{item:Name}`, `{skill:Name}`,
`{condition:Name}`, `{action:Name}`. The token names the entity exactly as
the rules source spells it. Like callouts, tokens degrade gracefully — a
renderer may turn them into rules links; as plain text they still read as a
deliberate, greppable citation. A token inside a backticked code span is
verbatim — that is how to *discuss* the syntax without invoking it.

## Log conventions

`log.md` records meaningful operations — page additions, restructures,
session absorptions, lint passes — grouped by date, newest first:

```markdown
## YYYY-MM-DD
* **Event-type**: summary
```

Event types: `Add`, `Update`, `Remove`, `Session`, `Lint`. Add today's entry
under today's date heading, creating the heading at the top of the file when
it isn't there yet. Keep each summary to 1–3 sentences with links to the
pages touched — the log is an index, not a journal. Deeper analysis belongs
on a wiki page, linked from the entry.
