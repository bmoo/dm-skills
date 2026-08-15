---
name: setup
description: >-
  First-run setup for a campaign repo: connect the environment's D&D content
  tools, then offer to bootstrap a planning-wiki scaffold at the repo root.
  Use when the DM asks to set up or get started with this skill library in a
  campaign repo, or asks for a campaign wiki / planning-wiki scaffold. Every
  phase is offered, skippable, and safe to rerun.
---

# Setup — first run in a campaign repo

Two phases, in order. Offer each one; a declined phase is complete, and the
skill can be rerun later to pick it up. Everything here happens in the **DM's
campaign repo** — the folder this skill was invoked to set up — never inside
the installed skill folder, which is read-only at runtime.

## Phase 1 — connect content tools

Skills that source rules take the first rung that answers: any D&D content
lookup tool the environment exposes, falling back to the bundled SRD dataset.
The chain discovers tools fresh each session, so there is nothing to
configure or record — this phase makes sure the first rung finds what the
table already has, and connects more only when the DM wants it.

1. **Survey the session's tools.** Look through what this environment
   actually exposes for anything that answers D&D content lookups — stat
   blocks, spells, items, rules text — under whatever name and packaging it
   arrived (an MCP server, a plugin, or otherwise). Tell the DM what you
   found, or that the bundled SRD is currently the only source.
2. **Smoke-test each find.** Run one real lookup per content tool — an
   entity the DM names, or one the tool should carry — and show the DM what
   came back. A tool that answers is connected: every rules-sourcing skill
   reaches it from here on with no further setup. Whatever the table has
   plugged in is the authority on its own content.
3. **Offer to connect more.** Ask whether the table has a content tool that
   isn't plugged in yet. If yes, walk the DM through this environment's own
   mechanism for adding tools — registering an MCP server, installing a
   plugin — following that tool's install instructions, and say plainly
   that a freshly added tool usually appears only after the session
   restarts: restart, rerun `setup`, and the survey will find it.

The phase closes when every content tool the DM wants connected has answered
a smoke-test lookup — or the DM has said the bundled SRD is enough.

## Phase 2 — bootstrap the planning wiki

The offer: this library can scaffold an agent-maintained campaign wiki at the
repo root — a directory skeleton (`nodes/{locations,factions,npcs,events}`,
`story/`, `sessions/`, `players/`), a self-contained schema doc
(`wiki-schema.md`), catalog + conformance scripts (`scripts/`), and a
chronological log (`log.md`). Make the offer in those terms and let the DM
decline: the skills discover whatever shape a campaign repo already has, so a
repo without the scaffold loses nothing but the head start. A populated
example of the scaffold in play is the [Emberwick Vale example
campaign](https://github.com/bmoo/dm-skills/tree/main/examples/emberwick-vale)
— offer it as something to skim before deciding.

The template lives in `wiki-scaffold/template/` beside this file; the
CLAUDE.md block it pairs with is `wiki-scaffold/claude-md-block.md`.

On acceptance:

1. **Preflight the root.** The scaffold lands only on clean ground. If any of
   its top-level paths — `nodes/`, `story/`, `sessions/`, `players/`,
   `scripts/`, `wiki-schema.md`, `log.md`, `index.md` — already exists at the
   repo root, stop the phase and report exactly which: an existing wiki (or
   anything resembling one) is the DM's to migrate by hand, and every existing
   file survives untouched.
2. **Copy the template.** Copy the *contents* of `wiki-scaffold/template/`
   into the repo root, preserving the directory structure. Every file ships
   as-is; the one edit is the next step.
3. **Name the campaign.** Ask the DM for the campaign's name and set
   `WIKI_TITLE` in the copied `scripts/wiki_config.py` to it. Everything else
   in that file is a documented default the DM can revisit later.
4. **Offer the CLAUDE.md block.** Show the DM the full text of
   `wiki-scaffold/claude-md-block.md` and ask whether to append it to the
   campaign repo's `CLAUDE.md` — it is the standing behavior that keeps the
   wiki alive between skill runs (facts → pages, questions → wiki-first, log,
   regenerate, check). With consent, append it verbatim, creating `CLAUDE.md`
   if the repo has none. If declined, the scaffold stands anyway —
   `wiki-schema.md` still governs pages, and the block can be appended on a
   rerun.
5. **Start green.** From the repo root run `python3 scripts/wiki-index.py`,
   then `python3 scripts/wiki-check.py --warnings`. The phase is done when
   the check exits clean — zero errors, zero warnings — on the freshly
   generated catalog. Anything it flags on a fresh copy is yours to fix
   before handing over, not the DM's.

Close by pointing the DM at `wiki-schema.md` as the wiki's schema and
suggesting they commit the scaffold as its own commit, so campaign content
starts from a clean baseline.
