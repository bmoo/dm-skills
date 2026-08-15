# `dungeon-generator/lead-interpretability` corpus — verdict map

The manifest for the [`dungeon-generator/lead-interpretability` corpus](README.md). Each
row maps one instance file → its **label** → the **expected verdict** a correct
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md) must
return when handed that instance against the **lead-interpretability** rubric row → a
one-line rationale. A future evaluation harness (out of scope here) runs the checker over each instance
and asserts the returned verdict equals the **Expected verdict** column.

Labels: **pass** = interpretable now (`approve`); **fail** = requires unseen
content (`disapprove`); **edge** = the borderline the criteria adjudicate — it
still resolves to `approve` or `disapprove`, stated explicitly below so the
boundary is pinned, not shrugged.

| Instance | Label | Expected verdict | Why |
|---|---|---|---|
| [`instances/pass-known-npc-manifest.md`](instances/pass-known-npc-manifest.md) | pass | **approve** | The manifest names **Old Harl** (met two nodes ago) and the **Salt Docks** (a known district) — reads now as a direction the party can act on. |
| [`instances/pass-seen-sigil-doorward.md`](instances/pass-seen-sigil-doorward.md) | pass | **approve** | The **three-rings-and-a-star** mark is the party's whole investigation, named aloud all delve; the arrow points at a visible shaft. Fully legible now. |
| [`instances/pass-plain-directional-scratch.md`](instances/pass-plain-directional-scratch.md) | pass | **approve** | Leans on **only in-dungeon** knowledge — a cell block already explored, a prisoner to go ask about. No earlier-node dependency at all; anchors the floor of the pass class. |
| [`instances/fail-unvisited-cant-key-cipher.md`](instances/fail-unvisited-cant-key-cipher.md) | fail | **disapprove** | The cipher is unreadable until the **cant-key** from an **unvisited** grove node is in hand — noise at the moment of finding. The `lead-interpretability` defect verbatim. |
| [`instances/fail-unmet-npc-reference.md`](instances/fail-unmet-npc-reference.md) | fail | **disapprove** | "Go to **Marisel**" points at a person the party has never met, heard of, or placed — first introduced in an unreached node. Turns entirely on unseen content. |
| [`instances/fail-forward-defined-mint-mark.md`](instances/fail-forward-defined-mint-mark.md) | fail | **disapprove** | The **broken-crown** mark's meaning is first defined **deeper in the same delve**, unreached — a forward reference. An unremarkable coin at the moment of finding. |
| [`instances/edge-incidental-earlier-mark.md`](instances/edge-incidental-earlier-mark.md) | edge | **disapprove** | The mark **was** seen earlier (not a forward reference) but only as **unremarked scenery**; the package never made it salient, so the party could not reliably connect it. `lead-interpretability`'s cannot-tell branch → disapprove. |
| [`instances/edge-common-knowledge-assumed.md`](instances/edge-common-knowledge-assumed.md) | edge | **approve** | The **Twin Sisters** were never introduced on-screen, but the campaign established them as **common regional knowledge** the party plausibly holds — "what the players already know" includes grounded common knowledge, so it reads as a directional clue. |
| [`instances/edge-partial-cipher-half-key.md`](instances/edge-partial-cipher-half-key.md) | edge | **approve** | One glyph the party **already decoded** delivers a real, actionable meaning now (the Broker ties every tracked shipment); the opaque remaining glyphs are not this lead's payload. Interpretable on known content. |

## The boundary the edges pin

The three edges bracket `lead-interpretability`'s hard case — **prior exposure that is
not clean prior knowledge**:

- **`edge-incidental-earlier-mark` → disapprove.** Seeing a symbol earlier is not
  the same as *knowing* it: an unremarked glimpse the package never made salient
  does not count as knowledge the party "already has", and where the package leaves
  that unsettled the checker disapproves.
- **`edge-common-knowledge-assumed` → approve.** Knowledge the party never acquired
  on-screen **can** still count — when the campaign has grounded it as common
  regional knowledge a local would hold. The line is *grounded* common knowledge,
  not any convenient assumption.
- **`edge-partial-cipher-half-key` → approve.** A lead whose **actionable meaning**
  rides on content the party already holds is interpretable now, even if adjacent
  content stays opaque — the opaque remainder is not this lead's payload.

Together they say: interpretability is judged on **what the party can actually read
now** — salient prior knowledge and grounded common knowledge count; unremarked
scenery and forward-defined content do not.
