# Eval assertion inventory

The mechanically checkable promises this library already makes, swept out of all
`skills/*/SKILL.md` files and every reference file beside them. This is the
master list the runtime checker (`lib/mechanical-checker/checker.py`) is
derived from.
`zoom-in` has since been collapsed into `build-session`
as `node-deepening.md`,
so its rows are filed under `build-session` below.

**This file invents no criteria.** Every row cites a file plus an **anchor
phrase** that appears verbatim in the shipped skill text — ``
(`build-session/combat.md` — "each creature × count with looked-up XP") ``. A
bare filename means the file of
the skill the section is about; anything else is written relative to `skills/`.
Anchors replaced line numbers, which rotted on every edit and which nothing read
; `lib/citation_anchors.py`
asserts, on every `pytest lib/`, that each phrase is still there and that no
line-number citation has crept back. Where a promise cannot be enforced as
written, it is flagged in
[Unenforceable as written](#unenforceable-as-written) — flagged, not fixed.
Rewriting skill text is a different job.

## Check methods

| Method | What it means |
|---|---|
| **regex** | A pattern over the emitted text or a written file. |
| **parse** | Structured extraction, then an assertion over the fields (arithmetic, counts, set membership, enum). |
| **graph** | A property of the edge list / clue web as a graph. |
| **judgement** | Needs a model or a human. Not free. |

**Deliberately removed: the trace and diff classes.** This file once carried
67 rows in two further classes — `trace`, asserting over the agent's tool-use
stream (premised on the observation that a headless run also
yields the tool-call stream), and `diff`, asserting over the fixture repo's
before/after state. None was ever executed: no harness existed, and
`lib/mechanical-checker/checker.py` registered none of them, so every skill
edit paid their upkeep for checks that never ran. They were removed rather
than kept as dead weight
([Decide the fate of the never-executed trace and diff rows](https://github.com/bmoo/dm-skills/issues/8));
the promises they cited still live where they are authored, in the skill
text's own MUSTs, and `docs/backpressure-candidates.md` records the history.
The realized rows that grade the same ground through real tests
(`review-rewards`, below) stay.

**Removed with the verification-chain cut** ([Execute the verification-chain
cut](https://github.com/bmoo/dm-skills/issues/9)): the judgement rows whose
rubric was never authored — `dungeon-generator/verification-slate-verdicts-against-image`
(vision, deliberately excluded from the checker's input scope),
`seed-clues/clue-interpretability`, `seed-clues/player-reachable-vehicle`,
`catch-up/reactions-proposed-not-invented`, and
`party-sync/character-section-is-prose` — plus the judgement facet of
`review-rewards/depth-default-with-quality-floor`. Their promises stay as
plain instructions in the skill text, where they were authored all along.
The judgement rows that remain below are graded by each generator's
one-round fresh check, against completion criteria stated in the skill
text itself.

Methods combine where a row has two halves — `graph` plus `parse`, and in one row
(`build-session/brief-locked-subject-canon`) **code plus judgement**: the parse half
runs in the deterministic tier and the judgement half grades what it cannot reach.
A combined row says in its own text where each half stops.

A fourth axis worth naming up front: several rows are **static lints over the
skill text itself**, not over a run's output. Those cost nothing — no model, no
`claude -p` — and are listed separately at the end.

---

## build-session — the fight procedure (`combat.md`)

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/encounter-meta-required-lines | Six lines required in the encounter-meta block — Party, Enemies, Budget, Terrain, Spotlight, Objective; Note optional (`build-session/session-page-format.md` — "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required; Note is optional", "**Note:** <optional — table rules, dials, absence adjustments>"; cited by `combat.md` — "The block's shape is specified once, and not here") | regex | Yes |
| build-session/enemies-line-arithmetic | `Enemies:` line arithmetic — each creature × count with XP summing to the stated total (`build-session/session-page-format.md` — "each creature × count with looked-up XP") | parse | Yes |
| build-session/budget-line-arithmetic | `Budget:` line arithmetic — per-char × N = budget, and spent ≤ budget (`build-session/session-page-format.md` — "<per-char> × <N> = **<budget>**"; `combat.md` — "multiply by party size", "spend toward the budget without going over") | parse | Yes |
| build-session/per-char-matches-budget-table | The per-char figure matches the SRD 5.2 budget table for that level × difficulty (`xp-budget.md` — "Cross-reference party level with difficulty on the table below to get the **per-character** number") | parse (table lookup) | Yes |
| build-session/distinct-stat-block-cap | **Hard rule:** never more than three distinct stat blocks in one encounter (`xp-budget.md` — "Cap at three monster types — hard rule", "Never put more than **three distinct stat blocks** in one encounter") | parse (count distinct) | Yes |
| build-session/stat-block-refs-on-enemies-line | Every creature on the `Enemies:` line carries `{monster:Name}` or a campaign-record stat-block link; a bare name is a filing defect (`combat.md` — "a bare creature name is a filing defect, never a valid entry") | regex | Yes, on the `Enemies:` line |
| build-session/stat-block-refs-in-prose | Every creature name in the surrounding terrain/tactics **prose** carries `{monster:Name}` or a campaign-record stat-block link (`combat.md` — "in the surrounding terrain/tactics prose") | judgement | No — see `unenforceable/stat-block-sweep-page-wide` |
| build-session/spotlight-texture-in-palette | `Spotlight:` names a texture from the palette — aimed / puzzle / steamroll / plain / curveball (`combat.md` — "aimed / puzzle / steamroll / plain / curveball"; `spotlight-doctrine.md` — "Give every designed situation exactly one **texture**") | parse (enum) | Yes |
| build-session/targeted-spotlight-names-target-and-staging | An aimed or puzzle fight names *whom* it shoots at and the staging that fires their ability (`combat.md` — "if aimed or puzzle, who it shoots at and the staging that fires their ability") | parse | Yes |
| build-session/swarm-carries-fragile-creatures | More than two creatures per character → fragile creatures included (`xp-budget.md` — "more than **two creatures per character**", "include **fragile creatures that can be defeated quickly**") | parse (ratio) + judgement | Trigger yes, remedy no |
| build-session/complication-from-menu | At least one complication, drawn from the menu (`combat.md` — "choose **at least one** complication", "An encounter without a complication is not finished") | — | No parse target — see `unenforceable/complication-field-missing` |
| build-session/set-piece-two-complication-sections | Set-piece fights take two complications from different menu sections (`combat.md` — "for a set-piece fight, take **two, from different menu sections**"; the menu sections are `complications.md` — "## Terrain & the battlefield" and its sibling H2s) | parse (section membership) | Section half yes; trigger no — see `unenforceable/set-piece-undefined` |

## build-session — the keyed-site procedure (`dungeon.md`)

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/two-entrances | **Floor:** ≥ 2 entrances (`xandering.md` — "**≥ 2 entrances.** The approach is the first strategic choice") | graph (count boundary `→` edges) | Yes |
| build-session/at-least-one-loop | **Floor:** ≥ 1 loop — topology must not reduce to a line or tree (`xandering.md` — "**≥ 1 loop.** Two branches hooked together", "If the topology reduces to a line or a tree, it fails") | graph (cycle detection) | Yes |
| build-session/no-secret-gated-spine | **Floor:** no secret-gated spine — objective still reachable with every `secret` edge removed (`xandering.md` — "never sits behind a single hidden or missable thing") | graph (connectivity under edge removal) | Yes |
| build-session/objective-two-routes | **Floor:** objective reachable by ≥ 2 distinct routes (`xandering.md` — "The objective sits deep, reachable by ≥ 2 routes") | graph (disjoint paths) | Yes |
| build-session/objective-routes-cost-differently | **Floor:** the ≥ 2 routes to the objective each cost something different (`xandering.md` — "each costing something different — fights, hazards, the dungeon mechanic, a favor") | judgement | No |
| build-session/guarded-approach-holds | A page claiming guards interpose must not carry a route that breaks the claim: where the header names a guarded approach, every route from an entrance to the objective passes one of the rooms it names (`dungeon.md` — "no approach to the objective is free", "every route from any entrance to the objective passes one of those rooms"). **No claim, no finding** — a site that omits the line asserts nothing, and an unguarded back way is legal design until the page says otherwise. Secret ways in count: a route that slips past the posts is the defect whether or not it is hidden. A guard standing *in* the objective room is not interposing, so the objective is never one of the rooms removed | graph (reachability with the named rooms removed) | Yes |
| build-session/edge-types-in-vocabulary | Every edge typed from the closed vocabulary — base (open/door/locked/grate/vertical⟨stairs·shaft-chute·ladder·slope⟩) plus modifiers (secret·one-way·trap·hazard·up/down) (`dungeon.md` — "every connection typed with a **base** — open / door / locked / grate / vertical", "**modifiers** that apply: secret · one-way · trap · hazard · up/down") | parse (enum) | Yes |
| build-session/type-column-token-strictness | **Token strictness:** everything before the first em-dash in the Type column is typed tokens; prose after (`map-render.md` — "everything before the first em-dash in the Type column MUST be typed tokens from the vocabulary above") | regex | Yes — the strongest single grammar in the library |
| build-session/slate-picks-in-header | Both slate picks are named in the package header — a Signature-technique field and a Dungeon-mechanic field (`dungeon.md` — "naming the one of each", "name both picks in the header as any run does"). The presence half the two commitment rows below delegate: each of those reads its own field and stays silent when the field is absent, so dropping a field is a defect only this row catches | parse (field presence) | Yes |
| build-session/one-signature-technique | Exactly one signature technique, drawn from the twelve (`xandering.md` — "The signature technique — pick exactly one", "one technique explored deeply beats all twelve crammed in") | parse (count = 1, enum) | Yes |
| build-session/one-dungeon-mechanic | Exactly one dungeon-wide mechanic, or an explicit "vanilla" waiver — never two (`dungeon-mechanics.md` — "Every dungeon carries **exactly one** dungeon-wide mechanic by default", "but never gets two: competing gimmicks blur both") | parse (count ∈ {0,1}) | Yes |
| build-session/mechanic-four-part-box | The mechanic ships as a four-part box: Trigger/Clock · Effect · Tells · Exploit (`dungeon-mechanics.md` — "the delivered mechanic ships as this box", "**Trigger/Clock** — what sets it off or advances it", "**Exploit** — how mastering it pays") | regex | Yes |
| build-session/default-scale | Default scale: 6–12 keyed areas, 1–2 levels, 2–4 combats (`dungeon.md` — "roughly 6–12 keyed areas on one or two levels with 2–4 combats") | parse (counts) | Yes, when the DM didn't override |
| build-session/fight-mix | Fight mix: one High set piece, the rest Low/Moderate (`dungeon.md` — "one High set piece guarding the objective or its exit, the rest Low/Moderate") | parse (difficulty labels) | Yes |
| build-session/fight-mix-avoidable-or-negotiable | Fight mix: at least one fight in the site is avoidable or negotiable (`dungeon.md` — "at least one avoidable or negotiable") | — | No carrier field — see `unenforceable/fight-mix-avoidable-or-negotiable` |
| build-session/fight-budget-and-complication | Every fight carries budget arithmetic and a complication; two for the set piece (`dungeon.md` — "the sized encounter block — budget arithmetic", "the complication(s) from its menu") | parse | Inherits the fight procedure's encounter arithmetic — XP totals, per-char budget, the DMG-table check, the distinct-stat-block cap — and its complication rules |
| build-session/every-flagged-pc-staged | Every PC's flagged ability is staged somewhere in the site (`dungeon.md` — "every flagged PC staged somewhere in the site") | parse (set cover vs roster) | Yes |
| build-session/aimed-slots-balanced | Aimed slots are balanced across the flagging roster — nobody takes a second while another who flagged has zero, and per-PC counts stay within one (`dungeon.md` — "the aimed slots balanced across the flagging roster", "Balance is a property of the finished key list") | count (aimed slots per PC; assert max−min ≤ 1) | Yes |
| build-session/magic-item-on-approved-list | A magic item is placed silently only if on the repo's approved list (`dungeon.md` — "A magic item may be placed silently **only if it's on the repo's approved list**") | parse (set membership) | Yes |
| build-session/noncombat-beat-files-spotlight-scene | A non-combat beat the site stages for a PC files its own `Spotlight (scene):` line at that key (`dungeon.md` — "files its own `Spotlight (scene):` line at that key") | regex | Yes |
| build-session/lead-interpretability | Leads interpretable with only what players already know (`dungeon.md` — "is every planted lead **interpretable with only what the players already know**") | judgement | No |
| build-session/verification-slate-derived-from-edges | Verification slate is **derived from the edge list**: one line per edge, per secret, per trap, per hazard, per room, plus legend · scale bar · labels · inventions · surround (`map-render.md` — "Derive the slate **mechanically from the edge list before looking at the image**", "one line per **edge**", "one **surround** line") | parse (line count == derived count) | Yes — the slate's *shape* |

## seed-clues

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| seed-clues/three-clue-rule | Three Clue Rule: ≥ 3 independent clues / leads at the target (`SKILL.md` — "any place they must go needs the same in leads") | parse (count) | Yes |
| seed-clues/sources-on-different-nodes | **Must:** sources sit on different nodes (`SKILL.md` — "**Must:** sources sit on different nodes") | parse (distinct count == clue count) | Yes |
| seed-clues/one-clue-ungated | **Must:** ≥ 1 clue is ungated — no check, cost, or favor (`SKILL.md` — "at least one clue is ungated — no check, no cost, no favor") | parse (cost field) | Yes |
| seed-clues/discovery-mechanisms-diverse | **Should:** discovery mechanisms are diverse (`SKILL.md` — "**Should:** discovery mechanisms are diverse") | — | No — see `unenforceable/discovery-mechanisms-diverse` |
| seed-clues/candidate-tagged-derived-or-new-canon | Every candidate tagged **derived** or **new canon** (`SKILL.md` — "tag each candidate **derived** (follows from written canon) or **new canon**") | parse (enum) | Yes |
| seed-clues/candidate-carries-five-parts | Every candidate carries all five parts: what players perceive · what it points at · source node · how discovered · cost (`SKILL.md` — "**what the players perceive**", "**what it points at**", "its source node", "how it is discovered", "its cost (ungated, check, favor)") | parse | Yes |
| seed-clues/one-proactive-candidate | ≥ 1 **proactive** candidate on the slate (`SKILL.md` — "Include at least one **proactive** candidate") | parse (count) | Yes |
| seed-clues/delivery-timing-tag-verbatim | Delivery-timing tag is one of two **verbatim** strings — `surfaces late in node` / `latest & flattest — offhand, once, no chaseable trail` (`SKILL.md` — "a plain forward/exit lead → **surfaces late in node**", "**latest & flattest — offhand, once, no chaseable trail**") | regex (exact) | Yes — cleanest string assertion in the library |
| seed-clues/only-forward-lead-tagged | Only the forward/exit lead is tagged; lateral leads carry no tag (`SKILL.md` — "Only that lead is tagged", "Lateral leads need no tag") | parse (count ≤ 1) | Yes |
| seed-clues/cluster-has-exit-edge | Exit check: ≥ 1 progression edge leads out of the touched cluster (`SKILL.md` — "confirm the loop is not closed — at least one progression edge leads *out*") | graph | Yes |
| seed-clues/single-proactive-exit-reported-fragile | A cluster whose only exit is one proactive trigger is reported as fragile (`SKILL.md` — "A cluster whose only exit is a single proactive trigger is fragile") | graph + regex | Yes |
| seed-clues/candidate-slate-oversupply | Roughly twice as many candidates as the gap needs (`SKILL.md` — "Draft roughly twice as many candidates as the gap needs") | — | No — see `unenforceable/candidate-slate-oversupply` |

## build-session + session-page-format

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/skeleton-sections-in-order | All nine skeleton sections present, in order, each filled or its gap named (`session-page-format.md` — "Sections, in order. Every section is either filled or its gap named on the page", "Every skeleton section is filled or its gap is named on the page") | parse (heading order) | Yes for presence/order; "gap named" is judgement |
| build-session/key-npcs-header | Key NPCs table header is exactly **Name \| Personality \| Role \| Stat Block \| Location** (`session-page-format.md` — "**Key NPCs** — one table, one row per NPC or creature likely to appear", "**Personality** is a single character from popular fiction" — the disputed fifth column) | regex | Yes — but see `unenforceable/npc-roster-column-contradiction` |
| build-session/role-word-count | Role is 3–8 words (`session-page-format.md` — "**Role** is a short phrase (3–8 words)") | parse (word count) | Yes |
| build-session/stat-block-resolvable | Every row's Stat Block is resolvable; the literal `N/A (non-combat)` is a defect (`session-page-format.md` — "`N/A (non-combat)` is a defect; a bare creature name is too") | regex | Yes |
| build-session/location-uses-page-keys | Location column uses page keys (`T1`), not prose directions (`session-page-format.md` — "**Location** uses the page's own keys", "not prose directions") | regex | Partial |
| build-session/npc-rows-named | Every row named — a descriptive placeholder is a defect (`session-page-format.md` — "**Every row is named** — a descriptive placeholder") | judgement | No |
| build-session/contents-index | Contents index: one line, 5–8 links, no nesting (`session-page-format.md` — "5–8 links to the page's key stops", "One line, no nesting — a jump bar, not an outline") | parse (count) | Yes |
| build-session/no-empty-scaffolding | No empty Recap/Notes scaffolding on an unplayed page (`session-page-format.md` — "no empty Recap/Notes sections waiting to be filled") | regex (heading absence) | Yes |
| build-session/no-page-history-preamble | No page-history preamble (`session-page-format.md` — "**No page history.**", "never open a session sheet") | judgement | No |
| build-session/clue-payload-shape | Every clue payload is one self-contained block with three labeled parts — **Show** / **They learn** / **Points at** (`session-page-format.md` — "with three labeled parts", "Every clue payload is one self-contained block in the conventions' shape — Show, They learn, Points at") | regex | Yes for shape; self-containment is judgement |
| build-session/slate-indexes-only | The slate only indexes clues — no clue content lives solely in the slate (`session-page-format.md` — "**The slate is an index:**", "no clue content lives only in the slate") | parse (every slate line links to a payload) | Yes |
| build-session/conclusion-leads | Conclusion carries ≥ 2 live leads to other nodes (`session-page-format.md` — "at least two live leads into the clue web toward other nodes, with no steer", "The Conclusion leaves at least two live leads to other nodes") | parse (count) | Yes |
| build-session/foreshadow-not-a-lead | Foreshadow-tagged content never counts toward the exits (`session-page-format.md` — "Content that reads only in retrospect is labeled **foreshadow**", "never counts toward the Conclusion's exits") | parse | Yes |
| build-session/lead-actionability | "Lead →" only where the actionability test passes (`session-page-format.md` — "holding it plus what the party has already encountered") | judgement | No |
| build-session/fights-are-encounter-meta | Every fight is a `> [!encounter-meta]` block (`session-page-format.md` — "Every fight is an `> [!encounter-meta]` block, complete per the fight procedure's own rules") | regex | Yes |
| build-session/art-style-declared | `art_style:` declared in frontmatter (`session-page-format.md` — "Record the style in the page's frontmatter", "`art_style:` declared in frontmatter and held across every image") | regex | Yes |
| build-session/art-pieces | Four narrative art pieces; splash immediately after the title/badge block; node diagram with the scene list, not at the top (`session-page-format.md` — "Every session carries **four narrative pieces**, regardless of length", "placed **immediately after the title/badge block**", "**The node diagram does not count** toward the four") | parse (count + position) | Yes, given a rule for identifying the node diagram |
| build-session/float-before-prose | `art-left`/`art-right` floats sit directly before wrapping prose, never adjacent to another callout (`session-page-format.md` — "place a float directly before the paragraphs or bullets that wrap it, never adjacent to another callout") | parse (block adjacency) | Yes |
| build-session/art-style-differs-from-neighbors | Art styles differ from the neighboring sessions' `art_style:` keys (`session-page-format.md` — "read the neighboring sessions' `art_style:` keys and pick something clearly distinct from all of them") | parse (inequality) | Inequality yes; "vary widely" no — see `unenforceable/art-styles-vary-widely` |
| build-session/links-resolve | Every link on the page resolves (`session-page-format.md` — "**Links and callouts.** Every link resolves", "Every link resolves; conventions match the repo guide") | parse (link checker) | Yes — pure static check on the emitted page |
| build-session/hotspot-map | Where a hotspot treatment exists: one labeled hotspot per key, no plain unlabeled keyed map, no redundant ASCII duplicate beside it (`session-page-format.md` — "a keyed map embeds with a labeled hotspot link per key", "no redundant text diagram of the same structure sits beside a hotspot map") | parse (hotspot count vs key count) | Yes |
| build-session/keyed-site-carries-map | A page with keyed areas embeds its rendered map — required because the abolished exits enumeration leaves prose and the map as the site's only readable topology (`session-page-format.md` — "**A keyed site carries its map.**", "**embeds its rendered map**", "**the room prose and the map are the only human-readable topology the site has**", "**silent data loss — a keyed dungeon the DM cannot navigate**") **Deliberately not merged with `build-session/hotspot-map`**: that row fires on a *hotspot treatment that already exists* and counts its badges against the keys, so it is silent on a page carrying no map at all — different trigger, different failure. Its unimplemented no-redundant-ASCII-duplicate clause stays its own, and out of this row | parse (keyed areas present → a `> [!map]` embed present) | Yes |
| build-session/edges-not-dm-visible | The render-ready edge table is filed on the page but concealed, and no edge ID survives anywhere a DM reads — a keyed area's exits, body prose, a `> [!dm-sidebar]`, an `> [!encounter-meta]` terrain line; keyed-area IDs are exempt (`session-page-format.md` — "**wrapped in an HTML comment**, so it renders to nothing and no reader ever sees it", "**stays on the page — never deleted**", "**Edge IDs appear nowhere a DM reads**", "**Keyed-area IDs are unaffected**", "**The per-key exits enumeration is abolished, not de-coded.**") | regex (negative, over the page's DM-visible text) | Yes for the codes and the concealment; whether a connection is described where it is narratively relevant is judgement |
| build-session/spotlight-coverage | Spotlight plan covers every PC — a beat or named resting (`SKILL.md` — "The plan is done when every PC is either given a beat or named as resting", "the spotlight plan covers every PC (a beat or named resting)"; `spotlight-doctrine.md` — "Every PC gets a beat somewhere across a scenario group — in any pillar") | judgement (over a deterministic pre-pass) | No, but newly checkable. The old "no durable artifact" verdict is stale: once the plan became transient, every staged beat landed as its own page annotation naming its target PC, so the **covered set is derivable from the finished page**. A deterministic pre-pass (`spotlight_coverage`) computes `roster − PCs named in Spotlight annotations` (both shapes, `session-page-format.md` — "**Spotlight lines.**") and hands the uncovered set + per-PC beat share to the judge. It **cannot fail a page alone** — "absence is the record: a PC named nowhere on the page was planned as resting" (`session-page-format.md` — "a PC named nowhere on the page was planned as resting"), so an uncovered PC is *either* a deliberate rest or a dropped beat, and only judgement separates them |
| build-session/spotlight-plan-not-filed | The spotlight plan is **never filed on the page** — no table, no Preparation entry, on a full or lean-sheet run (`SKILL.md` — "The spotlight plan is not filed on a lean-sheet run either"; `session-page-format.md` — "**The session spotlight plan is not filed here** — or anywhere on the page as a table", "The plan itself appears nowhere on the page: no table, no Preparation entry"). Long mis-classed `diff (negative)` and re-methoded when the trace/diff classes were removed: the registered check (`checker.py`) needs no before/after state — it reads the finished page alone for five filing shapes (a spotlight heading, a plan label, a plan-shaped table, annotations nested under Preparation, a filed resting roster) | regex (negative, pure output) | Yes — realized in `checker.py` |
| build-session/spotlight-annotations-name-pc | Every beat the plan staged carries its page annotation, each naming its target PC — encounter-meta `Spotlight:` for a fight, a `Spotlight (scene):` sidebar line otherwise (`session-page-format.md` — "**Every staged beat names its target PC** — an unnamed line is a defect", "Every beat the session's spotlight plan staged carries its page annotation"). **Absorbed exception — the plain fight and the pocket beat**: the encounter-meta `Spotlight:` field is a **required** label on *every* fight (`session-page-format.md` — "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required"), so a fight that stages no beat still carries one and has nothing to name — the library's own doctrine then produced a page its own gate failed. The shipped format already scopes the who-clause to the targeted textures (`session-page-format.md` — "if aimed/puzzle, who and the staging that fires their ability"), and `build-session/targeted-spotlight-names-target-and-staging` already absorbs that exception on this same field; this row had simply over-read its neighbouring sentence. So a **fight** field satisfies this row by declaring the one palette texture doctrine defines as aiming at nobody (`spotlight-doctrine.md` — "fiction-first, nobody aimed at. Legitimate and necessary", "**No single situation must aim at anyone.**") — which is what a doctrinally-required plain fight and the method doc's pocket beat (`build-session/SKILL.md` — "is *not* a budgeted beat — it is unplanned reserve that may never fire") both are. **Narrow by construction, not an escape hatch:** only the affirmative `plain` declaration excuses, so an `aimed` fight naming nobody — or any other unnamed value — still fires; and a `Spotlight (scene):` line is **never** excused, because a scene line exists only where a beat was staged (`session-page-format.md` — "each beat it stages appears at the scene that stages it"), so relabelling one `plain` does not rescue it. A page of nothing but plain fights passes this row **by design**: that page's uncovered set is `build-session/spotlight-coverage`'s to rule on, and firing here would usurp its ruled legal absence (`session-page-format.md` — "a PC named nowhere on the page was planned as resting") | regex (shape + a PC name from the roster, or the palette's `plain` texture on a fight field) | Yes |
| build-session/spotlight-shapes-separate | The two shapes stay separate: no `Spotlight (scene):` line inside an encounter-meta block, so the fight-variety ledger stays fights-only (`session-page-format.md` — "**The two labels are deliberately distinct.**", "a scene line must never read as a fight in that ledger") | regex (negative) | Yes |
| build-session/stat-block-sweep-page-wide | Stat-block sweep: every creature name anywhere on the page carries a resolvable reference (`session-page-format.md` — "A bare creature name is a defect: a missing link is not a broken link", "The stat-block sweep is done") | judgement | No — see `unenforceable/stat-block-sweep-page-wide` |
| build-session/plain-language | Plain-language sweep: no run-time line rests on an undefined coinage (`session-page-format.md` — "**Plain language in run-time text.**", "no run-time line depends on an undefined coinage or metaphor") | judgement | No |
| build-session/read-aloud-boundary | Read-aloud sweep: every read-aloud block carries only what the characters perceive from where they stand — no hidden history, causes, intent, or meanings; no imposed emotions or decisions; nothing beyond the party's vantage; dialogue, readable text, sensation-scoped atmosphere, and involuntary physical reactions stay legal (`session-page-format.md` — "**Read-aloud is what they perceive.**", "could someone standing there perceive this, from where they stand, right now?", "The read-aloud sweep is done") | judgement | No |
| build-session/aimed-item-names-pc | An item reward aimed at a particular PC names them in the Conclusion (`session-page-format.md` — "an item aimed at a particular PC names its intended PC"; `SKILL.md` — "The Conclusion line for an aimed item names its target PC") | parse (a roster PC name on the reward line) | Yes |

## build-session — `node-deepening.md`

The node-deepening procedure `build-session` loads at Step 3 (formerly the
`zoom-in` skill; it was later collapsed into `build-session`.

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/node-frontmatter-conventions | Frontmatter matches the page's directory and status conventions (`node-deepening.md` — "Frontmatter matches the page's directory and status conventions") | regex (vs fixture conventions) | Yes |
| build-session/clue-web-section-present | Clue-web section present with its glance line, even when leads are few (`node-deepening.md` — "Clue-web section present with its glance line (even if leads are few)") | regex | Yes |
| build-session/ious-keyed-or-rejected | Every IOU from step 1 keyed or explicitly rejected (`node-deepening.md` — "**IOUs** this pass must honor", "every IOU keyed or explicitly rejected") | parse (set cover) | Yes, given IOUs are marked in the fixture |
| build-session/clue-web-indexes-only | Clue content lives in the body under its own headings; the clue-web section only indexes (`node-deepening.md` — "Clue *content* lives in the body under its own headings; the clue-web section only indexes it") | parse | Yes |
| build-session/clue-interpretability | Every clue carries a player-reachable vehicle and is interpretable when found (`node-deepening.md` — "must carry a player-reachable vehicle: a concrete scene, action, check, or bargain yields it", "interpretable using only what the players already know when they could plausibly find it") | judgement | No |
| build-session/node-is-durable-situation | The page reads as a durable situation — more material than one session consumes (`node-deepening.md` — "the page reads as a durable situation — more material than one session consumes") | — | No — see `unenforceable/node-is-durable-situation` |
| build-session/no-plot-decisions | Decide nothing plot-relevant; bring plot decisions to the DM (`node-deepening.md` — "Elaborate set dressing freely — decide nothing plot-relevant") | judgement | No |

## build-session — the Spec axis (the session brief)

Every row above grades the page against a **library** promise — the Standards axis,
identical on every run. These grade it against **tonight's contract**: the session
brief the DM agreed before the build, published as a ticket on the campaign tracker
(`to-session-brief/SKILL.md` — "a published brief is in force") and read by
`build-session` when it takes the brief, before anything is read for the
build. The first nine are the **mechanically-checkable** half of
that axis,
derived from the named fields before drafting (`build-session/SKILL.md` — "Derive
tonight's Spec-axis check set from it") and run red-green during the build
(`build-session/SKILL.md` — "Draft to green against tonight's contract"); the last
three are the judgement-graded half, graded by the same one-round fresh
check as the Standards criteria (`build-session/SKILL.md` — "graded in the
same pass, against the brief itself").

**One row per filled field, and no row at all where the brief is silent.** Every row
below reads its own field out of the brief text handed in as `context["brief"]` and
returns nothing when that field is absent, so default-to-disapprove is scoped to a row
and never to the page (`build-session/SKILL.md` — "silence is never a constraint"; the brief
reaches the check as a tracker issue URL, `build-session/SKILL.md` — "body
only"). The **brief itself** is not optional: a
check asked to grade a contract it was never handed **raises** rather than faking a
verdict, the refusal `build-session/spotlight-annotations-name-pc` already makes
without a roster. Field names are read off the shipped template
(`to-session-brief/SKILL.md` — "Each line is a proposition about the finished page"),
so a brief written to that template needs no other convention; the two judgement-graded
fields (`Premise`, `Fit to established geography`) parse alongside these and yield no
mechanical id.

**The one row that is not a field row** is `build-session/brief-locked-subject-canon`.
It grades the Locked lines *as a set* — every subject any of them names — so there is no
field to leave blank and no id for `brief_checks` to return; it runs whenever a brief is
in force and finds nothing to say when the Locked half names no subject at all. It is
the row-not-a-channel the ablation asked for: it reads the record extract
`build-session/brief-introduced-canon` already requires and adds no input of its own.

**What these rows reach, said once here rather than row by row below.** A brief is
prose a DM wrote quickly, so no row here matches a *meaning*; each matches the
**named things** a field commits to — a proper-noun run, a clock hour, a DC, a count,
a revelation's own name — against the **structural slot** the page format puts them
in: a heading, the keyed index (`session-page-format.md` — "the **keyed index**
directly under the map"), the Features preamble (`session-page-format.md` — "a
**Features** preamble for what holds everywhere"), a clue payload
(`session-page-format.md` — "**Points at** *(behind the screen)* — the node or
revelation the clue targets"), the Key NPCs table, the Conclusion's exits
(`session-page-format.md` — "at least two live leads into the clue web toward other
nodes, with no steer"), or the edge table. **A whole-page phrase search is the
exception, never the default**: it is what makes two rows satisfiable by one sentence,
which is the failure this split exists to prevent, and exactly one row below takes it —
`brief-destination-nodes`, against evidence, with the cost stated in the row. Whether
the page is *right* about any of it stays judgement, and each row says where its own
reading stops.

**Calibrated against the frozen arms, not against intuition.** Every row here was run
over the seven worked Gloamfen pages in the ablation apparatus with their own briefs.
Five findings on pages that had kept the contract were traced and killed at the source:
a page writing *a thirty-foot ceiling* had stated a `30 feet` rule; a page naming the
close of a *6–8 p.m.* window had carried it; a page keying a clue called *Fenwick's
ledger* was not staging the excluded *Fenwick's reinstatement*; and three pages that
built the destination under a colloquial section title were not aimed elsewhere. **One
finding survived deliberately** and is described in `brief-revelation-paid-down`.

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/brief-introduced-canon | Every fact the brief lists under `Introduced canon` — facts tonight asserts the record does not already hold (`to-session-brief/SKILL.md` — "Facts tonight asserts that the record does not already hold") — is graded **twice against the campaign canon record extract**, the durable record extract handed in as its own named input on the party roster's precedent (`to-session-brief/SKILL.md` — "checked as a diff against the campaign canon record, which the checker is handed"; the checker has no filesystem reach into the campaign record — the extract is handed in, `build-session/SKILL.md` — "campaign canon record extract"): the **diff** half, that the record does not already carry the fact; and the **landed** half, that the page asserts it somewhere. It is the row **defined as** that diff, and it **refuses to run without** the extract rather than grading half a definition; `build-session/brief-locked-subject-canon` consumes the same extract on the same terms, which is what makes that row a row rather than a second channel | parse (term set vs the record extract, then vs the page) | Partial, and conservative in both directions by construction. The diff fires only when **every** distinctive term of a fact is already in the extract, so a genuinely new fact *about an existing subject* — which shares that subject's name with the record and nothing else — never fires; the landed half fires only when **none** of a fact's terms appears on the page, so a fact the page reworded still passes and only a fact the page never touched is caught. Both under-report deliberately: a false finding against a contract the DM wrote is worse here than a missed one, and *is this the same fact, said differently?* is judgement |
| build-session/brief-ground-rules-stated | The brief's named ground rules of tonight's place are stated on the page **before any room is keyed** (`to-session-brief/SKILL.md` — "The named ground rules of tonight's place, stated before any room or NPC is keyed"), which is exactly the format's Features slot (`session-page-format.md` — "a **Features** preamble for what holds everywhere", "(`T1`, `R3`…) each with its run content"). Graded on **the rule as stated**: each hard token the brief's rules carry (a DC, a die, a distance) present on the page — a distance in either notation, since a page writing *a thirty-foot ceiling* has stated a `30 feet` rule — and each present **ahead of the first keyed area of the section that rule is stated in**, judged per rule rather than against one boundary drawn from whichever rule happened to appear earliest. **Nothing about routes** — whether the page's own edges are consistent with a claim that guards interpose is `build-session/guarded-approach-holds`, a Standards row that needs no brief (`build-session/dungeon.md` — "every route from any entrance to the objective passes one of those rooms"), and the overlap between the two fields dissolved into it rather than being split between them | parse (token presence + position against the first keyed area) | Yes for both halves, on rules that carry a hard token. Two things it does not reach, named rather than smoothed: a ground-rules block written in pure prose carries no token and goes ungraded; and the field's **declared home** (node canon / campaign reference / introduced here — `to-session-brief/SKILL.md` — "with its home: node canon / campaign reference / **introduced here**") is the *brief's* declaration and is carried into the finding so the DM can see whether a dropped rule exists anywhere else. It is deliberately **not** graded as a page-visible provenance marker: the page format has no such slot, and minting one would be a new checkable promise this row is not entitled to make. The boundary is the first **keyed area**, not the Key NPCs table, because the format mandates that table as an early skeleton section (`session-page-format.md` — "Sections, in order") — a boundary no format-conformant page could clear is a broken row, and rooms and NPCs alike are *keyed* from the first keyed area on |
| build-session/brief-npc-commitments | Per named NPC, the page carries that NPC (`to-session-brief/SKILL.md` — "Per named NPC: identity, allegiance, and whether they survive"): every NPC the field names has a row of their own in the Key NPCs table (`session-page-format.md` — "**Key NPCs** — one table, one row per NPC or creature likely to appear"). Set cover against the brief, the same shape as `build-session/every-flagged-pc-staged` against the roster. The *"name only those an edit could not route around"* qualifier is the **brief's** instruction to its author (`to-session-brief/SKILL.md` — "name only those an edit could not route around") and is never a criterion here — this row grades the names it was given, and does not second-guess which ones earned a line | parse (set cover vs the Key NPCs Name column) | **Identity only, and the row ships precautionary.** Allegiance and survival are not reachable: the roster table's five columns carry neither (`session-page-format.md` — "**Personality** is a single character from popular fiction"), and adding one to carry them would re-decide the shipped template and mint a new format promise. So a page that lists a locked NPC and then reverses their allegiance passes this row; that is the judgement half's to catch. The field's own status is honest too — its ablation **leaked** (the withheld arm's `Exit edge` still named the curator's syndicate, so the roster kept her), which means its absence was never actually tested and the field is retained on the precautionary reading rather than earned by evidence |
| build-session/brief-timeline-commitments | The schedule the brief's `Timeline commitments` fixes survives onto the page: every **hour** the field names — a clock time or a named hour (midnight, noon, dawn, dusk) — is named on the page too, and **an hour range is one requirement either endpoint satisfies** (`to-session-brief/SKILL.md` — "The question that resolves tonight, either way — with the schedule as optional fill where one exists"). An hour is satisfied by **either** notation: a page writing *half past ten* has kept a 10:30 p.m. commitment, and a check that fires on that is a check about punctuation, not about the contract | parse (hour requirements from the field vs hour set from the page) | The schedule half yes. A range counts once because it names a **window**, not two commitments — the gala that runs *6–8 p.m.* is one fact, and a frozen arm that named only the close of that window had kept it. **The resolution half — that the question resolves tonight, either way — is not mechanical** and is not attempted here; a field carrying no clock at all (three of the four ablation situations carry none) yields no hour and this row stays silent on it, which is the field being kind-conditional rather than the field failing. Two blind spots: an hour word that doubles as a count (*one*, *two*) is cheap for a page to satisfy, and the row asserts an hour is *named*, never that the page hangs the right event on it |
| build-session/brief-revelation-paid-down | The revelation the brief names is paid down **through the clue web**: it is carried by at least one **clue payload block** (`session-page-format.md` — "**Points at** *(behind the screen)* — the node or revelation the clue targets") — named there, or said in the page's own words, since a payload carrying every distinctive term of the revelation has carried it — and where the field states both endpoints of its transition — *from j of n to k of n* — the page carries at least **k − j** distinct payloads (`to-session-brief/SKILL.md` — "Which one tonight advances, and to what state"). **This grades the named state transition, not that the page is about the revelation**, which is what makes it independently failable from the rubric-graded `Premise` row: a page can enact the premise in full and leave the revelation exactly where it was, and that is the failure the split buys. Reading payload blocks rather than prose is what enforces the split — **the sentence that satisfies `Premise` is prose and cannot satisfy this row** | parse (revelation name vs clue-payload blocks; count arithmetic where both endpoints are stated) | Yes, on the structural half. The revelation's **name** is taken from the field's emphasis or quotation spans, falling back to its proper nouns, so a brief that names its revelation in bare unpunctuated prose is graded on the weaker key. What the row cannot reach is the *ledger*: whether the campaign's revelation tracker really stood at *j* going in is a fact about the record, not about the page, and the tracker is not an input. **The one finding retained against a frozen arm is this row's**, and it is retained on purpose: that page's payloads all point at nodes rather than revelations, which the page format permits in general (*"the node **or** revelation"*) — but a brief that locks a revelation transition makes naming it the contract, and a page that pays clues down without recording what they pay leaves the DM no way to tell the revelation moved. Five of the six frozen pages whose brief filled this field named it; one did not |
| build-session/brief-destination-nodes | Every destination the brief aims the session at is **named on the page** (`to-session-brief/SKILL.md` — "Where the session is aimed. Earlier leads already point into these"). Matched on the destination's proper-noun runs — which are alternatives, not requirements, since a node's full name breaks into several — and, where the brief links the node's page, on that link's basename | parse (name / link-basename set cover vs the page) | Yes, and it is **the one row here that reads the whole page rather than a structural slot — a weakening made against evidence and recorded rather than quietly taken.** It was written to read headings, the keyed index and link targets, and **three of the five frozen Gloamfen arms failed it while building exactly the right place**: they title the section *"Inside the Museum After Dark"* and carry the node's full name only in prose and in the node diagram. A row that fires on three correct pages grades naming conventions, not aim. What survives is the failure the brief exists for — a page that re-anchored on a different conceit names the destination nowhere. The cost is real and stated: a premise sentence naming the destination satisfies this row too. That is **not** one of the two pairs Implementation Decision 5 rules on, and the page it lets through — one that names the node in its premise and builds elsewhere — is what the rubric-graded `Premise` row is positioned to fail. `Node cluster in reach` is **not** a row: the field was cut from the template outright, so there is no field to grade |
| build-session/brief-exit-edge | The exit the brief fixes is **named in the Conclusion's leads**: at least one `Lead →` in the Conclusion names something the `Exit edge` field names (`to-session-brief/SKILL.md` — "Where the party can leave toward, per `seed-clues` Step 5"; `session-page-format.md` — "at least two live leads into the clue web toward other nodes, with no steer"). This is the half the library has never had — `build-session/conclusion-leads` counts the exits and never asks **which node any of them reaches**, and `seed-clues` Step 5's cluster-level exit check exists as prose and is implemented nowhere | parse (proper-noun runs of the field vs the Conclusion's `Lead →` lines) | Yes. It asserts the named target is reachable *from the page* — that a lead points at it — never that the lead leaves the cluster, which needs the clue web and is `seed-clues/cluster-has-exit-edge`'s. A field naming no proper noun at all (*"any progression lead out"*) leaves nothing to look for and the row stays silent |
| build-session/brief-map-topology | The **shape** the brief commits the geography to holds in the page's own edge table (`to-session-brief/SKILL.md` — "**Map topology.** The shape"): a stated count of entrances or ways in equals the count of boundary edges, and a topology that names any vertical structure — floors, levels, a basement, an attic — is carried by at least one `vertical` edge. Shape only; whether the shape **fits** established geography is the brief's separate rubric-graded field | graph (boundary-edge count, vertical-token presence) + parse (the stated count) | Yes, and it is the half the ablation earned: both withheld arms **flattened a vertical site into a walled yard**, which is exactly the vertical assertion. It reads the edge table at any heading level, since a session page nests one under its location section rather than at the top level. A page with no edge table at all — a night with no keyed site — carries no shape to check and the row stays silent; a topology sentence stating neither a count nor a vertical does the same |
| build-session/brief-not-tonight | Nothing the brief deliberately excluded is **staged** by the page: no `Not tonight` item appears as a heading, in the keyed index, or in a Potential Scenes entry (`to-session-brief/SKILL.md` — "Named and deliberately excluded, so their absence reads as a decision rather than an oversight") | parse (exclusion keys vs the page's staging slots — negative) | Yes, and the slot list and the key shape are the whole design. The slots exclude the Key NPCs table and the clue slate **deliberately**: the Gloamfen brief locks the curator as an NPC, points its `Exit edge` at her syndicate, and excludes *confronting* that syndicate — all three at once and all three correct, so a row reading NPC rows or lead targets would fire on a page that kept the contract perfectly. The key is the exclusion's proper-noun run **plus the common noun after it** for the same reason, learned from a frozen arm: *"Fenwick's reinstatement"* reduced to the bare run `Fenwick` — who is also the night's client — and reported a page keying a clue called *"Fenwick's ledger of nights"* as staging a thread it never touched. Where no common noun follows, the run stands alone (`Old Town`). An excluded thread the page merely mentions, or points a lead toward, is not staged and is not a finding. Also not a slot: **the page title**, since a session named for its own subject (*The Gloamfen Malevolence*) is not staging the dig its brief took off the board |
| build-session/brief-premise-enacted | The page **enacts** the night the brief's `Premise` describes (`to-session-brief/SKILL.md` — "does the page enact it", "One sentence: what is happening tonight and why the party is in it") — the party arrive at it the way the premise says they do, and the scenes and keyed areas the page stages are that night being run. **Enactment, and nothing else.** Restating the premise never satisfies this row: not in the header, not as a Key Plot Points beat, and **not in a clue payload block**, which is the slot `build-session/brief-revelation-paid-down` reads. That row grades the **named state transition** and this one grades whether the page runs the night, so neither can be satisfied by the sentence that satisfies the other — a page can enact the premise in full and leave the revelation exactly where it was, and a page can pay the revelation down while building a different night. It is also where the cost `build-session/brief-destination-nodes` accepted lands: a page that names the destination in its premise sentence and builds elsewhere passes that row and fails this one | judgement (the fresh check) | No — and it is the field the ablation showed a brief cannot do without: the arm handed no brief at all was the one arm that failed premise enactment outright, keying the yard and never entering the house. What a checker must supply is the read no parse makes: whether the staged night *is* the night the sentence describes, rather than a night that shares its nouns |
| build-session/brief-fit-to-geography | The page's geography **fits what the record already establishes** — what the brief's `Fit to established geography` line commits to (`to-session-brief/SKILL.md` — "Layout — what the geography commits to", "Fit to established geography.") holds against the campaign canon record extract: what stands next to what, how far apart, and in which direction, as the page's map, travel times and sight-lines carry it. Graded against the extract for the same reason `build-session/brief-introduced-canon` is — the checker has **no filesystem reach into the campaign record**; the extract is handed in | judgement (the fresh check) | No, and **this row ships on the precautionary reading rather than an earned one — said here rather than smoothed over.** The field passed in *every* ablation arm that was scored for it, including the arm handed **no brief at all**, and in four of five arms of the other frozen situation; the one failure was collateral, in an arm withholding a different field. Worse, the test that would settle it has never been run: both situations' records already carried enough geography for the generator to fit, so the field has **never been tested against genuinely blank geography**. It is retained because a page that moves the tavern next door is a defect the DM would keep the page and curse, not because the ablation caught one |
| build-session/brief-locked-subject-canon | For **each subject a Locked line names**, the page asserts no fact about that subject which neither the brief nor the campaign canon record extract supplies (`SKILL.md` — "A subject a Locked line names is not silence"). **This is not a general no-new-canon rule**: a subject the brief never locks is silence, and inventing there is exactly what the generator is for (`SKILL.md` — "invent where both are silent"), so new content about an unlocked subject is never a finding here. Two halves, and the split is the honest one. The **executable** half reads the page's **Adventure Background** — the section the format defines as the page's own voice on what is true (`session-page-format.md` — "**Adventure Background** — what is actually going on, written for the DM") — and fires where a sentence naming a locked subject carries a **quantity** (a numeral or its spelled form) that appears in neither the brief nor the extract. The **judgement** half grades what a number does not mark. It rides on an input the axis already requires and adds **a row, not a channel** | parse (locked-subject set from the Locked fields × unlicensed quantities in the Adventure Background, against brief + record extract) + judgement (the fresh check) | Partial, and the partial half is the point. **The gap it closes is real and was invisible to the whole proposition set**: one frozen arm scored **11 of 11** while minting seven new facts about objects its brief locked — the sharpest of them a whole invented provenance for a locked item — and nothing in the set penalised it, because every other row asks whether the licensed facts *landed*, never whether unlicensed ones were added. The numeric tell catches the inventions that carry a number (*"made it himself, forty years ago"*) and never the ones that do not (*"and he made it badly on purpose"*), which is why the judgement half is not optional. Two scope decisions, both deliberate: the **Adventure Background only**, because a keyed area rendering a locked place in fresh words is the page doing its job and a whole-page read would fire on every correct page; and the subject set is taken from the **Locked** fields only, never from `Not tonight`, whose subjects are excluded rather than locked |

## catch-up

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| catch-up/spotlights-reconciled-from-annotations | Staged spotlights reconciled **from the page's annotations** — every encounter-meta `Spotlight:` field and `Spotlight (scene):` line — recording which **fired** and which were **denied or skipped**; the plan itself is transient and is never the source (`SKILL.md` — "the ledger is the session page itself: every encounter-meta `Spotlight:` field and every `Spotlight (scene):` sidebar line", "Record which of those staged beats **fired** and which were **denied or skipped**") | regex (player pages) + parse (set cover vs the page's annotations) | Yes |
| catch-up/loot-receipts-recorded | The recap names which PC received each item the session handed out (`SKILL.md` — "the recap names which PC received each item the session handed out") | parse (recap vs scripted transcript) | Yes, against a fixture transcript |


## build-session — the spotlight procedure (`spotlight.md`)

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| build-session/one-texture-per-situation | Exactly one texture per designed situation, from the five-value palette (`spotlight-doctrine.md` — "Give every designed situation exactly one **texture**, and rotate") | parse (enum, count = 1) | Yes |
| build-session/table-experience-rung-enum | **Table experience** rung ∈ {`new`, `learning`, `seasoned`} (`spotlight-doctrine.md` — "a three-rung ordinal — lives here and nowhere else") | parse (enum) | Yes |
| build-session/flagged-ability-pillar-and-staging | Every flagged ability tagged with its pillar ∈ {combat, social, exploration} and the staging that fires it (`spotlight-doctrine.md` — "Tag every flag with the **pillar** it lives in") | parse | Yes |
| build-session/no-repeat-staging-per-pc | Never the same staging for the same PC twice running (`spotlight-doctrine.md` — "**Never the same staging for the same PC twice running.**") | parse (vs the ledger) | Yes |
| build-session/curveball-on-request-only | Curveball is **on request only**, roughly once per adventure, and names whose tricks it denies (`spotlight-doctrine.md` — "**On request only**, roughly once per adventure: name whose tricks it denies") | parse | "Names whose" yes; frequency no |

## party-sync

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| party-sync/draft-placeholders-never-filed | Unknown or unfilled fields file as named gaps, never as placeholder numbers presented as canon (`SKILL.md` — "never file placeholder stats as canon") | regex (absence in the written page) | Yes |
| party-sync/player-matches-page-basename | `player` in the cache matches a player page basename (`SKILL.md` — "`player` must match a player page basename — that's the join key for page updates") | parse (set membership) | Yes |
| party-sync/unconfirmed-party-prompts-refresh | Cache not confirmed since before the last played session → say so and offer a refresh before relying on numbers (`SKILL.md` — "hasn't been confirmed since your last session") | parse (`confirmedAt` vs latest session date) + regex | Yes |
| party-sync/source-provenance-recorded | Each character's cache entry records which rung produced it — the tool's name or `interview` (`SKILL.md` — "records the source that produced it") | parse (field presence) | Yes |

## campaign-art

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| campaign-art/output-basename-matches-page | Output basename is kebab-case and matches the page basename (`SKILL.md` — "a descriptive kebab-case basename. Match the page basename") | regex (output path) | Yes |
| campaign-art/prompt-carries-exclude-clause | Prompt carries the Exclude clause — no text, captions, watermarks, frame (`SKILL.md` — "Exclude: no text, captions, watermarks, or frame/border — unless asked") | regex (prompt string) | Yes |
| campaign-art/prompt-composes-eight-parts | The prompt composes all eight labelled parts (`SKILL.md` — "write them as flowing sentences, not literally as a form") | — | No — see `unenforceable/prompt-composes-eight-parts` |

## review-rewards

The deterministic rows here are already realized: the skill ships its review
app as code, so the promises live behind a real seam and the bundled pytest
suite (`skills/review-rewards/scripts/test_*.py`, collected by a repo-root
`pytest`) asserts them today — no checker derivation pending. The quality
floor's judgement facet was retired with the verification-chain cut; it
stays a plain instruction in the skill text.

| Slug | Promise (source) | Method | Enforceable as written? |
|---|---|---|---|
| review-rewards/pool-exactly-approved | After ingestion the Approved Reward Pool contains exactly the approved and retained items in their consumer shape (`SKILL.md` — "contains exactly the approved and retained items in consumer shape") | parse + diff — realized in `test_ingest.py` and `test_e2e.py` | Yes |
| review-rewards/pool-carries-no-history | Deferrals, removals, review notes, and full rules text never enter the pool (`SKILL.md` — "Deferrals, removals, notes, and full rules text stay in the review state") | regex (absence) — realized in `test_ingest.py` | Yes |
| review-rewards/server-loopback-only | The review app binds loopback only; rules text is never reachable off the machine (`SKILL.md` — "The app is bound to loopback") | parse (bind address) — realized in `test_review_server.py` | Yes |
| review-rewards/state-write-confinement | The server writes only the designated decision-state file, whatever a request carries (`SKILL.md` — "writes only the designated decision-state file") | diff (filesystem before/after) — realized in `test_review_server.py` | Yes |
| review-rewards/ingest-validates-before-write | A malformed, stale, or unknown-decision payload is refused with the pool untouched (`SKILL.md` — "Ingest validates before it writes", "leave the pool untouched") | diff (negative) — realized in `test_ingest.py` | Yes |
| review-rewards/awarded-read-only | Awarded Items render as read-only history; a decision recorded against one fails validation (`state-format.md` — "read-only history, for loot parity") | parse — realized in `test_review_state.py` | Yes |
| review-rewards/graveyard-stays-removed | A graveyard entry stays removed until the DM writes an explicit restore decision (`state-format.md` — "with no record stays removed") | parse — realized in `test_review_state.py` and `test_e2e.py` | Yes |
| review-rewards/depth-default-with-quality-floor | Default depth is five per active PC plus five whole-party, overridable at invocation, under a quality floor that omits filler (`SKILL.md` — "five new candidates per active PC and five whole-party candidates", "fewer results are correct whenever another item would be filler") | parse (counts) | Counts yes; the quality floor is a plain instruction, not a row |
| review-rewards/official-2024-sources-only | Candidates come from official 2024-generation sources only (`SKILL.md` — "2014-era versions, third-party content, and homebrew are outside the catalog") | parse (source fields) | Yes |

---

## Static lints — no model run required

These check the **skill text itself**, not a run's output. They are free, they
run in milliseconds, and they catch the class of defect already sitting in the
library maintenance history (including ghost skill
references).

| Slug | Check | Method |
|---|---|---|
| lint/frontmatter-name-matches-dir | Frontmatter `name` matches the skill's directory name | parse |
| lint/frontmatter-has-name-and-description | Frontmatter carries both `name` and `description` | parse |
| lint/relative-links-resolve | Every relative link in a skill file resolves to a file that exists — including cross-skill loads (`../build-session/spotlight-doctrine.md`) | parse |
| lint/anchor-links-resolve | Every anchor link resolves to a heading that exists (e.g. `spotlight.md#the-data-ladder`, `spotlight-doctrine.md#legibility`) | parse |
| lint/named-handoff-skills-exist | Every skill named in prose as a hand-off target (`catch-up`, `seed-clues`, `campaign-art`) exists in `skills/` | parse |
| lint/encounter-meta-fields-match-parser | The encounter-meta field list, read out of the shipped spec section (`build-session/session-page-format.md` — "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required; Note is optional"), matches **both** code paths that read the block: the checker's `_ENCOUNTER_META_REQUIRED` literal, and the session parser's reading of the spec's own example block (`build-session/scripts/session_parser.py` — "encounter-meta"). The parser keeps a callout body as an opaque string and carries no field list to compare — so what it is held to is that the spec's block still parses as an `encounter-meta` callout with every label intact. The anchor sweep exposed that the parser had nothing to compare against; the single-source specification fixed that by pinning both paths to `lib/encounter_meta_spec.py`. | parse |
| lint/encounter-meta-spec-not-restated | The block's template has exactly one home: no file outside the spec section writes its placeholder form (`> **Party:** <…>`), so a fourth independent restatement of the field list cannot grow back. the fight procedure cites the section (`build-session/combat.md` — "The block's shape is specified once, and not here") instead of carrying its own copy. | parse |
| lint/render-directives-match-grammar | The directive set (`build-session/render.md` — "Directives: `> [!read-aloud]`, `> [!dm-sidebar]`, `> [!encounter-meta]`") matches the parser's grammar and the directives used in the format file (`build-session/session-page-format.md` — "Renderer directives") | parse |
| lint/render-tokens-match-conventions | The token set (`build-session/render.md` — "Reference tokens: `{monster:Name}`, `{item:Name}`, `{spell:Name}`") matches the tokens the format file's conventions require (`build-session/session-page-format.md` — "`{monster:Name}` (the renderer's token; see [render.md](render.md) for the full token set)") | parse |
| lint/opened-reference-files-exist | Every reference file a SKILL.md tells a step to "open" exists beside it | parse |
| lint/dependency-clusters-declared | Every cross-skill reference in the shipped tree is declared, and the README's install commands match. The master declaration is the dependency-cluster table in `docs/campaign-contract.md` — "the skill text tells the reader to open a sibling's file by relative path" — which types each edge as a load, a delegate or a citation. Three assertions over it: an `../<other-skill>/` path anywhere under `skills/` must appear in the table typed as a load or a citation (a **delegate** edge touches no files, so a path on one is a mis-typing); a declared load must still have a path in the tree, or the declaration has gone stale; and for every skill with a hard dependency — none, since the generator merge left every declared edge degrading — the README must carry an install command listing that skill plus the transitive closure of its hard dependencies (the assertion stays armed and bites again the day a hard edge returns). Deliberately dumb: it pins the *presence* of an edge, never the load/delegate/citation judgement or the hard/degrades column, both of which are prose | parse |
| lint/wiki-scaffold-starts-green | A fresh copy of the shipped wiki scaffold comes up clean. The setup skill's bootstrap phase closes only when the freshly generated catalog passes conformance with **zero errors and zero warnings** (`setup/SKILL.md` — "zero errors, zero warnings"), and it hands the DM a template it copies verbatim (`setup/SKILL.md` — "Every file ships as-is"). So the committed template is copied to a scratch directory, indexed with `wiki-index.py`, then checked with `wiki-check.py --warnings`; both must exit clean. A template edit that lands a page the schema rejects fails here, on the maintainer side, instead of on a consumer's first run — the one promise the bootstrap phase cannot keep by asking. | parse (the shipped scripts, run over a scratch copy) |
| lint/wiki-scaffold-preflight-covers-template | The bootstrap refuses to write over an existing wiki (`setup/SKILL.md` — "The scaffold lands only on clean ground") by naming the top-level paths it would land and stopping if any exists. Every top-level entry the committed template actually ships must appear in that list, or the copy step would clobber an unnamed path the preflight promised to guard. One-directional on purpose: `index.md` is named without shipping, because the first `wiki-index.py` run generates it — so the assertion is *shipped ⊆ named*, never the reverse. | parse |

The encounter-meta, render-directive and render-token lints are the sync
obligations `docs/campaign-contract.md` already declares; they are mechanically
checkable rather than trusted to a commit-message convention. The two
encounter-meta lints run today, in `lib/encounter_meta_spec.py`.

---

## Unenforceable as written

Surfacing these is a first-class output of this sweep. **None are fixed here** —
each is a promise the skill text makes that no assertion can carry in its current
wording. Some are cheap wording fixes; some are real design questions.

| Slug | The promise | Why it can't be checked |
|---|---|---|
| **unenforceable/npc-roster-column-contradiction** | Key NPCs roster columns | `build-session/SKILL.md` — "the roster table in the format's shape" names **four** columns; `build-session/session-page-format.md` — "**Key NPCs** — one table, one row per NPC or creature likely to appear" names **five**, adding Personality. A regex can enforce either, not both — the library contradicts itself. |
| **unenforceable/set-piece-undefined** | "For a **set-piece** fight, take two complications" (`build-session/combat.md` — "for a set-piece fight, take **two, from different menu sections**") | "Set-piece" is never defined mechanically, so the two-complication rule has no testable trigger. (`build-session/dungeon.md` — "one High set piece guarding the objective or its exit" ties it to the High-difficulty guard fight — that *is* testable, but only there.) |
| **unenforceable/cr-zero-sparingly** | "CR 0 sparingly" (`build-session/xp-budget.md` — "**CR 0 sparingly.** Worth-0-XP critters add bodies but no budget") | No threshold. |
| **unenforceable/candidate-slate-oversupply** | "Roughly twice as many candidates as the gap needs" (`seed-clues/SKILL.md` — "Draft roughly twice as many candidates as the gap needs") | "Roughly" admits no bound. |
| **unenforceable/discovery-mechanisms-diverse** | "Discovery mechanisms are diverse" (`seed-clues/SKILL.md` — "**Should:** discovery mechanisms are diverse") | A **Should**, and "diverse" has no metric — though the five mechanisms are enumerable (`seed-clues/SKILL.md` — "how it is discovered (conversation, physical trace, observation, proactive)"), so a distinct-count rule would be a small wording change. |
| **unenforceable/node-is-durable-situation** | "More material than one session consumes" (`build-session/node-deepening.md` — "more material than one session consumes") | No metric for session consumption. |
| **unenforceable/art-styles-vary-widely** | Art styles "must vary widely between sessions" (`build-session/session-page-format.md` — "styles must **vary widely between sessions**") | Inequality against the neighbors' `art_style:` keys is checkable; "widely — change the medium and register, not just the palette" is judgement. |
| **unenforceable/stat-block-sweep-page-wide** | The stat-block sweep (`build-session/session-page-format.md` — "**Stat-block references.** Every creature named anywhere on the page", "The stat-block sweep is done") | Requires knowing which strings on the page are creature names. The format file admits the difficulty itself: "a missing link is not a broken link, so only a deliberate sweep catches it." Enforceable only against a closed fixture roster, never in general. |
| **unenforceable/prompt-composes-eight-parts** | The eight-part prompt structure (`campaign-art/SKILL.md` — "Compose the prompt from these labelled parts") | Deliberately unparseable — "write them as flowing sentences, not literally as a form." |
| **unenforceable/fight-mix-avoidable-or-negotiable** | "At least one avoidable or negotiable" fight (`build-session/dungeon.md` — "at least one avoidable or negotiable") | The encounter-meta block has no field to carry it, so nothing records the claim. |
| **unenforceable/complication-field-missing** | "An encounter without a complication is not finished" (`build-session/combat.md` — "An encounter without a complication is not finished") | The encounter-meta block has **no complication field**. The filing block says the complication usually lives in `Objective:` (`build-session/session-page-format.md` — "the complication usually lives here") — "usually" is not a parse target. The library's single mandatory rule for the fight procedure is the one its filing format can't express. |
| **unenforceable/done-when-not-library-wide** | "Done when:" as a per-step closer | `seed-clues`, `catch-up`, and `build-session`'s SKILL.md (including `node-deepening.md`) state one per step. `combat.md`, `dungeon.md`, `spotlight.md`, `party-sync`, and `campaign-art` do not — they close steps in prose. A cross-library lint for "every step has a Done when" would fail most of the roster; it is a convention of three flows, not of the library. |

## What this exposes about the harness

Two shapes fall out of the sweep, and they are not equally priced:

1. **The static lints** need no model at all. They catch real, already-filed
   defects and cost nothing to run on every commit.
2. **Parse/graph assertions** need real output from a real run — the expensive
   tier. In practice every one of them runs against a hand-authored fixture
   today. the fight procedure's XP arithmetic, the keyed-site procedure's xandering floor,
   and seed-clues' clue-web musts are the densest, most valuable cases here.

**Judgement rows are a minority.** The doctrine that
matters most at the table (is the clue interpretable, is the prose plain, is the
NPC named rather than described) is exactly the part that stays judgement.
