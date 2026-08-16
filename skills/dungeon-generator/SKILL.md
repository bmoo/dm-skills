---
name: dungeon-generator
description: >-
  Generate a complete, runnable dungeon — a non-linear keyed site with
  party-balanced combats, one dungeon-wide mechanic, and setting-true rewards —
  anchored to a campaign-record node and justified by an objective the clue web
  already promises. Use whenever the DM wants a dungeon, delve, lair, or
  interior adventure site designed room-by-room for a node, a location, or an
  idea. Not for a single fight (that's combat-generator) and not for deepening
  a node's fiction without a keyed site.
---

# Dungeon Generator

"Dungeon" in the DMG's loose sense: any adventure location with interior
spaces to explore — a storm-drain junction, a closed hotel floor, or a
decommissioned base as readily as a tomb. The skill designs a **situation**,
not a plot (the *Don't Prep Plots* frame): a keyed, non-linear site the party
can attack in an order you didn't predict, justified by an objective they
already want.

The deliverable is a **chat package** — ephemeral until the DM says to keep
it. Filing to the campaign record is Step 8's offer, never automatic.

Four reference files sit beside this one; load each when its step says to:

- [`xandering.md`](xandering.md) — non-linearity: the structural floor, the
  twelve techniques, the signature-technique rule.
- [`dungeon-mechanics.md`](dungeon-mechanics.md) — the menu of dungeon-wide
  mechanics and the rules-expression template.
- [`dungeon-design.md`](dungeon-design.md) — site-design principles:
  purpose and history, layout, room design, ecology, the
  hide-extras-never-essentials rule.
- [`map-render.md`](map-render.md) — the tactical-map render step (Step 9):
  edge list → gpt-image-2 render → verification slate → filed `[!map]`.

Fights are sized by **invoking the combat-generator skill through its delegate
interface** — hand it each fight and embed the sized encounter block it hands
back. Its `xp-budget.md` and `complications.md` are its internals; it owns the
budget math and the complication menu behind that interface. What Step 5 does
load is the **spotlight** skill's [`doctrine.md`](../spotlight/doctrine.md) and
[`class-patterns.md`](../spotlight/class-patterns.md), for the textures you
rotate across the site. Those skills own their files (library sync obligations:
`docs/campaign-contract.md`).

## Invoked as a delegate — the interface

**Standalone**, the DM asks for a dungeon and Steps 1–2 pin the anchor,
objective, and party from the record. **As a delegate**, `build-session` hands
you a keyed site to build for a session it is prepping; its inputs come from
the caller and every step from Step 3 on runs the same.

**build-session hands you:**

- the anchor node, and the objective its clue web already promises (Step 1,
  settled by the caller);
- the party and each PC's Spotlight profile (Step 2);
- the scale — default a one-session delve (Step 3);
- the **transient session spotlight plan**, so the rotation *spends* that plan
  rather than minting a second one. The plan is transient and never read off a
  page — ask for it if it wasn't handed over.

**You hand back** the runnable dungeon package (Step 7's shape — keyed rooms
plus the concealed render-ready edge section, the dungeon mechanic, the
per-route resource arc, rewards, planted leads) **with its own fights already
sized as `> [!encounter-meta]` blocks**, each built by invoking
combat-generator per its interface. The caller embeds the package as-is and
does not re-size its fights or re-check its edges.

The render-ready edge table is handed back **already concealed** — the whole
`## Edges (render-ready)` section, heading included, wrapped in an HTML
comment — and is **never DM-visible**. It is machine state: the map renders
from it and the topology checks parse it straight out of the raw markdown.
Edges are a detail published adventures do not print — a human reads a site's
connectivity off the map, and off the room prose where a connection matters.
Concealing is this skill's job, done before the hand-off: the caller embeds
that comment with the rest of the package and strips nothing.

## Rules sourcing — non-negotiable

- **MUST** source all rules content — monster stat blocks, XP values, item
  text, trap and door mechanics, any rules detail — from the sourcing chain in
  [`rules-sourcing.md`](rules-sourcing.md), never from training-data memory
  (the 2024 rules differ from 2014). Look up every creature and item you place.
- The chain prefers whatever D&D content tools this environment has installed,
  then falls back to the bundled SRD dataset — take the first rung that answers.
- **MUST** browse the chosen source's catalog (its listings, filtered by
  type/CR/etc.) *before* shortlisting in Step 5 — never shortlist from memory,
  which silently defaults to famous core-book entries and ignores what the
  table's sources actually offer.
- If nothing in the chain answers, **say so and name the gap** — hand the DM
  what could not be sourced instead of filling it from memory.

## Step 1 — Pin the anchor and the objective

A dungeon is never self-justifying: something the party wants is inside, and
the clue web is how they know it. Settle both halves before any design:

- **Anchor.** If the DM named a node or seed, **read the whole page** and its
  clue web — its factions, tone, and history are the dungeon's fiction. If the
  request is freeform ("a smugglers' warren under the pier"), invent the
  anchor from what the setting establishes and flag that filing it later means
  creating a node.
- **Objective.** What the party comes to get or do — retrieve, learn, rescue,
  destroy, bargain. If the anchor's inbound leads already promise something
  ("the ledger is in the vault"), the objective **must honor that promise**;
  the dungeon pays off what the clue web advertised.

**No objective, no dungeon.** If nothing on the books supplies one, ask the DM
or propose candidates — the objective is settled before any design.

## Step 2 — Pin the party

Once, up front, the same way combat-generator does: count heads and note
classes wherever this repo tracks player characters; take the level the DM
gives or derive it from the repo's leveling rules and campaign progress.
State the level and size you're building for, and flag any composition gaps.
Read each PC's **Spotlight profile** via the
[spotlight skill's data ladder](../spotlight/SKILL.md#the-data-ladder) —
Step 5 textures fights with it.

## Step 3 — Pin the scale

Default: a **one-session delve** — roughly 6–12 keyed areas on one or two
levels with 2–4 combats — and say so. Scale up only when the DM asks
(a multi-session complex shifts toward multi-level techniques and required
rest niches). State the scale before drawing anything.

## Step 4 — Structure

Open [`xandering.md`](xandering.md). Draft the route topology — entrances,
branches, loops, secret paths — as a **room list with an explicit edge list**:
every connection typed with a **base** — open / door / locked / grate /
vertical (sub-type: stairs, shaft-chute, ladder, or slope) — plus any
**modifiers** that apply: secret · one-way · trap · hazard · up/down
(vertical edges only, read against the written endpoint order). `grate` is
anything the players can sense through but not travel through — bars, a
portcullis, a window. Attributes always ride as typed modifiers, never in
prose alone: a prose-only "secret" has been silently dropped before. The
edge list is the map — keep it complete enough to render from; rendering it
(ASCII, image) is a separate later job.

Then the **slate stop**, one interaction: present 2–3 candidate **signature
techniques** and 2–3 candidate **dungeon-wide mechanics** (from
[`dungeon-mechanics.md`](dungeon-mechanics.md)), each grounded in one line of
this anchor's specific fiction, with reinforcing pairings flagged. The DM
picks one of each — or says vanilla, which waives the mechanic (never the
floor).

**Don't proceed past the slate with either pick still open.** With no DM in the
run to make them — a delegate run, an unattended one — **self-serve**, the same
fallback Step 5 takes with no session plan: draw the slate anyway, take the
reinforcing pairing you flagged, and name both picks in the header as any run
does.

Finalize the room/edge list around the picks, then **verify the floor**
against the edge list (the checklist is in `xandering.md`): at least two
entrances, at least one loop, no critical-path progress gated behind a single
hidden thing, and the objective placed deep with **two or more routes**
reaching it, each costing something different. Structure is done when every
floor item is checked off the edge list.

## Step 5 — Stock

Open [`dungeon-design.md`](dungeon-design.md) for ecology and room
design, and the spotlight skill's [`doctrine.md`](../spotlight/doctrine.md) and
[`class-patterns.md`](../spotlight/class-patterns.md) for the textures you
rotate across the site. Per-fight sizing belongs to **combat-generator**
through its delegate interface (its *Invoked as a delegate* section), which
owns the XP budget and the complication menu behind that boundary.

- **Ecology first.** Who lives where and why it holds together — water, food,
  air, security, faction lines. The site must have an internal logic players
  can reason from.
- **Fights.** You own the **mix**: one High set piece guarding the objective
  or its exit, the rest Low/Moderate, at least one avoidable or negotiable.
  Hand each fight to combat-generator through its delegate interface — the
  pinned room and its enemies as the fight situation, the Step 2 party and
  rosters, the difficulty band you chose for that fight, and the fight's
  allocated spotlight beat from the rotation below. It hands back the sized
  encounter block — budget arithmetic shown, the action-economy guardrails
  honored, and the complication(s) from its menu (two, from different
  sections, for the set piece; one for the rest) — and its
  `> [!encounter-meta]` block. Embed what it returns as-is.
- **Textures, rotated.** A dungeon is a session-scale spotlight budget in one
  site: give each fight a texture from the doctrine's palette, keep plain and
  steamroll rooms in the mix, and rotate so every PC's flagged ability gets
  staged somewhere. A requested curveball room counts as one aimed slot. The
  **rotation across fights is yours**; the texture you allocate to a fight
  rides down in that fight's combat-generator hand-off, which renders it into
  the block's `Spotlight:` line.
  - **Balance the aimed slots, don't sequence them.** No PC takes a second
    aimed slot while another PC who flagged for one still has zero, and past
    that the per-PC counts stay within one of each other. Count the slots,
    not the running order: the party picks the route, so no room "follows"
    another. Balance is a property of the finished key list and holds down
    every path through the site.
  - **Session plan first.** Inside a session prep run the session has already
    allocated a spotlight budget — the rotation *spends* that plan rather
    than minting a second one. The plan is **transient**: it lives in the
    prep run that invoked you, never as a table on the session page, so ask
    for it if it wasn't handed over. A PC the plan names as deliberately
    resting gets no aimed slot here, and a beat the plan already promises
    elsewhere in the session isn't re-staged in a room. Where the site can't
    honor a planned beat, say so — the plan is the session's, and
    build-session owns reconciling it.
  - **No plan → self-serve.** A standalone dungeon allocates for itself,
    exactly as above, running the doctrine's variety check against the
    record's recent encounter-meta `Spotlight:` lines.
- **Resource arc, by route.** No fixed fight order exists, so chart attrition
  per plausible route: what the party has left when they reach the objective
  along each path, and which route trades fights for hazards or the mechanic.
- **Rest niches — conditional.** Only where the arc shows real depletion or
  the scale is multi-session: a defensible, lockable, or hidden room keyed as
  a viable rest spot, with a note on what the inhabitants do if the party
  holes up. A small delve may rightly have none.
- **Roster response.** The inhabitants are an active roster, not furniture:
  who investigates noise, what an alarm changes, how the dungeon looks on a
  return visit.

## Step 6 — Reward

Read whatever reward-economy rules this repo keeps and its approved-item
list, wherever its docs say those live. If the repo declares no reward
economy, ask the DM what the campaign uses before defaulting to standard
treasure.

- Rewards default to **favors owed, information, access, and meaningful
  mundane objects** — all cheap to place and all natural clue carriers.
- A magic item may be placed silently **only if it's on the repo's approved
  list**. If the list can't cover the dungeon, offer candidate items for the
  DM to approve or replace — shaped by the list page's proposal standard and
  fitted to the actual roster from Step 2, with loot parity: read recent
  item receipts from the campaign record and favor PCs light on recent
  loot. An approved item joins the list; an unvetted item never files as
  canon.
- **Secrets gate bonuses, never the spine**: hidden treasure rewards
  searching, but nothing essential hides where the party might never look.
- Information-treasure that points at another node is a **lead** — note it
  now for Step 8's clue-web wiring.

## Step 7 — Deliver

Present the dungeon in chat as a runnable package:

- **Header** — anchor, objective (one sentence — it justifies everything
  below), party level and size, scale, signature technique, dungeon mechanic.
  Add a `**Guarded approach:**` line — `·`-separated room IDs — **only** where
  the site claims no approach to the objective is free: it asserts that every
  route from any entrance to the objective passes one of those rooms. Omit it
  and the site claims nothing; an unguarded back way is legal design until the
  page says otherwise.
- **The mechanic's rules box** — trigger, effect in game terms, tells,
  exploit.
- **Keyed rooms** — each area: description, contents, and the connections
  that matter said in the room's own prose, with the connection's type and
  any DCs where the DM reads them. Never an exits list: the typed edge data
  lives once, in the concealed `## Edges (render-ready)` section, for the map
  render and the topology checks.
- **Fights** — each with budget math, complication, and tactics tied to the
  enemies' objective.
- **Resource arc** — attrition per plausible route to the objective; rest
  niches if any.
- **Rewards** — placed favors/information/items, approval flags on anything
  unvetted.
- **Leads planted** — every clue inside the dungeon that points at another
  node. Each must be interpretable using only what the players will already
  know on finding it — a lead that requires unseen content to mean anything
  is a defect, not foreshadowing.

## Definition of done — the mechanical self-check

Before Step 8 offers to file, **check the drafted package against the
mechanical promises the *site* owns** — the ones a compiler can settle: the
structural floor the edge list encodes, the edge grammar, the one signature
technique and the one dungeon mechanic, and the cross-fight properties that
hold across the whole key list. Checking is not filing: the check runs over
the package you hold in context, and nothing is written until the DM's yes in
Step 8.

**The inheritance split.** Every fight arrived from combat-generator already
self-checked against its own mechanical promises (the six required lines, the
XP arithmetic, the palette texture, the bare-name rule). This self-check
verifies only what the *site* owns — the facets no single fight block can
see — and where it reads a field off a block (a `Budget:` difficulty label, a
`Spotlight:` target), it reads what combat handed back and re-grades none of
that block's arithmetic.

**The shapes the checks read.** The drafted package carries the site-owned
facets in fixed shapes: a single **`## Edges (render-ready)`** table
(`Edge | Endpoints | Type` rows — the same section `map-render.md` consumes),
with `—` joining interior rooms, `→` marking each entrance, the objective
room's endpoint tagged `{objective}`, and the Type column token-strict per
Step 4; header fields **`**Signature technique:**`** and
**`**Dungeon mechanic:**`** naming the one of each (or `vanilla`), the
mechanic shipped as its four-part box, plus Step 7's optional
**`**Guarded approach:**`** line — absent, the interposition check has no
claim to grade and stays silent. The fights are already `> [!encounter-meta]`
blocks (the combat hand-back). If a facet isn't in these shapes the check
can't see it — consolidate the edge list and label the header before running.
The edge section carries its HTML-comment wrapper from the moment it is
drafted: every check reads raw markdown, so concealment is invisible to them
and there is no unconcealed window between the self-check and the hand-off.

- **Run the checks.** Hand the drafted package to
  `run_checks(output, "dungeon-generator", ["dungeon-generator/two-entrances",
  "dungeon-generator/at-least-one-loop",
  "dungeon-generator/no-secret-gated-spine",
  "dungeon-generator/objective-two-routes",
  "dungeon-generator/guarded-approach-holds",
  "dungeon-generator/edge-types-in-vocabulary",
  "dungeon-generator/type-column-token-strictness",
  "dungeon-generator/slate-picks-in-header",
  "dungeon-generator/one-signature-technique",
  "dungeon-generator/one-dungeon-mechanic",
  "dungeon-generator/mechanic-four-part-box", "dungeon-generator/default-scale",
  "dungeon-generator/fight-mix", "dungeon-generator/every-flagged-pc-staged",
  "dungeon-generator/aimed-slots-balanced"], context={"roster": <the Step 2
  flagged-ability roster>, "scale_overridden": <True if the DM asked for a
  non-default scale in Step 3>})` — the runnable checks live beside this skill
  at [`scripts/mechanical_checker`](scripts/mechanical_checker). Each is one
  site-owned promise, under the `dungeon-generator/` qualifier: **the graph
  floor** off the edge list — **two-entrances** ≥ 2 entrances,
  **at-least-one-loop** ≥ 1 interior loop, **no-secret-gated-spine** the
  objective still reachable with every `secret` edge removed,
  **objective-two-routes** the objective reachable by ≥ 2 edge-disjoint
  routes, **guarded-approach-holds** no route reaching the objective slipping
  past every room the `**Guarded approach:**` line names (silent where the
  line is absent); **the edge grammar** — **edge-types-in-vocabulary** every
  edge type token from the closed vocabulary,
  **type-column-token-strictness** everything before the first em-dash in the
  Type column is typed tokens, prose only after; **the site's commitments** —
  **slate-picks-in-header** both slate picks named in the header,
  **one-signature-technique** exactly one signature technique from the twelve,
  **one-dungeon-mechanic** exactly one dungeon-wide mechanic or an explicit
  vanilla waiver, **mechanic-four-part-box** the mechanic ships as its
  four-part box (Trigger/Clock · Effect · Tells · Exploit); and **the
  cross-fight facets** — **default-scale** the default scale (6–12 keyed
  areas, 1–2 levels, 2–4 combats) unless the DM overrode it, **fight-mix** the
  fight mix (one High set piece, the rest Low/Moderate),
  **every-flagged-pc-staged** every flagged PC staged somewhere in the site,
  **aimed-slots-balanced** the aimed slots balanced across the flagging
  roster. **Always hand the roster in** — the two roster-dependent staging
  checks refuse to run without it rather than fake a verdict. For the floor
  checks to read the objective, the edge list tags the objective room
  `{objective}` at its endpoint.
- **Self-heal, silently.** Drive each finding through the shared
  [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md) —
  reroute the topology to add the missing loop or second route, retype an
  off-vocabulary edge, restage a flagged PC who drew no beat, rebalance the
  aimed slots — up to **three attempts per check**, re-running that check
  after each. A finding that heals is telemetry.
- **Escalate what won't heal.** A check still failing after three attempts is
  **unhealable** — surface it in Step 8's offer as a terminal mechanical
  escalation: which check, expected vs. actual, where in the package, how
  many attempts. A compiler is certain — no confidence hedge.
- **File nothing.** The self-check runs over the package you hold in context;
  the DM's yes in Step 8 stays the sole trigger that writes to a page. The
  loop's one write is out-of-band: it appends a **run record** for the pass,
  then each finding — healed and unhealable alike — to the validator findings
  log, per [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md).

This is the deterministic slice of done. The subjective promises are the
fresh check below — run it after this self-check, before Step 8.

## Definition of done — the fresh check

The subjective promises the *site* owns — do the ≥ 2 routes to the objective
each cost something **different**, is every planted lead **interpretable with
only what the players already know** — need a grader that isn't you: you mark
your own homework, and you mark it kindly. Once the package is drafted and
self-healed, hand it to **one fresh-context checker**, one round. This gates
*completion*: Step 8's offer forms only when the check has run and its
findings are answered.

**Lead interpretability's boundaries, pinned:** salient prior knowledge and
**grounded common regional knowledge** a local would plausibly hold both
count as what the players already know; a symbol they glimpsed earlier only
as unremarked scenery does not — seeing is not knowing. A lead whose meaning
is first defined deeper in the same delve is a forward reference and fails;
a lead whose actionable payload rides on content the party already holds
passes even when adjacent content stays opaque.

**The inheritance split.** Every fight arrived from combat-generator already
checked (its **stat-block-refs-in-prose** and
**swarm-carries-fragile-creatures** criteria, graded by combat's fresh check
when it built the block). This check grades only the two criteria the *site*
owns — **objective-routes-cost-differently** and **lead-interpretability** —
so it is structurally unable to re-grade a fight.

- **Launch it fresh — output, criteria, roster, nothing else.** Start a
  genuinely fresh-context, **read-only** checker and hand it **only three
  things**: (1) the drafted dungeon package exactly as it stands, (2) the
  two criteria as this skill's own text states them — the route-cost
  promise in [`xandering.md`](xandering.md), the lead promise and its
  boundaries above — named as dungeon-generator's rows
  `[dungeon-generator/objective-routes-cost-differently,
  dungeon-generator/lead-interpretability]`, and (3) the party roster.
  Withhold your own reasoning — chain of thought, heal telemetry, any note
  arguing the site is good: a checker that sees only what a reader sees
  grades what a reader gets. It returns a plain `approve | disapprove`;
  every finding cites its inventory row, where in the package it sits (the
  route pair, the key/clue-note), the **quoted span** it fired on, and a
  one-line **reason** — and carries **no fix**. Its default when it cannot
  tell is **disapprove**. Log the pass through the shared library
  ([`scripts/mechanical_checker`](scripts/mechanical_checker), module
  `findings_log`): one `log_run` with `tier="judgement"` and the verdict,
  one `log_finding` per finding with its quoted span and reason.
- **On `disapprove`, one fix pass — no re-grade.** Refine the package
  against the findings once (the promise-pointers *are* the instruction;
  you own *how* — differentiate two same-cost routes, ground a lead that
  needs unseen content), marking each finding `fixed` / `skipped` /
  `no_change_needed`. Do not launch a second checker: one fresh read is the
  signal.
- **Survivors enrich Step 8's one offer.** Findings you skipped or could
  not fix fold into the existing file-offer, carrying their
  promise-pointers, quoted spans, and your outcome ledger — *"N issues I
  couldn't resolve — file anyway, or take over."* — in the same enriched
  list as any unhealed mechanical escalation from the self-check above. An
  `approve` leaves the offer reading exactly as it always has.
  Judgement gates *completion*, not filing.
- **File nothing.** The checker is read-only over your package; the DM's yes
  in Step 8 stays the sole trigger that writes to a page. The checker's one
  write is the out-of-band findings-log append its launch protocol instructs.

## Step 8 — Offer filing

Then **offer**, but don't assume — the package stays a chat prep aid until
the DM says to keep it. On the yes, run this checklist:

- [ ] Dungeon key onto the **session page**, pre-play, per the repo's page
  and granularity conventions — the concealed edge section with it. A node
  page is durable canon, and **session-scoped content must not land on one
  while the session is unplayed**, so the key does not go there now (still
  create the node if Step 1 invented it, and let it say where the site is
  built out). Whether a played site's topology is later promoted onto its
  node page is the consuming repo's affair — its absorption or catch-up
  flow — and is **not required**; a repo with no such flow gets the
  prohibition and stops there.
- [ ] Each fight files as an encounter-meta block per combat-generator's
  filing format — its `Spotlight:` line feeds the variety check's fallback
  ledger, so no fight files without one.
- [ ] A **non-combat** beat this site stages for a PC — an exploration or
  social spotlight in a keyed area — files its own `Spotlight (scene):`
  line at that key, as a one-line behind-the-screen note in a
  `> [!dm-sidebar]`:

  > **Spotlight (scene):** <PC name> — <pillar: social / exploration>;
  > <the staging that fires their flagged ability, and the tell that
  > points at it>

  The label is deliberately distinct from a fight's encounter-meta
  `Spotlight:` field — a scene line must never read as a fight in the
  variety ledger — and every line names its target PC. The shape is
  specified once, and not here: *Spotlight lines* in `build-session`'s
  [`session-page-format.md`](../build-session/session-page-format.md#conventions).
  This is a **citation, not a file to open at run time** — you already know
  the shape; the pointer is where a shape change lands (library sync
  obligations: `docs/campaign-contract.md`). The session's plan is
  transient; these annotations plus the encounter-meta lines are the whole
  record of what was aimed where, and catch-up reconciles from them.
- [ ] Every planted lead gets **both-ends** bookkeeping, and revelation
  evidence routes to the revelations checklist — both per the repo's
  clue-web conventions.
- [ ] Item approvals: anything the DM okays joins the repo's approved-items
  list (wherever its docs keep it); anything declined is cut or swapped
  before filing.
- [ ] **Inbound reachability**: the anchor needs at least one inbound lead
  promising the objective — none means the dungeon is unreachable; flag the
  gap to `seed-clues` rather than inventing a lead here.
- [ ] Catalog and log updated per the repo's conventions.

## Step 9 — Offer the tactical map

After filing, **offer a rendered tactical map** of the keyed site. On the
yes, open [`map-render.md`](map-render.md) and follow it — it owns the whole
step: grid anchor, prompt assembly from the legend fragments, generation,
the verification slate (with its re-roll and escalation policy), and filing
via the `[!map]` callout.

The step also runs **standalone** against a session page that already has an
`## Edges (render-ready)` section — the way sites filed before this step
existed get their maps.
