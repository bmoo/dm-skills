# Golden corpus — `build-session/clue-interpretability` (node-deepening)

A labeled corpus for **`build-session/clue-interpretability`** — *"every clue or lead
written into a deepened node must carry a player-reachable vehicle — a concrete scene,
action, check, or bargain that yields it — AND be interpretable using only what the
players already know when they could plausibly find it; a fact stated in DM-facing text
with no way for the players to obtain it is not a placed clue."* (See the row in
[`../../judgement-rubric.md`](../../judgement-rubric.md), source:
`node-deepening.md` — "the clue-web section only indexes it", the Step 3 Draft
rule.)

## Purpose — pin the boundary by example

`clue-interpretability` is a **reader-interpretation** judgement, and it is
**two-pronged**: a clue must be **got** (a player-reachable vehicle) and, once got,
**read** (interpretable with prior knowledge). The same criteria words ("reachable",
"interpretable", "already know") drift from node to node, so hand-written anchors alone
leave the boundary soft. This corpus pins it **by example** — clue instances labeled
with the verdict a correct checker must return, spanning clear passes, clear fails on
**each** prong, and the genuine edges the criteria exist to adjudicate.

## What each instance is

Every instance is **self-contained** — it carries exactly what the
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
would see for this one clue, and nothing else:

1. **The clue** — as it sits in the deepened node (the run note, the DM text, the
   staged scene).
2. **The node context** — the minimal facts needed to judge **both prongs**: what the
   players can *do* at the node to obtain the clue (the vehicle), and what they already
   know when they could plausibly find it (the interpretability context). This is *not*
   the party roster — `clue-interpretability` does not read the roster; see the rubric
   row's *Roster use*.

Nothing else travels with an instance — no generator reasoning, no fix, no hint at the
expected verdict inside the instance file. The label lives only in the
[verdict map](verdict-map.md).

## Labels

Each instance is labeled with the verdict a correct checker returns:

- **pass** → `approve` — both prongs hold: a reachable vehicle **and** interpretable
  with the stated prior knowledge.
- **fail** → `disapprove` — one prong breaks. The verdict map's **Prong** column names
  which: a **vehicle** fail (a DM-facing fact with no obtaining scene, or a clue behind
  an unreachable barrier) or an **interpretability** fail (needs unseen content).
- **edge** → the borderline the criteria must adjudicate; its expected verdict is stated
  explicitly in the verdict map (an edge is not a third label — it resolves to `approve`
  or `disapprove`, and the map says which, so the boundary is pinned rather than left to
  a shrug).

## Both prongs are exercised

By design the fail class spans **both** prongs — `fail-dm-facing-altar-secret` and
`fail-sealed-reliquary-no-access` fail the **vehicle** prong (no
`lead-interpretability` analog), and `fail-unseen-choir-glyph` fails the
**interpretability** prong (the branch `clue-interpretability` shares with
`lead-interpretability`). The edges bracket one boundary per prong. This is what keeps
`clue-interpretability` from collapsing into a second copy of `lead-interpretability`:
if every fail were "needs unseen content," the vehicle prong —
`clue-interpretability`'s distinguishing half — would go untested.

## The verdict map

[`verdict-map.md`](verdict-map.md) is the manifest: each instance file → its label →
the prong at issue → its expected verdict → a one-line rationale. A future harness runs
the checker over each instance and asserts its verdict matches the map.

## Out of scope — the validation harness

**This corpus is data only.** The harness that runs the checker over these instances
and asserts each verdict matches the map is **out of scope here** — it is edit-time work
for the evaluation harness, not
built or run at the table. This corpus contains the labeled instances and
the verdict map; it adds no pytest and no validation harness for them.

## Layout

```
clue-interpretability/
├── README.md                     ← this file
├── verdict-map.md                ← instance → label → prong → expected verdict → rationale
└── instances/
    ├── pass-searchable-ledger-known-seal.md
    ├── pass-prisoner-bargain.md
    ├── pass-in-node-check-directional.md
    ├── fail-dm-facing-altar-secret.md          ← vehicle fail
    ├── fail-sealed-reliquary-no-access.md       ← vehicle fail
    ├── fail-unseen-choir-glyph.md               ← interpretability fail
    ├── edge-passive-mural-figure.md             ← borderline vehicle → disapprove
    ├── edge-staged-perception-monument.md       ← borderline vehicle → approve
    └── edge-common-regional-symbol.md           ← borderline interpretability → approve
```
