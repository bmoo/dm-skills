# Golden corpus — `dungeon-generator/lead-interpretability`

A labeled corpus for **`dungeon-generator/lead-interpretability`** — *"every
planted lead is interpretable using only what the players will already know on
finding it; a lead that requires unseen content to mean anything is a defect, not
foreshadowing."* (See the row in
[`../../judgement-rubric.md`](../../judgement-rubric.md), source: the Step 7
"Leads planted" delivery bullet.)

## Purpose — pin the boundary by example

`lead-interpretability` is a **reader-interpretation** judgement: *can the party,
at the moment they find a lead, read it with only what they already know?* The
same criteria words ("interpretable", "already know", "unseen content") drift
from output to output, so hand-written anchors alone leave the boundary soft.
This corpus pins it **by example** — a set of planted-lead instances labeled with
the verdict a correct checker must return, spanning clear passes, clear fails,
and the genuine edges the criteria exist to adjudicate. It is the labeled
boundary `lead-interpretability`'s anchors point at.

## What each instance is

Every instance is **self-contained** — it carries exactly what the
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
would see for this one lead, and nothing else:

1. **The planted lead** — the clue text as it sits at its key in the dungeon.
2. **What the players already know** — the minimal campaign-knowledge context
   needed to judge the lead: the nodes visited, NPCs met, symbols/names already
   seen. This is the "what the players already know on finding it" the row is
   graded against. (It is *not* the party roster — `lead-interpretability` does
   not read the roster; see the rubric row's *Roster use*.)

Nothing else travels with an instance — no generator reasoning, no fix, no hint at
the expected verdict inside the instance file. The label lives only in the
[verdict map](verdict-map.md).

## Labels

Each instance is labeled with the verdict a correct checker returns:

- **pass** → `approve` — the lead is interpretable with only the stated prior
  knowledge.
- **fail** → `disapprove` — the lead requires **unseen content** to mean anything
  (the `lead-interpretability` defect).
- **edge** → the borderline the criteria must adjudicate; its expected verdict is
  stated explicitly in the verdict map (an edge is not a third label — it resolves
  to `approve` or `disapprove`, and the map says which, so the boundary is pinned
  rather than left to a shrug).

## The verdict map

[`verdict-map.md`](verdict-map.md) is the manifest: each instance file → its label
→ its expected verdict → a one-line rationale. A future harness runs the checker
over each instance and asserts its verdict matches the map.

## Out of scope — the validation harness

**This corpus is data only.** The harness that runs the checker over these
instances and asserts each verdict matches the map is **out of scope here** — it
is edit-time work for the evaluation harness, not built or run at the table.
This corpus contains the labeled instances and the verdict map; it adds no pytest and no validation
harness for them.

## Layout

```
lead-interpretability/
├── README.md                     ← this file
├── verdict-map.md                ← instance → label → expected verdict → rationale
└── instances/
    ├── pass-known-npc-manifest.md
    ├── pass-seen-sigil-doorward.md
    ├── pass-plain-directional-scratch.md
    ├── fail-unvisited-cant-key-cipher.md
    ├── fail-unmet-npc-reference.md
    ├── fail-forward-defined-mint-mark.md
    ├── edge-incidental-earlier-mark.md
    ├── edge-common-knowledge-assumed.md
    └── edge-partial-cipher-half-key.md
```
