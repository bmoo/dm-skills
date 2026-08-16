# Map render — the tactical map step

Turns the filed `## Edges (render-ready)` list — off whichever page carries
it — into a **DM-only tactical map**: a gpt-image-2 render on a true 5-ft
grid, verified against the edge list by a slate walk, filed to the wiki.

**The posture:** *runnable and handsome, in that order.* A DM must be able to
count squares off it; connections must read at a glance; it must never
*silently* contradict canon. Beyond that, **the drawn map is the dungeon** — a
room that renders a square larger than anyone imagined simply *is* that size,
and the edge list is prep scaffolding, not a contract. The verification slate
exists to make every divergence a conscious choice, never a silent one.

**One artifact.** The render is the DM sheet — secrets drawn plainly, node
IDs, legend. Players only ever see the DM's hand transcription at the table.
No player-facing variant is produced, and per-floor renders of a multi-level
site need not share a scale.

## When to run

- **In the forward flow:** after Step 8 files the dungeon key onto the
  session page — offer the render the same way Step 8 offers filing.
  Never before filing: the render consumes the *filed* edge list.
- **Standalone:** against a **session page** that already carries an
  `## Edges (render-ready)` section — the accepted edge case for sites
  filed before this step existed. Invoked directly — "render the map for
  \<site\>" — with no other step of this skill in play. No node page need
  exist: a site built out on an unplayed session page renders from that page
  alone.

  A site whose edge list sits on a **node** page is out of scope: Step R5
  files onto the session page the site is built out on, so a render read
  off a node page would have nowhere to land; relocating topology between
  page kinds is the consuming repo's business.

A page without a filed edge list can't be rendered; authoring one is
node-deepening work (build-session's `node-deepening.md`), not this step's.

## Inputs — the edge-list contract

The render consumes two sections of the page carrying the filed edge list:

1. **`## Edges (render-ready)`** — the topology. Each row: edge ID,
   endpoints, and a Type column in the Step 4 vocabulary — a **base**
   (`open` · `door` · `locked` · `grate` · `vertical`⟨stairs · shaft-chute ·
   ladder · slope⟩) plus composable **modifiers** (`secret` · `one-way` ·
   `trap` · `hazard` · `up`/`down` on verticals, read against the written
   endpoint order).
2. **`## Keyed areas`** — room names and flavor (quarter/zone groupings,
   water, rubble, light), which feed the prompt's texture language.

The edge section is filed **concealed** — the whole section, heading
included, inside an HTML comment — because it is machine state and never
DM-visible. This render reads raw markdown, so the concealment is invisible
to it and the section parses exactly as it always did.

**Token strictness:** everything before the first em-dash in the Type column
MUST be typed tokens from the vocabulary above — the em-dash is the boundary;
after it is annotation, free prose. The slate is derived mechanically from
the tokens, so an attribute that lives only in prose is invisible to
verification — how a secret chute got silently dropped once. If a page's
edge list predates this contract, tighten the Type column first and show the
DM the diff.

Endpoint notation: `—` is an interior edge, `→` marks an edge crossing the
site boundary (an entrance), written whichever direction reads naturally —
it is **not** a one-way marker. Only the `one-way` modifier restricts travel.

## Step R1 — Draw the wireframe anchor

**The model preserves what it is handed and ignores what it is told** — so
hand it *everything*. The anchor is not a blank grid but a **programmatic
wireframe** — grey room floors, walls derived from the edge list, room-ID
labels — so the topology rides the preserved channel too. With a wireframe
anchor the blank-grid failure classes (merged junctions, corridors landing on
the nearer room, invented shortcuts) stopped occurring.

Author a layout JSON from the edge list and keyed areas, then draw it:

```json
{
  "rooms":     [{"id": "N1", "block": [c0, r0, c1, r1]}],
  "corridors": [{"id": "E2", "path": [[c, r], [c, r]]}]
}
```

```bash
python3 <this skill's folder>/scripts/make-blank-grid.py \
  --size <WIDTHxHEIGHT> --pitch 48 \
  --layout <scratch>/layout.json --fill --output <scratch>/wireframe.png
```

Blocks are inclusive cell ranges. Paths are orthogonal waypoints starting
and ending one cell **inside** the rooms they join — a wall opening exists
only where consecutive path cells cross a boundary, so **the anchor cannot
express an invented connection**. A waypoint off the map edge opens an
entrance mouth in the map-edge wall. The script errors on room overlap;
fix the layout, never fudge it.

- `--size` must equal the gpt-image-2 `--size` exactly. Pick orientation
  from the site's shape (a long march of zones wants portrait; a sprawl
  wants landscape). Both edges multiples of 16, ratio ≤ 3:1. Default to the
  doubled sizes (`1536x2304`, `2304x1536`) — a 16-room site needs the
  resolution.
