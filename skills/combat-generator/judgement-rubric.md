# combat-generator — judgement rubric

The rows the [fresh-context checker](scripts/judgement_checker/checker-launch-protocol.md)
grades a drafted combat encounter against. This file ships **beside
`SKILL.md`** (per [`scripts/judgement_checker/rubric-format.md`](scripts/judgement_checker/rubric-format.md),
"Where the real rubrics live") and is written in the format that directory
defines. It is combat-generator's rubric and combat's only — a session page is
graded against `build-session`'s rows, never these (spec user story 17).

Every row below **is** a `judgement`-method row of
[`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md)'s
combat-generator table — **derived from the inventory, never hand-copied**. The
combat table carries exactly **two** judgement-method rows
(**stat-block-refs-in-prose**, **swarm-carries-fragile-creatures**), and combat's
judgement surface is genuinely thin — that is correct, not an omission. Both are
**structural** judgements, so each carries hand-written anchors only; no golden
corpus (corpora are reserved for the reader-interpretation rows
`lead-interpretability` / `clue-interpretability` / `plain-language` /
`read-aloud-boundary`).

A finding against any row here **cites that row's inventory id as its
promise-pointer**, **anchors to where in the output the break is**, and **carries
no concrete fix** — the checker names *which* promise broke; the generator owns
*how* (spec user story 19; shape fixed in
[`scripts/judgement_checker/verdict-contract.md`](scripts/judgement_checker/verdict-contract.md)).

---

## Row `combat-generator/stat-block-refs-in-prose` — creature names in the terrain/tactics **prose** carry the reference convention

- **Inventory check id:** `combat-generator/stat-block-refs-in-prose`
  *(from
  [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md), the
  combat-generator table — method: judgement, "No — see
  `unenforceable/stat-block-sweep-page-wide`". The sibling row
  **stat-block-refs-on-enemies-line** covers the `Enemies:` line **mechanically** —
  a regex, already run in the deterministic self-check; `stat-block-refs-in-prose`
  is the **prose** the block sits in, where no regex can tell which strings are
  creature names.)*

- **Promise text:** **Every creature name — on the `Enemies:` line and in the
  surrounding terrain/tactics prose — is written in the repo's stat-block reference
  convention** (`{monster:Name}` where the render tokens are in use; otherwise a
  stat-block link to the campaign record), so downstream renderers link it to its
  stat block. A bare creature name is a filing defect, never a valid entry.
  *(Source: `SKILL.md` — "in the surrounding terrain/tactics prose" — the
  filing-format convention: "**Every creature name … in the surrounding
  terrain/tactics prose — is written in the repo's stat-block reference
  convention**". The inventory row cites the same passage, the Tactics/prose
  region the convention governs.)*

- **Roster use:** **None.** `stat-block-refs-in-prose` is structural — it asks
  whether a creature named in the prose carries its reference token, which is
  legible from the output alone. The disambiguating context ("which strings are
  creature names") is the **output's own `Enemies:` line**, not the roster. *(The
  roster is handed in per the launch protocol; this row does not read it.)*

- **Criteria:**
  - **Scope — this encounter's creatures.** The creatures in play are the ones on
    the `Enemies:` line. `stat-block-refs-in-prose` grades the **prose** — the
    Terrain & setup, Tactics, complication-staging, and Clue-note text around the
    block — for mentions **of those creatures**. Ambient fiction naming nothing that
    is statted in this fight ("guard dogs bark somewhere in the dark", "this is
    goblin country") is *not* a creature reference and is out of scope.
  - **Holds when** every prose mention of a creature that appears on the `Enemies:`
    line carries the reference convention — the `{monster:Name}` token where render
    tokens are in use, or a stat-block link to the campaign record otherwise —
    exactly as it does on the `Enemies:` line.
  - **Breaks when** a creature that is on the `Enemies:` line is named **bare** in
    the prose — the token/link present on the `Enemies:` line is dropped when the
    same creature is described in Terrain or Tactics ("the ogre charges from the
    ledge", with no token, though `{monster:ogre}` sits on the `Enemies:` line). The
    defect is one prose mention; report it at that sentence/paragraph.
  - **Cannot tell → disapprove.** If it is ambiguous whether a prose noun refers to
    a creature in this fight or to never-statted ambient fiction ("the goblins" —
    the two on the `Enemies:` line, or the region's inhabitants at large?), the
    checker **disapproves** and names the location, so the generator can
    disambiguate (tokenise the reference, or reword the ambient mention so it
    plainly is not one). Uncertainty is a disapprove, never a pass (this is the
    `unenforceable/stat-block-sweep-page-wide` difficulty made explicit).

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** `Enemies:` line: `{monster:ogre} ×1, {monster:goblin} ×4`.
    Tactics prose: *"The `{monster:ogre}` shoulders through the doorway round one
    while the four `{monster:goblin}` archers scatter to the gallery and loose from
    cover."* Every prose mention of an on-`Enemies:` creature carries its token.
    **Holds.**
  - **Bad — breaks.** Same `Enemies:` line. Tactics prose: *"The ogre shoulders
    through the doorway while the goblins scatter to the gallery."* Both creatures
    are on the `Enemies:` line with tokens, but their prose mentions are **bare** —
    the convention is dropped in the tactics text. **Breaks
    `stat-block-refs-in-prose`** at the Tactics paragraph (report each bare mention
    at its sentence).
  - **Edge — the boundary.** Same `Enemies:` line. Terrain prose: *"Old kennels line
    the north wall; you can still hear guard dogs baying somewhere below the keep."*
    No `guard dog` is on the `Enemies:` line — the baying is **ambient fiction,
    never statted**, so it is **out of scope** and does **not** break
    `stat-block-refs-in-prose`. **Holds.** *(Contrast: if a `{monster:mastiff} ×2`
    were on the `Enemies:` line and the prose said "two mastiffs lunge from the
    kennels" bare, that would break — the referent is a creature in this fight. When
    the checker cannot decide which case it is looking at, it disapproves and names
    the line.)*

- **Corpus pointer:** *none* — `stat-block-refs-in-prose` is structural (does this
  prose creature-mention carry its reference token?), so hand-written anchors are
  the floor and the ceiling. (The reserved corpus slot is for the
  reader-interpretation rows `lead-interpretability` / `clue-interpretability` /
  `plain-language` / `read-aloud-boundary` only.)

---

## Row `combat-generator/swarm-carries-fragile-creatures` — a swarm carries fragile creatures so the action economy does not crush the party

- **Inventory check id:** `combat-generator/swarm-carries-fragile-creatures`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the combat-generator table — method: "parse (ratio) + judgement", enforceability
  "Trigger yes, remedy no". The **trigger** — more than two creatures per character
  — is a mechanical ratio, deliberately **not** built as a deterministic check in
  the deterministic self-check because its **remedy has no deterministic heal**. This rubric
  grades the **remedy**: given the trigger fires, are fragile creatures included?)*

- **Promise text:** With **more than two creatures per character**, a lucky enemy
  streak can spike damage past what the budget implies — so **include fragile
  creatures that can be defeated quickly** to bleed off that risk (it matters most
  at levels 1–2).
  *(Source: `xp-budget.md` — "include **fragile creatures that can be defeated
  quickly**" — the Action-economy guardrails: "**More creatures per side = more
  dice = more swing … include fragile creatures that can be defeated
  quickly**".)*

- **Roster use:** **Reads party size.** The trigger is a ratio of creatures to
  **characters**, so the checker counts the encounter's creatures (from the
  `Enemies:` line) against the **number of PCs in the roster** to decide whether the
  row activates. Once activated, the *judgement* it grades — "is a quick-kill
  bleed-off valve present?" — reads the output's stat blocks, not the roster.

- **Criteria:**
  - **Activation (the trigger, strictly `> 2:1`).** Count creatures ÷ PCs.
    - **≤ 2 creatures per character → the row does not apply.** It **holds
      vacuously**; no fragile requirement, no finding. Exactly `2.0` (e.g. 8
      creatures / 4 PCs) is **not** greater than two — the row does not fire.
    - **> 2 creatures per character** (e.g. 8 / 3 = 2.67) → the row **activates** and
      the remedy is graded below.
  - **Holds when**, with the trigger active, the encounter includes **at least one
    fragile creature that can be defeated quickly** — a mook/minion whose HP and
    defenses let the party drop it in roughly a single turn's focus (low HP, CR well
    below the party's level), giving the party a way to thin the crowd and cut the
    incoming dice before the swing compounds.
  - **Breaks when**, with the trigger active, **every** creature is durable — nothing
    the party can remove quickly, so the >2:1 dice advantage rides for the whole
    fight with no bleed-off valve. Report it against the encounter (the `Enemies:`
    roster as a whole), not one line.
  - **Cannot tell → disapprove.** If the trigger is active and it is ambiguous
    whether any creature is *quickly defeatable* — the block does not make HP /
    defenses legible enough to judge the bleed-off valve exists — the checker
    **disapproves** and says so, so the generator can make the fragile creature
    plain (or add one). Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** 3 PCs; `Enemies:` `{monster:goblin} ×6, {monster:hobgoblin}
    ×2` — 8 creatures, 2.67 per character, trigger active. The six goblins (~7 HP,
    AC 15) drop to a single hit; the party can thin the swarm fast and cut the dice.
    A fragile bleed-off valve is present. **Holds.**
  - **Bad — breaks.** 3 PCs; `Enemies:` `{monster:orc} ×7` — 7 creatures, 2.33 per
    character, trigger active. Every orc is durable (~15 HP, hits hard); none can be
    removed in a turn, so the >2:1 dice advantage rides the whole fight with no
    fragile creature to bleed it off. **Breaks `swarm-carries-fragile-creatures`** —
    a level-1–2 party gets ground down by the action economy.
  - **Edge — the boundary.** 3 PCs; `Enemies:` `{monster:bandit} ×5,
    {monster:bandit-captain} ×2` — 7 creatures, 2.33 per character, trigger active.
    The bandits are **middling** — ~11 HP, AC 12: not clearly a one-hit mook, not
    clearly a tank. The judgement the checker must adjudicate is *"is this the
    quick-kill valve, or not?"* If the block makes plain that a level-appropriate
    party fells a bandit in one focused turn, the valve exists and it **holds**; if
    the block leaves the bandit's durability ambiguous — no HP legible, no tell that
    it drops fast — the checker **cannot tell** and **disapproves**, naming the
    encounter so the generator makes the bleed-off valve plain. This is the
    borderline the criteria exist to settle. *(The trigger-boundary — exactly 2:1 —
    is settled in the criteria above, not here: it is arithmetic the checker
    computes, not a judgement it adjudicates.)*

- **Corpus pointer:** *none* — `swarm-carries-fragile-creatures` is structural (does
  a triggered swarm carry a quick-kill valve?), so hand-written anchors are the
  floor and the ceiling.
