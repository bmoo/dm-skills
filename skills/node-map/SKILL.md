---
name: node-map
description: >-
  Render a high-level ASCII node-flow diagram for session prep — the nodes,
  the hub, the branch, and the clue/lead edges between them — for a session,
  a scenario group, an act, or a single node's clue web. Use when the DM
  wants to *see* the shape of upcoming play — a map, flow, node diagram, or
  "how do these connect" view to prep from, or to ask "strike this clue — what
  still reaches?" and get the as-if counterfactual as an Artifact. Read-only.
  The as-built map depicts only what the campaign record already establishes;
  the as-if mode is the one carve-out, and it only ever strikes edges the
  record establishes — it never adds one.
---

# Node Map

Render a compact ASCII node-flow map that lets the DM see the structure of upcoming play at a glance — which node is the hub, where the branch opens, and what clue or lead carries the players along each edge. This is a *prep aid*, not canon: it visualizes the campaign record, it never invents it.

1. **Resolve the scope.** The DM names what to map. Common scopes:
   - *"the first session or two"* / a session → the scenario group(s) that session covers.
   - a **scenario group** → its nodes and the edges between them.
   - an **act** → the act's scenario groups at low resolution, one cluster each.
   - a single **node** → that node's clue web — its leads out and the known clues in.
   If the scope is ambiguous, ask in one line; otherwise pick the obvious reading and say which you chose.

2. **Gather the structure from the campaign record — do not improvise it.** Locate each of these via the campaign repo's structure guide (`CLAUDE.md` or equivalent, and any planning-method handbook it points to), then read:
   - the **macro-outline** page — acts → scenario groups → nodes; the skeleton of any map.
   - the **live status layer** — active threads, scenario timelines, and the revelations checklist (clue coverage and under-seeded warnings).
   - the **clue-web section** of each node page in scope — its glance line gives you the edges; its per-lead entries give you the edge labels.
   - the relevant **session pages** for prepped beats that aren't yet their own node (e.g. a road encounter).

3. **Draw the map** using the visual vocabulary below. Keep it scannable — boxes for nodes, arrows for leads, short edge labels lifted from the clue web. Group a linear stretch visually distinct from a live branch.

4. **Tell the truth about prep state on the map itself.** Mark prepped nodes vs placeholders, undecided objectives, and under-seeded revelations *in the diagram or a short note beneath it*. A gap in prep is information the DM needs — surface it, never paper over it. Do not draw an edge the clue web doesn't support; if a connection is intended but unclued, draw it dashed and flag it. Draw nodes whose mysteries the repo tracks as deliberately open, but mark the undecided pieces rather than guessing them.

5. **Deliver in chat by default.** After the diagram, add a few-line "what this surfaces" read — asymmetric prep, open objectives, thin clue coverage. Then offer to save it into the relevant macro-outline or session page. Only write to a file if the DM says so — durable additions land on a page, but a prep visualization is a one-off until the DM wants it kept.

## Visual vocabulary

Use these consistently so the DM learns to read them at a glance:

```
┌──────────┐        a node (single line)
│  NODE    │
└──────────┘

╔══════════╗        a HUB — the node a branch opens from; mark with ★ HUB
║  NODE ★  ║
╚══════════╝

A ──label──► B      a lead/clue edge: label is the clue, lifted from the Clue Web
A ◄────────► B      a two-way connection (e.g. tunnels that link both directions)
A ····► (note)      a deferred / floating thread — resurfaces later, no fixed edge
╔═ glimpse ═╗       a glimpse or aside on an edge (e.g. a figure seen mid-encounter)
```

Three more belong to the counterfactual mode below, and nothing else uses them:

```
A ──label──▻ B      a NAMING edge — hollow head, because nothing arrives: it
                    establishes B, or a reason to go, and carries no way to get
                    there. The shipped solid ──► is a LOCATING edge: following
                    it puts the party in front of B. Only locating edges carry
                    reach.
A ──╳──► B          a STRUCK edge — the clue the counterfactual removes. Drawn
                    over, never deleted: a gap where a lead used to be is
                    unreadable.
┌╌╌╌╌╌╌┐
╎ NODE ╎            an ORPHANED node — no locating edge reaches it any more. The
└╌╌╌╌╌╌┘            dashed rule replaces whatever rule the box had, so an
                    orphaned hub is dashed too.
```

