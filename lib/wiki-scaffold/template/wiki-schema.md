---
type: schema
title: Campaign Wiki Schema
description: The conventions this wiki runs on — the OKF v0.2 bundle rules it conforms to, and the campaign conventions layered on top.
tags: [meta, schema, conventions]
status: stable
generated: { by: dm-skills/setup, at: 2026-09-12T00:00:00-07:00 }
---

# Campaign Wiki Schema

This repo is an agent-maintained campaign wiki and an **Open Knowledge Format
v0.2 bundle**: markdown concepts with YAML frontmatter, a catalog generated
from that frontmatter, and a chronological log. The
[OKF v0.2 spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
governs frontmatter, the reserved files `index.md` and `log.md`, and link
form; section references below (§4.1, §5, …) are the spec's own. Everything
else in this file is campaign convention layered on top, and where this file
is stricter than the spec, the stricter rule wins here.

OKF's words are used throughout: a **concept** is any markdown file carrying
frontmatter (what the skills have called a page), and the **bundle** is this
directory tree, whose **bundle root** is the repo root. A concept's **id** is
its path within the bundle without the `.md` suffix.

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
| `scripts/`         | The wiki tooling — catalog generator, conformance check, groomer |

`index.md` is the generated catalog and `log.md` the chronological log. Both
are **reserved filenames** at every level (§3.1) — never use either name for a
concept. Index files are generated, never hand-edited, and carry no
frontmatter, with one exception: the bundle-root `index.md` declares
`okf_version: "0.2"` (§12), and the generator writes it.

## Frontmatter

Every concept opens with a YAML frontmatter block. One key is required (§4.1):

- `type:` — non-empty, and it **matches the concept's immediate directory**:
  `nodes/npcs/` → `type: npc`, `nodes/locations/` → `type: location`,
  `story/` → `type: story`, `players/` → `type: player`,
  `sessions/` → `type: session`. The seed-idea inboxes use
  `type: seed-ideas` wherever they live, and this file uses `type: schema`.
  (The spec allows any value; the directory rule is this wiki's.)

Five more are expected on every concept, and the checker warns when one is
missing:

- `title:` — the display name; the catalog prints it.
- `description:` — **one plain sentence with no markdown links.** The catalog
  prints it verbatim in more than one directory, so a link inside it resolves
  in one place and breaks in another.
- `tags:` — a short inline list; see *Tags* below.
- `status:` — one of `draft`, `stable`, `deprecated` (§5.4). Absent means
  `stable`, but state it anyway. What they mean here:
  - `draft` — not yet true at the table: seed inboxes, stubs, and **every
    session page until it is played**.
  - `stable` — in play. Canon and active alike.
  - `deprecated` — retired or superseded; kept so links and history still
    resolve.
- `generated:` — who last made a meaningful change and when (§5.2):
  `generated: { by: <actor>, at: <timestamp> }`. `by` is required within it.
  It records the **last writer**, not the original author.

Optional:

- `stale_after:` — an absolute instant after which the concept is stale
  (§5.5). Set it on concepts whose truth has a horizon — the live layer
  (`story/campaign-status.md`) and prep sheets, keyed to the next session
  date. The groomer reports what has gone stale; it never sets the value.

Two format rules apply to every timestamp and every actor:

- **Timestamps** are ISO 8601 with an explicit UTC offset (§5):
  `2026-09-12T19:30:00-07:00` or `2026-09-13T02:30:00Z`. Date-only values are
  not timestamps. The legacy `timestamp:` key is retired (§13.1); migrate it
  to `generated.at`.
- **Actors** (§7): a skill writes `dm-skills/<skill-name>` (a locally
  maintained skill writes `<repo>/<skill-name>`, e.g. `sd-campaign/lazy-dm`);
  the DM writing by hand is `human:<id>`. The `human:` prefix is what
  consumers key trust off, so never put it on machine-written content.

Any other key is permitted and preserved (§4.1); `aliases`, `date`,
`session_number` and the like are campaign extensions. Run
`python3 scripts/wiki-check.py --warnings` before committing — it fails on a
missing frontmatter block, an empty `type`, or a malformed reserved file
(§11), and warns on everything else. Run `python3 scripts/wiki-index.py`
after any batch of changes — the catalog is built from frontmatter, so
keeping `title`, `description`, and `status` current is how it stays true.

## Tags

Tags are cross-cutting; `type` and the directory already say what a concept
is, so a tag says something the directory does not. The suggested vocabulary,
with the checker warning on tags outside it:

| Tag          | Use on                                                        |
| ------------ | ------------------------------------------------------------- |
| `pc`         | a player character                                            |
| `recurring`  | an NPC or location the campaign returns to                    |
| `antagonist` | a faction or NPC working against the party                    |
| `patron`     | an NPC who gives the party work                               |
| `hub`        | a location sessions start from and return to                  |
| `historical` | a concept about the past rather than the present situation    |
| `played`     | a session page that has been run                              |
| `live-layer` | the campaign-status concept and its companions                |
| `prep-sheet` | a one-page prep condensation                                  |
| `seeds`      | a seed-ideas inbox                                            |
| `dungeon`    | a site with keyed areas and a map                             |
| `rewards`    | a treasure or reward pool                                     |

Setting tags — region, district, faction, and person names — are free-form and
exempt from the warning when they match the slug of an existing concept's
basename (`old-town`, `wardens`). Lifecycle words (`stub`, `prep`, `canon`)
are not tags any more; `status` carries them.

## Granularity and seed promotion

Each category directory has a seed-ideas inbox (e.g.
`nodes/npcs/npcs-seed-ideas.md`) — the catch-all for stubs that haven't yet
earned their own concept. A seed lives as an `## H2` section in the inbox.

A topic earns its own concept when any of these holds:

- it has grown past roughly 150 words,
- three or more other concepts reference it,
- the DM says so.

Promote the seed by moving its content to a new concept in the same directory
(frontmatter per the rules above, `status: draft` until it is true at the
table) and leaving no copy behind in the inbox.

**Session-bound content never earns its own node concept, regardless of
size.** A character or location that exists only inside one session's events
is inlined on that session page. It gets a node concept (or a seed) only when
it has life beyond the session that introduced it — other nodes reference it,
it is due to recur, or it anchors an investigation thread.

## The rebuild test

The inverse discipline: session-scoped content never lands on a node concept
ahead of play, even when the node itself is legitimate. The test — **if this
session were rebuilt from scratch against this node, would this content be
rebuilt too?** If yes, it is session output and belongs only on the session
page while that session is `draft`. A node holds what a rebuild would *read*,
not what a rebuild would *produce*.

- **Rebuilt every time — session page only, while unplayed:** encounter
  rosters and XP budgets, party size and level, named PCs, resource arcs,
  route pacing, contingency lists, boxed text written for one table.
- **Read every time — node concept, regardless of play status:** the site's
  layout and topology, its keyed areas, the map, the fiction and faction
  stakes, what is on offer as reward and how it is earned.

This is a pre-play discipline, not a permanent ban. Once a session is played
— its `status` flips to `stable` and it gains the `played` tag — history is
free to flow back onto the nodes it touched. Where an *unplayed* node must
gesture at the rebuilt layer, it states what the situation *rewards* — a
reach front-liner, a tool-user, a control caster — never who plays it or
what it costs them.

## Link conventions

Links use the spec's recommended **bundle-relative form** (§6.1): they begin
with `/` and resolve against the bundle root, so a link survives its source
being moved.

- **Concept links:** `[Display Text](/nodes/npcs/maren-tallow.md)`. Keep the
  `.md` suffix and keep basenames globally unique.
- **Display text:** a human-readable label; a title-cased basename is fine
  when it reads naturally.
- **Image embeds:** `![Alt text](/media/images/file.ext)`.
- **Heading anchors:** `[text](/path.md#heading-slug)`, or
  `[text](#heading-slug)` same-file. Slug rules: lowercase, spaces become
  hyphens, other punctuation drops.
- **Relative links** (`../npcs/x.md`) are conformant (§6.1) and the checker
  accepts them — Obsidian rewrites links to this form when a file is renamed —
  but new writing uses the `/` form.
- A link whose target does not exist is not an error (§6.1); the groomer
  reports it as a missing concept.
- **Node concepts never link into a `draft` session page.** A session page
  is regenerable until played (the rebuild test above) — a node that
  hard-links into it inherits that fragility. Describe the material in prose
  instead; once the session is played, link it like any other concept.
  `story/` concepts are not the node web and may point at a live session
  build freely.

## The catalog

`index.md` at the bundle root, and one in each category directory, is
generated from frontmatter (§8). Each entry is
`* [Title](/path/to/concept.md) - description`; a subdirectory entry is
`* [Label](subdir/) - description`. Nothing in an index is hand-written.

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

Rules entities in concept prose are marked with reference tokens:
`{monster:Name}`, `{spell:Name}`, `{item:Name}`, `{skill:Name}`,
`{condition:Name}`, `{action:Name}`. The token names the entity exactly as
the rules source spells it. Like callouts, tokens degrade gracefully — a
renderer may turn them into rules links; as plain text they still read as a
deliberate, greppable citation. A token inside a backticked code span is
verbatim — that is how to *discuss* the syntax without invoking it.

## Log conventions

`log.md` records meaningful operations — concept additions, restructures,
session absorptions, groomer passes — as date-grouped entries, newest first
(§9). It opens with an H1 title; date headings are `## YYYY-MM-DD`, the one
thing the spec requires of a log:

```markdown
# Campaign Log

## YYYY-MM-DD
* **Creation**: summary
```

Labels follow the spec's convention — `Creation`, `Update`, `Deprecation` —
plus two of this wiki's own: `Session` (a session absorbed) and `Lint` (a
groomer pass). Add today's entry under today's date heading, creating the
heading at the top of the file when it isn't there yet. Keep each summary to
1–3 sentences with links to the concepts touched — the log is an index, not a
journal. Deeper analysis belongs on a concept, linked from the entry.
