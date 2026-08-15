# `build-session/clue-interpretability` corpus — verdict map

The manifest for the [`build-session/clue-interpretability` corpus](README.md). Each row
maps one instance file → its **label** → the **expected verdict** a correct
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md) must
return when handed that instance against the **clue-interpretability** rubric row → a
one-line rationale. A future evaluation harness (out of scope here) runs the checker over each instance
and asserts the returned verdict equals the **Expected verdict** column.

`clue-interpretability` has **two prongs** — a clue must carry a **player-reachable
vehicle** *and* be **interpretable when found**; a failure of *either* breaks the row.
Labels: **pass** = both prongs hold (`approve`); **fail** = one prong breaks
(`disapprove`), and the **Prong** column names which; **edge** = the borderline the
criteria adjudicate — it still resolves to `approve` or `disapprove`, stated explicitly
below so the boundary is pinned, not shrugged.

| Instance | Label | Prong at issue | Expected verdict | Why |
|---|---|---|---|---|
| [`instances/pass-searchable-ledger-known-seal.md`](instances/pass-searchable-ledger-known-seal.md) | pass | both hold | **approve** | A **search** yields the ledger (vehicle); its **three-keys-over-a-wave** seal is Voss's, already met (interpretable). Both prongs clear. |
| [`instances/pass-prisoner-bargain.md`](instances/pass-prisoner-bargain.md) | pass | both hold | **approve** | A **bargain** with the runner yields the clue (vehicle); it names the **Salt Docks** and **Red**, both known (interpretable). |
| [`instances/pass-in-node-check-directional.md`](instances/pass-in-node-check-directional.md) | pass | both hold | **approve** | A **check** on the silt line yields it (vehicle); it leans on **only in-node knowledge** — the barred door already found (interpretable). Floor of the pass class. |
| [`instances/fail-dm-facing-altar-secret.md`](instances/fail-dm-facing-altar-secret.md) | fail | **vehicle** | **disapprove** | The altar-hides-the-key fact sits **only in DM notes** — no scene, search, check, or bargain delivers it. "A fact stated in DM-facing text with no way to obtain it is not a placed clue." The vehicle prong, verbatim. |
| [`instances/fail-sealed-reliquary-no-access.md`](instances/fail-sealed-reliquary-no-access.md) | fail | **vehicle** | **disapprove** | The confession has an in-fiction container but **no reachable way to open it at this node** — the only key is absent and no alternative is placed. No player-reachable vehicle here. |
| [`instances/fail-unseen-choir-glyph.md`](instances/fail-unseen-choir-glyph.md) | fail | **interpretability** | **disapprove** | The mosaic **has a vehicle** (an Investigation check) but resolves only with the **cant-key** from an **unvisited** grove — noise at the moment of finding. The interpretability prong (the `lead-interpretability`-shared branch). |
| [`instances/edge-passive-mural-figure.md`](instances/edge-passive-mural-figure.md) | edge | **vehicle** (borderline) | **disapprove** | The painted-over figure is written as DM narration with **no staged player action** that surfaces it — a passive backdrop, not a reachable vehicle. `clue-interpretability`'s cannot-tell branch on the vehicle prong → disapprove. |
| [`instances/edge-staged-perception-monument.md`](instances/edge-staged-perception-monument.md) | edge | **vehicle** (borderline) | **approve** | Unlike the mural, the page **stages the observation** — a called Perception check at the focal monument *and* an NPC who volunteers it. A concrete vehicle; the crest is already known, so both prongs hold. |
| [`instances/edge-common-regional-symbol.md`](instances/edge-common-regional-symbol.md) | edge | **interpretability** (borderline) | **approve** | The token is in plain reach (vehicle holds); the **Twin Sisters** were never shown on-screen but are **grounded common regional knowledge** — "what the players already know" includes that, so it reads. |

## The boundaries the edges pin

The three edges bracket `clue-interpretability`'s two hard cases — one per prong:

- **`edge-passive-mural-figure` → disapprove** vs. **`edge-staged-perception-monument` →
  approve** pin the **vehicle** boundary: a perceivable detail is not a placed clue
  unless the page gives the players a **concrete action that surfaces it** — a called
  check, an NPC who points at it, a reason to look. DM narration that "a keen eye would
  note" something, with no staged action, is a passive backdrop and fails the vehicle
  prong; the same kind of detail with a staged check or a volunteering NPC passes.
- **`edge-common-regional-symbol` → approve** pins the **interpretability** boundary the
  same way `lead-interpretability` does: knowledge the party never acquired on-screen
  **can** still count when the campaign has grounded it as common regional knowledge a
  local would hold — as against `fail-unseen-choir-glyph`, where the needed key lives in
  unreached content and the clue is noise.

Together they say: a clue must be **got** and then **read** — the vehicle prong asks
whether a player action delivers it; the interpretability prong asks whether, once
delivered, it means something with what the party already holds. Both must clear.

## Distinct from `dungeon-generator/lead-interpretability`

`lead-interpretability` (dungeon) and `clue-interpretability` (node-deepening) share the
*interpretability* prong but are not the same row. **lead-interpretability** grades a
**planted lead inside a dungeon that points at another node** — it assumes the lead is
found and asks only whether it *reads* with prior knowledge. **clue-interpretability**
grades a **clue inside a deepened node** and carries a second prong
`lead-interpretability` has no analog for: whether the clue has a **player-reachable
vehicle** to be got at all. The vehicle-failure instances here
(`fail-dm-facing-altar-secret`, `fail-sealed-reliquary-no-access`, the mural edge) have
**no `lead-interpretability` counterpart** — that is the distinction the two corpora
keep.