Phase styling — make the play-shape legible:

- **Linear / locked stretch** (no real player choice yet): chain the nodes top-to-bottom with `═══` double edges, and note *why* it's a corridor.
- **Live branch** (players choose): fan out with `─── ` single edges to the options side by side.
- Tag each node's prep state inline: `★ prepped`, `(placeholder)`, or an open `objective: TBD`.
- Close with a small legend mapping line styles to session phases (e.g. `═══ Session 1 (linear)` / `─── Session 2+ (branch live)`).

Anchor the whole thing in the *Don't Prep Plots* frame: this is **a map for the GM, not a corridor for the players** (see the repo's planning-method handbook). The branch points and clue edges are the load-bearing structure; draw those faithfully and let the rest stay sparse.

Keep maps ASCII-only and monospace-safe (box-drawing characters are fine) with lines under ~80 columns so nothing wraps in a terminal or a GitHub code fence.

## Counterfactual mode — strike a clue, see what still reaches

The one **as-if** view this skill draws, and the only place the three glyphs above
are used. Reached by an explicit ask — *"strike this clue — what still reaches?"*,
*"what if they never take that lead?"*, *"where is the single point of failure?"*.
Steps 1 and 2 run unchanged; then:

**A. Type every lead edge in scope — `locates` or `names`.** A **locating** edge
puts the party in front of its target; a **naming** edge establishes the target,
or a reason to go, and carries no way to get there. The type belongs to the
*edge*, not the clue — one lead can locate one node and only name another. Read
the type off the entry's own sentence. Where a sentence does not say, **the edge
does not count as locating**: the question asked is *where is the single point of
failure*, so over-reporting is the safe error. Two values, never a third — a
prospective locator ("may know where it stands"), a stale sighting, and a locator
sitting somewhere unreachable all answer the only question here the same way, and
all read as `names`.

Check the campaign's planning-method handbook for a marking convention first
(*Lead typing — names vs locates*); where it states one, follow it. Absent one —
the normal case — infer from the sentences and **say so**. Never silence, never a
refusal to answer for want of a convention. File the reading as a **strike
ledger**, one row per edge, which is what the DM audits and what the arithmetic
below is reconciled against:

| Edge | Type | Read from | After the strike |
|---|---|---|---|
| Copperton → Ruins of Emberwillow | locates | "go there and consult the druid Fernwyn" | struck |
| Ruins of Emberwillow → Redfang Castle | names | "might know the whereabouts" — prospective | standing |

**B. Draw both states** — as-built above, as-if below — in the vocabulary above.

**C. Verify your own arithmetic before you deliver it.** The output *is* a count,
and a count nobody checked is not an answer. Recompute reachability **twice** over
the ledger — once with every row standing, once with the struck rows removed —
walking only `locates` edges out from where the party can already get, and report
both sets:

```
Orphaned as-built: Redfang Castle · Stonesong Cave
Orphaned as-if: Redfang Castle · Ruins of Emberwillow · Stonesong Cave
```

Names are separated by `·`, and either line reads `none` when its set is empty.
**Both are mandatory**, and the
second without the first is the specific false headline this guards against:
*"one strike orphans both destination nodes"* is a different claim when they were
already unreachable. Then reconcile the drawing against the ledger — a node drawn
orphaned that the ledger still reaches, or drawn reached that the ledger orphans,
is an arithmetic bug and not a drawing choice.

**D. Deliver as an Artifact** — both diagrams in a `<pre>`, the ledger, both
verdict lines, and the "what this surfaces" read. Self-contained and theme-aware;
the DM reads it on a tablet. **The sketch is the whole deliverable**: it carried
the entire finding in the build that settled this, and an interactive sweep buys
only the round trip a second strike would cost. Build one **only** when the DM
asks to browse the strike space rather than to name a strike.

None of this touches the as-built map, which stays ASCII in chat per step 5.

