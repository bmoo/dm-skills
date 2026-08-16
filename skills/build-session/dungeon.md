# Building a Keyed Site

The keyed-site procedure of the `build-session` skill — a complete, runnable
dungeon: a non-linear keyed site with party-balanced combats, one dungeon-wide
mechanic, and setting-true rewards, anchored to a campaign-record node and
justified by an objective the clue web already promises. Step 5 of a session
build loads it whenever the party will explore a location room-by-room; it is
not for a single fight (that's [`combat.md`](combat.md)) and not for deepening
a node's fiction without a keyed site (that's
[`node-deepening.md`](node-deepening.md)).

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

Fights are sized by **following the fight procedure beside this file
([`combat.md`](combat.md))** — hand it each fight and embed the sized
encounter block it produces. Its `xp-budget.md` and `complications.md` are its
references; it owns the budget math and the complication menu. What Step 5
does load is [`spotlight-doctrine.md`](spotlight-doctrine.md) and
[`class-patterns.md`](class-patterns.md) beside this file, for the textures
you rotate across the site (library sync obligations:
`docs/campaign-contract.md`).

## Inputs

A session build has already settled these by the time it loads this file —
Steps 1–2 restate them, so skip to Step 3:

- the anchor node, and the objective its clue web already promises (Step 1);
- the party and each PC's Spotlight profile (Step 2);
- the scale — default a one-session delve (Step 3);
- the **transient session spotlight plan**, so the rotation *spends* that plan
  rather than minting a second one. The plan is transient and never read off
  a page; with no plan in the run, Step 5 self-serves.

A site built outside a full session build — a one-off the DM asks for
mid-prep — pins whatever is still open via Steps 1–2 first.

The product is the runnable dungeon package (Step 7's shape — keyed rooms
plus the concealed render-ready edge section, the dungeon mechanic, the
per-route resource arc, rewards, planted leads) **with its own fights already
sized as `> [!encounter-meta]` blocks**, each built via
[`combat.md`](combat.md). The page build embeds the package as-is and does
not re-size its fights or re-check its edges.

The render-ready edge table ships **already concealed** — the whole
`## Edges (render-ready)` section, heading included, wrapped in an HTML
comment — and is **never DM-visible**. It is machine state: the map renders
from it and the topology checks parse it straight out of the raw markdown.
Edges are a detail published adventures do not print — a human reads a site's
connectivity off the map, and off the room prose where a connection matters.
Conceal it the moment it is drafted: the page build embeds that comment with
the rest of the package and strips nothing.

## Rules sourcing — non-negotiable

The sourcing doctrine is stated once, in [`combat.md`](combat.md)'s *Rules
sourcing — non-negotiable* block, and binds every content type this
procedure places — monster stat blocks, XP values, item text, trap and door
mechanics. Browse the chosen source's catalog *before* Step 5 shortlists.

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

