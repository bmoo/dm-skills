"""Model-free mechanical checker for generator output.

The deterministic tier of the runtime output-verification loop.
A generator runs these checks on its *own* output text to
catch mechanical promise-breaks — arithmetic, counts, format, graph properties —
before it offers the output to file.

Pure and model-free by construction:

  - The single public entry point, ``run_checks``, takes the output artifact as a
    plain string. It performs NO I/O — it never reads a file, never calls a
    model. String in, findings out.
  - Every individual check is likewise a pure ``str -> list[Finding]`` function,
    registered by its check id and tagged with the producing skill it belongs to.

This is the sole test seam for the whole deterministic tier. Per-generator checks
are added by registering more functions — see
``register_check`` and the README beside this file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Finding — the verdict shape every check reports.
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Finding:
    """One broken mechanical promise.

    A *passing* check contributes NO finding — the findings list is failures
    only. The four fields are exactly what user story 18 asks the terminal
    mechanical-escalation to carry: which check, what was expected, what was
    actually found, and where on the page.
    """

    check_id: str
    expected: str
    actual: str
    output_location: str


# A check is a pure function: the artifact text in, a list of findings out.
#
# Most checks need only the artifact (``str -> list[Finding]``). A check that
# needs external context the artifact alone cannot carry takes a second
# argument, an optional context dict (``(str, dict | None) -> list[Finding]``).
# The registry records which shape a check has (``takes_context``) so
# ``run_checks`` dispatches each correctly; a context-free check never sees the
# context, a context-taking one always does. No shipped check takes context
# today; the seam stays for the next one that does.
Context = Optional[Dict[str, Any]]
CheckFn = Callable[..., List[Finding]]


# --------------------------------------------------------------------------- #
# Registry — the extension point later checks grow.
# --------------------------------------------------------------------------- #
#
# Each check is registered under its check id and tagged with the producing
# skill that owns it. Adding a check is a one-function, one-registration
# operation: write ``def _my_check(artifact) -> list[Finding]`` and decorate it
# with ``@register_check("combat-generator/enemies-line-arithmetic",
# "combat-generator")``. ``run_checks`` then selects it whenever a caller
# requests that id.

_REGISTRY: Dict[str, "_RegisteredCheck"] = {}


@dataclass(frozen=True)
class _RegisteredCheck:
    check_id: str
    producing_skill: str
    fn: CheckFn
    takes_context: bool


def register_check(
    check_id: str, producing_skill: str, takes_context: bool = False
) -> Callable[[CheckFn], CheckFn]:
    """Decorator: register ``fn`` as the check ``check_id`` owned by
    ``producing_skill``. Raises if the id is already taken (two checks sharing an
    id is the silent-collision failure class this loop exists to kill).

    ``check_id`` is the promise's stable slug, ``<qualifier>/<stem>``, and its
    qualifier IS ``producing_skill`` — that is the whole reason the shipping skill
    folder was chosen as the qualifier. Registering a check whose qualifier names
    a different skill (or an id carrying no qualifier at all) raises HERE, at
    import time, so a misfiled check is impossible rather than merely unlikely.

    ``takes_context`` declares the check's shape. It defaults to ``False`` — a
    context-free ``str -> list[Finding]`` check, which is every shipped check.
    Pass ``takes_context=True`` for a check whose signature is
    ``(str, dict | None) -> list[Finding]`` because it needs external context
    (a party roster, say) the artifact cannot carry.
    ``run_checks`` reads this flag to hand the context only to the checks that
    asked for it, so the default keeps every existing 3-arg call working
    unchanged."""

    def _decorate(fn: CheckFn) -> CheckFn:
        if check_id in _REGISTRY:
            raise ValueError(
                f"check id {check_id!r} is already registered "
                f"(to {_REGISTRY[check_id].producing_skill!r})"
            )
        qualifier, slash, stem = check_id.partition("/")
        if not slash or not stem or qualifier != producing_skill:
            raise ValueError(
                f"check id {check_id!r} must be a '<producing skill>/<stem>' slug "
                f"qualified by {producing_skill!r}, not {qualifier!r}; the "
                f"qualifier names the skill that owns the promise"
            )
        _REGISTRY[check_id] = _RegisteredCheck(check_id, producing_skill, fn, takes_context)
        return fn

    return _decorate


# --------------------------------------------------------------------------- #
# Public entry point.
# --------------------------------------------------------------------------- #

def run_checks(
    artifact: str,
    producing_skill: str,
    checks: List[str],
    context: Context = None,
) -> List[Finding]:
    """Run the requested mechanical checks over ``artifact`` and return findings.

    Args:
        artifact: the generated output, as a string. The generator has its
            output text in context and hands it in — this keeps the function pure
            and the test seam a plain string-in / findings-out. NO file is read
            inside this function.
        producing_skill: which skill produced the output — ``"combat-generator"``
            for every shipped check. Only checks owned by this skill may be
            requested, so a caller applies only its own skill's check subset.
        checks: the rubric subset — the list of check ids to apply.
        context: optional external data a check needs and the artifact text
            cannot carry. This stays PURE — ``context`` is data handed in, never
            I/O. A context-free check ignores it entirely; only checks registered
            with ``takes_context=True`` receive it. Defaults to ``None`` so every
            3-arg call is unchanged.

    Returns:
        A list of :class:`Finding`, one per broken promise, in the order the
        requested check ids were given (and, within a check, the order the check
        emits them). A check that passes contributes nothing.

    Raises:
        ValueError: if a requested id is unregistered, or is registered but owned
            by a skill other than ``producing_skill``. Silently skipping an
            unknown or mis-scoped check is the same failure class as a broken
            symlink — this loop refuses to skip silently, so it raises loudly. A
            context-taking check may also raise if it is run without the context
            it needs — the loop refuses to fake a verdict it cannot reach.
    """
    findings: List[Finding] = []
    for check_id in checks:
        registered = _REGISTRY.get(check_id)
        if registered is None:
            raise ValueError(
                f"unknown check id {check_id!r}; registered ids: "
                f"{sorted(_REGISTRY)}"
            )
        if registered.producing_skill != producing_skill:
            raise ValueError(
                f"check {check_id!r} is owned by "
                f"{registered.producing_skill!r}, not {producing_skill!r}; "
                f"a caller applies only its own skill's rubric subset"
            )
        if registered.takes_context:
            findings.extend(registered.fn(artifact, context))
        else:
            findings.extend(registered.fn(artifact))
    return findings


# --------------------------------------------------------------------------- #
# Reference check — the encounter-meta required lines (the fight procedure).
# --------------------------------------------------------------------------- #
#
# The `> [!encounter-meta]` block must
# carry its six required lines — Party, Enemies, Budget, Terrain, Spotlight,
# Objective (Note optional). The block spec lives in the library's shape
# statement (`lib/encounter-meta-format.md` — "Note is optional"), which the
# fight skill's *Filing format* section cites rather than restates.
#
# The list below stays a **literal**: this directory ships into the skills by
# symlink and must not read the maintenance docs at run time.
#
# This one check proves the whole path end to end; the rest of the fight
# procedure's mechanical rows extend the same registry below.

_ENCOUNTER_META_REQUIRED = ("Party", "Enemies", "Budget", "Terrain", "Spotlight", "Objective")

# The block opens with a `> [!encounter-meta]` callout marker.
_ENCOUNTER_META_MARKER = re.compile(r"^\s*>\s*\[!encounter-meta\]\s*$", re.MULTILINE)


def _required_label_present(block: str, label: str) -> bool:
    """True if the encounter-meta ``block`` carries a ``> **<label>:**`` line."""
    pattern = re.compile(
        r"^\s*>\s*\*\*" + re.escape(label) + r":\*\*",
        re.MULTILINE,
    )
    return bool(pattern.search(block))


def _extract_encounter_meta_block(artifact: str) -> str | None:
    """Return the text of the first encounter-meta callout, marker through its
    last consecutive `>` quoted line, or None if the artifact has no such block."""
    marker = _ENCOUNTER_META_MARKER.search(artifact)
    if marker is None:
        return None
    lines = artifact[marker.start():].splitlines()
    block_lines = [lines[0]]  # the marker line itself
    for line in lines[1:]:
        if line.lstrip().startswith(">"):
            block_lines.append(line)
        else:
            break
    return "\n".join(block_lines)


@register_check("combat-generator/encounter-meta-required-lines", "combat-generator")
def check_encounter_meta_required_lines(artifact: str) -> List[Finding]:
    """The encounter-meta block carries all six required lines.

    Party, Enemies, Budget, Terrain, Spotlight, Objective are required; Note is
    optional. A missing required line is a filing defect.
    """
    location = "> [!encounter-meta] block"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return [
            Finding(
                check_id="combat-generator/encounter-meta-required-lines",
                expected="an encounter-meta block with lines: "
                + ", ".join(_ENCOUNTER_META_REQUIRED),
                actual="no `> [!encounter-meta]` block found",
                output_location=location,
            )
        ]

    missing = [label for label in _ENCOUNTER_META_REQUIRED if not _required_label_present(block, label)]
    if not missing:
        return []

    present = [label for label in _ENCOUNTER_META_REQUIRED if label not in missing]
    return [
        Finding(
            check_id="combat-generator/encounter-meta-required-lines",
            expected="all six required lines: " + ", ".join(_ENCOUNTER_META_REQUIRED),
            actual="missing " + ", ".join(missing)
            + (" (present: " + ", ".join(present) + ")" if present else ""),
            output_location=location,
        )
    ]


# --------------------------------------------------------------------------- #
# The fight procedure's content checks.
# --------------------------------------------------------------------------- #
#
# Scope discipline (shared with /): the required-lines check owns
# *presence* — a missing block or a missing required line is its finding. The
# content checks fire only on a line that is PRESENT but whose content breaks the
# promise; each returns [] when the line it needs is absent, so a missing block
# yields exactly one finding, the required-lines check's, and every finding stays
# singly-fixable by the self-heal loop. Every check reads within the
# encounter-meta block, exactly as the required-lines check does.


def _meta_line_value(block: str, label: str) -> str | None:
    """Return the text after ``> **<label>:**`` in the encounter-meta ``block``,
    or None if the block carries no such line. The required-lines check reports
    the absent-line case."""
    m = re.search(
        r"^\s*>\s*\*\*" + re.escape(label) + r":\*\*\s*(.*)$",
        block,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def _int(text: str) -> int:
    """Parse an XP/count integer that may carry thousands separators (`1,100`)."""
    return int(text.replace(",", "").strip())


# One creature entry on the `Enemies:` line: a stat-block reference, then
# `× <count>`, then an optional `(<per-creature XP> XP)`. The reference is one of
# three forms — a `{monster:Name}` render token, a `[Name](link)` markdown link,
# or a BARE name (which the stat-block-reference check flags). Multiplication is
# `×` (U+00D7) or a plain `x`.
_CREATURE_RE = re.compile(
    r"(?P<tagged>\{monster:(?P<mname>[^}]+)\})"
    r"|(?P<linked>\[(?P<lname>[^\]]+)\]\([^)]*\))"
    r"|(?P<bare>[A-Za-z][A-Za-z0-9 '\-]*?)"
    r"(?=\s*[×x]\s*\d)",
    re.UNICODE,
)
# Given a matched reference, the `× count (perXP XP)` tail that follows it.
_COUNT_XP_RE = re.compile(r"\s*[×x]\s*(?P<count>\d+)\s*(?:\(\s*(?P<xp>[\d,]+)\s*XP\s*\))?", re.UNICODE)
# The stated line total: `→ **<total> XP**` (the `XP` word is optional inside the bold).
_ENEMIES_TOTAL_RE = re.compile(r"→\s*\*\*\s*(?P<total>[\d,]+)\s*(?:XP)?\s*\*\*", re.UNICODE)


@dataclass(frozen=True)
class _Creature:
    name: str
    form: str  # "tagged" | "linked" | "bare"
    count: int
    per_xp: int | None


def _parse_creatures(enemies_line: str) -> list[_Creature]:
    """Extract every `<ref> × <count> (<perXP> XP)` entry on the Enemies line."""
    creatures: list[_Creature] = []
    for ref in _CREATURE_RE.finditer(enemies_line):
        tail = _COUNT_XP_RE.match(enemies_line, ref.end())
        if tail is None:  # a `{monster:...}` in prose with no `× count` — not an entry
            continue
        if ref.group("mname") is not None:
            name, form = ref.group("mname").strip(), "tagged"
        elif ref.group("lname") is not None:
            name, form = ref.group("lname").strip(), "linked"
        else:
            name, form = ref.group("bare").strip(), "bare"
        xp = _int(tail.group("xp")) if tail.group("xp") else None
        creatures.append(_Creature(name, form, _int(tail.group("count")), xp))
    return creatures


@register_check("combat-generator/enemies-line-arithmetic", "combat-generator")
def check_enemies_line_arithmetic(artifact: str) -> List[Finding]:
    """On the `Enemies:` line, Σ(count × per-creature XP) equals the stated
    total (`lib/encounter-meta-format.md` — "each creature × count with
    looked-up XP"). Fires only when the line carries entries *and* a total
    to compare — an unparseable or absent line belongs to the required-lines
    check, not here."""
    location = "> [!encounter-meta] block, `Enemies:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line = _meta_line_value(block, "Enemies")
    if line is None:
        return []
    total_m = _ENEMIES_TOTAL_RE.search(line)
    creatures = [c for c in _parse_creatures(line) if c.per_xp is not None]
    if total_m is None or not creatures:
        return []
    computed = sum(c.count * c.per_xp for c in creatures)
    stated = _int(total_m.group("total"))
    if computed == stated:
        return []
    terms = " + ".join(f"{c.count}×{c.per_xp}" for c in creatures)
    return [
        Finding(
            check_id="combat-generator/enemies-line-arithmetic",
            expected=f"Σ(count × XP) = {computed} ({terms})",
            actual=f"stated total {stated}",
            output_location=location,
        )
    ]


# The XP-budget-per-character table, transcribed from
# `combat-generator/xp-budget.md` — "XP Budget per Character" (SRD 5.2
# "Combat Encounter Difficulty"). Embedded as data so the checker stays pure
# and self-contained;
# the citation is the sync obligation if the table ever changes.
_XP_BUDGET_PER_CHAR: Dict[int, Dict[str, int]] = {
    1: {"Low": 50, "Moderate": 75, "High": 100},
    2: {"Low": 100, "Moderate": 150, "High": 200},
    3: {"Low": 150, "Moderate": 225, "High": 400},
    4: {"Low": 250, "Moderate": 375, "High": 500},
    5: {"Low": 500, "Moderate": 750, "High": 1100},
    6: {"Low": 600, "Moderate": 1000, "High": 1400},
    7: {"Low": 750, "Moderate": 1300, "High": 1700},
    8: {"Low": 1000, "Moderate": 1700, "High": 2100},
    9: {"Low": 1300, "Moderate": 2000, "High": 2600},
    10: {"Low": 1600, "Moderate": 2300, "High": 3100},
    11: {"Low": 1900, "Moderate": 2900, "High": 4100},
    12: {"Low": 2200, "Moderate": 3700, "High": 4700},
    13: {"Low": 2600, "Moderate": 4200, "High": 5400},
    14: {"Low": 2900, "Moderate": 4900, "High": 6200},
    15: {"Low": 3300, "Moderate": 5400, "High": 7800},
    16: {"Low": 3800, "Moderate": 6100, "High": 9800},
    17: {"Low": 4500, "Moderate": 7200, "High": 11700},
    18: {"Low": 5000, "Moderate": 8700, "High": 14200},
    19: {"Low": 5500, "Moderate": 10700, "High": 17200},
    20: {"Low": 6400, "Moderate": 13200, "High": 22000},
}
_BUDGET_BANDS = ("Low", "Moderate", "High")

# The `Budget:` line: `<difficulty>, level <L>, <N> PCs = <per-char> × <N> =
# **<budget>** (<spent>, <remainder>)`.
_BUDGET_RE = re.compile(
    r"(?P<difficulty>[A-Za-z]+)\s*,\s*level\s*(?P<level>\d+)\s*,\s*(?P<pcs>\d+)\s*PCs?\s*=\s*"
    r"(?P<perchar>[\d,]+)\s*[×x]\s*(?P<n>\d+)\s*=\s*\*\*\s*(?P<budget>[\d,]+)\s*\*\*"
    r"(?:\s*\(\s*(?P<spent>[\d,]+)\s*spent)?",
    re.IGNORECASE,
)


def _parse_budget(block: str):
    line = _meta_line_value(block, "Budget")
    if line is None:
        return None, None
    return line, _BUDGET_RE.search(line)


@register_check("combat-generator/budget-line-arithmetic", "combat-generator")
def check_budget_line_arithmetic(artifact: str) -> List[Finding]:
    """The `Budget:` line's arithmetic holds — per-char × N = budget, and
    spent ≤ budget (`lib/encounter-meta-format.md` — "<per-char> × <N> =
    **<budget>**"; `combat-generator/SKILL.md` — "multiply by party size"). The two are independent
    fixes, so each violation is its own finding."""
    location = "> [!encounter-meta] block, `Budget:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line, m = _parse_budget(block)
    if m is None:
        return []
    findings: List[Finding] = []
    perchar, n, budget = _int(m.group("perchar")), _int(m.group("n")), _int(m.group("budget"))
    if perchar * n != budget:
        findings.append(
            Finding(
                check_id="combat-generator/budget-line-arithmetic",
                expected=f"per-char × N = budget: {perchar} × {n} = {perchar * n}",
                actual=f"stated budget {budget}",
                output_location=location,
            )
        )
    if m.group("spent") is not None:
        spent = _int(m.group("spent"))
        if spent > budget:
            findings.append(
                Finding(
                    check_id="combat-generator/budget-line-arithmetic",
                    expected=f"spent ≤ budget ({budget})",
                    actual=f"spent {spent} exceeds budget by {spent - budget}",
                    output_location=location,
                )
            )
    return findings


@register_check("combat-generator/per-char-matches-budget-table", "combat-generator")
def check_per_char_matches_budget_table(artifact: str) -> List[Finding]:
    """The per-char figure matches the SRD 5.2 budget table for that level ×
    difficulty (`combat-generator/xp-budget.md` — "Cross-reference party level
    with difficulty on the table below"). The band must be Low/Moderate/High — a
    stray band (`Hard`) has no column and is itself the defect."""
    location = "> [!encounter-meta] block, `Budget:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line, m = _parse_budget(block)
    if m is None:
        return []
    raw_band = m.group("difficulty")
    band = raw_band.capitalize()
    level, perchar = _int(m.group("level")), _int(m.group("perchar"))
    if band not in _BUDGET_BANDS:
        return [
            Finding(
                check_id="combat-generator/per-char-matches-budget-table",
                expected=f"difficulty ∈ {{{', '.join(_BUDGET_BANDS)}}} (budget bands)",
                actual=f"difficulty {raw_band!r} names no column in the budget table",
                output_location=location,
            )
        ]
    if level not in _XP_BUDGET_PER_CHAR:
        return []  # out-of-table level: presence/range is not this promise
    expected = _XP_BUDGET_PER_CHAR[level][band]
    if perchar == expected:
        return []
    return [
        Finding(
            check_id="combat-generator/per-char-matches-budget-table",
            expected=f"per-char {expected} ({band}, level {level})",
            actual=f"stated per-char {perchar}",
            output_location=location,
        )
    ]


@register_check("combat-generator/distinct-stat-block-cap", "combat-generator")
def check_distinct_stat_block_cap(artifact: str) -> List[Finding]:
    """Never more than three distinct stat blocks in one encounter — the
    hard rule (`combat-generator/xp-budget.md` — "Never put more than **three
    distinct stat blocks** in one encounter"). Copies of a type are fine; it's
    the number
    of *kinds* that is capped."""
    location = "> [!encounter-meta] block, `Enemies:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line = _meta_line_value(block, "Enemies")
    if line is None:
        return []
    creatures = _parse_creatures(line)
    if not creatures:
        return []
    distinct = list(dict.fromkeys(c.name.lower() for c in creatures))
    if len(distinct) <= 3:
        return []
    names = ", ".join(sorted({c.name for c in creatures}))
    return [
        Finding(
            check_id="combat-generator/distinct-stat-block-cap",
            expected="≤ 3 distinct stat blocks (hard rule)",
            actual=f"{len(distinct)} distinct stat blocks: {names}",
            output_location=location,
        )
    ]


@register_check("combat-generator/stat-block-refs-on-enemies-line", "combat-generator")
def check_enemies_carry_stat_block_reference(artifact: str) -> List[Finding]:
    """Every creature on the `Enemies:` line carries a `{monster:Name}` token
    or a stat-block link; a bare name is a filing defect
    (`combat-generator/SKILL.md` — "a bare creature name is a filing defect")."""
    location = "> [!encounter-meta] block, `Enemies:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line = _meta_line_value(block, "Enemies")
    if line is None:
        return []
    bare = [c.name for c in _parse_creatures(line) if c.form == "bare"]
    if not bare:
        return []
    return [
        Finding(
            check_id="combat-generator/stat-block-refs-on-enemies-line",
            expected="every creature carries `{monster:Name}` or a stat-block link",
            actual="bare creature name(s): " + ", ".join(bare),
            output_location=location,
        )
    ]


_SPOTLIGHT_PALETTE = ("aimed", "puzzle", "steamroll", "plain", "curveball")
_TARGETED_TEXTURES = ("aimed", "puzzle")
# The texture is the leading word of the Spotlight value.
_TEXTURE_RE = re.compile(r"^\s*([A-Za-z]+)")
# A target clause names whom: `at Vex` / `for Vex` (a capitalised name).
_TARGET_RE = re.compile(r"\b(?:at|for)\s+[A-Z][A-Za-z'\-]+")


def _spotlight_texture(block: str):
    line = _meta_line_value(block, "Spotlight")
    if line is None:
        return None, None
    m = _TEXTURE_RE.match(line)
    return line, (m.group(1).lower() if m else None)


@register_check("combat-generator/spotlight-texture-in-palette", "combat-generator")
def check_spotlight_texture_in_palette(artifact: str) -> List[Finding]:
    """The `Spotlight:` line names a texture from the palette — aimed /
    puzzle / steamroll / plain / curveball (`combat-generator/SKILL.md` —
    "aimed / puzzle / steamroll / plain / curveball")."""
    location = "> [!encounter-meta] block, `Spotlight:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line, texture = _spotlight_texture(block)
    if line is None:
        return []
    if texture in _SPOTLIGHT_PALETTE:
        return []
    return [
        Finding(
            check_id="combat-generator/spotlight-texture-in-palette",
            expected="a texture from {" + ", ".join(_SPOTLIGHT_PALETTE) + "}",
            actual=f"leading texture {texture!r}" if texture else "no texture word",
            output_location=location,
        )
    ]


@register_check("combat-generator/targeted-spotlight-names-target-and-staging", "combat-generator")
def check_targeted_spotlight_names_target_and_staging(artifact: str) -> List[Finding]:
    """An aimed or puzzle fight names *whom* it shoots at and carries a
    staging clause (`combat-generator/SKILL.md` — "if aimed or puzzle, who it
    shoots at and the staging that fires their ability"). Structural presence
    only — that
    the staging actually *fires* the ability is a judgement facet, not checked
    here. Non-targeted textures (steamroll/plain/curveball) impose no such
    requirement, so they contribute no finding."""
    location = "> [!encounter-meta] block, `Spotlight:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    line, texture = _spotlight_texture(block)
    if line is None or texture not in _TARGETED_TEXTURES:
        return []
    missing = []
    if not _TARGET_RE.search(line):
        missing.append("a target clause naming whom (`at <Name>`)")
    if "—" not in line:
        missing.append("a staging clause (em-dash — the staging that fires their ability)")
    if not missing:
        return []
    return [
        Finding(
            check_id="combat-generator/targeted-spotlight-names-target-and-staging",
            expected=f"an {texture} spotlight names a target and a staging clause",
            actual="missing " + " and ".join(missing),
            output_location=location,
        )
    ]


@register_check("combat-generator/floating-terrain-roles", "combat-generator")
def check_floating_terrain_roles(artifact: str) -> List[Finding]:
    """A floating fight's `Terrain:` line is role-form: `needs:` followed by two
    or more terrain roles (`lib/encounter-meta-format.md` — "its `Terrain:` line
    carries the terrain *roles* the fight needs"). Requested only when the fight
    being checked is the floating form — a pinned fight's concrete terrain is a
    different promise, graded by no mechanical rule. Returns [] when the block or
    the line is absent; the required-lines check owns presence."""
    location = "> [!encounter-meta] block, `Terrain:` line"
    block = _extract_encounter_meta_block(artifact)
    if block is None:
        return []
    value = _meta_line_value(block, "Terrain")
    if value is None:
        return []
    m = re.match(r"needs\s*[:\u2014-]\s*(?P<roles>.+)$", value, re.IGNORECASE)
    if m is None:
        return [
            Finding(
                check_id="combat-generator/floating-terrain-roles",
                expected="a role-form Terrain line: `needs:` plus two or more terrain roles",
                actual=f"Terrain line is not role-form: {value!r}",
                output_location=location,
            )
        ]
    roles = [r.strip() for r in re.split(r"[,;\u00b7]", m.group("roles")) if r.strip()]
    if len(roles) >= 2:
        return []
    return [
        Finding(
            check_id="combat-generator/floating-terrain-roles",
            expected="two or more terrain roles after `needs:`",
            actual=f"{len(roles)} role(s) found: {m.group('roles')!r}",
            output_location=location,
        )
    ]
