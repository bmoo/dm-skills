---
name: spotlight
description: >-
  Spotlight doctrine — shoot your monks. Use when the DM wants to aim a
  situation (a fight, a scene, a session) at a PC's build, audit prep for
  spotlight coverage or repeated tells, or asks who's due a spotlight. The
  fight-level prep skills load this skill's doctrine files for their spotlight
  steps; a session build invokes this skill's delegate interface for the
  session's spotlight plan.
---

# Spotlight

A player's build is a **statement** — *this is what I want to do at the table*
— and most of a statement is reactive or situational: it fires only if the DM
stages for it. This skill owns the doctrine for honoring statements without
turning every scene into an engineered showcase.

Two reference files sit beside this one:

- [`doctrine.md`](doctrine.md) — the pacing rules: the session budget, the
  texture palette, the anti-tell rules, the flagging heuristic, evidence and
  precedence.
- [`class-patterns.md`](class-patterns.md) — per-class staging patterns,
  combat and out-of-combat, verified against the 2024 rules. Patterns, not
  inventory.

This skill owns both files. Three consumers load them directly:
combat-generator and dungeon-generator (texturing fights) and party-sync
(sync-time flagging). A caller that needs a whole session's plan **invokes
this skill through the delegate interface below** rather than opening these
files. Changing their shape is a breaking change (library sync obligations:
`docs/campaign-contract.md`).

## The data ladder

Reading a PC for spotlighting climbs down this ladder — take the highest rung
that is present and fresh. The ladder self-heals: the DM never has to
remember the dependency.

1. **The Spotlight profile** on the player page. Its *character half* is the
   flagged-ability list party-sync precomputes at sync time; its *player
   half* is observed play, maintained by catch-up from this campaign's
   transcripts. Player half outranks character half; both outrank
   class-generic patterns.
2. **Profile missing or stale (>7 days)?** Derive the flags live: read the
   party cache wherever this repo keeps synced sheets, look up the build's
   features at its level via the sourcing chain in
   [`rules-sourcing.md`](rules-sourcing.md), and apply
   the flagging heuristic in `doctrine.md`. Offer to persist the result to
   the profile. Never auto-trigger a re-scrape of a third-party service — a
   real re-sync is the DM's call.
3. **No party cache at all?** Say so and offer a party-sync run. Don't
   spotlight from memory.

**Evidence for the variety check** is the structured combat data in this
campaign's record repo (the repo's guide says where): the encounter ledger
and per-session JSONs. **Only this campaign's record feeds this** — never
another campaign's data, even for the same players. Before played sessions
exist, fall back to `Spotlight:` lines in prepped encounter-meta blocks
(format: combat-generator's *Filing format* section).

## Invoked as a delegate — the interface

This skill runs two ways. **Directly**, the DM asks for an aim, an audit, or
who's due, and the three modes below answer. **As a delegate**, another skill
— `build-session` prepping a session — hands you the session and asks for its
**spotlight plan**; the DM never addresses this path, and the doctrine files
are internals behind it: a caller that needs a plan invokes this interface
rather than loading them.

**What a caller hands you to allocate one session's plan:** the party (so the
data ladder above has a roster to climb for each PC), the session's **planned
situations** — the likely set-pieces and scenes, with the pillar each lives in
(social, exploration, combat) — and any beat already fixed by an earlier run or
by the DM. Planned situations only: reserve pressure a caller may never inject
is not yours to allocate against.

**What you hand back — in-run, never filed:** the **roster you read** — each PC
with the flagged abilities and the **Table experience** rung the ladder
resolved, so the caller can spend it into its own checks and its fight- and
site-level delegates without a second ladder pass — and the session's
**allocated budget**: one line per PC, either a real beat with its pillar or a
named rest, plus a
texture per likely set-piece from the palette, and, for every **Aimed** or
**Puzzle** beat, its **legibility** — *how plainly the DM points at it*. Set
legibility per [`doctrine.md`](doctrine.md#legibility): read the target PC's
**Table experience** rung off their profile's player half and calibrate the
tell as that section prescribes — its vocabulary, its never-default rule, and
its missing/off-list handling all live there, and this pass only reads the
rung, never writes it. Allocate from the record — profiles and the recent
ledger — not from memory; the ladder's own fallbacks apply when a rung is
missing or stale.

**What the caller is responsible for:** the plan is **transient prep-run
state** handed back in chat, so the caller spends it inside the same run — into
its own page or sheet, and down to any fight- or site-level skill it delegates
to, which spends the beat it is handed instead of aiming independently. The
caller owns whether every PC came out covered, whether a beat it could not
stage is reported, and what (if anything) reaches a page: this skill files
nothing.

## Direct invocation

When invoked directly rather than through another skill:

- **Aim** — "aim this encounter at this PC", "spotlight this player somewhere
  this session": load `doctrine.md`, climb the ladder, stage per the texture
  palette and the class patterns. Done when the situation names its texture
  and, if aimed, whose flagged ability the staging fires.
- **Audit** — "audit this prep for spotlights": check every prepared
  situation against the doctrine — texture named? staging a repeated tell?
  budget spread across the session's pillars? every PC due a beat getting one
  somewhere? Done when each situation has a verdict and the gaps are listed.
- **Who's due** — read the profiles and the ledger; answer which PCs'
  statements have gone longest unhonored, each with the staging that would
  pay it off.
