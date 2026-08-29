# The encounter-meta block

Every fight filed onto a page lands as an `> [!encounter-meta]` callout — the
machine-findable summary of the fight's vitals, with the prose it sits in
(terrain, tactics, the complication's staging) as normal page text around it.
The combat-generator skill composes the block (its *Filing format* section
owns what goes in the fields); every procedure that files a fight files it in
this shape. **This file is the library's one statement of that shape** —
nothing else restates it.

```markdown
> [!encounter-meta]
> **Party:** <size and level sized for, e.g. 6 PCs, Level 1>
> **Enemies:** <each creature × count with looked-up XP> → **<total XP>**
> **Budget:** <difficulty>, level <L>, <N> PCs = <per-char> × <N> = **<budget>** (<spent>, <remainder>)
> **Terrain:** <one line — levels, cover, hazards>
> **Spotlight:** <texture; if aimed/puzzle, who and the staging that fires their ability>
> **Objective:** <the win condition — the complication usually lives here>
> **Note:** <optional — table rules, dials, absence adjustments>
```

Party, Enemies, Budget, Terrain, Spotlight, and Objective are required;
Note is optional. Every creature named on the `Enemies:` line carries a
stat-block reference (`{monster:Name}` where the render tokens are in use) —
a bare creature name is a defect here as everywhere on a page. The
`Spotlight:` field is the **fight** half of a page's spotlight annotations: a
`Spotlight (scene):` line (the session-page format's other spotlight shape)
never sits inside this block, which is what keeps the fight-variety ledger
fights-only.

This is a **library-owned format — never improvise its shape.** The block
above is what the code reads: build-session's parser
(`scripts/session_parser.py`) reads the callout, the mechanical checker
(`lib/mechanical-checker/`) asserts its six labels, and campaign repos may
build tooling that parses it. Changing the shape is a breaking change, and
every reader is held to this file rather than to a copy of it (library sync
obligations: `docs/campaign-contract.md`).
