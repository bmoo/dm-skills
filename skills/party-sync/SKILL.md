---
name: party-sync
description: >-
  Keep the campaign record's picture of the party current — refresh the
  party cache JSON and each player page's Character section so other skills
  and queries work from current sheets. Character data comes from whatever
  character tool the environment offers, or from the DM directly in chat.
  Use when the DM wants the party synced/refreshed, asks about a PC's
  current stats/spells/gear beyond what the campaign record holds, when
  another skill needs party numbers that are missing or unconfirmed since
  the last session, or for first-time party setup.
---

# Party Sync — character sheets → campaign record

Bring the campaign record's picture of the party up to date with the players' actual character sheets. Two artifacts stay current:

- **The party cache JSON** — the machine-readable party payload. Other skills and queries read this; between refreshes it is the authoritative numbers.
- **Each player page's `## Character` section** — written in the campaign record's own voice.

Where those live is the campaign repo's call: read its guide (`CLAUDE.md` or equivalent) for where player pages and the party cache are kept. If the repo doesn't say, ask the DM and offer to record the answer in its docs. The character source — a tool or the DM — is authoritative for anything on the sheet (stats, spells, gear, level). The campaign record is authoritative for everything else on a player page (personality, relationships, table notes) — never touch those sections.

## The intake chain

Where character data comes from. Take the first rung that answers; never skip past the chain to training-data memory:

1. **The campaign's own character tools.** If this environment has a character-sheet lookup tool installed (an MCP server or similar), read each character from it. Whatever the table has plugged in is the authority on its own characters — prefer it without comment on where its data comes from.
2. **The DM, in chat.** No tool, or a character the tool doesn't cover? Interview the DM in plain prose: ask what changed — level-ups, new spells, new items, corrections — and treat the answers as the sheet.

A number neither rung can source stays a **named gap**: tell the DM exactly which fields could not be sourced, file what's real, and never fill the gap from memory. Unknown species/class or obviously unfilled numbers are gaps too — file what's known (e.g. "Warlock 1, rest of the sheet unconfirmed") and never file placeholder stats as canon.

**Handle failures per character**, not wholesale: a character the tool errors on falls to the interview rung; sync what succeeds and report what fell back and why. A wholly failed sync changes nothing in the campaign record and earns no log entry — just report it.

## The party cache

The cache is the roster — there is no separate config file. One entry per character; each entry records the source that produced it (the tool's name, or `interview`):

```json
{
  "confirmedAt": "<ISO date of the last confirmed refresh>",
  "characters": [
    {
      "name": "<character name>",
      "player": "<player page basename, e.g. dan>",
      "class": "<class and subclass once chosen>",
      "level": 5,
      "source": "<tool name or \"interview\">",
      "ac": 16,
      "hp": 38,
      "spellSaveDC": 14,
      "notableItems": [],
      "notableSpells": [],
      "backstory": "<player-authored text, if provided>"
    }
  ]
}
```

**Required core per character: `name`, `player`, `class`, `level`, `source`** — this is what downstream skills actually read. Everything past the core is optional depth: fill it to whatever depth the source provided, and don't quiz a DM in chat for numbers nothing consumes. A stat-line offered is a stat-line filed; a stat-line unknown is simply absent.

`player` must match a player page basename — that's the join key for page updates.

## First-time setup (no cache yet)

Interview the DM in plain prose:

1. Ask who's in the party. With a character tool installed, list the characters it reports and propose the roster; without one, take the roster from the DM.
2. Map each character to an existing player page (list the basenames you find). Corroborate against what the campaign record already establishes (a page that says "Warlock" claims the campaign's Warlock), and put any mapping you can't corroborate to the DM rather than assuming.
3. Gather the required core for each character, plus whatever depth is offered, and run the first refresh below.
4. Offer the backstory intake: any player-authored backstory, traits, or goals the DM can paste into chat ride along (see the Backstory note in the refresh flow).

## Refresh flow

0. **No cache?** Do first-time setup above.
1. **Gather.** Walk the intake chain per character, diff the fresh data against the current cache to build the changelog, then write the new cache where the repo keeps it and stamp `confirmedAt`.
2. **Update player pages.** For each refreshed character, rewrite only the `## Character` section of the player's page (create it right after the intro line if absent; it replaces any older class/species section). Write it as the campaign record would — short prose plus a compact stat line, not a generated dump: character name, species, class/level/subclass, one-line combat stats (AC / HP / init) if known, spellcasting DC and notable spells if any, notable magic items. Everything deeper lives in the JSON.
   **Spotlight profile:** refresh the `## Spotlight profile` section's *character* half, creating the section on first refresh. From the refreshed sheet data, look up the build's features at its level via the sourcing chain in [`rules-sourcing.md`](rules-sourcing.md) and apply the flagging heuristic in the build-session skill's [`spotlight-doctrine.md`](../build-session/spotlight-doctrine.md) — **if that skill is installed**; without it, skip this Spotlight-profile refresh and leave the section as it stands: flag the reactive, situational, and niche-pick abilities, each with the staging that fires it and its pillar (combat / social / exploration). This precomputed list is what the generator skills read at design time. The *player* half (observed style, table delights, fired/denied history) belongs to the catch-up skill; never rewrite it from sheet data.
   **Backstory:** player-authored text is plot material the DM asked players to provide — offer the DM the chance to paste any new or changed backstory into chat, file it in the cache's `backstory` field, and summarize it on the player page (a `### Backstory` subsection under Character) so it can be woven into prep. Quote sparingly; the full text stays in the JSON.
3. **Bookkeeping.** If the repo keeps an index of player pages (a README table, a roster page), update the affected lines — a page that gains a real class/species is no longer a *stub*. If the repo keeps a change log, add an entry (`update`, 1–3 sentences: who changed and the headline diffs — level-ups, new spells, new items). Commit per the repo's own sync conventions.

## Party overview table

On request ("show me the party", "party overview"), render the cache as one compact table — one row per PC, columns like Character | Player | Class/Level | AC | HP | Key stats — from the party cache JSON (offer a refresh if unconfirmed, below). This is a read view, not a refresh; it changes nothing.

## Session-boundary freshness

`confirmedAt` records the last confirmed refresh. Sheets change when play happens, not when time passes: whenever a skill or query reads the cache and it hasn't been confirmed since your last session, say so and ask — any level-ups, new items, or new spells since last session? — before relying on the numbers. A quick "no changes" is a confirmation: stamp `confirmedAt` and move on. If the cache doesn't exist, run first-time setup.
