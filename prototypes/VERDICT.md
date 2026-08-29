# Floating fight forms — prototype verdict

Throwaway prototypes (never merge). They settled how the library resolves
the tension between build-session's scene-tied fights and the Eight Steps'
scene-decoupled "choose relevant monsters."

## Question

What form lets a prepped fight move to whatever scene actually fires, with
a couple of on-the-fly changes — without losing the XP math, complications,
and spotlight machinery?

## Verdict

Every fight is one of two forms, named by the caller:

- **Pinned** — the fight *is* the scene (fight-scenes, keyed rooms).
  Today's fully concrete output; moving it is not a supported operation.
- **Floating** — chosen form: **pre-cast roster, functional prose**
  (`portable-fight-prototype.html`'s lineage, final shape in
  `floating-fight-forms.html` Option A′). Real creatures on the Enemies
  line only (exact math, stat links); everywhere else roles — a
  mechanism-named title, leader/screen/skirmisher, 2–4 terrain roles the
  fight *needs*, tactics that run verbatim under any casting. Bound at the
  table by casting the live scene's nouns into the roles out loud. Files
  in the session page's optional **Relevant Monsters** section.

## Rejected along the way

- Binding tables (won't be read mid-session; pre-built alternates are
  speculative prep) — bindings exist only when the fight is the scene.
- Shea-bare monster lists (lose the fight mechanics worth preserving).
- Uncast XP-slot rosters (mid-session lookup defeats the generator; the
  sourcing doctrine and Enemies-line checks can't run on approximations).
- A `Habitat:` meta line (a scene descriptor by another name).
- Scene-flavored names ("The Drowning-Rite", "Eelgrass Cult ambush") —
  a ritual happens at a place; cultists exist at a place.

Implementation: the `floating-fights` branch (commit "Add the floating
fight form beside pinned").