Once, up front, the same way the fight procedure does: heads, classes, and
level from wherever this repo tracks them; state the level and size you're
building for, and flag any composition gaps. Read each PC's **Spotlight
profile** via the
[data ladder in `spotlight.md`](spotlight.md#the-data-ladder) —
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

**Don't proceed past the slate with either pick still open.** Inside a
session build, don't stop the Eight Steps traversal for it — **self-serve**,
the same fallback Step 5 takes with no session plan: draw the slate anyway,
take the reinforcing pairing you flagged, and name both picks in the header
as any run does.

Finalize the room/edge list around the picks, then **verify the floor**
against the edge list (the checklist is in `xandering.md`): at least two
entrances, at least one loop, no critical-path progress gated behind a single
hidden thing, and the objective placed deep with **two or more routes**
reaching it, each costing something different. Structure is done when every
floor item is checked off the edge list.

## Step 5 — Stock

Open [`dungeon-design.md`](dungeon-design.md) for ecology and room
design, and [`spotlight-doctrine.md`](spotlight-doctrine.md) and
[`class-patterns.md`](class-patterns.md) for the
textures you rotate across the site. Per-fight sizing belongs to the fight
procedure ([`combat.md`](combat.md)), which owns the XP budget and the
complication menu.

- **Ecology first.** Who lives where and why it holds together — water, food,
  air, security, faction lines. The site must have an internal logic players
  can reason from.
- **Fights.** You own the **mix**: one High set piece guarding the objective
  or its exit, the rest Low/Moderate, at least one avoidable or negotiable.
  Build each fight via [`combat.md`](combat.md) — the
  pinned room and its enemies as the fight situation, the Step 2 party and
  rosters, the difficulty band you chose for that fight, and the fight's
  allocated spotlight beat from the rotation below. It produces the sized
  encounter block — budget arithmetic shown, the action-economy guardrails
  honored, and the complication(s) from its menu (two, from different
  sections, for the set piece; one for the rest) — and its
  `> [!encounter-meta]` block. Embed what it produces as-is.
- **Textures, rotated.** A dungeon is a session-scale spotlight budget in one
  site: give each fight a texture from the doctrine's palette, keep plain and
  steamroll rooms in the mix, and rotate so every PC's flagged ability gets
  staged somewhere. A requested curveball room counts as one aimed slot. The
  **rotation across fights is yours**; the texture you allocate to a fight
  rides down in that fight's [`combat.md`](combat.md) hand-off, which renders it into
  the block's `Spotlight:` line.
  - **Balance the aimed slots, don't sequence them.** No PC takes a second
    aimed slot while another PC who flagged for one still has zero, and past
    that the per-PC counts stay within one of each other. Count the slots,
    not the running order: the party picks the route, so no room "follows"
    another. Balance is a property of the finished key list and holds down
    every path through the site.
  - **Session plan first.** Inside a session build the session has already
    allocated a spotlight budget — the rotation *spends* that plan rather
    than minting a second one. The plan is **transient**: it lives in the
    prep run, never as a table on the session page. A PC the plan names as
    deliberately resting gets no aimed slot here, and a beat the plan
    already promises elsewhere in the session isn't re-staged in a room.
    Where the site can't honor a planned beat, say so — the plan is the
    session's, and Step 5's reconciliation pass (`SKILL.md`) owns squaring
    it against the finished page.
  - **No plan → self-serve.** A site built with no session plan in the run
    allocates for itself, exactly as above, running the doctrine's variety
    check against the record's recent encounter-meta `Spotlight:` lines.
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

## Definition of done

Before Step 8 offers to file, run both parts of the shared verification
protocol in [`verification.md`](verification.md) over the drafted package.
The self-check settles the mechanical promises the *site* owns — the
structural floor the edge list encodes, the edge grammar, the slate picks,
and the cross-fight properties no single fight block can see; the fresh
check grades the site's two subjective criteria. Nothing is written until
the DM's yes in Step 8.

**The inheritance split.** Every fight arrived from the fight procedure
already checked — its mechanical rows (the six required lines, the XP
arithmetic, the palette texture, the bare-name rule) by its own self-check,
its **stat-block-refs-in-prose** and **swarm-carries-fragile-creatures**
criteria by its own fresh check. Both passes here verify only what the
*site* owns: where a check reads a field off a block (a `Budget:`
difficulty label, a `Spotlight:` target), it reads what the fight build
produced and re-grades none of that block's arithmetic, and the fresh
checker is handed no fight criterion, so it is structurally unable to
re-grade a fight.

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

**The self-check** (Part 1) hands the drafted package to
`run_checks(output, "build-session", [<the ids below, under the
build-session/ qualifier>], context={"roster": <the Step 2 flagged-ability
roster>, "scale_overridden": <True if the DM asked for a non-default scale
in Step 3>})`. **Always hand the roster in** — the two roster-dependent
staging checks refuse to run without it rather than fake a verdict; for the
floor checks to read the objective, the edge list tags the objective room
`{objective}` at its endpoint. Each id is one site-owned promise:

| Check id | Promise |
|---|---|
| `two-entrances` | ≥ 2 entrances, off the edge list |
| `at-least-one-loop` | ≥ 1 interior loop |
| `no-secret-gated-spine` | the objective still reachable with every `secret` edge removed |
| `objective-two-routes` | the objective reachable by ≥ 2 edge-disjoint routes |
| `guarded-approach-holds` | no route reaching the objective slipping past every room the `**Guarded approach:**` line names (silent where the line is absent) |
| `edge-types-in-vocabulary` | every edge type token from the closed vocabulary |
| `type-column-token-strictness` | everything before the first em-dash in the Type column is typed tokens, prose only after |
| `slate-picks-in-header` | both slate picks named in the header |
| `one-signature-technique` | exactly one signature technique from the twelve |
| `one-dungeon-mechanic` | exactly one dungeon-wide mechanic or an explicit vanilla waiver |
| `mechanic-four-part-box` | the mechanic ships as its four-part box (Trigger/Clock · Effect · Tells · Exploit) |
| `default-scale` | the default scale (6–12 keyed areas, 1–2 levels, 2–4 combats) unless the DM overrode it |
| `fight-mix` | the fight mix (one High set piece, the rest Low/Moderate) |
| `every-flagged-pc-staged` | every flagged PC staged somewhere in the site |
| `aimed-slots-balanced` | the aimed slots balanced across the flagging roster |

**The fresh check** (Part 2) grades the two criteria the *site* owns — do
the ≥ 2 routes to the objective each cost something **different** (the
route-cost promise in [`xandering.md`](xandering.md)), and is every planted
lead **interpretable with only what the players already know** (the lead
promise and its boundaries below) — named as their inventory rows
`[build-session/objective-routes-cost-differently,
build-session/lead-interpretability]`, with the party roster as the
checker's third input.

**Lead interpretability's boundaries, pinned:** salient prior knowledge and
**grounded common regional knowledge** a local would plausibly hold both
count as what the players already know; a symbol they glimpsed earlier only
as unremarked scenery does not — seeing is not knowing. A lead whose meaning
is first defined deeper in the same delve is a forward reference and fails;
a lead whose actionable payload rides on content the party already holds
passes even when adjacent content stays opaque.

## Step 8 — Offer filing

Then **offer**, but don't assume — the package stays a chat prep aid until
the DM says to keep it. On the yes, run this checklist:

- [ ] Dungeon key onto the **session page**, pre-play, per the repo's page
  and granularity conventions — the concealed edge section with it. A node
  page is durable canon, and **session-scoped content must not land on one
  while the session is unplayed** (still create the node if Step 1 invented
  it, and let it say where the site is built out). Whether a played site's
  topology is later promoted onto its node page is the consuming repo's
  affair, and **not required**.
- [ ] Each fight files as an encounter-meta block per the fight procedure's
  *Filing format* section ([`combat.md`](combat.md)) — its `Spotlight:` line
  feeds the variety check's fallback ledger, so no fight files without one.
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
  [`session-page-format.md`](session-page-format.md#conventions).
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
