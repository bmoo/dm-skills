---
name: combat-generator
description: >-
  Generate a combat encounter sized to the party's action economy with the SRD
  5.2 XP-budget table, grounded in a campaign-record node and the campaign's own
  setting, carrying at least one complication and a spotlight texture. Use
  whenever the DM wants to generate a fight/combat/encounter for a node, a
  session, or a location — or asks what the party should fight.
---

# Combat Generator

Build a **situation**, not a scripted fight (the *Don't Prep Plots* frame): the
right XP budget, enemies that belong in the place, terrain to fight over, and a
**complication** that turns a hit-point race into a decision.

Two reference files sit beside this one; load them when their step says to:

- [`xp-budget.md`](xp-budget.md) — the SRD 5.2 budget table and the
  action-economy guardrails.
- [`complications.md`](complications.md) — the menu of complications.

Spotlight doctrine lives in the sibling [`spotlight` skill](../spotlight/SKILL.md)
— Steps 2 and 5 load its `doctrine.md` and `class-patterns.md`. Those two files
are this skill's **internals**: `dungeon-generator` and `build-session` size
their fights through the delegate interface below and never reach in (library
sync obligations: `docs/campaign-contract.md`).

## Invoked as a delegate — the interface

**Standalone**, the DM asks for a fight and Steps 1–2 pin the situation and
party from the record. **As a delegate**, `dungeon-generator` (sizing a keyed
site's fight) or `build-session` (sizing a session's fight) hands you one fight
to size; Steps 1–2's inputs come from the caller and every step from Step 3 on
runs the same.

**The caller hands you:**

- the pinned fight situation — node/location, the enemies-or-faction and their
  objective, the terrain potential (Step 1, already settled; don't re-pin it);
- the party and each PC's Spotlight profile (Step 2's read, done for the
  caller's table);
- the difficulty band — Low / Moderate / High (the caller's, not a default);
- the fight's **allocated spotlight beat** — its texture and, if aimed or
  puzzle, the target PC. The beat comes down the chain from the session
  spotlight plan, whose shape `spotlight` owns as the return of its delegate
  interface: inside a session run `build-session` invokes it; a standalone
  dungeon self-allocates its own session-scale budget. Apply the beat via
  Step 5's *Session plan first* path rather than aiming independently — and,
  because it is transient and never read off a page, ask for it if a prep-run
  caller didn't hand it over.

**You hand back** the runnable encounter block (Step 7's shape) **and its
`> [!encounter-meta]` filing block** (the *Filing format* section), complete
and internally consistent — the caller embeds that block as-is and does not
re-derive the budget, re-pick the complication, or reshape the meta block.
Whether it files onto a page is the caller's call, made once for the whole
site or session.

## Rules sourcing — non-negotiable

- **MUST** source all rules content — monster stat blocks, XP values, any rules
  detail — from the sourcing chain in [`rules-sourcing.md`](rules-sourcing.md),
  never from training-data memory (2024 stat blocks and XP differ from 2014).
  Look up every creature you place; confirm its XP before you spend it.
- The chain prefers whatever D&D content tools this environment has installed,
  then falls back to the bundled SRD dataset — take the first rung that answers.
- **MUST** browse the chosen source's catalog (its listings, filtered by
  type/CR/etc.) *before* shortlisting — never shortlist from memory, which
  silently defaults to famous core-book entries and ignores what the table's
  sources actually offer.
- If nothing in the chain answers, **say so and name the gap** — hand the DM
  what could not be sourced instead of filling it from memory.

## Step 1 — Pin the situation

*Invoked as a delegate, the caller hands this in — skip to Step 3.* Standalone,
settle five things before any math:

- **Where.** The node or location the fight happens at. If the DM named a
  location with its own page in the campaign record, **read the whole page** —
  its inhabitants, factions, terrain, and clue/lead notes are your enemy roster
  and your complication seeds. If only a vibe was given, pick the fitting node
  or say you're inventing the place.
- **Who & why.** Which faction or creatures, and what they want *right now* —
  enemies with an objective (guard, retrieve, stall, flee) drive better fights
  than enemies who exist to be killed. Pull from the location's faction ties
  and any live campaign-status tracking this repo keeps.
- **Difficulty.** Low / Moderate / High (the budget reference defines each
  band). If unstated, default **Moderate** and say so.
- **Setting frame.** Take it from the campaign record, not from assumption —
  the location's page and the repo's setting material carry the tone, the
  world's rules, and what's mundane vs. hidden. Hold that for the complication
  and the terrain so the fight reads as part of *this* campaign.
- **Terrain potential.** If the node's physical layout plausibly supports
  multiple levels — a balcony, scaffolding, a stairwell, a parking structure —
  default to laying the fight out across them; if the node reads as a single
  open space, keep it flat. Independent of whether elevation ends up as
  Step 6's chosen complication.

If any of the five is ambiguous and the choice changes the fight, ask in one
line; otherwise pick the obvious reading and name your choice.

## Step 2 — Pin the party (action economy)

*Invoked as a delegate, the caller hands the party and rosters in.* The
encounter must match **how many characters act and what they can do**,
alongside level.

- **Head-count and classes** from wherever this repo tracks player characters
  (a `players/` folder, character sheets, a session log). Where a sheet is
  undecided, leave it undecided.
- **Builds, not just head-count.** For each PC with a sheet, read their
  **Spotlight profile** via the
  [spotlight skill's data ladder](../spotlight/SKILL.md#the-data-ladder): the
  character half carries the flagged setup-dependent abilities, the player half
  the observed style that outranks them. A missing or stale rung self-heals per
  the ladder — read it regardless.
- **Level.** Use the level the DM gives; if unstated, derive it from the repo's
  leveling rules and campaign-progress tracking. State the level you're sizing
  for.
- **Composition gaps.** Where classes aren't set, size to head-count and level,
  and flag that the action-economy read will sharpen once classes are known
  (no healer or no ranged answer changes which complications bite).

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

Open the spotlight skill's [`doctrine.md`](../spotlight/doctrine.md), and
[`class-patterns.md`](../spotlight/class-patterns.md) if the fight ends up
aimed:

- **Session plan first.** Inside a session prep run the session has already
  allocated a spotlight budget — take the fight's texture and target from it.
  The plan is **transient**: it lives in the prep run that invoked you, never
  as a table on the session page, so ask for it if it wasn't handed over.
  Where the fight can't honor a planned beat, say so — the plan is the
  session's, and build-session owns reconciling it.
- **No plan → self-serve.** Run the doctrine's variety check against the
  campaign record's structured combat data (fallback: recent encounter-meta
  `Spotlight:` lines), then pick a texture from the palette. No fight must aim
  at anyone — plain is a legitimate result.
- **Texturing stages the roster Step 4 already bought** — adding creatures is
  Step 4's job, finished before this step.
- **Set legibility on an aimed or puzzle beat.** Texture picks *what* fires;
  the doctrine's [Legibility](../spotlight/doctrine.md#legibility) axis picks
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

### Definition of done — the mechanical self-check

Before you offer, **compose the encounter-meta callout** (the *Filing format*
section below) in context and check it against its own mechanical promises.
Composing is not filing: the block is drafted to self-check and written to a
page only on the DM's yes. A delegate run already holds this block (it is the
hand-back); a standalone run drafts it now from the numbers Steps 3–6 settled.

- **Run the checks.** Hand the drafted block to
  `run_checks(output, "combat-generator",
  ["combat-generator/encounter-meta-required-lines",
  "combat-generator/enemies-line-arithmetic",
  "combat-generator/budget-line-arithmetic",
  "combat-generator/per-char-matches-budget-table",
  "combat-generator/distinct-stat-block-cap",
  "combat-generator/stat-block-refs-on-enemies-line",
  "combat-generator/spotlight-texture-in-palette",
  "combat-generator/targeted-spotlight-names-target-and-staging"])` — the
  runnable checks live beside this skill at
  [`scripts/mechanical_checker`](scripts/mechanical_checker). Each check is one
  promise: **encounter-meta-required-lines** the six required lines are
  present; **enemies-line-arithmetic** the `Enemies:` line sums (each creature
  × count with looked-up XP reaches the stated total);
  **budget-line-arithmetic** per-char × N = budget, spent ≤ budget;
  **per-char-matches-budget-table** the per-char figure matches the budget table for
  that level × difficulty; **distinct-stat-block-cap** never more than three
  distinct stat blocks; **stat-block-refs-on-enemies-line** every creature on
  the `Enemies:` line carries its `{monster:Name}` token or stat-block link;
  **spotlight-texture-in-palette** the `Spotlight:` texture is one of the five;
  **targeted-spotlight-names-target-and-staging** an aimed or puzzle spotlight
  names whom it shoots at and carries its staging clause.
- **Self-heal, silently.** Drive each finding through the shared
  [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md) —
  re-derive the sum, re-add the missing line, re-source the bare name — up to
  **three attempts per check**, re-running that check after each. A finding
  that heals is telemetry; this is arithmetic you fix, not arithmetic you ask
  the DM to adjudicate.
- **Escalate what won't heal.** A check still failing after three attempts is
  **unhealable** — surface it in the offer below as a terminal mechanical
  escalation: which check, expected vs. actual, where in the block, how many
  attempts. A compiler is certain — no confidence hedge.
- **File nothing.** The self-check runs over the block you hold in context; the
  DM's yes below stays the sole trigger that writes to a page. The loop's one
  write is out-of-band: it appends a **run record** for the pass, then each
  finding — healed and unhealable alike — to the validator findings log, per
  [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md).

This is the deterministic slice of done. The subjective promises are the
fresh check below — run it after this self-check, before you offer.

### Definition of done — the fresh check

The subjective promises — is a creature named *in the prose*, does a swarm
carry a fragile creature — need a grader that isn't you: you mark your own
homework, and you mark it kindly. When the block is drafted and self-healed,
hand it to **one fresh-context checker**, one round. This gates *completion*:
the offer below forms only when the check has run and its findings are
answered.

- **Launch it fresh — output, criteria, roster, nothing else.** Start a
  genuinely fresh-context, **read-only** checker and hand it **only three
  things**: (1) the drafted encounter block exactly as it stands, (2) the two
  criteria as this skill's own text states them — the prose-reference rule
  in *Filing format* below, the fragile-creatures rule in
  [`xp-budget.md`](xp-budget.md) — named as combat-generator's rows
  `[combat-generator/stat-block-refs-in-prose,
  combat-generator/swarm-carries-fragile-creatures]`, and (3) the party
  roster. Withhold your own reasoning — chain of thought, heal telemetry,
  any note arguing the fight is good: a checker that sees only what a reader
  sees grades what a reader gets. It returns a plain `approve | disapprove`;
  every finding cites its inventory row, where in the block it sits, the
  **quoted span** it fired on, and a one-line **reason** — and carries **no
  fix**. Its default when it cannot tell is **disapprove**. Log the pass
  through the shared library
  ([`scripts/mechanical_checker`](scripts/mechanical_checker), module
  `findings_log`): one `log_run` with `tier="judgement"` and the verdict,
  one `log_finding` per finding with its quoted span and reason.
- **On `disapprove`, one fix pass — no re-grade.** Refine the block against
  the findings once (the promise-pointers *are* the instruction; you own
  *how* to fix), marking each finding `fixed` / `skipped` /
  `no_change_needed`. Do not launch a second checker: one fresh read is the
  signal.
- **Survivors enrich the one offer.** Findings you skipped or could not fix
  fold into the file-offer below, carrying their promise-pointers, quoted
  spans, and your outcome ledger — *"N issues I couldn't resolve — file
  anyway, or take over."* An `approve` leaves the offer reading exactly as
  it always has. The check gates *completion*, not filing.
- **File nothing.** The checker is read-only over your block; the DM's yes
  below stays the sole trigger that writes to a page. The check's one write
  is the out-of-band findings-log append above.

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
before played sessions exist (see the spotlight skill) and — because the
session spotlight plan is transient — half of what catch-up reconciles after
play, so an aimed or puzzle fight names the PC it shoots at. **Never file an
encounter without one.**

**The block's shape is specified once, and not here.** It lives with the page
format the block travels on:
[*The encounter-meta block*](../build-session/session-page-format.md#the-encounter-meta-block)
in `build-session`'s `session-page-format.md` — the template, its six required
labels (Party, Enemies, Budget, Terrain, Spotlight, Objective, plus the
optional Note) and the shape both the session parser and the deterministic
checker are pinned to. Write the block exactly as specified there;
dungeon-generator files its fights in the same shape. This is a **citation, not
a file to open at run time** — you already know the shape; the pointer is where
a shape change lands (library sync obligations: `docs/campaign-contract.md`).

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