- 48 px per 5-ft square is the tested pitch. State the resulting
  square count (`cols × rows`) — the prompt references it.
- `--fill` paints every non-floor cell as dark mottled earth, and it is
  the standard anchor: the thematic surround must ride the *preserved*
  channel like the geometry does (a prompt licensed to repaint the margins
  has painted over lanes).

**Layout rules** — each bought with a render failure:

- **Engineer for clarity:** straight drops, targets directly below or
  beside their sources, generous whitespace between features.
- **Breathing room:** a corridor lane keeps at least one empty square
  from every wall it does not connect to — hugging lanes get sealed or
  truncated in the paint.
- **No ambiguous junctions:** two corridors join by one path ending on a
  cell of the other; prefer a clean T into a straight segment with clear
  ground around the joint.
- **Lengthen tight links:** a one-cell room-to-room corridor risks being
  bricked over — use two cells or more where the fiction allows.
  (Shared-wall openings between touching rooms are fine; the crossing
  step opens the wall.)

**Residual risk:** topology errors now concentrate at *tight geometry* —
long hugging crawls and mid-corridor junctions. Expect that edge class to
need a re-roll, a targeted edit pass, or a conscious amendment.

## Step R2 — Assemble the prompt

Compose from these parts, in order:

1. **The anchor instruction**, verbatim-close (tested wording — each clause
   bought back a failure):
   > The attached image is the complete WIREFRAME LAYOUT of this dungeon
   > on a 5-ft tactical grid, ⟨C⟩ squares wide by ⟨R⟩ squares tall. Grey
   > rectangles are the room floors, one-square-wide grey lines are the
   > corridors, dark lines are the walls, and each gap in a wall is a
   > doorway or opening. Every room already carries its ID label. THIS
   > GEOMETRY IS LAW: do not move, resize, reshape, add, remove, or
   > reconnect any room, corridor, wall, or opening; do not redraw,
   > resize, or offset the grid. Paint the finished map exactly on top of
   > this wireframe — beautify the surfaces, keep every wall and every
   > opening precisely where drawn, keep every room's ID label where it
   > stands. EVERY floor cell the wireframe shows must be painted as
   > walkable floor, and EVERY gap in a wireframe wall must remain an
   > open connection — sealing a drawn corridor or bricking over a drawn
   > opening is an error. AFTER texturing, REDRAW the faint 5-ft grid
   > lines over every finished floor so squares can be counted inside
   > every room and corridor.
   Follow it with the two absolute rules (belt and braces even with the
   wireframe): *every corridor joins rooms at both ends — no dead ends;
   every connection is its own separate passage — no merges, no T-joins,
   no shared junctions beyond those drawn.*
2. **The style line** — top-down tactical map, flat colors, no perspective;
   name the site's material palette from the keyed areas (brick, adobe,
   black water, string-bulbs…). This is where *handsome* is earned — art
   direction is welcome, as long as walls, glyphs, and labels stay crisp.

   **Palette words suppress the grid.** A masonry palette — "red brick",
   "flagstone", "cobbles", "tile" — makes the model pave those rooms in
   fine coursing *instead of* drawing the 5-ft grid, and only in those
   rooms. Whenever the palette names a coursed material, say so
   explicitly: the grid squares are **large**, far bigger than a floor
   brick; **brick coursing, cobbles and flagstone patterns are not a
   grid**; every room carries the same grid drawn *on top of* its
   material, one continuous size across the whole map.
   Then **the surround**: declare the anchor's dark fill SOLID EARTH —
   unexcavated ground, nothing in it passable — and dress it in the site's
   own strata (roots reaching down, old bones, buried debris), kept dimmer
   and quieter than the floors, with NO grid lines on the earth and the
   explicit guard that nothing painted in it may read as a room, corridor,
   doorway, or passable space.
