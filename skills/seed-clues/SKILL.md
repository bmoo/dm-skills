---
name: seed-clues
description: Seed clues toward an under-clued target — a revelation short on evidence, or a node/route short on leads. Use when the DM asks how the players learn or reach something, says a revelation or node needs more clues, or when another skill or an audit flags a coverage gap. Not for deciding what the revelation itself is (that is plot authoring), and a passing mention that something is under-clued is not a trigger.
---

# Seed Clues

The Three Clue Rule: any conclusion the players must reach needs at least three independent clues, and any place they must go needs the same in leads. This skill closes a named coverage gap. Two branches share the steps below: **evidence** (the target is a revelation) and **leads** (the target is a node or route).

Before anything, read the campaign repo's own guide to its structure (`CLAUDE.md` or equivalent, and any planning-method handbook it points to). Clue-web layout, checklist format, link style, and log conventions are owned by those docs; this skill enumerates *what* must be touched, the docs say *how*. Where the docs don't resolve a convention this skill needs, ask the DM inline and offer to record the answer in the campaign's own docs so the next run discovers it.

**Every candidate clue must be TRUE — the method bans red herrings.**

**Authorship:** every clue is a canon assertion — the skill proposes, the DM decides. Drafting a candidate means drafting canon for the DM's veto.

## Steps

### 1. Frame the target
Classify the branch, then read the canon around the target: the revelation's checklist entry and every page its clues touch, or the node and every lead currently pointing at it. State the gap precisely — is it count, gating (everything costs a roll), concreteness (clues parked on unbuilt nodes), or route coverage?
**Done when:** existing coverage is enumerated with each clue's source node, gating, and built/unbuilt status.

### 2. Slate
Draft roughly twice as many candidates as the gap needs. Derive before inventing: mine existing pages for implied-but-unkeyed clues first, and tag each candidate **derived** (follows from written canon) or **new canon** (a fresh assertion), so the DM can wave derived ones through and spend attention on the new. Each candidate is one paragraph: **what the players perceive** (the clue in concrete, presentable form — the words, the image, the object, the trace; at the table the DM presents and the players interpret, so a conclusion with no perceivable carrier is not a candidate), **what it points at** (the takeaway a player could act on), its source node (an unbuilt source says so on its face), how it is discovered (conversation, physical trace, observation, proactive), and its cost (ungated, check, favor). Include at least one **proactive** candidate — a clue that comes to the players: a timeline event, a visitor, a message. Present the slate in prose with a recommended set that already passes step 5's standard.

**Delivery-timing tag (leads branch).** The **forward/exit lead** a run mints — the progression edge *out* of the cluster, the one the exit check in step 5 tracks — carries a **delivery-timing tag** so the dosing survives from clue-authoring into session prep. Only that lead is tagged, and only if the run mints one (a run closing purely lateral coverage mints none). Two values, worded so a downstream prep skill reads them verbatim:
- a plain forward/exit lead → **surfaces late in node**
- a lead into a thread deliberately gated behind later content → **latest & flattest — offhand, once, no chaseable trail**

The tag meters *when and how loudly* the lead lands, never *whether* the thread may be seeded — this is delivery timing + intensity, not target selection, so seeding a deferred thread stays fine. Lateral leads need no tag.
**Done when:** the slate is in front of the DM with a passing recommended set.

### 3. Decide
The DM picks, edits, rejects, or defers. Picked → place. Rejected → discard; write nothing. Deferred → also write nothing: the gap's existing shortfall flag (add one if missing) is the only durable trace, and a future run regenerates a fresh slate from then-current canon. Never park unpicked candidates in the campaign record — proposals are regenerable views, not documents.
**Done when:** every candidate is picked, rejected, or the run ends with the flag as sole residue.

### 4. Place
For each picked clue, the content lands in its source node's body under its own heading. Then the fork: **evidence** — add the checklist row anchored to that heading; **leads** — index the lead in the source node's clue-web section and mirror the target end per the repo's conventions. A forward/exit lead carries its **delivery-timing tag** (step 2) into that clue-web entry, so session prep inherits the dosing rather than re-deriving it. A placement on an unbuilt node is an IOU: mark it with the repo's to-be-keyed convention so the node's eventual build honors it.
**Done when:** every picked clue exists at both of its ends.

### 5. Check
Verify the *placed set*, not the slate:
- **Must:** sources sit on different nodes.
- **Must:** at least one clue is ungated — no check, no cost, no favor.
- **Must:** at least two are concrete-now, on built nodes (IOUs are taxed: design-coverage is not table-coverage).
- **Should:** discovery mechanisms are diverse.
- **Must:** every clue is interpretable using only what the players already know at the moment of discovery — a clue may gain meaning later, but must never require unseen content to mean anything at all.
- **Must:** every placed clue kept a player-reachable vehicle — a concrete scene, action, check, or bargain at the table yields it. A fact stated in DM-facing text with no way for the players to obtain it is not a placed clue.
- For a target that must land across a multi-branch stretch: sources spread across the branches, not stacked on one.

Then the **exit check**: map the cluster this run touched (the repo's node-map skill draws exactly this, if installed) and confirm the loop is not closed — at least one progression edge leads *out*: an outbound lead to a node beyond the cluster, or a named, triggered proactive event that will come to the players. A cluster whose only exit is a single proactive trigger is fragile — one exit is a plan with no backups; report it. Any failed must: propose a swap, never silently place a fragile set.
**Done when:** every must passes, or the DM has accepted the shortfall and it carries an honest flag.

### 6. Bookkeep
Complete every item, or mark it N/A with the reason:
- [ ] Checklist entry updated — clue count, anchors, and shortfall flag added, revised, or removed truthfully
- [ ] Both ends of every placed lead present
- [ ] A clue pointing at an undecided mystery is recorded in the repo's open-questions tracking, per its convention
- [ ] Operation log entry written

If the repo's docs name an obligation this list lacks, do it and flag the gap so this list can be fixed. Re-walk the boxes against the actual files, not from memory.
**Done when:** every box checked or N/A-with-reason.
