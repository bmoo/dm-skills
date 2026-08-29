---
name: combat-generator
description: >-
  Generate a combat encounter sized to the party's action economy with the
  SRD 5.2 XP-budget table, grounded in a campaign-record node and the
  campaign's own setting, carrying at least one complication and a spotlight
  texture, delivered with its machine-readable encounter-meta filing block.
  Use whenever the DM wants a fight/combat/encounter built for a node, a
  session, or a location — or asks what the party should fight — and
  whenever another skill needs one fight sized.
---

# Combat Generator

Build a **situation**, not a scripted fight (the *Don't Prep Plots* frame):
the right XP budget, enemies that belong in the place, terrain to fight over,
and a **complication** that turns a hit-point race into a decision.

Reference files sit beside this one; load each when its step says to:

- [`xp-budget.md`](xp-budget.md) — the SRD 5.2 budget table and the
  action-economy guardrails.
- [`complications.md`](complications.md) — the menu of complications.
- [`spotlight-doctrine.md`](spotlight-doctrine.md) and
  [`class-patterns.md`](class-patterns.md) — spotlight doctrine: the data
  ladder Step 2 climbs, the texture palette and legibility rules Step 5
  applies, the per-class staging patterns for an aimed fight.

## Inputs

A caller — the DM mid-prep, or another skill invoking this one with a wider
prep plan of its own — may hand any of these in already settled; Steps 1–2
restate them, so skip to Step 3 when they all arrive:

- the pinned fight situation — node/location, the enemies-or-faction and
  their objective, the terrain potential (Step 1's five pins; don't re-pin
  what arrives settled);
- the party and each PC's Spotlight profile (Step 2's read);
- the difficulty band — Low / Moderate / High (the caller's pick, not a
  default);
- the fight's **allocated spotlight beat** — its texture and, if aimed or
  puzzle, the target PC, when the caller runs a spotlight plan spanning more
  than this fight. Such a plan is the caller's transient state, never read
  off a page: spend a handed beat via Step 5's *Handed beat first* path
  rather than aiming independently, and with no beat handed Step 5
  self-serves.

Anything not handed in, Steps 1–2 pin from the campaign record and the DM's
ask.