3. **The rooms** — dressing only; positions and IDs are already in the
   wireframe. One line each: ID, name, one clause of interior flavor,
   zone palette gestures. No coordinates.
4. **The connections** — "The wireframe's connections are exactly these
   ⟨N⟩ — draw each with its symbol, and add NO other door, corridor, or
   opening anywhere", then one line per edge: which wireframe passage it
   is (by position, e.g. "the corridor dropping from N2's bottom wall
   into N5"), and the **legend fragment** for its base + modifiers (table
   below). The *nothing else* clause matters: invented corridors are the
   classic failure.
5. **Labels — edge IDs stay off the map.** Wanted: room IDs with names,
   entrance destination labels ("↑ Harrow cellar"), hazard short names,
   secret "S" marks. Bare E-numbers are prep bookkeeping — render one only
   when the session page stages an interaction with that edge by ID. The
   prompt's per-edge lines still *reference* edges by position and symbol;
   they just don't ask for the ID to be painted.
6. **Furniture** — each room labeled with its ID in bold; a small legend
   box keyed to the symbols actually used, drawn on a pale parchment
   plaque set into the earth; a scale bar "1 square = 5 ft"; the title on
   a parchment banner. Text on this map is wanted (it's a DM sheet) — but
   keep labels short; long strings garble.

### Legend fragments

| Type | Prompt fragment |
|---|---|
| `open` | an open doorway: a plain gap in the wall with no door leaf, the wall ends thickened slightly at both jambs — *weak against a door-rich art idiom: short room-to-room openings get closed doors anyway. Where open-plan matters, add "no door leaf anywhere on this passage" to that edge's line* |
| `door` | a closed wooden door: a solid dark-brown rectangle exactly spanning the gap in the wall, perpendicular to the wall line |
| `locked` | the closed-door rectangle with a small red padlock icon centered on it |
| `grate` | a barred grate spanning the gap: a row of short parallel bars one can see through but not pass |
| `vertical`⟨stairs⟩ | a staircase: parallel tread lines across the passage, treads growing narrower toward the lower end |
| `vertical`⟨shaft-chute⟩ | a vertical shaft: a small hatched circle at the connection point |
| `vertical`⟨ladder⟩ | a ladder: two parallel rails with evenly spaced rungs |
| `vertical`⟨slope⟩ | a sloping passage marked with downhill chevrons |
| `secret` (modifier) | drawn with a dashed outline instead of solid, with a bold red letter "S" directly beside it |
| `one-way` (modifier) | a bold arrowhead along the centerline pointing the only direction of travel |
| `trap` (modifier) | a small solid red triangle with a bold white "T" inside, on the trapped tile or door |
| `hazard` (modifier) | diagonal yellow-and-black caution stripes over the affected tiles, with a short name label |
| `up`/`down` (modifier) | rendered as the destination label ("↓ N5" / "↑ El Campo Santo"), never as an arrow — arrows belong to `one-way` |

Modifiers compose onto bases in the prompt line: a `vertical⟨shaft-chute⟩ ·
up · secret` reads "a vertical shaft — a small hatched circle — drawn dashed
with a bold red S beside it, labeled '↑ ⟨destination⟩'".

## Step R3 — Generate

Reuse the `campaign-art` generator, wireframe attached as the reference
(this switches it to the edits endpoint, which is the point):

```bash
python3 .claude/skills/campaign-art/scripts/generate_image.py \
  --prompt "<the Step R2 prompt>" \
  --reference <scratch>/wireframe.png \
  --output Media/images/<site-basename>-map.png \
  --size <same WIDTHxHEIGHT> --quality high
```

Generous Bash timeout (~300000 ms or higher) — a high-quality render commonly
takes two minutes plus. `OPENAI_API_KEY` comes from the environment, never
the repo.

## Step R4 — Walk the verification slate

Derive the slate **mechanically from the edge list before looking at the
image** — never from memory, never from the image itself:

- one line per **edge**: endpoints connected, base symbol right, modifiers
  present;
- one line per **secret** — these are the lines that bite;
- one line per **trap** and **hazard** marking;
- one line per **room**: present, labeled with its ID, **and its floor grid
  countable** — walk this room by room, never as one global glance: the
  failure is *per-palette*, not per-image;
- two furniture lines: legend box present and truthful · scale bar present;
- one **labels** line: no bare edge-ID codes painted anywhere, and the
  wanted labels — room IDs + names, entrance destinations, hazard short
  names, secret "S" marks — all present;
- one **inventions** line: no room, corridor, or connection the edge list
  doesn't have (walk the image for extras — this direction catches what
  the per-edge lines can't);
- one **surround** line: the earth fill covers all negative space, stays
  dimmer than the floors, and contains nothing that reads as a room,
  corridor, or opening.

**Walk the slate on the image you are filing, not the diff from the last
one.** A re-roll or targeted edit regenerates *everything*, including the
parts nobody asked to change. Re-walk every line, every render.

Read the rendered image and mark every line **pass / amend / critical** —
the flag is for divergence that breaks the dungeon, not divergence that
needs an edit:

- **Pass** — matches, or differs only in ways the bar doesn't price
  (room a square bigger, corridor bends, style).
- **Amend** — any divergence that leaves the floor check standing.
  **Resolution: the drawn map is canonical.** Amend the filed edge list,
  the prose around it, and any other page that snapshots the site to match
  the image — in the filing commit, named in the log. This covers cosmetic
  drift *and* structural divergence — a door drawn where `open` was
  written, rooms moved, a re-routed **bonus** connection, even a secret —
  *provided* the amendment carries its load: if the lost or changed link
  backed a clue-web lead or a revelation, re-seed that clue
  (`seed-clues`) in the same amendment. The sin guarded against is
  *silent* loss; the cure is a recorded edit, not an escalation.
- **Critical** — the drawn geometry breaks the floor check or the sheet:
  an entrance lost, a spine route to the objective deleted, a free
  bypass invented around a priced route, a room missing or unlabeled, an
  illegible or absent floor grid.

**Restoring the spec is conformance; adopting the drawing is a decision.**
Drawn-map-is-canon settles *drafting* divergence — it is not licence to
adopt a change that rewrites a node's role, deletes a priced gate, or
re-points a clue. While the edge list is still achievable, prefer another
render: the DM only ever needs to be asked to **change** canon, never to
**keep** it.

**Re-roll policy:** any critical line → re-roll, **naming the failure
precisely in the tightened prompt** — a named failure reliably fixes on the
next roll — up to **two re-rolls** (three images total). *Cost to canon is a
second trigger*: a divergence cheap to name but expensive to amend earns a
roll even when it scores as amend. Beyond the ceiling, a **targeted edit
pass** — same anchor and prompt, only the surviving failures named — is the
sanctioned remedy; it is not a fresh roll.

**Expect the tight-lane class to trade** — naming one fix reliably costs
another; that is the step's ceiling, and the reason bonus-edge drift is
priced as amend rather than chased. Judge each render on its own full
slate — don't mix rooms from different runs. If every render still carries
a critical line, stop and flag the DM with the best image and the failed
lines: *this divergence needs your decision* — accept-with-amendment, a
targeted edit pass, more rolls, or no map. That flag is the only point the
DM enters the loop; amendments never escalate.

## Step R5 — File

On a fully passing (or amend-resolved) slate:

1. Image is already at `Media/images/<site-basename>-map.png` (match the
   basename of the page the site is built out on; `-map` suffix).
2. Embed on the **session page** the site is built out on — session-scoped
   output by the same test that keeps the edge table off a node page. It
   lands as the page's *clickable keyed hotspot map* (the session format's
   "the map navigates too" treatment), never a plain `[!map]` embed; badge
   positions start from the layout JSON's room centers, then are verified
   against the drawn render — rooms drift in generation. The render
   **replaces** any earlier stylized site illustration on that page: one
   keyed map per site, the superseded image retired in the same change.
3. Apply any amendments to the edge list **in the same commit** as
   the embed — the page must never carry a map and an edge list that
   disagree.
4. Post the slate result wherever the work is being tracked, write the
   operation log entry (drift amendments named), refresh the page's own
   summary metadata and whatever catalog the repo builds from it, and
   redeploy if the repo has a publish step.
