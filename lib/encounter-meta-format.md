# The encounter-meta block

Every fight filed onto a prep sheet or node page lands as an `> [!encounter-meta]` callout — the
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
Note is optional. A **floating** fight (the combat-generator skill's
scene-free form) fills the same six labels — its `Terrain:` line carries the
terrain *roles* the fight needs (`needs: a high position, a cover field, a
choke`) rather than concrete ground, and its creature names appear on the
`Enemies:` line only. The shape is unchanged; the checker's
`combat-generator/floating-terrain-roles` rule asserts the role-form line
when a floating fight is checked. Every creature named on the `Enemies:` line carries a
stat-block reference (`{monster:Name}` where the render tokens are in use) —
a bare creature name is a defect here as everywhere on a page. The
`Spotlight:` field names the fight's texture and, for an aimed or puzzle
fight, the opportunity it stages and whom it is staged for — never who acts
or whether it works; it is the line catch-up marks fired or denied after
play.

This is a **library-owned format — never improvise its shape.** The block
above is what the code reads: combat-generator's mechanical checker
(`scripts/mechanical_checker/` inside that skill) asserts its six labels, and campaign repos may
build tooling that parses it. Changing the shape is a breaking change, and
every reader is held to this file rather than to a copy of it.
