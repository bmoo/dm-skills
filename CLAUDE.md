# dnd-skills — working notes

## Transient visual output → Artifacts

For **transient, throwaway visual output** — explainers (e.g. the `/teach` skill),
`/prototype` output, sketches, and other ephemeral learning/prototyping aids — use
the **Artifact tool** rather than local files or a dev server. The owner works from
an iPad over mosh/Blink, so a hosted `claude.ai` URL that opens in Safari is the
right delivery mechanism for something meant to be glanced at, not kept.

This is about *disposable* diagrams. Durable, versioned deliverables that belong to
the repo (committed docs, skill assets, etc.) are a separate concern — don't route
those through artifacts just because they're visual.

- Redeploy to the **same file path** to keep the same URL when iterating.
- Prefer native Mermaid (```mermaid fences / `<pre class="mermaid">`) for
  flowcharts, state machines, sequence/ER diagrams; hand-built SVG/HTML+CSS for
  anything Mermaid can't express.
- Keep artifacts self-contained (CSP blocks external CDNs) and theme-aware
  (light/dark) so they read well on the iPad in either theme.

## The verifier is derived — keep it in sync when you edit a skill

`docs/eval-assertion-inventory.md` is the **master** list of every checkable
promise the skills make. The runtime verifier derived from it is
`lib/mechanical-checker/checker.py` + its fixtures — the chain is
**inventory → `checker.py` only**. (Subjective bars are no longer derived
artifacts: since the verification-chain cut they live as completion criteria
in each skill's own text, graded by a one-round fresh check, so editing one
is a skill-text edit plus its inventory row.)

So when a skill edit **adds, changes, or removes a checkable promise**
(an arithmetic/count/format rule, a graph property, or a subjective quality
bar like "interpretable" / "no undefined coinage"), update the chain in order:

1. **the inventory row first** (master), then
2. `checker.py` + a fixture, where the promise is mechanical.

Never hand-edit the checker out of sync with the inventory. The anchor
check below covers one half of the drift mechanically — reword a passage a row
cites and `pytest lib/` fails — but a *new* promise added to a skill is invisible
to it, so until the maintainer-side additive sweep ships this rule is the
only guard against that half.

### Cite an anchor phrase, never a line number

Every citation in that chain — inventory row, `checker.py` docstring —
names a **file plus a phrase that appears verbatim in it**:

```
(`combat-generator/SKILL.md` — "each creature × count with looked-up XP")
(`combat-generator/xp-budget.md` — "three distinct stat blocks", "CR 0 sparingly")
(`build-session/SKILL.md` — "the DM's yes"; `spotlight/doctrine.md` — "flagged ability")
```

A bare filename (plain `SKILL.md`, or `xp-budget.md`) means the file of the
skill the context belongs to: the inventory section it sits under.
Anywhere with no owning skill (`checker.py`, the inventory's lint and
unenforceable sections, the library prose) spells the skill out. Anything with a
`/` is written relative to `skills/`.

Line numbers rotted on every edit and nothing read them, so nobody noticed
in the anchor-migration work. `lib/citation_anchors.py` now enforces the replacement, and **`pytest
lib/` is the gate** — no hook to install. It asserts three things: every anchor
phrase is still in the file it names, no filename-plus-line-number citation has
crept back anywhere, and no citation half-parses. `python lib/citation_anchors.py` prints
the same report directly. When a phrase you cite gets reworded in the skill
text, re-pick the anchor rather than loosening the check.

### Retiring a claim the library used to make

The mirror of the anchor check, and the same `pytest lib/` gate:
`lib/retired_phrases.py` holds a denylist of sentences the library **used to**
assert, grepped over every tracked file. `d1a08f9` changed a fact in one skill
and left six other locations asserting the old one; `docs/campaign-contract.md`'s
*"Must move in the same commit"* table is the manual mechanism that didn't catch
it, because reading it is a step a human has to remember.

So when a commit **reverses** something the library asserts — not a reword, a
reversal — add the sentence it falsified to `RETIRED`, naming the retiring commit
beside it. Two rules, both enforced by tests: the phrase must be gone from the
whole tree when you add it (that failure is how you find the copy you missed),
and it must be quotable from the removed side of the commit you name. See
`lib/retired_phrases.py` for the longer version and
`docs/campaign-contract.md` for where the obligation sits.
