# `build-session/spotlight-coverage` corpus — verdict map

The manifest for the [`build-session/spotlight-coverage` corpus](README.md). Each row
maps one instance file → its **label** → the **expected verdict** a correct
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md) must
return when handed that instance against the **spotlight-coverage** rubric row → a
one-line rationale. A future evaluation harness (out of scope here) runs the checker over each instance
and asserts the returned verdict equals the **Expected verdict** column.

`spotlight-coverage` is the library's **legal-absence** row: the deterministic pre-pass
computes the uncovered set, but an uncovered PC is legal — *"absence is the record: a PC
named nowhere on the page was planned as resting"* (`session-page-format.md` —
"a PC named nowhere on the page was planned as resting").
So every instance carries the **pre-pass output** (uncovered set + per-PC beat share)
and the checker rules on one question only: **is each absence a defensible rest, or a
dropped beat?** Labels: **pass** = the absence is defensible, or there is none
(`approve`); **fail** = an absence reads as a dropped beat (`disapprove`), and the
**Signal** column names which break signal fired; **edge** = the borderline the criteria
adjudicate — it still resolves to `approve` or `disapprove`, stated explicitly below so
the boundary is pinned, not shrugged.

| Instance | Label | Signal at issue | Expected verdict | Why |
|---|---|---|---|---|
| [`instances/pass-full-coverage.md`](instances/pass-full-coverage.md) | pass | none — uncovered set empty | **approve** | Four PCs, four beats, uncovered `[]`. `spotlight-coverage` has nothing to rule on; the row holds without any defensibility judgement at all. The floor of the pass class. |
| [`instances/pass-defensible-rest-no-carrier.md`](instances/pass-defensible-rest-no-carrier.md) | pass | obvious carrier — none exists | **approve** | Nyla uncovered, but the page is a secular customs house: no undead, no consecrated ground, no rite, nothing her Channel Divinity answers. Beats evenly spread (1/1/1). The page's own content supports the rest. |
| [`instances/pass-two-rests-short-session.md`](instances/pass-two-rests-short-session.md) | pass | obvious carrier — none exists | **approve** | **Two** PCs uncovered still holds: one social set-piece is the whole night, staging no fight, climb, or rite. Doctrine's *"no single situation must aim at anyone"* is the baseline, and a one-scene page cannot carry four beats. The ceiling of the pass class. |
| [`instances/fail-obvious-carrier-aimed-elsewhere.md`](instances/fail-obvious-carrier-aimed-elsewhere.md) | fail | **obvious carrier** + **hoarding** | **disapprove** | The desecrated shrine — restless dead, fouled ground, a widow asking — is annotated for **Vex**, while Nyla (Channel Divinity) is named nowhere and Vex holds 3 of 5 beats. Both break signals at once. |
| [`instances/fail-hoarded-beats.md`](instances/fail-hoarded-beats.md) | fail | **hoarding** | **disapprove** | Isolates hoarding: no single scene is unmistakably Sera's or Nyla's, but a five-beat page spent **four on one PC** and left two silent. That share is attention running out, not a budgeted rest. |
| [`instances/fail-uncovered-pc-is-the-only-key.md`](instances/fail-uncovered-pc-is-the-only-key.md) | fail | **obvious carrier** | **disapprove** | Isolates the carrier signal: beats are evenly spread (no hoarding), yet the page's spine — a ward the page itself says "answers only to a counterspell" — is annotated for **Bram**, whose Grapple cannot touch it, while **Sera** is named nowhere. |
| [`instances/edge-unstaged-funeral.md`](instances/edge-unstaged-funeral.md) | edge | **obvious carrier** (borderline) | **approve** | The funeral is subject matter a cleric owns, but the page **stages nothing in it** — no action, no check, no NPC asking anything, nothing that goes wrong. A scene that aims at nobody is the plain baseline doctrine protects, not an unused carrier. Nyla's rest holds. |
| [`instances/edge-staged-funeral-rite.md`](instances/edge-staged-funeral-rite.md) | edge | **obvious carrier** (borderline) | **disapprove** | The same funeral, same pre-pass output — but the widow **asks**, the page names a **Channel Divinity** resolution, and failing it carries a consequence two nodes on. A staged action the uncovered PC's flagged ability answers, annotated for no one: an unused obvious carrier. |
| [`instances/edge-secondary-mention-only.md`](instances/edge-secondary-mention-only.md) | edge | the **secondary-mention rule** | **approve** | Bram is named only inside Vex's beat, and that **counts as covered** — doctrine budgets "a beat somewhere, in any pillar", and a scene that reinforces one PC with another has staged both. The checker does **not** override the pre-pass to re-open a covered PC. Naming is the test; primacy is not. |
| [`instances/edge-second-straight-rest.md`](instances/edge-second-straight-rest.md) | edge | **scope** — consecutive rests | **approve** | The page's content supports the rest exactly as in `pass-defensible-rest-no-carrier`; only a recap line hints this is Nyla's second straight rest. **Rest streaks are catch-up's row** (`catch-up/SKILL.md` — "note a PC who has now rested across consecutive sessions"), not `spotlight-coverage`'s — this checker grades one page in fresh context and is handed no prior-session state, so it must not rule on a streak it cannot actually see. |

## The boundaries the edges pin

The four edges bracket `spotlight-coverage`'s three hard cases:

- **`edge-unstaged-funeral` → approve** vs. **`edge-staged-funeral-rite` →
  disapprove** pin the **obvious-carrier** boundary, the row's central judgement. The
  two instances carry the *same scene, same roster, same pre-pass output* and differ
  in one thing: whether the scene **stages a player action** the uncovered PC's
  flagged ability answers. Subject matter alone never makes a carrier — a funeral on
  the page does not owe the cleric a beat. A staged action she is the answer to does.
  (This is deliberately the same shape as `clue-interpretability`'s
  `edge-passive-mural-figure` / `edge-staged-perception-monument` pair: a page owes
  nothing for what it merely *depicts*, and everything for what it *stages*.)
- **`edge-secondary-mention-only` → approve** pins the **secondary-mention** rule
  against the checker's temptation to re-litigate coverage the pre-pass already
  settled. Anything else makes the row disagree with itself run to run — the exact
  drift a corpus exists to stop.
- **`edge-second-straight-rest` → approve** pins the **scope** boundary. A second
  straight rest is a real finding *somewhere*; it is not this checker's, because this
  checker sees one page. Ruling on it here would mean guessing from a recap line —
  and a first rest and a fifth look identical to a fresh-context grader.

## The pass class is wide on purpose

Three of ten instances pass with a **non-empty** uncovered set, one of them with **two**
PCs uncovered. That weighting is deliberate: resting is correct doctrine, and a checker
that reads every absence as a defect would fire on most well-built pages and be waived
into uselessness — the fate one campaign's log records for
`spotlight-plan-not-filed` when it flagged something nobody could act on. The fail class
is reserved for absences the page's **own content** contradicts.

## Distinct from `dungeon-generator/every-flagged-pc-staged`

Dungeon's **every-flagged-pc-staged** is the same set-cover computation and a different
verdict authority. `every-flagged-pc-staged` covers the **flagging** roster inside a
single site and returns a mechanical `Finding` outright, because an unstaged flagged
ability there **is** a defect. `spotlight-coverage` covers the **whole** roster across a
session page and returns nothing on its own, because a PC absent from a session page
was, by the format's own rule, planned as resting. Same extractor (`_spotlight_lines`),
same arithmetic, opposite default — and that difference is why one is mechanical and the
other is judgement.
