# Rendering a session page to PDF

Load this file only when the DM asks for a printable/styled PDF of a
session page. The renderer produces a modern adventure-book look — light
parchment page, themed accent colors, boxed read-aloud text — from a page
written in the session-page format
([session-page-format.md](session-page-format.md)).

## Usage

```bash
python3 <skill-folder>/scripts/render_session.py <input.md> [--output <output.pdf>]
```

`scripts/` sits beside this file in the installed skill folder. If
`--output` is omitted, the PDF is written alongside the input file with the
same basename.

## Format authority

The wire format's authority is `scripts/session_parser.py` (its module
docstring lists the directive grammar) and the fixtures under
`scripts/fixtures/` — read those when a document fails to parse. The parser
fixes no section list; the skeleton lives in
[session-page-format.md](session-page-format.md).

Directives: `> [!read-aloud]`, `> [!dm-sidebar]`, `> [!encounter-meta]`,
`> [!map]`, `> [!art]` (float variants `art-left`/`art-right`),
`> [!hazard]`, `> [!contagion]`, `> [!npc-quote]`, `> [!sidebar]`,
`> [!page-break]`.

Reference tokens: `{monster:Name}`, `{item:Name}`, `{spell:Name}`,
`{skill:Name}`, `{condition:Name}`, `{action:Name}`.

## Styling

`scripts/styles.css` carries the palette: a light parchment page background
and per-session accent themes (set `data-theme` on the body; available
themes are listed at the top of the stylesheet). The PDF and any
campaign-site renderer should stay visually aligned — when the palette here
changes, sync the site's stylesheet in the same round of work.

Proven treatments any downstream renderer should honor:

- **Read-aloud** renders as boxed text: a pale salmon panel, 2px
  dark-red rules top and bottom, a small dot capping each end of both
  rules, body text upright (not italic), no kind label.
- **Reference-token colors:** `{monster:}`/`{spell:}`/`{item:}` render as
  **bold red** links to their entity's reference page; `{skill:}`,
  `{condition:}`, `{action:}` render as **bold green** links to public
  rules pages (the anchor scheme lives in `scripts/resolver.py`). Names
  outside the known sets (house conditions and the
  like) degrade to bold green text — a styled term, never a broken link.
- **Art callouts** render as a figure: a small uppercase artist-credit
  line above the image, the image full-bleed within its column (a subtle
  irregular clip-path sells the printed-inset look), and the caption line
  in small muted type below. `art-left`/`art-right` float at roughly 46%
  column width so prose wraps beside the study; callout boxes `clear`
  floats rather than sitting beside them — a box pinned in the leftover
  column renders as a long skinny strip, so only flowing prose shares a
  line with a float.
