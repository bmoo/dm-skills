# dungeon-generator — judgement rubric

The rows the [fresh-context checker](scripts/judgement_checker/checker-launch-protocol.md)
grades a drafted keyed site against. This file ships **beside `SKILL.md`** (per
[`scripts/judgement_checker/rubric-format.md`](scripts/judgement_checker/rubric-format.md),
"Where the real rubrics live") and is written in the format that directory
defines. It is dungeon-generator's rubric and dungeon's only — a session page is
graded against `build-session`'s rows, a fight against combat-generator's, never
these (spec user story 17).

Every row below **is** a `judgement`-method row of
[`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md)'s
dungeon-generator table — **derived from the inventory, never hand-copied**. The
dungeon table carries exactly these two site-owned judgement-method rows —
**objective-routes-cost-differently** and **lead-interpretability**. (The table's
third judgement row, **verification-slate-verdicts-against-image** — the slate line's
pass/amend/critical verdict *against the rendered image* — is `judgement (vision)`,
and vision is **out of scope** for this verifier: the checker is never handed images,
so `verification-slate-verdicts-against-image` is deliberately **excluded** here, not
authored.)

**objective-routes-cost-differently** is a **structural** judgement (do the routes'
costs differ in kind?), so it carries hand-written anchors only — no golden corpus.
**lead-interpretability** is a **reader-interpretation** judgement (can the party, on
finding a lead, read it with only what they already know?), so it carries
hand-written anchors **and** a labeled golden corpus — one of the four
reader-interpretation rows (`lead-interpretability` / `clue-interpretability` /
`plain-language` / `read-aloud-boundary`) for which the format reserves a corpus
pointer.

A finding against any row here **cites that row's inventory id as its
promise-pointer**, **anchors to where in the output the break is**, and **carries
no concrete fix** — the checker names *which* promise broke; the generator owns
*how* (spec user story 19; shape fixed in
[`scripts/judgement_checker/verdict-contract.md`](scripts/judgement_checker/verdict-contract.md)).

The checker is handed the rubric subset
**`[dungeon-generator/objective-routes-cost-differently,
dungeon-generator/lead-interpretability]`** and nothing else — so it is structurally
unable to re-grade the fights the package carries. Those fights arrived **already
judgement-checked by combat-generator** (its **stat-block-refs-in-prose** /
**swarm-carries-fragile-creatures** rows ran when combat built each one); this rubric
holds no combat row, exactly as the deterministic self-check holds no combat
mechanical row (spec user stories 9/20).

---

## Row `dungeon-generator/objective-routes-cost-differently` — the ≥ 2 routes to the objective each cost something *different*

- **Inventory check id:** `dungeon-generator/objective-routes-cost-differently`
  *(from
  [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md), the
  dungeon-generator table — method: judgement, enforceable-as-written: No. The
  sibling row **objective-two-routes** covers the route **count** mechanically — a
  graph check for ≥ 2 edge-disjoint routes to the `{objective}` room, already run in
  the deterministic self-check (`run_checks(..., ["…",
  "dungeon-generator/objective-two-routes", …])`).
  `objective-routes-cost-differently` grades what no graph can see: whether those
  routes are meaningfully **distinct in cost**. The count is settled; this is the
  remedy, structured like combat's `swarm-carries-fragile-creatures` trigger/remedy
  split.)*

- **Promise text:** The objective sits deep, **reachable by ≥ 2 routes, each costing
  something different** — fights, hazards, the dungeon mechanic, a favor. Two routes
  that levy the *same* toll are one choice wearing two coats, not a meaningful
  branch. *(Source: `xandering.md` — "each costing something different — fights,
  hazards, the dungeon mechanic, a favor" — the floor's fourth rule. The inventory
  row `objective-routes-cost-differently` cites that same clause;
  `objective-two-routes`'s count derives from the sentence it closes
  (`xandering.md` — "The objective sits deep, reachable by ≥ 2 routes").)*

- **Roster use:** **None.** `objective-routes-cost-differently` is structural — it
  asks whether the routes' costs differ *in kind*, which is legible from the keyed
  site alone (the edge list, the fights and hazards each route crosses, the mechanic
  and favors it demands). The party roster carries flagged-ability / Spotlight
  profiles, which say nothing about route cost, so this row does not read it. *(The
  roster is handed in per the launch protocol regardless; this row simply does not
  consult it.)*

- **Criteria:**
  - **Activation.** `objective-routes-cost-differently` grades only once
    **`objective-two-routes` holds** — there *are* ≥ 2 edge-disjoint routes to the
    `{objective}` room. If the count is short, that is `objective-two-routes`'s
    mechanical finding, not `objective-routes-cost-differently`'s;
    `objective-routes-cost-differently` presumes the routes exist and grades their
    costs.
  - **Identify each route's cost.** For each of the ≥ 2 routes, read what the party
    must spend to traverse it: the fights it forces, the hazards it crosses, whether
    it demands the dungeon mechanic, whether it turns on a favor / social price / a
    key or secret. A route's *cost* is the kind of toll it levies, not its length.
  - **Holds when** the routes' costs differ **in kind** — one route is a fight
    gauntlet, another a hazard crossing; one spends the dungeon mechanic, another
    buys passage with a favor. The party faces a genuine *choice of price*, not the
    same toll by two doors.
  - **Breaks when** the routes levy the **same kind** of cost with no distinguishing
    price — both are "cross two Moderate fights", or both are "pass the same hazard",
    so the second route is a reskin of the first and the branch is cosmetic. Report
    it against the route pair (name both routes / their edge spans), not one edge.
  - **Cannot tell → disapprove.** If a route's cost is not legible from the package —
    a route whose edges are typed but whose fights/hazards/mechanic demands the
    package never makes plain, so the checker cannot compare its price to the other's
    — the checker **disapproves** and names the routes, so the generator can make
    each route's cost explicit (or differentiate them). Uncertainty is a disapprove,
    never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Two routes to the flooded vault `{objective}`. **Route A** —
    the drowned stair: two fights (a `{monster:sahuagin}` picket, then the eel
    warren) and no way around them. **Route B** — the cistern sluice: no fight, but
    it demands the dungeon mechanic (open the flood-gates, which drops the water and
    triggers the rising-silt clock everywhere else) *and* a favor from the captured
    smuggler who knows the valve order. A fight gauntlet versus a mechanic-and-favor
    price — the costs differ **in kind**. **Holds.**
  - **Bad — breaks.** Two routes to the same vault. **Route A** — the east gallery: a
    Moderate `{monster:cultist}` fight, then a Moderate `{monster:cult-fanatic}`
    fight. **Route B** — the west gallery: a Moderate `{monster:cultist}` fight, then
    a Moderate `{monster:cult-fanatic}` fight. Both routes are "two Moderate fights
    of the same creatures" — the same toll behind two doors. The branch is cosmetic.
    **Breaks `objective-routes-cost-differently`** at the route pair — the party has
    no real choice of price.
  - **Edge — the boundary.** Two routes to the vault. **Route A** — one Hard fight
    (the guard captain). **Route B** — one Hard fight (a hazard-warded golem) *plus*
    a hazard crossing (the collapsing floor). Both routes' spine is "one Hard fight",
    so they rhyme; but Route B adds a hazard Route A lacks. The judgement the checker
    must adjudicate is *"is the added hazard enough to make the costs differ in kind,
    or is this two Hard fights with a garnish?"* If the package makes plain the
    hazard is a real, avoidable-only-by-A price the party weighs (Route B trades a
    hazard for something Route A charges elsewhere), the costs differ and it
    **holds**; if the hazard is incidental flavor on what is otherwise the same "one
    Hard fight" toll — or the package leaves the hazard's bite unstated — the checker
    **cannot tell** and **disapproves**, naming both routes so the generator makes
    the price distinction plain (or sharpens it). This is the borderline the criteria
    exist to settle.

- **Corpus pointer:** *none* — `objective-routes-cost-differently` is structural (do
  these routes' costs differ in kind?), so hand-written anchors are the floor and the
  ceiling. (The reserved corpus slot is for the reader-interpretation rows
  `lead-interpretability` / `clue-interpretability` / `plain-language` /
  `read-aloud-boundary` only.)

---

## Row `dungeon-generator/lead-interpretability` — every planted lead is interpretable with only what the players already know

- **Inventory check id:** `dungeon-generator/lead-interpretability`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the dungeon-generator table — method: judgement, enforceable-as-written: No. This
  is one of the library's four **reader-interpretation** rows — *can a party, on
  finding this, read it?* — so it carries a golden corpus on top of its anchors,
  alongside `clue-interpretability`, `plain-language` and `read-aloud-boundary`.)*

- **Promise text:** Every clue inside the dungeon that points at another node — a
  **planted lead** — must be **interpretable using only what the players will already
  know on finding it**. A lead that requires unseen content to mean anything is a
  **defect, not foreshadowing**. *(Source: the Step 7 "**Leads planted**" delivery
  bullet — "**Each must be interpretable using only what the players will already
  know on finding it — a lead that requires unseen content to mean anything is a
  defect, not foreshadowing.**" The inventory row `lead-interpretability` cites
  the same Leads-planted promise (`SKILL.md` — "is every planted lead
  **interpretable with only what the players already know**"); it is the delivery-package
  bullet, not the Step-8 filing checklist's clue-web bookkeeping.)*

- **Roster use:** **None** — but not for the structural reason `npc-rows-named`
  gives. `lead-interpretability` turns on **what the party already knows** — their
  accumulated campaign knowledge, the nodes they have visited, the names and symbols
  they have already met. That knowledge state is **not in the roster**, which carries
  each PC's flagged-ability / Spotlight profile and nothing about what the party has
  learned. So the checker does not read the roster for `lead-interpretability`; it
  judges interpretability against the "what the players already know" context the row
  is graded with (the corpus supplies that context per instance; a live run reads it
  from the campaign state the package sits in). *(The roster is handed in per
  protocol regardless; `lead-interpretability` does not consult it — a flagged
  ability neither makes nor breaks whether a lead is readable.)*

- **Criteria:**
  - **The reader is the party at the moment of finding.** Judge each lead as the
    party reads it **when and where they find it**, with only what they already know
    then — earlier nodes visited, NPCs met, symbols and names already seen, common
    knowledge the campaign has established. Not what the DM knows, not what a later
    node will reveal.
  - **Holds when** the lead resolves to a **direction, a place, or a next question**
    using only that prior knowledge — it names or points at something the party can
    already place ("the ledger is stamped with the Harbormaster's seal" when the
    party has met the Harbormaster), so it *foreshadows*: it means something now and
    more later.
  - **Breaks when** the lead can only be read **once the party sees content they have
    not yet reached** — it turns on a name, symbol, cipher, or fact first defined in
    a node the party has not visited, so at the moment of finding it is **noise**: a
    stamped sigil they have never seen, a coded phrase whose key is in an unvisited
    room, a reference to an NPC not yet introduced. That is the defect the promise
    names — "requires unseen content to mean anything". Report it at the lead's
    location (the key / clue-note where it is planted).
  - **Cannot tell → disapprove.** If it is ambiguous whether the party would already
    hold the knowledge a lead needs — the package does not establish whether the
    referenced name/symbol was seen earlier, or the lead is legible only on a
    generous reading — the checker **disapproves** and names the lead, so the
    generator can either ground the reference in something already known or make the
    prior knowledge explicit. Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Party already met **Old Harl** the caravan master (an earlier
    node). Lead planted in the smugglers' cache: *a manifest in Old Harl's hand,
    routing "the cargo" to the Salt Docks.* The party knows Harl and knows the Salt
    Docks are a place — the lead reads **now** as "Harl is moving something to the
    docks", a direction they can act on. Interpretable with only what they know.
    **Holds.**
  - **Bad — breaks.** Lead planted in the shrine: *a tile floor-cipher that spells a
    location once you hold the **Verdant Choir's cant-key** — a decoding table found
    only in the grove node the party has not visited.* At the moment of finding, the
    cipher is unreadable noise; it means nothing until unseen content (the cant-key)
    is in hand. **Breaks `lead-interpretability`** at the shrine key — it requires
    unseen content to mean anything, the exact defect the promise names.
  - **Edge — the boundary.** Lead planted in the counting-house: *a coin stamped with
    a **three-rings-and-a-star** mint-mark, the same mark the party glimpsed once,
    stamped on a crate, back at the warehouse node they did pass through.* Whether
    this holds turns on **how firmly that earlier glimpse landed** — if the warehouse
    beat made the mark salient (the party remarked on it, it was called out), the
    party can place the coin now and it **holds**; if the mark was incidental
    set-dressing the party had no reason to register, the coin is effectively a
    first-showing symbol and the lead **breaks**. The checker judges whether the
    prior exposure was real knowledge or scenery; where the package does not
    establish that the earlier mark was ever made legible, the checker **cannot
    tell** and **disapproves**, naming the lead so the generator grounds the callback
    (or drops it). This is the borderline the corpus pins by example.

- **Corpus pointer:** **`corpus/lead-interpretability/`** — the labeled golden corpus
  for this row (pass / fail / edge instances + a [verdict
  map](corpus/lead-interpretability/verdict-map.md)). Each instance is a
  self-contained planted-lead example (the lead text **plus** the minimal "what the
  players already know" context the row is judged against) labeled with its expected
  verdict, so `lead-interpretability`'s boundary is pinned **by example**, not by
  adjectives alone. The corpus is added **on top of** the hand-written anchors above,
  per the rubric format's reader-interpretation slot. *(The harness that runs the
  checker over the corpus and asserts each verdict matches its label is **out of
  scope here** — it is edit-time work for the evaluation harness. This rubric
  authors the corpus data and verdict map only.)*