The product is the runnable encounter block (Step 7's shape) **and its
`> [!encounter-meta]` filing block** (the *Filing format* section), complete
and internally consistent — a caller embeds that block as-is, with no
re-derived budget and no re-picked complication. Whether anything files onto
a page is settled at the offer, once.

## Rules sourcing — non-negotiable

The sourcing doctrine and its lookup chain are stated once, in
[`rules-sourcing.md`](rules-sourcing.md) beside this file, and bind every
rules detail this skill places — monster stat blocks, XP values, item text.
Look up every creature you place; confirm its XP before you spend it; browse
the chosen source's catalog *before* Step 4 shortlists.

## Step 1 — Pin the situation

*Handed in settled? Skip to Step 3.* Otherwise, settle five things before
any math — where one is ambiguous and the choice changes the fight, ask in
one line; otherwise pick the obvious reading and name it:

- **Where.** The node or location. If the DM named one with its own page in
  the campaign record, **read the whole page** — its inhabitants, factions,
  terrain, and clue/lead notes are your enemy roster and complication seeds.
  If only a vibe was given, pick the fitting node or say you're inventing
  the place.
- **Who & why.** Which faction or creatures, and what they want *right
  now* — enemies with an objective (guard, retrieve, stall, flee) drive
  better fights than enemies who exist to be killed.
- **Difficulty.** Low / Moderate / High. If unstated, default **Moderate**
  and say so.
- **Setting frame.** From the campaign record, not assumption — the tone,
  the world's rules, what's mundane vs. hidden — so the fight reads as part
  of *this* campaign.
- **Terrain potential.** If the node's layout plausibly supports multiple
  levels — a balcony, a stairwell, a parking structure — default to laying
  the fight out across them; a single open space stays flat. Independent of
  whether elevation ends up as Step 6's chosen complication.

## Step 2 — Pin the party (action economy)

*Handed in settled? Skip to Step 3.* The encounter must match **how many
characters act and what they can do**, alongside level:

- **Head-count and classes** from wherever this repo tracks player
  characters; where a sheet is undecided, leave it undecided. Where classes
  aren't set, size to head-count and level, and flag that the
  action-economy read will sharpen once classes are known.
- **Builds, not just head-count.** For each PC with a sheet, read their
  **Spotlight profile** via the
  [data ladder in `spotlight-doctrine.md`](spotlight-doctrine.md#the-data-ladder):
  the character half carries the flagged setup-dependent abilities, the
  player half the observed style that outranks them. A missing or stale
  rung self-heals per the ladder — read it regardless.
- **Level.** Use the level the DM gives; if unstated, derive it from the
  repo's leveling rules and campaign progress. State the level you're
  sizing for.

## Step 3 — Compute the XP budget

Open [`xp-budget.md`](xp-budget.md). Cross-reference party level × difficulty
for the **per-character** number, **multiply by party size**, and state the
total budget explicitly (e.g. "Moderate, level 2, 5 PCs → 150 × 5 =
**750 XP**"). This number is the hard ceiling for Step 4.

## Step 4 — Spend the budget on enemies that belong

Choose creatures that fit the node and the setting, look up each one's 2024 XP
via the sourcing chain, and spend toward the budget without going over,
honoring the **action-economy guardrails** in the budget reference — shape vs.
party size, the three-monster-type cap, CR spikes.

Show the arithmetic — each creature, its XP, the running total, the remainder.
The fight is sized when the math is on the page and under budget.

## Step 5 — Give the fight a texture (spotlight doctrine)

Open [`spotlight-doctrine.md`](spotlight-doctrine.md), and
[`class-patterns.md`](class-patterns.md) if the fight ends up
aimed:

- **Handed beat first.** A caller running a wider spotlight plan has already
  allocated this fight's texture and target — take them from the handed
  beat. Where the fight can't honor it, say so in the hand-back: the plan is
  the caller's, and reconciling it against the finished work is the
  caller's job.
- **No beat → self-serve.** Run the doctrine's variety check against the
  campaign record's structured combat data (fallback: recent encounter-meta
  `Spotlight:` lines), then pick a texture from the palette. No fight must aim
  at anyone — plain is a legitimate result.
- **Texturing stages the roster Step 4 already bought** — adding creatures is
  Step 4's job, finished before this step.
- **Set legibility on an aimed or puzzle beat.** Texture picks *what* fires;
  the doctrine's [Legibility](spotlight-doctrine.md#legibility) axis picks
  *how plainly the DM points at it*. Read the target PC's **Table experience**
  rung from their profile's player half and calibrate the tell as that section
  prescribes — this skill reads the rung, never writes it.

The step is done when the fight names its texture — and, if aimed or puzzle,
whom it shoots at, what staging fires their flagged ability, its legibility
read against the target's Table experience, and that the staging isn't a
repeated tell.

## Step 6 — Add at least one complication

Open [`complications.md`](complications.md) and choose **at least one**
complication that fits the enemies, the node, and the campaign's setting.
Prefer one that reframes the *objective* (a timer, a protected target, innocent
minions) over one that only adds damage, and wire it into the terrain and the
enemies' goal so it reads as part of the fiction. If the encounter sits on a
location's page and this repo tracks clues/leads, check whether the
complication is a place to plant one toward another node, and call that out.

One complication is the floor, not the target: for a set-piece fight, take
**two, from different menu sections** — an objective twist plus a battlefield
element multiplies the fight's possible states rather than adding to them. For
a fight meant to run short, stop at one. An encounter without a complication is
not finished.

## Step 7 — Deliver

Present the encounter in chat as a runnable block:

- **Header** — node, party level & size, difficulty, total XP budget.
- **Enemies** — each creature with its XP and the budget math; the total vs.
  budget.
- **Terrain & setup** — where they are, elevation/cover/hazards, how the fight
  opens. Multi-level terrain shows which enemies and cover sit on which level,
  not just that the room has levels.
- **The spotlight** — the fight's texture (aimed / puzzle / steamroll / plain /
  curveball); if aimed or puzzle, who it shoots at and the staging that fires
  their ability; for a curveball, whose tricks it denies.
- **The complication** — named, with one line on how to run it.
- **Tactics** — what the enemies do round one and how they react (flee, parley,
  call reinforcements), tied to their objective.
- **Clue note** — if it sits on a node, the lead a complication outcome can
  carry.

### Definition of done

Before you offer, **compose the encounter-meta callout** (the *Filing format*
section below) in context from the numbers Steps 3–6 settled — it is what a
caller embeds — then run both parts of the shared verification protocol in
[`verification.md`](verification.md) over it. Composing is not filing: the
block is written to a page only on the DM's yes below.

**The self-check** (Part 1) hands the drafted block to
`run_checks(output, "combat-generator", [<the ids below, under the
combat-generator/ qualifier>])`. Each id is one promise:

| Check id | Promise |
|---|---|
| `encounter-meta-required-lines` | the six required lines are present |
| `enemies-line-arithmetic` | the `Enemies:` line sums — each creature × count with looked-up XP reaches the stated total |
| `budget-line-arithmetic` | per-char × N = budget, spent ≤ budget |
| `per-char-matches-budget-table` | the per-char figure matches the budget table for that level × difficulty |
| `distinct-stat-block-cap` | never more than three distinct stat blocks |
| `stat-block-refs-on-enemies-line` | every creature on the `Enemies:` line carries its `{monster:Name}` token or stat-block link |
| `spotlight-texture-in-palette` | the `Spotlight:` texture is one of the five |
| `targeted-spotlight-names-target-and-staging` | an aimed or puzzle spotlight names whom it shoots at and carries its staging clause |

**The fresh check** (Part 2) grades the two criteria this skill owns, as
its own text states them — the prose-reference rule in *Filing format*
below and the fragile-creatures rule in
[`xp-budget.md`](xp-budget.md) — named by their stable check ids
`[combat-generator/stat-block-refs-in-prose,
combat-generator/swarm-carries-fragile-creatures]`, with the party roster as
the checker's third input.

Then **offer**, but don't assume: to file the encounter into wherever this repo
keeps session prep or the location page, and to log it if the repo keeps a
change log. On an exhausted loop this same offer carries the surviving
findings; with no findings it reads exactly as it always has. A generated fight
stays a chat prep aid until the DM says to keep it. Wait for the yes — and
when a caller with a wider build embeds the block, the one offer belongs to
that caller, made once for the whole work.

## Filing format — the encounter-meta block

On the yes, the encounter's vitals land on the page as an **encounter-meta
callout** (the prose — terrain, tactics, the complication's staging — lives
around it as normal page text). This is the machine-findable summary other
tooling greps for: the `Spotlight:` line is the variety check's fallback
ledger before played sessions exist
([`spotlight-doctrine.md`](spotlight-doctrine.md)) and half of what
play-absorption tooling reconciles afterward — a spotlight plan is transient,
so an aimed or puzzle fight names the PC it shoots at. **Never file an
encounter without one.**

**The block's shape is specified once, and not here.** It lives at
[`encounter-meta-format.md`](encounter-meta-format.md) beside this file —
the template, its required labels, and the shape both the library's parser
and the deterministic checker are pinned to. A **citation, not a file to
open at run time** — you already know the shape; the pointer is where a
shape change lands (library sync obligations: `docs/campaign-contract.md`).

What this skill owns is what goes *in* those fields. **Every creature name — on
the `Enemies:` line and in the surrounding terrain/tactics prose — is written
in the repo's stat-block reference convention** (`{monster:Name}` where the
render tokens are in use), so downstream renderers link it to its stat block. A
published creature links to its public reference page; a homebrew or reskinned
creature references its stat block's page in the campaign record instead — a
bare creature name is a filing defect, never a valid entry. The `Objective:`
line carries the win condition, and the complication usually lives there; the
`Spotlight:` line names the fight's texture, and an aimed or puzzle fight names
whom it shoots at and the staging that fires their ability.
