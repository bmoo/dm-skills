---
name: review-rewards
description: >-
  Run the DM's magic-item reward review: assemble a character-aware candidate
  slate from official 2024-generation sources, serve it as a private localhost
  review page, and when the DM says the review is done, ingest the saved
  decisions into the Approved Reward Pool that session-building skills
  consume. Use when the DM wants to review, vet, or refresh magic-item
  rewards or the approved-items list, or to revisit deferred or removed
  rewards.
---

# Review Rewards — candidate slate → DM review → Approved Reward Pool

A two-turn workflow. This turn: gather the campaign's state, research a
candidate slate, and serve it on a localhost review page. The DM reviews at
their own pace — every decision saves continuously — then tells you the
review is done. That message is the second turn's trigger **and its
authorization**: ingest the saved decisions, rewrite the Approved Reward
Pool, report what changed, and stop the server, with no second confirmation
round.

The vocabulary, used exactly:

- **Approved Reward Pool** — the narrow consumer contract other skills read.
  An item in it may be placed silently during prep; everything else needs the
  DM's yes.
- **Eligible Reward** — current-level appropriate, exciting and meaningful
  for at least one active PC or the whole party, nonredundant with existing
  gear, and compatible with every Protected Challenge.
- **Protected Challenge** — a prepared, still-unfinished challenge whose core
  mechanic rewards must not cancel. Read them from the campaign's current
  prep each run; the list is never hardcoded.
- **Awarded Item / Deferred Reward / Removed Reward** — history shown
  read-only for loot parity; a good item postponed under an optional
  condition; an item expired or rejected out of ordinary future reviews
  until the DM restores it from the **graveyard**.

Where things live is the campaign repo's call — read its guide (`CLAUDE.md`
or equivalent) for the Approved Reward Pool's location and for where reward
review state is kept. If the guide doesn't say, ask the DM and offer to
record the answers. Review state defaults to a `rewards-review/` directory at
the campaign root: `review-data.json` and `decisions.json`, committed to the
repo (so both agents and every machine share decisions) but **outside the
wiki/site bundle** — full official rules text and campaign-sensitive
recommendations are for local DM review only and are never published.

## Step 1 — Gather

Read, in the campaign's own record: the campaign level (the record is
authoritative for level), the active roster with classes and subclasses,
live character sheets through whatever character tool the environment offers
(the sheet is authoritative for recorded equipment and build choices),
player records, existing equipment and attuned items, Artificer replication
choices, Awarded Items and recent item receipts, the current Approved Reward
Pool, the previous review state if any, and every prepared near-term
challenge — those become this run's Protected Challenges, with their core
mechanics named.

A field no source can answer is a **named gap**: report exactly what could
not be sourced and go on without inventing it. A PC whose subclass is
unknown is reviewed as their class at the current level — recommend broadly
useful class items spanning that class's distinct play styles, and invent no
subclass features.

Done when every input above is either in hand or a named gap.

## Step 2 — Research the slate

Source items through the lookup chain in
[`rules-sourcing.md`](rules-sourcing.md), searching **every official source
the environment's content tools carry from the 2024 rules generation
forward** — the whole eligible catalog, not just famous core items. 2014-era
versions, third-party content, and homebrew are outside the catalog.

- **Depth**: five new candidates per active PC and five whole-party
  candidates, unless the invocation asked for a different depth — accept
  natural-language overrides. The count is a target under a **quality
  floor**: fewer results are correct whenever another item would be filler.
- **Every candidate clears the Eligible Reward bar.** Aim each at one active
  PC or the whole party. When an item fits several targets, pick one primary
  target and mention the secondary fit in its rationale.
- **Redundancy**: exclude exact redundancies — items already owned or
  replicable by a party Artificer. Keep useful partial overlaps and name the
  overlap in the entry's gear relation so the DM can judge the difference.
- **Protected Challenges**: strong situational advantages are welcome —
  magic items should reward clever play. Exclude an item whose possession or
  routine activation cancels a Protected Challenge's core mechanic, and note
  any lesser interaction on the entry.
- **Graveyard**: previously Removed Rewards stay out of candidate research;
  they re-enter only through the page's restore control. A Deferred Reward
  re-enters as a candidate when its condition has been met.

Done when each target's slate is at depth or honestly short of it.

## Step 3 — Write the catalog

Write `review-data.json` per [`state-format.md`](state-format.md): campaign
framing plus one entry per item across all four origins — existing pool
items (they re-earn eligibility each review), new candidates, Awarded Items
read-only, and the graveyard. Preserve the authoritative name, source,
rarity, attunement, and the **full official rules text verbatim** on every
entry, and give every reviewable entry its target and one concise
campaign-fit sentence. Stamp a fresh `catalogVersion` and fold the previous
review's decisions forward as `state-format.md` directs.

## Step 4 — Serve and pause

```bash
python <skill>/scripts/review_server.py \
  --data <review-dir>/review-data.json --state <review-dir>/decisions.json
```

The app is bound to loopback and writes only the designated decision-state
file. Give the DM the printed URL and stop the turn: the review is theirs.
Resume only when the DM says the review is done.

## Step 5 — Ingest on "done"

The DM's done-message authorizes ingestion — run it in this same session
without asking again:

```bash
python <skill>/scripts/ingest.py \
  --data <review-dir>/review-data.json --state <review-dir>/decisions.json \
  --pool-out <the campaign's Approved Reward Pool path>
```

Ingest validates before it writes; if it refuses (malformed or stale state,
unknown decisions, ambiguous identities), relay its errors, leave the pool
untouched, and leave the server up for the DM to correct the review. On
success the pool now contains exactly the approved and retained items in
consumer shape — name, rarity, attunement, target, one fit note, under the
proposal standard, reviewed level, and Protected Challenges considered.
Deferrals, removals, notes, and full rules text stay in the review state;
awarded history stays in the session and player records.

Then: relay the printed change report (additions, retained, removals,
deferrals), stop the localhost server, and commit the review state and pool
the way the campaign's guide says changes land. If frontmatter or similar
page furniture is required by the campaign's wiki schema, add it above the
generated pool body without altering the body.
