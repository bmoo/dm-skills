# Building a Fight

The fight procedure of the `build-session` skill. Step 5 of a session build
loads it for each fight the session needs; the keyed-site procedure
([`dungeon.md`](dungeon.md)) loads it for each fight in a site. Build a
**situation**, not a scripted fight (the *Don't Prep Plots* frame): the
right XP budget, enemies that belong in the place, terrain to fight over, and a
**complication** that turns a hit-point race into a decision.

Two reference files sit beside this one; load them when their step says to:

- [`xp-budget.md`](xp-budget.md) — the SRD 5.2 budget table and the
  action-economy guardrails.
- [`complications.md`](complications.md) — the menu of complications.

Spotlight doctrine lives beside this file — Steps 2 and 5 load
[`spotlight.md`](spotlight.md)'s data ladder,
[`spotlight-doctrine.md`](spotlight-doctrine.md), and
[`class-patterns.md`](class-patterns.md).

## Inputs

A session build has already settled these by the time it loads this file —
Steps 1–2 restate them, so skip to Step 3:

- the pinned fight situation — node/location, the enemies-or-faction and their
  objective, the terrain potential (Step 1, already settled; don't re-pin it);
- the party and each PC's Spotlight profile (Step 2's read);
- the difficulty band — Low / Moderate / High (the run's pick, not a default);
- the fight's **allocated spotlight beat** — its texture and, if aimed or
  puzzle, the target PC, from the session spotlight plan. The plan is
  transient prep-run state, never read off a page; apply the beat via
  Step 5's *Session plan first* path rather than aiming independently, and
  with no plan in the run Step 5 self-serves.

A fight built outside a full session build — a one-off the DM asks for
mid-prep — pins whatever is still open via Steps 1–2 first.

The product is the runnable encounter block (Step 7's shape) **and its
`> [!encounter-meta]` filing block** (the *Filing format* section), complete
and internally consistent — the page build embeds that block as-is, with no
re-derived budget and no re-picked complication.

## Rules sourcing — non-negotiable

This block is the library's one statement of the sourcing doctrine; the
keyed-site procedure ([`dungeon.md`](dungeon.md)) follows it too, for every
content type it places.

- **MUST** source all rules content — monster stat blocks, XP values, item
  text, trap and door mechanics, any rules detail — from the sourcing chain in
  [`rules-sourcing.md`](rules-sourcing.md),
  never from training-data memory (the 2024 rules differ from 2014).
  Look up every creature and item you place; confirm a creature's XP before
  you spend it.
- The chain prefers whatever D&D content tools this environment has installed,
  then falls back to the bundled SRD dataset — take the first rung that answers.
- **MUST** browse the chosen source's catalog (its listings, filtered by
  type/CR/etc.) *before* shortlisting — never shortlist from memory, which
  silently defaults to famous core-book entries and ignores what the table's
  sources actually offer.
- If nothing in the chain answers, **say so and name the gap** — hand the DM
  what could not be sourced instead of filling it from memory.

## Step 1 — Pin the situation

*Inside a session build these arrive settled from the prep run — skip to
Step 3.* Otherwise, settle five things before any math — where one is
ambiguous and the choice changes the fight, ask in one line; otherwise pick
the obvious reading and name it:

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

*Inside a session build the party and rosters arrive from the prep run.*
The encounter must match **how many characters act and what they can do**,
alongside level:

- **Head-count and classes** from wherever this repo tracks player
  characters; where a sheet is undecided, leave it undecided. Where classes
  aren't set, size to head-count and level, and flag that the
  action-economy read will sharpen once classes are known.
- **Builds, not just head-count.** For each PC with a sheet, read their
  **Spotlight profile** via the
  [data ladder in `spotlight.md`](spotlight.md#the-data-ladder): the
  character half carries the flagged setup-dependent abilities, the player
  half the observed style that outranks them. A missing or stale rung
  self-heals per the ladder — read it regardless.
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

- **Session plan first.** Inside a session build the session has already
  allocated a spotlight budget — take the fight's texture and target from it.
  The plan is **transient**: it lives in the prep run, never as a table on
  the session page. Where the fight can't honor a planned beat, say so —
  the plan is the session's, and Step 5's reconciliation pass
  (`SKILL.md`) owns squaring it against the finished page.
- **No plan → self-serve.** Run the doctrine's variety check against the
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
section below) in context from the numbers Steps 3–6 settled — it is what the
page build embeds — then run both parts of the shared verification protocol in
[`verification.md`](verification.md) over it. Composing is not filing: the
block is written to a page only on the DM's yes below.

**The self-check** (Part 1) hands the drafted block to
`run_checks(output, "build-session", [<the ids below, under the
build-session/ qualifier>])`. Each id is one promise:

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

**The fresh check** (Part 2) grades the two criteria this procedure owns, as
this skill's own text states them — the prose-reference rule in *Filing
format* below and the fragile-creatures rule in
[`xp-budget.md`](xp-budget.md) — named by their stable check ids
`[build-session/stat-block-refs-in-prose,
build-session/swarm-carries-fragile-creatures]`, with the party roster as
the checker's third input.

Then **offer**, but don't assume: to file the encounter into wherever this repo
keeps session prep or the location page, and to log it if the repo keeps a
change log. On an exhausted loop this same offer carries the surviving
findings; with no findings it reads exactly as it always has. A generated fight
stays a chat prep aid until the DM says to keep it. Wait for the yes.

## Filing format — the encounter-meta block

On the yes, the encounter's vitals land on the page as an **encounter-meta
callout** (the prose — terrain, tactics, the complication's staging — lives
around it as normal page text). This is the machine-findable summary other
tooling greps for: the `Spotlight:` line is the variety check's fallback ledger
before played sessions exist (see [`spotlight.md`](spotlight.md)) and — because the
session spotlight plan is transient — half of what catch-up reconciles after
play, so an aimed or puzzle fight names the PC it shoots at. **Never file an
encounter without one.**

**The block's shape is specified once, and not here.** It lives at
[*The encounter-meta block*](session-page-format.md#the-encounter-meta-block)
in `session-page-format.md` — the template, its required labels, and the
shape both the session parser and the deterministic checker are pinned to;
the keyed-site procedure files its fights in the same shape. A **citation,
not a file to open at run time** — you already know the shape; the pointer
is where a shape change lands (library sync obligations:
`docs/campaign-contract.md`).

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
