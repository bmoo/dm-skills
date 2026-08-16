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

## Checks

A check earns a place in this repo only if it verifies shipped content or a
consumer's repo. Checks over this repo's own maintenance documents do not get
written.

The mechanical checker and its fixtures are build-session's runtime
specification. Add a mechanical rule by writing the check and its passing and
failing fixture; subjective bars stay as completion criteria in the skill text
and a one-round fresh check grades them.

Run `pytest checks/ skills/build-session/scripts/` for the content gate.

### When a commit reverses something the library asserts

A reversal — not a reword — is rarely confined to one file. `docs/campaign-contract.md`'s
*"Must move in the same commit"* table records where each coupled shape is
restated; read it and sweep the tree for the sentence you just falsified, so the
change lands everywhere at once rather than in the one file you were editing.
Nothing enforces this mechanically.
