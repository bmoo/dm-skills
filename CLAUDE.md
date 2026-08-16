# dm-skills — working notes

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
`build-session/scripts/mechanical_checker/checker.py` + its fixtures — the chain is
**inventory → `checker.py` only**. (Subjective bars are no longer derived
artifacts: since the verification-chain cut they live as completion criteria
in each skill's own text, graded by a one-round fresh check, so editing one
is a skill-text edit plus its inventory row.)

So when a skill edit **adds, changes, or removes a checkable promise**
(an arithmetic/count/format rule, a graph property, or a subjective quality
bar like "interpretable" / "no undefined coinage"), update the chain in order:

1. **the inventory row first** (master), then
2. `checker.py` + a fixture, where the promise is mechanical.

The checker now lives inside the skill that runs it. Run
`pytest checks/ skills/build-session/scripts/` to exercise the fixture you just
added along with checks over shipped content.

Never hand-edit the checker out of sync with the inventory. A *new* promise
added to a skill is invisible until its inventory row and, where applicable,
checker support are added, so this rule is the guard against that drift.

### When a commit reverses something the library asserts

A reversal — not a reword — is rarely confined to one file. `docs/campaign-contract.md`'s
*"Must move in the same commit"* table records where each coupled shape is
restated; read it and sweep the tree for the sentence you just falsified, so the
change lands everywhere at once rather than in the one file you were editing.
Nothing enforces this mechanically.
