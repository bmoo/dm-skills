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
# Finding — the verdict shape the three generator check suites inherit verbatim.
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
# Most checks need only the artifact (``str -> list[Finding]``). A few —
# dungeon's roster-dependent staging checks need external context the
# artifact alone cannot carry (the party's flagged-ability roster, whether the DM
# overrode the default scale). Those take a second argument, an optional context
# dict (``(str, dict | None) -> list[Finding]``). The registry records which shape
# a check has (``takes_context``) so ``run_checks`` dispatches each correctly; a
# context-free check never sees the context, a context-taking one always does.
Context = Optional[Dict[str, Any]]
CheckFn = Callable[..., List[Finding]]


# --------------------------------------------------------------------------- #
# Registry — the extension point later checks grow.
# --------------------------------------------------------------------------- #
#
# Each check is registered under its check id and tagged with the producing
# skill that owns it. Adding a check is a one-function, one-registration
# operation: write ``def _my_check(artifact) -> list[Finding]`` and decorate it
# with ``@register_check("build-session/enemies-line-arithmetic",
# "build-session")``. ``run_checks`` then selects it whenever a caller
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

    ``check_id`` is the promise's inventory slug, ``<qualifier>/<stem>``, and its
    qualifier IS ``producing_skill`` — that is the whole reason the shipping skill
    folder was chosen as the qualifier. Registering a check whose qualifier names
    a different skill (or an id carrying no qualifier at all) raises HERE, at
    import time, so a misfiled check is impossible rather than merely unlikely.

    ``takes_context`` declares the check's shape. It defaults to ``False`` — a
    context-free ``str -> list[Finding]`` check, which is every combat check and
    most dungeon checks. Pass ``takes_context=True`` for a check whose signature
    is ``(str, dict | None) -> list[Finding]`` because it needs the external
    context (the roster, the scale-override flag) that the staging checks
    require.
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
        producing_skill: which skill produced the output — one of
            ``"build-session"``, ``"build-session"``, ``"build-session"``.
            Only checks owned by this skill may be requested, so a caller applies
            only its own skill's rubric subset (spec user story 17).
        checks: the rubric subset — the list of check ids to apply.
        context: optional external data a roster-dependent check needs and the
            artifact text cannot carry — e.g.
            ``{"roster": [{"pc": "Vex", "flagged": ["Sentinel reach"]}, ...],
            "scale_overridden": False}``. This stays PURE — ``context`` is data
            handed in, never I/O. A context-free check (every combat check, most
            dungeon checks) ignores it entirely; only checks registered with
            ``takes_context=True`` (dungeon's staging checks) receive it. Defaults to
            ``None`` so every pre-existing 3-arg call is unchanged.

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
            it needs (see the staging checks) — the loop refuses to fake a verdict it cannot
            reach.
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
# From docs/eval-assertion-inventory.md: the `> [!encounter-meta]` block must
# carry its six required lines — Party, Enemies, Budget, Terrain, Spotlight,
# Objective (Note optional). The block spec lives in the format doc the block
# travels on (`build-session/session-page-format.md` — "Note is optional"),
# which the fight procedure's *Filing format* section cites rather than
# restates.
#
# The list below stays a **literal**: this directory materialises into every
# consumer through a symlink and must not read the maintenance docs at run time.
# `lib/encounter_meta_spec.py` is what holds it to the spec — a maintainer-side
# test asserting this tuple equals the labels the shipped section declares.
#
# This one check proves the whole path end to end.  extends the same registry
# with the rest of the fight procedure's mechanical rows.

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


@register_check("build-session/encounter-meta-required-lines", "build-session")
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
                check_id="build-session/encounter-meta-required-lines",
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
            check_id="build-session/encounter-meta-required-lines",
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


@register_check("build-session/enemies-line-arithmetic", "build-session")
def check_enemies_line_arithmetic(artifact: str) -> List[Finding]:
    """On the `Enemies:` line, Σ(count × per-creature XP) equals the stated
    total (`build-session/session-page-format.md` — "each creature × count with
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
            check_id="build-session/enemies-line-arithmetic",
            expected=f"Σ(count × XP) = {computed} ({terms})",
            actual=f"stated total {stated}",
            output_location=location,
        )
    ]


# The XP-budget-per-character table, transcribed from
# `build-session/xp-budget.md` — "XP Budget per Character" (SRD 5.2
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


@register_check("build-session/budget-line-arithmetic", "build-session")
def check_budget_line_arithmetic(artifact: str) -> List[Finding]:
    """The `Budget:` line's arithmetic holds — per-char × N = budget, and
    spent ≤ budget (`build-session/session-page-format.md` — "<per-char> × <N> =
    **<budget>**"; `build-session/combat.md` — "multiply by party size"). The two are independent
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
                check_id="build-session/budget-line-arithmetic",
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
                    check_id="build-session/budget-line-arithmetic",
                    expected=f"spent ≤ budget ({budget})",
                    actual=f"spent {spent} exceeds budget by {spent - budget}",
                    output_location=location,
                )
            )
    return findings


@register_check("build-session/per-char-matches-budget-table", "build-session")
def check_per_char_matches_budget_table(artifact: str) -> List[Finding]:
    """The per-char figure matches the SRD 5.2 budget table for that level ×
    difficulty (`build-session/xp-budget.md` — "Cross-reference party level
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
                check_id="build-session/per-char-matches-budget-table",
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
            check_id="build-session/per-char-matches-budget-table",
            expected=f"per-char {expected} ({band}, level {level})",
            actual=f"stated per-char {perchar}",
            output_location=location,
        )
    ]


@register_check("build-session/distinct-stat-block-cap", "build-session")
def check_distinct_stat_block_cap(artifact: str) -> List[Finding]:
    """Never more than three distinct stat blocks in one encounter — the
    hard rule (`build-session/xp-budget.md` — "Never put more than **three
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
            check_id="build-session/distinct-stat-block-cap",
            expected="≤ 3 distinct stat blocks (hard rule)",
            actual=f"{len(distinct)} distinct stat blocks: {names}",
            output_location=location,
        )
    ]


@register_check("build-session/stat-block-refs-on-enemies-line", "build-session")
def check_enemies_carry_stat_block_reference(artifact: str) -> List[Finding]:
    """Every creature on the `Enemies:` line carries a `{monster:Name}` token
    or a stat-block link; a bare name is a filing defect
    (`build-session/combat.md` — "a bare creature name is a filing defect")."""
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
            check_id="build-session/stat-block-refs-on-enemies-line",
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


@register_check("build-session/spotlight-texture-in-palette", "build-session")
def check_spotlight_texture_in_palette(artifact: str) -> List[Finding]:
    """The `Spotlight:` line names a texture from the palette — aimed /
    puzzle / steamroll / plain / curveball (`build-session/combat.md` —
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
            check_id="build-session/spotlight-texture-in-palette",
            expected="a texture from {" + ", ".join(_SPOTLIGHT_PALETTE) + "}",
            actual=f"leading texture {texture!r}" if texture else "no texture word",
            output_location=location,
        )
    ]


@register_check("build-session/targeted-spotlight-names-target-and-staging", "build-session")
def check_targeted_spotlight_names_target_and_staging(artifact: str) -> List[Finding]:
    """An aimed or puzzle fight names *whom* it shoots at and carries a
    staging clause (`build-session/combat.md` — "if aimed or puzzle, who it
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
            check_id="build-session/targeted-spotlight-names-target-and-staging",
            expected=f"an {texture} spotlight names a target and a staging clause",
            actual="missing " + " and ".join(missing),
            output_location=location,
        )
    ]


# --------------------------------------------------------------------------- #
# The keyed-site procedure's checks.
# --------------------------------------------------------------------------- #
#
# THE INHERITANCE SPLIT (spec user stories 9/20). Dungeon builds each fight by
# following the fight procedure, which already self-checked that fight's
# encounter-meta block against its own checks. So the site self-check does NOT
# re-run them: the per-block
# facets (six required lines, XP arithmetic, palette texture, bare-name) arrive
# already self-checked. Dungeon checks only what the *site* owns — the facets no
# single block can see:
#   - the site STRUCTURE the edge list encodes: entrances, loops, the
#     objective's reachability, the edge grammar, the signature technique, the
#     one dungeon-wide mechanic and its box;
#   - the CROSS-FIGHT properties across the whole roster of fights: the default
#     scale's counts, the fight mix, the flagged-ability set-cover and the
#     aimed-slot balance.
# Where a cross-fight check reads a per-block field (the fight-mix check reads a
# `Budget:` difficulty *label*, the staging check reads a `Spotlight:` *target*),
# it reads the field as
# handed back — it never re-verifies that field's arithmetic. Reading a label is
# not re-grading a delegated block; that is the inheritance split, in code.


# --- The render-ready edge list: parse it into a graph, then assert. --------- #
#
# The graph-floor checks and the edge-grammar checks read the `## Edges
# (render-ready)` table, whose contract states
# (`build-session/map-render.md` — "edge ID, endpoints, and a Type column"):
# each row is an edge ID, an Endpoints cell, and a Type cell. `—` (em-dash)
# joins two interior rooms; `→` marks an edge crossing the site boundary (an
# entrance). In the Type
# cell everything before the first em-dash is `·`-separated typed tokens; prose
# follows the dash. This parser formalises that stated contract into a graph.

# READS RAW MARKDOWN, DELIBERATELY. This pattern is applied to the
# artifact's source text, never to rendered output, so it keeps matching when the
# edge table is wrapped in an HTML comment — which is how the table is filed on a
# session page, invisible to the DM but still readable by the machinery. Do not
# "fix" this to skip commented-out regions. `_parse_edge_table` and
# `_objective_node` both return nothing at all when this finds no section, so a
# comment-skipping change would silently switch off every graph-floor and
# edge-grammar check that depends on them: no error, no finding, nothing failing
# anywhere to tell you the checks stopped running.
_EDGES_SECTION_RE = re.compile(
    r"^\s*##\s+Edges\b.*?$(?P<body>.*?)(?=^\s*##\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
_TABLE_ROW_RE = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$", re.MULTILINE)
# A room ID is a capitalised token ending in digits (N1, R12); the exterior side
# of an entrance ("Surface", "Street") does not match, which is how the parser
# tells the room end of a `→` edge from the outside end.
_ROOM_ID_RE = re.compile(r"^[A-Z][A-Za-z]*\d+$")
_OBJECTIVE_TAG_RE = re.compile(r"\{\s*objective\s*\}", re.IGNORECASE)

# Edge-type vocabulary (Step 4 / map-render.md legend); membership is asserted by
# the edge-vocabulary check.
_EDGE_BASES = {"open", "door", "locked", "grate"}
_VERTICAL_SUBS = {"stairs", "shaft-chute", "ladder", "slope"}
_EDGE_MODIFIERS = {"secret", "one-way", "trap", "hazard", "up", "down"}
_VERTICAL_TOKEN_RE = re.compile(r"^vertical⟨(?P<sub>[^⟩]+)⟩$")


@dataclass(frozen=True)
class _Edge:
    edge_id: str
    a: str              # one endpoint (room id, or exterior label if boundary)
    b: str              # the other endpoint
    boundary: bool      # True if written with `→` (crosses the site boundary)
    tokens: tuple       # typed tokens before the first em-dash in the Type cell
    prose_fragments: tuple  # `·`-split fragments before the dash that carry spaces
    raw_type: str


def _split_row(row: str) -> list[str]:
    return [c.strip() for c in row.split("|")]


def _parse_edge_table(artifact: str) -> list[_Edge]:
    """Parse the `## Edges (render-ready)` table into edges. Returns [] when the
    artifact carries no such section — a missing edge list is a presence defect,
    not a graph or grammar defect, so the structural checks stay silent on it.

    **The empty return is why the raw-markdown read matters.** This parser
    is handed source text, so it finds the section whether or not the table is
    wrapped in an HTML comment, and a concealed table is checked exactly like a
    visible one. That dependence is load-bearing: teach the section regex to skip
    commented-out regions and a concealed table parses to no edges, whereupon
    every check downstream of this function reads that as "no edge list here" and
    stays quiet. Seven graph-floor and edge-grammar checks would stop running with
    nothing failing anywhere to say so."""
    sec = _EDGES_SECTION_RE.search(artifact)
    if sec is None:
        return []
    return _parse_edge_rows(sec.group("body"))


def _parse_edge_rows(body: str) -> list[_Edge]:
    """The row loop of `_parse_edge_table`, split out so a caller that located the
    section itself can reuse it — the session page nests its edge table under a
    location section rather than at the top level."""
    edges: list[_Edge] = []
    for m in _TABLE_ROW_RE.finditer(body):
        cells = [c for c in _split_row(m.group("cells")) if c != ""]
        if len(cells) < 3:
            continue
        endpoints = cells[1]
        # Header row ("Endpoints") and the `|---|` separator carry no `—`/`→`.
        boundary = "→" in endpoints
        sep = "→" if boundary else ("—" if "—" in endpoints else None)
        if sep is None:
            continue
        parts = endpoints.split(sep)
        if len(parts) != 2:
            continue
        a_raw, b_raw = parts[0].strip(), parts[1].strip()
        a = _OBJECTIVE_TAG_RE.sub("", a_raw).strip()
        b = _OBJECTIVE_TAG_RE.sub("", b_raw).strip()
        raw_type = cells[2]
        pre = raw_type.split("—", 1)[0]
        frags = [f.strip() for f in pre.split("·") if f.strip()]
        tokens = tuple(f for f in frags if " " not in f)
        prose = tuple(f for f in frags if " " in f)
        edges.append(_Edge(cells[0], a, b, boundary, tokens, prose, raw_type))
    return edges


def _objective_node(artifact: str) -> str | None:
    """The room ID tagged ``{objective}`` in the edge list, or None if untagged.
    The secret-spine and two-route checks own reachability *to* the objective;
    when no objective is marked they cannot assess it and stay silent (the DoD
    instructs the generator to tag it)."""
    sec = _EDGES_SECTION_RE.search(artifact)
    body = sec.group("body") if sec else artifact
    for m in _TABLE_ROW_RE.finditer(body):
        for cell in _split_row(m.group("cells")):
            if not _OBJECTIVE_TAG_RE.search(cell):
                continue
            # The tag rides the objective endpoint specifically — return the room
            # ID of the endpoint that carries `{objective}`, not merely the first
            # room ID in the cell.
            for endpoint in re.split(r"—|→", cell):
                if _OBJECTIVE_TAG_RE.search(endpoint):
                    cand = _OBJECTIVE_TAG_RE.sub("", endpoint).strip()
                    if _ROOM_ID_RE.match(cand):
                        return cand
    return None


def _interior_rooms(edges: list[_Edge]) -> set:
    rooms: set = set()
    for e in edges:
        if not e.boundary:
            rooms.add(e.a)
            rooms.add(e.b)
    return rooms


def _entrance_rooms(edges: list[_Edge], include_secret: bool = True) -> list[str]:
    """Room-side node of each boundary (`→`) edge — the interior end you enter
    at. ``include_secret=False`` drops entrances gated by a `secret` token, which
    is how the secret-spine check reads the graph."""
    interior = _interior_rooms(edges)
    result: list[str] = []
    for e in edges:
        if not e.boundary:
            continue
        if not include_secret and "secret" in e.tokens:
            continue
        # the room end is whichever endpoint is a known interior room (or, failing
        # that, whichever matches the room-ID shape); the other end is outside.
        room = None
        for cand in (e.a, e.b):
            if cand in interior:
                room = cand
                break
        if room is None:
            for cand in (e.a, e.b):
                if _ROOM_ID_RE.match(cand):
                    room = cand
                    break
        if room is not None:
            result.append(room)
    return result


@register_check("build-session/two-entrances", "build-session")
def check_two_entrances(artifact: str) -> List[Finding]:
    """The site has at least two entrances — boundary (`→`) edges
    (`build-session/xandering.md` — "**≥ 2 entrances.**"). The approach is
    the first strategic choice; one way in
    is a railroad."""
    location = "`## Edges (render-ready)` — boundary (`→`) edges"
    edges = _parse_edge_table(artifact)
    if not edges:
        # This check owns edge-list PRESENCE (as the required-lines check owns the
        # encounter-meta block): a missing or mis-formatted `## Edges
        # (render-ready)` table would make every other graph/grammar check silently
        # return [] — a false all-clear. It refuses that silence and fires loudly;
        # a real dungeon always has a table, so this never false-fires, and the
        # single loud finding stays singly fixable (fix the table, and the
        # graph/grammar checks can then grade it).
        return [
            Finding(
                check_id="build-session/two-entrances",
                expected="≥ 2 entrances in a `## Edges (render-ready)` table",
                actual="no parseable `## Edges (render-ready)` table found "
                "(Edge | Endpoints | Type rows, `→` marking each entrance)",
                output_location=location,
            )
        ]
    entrances = [e for e in edges if e.boundary]
    if len(entrances) >= 2:
        return []
    return [
        Finding(
            check_id="build-session/two-entrances",
            expected="≥ 2 entrances (boundary `→` edges)",
            actual=f"{len(entrances)} entrance(s): "
            + (", ".join(e.edge_id for e in entrances) or "none"),
            output_location=location,
        )
    ]


@register_check("build-session/at-least-one-loop", "build-session")
def check_at_least_one_loop(artifact: str) -> List[Finding]:
    """The interior topology carries at least one loop — it must not reduce to
    a line or a tree (`build-session/xandering.md` — "If the topology
    reduces to a line or a tree, it fails"). Detected by union-find over the
    interior (`—`) edges: an edge joining two already-connected rooms closes a
    cycle. Entrances (the loop through the surface the two-entrances check grades)
    are excluded, so this is a genuine *interior* loop, independent of them."""
    location = "`## Edges (render-ready)` — interior (`—`) topology"
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    interior = [e for e in edges if not e.boundary]
    parent: Dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    has_cycle = False
    for e in interior:
        ra, rb = find(e.a), find(e.b)
        if ra == rb:
            has_cycle = True
            break
        parent[ra] = rb
    if has_cycle:
        return []
    return [
        Finding(
            check_id="build-session/at-least-one-loop",
            expected="≥ 1 loop — the interior topology must not reduce to a tree",
            actual="no loop: every interior edge joins two disconnected rooms "
            "(the site is a line or a tree)",
            output_location=location,
        )
    ]


def _adjacency(edges: list[_Edge], drop_secret: bool) -> Dict[str, set]:
    adj: Dict[str, set] = {}
    for e in edges:
        if e.boundary:
            continue
        if drop_secret and "secret" in e.tokens:
            continue
        adj.setdefault(e.a, set()).add(e.b)
        adj.setdefault(e.b, set()).add(e.a)
    return adj


@register_check("build-session/no-secret-gated-spine", "build-session")
def check_no_secret_gated_spine(artifact: str) -> List[Finding]:
    """No secret-gated spine — with every `secret` edge removed, the objective
    is still reachable from an entrance (`build-session/xandering.md` —
    "**No secret-gated spine.**"). Secrets gate
    bonuses, never essential progress (the DMG hidden-things rule)."""
    location = "`## Edges (render-ready)` — connectivity with `secret` edges removed"
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    objective = _objective_node(artifact)
    if objective is None:
        return []
    entrances = _entrance_rooms(edges, include_secret=False)
    if not entrances:
        return []
    adj = _adjacency(edges, drop_secret=True)
    seen = set(entrances)
    stack = list(entrances)
    while stack:
        node = stack.pop()
        if node == objective:
            return []
        for nxt in adj.get(node, ()):  # noqa: E501
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    if objective in seen:
        return []
    return [
        Finding(
            check_id="build-session/no-secret-gated-spine",
            expected=f"objective {objective} reachable with every `secret` edge removed",
            actual=f"objective {objective} is unreachable once secret edges are "
            "dropped — a hidden thing gates the spine",
            output_location=location,
        )
    ]


def _max_flow_two(edges: list[_Edge], sources: list[str], sink: str) -> int:
    """Unit-capacity max-flow from a super-source over ``sources`` to ``sink``,
    capped at 2 (we only need to know whether ≥ 2 edge-disjoint routes exist).
    Each undirected interior edge is a pair of opposed unit arcs, so the residual
    method counts *edge-disjoint* routes: a corridor collapse severs both only if
    they truly share it. The super-source→entrance arcs are high-capacity, so the
    count is of routes to the objective, not of entrances."""
    SRC = "__SUPER_SOURCE__"
    cap: Dict[str, Dict[str, int]] = {}

    def add_arc(u: str, v: str, c: int) -> None:
        cap.setdefault(u, {})
        cap.setdefault(v, {})
        cap[u][v] = cap[u].get(v, 0) + c
        cap[v].setdefault(u, 0)

    for e in edges:
        if e.boundary:
            continue
        add_arc(e.a, e.b, 1)
        add_arc(e.b, e.a, 1)
    for s in set(sources):
        add_arc(SRC, s, 2)

    flow = 0
    while flow < 2:
        # BFS for an augmenting path in the residual graph.
        parent: Dict[str, str] = {SRC: SRC}
        queue = [SRC]
        while queue:
            u = queue.pop(0)
            if u == sink:
                break
            for v, c in cap.get(u, {}).items():
                if c > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        # augment by 1 along the found path
        v = sink
        while v != SRC:
            u = parent[v]
            cap[u][v] -= 1
            cap[v][u] += 1
            v = u
        flow += 1
    return flow


@register_check("build-session/objective-two-routes", "build-session")
def check_objective_two_routes(artifact: str) -> List[Finding]:
    """The objective is reachable by ≥ 2 edge-disjoint routes
    (`build-session/xandering.md` — "The objective sits deep, reachable by
    ≥ 2 routes") — no single corridor collapse severs every approach.
    Two approaches that funnel through one shared bottleneck edge to the vault
    fail this: they are one route with a fork, not two."""
    location = "`## Edges (render-ready)` — routes to the objective"
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    objective = _objective_node(artifact)
    if objective is None:
        return []
    entrances = _entrance_rooms(edges, include_secret=True)
    if not entrances:
        return []
    routes = _max_flow_two(edges, entrances, objective)
    if routes >= 2:
        return []
    return [
        Finding(
            check_id="build-session/objective-two-routes",
            expected=f"≥ 2 edge-disjoint routes to objective {objective}",
            actual=f"only {routes} independent route(s) reach {objective} — the "
            "approaches share a single bottleneck edge",
            output_location=location,
        )
    ]


_GUARDED_APPROACH_FIELD_RE = re.compile(
    r"^.*\*\*\s*Guarded approach\s*:?\s*\*\*\s*(?P<value>.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _guarded_rooms(artifact: str) -> list[str]:
    """The room IDs the header's `**Guarded approach:**` field names — the page's
    own claim that no approach to the objective is free
    (`build-session/dungeon.md` — "no approach to the objective is free").
    Returns [] when the field is absent, and equally when it is present but names
    no room ID at all ("none", "—"): the claim is what the check grades, and a
    page that makes none is not making a broken one. Prose after an em-dash is
    dropped, the same token/prose boundary the signature-technique field uses.

    IDs are picked out of the pre-em-dash region rather than required to be the
    whole of a `·`-separated token, because the habit every ablation arm wrote
    its posts in was parenthesised — "two on the front desk (M1), four on the
    upper landing (M5)". Insisting on bare tokens would leave the check dark on
    exactly the prose the defect arrived in."""
    m = _GUARDED_APPROACH_FIELD_RE.search(artifact)
    if m is None:
        return []
    value = m.group("value").split("—", 1)[0]
    return list(dict.fromkeys(re.findall(r"\b[A-Z][A-Za-z]*\d+\b", value)))


@register_check("build-session/guarded-approach-holds", "build-session")
def check_guarded_approach_holds(artifact: str) -> List[Finding]:
    """A page that claims guards interpose must not carry a route that breaks the
    claim: where the header names a guarded approach, every route from an entrance
    to the objective passes one of those rooms (`build-session/dungeon.md` —
    "every route from any entrance to the objective passes one of those rooms").
    A page states a security posture in prose and then lists a route walking
    straight past it — four of five ablation arms shipped exactly that.

    **No claim, no finding.** The claim is read from the header field, never
    inferred from where the guards stand, and that distinction is load-bearing: a
    site may hold guard posts *and* a deliberate unguarded back way, and the one
    ablation arm that got this right said so in as many words — it scoped its
    claim to the routes that do not go over the roof. Inferring the claim from the
    posts would fail that page for being correct.

    Secret ways in are counted (`include_secret=True`): a route that slips past
    the posts is the defect whether or not it is hidden — which is what separates
    this from the secret-gated-spine check, where a secret edge is the thing
    removed. And a guard standing *in* the objective room is not interposing, so
    the objective is never removed: deleting it would make itself unreachable and
    pass every page vacuously."""
    location = (
        "`## Edges (render-ready)` — routes to the objective, against the header's "
        "`**Guarded approach:**`"
    )
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    guarded = _guarded_rooms(artifact)
    if not guarded:
        return []
    objective = _objective_node(artifact)
    if objective is None:
        return []
    entrances = _entrance_rooms(edges, include_secret=True)
    if not entrances:
        return []
    blocked = set(guarded) - {objective}
    adj = _adjacency(edges, drop_secret=False)
    # BFS from every entrance that is not itself a post, never stepping into one:
    # what survives is exactly the set of rooms reachable without meeting a guard.
    parent: Dict[str, str] = {}
    queue = [room for room in dict.fromkeys(entrances) if room not in blocked]
    seen = set(queue)
    free_route = None
    while queue:
        node = queue.pop(0)
        if node == objective:
            free_route = node
            break
        for nxt in adj.get(node, ()):
            if nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            parent[nxt] = node
            queue.append(nxt)
    if free_route is None:
        return []
    path = [free_route]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    return [
        Finding(
            check_id="build-session/guarded-approach-holds",
            expected=f"every route to objective {objective} passes a guarded room "
            "(" + " · ".join(guarded) + ")",
            actual=f"a route reaches {objective} past none of them: "
            + " → ".join(reversed(path)),
            output_location=location,
        )
    ]


def _valid_edge_token(tok: str) -> bool:
    if tok in _EDGE_BASES or tok in _EDGE_MODIFIERS or tok == "vertical":
        return True
    vm = _VERTICAL_TOKEN_RE.match(tok)
    return bool(vm and vm.group("sub") in _VERTICAL_SUBS)


@register_check("build-session/edge-types-in-vocabulary", "build-session")
def check_edge_types_in_vocabulary(artifact: str) -> List[Finding]:
    """Every typed edge token is drawn from the closed vocabulary — bases
    (open/door/locked/grate/vertical⟨stairs·shaft-chute·ladder·slope⟩) plus
    modifiers (secret·one-way·trap·hazard·up/down)
    (`build-session/dungeon.md` — "every connection typed with a **base**").
    Enum
    membership only: this check grades the well-formed tokens, and leaves the
    *structure* of the Type cell (is anything before the dash prose rather than
    tokens?) to the token-strictness check — a prose fragment is that check's
    finding, not a bad enum value here."""
    location = "`## Edges (render-ready)` — Type column vocabulary"
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    offenders: list[str] = []
    for e in edges:
        for tok in e.tokens:  # tokens already exclude space-carrying (prose) fragments
            if not _valid_edge_token(tok):
                offenders.append(f"{e.edge_id}:{tok!r}")
    if not offenders:
        return []
    return [
        Finding(
            check_id="build-session/edge-types-in-vocabulary",
            expected="every edge type token drawn from the closed vocabulary",
            actual="off-vocabulary token(s): " + ", ".join(offenders),
            output_location=location,
        )
    ]


@register_check("build-session/type-column-token-strictness", "build-session")
def check_type_column_token_strictness(artifact: str) -> List[Finding]:
    """Token strictness — everything before the first em-dash in the Type
    column is `·`-separated typed tokens; prose comes only *after* the dash
    (`build-session/map-render.md` — "everything before the first em-dash
    in the Type column MUST be typed tokens"). An attribute that lives in prose
    before the dash is
    invisible to the slate — exactly how the E5 secret chute got dropped. This
    check owns the structural boundary; whether a well-formed token is in the
    vocabulary is the edge-vocabulary check's promise, not this one's."""
    location = "`## Edges (render-ready)` — Type column, pre-em-dash region"
    edges = _parse_edge_table(artifact)
    if not edges:
        return []
    offenders: list[str] = []
    for e in edges:
        for frag in e.prose_fragments:
            offenders.append(f"{e.edge_id}:{frag!r}")
    if not offenders:
        return []
    return [
        Finding(
            check_id="build-session/type-column-token-strictness",
            expected="before the first em-dash: only `·`-separated typed tokens",
            actual="prose before the em-dash (an attribute the slate can't see): "
            + ", ".join(offenders),
            output_location=location,
        )
    ]


# --- Signature technique, mechanic, and its box. ----------------------------- #

# The twelve techniques (`build-session/xandering.md` — "twelve techniques"),
# each with a distinctive matcher.
_TECHNIQUES = [
    # Each matcher accepts the current name and the pre-rename phrasing, so
    # slates generated before the technique-name rewording still resolve.
    ("Many ways in", re.compile(r"many\s+ways\s+in|multiple\s+entrances", re.IGNORECASE)),
    ("Route loops", re.compile(r"\bloops?\b", re.IGNORECASE)),
    ("Redundant level links", re.compile(r"redundant\s+level\s+links|multiple\s+level\s+connections", re.IGNORECASE)),
    ("Level-skipping links", re.compile(r"level-?skipping|discontinuous", re.IGNORECASE)),
    ("Hidden byways", re.compile(r"hidden\s+byways|unusual\s+paths|secret\s+(?:&|and)\s+unusual", re.IGNORECASE)),
    ("Pocket levels", re.compile(r"pocket\s+levels?|sub-?levels?", re.IGNORECASE)),
    ("Split levels", re.compile(r"split\s+levels?|divided\s+levels?", re.IGNORECASE)),
    ("A dungeon inside a dungeon", re.compile(r"dungeon\s+inside\s+a\s+dungeon|nested\s+dungeons?", re.IGNORECASE)),
    ("Half-flights and grades", re.compile(r"half-?flights?|elevation\s+shifts?", re.IGNORECASE)),
    ("Mid-structure arrival", re.compile(r"mid-?structure|midpoint", re.IGNORECASE)),
    ("Impossible geometry", re.compile(r"impossible\s+geometry|non-euclidean", re.IGNORECASE)),
    ("Elsewhere doors", re.compile(r"elsewhere\s+doors?|extradimensional", re.IGNORECASE)),
]
_SIGNATURE_FIELD_RE = re.compile(
    r"^.*\*\*\s*Signature technique\s*:?\s*\*\*\s*(?P<value>.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


@register_check("build-session/one-signature-technique", "build-session")
def check_one_signature_technique(artifact: str) -> List[Finding]:
    """Exactly one signature technique, drawn from the twelve
    (`build-session/xandering.md` — "The signature technique — pick exactly
    one"). One technique explored deeply beats twelve
    crammed in. Reads the header's `**Signature technique:**` field; a missing
    field is a presence defect this check stays silent on."""
    location = "package header — `**Signature technique:**`"
    m = _SIGNATURE_FIELD_RE.search(artifact)
    if m is None:
        return []
    # The technique name is the clause BEFORE the first em-dash; fiction prose
    # ("Loops — the stairwells nest two sub-levels") follows the dash and must not
    # be counted as a second technique. Same token/prose boundary the
    # token-strictness check enforces.
    value = m.group("value").split("—", 1)[0].strip()
    named = [name for name, rx in _TECHNIQUES if rx.search(value)]
    if len(named) == 1:
        return []
    if not named:
        return [
            Finding(
                check_id="build-session/one-signature-technique",
                expected="exactly one signature technique from the twelve",
                actual=f"names none of the twelve: {value!r}",
                output_location=location,
            )
        ]
    return [
        Finding(
            check_id="build-session/one-signature-technique",
            expected="exactly one signature technique from the twelve",
            actual=f"names {len(named)}: " + ", ".join(named),
            output_location=location,
        )
    ]


_MECHANIC_FIELD_RE = re.compile(
    r"^.*\*\*\s*Dungeon mechanic\s*:?\s*\*\*\s*(?P<value>.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_TRIGGER_LABEL_RE = re.compile(r"\*\*\s*Trigger(?:/Clock)?\b", re.IGNORECASE)
_EFFECT_LABEL_RE = re.compile(r"\*\*\s*Effect\b", re.IGNORECASE)
_TELLS_LABEL_RE = re.compile(r"\*\*\s*Tells\b", re.IGNORECASE)
_EXPLOIT_LABEL_RE = re.compile(r"\*\*\s*Exploit\b", re.IGNORECASE)


def _mechanic_is_vanilla(artifact: str) -> bool:
    m = _MECHANIC_FIELD_RE.search(artifact)
    return bool(m and "vanilla" in m.group("value").lower())


@register_check("build-session/one-dungeon-mechanic", "build-session")
def check_one_dungeon_mechanic(artifact: str) -> List[Finding]:
    """Exactly one dungeon-wide mechanic, or an explicit "vanilla" waiver —
    never two (`build-session/dungeon-mechanics.md` — "but never gets two:
    competing gimmicks blur both"). Counts the mechanic rules-boxes by
    their `**Trigger/Clock**` label: two boxes is two competing gimmicks; zero
    boxes is a defect unless the header waived the mechanic as vanilla."""
    location = "the dungeon mechanic's rules box"
    n_boxes = len(_TRIGGER_LABEL_RE.findall(artifact))
    vanilla = _mechanic_is_vanilla(artifact)
    if n_boxes >= 2:
        return [
            Finding(
                check_id="build-session/one-dungeon-mechanic",
                expected="exactly one dungeon-wide mechanic (or a vanilla waiver)",
                actual=f"{n_boxes} mechanic boxes — competing gimmicks blur both",
                output_location=location,
            )
        ]
    if n_boxes == 0 and not vanilla:
        return [
            Finding(
                check_id="build-session/one-dungeon-mechanic",
                expected="one dungeon-wide mechanic, or an explicit 'vanilla' waiver",
                actual="no mechanic box and no vanilla waiver",
                output_location=location,
            )
        ]
    return []


@register_check("build-session/mechanic-four-part-box", "build-session")
def check_mechanic_four_part_box(artifact: str) -> List[Finding]:
    """The mechanic ships as a four-part box — Trigger/Clock · Effect · Tells
    · Exploit (`build-session/dungeon-mechanics.md` — "the delivered
    mechanic ships as this box"). The Exploit clause is what makes the
    mechanic a toy rather than a tax. A vanilla site ships no box (that belongs to
    the one-mechanic check), so this one stays silent when there is no box."""
    location = "the dungeon mechanic's rules box"
    if not _TRIGGER_LABEL_RE.search(artifact):
        return []
    missing = []
    if not _EFFECT_LABEL_RE.search(artifact):
        missing.append("Effect")
    if not _TELLS_LABEL_RE.search(artifact):
        missing.append("Tells")
    if not _EXPLOIT_LABEL_RE.search(artifact):
        missing.append("Exploit")
    if not missing:
        return []
    return [
        Finding(
            check_id="build-session/mechanic-four-part-box",
            expected="a four-part box: Trigger/Clock · Effect · Tells · Exploit",
            actual="missing " + ", ".join(missing),
            output_location=location,
        )
    ]


@register_check("build-session/slate-picks-in-header", "build-session")
def check_slate_picks_in_header(artifact: str) -> List[Finding]:
    """Both slate picks are named in the package header — a Signature-technique
    field and a Dungeon-mechanic field (`build-session/dungeon.md` — "naming
    the one of each"). This is the PRESENCE half the two checks above delegate:
    each reads its own field and stays silent when the field is absent, so
    without this one a package that simply drops a field passes both. The picks
    land in the header whoever settled them (`build-session/dungeon.md` —
    "name both picks in the header as any run does"), so a missing field is the
    same defect in an unattended run as in an attended one."""
    location = "package header — the two slate-pick fields"
    missing = []
    if _SIGNATURE_FIELD_RE.search(artifact) is None:
        missing.append("Signature technique")
    if _MECHANIC_FIELD_RE.search(artifact) is None:
        missing.append("Dungeon mechanic")
    if not missing:
        return []
    return [
        Finding(
            check_id="build-session/slate-picks-in-header",
            expected="both slate picks named in the header: "
            "`**Signature technique:**` and `**Dungeon mechanic:**`",
            actual="no header field for " + ", ".join(missing),
            output_location=location,
        )
    ]


# --- Cross-fight facets: the scale counts, the fight mix, the roster. -------- #
#
# These read across ALL encounter-meta blocks — the caller-owned properties no
# single block can see. Reading a field off a block (its `Budget:` label, its
# `Spotlight:` target) is not re-running the fight procedure's checks on it: the
# block arrived
# self-checked by the fight procedure; the site reads what it needs and re-grades
# nothing.


def _all_encounter_meta_blocks(artifact: str) -> list[str]:
    """Every encounter-meta callout in the artifact, marker through its last
    consecutive `>` line. Combat's ``_extract_encounter_meta_block`` returns only
    the first; the dungeon cross-fight checks need them all."""
    blocks: list[str] = []
    for marker in _ENCOUNTER_META_MARKER.finditer(artifact):
        lines = artifact[marker.start():].splitlines()
        block_lines = [lines[0]]
        for line in lines[1:]:
            if line.lstrip().startswith(">"):
                block_lines.append(line)
            else:
                break
        blocks.append("\n".join(block_lines))
    return blocks


_LEVEL_HEADING_RE = re.compile(r"^\s*##\s+Level\b", re.MULTILINE | re.IGNORECASE)


def _context_scale_overridden(context: Context) -> bool:
    return bool(context and context.get("scale_overridden"))


@register_check("build-session/default-scale", "build-session", takes_context=True)
def check_default_scale(artifact: str, context: Context) -> List[Finding]:
    """The default scale holds — 6–12 keyed areas, 1–2 levels, 2–4 combats
    (`build-session/dungeon.md` — "roughly 6–12 keyed areas on one or two
    levels with 2–4 combats") — but ONLY when the DM did not override it. The
    override
    flag rides in ``context['scale_overridden']``; with no context the check
    assumes the default (an un-overridden run) and grades it. Keyed areas are the
    distinct room IDs in the edge list; combats are the encounter-meta blocks;
    levels are the `## Level` headings (a single-level site has none → 1). Each
    dimension is its own finding so a single miss is singly-fixable."""
    if _context_scale_overridden(context):
        return []  # the DM chose a non-default scale; this check does not apply
    location = "the delivered package — scale"
    edges = _parse_edge_table(artifact)
    findings: List[Finding] = []
    rooms = _interior_rooms(edges) | {
        r for e in edges for r in (e.a, e.b) if _ROOM_ID_RE.match(r)
    }
    n_rooms = len(rooms)
    if edges and not (6 <= n_rooms <= 12):
        findings.append(
            Finding(
                check_id="build-session/default-scale",
                expected="6–12 keyed areas (default scale)",
                actual=f"{n_rooms} keyed areas",
                output_location=location,
            )
        )
    n_combats = len(_all_encounter_meta_blocks(artifact))
    if not (2 <= n_combats <= 4):
        findings.append(
            Finding(
                check_id="build-session/default-scale",
                expected="2–4 combats (default scale)",
                actual=f"{n_combats} combats",
                output_location=location,
            )
        )
    n_levels = len(_LEVEL_HEADING_RE.findall(artifact)) or 1
    if not (1 <= n_levels <= 2):
        findings.append(
            Finding(
                check_id="build-session/default-scale",
                expected="1–2 levels (default scale)",
                actual=f"{n_levels} levels",
                output_location=location,
            )
        )
    return findings


_BUDGET_LABEL_RE = re.compile(r"^\s*(?P<label>[A-Za-z]+)\s*,", re.IGNORECASE)


def _fight_difficulty(block: str) -> str | None:
    line = _meta_line_value(block, "Budget")
    if line is None:
        return None
    m = _BUDGET_LABEL_RE.match(line)
    return m.group("label").capitalize() if m else None


@register_check("build-session/fight-mix", "build-session")
def check_fight_mix(artifact: str) -> List[Finding]:
    """The fight mix carries exactly one High set piece, the rest
    Low/Moderate (`build-session/dungeon.md` — "one High set piece guarding
    the objective or its exit, the rest Low/Moderate"). A cross-fight,
    caller-owned facet: it reads
    each fight's `Budget:` difficulty *label* across the whole site — it does not
    re-verify that fight's budget arithmetic (that is the fight procedure's budget
    arithmetic, inherited from its own self-check). Whether each label is a valid
    band is likewise inherited, from the fight procedure's budget-table check; this
    check owns only the count of set pieces."""
    location = "the site's fights — `Budget:` difficulty labels"
    blocks = _all_encounter_meta_blocks(artifact)
    labels = [d for d in (_fight_difficulty(b) for b in blocks) if d is not None]
    if not labels:
        return []
    highs = [d for d in labels if d == "High"]
    if len(highs) == 1:
        return []
    return [
        Finding(
            check_id="build-session/fight-mix",
            expected="exactly one High set piece, the rest Low/Moderate",
            actual=f"{len(highs)} High fights among {len(labels)}: "
            + ", ".join(labels),
            output_location=location,
        )
    ]


# The Spotlight line's target clause names whom the fight/scene shoots at.
_SPOTLIGHT_SCENE_RE = re.compile(
    r"\*\*\s*Spotlight(?:\s*\(scene\))?\s*:?\s*\*\*\s*(?P<value>.+)$",
    re.IGNORECASE | re.MULTILINE,
)
# A requested curveball counts as one aimed slot
# (`build-session/dungeon.md` — "aimed slots").
_AIMED_SLOT_TEXTURES = ("aimed", "curveball")


def _require_roster(context: Context, check_id: str) -> list:
    """Return the flagged-ability roster from context, or RAISE. A roster-
    dependent check handed no roster cannot verify its promise; the library
    refuses to fake a verdict (as it already refuses unknown/mis-scoped ids), and
    the DoD instructs the generator to always hand the roster in (dungeon Step 2
    reads it)."""
    if not context or "roster" not in context or context.get("roster") is None:
        raise ValueError(
            f"check {check_id!r} needs context['roster'] (the party's flagged-"
            f"ability roster) and none was supplied; the caller must pass "
            f"context={{'roster': [...]}} — dungeon Step 2 reads it"
        )
    return context["roster"]


def _spotlight_lines(artifact: str) -> list[str]:
    """Every Spotlight / Spotlight (scene) value in the artifact — the fight
    encounter-meta lines and any keyed-area scene lines together."""
    return [m.group("value").strip() for m in _SPOTLIGHT_SCENE_RE.finditer(artifact)]


def _flagging_pcs(roster: list) -> list[str]:
    return [entry["pc"] for entry in roster if entry.get("flagged")]


@register_check("build-session/every-flagged-pc-staged", "build-session", takes_context=True)
def check_every_flagged_pc_staged(artifact: str, context: Context) -> List[Finding]:
    """Every PC's flagged ability is staged somewhere in the site — a
    set-cover of the flagging roster (`build-session/dungeon.md` — "every
    flagged PC staged somewhere in the site"). Cross-fight and
    roster-dependent: a PC is staged if any Spotlight or Spotlight (scene) line
    names them. Needs the roster (from ``context``); raises if it is not
    supplied."""
    location = "the site's Spotlight lines vs. the flagging roster"
    roster = _require_roster(context, "build-session/every-flagged-pc-staged")
    flagging = _flagging_pcs(roster)
    if not flagging:
        return []
    staged_text = "\n".join(_spotlight_lines(artifact))
    uncovered = [
        pc for pc in flagging
        if not re.search(r"\b" + re.escape(pc) + r"\b", staged_text)
    ]
    if not uncovered:
        return []
    return [
        Finding(
            check_id="build-session/every-flagged-pc-staged",
            expected="every flagged PC's ability staged somewhere in the site",
            actual="never staged: " + ", ".join(uncovered),
            output_location=location,
        )
    ]


@register_check("build-session/aimed-slots-balanced", "build-session", takes_context=True)
def check_aimed_slots_balanced(artifact: str, context: Context) -> List[Finding]:
    """The aimed slots are balanced across the flagging roster — nobody takes
    a second while another who flagged has zero, and per-PC counts stay within one
    (`build-session/dungeon.md` — "the aimed slots balanced across the
    flagging roster"). An aimed slot is a fight whose Spotlight texture is
    `aimed` or `curveball` (a requested curveball counts as one
    aimed slot); `puzzle` stages a PC for the flagged-ability set-cover but is not
    an aimed slot for this balance. Counts the slots, not the running order — the party picks
    the route, so no room 'follows' another. Needs the roster; raises without
    it."""
    location = "the site's aimed slots per flagging PC"
    roster = _require_roster(context, "build-session/aimed-slots-balanced")
    flagging = _flagging_pcs(roster)
    if not flagging:
        return []
    counts = {pc: 0 for pc in flagging}
    for block in _all_encounter_meta_blocks(artifact):
        line, texture = _spotlight_texture(block)
        if line is None or texture not in _AIMED_SLOT_TEXTURES:
            continue
        for pc in flagging:
            if re.search(r"\b" + re.escape(pc) + r"\b", line):
                counts[pc] += 1
                break
    values = list(counts.values())
    if max(values) - min(values) <= 1:
        return []
    detail = ", ".join(f"{pc}:{n}" for pc, n in counts.items())
    return [
        Finding(
            check_id="build-session/aimed-slots-balanced",
            expected="aimed slots balanced across the flagging roster (max − min ≤ 1)",
            actual=f"unbalanced — {detail}",
            output_location=location,
        )
    ]


# --------------------------------------------------------------------------- #
# build-session's page-structural and node-deepening checks.
# --------------------------------------------------------------------------- #
#
# THE TWO-DELEGATE INHERITANCE SPLIT (spec user stories 10/20/21). build-session
# compiles a whole session page that pulls in TWO delegates' self-checked output:
#   - fights, built via the fight procedure (self-checked there), and
#   - keyed sites, built via the keyed-site procedure (self-checked against
#     its own rows) —
#     which itself already inherited combat's fights.
# So the page self-check does NOT re-run any fight- or site-owned row
# on the page. Those pieces
# arrive self-checked. build-session checks only what the WHOLE PAGE / SESSION
# owns and no single delegated block can see:
#   - the page skeleton and its ordered sections;
#   - the roster tables, the contents index, the clue-payload shapes and the slate
#     that indexes them, the Conclusion's exits;
#   - the art placement and link integrity;
#   - the cross-piece variety/balance the session owns across the whole page — the
#     spotlight-plan discipline that spans every fight and scene.
# Where a page-structural check reads a delegated block (the fight-filing check
# reads that a fight is FILED as an encounter-meta callout), it grades the block's
# PRESENCE/shape on the page, never re-grades its XP arithmetic — that arrived
# self-checked from combat. Reading a block's filing shape is not re-running
# combat's own checks; that is the inheritance split, in code — exactly as
# dungeon's cross-fight checks read a `Budget:`/`Spotlight:` field without
# re-grading it.
#
# Scope discipline (shared with /): the skeleton check owns SECTION
# presence — a missing skeleton section is its finding. Every content check reads
# within its target structure and returns [] when that structure is absent (no Key
# NPCs table, no clue payload, no Conclusion), so a missing section yields exactly
# one finding, the skeleton check's, and every finding stays singly-fixable by the
# self-heal loop.


# --- Shared page helpers. ---------------------------------------------------- #

_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$", re.MULTILINE)
_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
_ANCHOR_LINK_RE = re.compile(r"\[[^\]]+\]\(#(?P<anchor>[^)]*)\)")
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<fm>.*?)\n---\s*\n", re.DOTALL)


def _headings(artifact: str) -> list:
    """Every ATX heading as ``(level, text)`` in document order."""
    return [(len(m.group("hashes")), m.group("text").strip()) for m in _HEADING_RE.finditer(artifact)]


def _slug(text: str) -> str:
    """GitHub-style heading slug: lowercase, punctuation stripped, **each space its
    own hyphen**.

    That last part is the whole subtlety. GFM auto-identifiers and pandoc
    both map one space to one hyphen, so a heading in the library's own prescribed
    keyed style — `T1 — Gatehouse`, the spaced em dash `_KEYED_INDEX_RE` below
    expects — loses the dash as punctuation and keeps *both* surrounding spaces:
    `t1--gatehouse`. Collapsing the run instead (`\\s+` → one hyphen) invented an
    anchor neither renderer emits, which failed correct pages and, worse, passed
    pages whose links 404 on GitHub and in the site build. ` & ` is the same shape.

    Still deliberately simple in one respect: no duplicate-heading `-1` suffixes,
    so a page repeating a heading is out of scope."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\t\n\r\f\v]", " ", s)
    s = s.replace(" ", "-")
    return s


def _section_body(artifact: str, name: str) -> str | None:
    """The text under the level-2 heading ``## <name>`` up to the next `## ` (or
    EOF), or None if the page has no such section."""
    m = re.search(
        r"^##\s+" + re.escape(name) + r"\s*$(?P<body>.*?)(?=^##\s|\Z)",
        artifact,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    return m.group("body") if m else None


def _parse_table(body: str) -> list:
    """Every markdown table row in ``body`` as a list of cells, the `|---|`
    separator row dropped."""
    rows: list = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            rows.append(cells)
    return [r for r in rows if not all(set(c) <= set("-: ") and c for c in r) and any(r)]


def _key_npcs_table(artifact: str) -> list | None:
    """The Key NPCs table rows (header first), or None if the section/table is
    absent — the skeleton check owns the section's presence, so the roster checks
    stay silent."""
    body = _section_body(artifact, "Key NPCs")
    if body is None:
        return None
    rows = _parse_table(body)
    return rows or None


def _col_index(header: list, name: str) -> int | None:
    """Locate a column BY HEADER NAME, never by position — so the roster-column
    checks stay robust whether the header is the format-file's 5 columns or, under
    unenforceable/npc-roster-column-contradiction, some variant."""
    for i, c in enumerate(header):
        if c.strip().lower() == name.lower():
            return i
    return None


# --- The nine skeleton sections, present and in order. ----------------------- #

# The fixed-name skeleton sections
# (`build-session/session-page-format.md` — "Sections, in order."). The title is
# the H1; the body/location sections (§7) carry campaign-specific names and the
# lore appendix (§9) is optional, so this check grades the fixed markers' presence
# + order and requires ≥ 1 named body section between the start and the
# Conclusion. The "each filled or its gap named" half is judgement (out of scope)
# — this check does the presence/order half.
_SKELETON_FIXED_SECTIONS = [
    "Key Plot Points",
    "Preparation",
    "Key NPCs",
    "Adventure Background",
    "Beginning the Adventure",
    "Conclusion",
]


@register_check("build-session/skeleton-sections-in-order", "build-session")
def check_skeleton_sections_in_order(artifact: str) -> List[Finding]:
    """The skeleton's fixed sections are present, in order, with ≥ 1 named body
    section before the Conclusion (`build-session/session-page-format.md` —
    "Every skeleton section is filled or its gap is named on the page"). It
    owns SECTION presence for the whole page."""
    location = "the page skeleton — section headings"
    headings = _headings(artifact)
    if not any(lvl == 1 for lvl, _ in headings):
        return [Finding("build-session/skeleton-sections-in-order", "a level-1 title heading opening the page", "no `# ` title heading found", location)]
    l2 = [t for lvl, t in headings if lvl == 2]
    lower = [t.lower() for t in l2]
    positions: Dict[str, int] = {}
    missing: list = []
    for name in _SKELETON_FIXED_SECTIONS:
        try:
            positions[name] = lower.index(name.lower())
        except ValueError:
            missing.append(name)
    if missing:
        return [Finding("build-session/skeleton-sections-in-order", "the skeleton's fixed sections present (" + ", ".join(_SKELETON_FIXED_SECTIONS) + ")",
                        "missing section(s): " + ", ".join(missing), location)]
    ordered = [positions[n] for n in _SKELETON_FIXED_SECTIONS]
    if ordered != sorted(ordered):
        found_order = sorted(_SKELETON_FIXED_SECTIONS, key=lambda n: positions[n])
        return [Finding("build-session/skeleton-sections-in-order", "the skeleton sections in order: " + ", ".join(_SKELETON_FIXED_SECTIONS),
                        "out of order — found: " + ", ".join(found_order), location)]
    fixed_lower = {n.lower() for n in _SKELETON_FIXED_SECTIONS}
    body = [l2[i] for i in range(positions["Beginning the Adventure"] + 1, positions["Conclusion"])
            if l2[i].lower() not in fixed_lower]
    if not body:
        return [Finding("build-session/skeleton-sections-in-order", "≥ 1 named body/location section between Beginning the Adventure and Conclusion",
                        "no body section — the keyed play has nowhere to live", location)]
    return []


# --- The Key NPCs roster table. ---------------------------------------------- #

# THE LIBRARY CONTRADICTS ITSELF ON THIS HEADER — the inventory records it as
# unenforceable/npc-roster-column-contradiction.
# (`build-session/SKILL.md` — "the roster table in the format's shape")
# states a FOUR-column header (Name | Role | Stat Block | Location);
# (`build-session/session-page-format.md` — "one table, one row per NPC")
# states FIVE (Name | Personality | Role | Stat
# Block | Location). A regex can enforce one, not both. The header check enforces
# the FORMAT FILE's five-column header, because the format doc is the authority on
# page format. The SKILL.md
# four-column header is a KNOWN DISCREPANCY, recorded here deliberately — it is
# NOT resolved here (rewriting skill text is a separate job).
_KEY_NPCS_EXPECTED_COLS = ["Name", "Personality", "Role", "Stat Block", "Location"]


@register_check("build-session/key-npcs-header", "build-session")
def check_key_npcs_header(artifact: str) -> List[Finding]:
    """The Key NPCs header is exactly Name | Personality | Role | Stat Block |
    Location (`build-session/session-page-format.md` — "one table, one row per
    NPC or creature likely to appear"; see
    unenforceable/npc-roster-column-contradiction — the SKILL.md four-column
    header is the contradiction this check does NOT enforce)."""
    location = "the Key NPCs table header"
    rows = _key_npcs_table(artifact)
    if rows is None:
        return []
    header = rows[0]
    if header == _KEY_NPCS_EXPECTED_COLS:
        return []
    return [Finding("build-session/key-npcs-header", "Key NPCs header exactly: " + " | ".join(_KEY_NPCS_EXPECTED_COLS)
                    + " (format-file 5-column authority; see"
                    + " unenforceable/npc-roster-column-contradiction)",
                    "found: " + " | ".join(header), location)]


@register_check("build-session/role-word-count", "build-session")
def check_role_word_count(artifact: str) -> List[Finding]:
    """Every Key NPCs Role is 3–8 words (`build-session/session-page-format.md`
    — "**Role** is a short phrase (3–8 words)")."""
    location = "the Key NPCs table, Role column"
    rows = _key_npcs_table(artifact)
    if rows is None or len(rows) < 2:
        return []
    idx = _col_index(rows[0], "Role")
    if idx is None:
        return []  # the header check owns the header shape
    offenders = []
    for r in rows[1:]:
        if idx >= len(r):
            continue
        n = len(r[idx].split())
        if not (3 <= n <= 8):
            offenders.append(f"{(r[0] if r else '?')!r} ({n} words)")
    if not offenders:
        return []
    return [Finding("build-session/role-word-count", "every Role is 3–8 words", "off-range Role(s): " + ", ".join(offenders), location)]


_STATBLOCK_RESOLVABLE_RE = re.compile(r"\{monster:[^}]+\}|\[[^\]]+\]\([^)]+\)")


@register_check("build-session/stat-block-resolvable", "build-session")
def check_stat_block_resolvable(artifact: str) -> List[Finding]:
    """Every row's Stat Block is a resolvable reference — `{monster:Name}` or a
    link; the literal `N/A (non-combat)` (and a bare name) is a defect
    (`build-session/session-page-format.md` — "`N/A (non-combat)` is a
    defect")."""
    location = "the Key NPCs table, Stat Block column"
    rows = _key_npcs_table(artifact)
    if rows is None or len(rows) < 2:
        return []
    idx = _col_index(rows[0], "Stat Block")
    if idx is None:
        return []
    offenders = []
    for r in rows[1:]:
        if idx >= len(r):
            continue
        if not _STATBLOCK_RESOLVABLE_RE.search(r[idx]):
            offenders.append(f"{(r[0] if r else '?')!r}: {r[idx]!r}")
    if not offenders:
        return []
    return [Finding("build-session/stat-block-resolvable", "every Stat Block is resolvable ({monster:Name} or a link); `N/A (non-combat)` is a defect",
                    "unresolvable Stat Block(s): " + ", ".join(offenders), location)]


_LOCATION_KEY_RE = re.compile(r"\b[A-Z]\d+\b|\[[^\]]+\]\([^)]+\)")


@register_check("build-session/location-uses-page-keys", "build-session")
def check_location_uses_keys(artifact: str) -> List[Finding]:
    """PROXY — the inventory rates this "Partial". The Location column uses page
    keys (`T1`) or links to keyed sections, not prose directions
    (`build-session/session-page-format.md` — "not prose directions"). The
    defensible proxy: a cell must carry a key
    token or a markdown link; a prose-only cell is flagged. It can't judge whether
    free prose names a real direction — hence a proxy, flagged as such."""
    location = "the Key NPCs table, Location column"
    rows = _key_npcs_table(artifact)
    if rows is None or len(rows) < 2:
        return []
    idx = _col_index(rows[0], "Location")
    if idx is None:
        return []
    offenders = []
    for r in rows[1:]:
        if idx >= len(r):
            continue
        cell = r[idx]
        if cell and not _LOCATION_KEY_RE.search(cell):
            offenders.append(f"{(r[0] if r else '?')!r}: {cell!r}")
    if not offenders:
        return []
    return [Finding("build-session/location-uses-page-keys", "every Location is a page key (T1) or a link, not prose",
                    "prose Location(s): " + ", ".join(offenders), location)]


# --- The header contents index. ---------------------------------------------- #

_CONTENTS_LINE_RE = re.compile(r"^.*Contents\s*:.*$", re.MULTILINE | re.IGNORECASE)


@register_check("build-session/contents-index", "build-session")
def check_contents_index(artifact: str) -> List[Finding]:
    """The contents index is one line, 5–8 links, no nesting
    (`build-session/session-page-format.md` — "One line, no nesting — a jump
    bar, not an outline"). Grades the contents line WHEN PRESENT; whether
    a jump bar is required at all is judgement, so an absent line is not this
    check's to grade."""
    location = "the header contents index"
    m = _CONTENTS_LINE_RE.search(artifact)
    if m is None:
        return []
    n = len(_LINK_RE.findall(m.group(0)))
    if 5 <= n <= 8:
        return []
    return [Finding("build-session/contents-index", "the contents index carries 5–8 links on one line",
                    f"{n} link(s) on the contents line", location)]


# --- No empty post-play scaffolding. ----------------------------------------- #

_SCAFFOLD_RE = re.compile(
    r"^##\s+(?P<h>Recap|Notes|Session Notes|Post-Session Notes|Post-play Notes)\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


@register_check("build-session/no-empty-scaffolding", "build-session")
def check_no_empty_scaffolding(artifact: str) -> List[Finding]:
    """No empty Recap/Notes scaffolding on the page — the played-session flow
    adds the record after the table, not before
    (`build-session/session-page-format.md` — "no empty Recap/Notes sections
    waiting to be filled").
    Pure-output regex over the emitted page."""
    location = "post-play scaffolding headings"
    offenders = []
    for m in _SCAFFOLD_RE.finditer(artifact):
        body = m.group("body").strip()
        if not body or re.fullmatch(r"[-*_>\s]*", body) or re.fullmatch(r"(?is).{0,40}\b(TBD|TODO|to be filled|to come)\b.{0,40}", body):
            offenders.append(m.group("h"))
    if not offenders:
        return []
    return [Finding("build-session/no-empty-scaffolding", "no empty Recap/Notes scaffolding on an unplayed page",
                    "empty scaffolding heading(s): " + ", ".join(offenders), location)]


# --- Clue payloads and the slate that indexes them. -------------------------- #

@register_check("build-session/clue-payload-shape", "build-session")
def check_clue_payload_shape(artifact: str) -> List[Finding]:
    """Every clue payload is one block with three labeled parts — Show / They
    learn / Points at (`build-session/session-page-format.md` — "with three
    labeled parts"). A payload is
    anchored by a `**Show**` label, bounded by the next Show or the next heading;
    each must carry They learn and Points at. Self-containment is judgement — this
    check does the shape half."""
    location = "a clue payload block"
    starts = [m.start() for m in re.finditer(r"\*\*Show\b", artifact, re.IGNORECASE)]
    if not starts:
        return []
    findings = []
    for i, s in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else len(artifact)
        heading = re.search(r"^#{1,6}\s", artifact[s:nxt], re.MULTILINE)
        region = artifact[s:(s + heading.start() if heading else nxt)]
        missing = []
        if not re.search(r"\*\*They learn\b", region, re.IGNORECASE):
            missing.append("They learn")
        if not re.search(r"\*\*Points at\b", region, re.IGNORECASE):
            missing.append("Points at")
        if missing:
            findings.append(Finding("build-session/clue-payload-shape", "every clue payload carries Show / They learn / Points at",
                                    "payload missing: " + ", ".join(missing), location))
    return findings


_SLATE_HEADING_RE = re.compile(r"^#{1,6}\s+.*(Secrets|Clue slate|Clues)\b", re.MULTILINE | re.IGNORECASE)


@register_check("build-session/slate-indexes-only", "build-session")
def check_slate_indexes_only(artifact: str) -> List[Finding]:
    """The slate only indexes clues — every slate line links to a payload; no
    clue content lives solely in the slate
    (`build-session/session-page-format.md` — "**The slate is an index:**")."""
    location = "the secrets-and-clues slate"
    m = _SLATE_HEADING_RE.search(artifact)
    if m is None:
        return []
    body = artifact[m.end():]
    nxt = re.search(r"^#{1,6}\s", body, re.MULTILINE)
    if nxt:
        body = body[:nxt.start()]
    offenders = []
    for line in body.splitlines():
        s = line.strip()
        if s[:1] in ("-", "*") and s[1:].strip() and not _LINK_RE.search(s):
            offenders.append(s[:50])
    if not offenders:
        return []
    return [Finding("build-session/slate-indexes-only", "every slate line indexes a clue via a link",
                    "slate line(s) with no link to a payload: " + "; ".join(offenders), location)]


# --- The Conclusion's exits, foreshadow excluded. ---------------------------- #

_LEAD_RE = re.compile(r"Lead\s*(?:→|->)", re.IGNORECASE)
_FORESHADOW_RE = re.compile(r"\bforeshadow\b", re.IGNORECASE)


@register_check("build-session/conclusion-leads", "build-session")
def check_conclusion_leads(artifact: str) -> List[Finding]:
    """The Conclusion carries ≥ 2 live leads (`Lead →`) to other nodes
    (`build-session/session-page-format.md` — "The Conclusion leaves at least
    two live leads to other nodes")."""
    location = "the Conclusion — live leads"
    body = _section_body(artifact, "Conclusion")
    if body is None:
        return []
    n = len(_LEAD_RE.findall(body))
    if n >= 2:
        return []
    return [Finding("build-session/conclusion-leads", "the Conclusion carries ≥ 2 live leads (`Lead →`) to other nodes",
                    f"{n} lead(s) in the Conclusion", location)]


@register_check("build-session/foreshadow-not-a-lead", "build-session")
def check_foreshadow_not_a_lead(artifact: str) -> List[Finding]:
    """Foreshadow-tagged content never counts toward the exits — a line is
    never tagged both `Lead →` and foreshadow
    (`build-session/session-page-format.md` — "never counts toward the
    Conclusion's exits")."""
    location = "a lead/foreshadow tag"
    offenders = []
    for line in artifact.splitlines():
        if _LEAD_RE.search(line) and _FORESHADOW_RE.search(line):
            offenders.append(line.strip()[:60])
    if not offenders:
        return []
    return [Finding("build-session/foreshadow-not-a-lead", "foreshadow content is never also tagged `Lead →` (never counts toward the exits)",
                    "line tagged both Lead and foreshadow: " + "; ".join(offenders), location)]


# --- Every fight FILED as an encounter-meta callout (page-structural). -------- #

@register_check("build-session/fights-are-encounter-meta", "build-session")
def check_fights_are_encounter_meta(artifact: str) -> List[Finding]:
    """Every fight is filed as a `> [!encounter-meta]` block
    (`build-session/session-page-format.md` — "Every fight is an
    `> [!encounter-meta]` block"). PAGE-STRUCTURAL presence only: a fight is
    signaled by an `Enemies:` field; every such field must sit inside an
    encounter-meta callout. This does NOT re-grade the block's six lines or XP
    arithmetic — those arrive self-checked by the fight procedure, and
    re-running them is exactly what the two-delegate inheritance forbids."""
    location = "a fight block on the page"
    total = len(re.findall(r"\*\*Enemies:\*\*", artifact))
    inside = sum(len(re.findall(r"\*\*Enemies:\*\*", b)) for b in _all_encounter_meta_blocks(artifact))
    if total <= inside:
        return []
    return [Finding("build-session/fights-are-encounter-meta", "every fight is filed as a `> [!encounter-meta]` callout",
                    f"{total - inside} fight(s) carry an `Enemies:` field outside any encounter-meta callout",
                    location)]


# --- Session art. ------------------------------------------------------------ #

@register_check("build-session/art-style-declared", "build-session")
def check_art_style_declared(artifact: str) -> List[Finding]:
    """`art_style:` declared in the frontmatter
    (`build-session/session-page-format.md` — "`art_style:` declared in
    frontmatter and held across every image")."""
    location = "the page frontmatter — `art_style:`"
    m = _FRONTMATTER_RE.search(artifact)
    fm = m.group("fm") if m else ""
    if re.search(r"^\s*art_style\s*:\s*\S", fm, re.MULTILINE):
        return []
    return [Finding("build-session/art-style-declared", "`art_style:` declared in the frontmatter",
                    "no `art_style:` key in the frontmatter", location)]


_ART_MARKER_RE = re.compile(r"^\s*>\s*\[!(art|art-left|art-right)\]\s*$", re.MULTILINE)
_FLOAT_MARKER_RE = re.compile(r"^\s*>\s*\[!(art-left|art-right)\]\s*$", re.MULTILINE)
_MAP_MARKER_RE = re.compile(r"^\s*>\s*\[!map\]\s*$", re.MULTILINE)
_CALLOUT_MARKER_RE = re.compile(r"^\s*>\s*\[!")
_NODE_DIAGRAM_RE = re.compile(r"node\s+(diagram|map)", re.IGNORECASE)


def _callout_block(artifact: str, start: int) -> str:
    """The callout beginning at ``start``, its marker line through the last
    consecutive `>` quoted line."""
    lines = artifact[start:].splitlines()
    block = [lines[0]]
    for line in lines[1:]:
        if line.lstrip().startswith(">"):
            block.append(line)
        else:
            break
    return "\n".join(block)


@register_check("build-session/art-pieces", "build-session")
def check_art_pieces(artifact: str) -> List[Finding]:
    """Four narrative art pieces; the splash sits after the title/badge block
    (before the first section); the node diagram lives with the scene list, not at
    the top (`build-session/session-page-format.md` — "Every session carries
    **four narrative pieces**, regardless of length"). The node diagram is
    identified by its caption text ("node diagram"/"node map") and excluded from the
    count of four — a defensible rule; the count is the solid core, splash/node
    position are position sub-facets."""
    location = "the page art"
    callouts = [(m.start(), _callout_block(artifact, m.start())) for m in _ART_MARKER_RE.finditer(artifact)]
    if not callouts:
        return [Finding("build-session/art-pieces", "four narrative art pieces", "no art callouts on the page", location)]
    narrative = [(p, b) for p, b in callouts if not _NODE_DIAGRAM_RE.search(b)]
    node = [(p, b) for p, b in callouts if _NODE_DIAGRAM_RE.search(b)]
    findings = []
    if len(narrative) != 4:
        findings.append(Finding("build-session/art-pieces", "four narrative art pieces (the node diagram excluded)",
                                f"{len(narrative)} narrative art piece(s)", location))
    first_body = re.search(r"^##\s", artifact, re.MULTILINE)
    if narrative and first_body and min(p for p, _ in narrative) > first_body.start():
        findings.append(Finding("build-session/art-pieces", "the chapter splash sits after the title/badge block, before the first section",
                                "the first art piece appears after the first `##` section — no splash opens the page",
                                location))
    if node and first_body and min(p for p, _ in node) < first_body.start():
        findings.append(Finding("build-session/art-pieces", "the node diagram lives with the scene list, not at the top",
                                "the node diagram appears before the first `##` section", location))
    return findings


@register_check("build-session/float-before-prose", "build-session")
def check_float_before_prose(artifact: str) -> List[Finding]:
    """`art-left`/`art-right` floats sit directly before wrapping prose, never
    adjacent to another callout — a float against a sidebar strands the image beside
    empty space (`build-session/session-page-format.md` — "never adjacent to
    another callout")."""
    location = "an art-left/art-right float"
    offenders = []
    for m in _FLOAT_MARKER_RE.finditer(artifact):
        lines = artifact[m.start():].splitlines()
        i = 1
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i < len(lines) and _CALLOUT_MARKER_RE.match(lines[i]):
            offenders.append(lines[0].strip())
    if not offenders:
        return []
    return [Finding("build-session/float-before-prose", "every float sits directly before wrapping prose, never adjacent to another callout",
                    "float(s) immediately followed by another callout: " + "; ".join(offenders), location)]


@register_check("build-session/art-style-differs-from-neighbors", "build-session", takes_context=True)
def check_art_style_differs_from_neighbors(artifact: str, context: Context) -> List[Finding]:
    """This session's `art_style:` differs from every neighboring session's key
    (`build-session/session-page-format.md` — "read the neighboring sessions'
    `art_style:` keys"). Only the INEQUALITY is checkable; "vary
    widely" is judgement — unenforceable/art-styles-vary-widely — out of scope.

    takes_context: the neighbors' keys can't be read off this page. DIVERGENCE FROM
    the annotation check's raise-on-missing — neighbors legitimately may not exist
    (the first
    session in a campaign has none), so absent neighbor data → [] (the inequality is
    vacuously satisfied), NOT a raise. This is a deliberate decision, not an
    oversight: a roster is always available to a self-check (Step 3 read it) but a
    neighbor list is not."""
    location = "the page frontmatter — `art_style:` vs neighbors"
    neighbors = (context or {}).get("neighbor_art_styles") or []
    if not neighbors:
        return []
    m = _FRONTMATTER_RE.search(artifact)
    sm = re.search(r"^\s*art_style\s*:\s*(?P<v>.+?)\s*$", m.group("fm"), re.MULTILINE) if m else None
    if sm is None:
        return []  # the art-style check owns art_style presence
    style = sm.group("v").strip().strip("\"'").lower()
    clash = [n for n in neighbors if str(n).strip().strip("\"'").lower() == style]
    if not clash:
        return []
    return [Finding("build-session/art-style-differs-from-neighbors", "this session's art_style differs from every neighbor's",
                    "art_style matches neighbor(s): " + ", ".join(clash), location)]


# --- Every on-page anchor link resolves. ------------------------------------- #

@register_check("build-session/links-resolve", "build-session")
def check_links_resolve(artifact: str) -> List[Finding]:
    """Every link on the page resolves (`build-session/session-page-format.md`
    — "Every link resolves; conventions match the repo guide").

    PURE-STATIC scope: only intra-page anchor links (`](#slug)`) are checkable
    without I/O — run_checks reads nothing off disk, so a link to another FILE can't
    be resolved here (that needs the repo tree, out of the pure function's reach).
    This is the high-value pure-output slice: every on-page anchor must hit a
    heading on the same page (and an empty `](#)` target is a defect)."""
    location = "an on-page anchor link"
    slugs = {_slug(t) for _, t in _headings(artifact)}
    offenders = []
    for m in _ANCHOR_LINK_RE.finditer(artifact):
        a = m.group("anchor").strip()
        if a == "" or a not in slugs:
            offenders.append("#" + a)
    if not offenders:
        return []
    return [Finding("build-session/links-resolve", "every on-page anchor link resolves to a heading",
                    "dangling anchor link(s): " + ", ".join(offenders), location)]


# --- The keyed hotspot map (conditional). ------------------------------------ #

_KEY_HEADING_RE = re.compile(r"^#{2,6}\s+([A-Z]\d+)\b", re.MULTILINE)


@register_check("build-session/hotspot-map", "build-session")
def check_hotspot_map(artifact: str) -> List[Finding]:
    """Where a hotspot treatment exists, one labeled hotspot per key
    (`build-session/session-page-format.md` — "a keyed map embeds with a
    labeled hotspot link per key"). CONDITIONAL — a hotspot map is a
    `> [!map]` callout carrying anchor links (the clickable hotspots). A plain map
    with no links is not a hotspot treatment (the repo may have no clickable
    renderer), so this check stays silent on it; where the treatment exists, its
    hotspot
    count must equal the keyed-area count."""
    location = "the keyed hotspot map"
    findings = []
    keys = set(_KEY_HEADING_RE.findall(artifact))
    for m in _MAP_MARKER_RE.finditer(artifact):
        block = _callout_block(artifact, m.start())
        hotspots = _ANCHOR_LINK_RE.findall(block)
        if not hotspots:
            continue
        if len(hotspots) != len(keys):
            findings.append(Finding("build-session/hotspot-map", "one labeled hotspot per key on the keyed map",
                                    f"{len(hotspots)} hotspot link(s) vs {len(keys)} keyed area(s)", location))
    return findings


@register_check("build-session/keyed-site-carries-map", "build-session")
def check_keyed_site_carries_map(artifact: str) -> List[Finding]:
    """A page with keyed areas embeds its rendered map
    (`build-session/session-page-format.md` — "**A keyed site carries its map.**",
    "**embeds its rendered map**"). Required rather than polish because the
    per-key exits enumeration is abolished and the edge table is concealed
    machine state, so "**the room prose and the map are the only human-readable
    topology the site has**" — a keyed page with no map is "**silent data loss —
    a keyed dungeon the DM cannot navigate**".

    CONDITIONAL on keyed areas: a page with none carries no site to navigate and
    passes silently, so a non-dungeon session is never penalised.

    NOT the same promise as `build-session/hotspot-map`, and deliberately not
    folded into it. That check fires on a hotspot treatment that ALREADY
    EXISTS and counts its badges against the keys; it is silent on a page with no
    map at all, which is this check's entire trigger. Different trigger, different
    failure — and its unimplemented no-redundant-ASCII-duplicate clause is not
    this check's to implement. Both read the same two shapes (`_KEY_HEADING_RE`,
    `_MAP_MARKER_RE`) on purpose: one keyed-area parse, so the two can never
    disagree about what a key is."""
    check_id = "build-session/keyed-site-carries-map"
    keys = sorted(set(_KEY_HEADING_RE.findall(artifact)))
    if not keys:
        return []
    if _MAP_MARKER_RE.search(artifact) is not None:
        return []
    return [Finding(check_id, "a page with keyed areas embeds its rendered map",
                    f"{len(keys)} keyed area(s) ({', '.join(keys)}) and no `> [!map]` embed",
                    "the page — the keyed site's map")]


# --- Edges are machine state, not something the DM reads. --------------------- #

# The one comment-aware pair in this module. Every other check reads the page's
# raw markdown on purpose (see `_EDGES_SECTION_RE`); this one reads what a READER
# is left with, which is the raw text minus its well-formed HTML comments.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_COMMENT_OPENER = "<!--"

_VISIBLE_EDGES_HEADING_RE = re.compile(r"^[ \t]*#{1,6}[ \t]+Edges\b.*$", re.MULTILINE | re.IGNORECASE)
# An edge ID as the page writes it — `E1`, `E12`. The lookbehind keeps it a token
# rather than a suffix, so `TYPE5` and `#e1` anchors are not edges; keyed-area IDs
# (`T1`, `N3`) never match at all, which is the exemption, not an oversight.
_EDGE_CODE_RE = re.compile(r"(?<![\w#-])E\d{1,3}\b")


def _dm_visible_text(artifact: str) -> str:
    """``artifact`` with every well-formed HTML comment blanked out — what a DM
    reading the published page is actually shown. Newlines inside the comment are
    kept so the surviving text stays on its own lines."""
    return _HTML_COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), artifact)


@register_check("build-session/edges-not-dm-visible", "build-session")
def check_edges_not_dm_visible(artifact: str) -> List[Finding]:
    """The render-ready edge table is filed on the page but concealed, and no edge
    ID survives anywhere a DM reads (`build-session/session-page-format.md` —
    "**wrapped in an HTML comment**, so it renders to nothing and no reader ever
    sees it", "**Edge IDs appear nowhere a DM reads**"). Edges are a detail
    published adventures never print; the DM reads connectivity off the map, and
    each connection that matters is described in its room's own prose
    (`build-session/session-page-format.md` — "**The per-key exits enumeration is
    abolished, not de-coded.**").

    Pure-output negative check over the page's DM-VISIBLE text — the artifact
    minus its well-formed HTML comments — in three shapes:

      1. an **unclosed comment opener**, reported alone and first. A `<!--` with no
         `-->` conceals everything after it, so the page below it is neither
         visible nor reliably hidden and there is nothing honest to judge until it
         is closed;
      2. a **visible `Edges` heading** at any level — the table is filed, not
         deleted (`build-session/session-page-format.md` — "**stays on the page —
         never deleted**"), so a heading outside a comment means an unconcealed
         one;
      3. a **surviving edge code** in visible text, once per distinct code, in page
         order — the same finding whether it sits in a keyed area's exits, in body
         prose, in a `> [!dm-sidebar]`, or on an `> [!encounter-meta]` terrain
         line, because all four are text the DM reads. Each finding names the
         offending token.

    Keyed-area IDs are untouched (`build-session/session-page-format.md` —
    "**Keyed-area IDs are unaffected**"): they resolve visually against the hotspot
    map, so `T1` and `N3` are not edges and never match. A page with no keyed site
    carries no codes and passes silently."""
    check_id = "build-session/edges-not-dm-visible"

    stripped = _HTML_COMMENT_RE.sub("", artifact)
    if _COMMENT_OPENER in stripped:
        line = next(l for l in stripped.splitlines() if _COMMENT_OPENER in l)
        return [Finding(check_id, "every HTML comment on the page is closed",
                        "an unclosed comment opener, which hides the rest of the page: "
                        + line.strip()[:80], "the page — an unclosed HTML comment")]

    visible = _dm_visible_text(artifact)
    findings = []

    heading = _VISIBLE_EDGES_HEADING_RE.search(visible)
    if heading is not None:
        findings.append(Finding(check_id, "the render-ready edge table is concealed inside an HTML comment, never DM-visible",
                                "a DM-visible edge heading: " + heading.group(0).strip()[:80],
                                "the page — the edge table"))

    seen = set()
    for m in _EDGE_CODE_RE.finditer(visible):
        code = m.group(0)
        if code in seen:
            continue
        seen.add(code)
        line = visible[visible.rfind("\n", 0, m.start()) + 1:].split("\n", 1)[0]
        findings.append(Finding(check_id, "no edge ID appears anywhere a DM reads",
                                f"a DM-visible edge ID, {code}: " + line.strip()[:80],
                                "the page — DM-visible text"))
    return findings


# --- The transient spotlight plan and its per-beat effects. ------------------- #

_SPOTLIGHT_PLAN_HEADING_RE = re.compile(r"^#{1,6}\s+.*\bSpotlight\b.*$", re.MULTILINE | re.IGNORECASE)
_SPOTLIGHT_PLAN_LABEL_RE = re.compile(r"\*\*\s*Spotlight\s+(plan|budget|allocation|ledger)\b", re.IGNORECASE)
# Resting is expressed by ABSENCE
# (`build-session/session-page-format.md` — "**Absence is the record:**"), so a
# filed
# roster of who rests is plan state that escaped the run — never a page annotation.
_SPOTLIGHT_RESTING_LABEL_RE = re.compile(r"\*\*\s*(?:Resting|Rests|At\s+rest|Resting\s+this\s+session)\s*:?\s*\*\*", re.IGNORECASE)

# A plan filed as a TABLE need use none of the words above — the header row is what
# gives it away. Either a column literally headed for the spotlight, or the plan's
# characteristic pairing: a who-column against a beat/pillar/texture/rest column.
_PLAN_TABLE_SPOTLIGHT_COL_RE = re.compile(r"\bspotlight\b", re.IGNORECASE)
_PLAN_TABLE_WHO_COL_RE = re.compile(r"^\W*(pc|pcs|character|characters|player|players|who)\b", re.IGNORECASE)
_PLAN_TABLE_WHAT_COL_RE = re.compile(r"\b(beat|beats|pillar|pillars|texture|textures|rest|resting|legibility)\b", re.IGNORECASE)


def _table_headers(artifact: str) -> list:
    """The header-row cells of every markdown table in ``artifact`` — a `|`-row
    immediately followed by a `|---|` separator row. Used by the filed-plan check
    to recognise a
    filed spotlight-plan table by its COLUMNS, whatever its heading says."""
    lines = artifact.splitlines()
    headers = []
    for i, line in enumerate(lines[:-1]):
        s, nxt = line.strip(), lines[i + 1].strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        if not (nxt.startswith("|") and nxt.endswith("|")):
            continue
        sep = [c.strip() for c in nxt.strip("|").split("|")]
        if sep and all(c and set(c) <= set("-: ") for c in sep):
            headers.append([c.strip() for c in s.strip("|").split("|")])
    return headers


def _filed_plan_table(artifact: str) -> str | None:
    """A table header row that reads as a filed spotlight plan, or None."""
    for header in _table_headers(artifact):
        if any(_PLAN_TABLE_SPOTLIGHT_COL_RE.search(c) for c in header):
            return " | ".join(header)
        if any(_PLAN_TABLE_WHO_COL_RE.search(c) for c in header) and any(
            _PLAN_TABLE_WHAT_COL_RE.search(c) for c in header
        ):
            return " | ".join(header)
    return None


@register_check("build-session/spotlight-plan-not-filed", "build-session")
def check_spotlight_plan_not_filed(artifact: str) -> List[Finding]:
    """The spotlight plan is never filed on the page — no plan table, no
    Preparation entry (`build-session/SKILL.md` — "The spotlight plan is not
    filed on a lean-sheet run either"; `build-session/session-page-format.md` —
    "The plan itself appears nowhere on the page: no table, no Preparation
    entry"). The plan is transient prep-run state; only its per-beat EFFECTS
    (encounter-meta `Spotlight:` fields, `Spotlight (scene):` lines) land.

    Pure-output negative check over five filing shapes, widest-net first, because a
    plan can be filed without ever using the word "plan":

      1. **any heading naming the spotlight** — the page's legitimate annotations are
         inline `**Spotlight:**` / `**Spotlight (scene):**` labels inside callouts at
         the scene that stages them; no skeleton section is headed for the spotlight,
         so a `## Spotlight …` heading of any wording is a filed plan;
      2. a bold **Spotlight plan/budget/allocation/ledger** label;
      3. a **plan table**, recognised by its COLUMNS (`_filed_plan_table`) — a
         spotlight column, or a who-column paired with a beat/pillar/texture/rest
         column — so a table headed `| PC | Pillar | Beat |` is caught though it names
         the spotlight nowhere;
      4. a **Spotlight annotation inside the `## Preparation` section** — annotations
         belong at the scene that stages the beat, so a nest of them under Preparation
         is the plan re-filed as a bookmark list
         (`build-session/session-page-format.md` — "**The session spotlight plan
         is not filed here**");
      5. a bold **Resting:** roster — resting is recorded by ABSENCE
         (`build-session/session-page-format.md` — "**Absence is the record:**"),
         so a filed rest list is plan state.

    It does NOT flag the per-beat Spotlight annotations at their own scenes (the
    annotation check's concern), which carry no heading, sit in no table, and live
    outside Preparation."""
    location = "the page — a filed spotlight plan"

    def _finding(actual: str) -> List[Finding]:
        return [Finding("build-session/spotlight-plan-not-filed", "the spotlight plan is never filed on the page (no table, no Preparation entry)",
                        "a filed spotlight plan: " + actual.strip()[:80], location)]

    m = (_SPOTLIGHT_PLAN_HEADING_RE.search(artifact)
         or _SPOTLIGHT_PLAN_LABEL_RE.search(artifact)
         or _SPOTLIGHT_RESTING_LABEL_RE.search(artifact))
    if m is not None:
        return _finding(m.group(0))

    table = _filed_plan_table(artifact)
    if table is not None:
        return _finding("a plan table headed | " + table + " |")

    prep = _section_body(artifact, "Preparation")
    if prep is not None:
        annotations = _spotlight_lines(prep)
        if annotations:
            return _finding("a Spotlight annotation filed under Preparation: " + annotations[0])

    return []


_SPOTLIGHT_ANNOTATION_RE = re.compile(
    r"\*\*\s*Spotlight(?P<scene>\s*\(scene\))?\s*:\s*\*\*\s*(?P<v>.+)$", re.IGNORECASE | re.MULTILINE
)
# The one palette texture whose definition is "nobody aimed at" — see the
# absorbed exception in ``check_spotlight_annotations_name_pc``.
_UNAIMED_TEXTURE = "plain"


# --- The spotlight-coverage pre-pass: the uncovered set (NOT a verdict). ------ #

@dataclass(frozen=True)
class SpotlightCoverage:
    """What the finished page records about who got a beat — the spotlight-coverage
    pre-pass output.

    Deliberately NOT a ``Finding`` and NOT a registered check: an uncovered PC is
    **legal**. "Absence is the record: a PC named nowhere on the page was planned as
    resting" (`build-session/session-page-format.md` — "a PC named nowhere on
    the page was planned as resting"), so an uncovered PC is *either* a
    deliberate rest (correct) *or* a dropped beat (a defect), and the page alone
    cannot tell them apart. That distinction is the judgement tier's; this pre-pass
    only hands it the facts.

    Fields:
      ``covered`` — roster PCs named in at least one Spotlight annotation, in roster
        order; ``uncovered`` — the rest, the set the judge rules on;
      ``beats_per_pc`` — how many annotations name each PC, the judge's signal for
        "one PC absorbed a disproportionate share of the beats".
    """

    covered: List[str]
    uncovered: List[str]
    beats_per_pc: Dict[str, int]


def spotlight_coverage(artifact: str, roster: list) -> SpotlightCoverage:
    """The deterministic spotlight-coverage pre-pass: ``roster − PCs named in
    Spotlight annotations``
    (`build-session/SKILL.md` — "every PC is either given a beat or named as
    resting"; `build-session/spotlight-doctrine.md` — "Every PC gets a beat somewhere across a
    scenario group — in any pillar").

    Newly computable since the spotlight plan became transient: every staged beat now lands
    as its own page annotation naming its target PC, so the **covered set is
    derivable from the finished page** — the plan is no longer the only record.

    Reads the SAME lines the annotation check grades and dungeon's staging check
    covers — ``_spotlight_lines``, both the
    fight `Spotlight:` fields and the `Spotlight (scene):` sidebar lines — so the
    three never disagree about what a staged beat is.

    **The secondary-mention rule, stated rather than left implicit in a regex:** a PC
    named *anywhere* in an annotation's value counts as covered, including as a
    secondary named inside another PC's beat. Doctrine budgets "a beat somewhere
    across a scenario group — in any pillar", and a scene that reinforces one PC with
    another has staged both. Naming is the test; primacy is not.

    This is the same set-cover as dungeon's `check_every_flagged_pc_staged` over a
    different domain: that check covers the **flagging** roster inside a dungeon
    and RETURNS A FINDING because an unstaged flagged ability there is a defect
    outright; this pre-pass covers the **whole** roster across a session page and
    returns DATA, because
    resting is legal. Same extractor, different verdict authority.

    Returns a :class:`SpotlightCoverage`. Raises nothing and fails nothing.
    """
    pcs = [entry["pc"] for entry in roster]
    values = _spotlight_lines(artifact)
    beats_per_pc = {
        pc: sum(1 for v in values if re.search(r"\b" + re.escape(pc) + r"\b", v))
        for pc in pcs
    }
    covered = [pc for pc in pcs if beats_per_pc[pc] > 0]
    uncovered = [pc for pc in pcs if beats_per_pc[pc] == 0]
    return SpotlightCoverage(covered=covered, uncovered=uncovered, beats_per_pc=beats_per_pc)


@register_check("build-session/spotlight-annotations-name-pc", "build-session", takes_context=True)
def check_spotlight_annotations_name_pc(artifact: str, context: Context) -> List[Finding]:
    """Every staged beat carries its page annotation naming its target PC — an
    encounter-meta `Spotlight:` for a fight, a `Spotlight (scene):` sidebar line
    otherwise (`build-session/session-page-format.md` — "**Every staged beat
    names its target PC**"). Regex shape + a PC name
    from the roster.

    takes_context + RAISES (mirrors dungeon's staging-check `_require_roster`):
    Step 3 always
    read the roster, so a build-session self-check always has it; refusing to run
    without it beats faking a verdict. Checks that the annotation lines PRESENT on
    the page each name a roster PC — NOT completeness against the (transient) plan,
    which is trace-only — the spotlight-coverage and unplaced-beat rows own it —
    out of scope.

    THE ABSORBED EXCEPTION — the plain fight and the pocket beat. The
    encounter-meta `Spotlight:` field is a REQUIRED label on *every* fight
    (`build-session/session-page-format.md` — "Party, Enemies, Budget, Terrain,
    Spotlight, and Objective are required"), so a fight that stages no beat still
    carries one and has nothing to name — which is how the library's own doctrine
    produced a page its own gate failed. The shipped format already scopes the
    who-clause to the targeted textures
    (`build-session/session-page-format.md` — "if aimed/puzzle, who and the
    staging that fires their ability"), exactly as
    ``check_targeted_spotlight_names_target_and_staging`` above already absorbs it
    on this same field. So a FIGHT field whose leading texture is ``plain`` — the
    one palette value doctrine defines as aiming at nobody
    (`build-session/spotlight-doctrine.md` — "fiction-first, nobody aimed at. Legitimate and
    necessary") — satisfies the row, which is what a doctrinally-required plain
    fight and the method doc's pocket beat
    (`build-session/SKILL.md` — "is *not* a budgeted beat — it is unplanned
    reserve that may never fire") both are.

    NARROW BY CONSTRUCTION, so it is not an escape hatch. Only the affirmative
    ``plain`` declaration excuses: an `aimed` fight naming nobody, or any other
    unnamed value, still fires. And a `Spotlight (scene):` line is NEVER excused —
    a scene line exists only where a beat was staged
    (`build-session/session-page-format.md` — "each beat it stages appears at the
    scene that stages it"), so relabelling one ``plain`` does not rescue it. A page
    of nothing but plain fights passes here BY DESIGN: that page's uncovered set is
    ``build-session/spotlight-coverage``'s to rule on, and firing here would usurp
    its ruled legal absence (`build-session/session-page-format.md` — "a PC named
    nowhere on the page was planned as resting")."""
    location = "the page's Spotlight annotation lines vs the roster"
    roster = _require_roster(context, "build-session/spotlight-annotations-name-pc")
    pcs = [e["pc"] for e in roster]
    if not pcs:
        return []
    offenders = []
    for m in _SPOTLIGHT_ANNOTATION_RE.finditer(artifact):
        val = m.group("v")
        if any(re.search(r"\b" + re.escape(pc) + r"\b", val) for pc in pcs):
            continue
        if m.group("scene") is None:
            texture = _TEXTURE_RE.match(val)
            if texture is not None and texture.group(1).lower() == _UNAIMED_TEXTURE:
                continue
        offenders.append(val.strip()[:50])
    if not offenders:
        return []
    return [Finding("build-session/spotlight-annotations-name-pc", "every staged-beat Spotlight annotation names a target PC from the roster (a fight field declaring the `plain` texture stages no beat and is exempt)",
                    "annotation(s) naming no roster PC: " + "; ".join(offenders), location)]


@register_check("build-session/spotlight-shapes-separate", "build-session")
def check_scene_line_not_in_encounter_meta(artifact: str) -> List[Finding]:
    """The two shapes stay separate — no `Spotlight (scene):` line inside an
    encounter-meta block, so the fight-variety ledger stays fights-only
    (`build-session/session-page-format.md` — "**The two labels are
    deliberately distinct.**"). Regex-negative over each encounter-meta
    block."""
    location = "an encounter-meta block"
    n = sum(1 for b in _all_encounter_meta_blocks(artifact)
            if re.search(r"Spotlight\s*\(scene\)\s*:", b, re.IGNORECASE))
    if n == 0:
        return []
    return [Finding("build-session/spotlight-shapes-separate", "no `Spotlight (scene):` line inside an encounter-meta block (the two shapes stay separate)",
                    f"{n} encounter-meta block(s) carry a `Spotlight (scene):` line", location)]


# --- The node-deepening rows, graded over the DEEPENED-NODE artifact. --------- #
#
# build-session loads node-deepening.md at Step 3 when a location tonight's play
# needs is too thin to run cold. These two rows grade that procedure's output — a
# NODE PAGE, a different artifact from the session page the session-page rows grade. The DoD
# names which check sees which artifact.

_CLUE_WEB_HEADING_RE = re.compile(r"^(#{2,6})\s+Clue[\s-]?web\b", re.MULTILINE | re.IGNORECASE)


def _clue_web_body(artifact: str):
    m = _CLUE_WEB_HEADING_RE.search(artifact)
    if m is None:
        return None
    body = artifact[m.end():]
    nxt = re.search(r"^#{1,6}\s", body, re.MULTILINE)
    return body[:nxt.start()] if nxt else body


@register_check("build-session/clue-web-section-present", "build-session")
def check_clue_web_present(artifact: str) -> List[Finding]:
    """The clue-web section is present with its glance line, even when leads are
    few (`build-session/node-deepening.md` — "Clue-web section present with its
    glance line"). This check owns the clue-web section's PRESENCE
    on the node page (as the skeleton check owns the session page's sections), so
    the indexes-only check stays silent when it is absent."""
    location = "the node's clue-web section"
    body = _clue_web_body(artifact)
    if body is None:
        return [Finding("build-session/clue-web-section-present", "a clue-web section with its glance line", "no clue-web section found", location)]
    glance = next((s for s in (ln.strip() for ln in body.splitlines()) if s), "")
    if not glance:
        return [Finding("build-session/clue-web-section-present", "the clue-web section carries a glance line",
                        "clue-web section present but has no glance line", location)]
    return []


@register_check("build-session/clue-web-indexes-only", "build-session")
def check_clue_web_indexes_only(artifact: str) -> List[Finding]:
    """Clue content lives in the body under its own headings; the clue-web
    section only indexes (`build-session/node-deepening.md` — "the clue-web
    section only indexes it"). A payload part (Show / They learn
    / Points at) inside the clue-web section is the defect — that content belongs in
    the body, the section should carry only an index."""
    location = "the node's clue-web section"
    body = _clue_web_body(artifact)
    if body is None:
        return []  # the clue-web presence check owns presence
    if re.search(r"\*\*(Show|They learn|Points at)\b", body, re.IGNORECASE):
        return [Finding("build-session/clue-web-indexes-only", "the clue-web section only indexes; clue content lives in the body under its own headings",
                        "the clue-web section carries clue payload content (Show/They learn/Points at) instead of an index",
                        location)]
    return []


# --------------------------------------------------------------------------- #
# build-session — the Spec axis: the session brief.
# --------------------------------------------------------------------------- #
#
# Every check above grades an artifact against a LIBRARY promise. These grade it
# against TONIGHT'S CONTRACT — the session brief the DM agreed before the build
# (`skills/to-session-brief/SKILL.md` — "a published brief is in force"), handed
# in verbatim as `context["brief"]`.
#
# Three structural rules, all ruled upstream and all implemented here rather than
# trusted to the caller:
#
#   * **The library parses the brief, not the builder.** `brief_checks` turns a
#     brief into the check ids for the fields it filled — mechanical fill-in from
#     an enumerated field set, never the generator's judgement about what is worth
#     checking. A generator that writes its own acceptance criteria can write weak
#     ones and nothing downstream would notice, which is why the derivation is a
#     template application and not a decision.
#   * **One row per FILLED field.** Every check returns [] when its field is
#     absent from the brief, so silence is never a constraint
#     (`skills/build-session/SKILL.md` — "silence is never a constraint").
#   * **The brief itself is not optional.** A check asked to grade a contract it
#     was never handed raises, the same refusal `spotlight-annotations-name-pc`
#     makes without a roster. A blank FIELD is silence; a missing BRIEF is a
#     caller error, and faking a verdict on one is worse than stopping.
#
# No check here matches a *meaning*. Each matches the **named things** a field
# commits to against the **structural slot** the page format puts them in — a
# heading, the keyed index, the Features preamble, a clue payload block, the Key
# NPCs table, the Conclusion's exits, the edge table. Never anywhere-on-the-page:
# a whole-page phrase search is what makes two rows satisfiable by one sentence.

# The brief's Locked fields, in template order, mapped to the row that grades
# each. `Premise` and `Fit to established geography` are judgement-graded and
# deliberately carry no mechanical id
# (`skills/to-session-brief/SKILL.md` — "does the page enact it").
_BRIEF_FIELD_CHECKS = (
    ("introduced canon", "build-session/brief-introduced-canon"),
    ("environmental ground rules", "build-session/brief-ground-rules-stated"),
    ("npc commitments", "build-session/brief-npc-commitments"),
    ("timeline commitments", "build-session/brief-timeline-commitments"),
    ("revelation paid down", "build-session/brief-revelation-paid-down"),
    ("destination node(s)", "build-session/brief-destination-nodes"),
    ("exit edge", "build-session/brief-exit-edge"),
    ("map topology", "build-session/brief-map-topology"),
    ("not tonight", "build-session/brief-not-tonight"),
)

# `- **Field name.** value…` at the left margin. Sub-bullets are indented, which
# is how a field's own items stay part of its value instead of opening a new one.
_BRIEF_FIELD_RE = re.compile(
    r"^-\s+\*\*(?P<name>[^*]+?)\*\*\.?\s*(?P<rest>.*)$", re.MULTILINE
)
_BRIEF_NOT_TONIGHT_RE = re.compile(
    r"^#{1,6}\s+Not tonight\s*$(?P<body>.*?)(?=^#{1,6}\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
# A value that says nothing: empty, a dash, or an unfilled `<placeholder>`.
_BRIEF_BLANK_RE = re.compile(r"^(?:[-—–_.\s]*|<[^>]*>)$")


def _brief_field_name(raw: str) -> str:
    """`**Destination node(s).**` -> `destination node(s)`. Written once so the
    field key is the template's own wording lowercased, with the trailing period
    the template writes inside the bold dropped."""
    return raw.strip().rstrip(".").strip().lower()


def brief_fields(brief: str) -> Dict[str, str]:
    """Every field the brief FILLED, keyed by the template's own field name.

    Locked fields are the left-margin `- **Name.** …` bullets, each running to the
    next left-margin bullet or the next heading — so a field's indented sub-items
    (the per-NPC lines, the per-fact lines) stay part of its value. `Not tonight`
    is a section rather than a bullet and is read as one, under the key
    ``"not tonight"``.

    A field whose value is empty, a bare dash, or an unfilled `<placeholder>` is
    **not returned**: it is a field the brief did not fill, and the whole axis
    turns on absent field -> absent row. An explicit declaration ("none; all
    derived") IS a filled field — the DM wrote it — and is returned; its row then
    finds nothing named and reports nothing, which is a different thing from not
    running."""
    fields: Dict[str, str] = {}
    matches = list(_BRIEF_FIELD_RE.finditer(brief))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(brief)
        region = brief[m.start():end]
        heading = re.search(r"^#{1,6}\s", region, re.MULTILINE)
        if heading:
            region = region[:heading.start()]
        value = region[m.start("rest") - m.start():].strip()
        if _BRIEF_BLANK_RE.match(value):
            continue
        fields[_brief_field_name(m.group("name"))] = value
    section = _BRIEF_NOT_TONIGHT_RE.search(brief)
    if section:
        body = "\n".join(
            line for line in section.group("body").splitlines()
            if line.strip().startswith(("-", "*"))
        ).strip()
        if body and not _BRIEF_BLANK_RE.match(body):
            fields["not tonight"] = body
    return fields


def brief_checks(brief: str) -> List[str]:
    """The Spec-axis check ids for the fields this brief filled, in template order.

    This is the derivation, and it is deliberately a **template application**: an
    enumerated field set in, the matching ids out. The generator does not choose —
    it may not drop a check for a field the brief filled, and it may not add one
    the brief did not license (`skills/build-session/SKILL.md` — "add one the brief did not license"). Run it before drafting; the ids it returns are what Step 4
    drafts to green against and Step 6 re-runs.

    A field the brief left blank yields **no id**, which is how "silence is never
    a constraint" is enforced upstream of any check body."""
    filled = brief_fields(brief)
    aliases = {"destination nodes": "destination node(s)", "destination node": "destination node(s)"}
    for alias, canonical in aliases.items():
        if alias in filled and canonical not in filled:
            filled[canonical] = filled[alias]
    return [check for field, check in _BRIEF_FIELD_CHECKS if field in filled]


def _brief_or_raise(context: Context, check_id: str) -> str:
    """The brief body, or a stop. A Spec-axis row grades a contract, and a row
    asked to grade one it never received cannot reach a verdict."""
    brief = (context or {}).get("brief")
    if not isinstance(brief, str) or not brief.strip():
        raise ValueError(
            f"{check_id} grades the page against the session brief and was handed "
            "none; pass the brief body verbatim as context['brief']. Grading a "
            "contract you were not given is a faked verdict, so this stops instead."
        )
    return brief


def _brief_value(context: Context, field: str, check_id: str) -> str | None:
    """This check's field out of the brief, or None when the brief did not fill it.

    The distinction this function draws is the axis's whole shape — **a blank field
    is silence and yields no finding; a missing brief is a caller error and
    stops.**"""
    brief = _brief_or_raise(context, check_id)
    fields = brief_fields(brief)
    if field == "destination node(s)":
        for alias in ("destination node(s)", "destination nodes", "destination node"):
            if alias in fields:
                return fields[alias]
        return None
    return fields.get(field)


# --- The matching currency: proper-noun runs, emphasis spans, hard tokens. ---- #
#
# A brief is prose a DM wrote quickly, so the only reliable keys in it are the
# things it NAMES. Three extractors serve all nine rows.

_PROPER_RUN_RE = re.compile(r"\b[A-Z][A-Za-z]*(?:'s)?(?:\s+[A-Z][A-Za-z]*(?:'s)?)*")
# Words that open a sentence or join a clause and carry no reference. A leading
# `-ing` word is dropped too, which is what turns "Confronting Selke's syndicate"
# into the key that matters.
_RUN_STOPWORDS = frozenset("""
a an and at by for from if in into it its no not of on or per that the their them
these this those to under upon when where whether which who with without each
every one two three both all any but so then there they he she we you i as
tonight session party dm lead leads free named name only those write
""".split())


def _proper_noun_offsets(text: str) -> List[tuple]:
    """Every proper-noun run as ``(run, start_offset, end_offset)``.

    "The Grayharbour Museum of Natural History" yields "Grayharbour Museum" and
    "Natural History"; "Confronting Selke's syndicate" yields "Selke"; "At least
    one progression lead" yields nothing at all. Leading stopwords and leading
    `-ing` verbs are dropped, possessives are stripped, and a surviving run needs
    a word of four letters or more — which is what keeps "DC" and initials out.

    Both offsets are carried because two callers need different ends of the run:
    the exclusion keys need the word that **follows** it, and the locked-subject
    set needs to know whether it **opened** a sentence."""
    spans: List[tuple] = []
    seen = set()
    for match in _PROPER_RUN_RE.finditer(text):
        words = [
            (w[:-2] if w.endswith("'s") else w).rstrip("'")
            for w in match.group(0).split()
        ]
        dropped = 0
        while words and (
            words[0].lower() in _RUN_STOPWORDS or words[0].lower().endswith("ing")
        ):
            words.pop(0)
            dropped += 1
        if not words or not any(len(w) >= 4 for w in words):
            continue
        run = " ".join(words)
        if run in seen:
            continue
        seen.add(run)
        start = match.start()
        if dropped:
            offset = match.group(0).find(words[0], 0)
            start = match.start() + (offset if offset >= 0 else 0)
        spans.append((run, start, match.end()))
    return spans


def _proper_noun_spans(text: str) -> List[tuple]:
    """``(run, end_offset_in_text)`` — the exclusion keys' view of the scan."""
    return [(run, end) for run, _, end in _proper_noun_offsets(text)]


def _proper_noun_runs(text: str) -> List[str]:
    return [run for run, _ in _proper_noun_spans(text)]


_EMPHASIS_RE = re.compile(
    r"\*\*(?P<b>[^*]{1,200}?)\*\*|\*(?!\*)(?P<i>[^*]{1,200}?)\*(?!\*)"
    r"|\"(?P<q>[^\"\n]{1,200}?)\"|“(?P<c>[^”\n]{1,200}?)”"
)


def _emphasis_spans(text: str) -> List[str]:
    """Bold, italic and quoted spans, in order — how a brief marks the name of a
    thing inside a sentence about it. A span may straddle a line break, because
    the template hard-wraps at 80 columns and an italicised revelation name is
    routinely longer than what is left of the line."""
    spans: List[str] = []
    for m in _EMPHASIS_RE.finditer(text):
        value = (m.group("b") or m.group("i") or m.group("q") or m.group("c") or "").strip()
        if value and value not in spans:
            spans.append(value)
    return spans


_HARD_TOKEN_RES = (
    re.compile(r"\bDC\s*\d+", re.IGNORECASE),
    re.compile(r"\b\d+d\d+\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*(?:feet|foot|ft\.?|miles?|squares?)\b", re.IGNORECASE),
)


def _hard_tokens(text: str) -> List[str]:
    """The parts of a ground rule a page cannot paraphrase away — a DC, a die, a
    distance. Numbers are the only thing in a prose rule that survives rewording
    intact, which is why the position check reads them and not the wording."""
    tokens: List[str] = []
    for pattern in _HARD_TOKEN_RES:
        for m in pattern.finditer(text):
            token = re.sub(r"\s+", " ", m.group(0)).strip()
            if token.lower() not in [t.lower() for t in tokens]:
                tokens.append(token)
    return tokens


_NUMBER_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
    8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
    60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety", 100: "one hundred",
}
_DISTANCE_TOKEN_RE = re.compile(r"^(?P<n>\d+)\s*(?:feet|foot|ft\.?)$", re.IGNORECASE)


def _token_pattern(token: str) -> str:
    """The regex a hard token is looked for by. A distance also matches its
    spelled form — a page writing *a thirty-foot ceiling* has stated the brief's
    `30 feet` rule, and firing on that would be a finding about notation rather
    than about the contract, the same call the hour matching makes. DCs and dice
    are matched literally: nobody writes *DC twelve*."""
    distance = _DISTANCE_TOKEN_RE.match(token)
    if distance:
        n = int(distance.group("n"))
        forms = [rf"{n}\s*(?:feet|foot|ft\.?)"]
        word = _NUMBER_WORDS.get(n)
        if word:
            forms.append(rf"{word}[\s-]*(?:feet|foot|ft\.?)")
        return "(?:" + "|".join(forms) + ")"
    return re.escape(token).replace(r"\ ", r"\s+")


def _token_present(artifact: str, token: str) -> bool:
    return bool(re.search(_token_pattern(token), artifact, re.IGNORECASE))


def _contains(haystack: str, needle: str) -> bool:
    """Whitespace-normalised, case-insensitive containment — the one comparison
    every row here uses. Both sides are hard-wrapped prose, so normalising is what
    keeps the test literal instead of turning it into a pattern."""
    return re.sub(r"\s+", " ", needle).strip().lower() in re.sub(r"\s+", " ", haystack).lower()


# --- The page's structural slots. -------------------------------------------- #

_KEYED_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<key>[A-Z]{1,3}\d+)\b", re.MULTILINE)
_KEYED_INDEX_RE = re.compile(
    r"^\s*[-*]\s+\[(?P<text>[A-Z]{1,3}\d+\s*[—–-]\s*[^\]]+)\]", re.MULTILINE
)
_HEADING_TEXT_RE = re.compile(r"^#{1,6}\s+(?P<text>.+?)\s*$", re.MULTILINE)
_SUBHEADING_TEXT_RE = re.compile(r"^#{2,6}\s+(?P<text>.+?)\s*$", re.MULTILINE)
# The heading line is matched with `[^\n]*` rather than `.*`, the same call
# `_ADVENTURE_BACKGROUND_RE` makes: DOTALL is needed for the body and would let a
# `.*` heading swallow the section it is anchoring, leaving `body` empty for every
# input — which is exactly what this slot did, silently, before the expression
# was corrected.
_POTENTIAL_SCENES_RE = re.compile(
    r"^#{1,6}[ \t]+[^\n]*Potential Scenes[^\n]*\n(?P<body>.*?)(?=^#{1,6}\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


def _staging_slots(artifact: str, include_title: bool = True) -> List[str]:
    """What the page says it STAGES: its headings, its keyed index lines
    (`skills/build-session/session-page-format.md` — "the **keyed index**
    directly under the map"), and its Potential Scenes entries.

    Deliberately not the Key NPCs table and not the clue slate. The Gloamfen brief
    locks the curator as an NPC, aims its exit edge at her syndicate, and excludes
    *confronting* that syndicate — three correct lines at once — so a slot list
    reading NPC rows or lead targets would fire on a page that kept the contract
    perfectly.

    ``include_title=False`` drops the H1. The title names the **session**, not a
    place the page stages: the Gloamfen page is called *The Gloamfen Malevolence*
    while its brief excludes travelling to the Gloamfen dig, and reading the title
    as staging would fail that page for being named after its own subject."""
    heading_re = _HEADING_TEXT_RE if include_title else _SUBHEADING_TEXT_RE
    slots = [m.group("text").strip() for m in heading_re.finditer(artifact)]
    slots += [m.group("text").strip() for m in _KEYED_INDEX_RE.finditer(artifact)]
    scenes = _POTENTIAL_SCENES_RE.search(artifact)
    if scenes:
        slots += [
            line.strip().lstrip("-*").strip()
            for line in scenes.group("body").splitlines()
            if line.strip().startswith(("-", "*"))
        ]
    return [s for s in slots if s]


def _clue_payload_blocks(artifact: str) -> List[str]:
    """Each clue payload as one block — a `**Show**` label through the next Show or
    the next heading, the same bounding `clue-payload-shape` uses. This is the
    structural slot that keeps the revelation row off the premise row's prose."""
    starts = [m.start() for m in re.finditer(r"\*\*Show\b", artifact, re.IGNORECASE)]
    blocks: List[str] = []
    for i, start in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else len(artifact)
        heading = re.search(r"^#{1,6}\s", artifact[start:nxt], re.MULTILINE)
        blocks.append(artifact[start:(start + heading.start() if heading else nxt)])
    return blocks


# --- Introduced canon: the diff, and whether the page used the licence. ------- #

_CANON_STOPWORDS = frozenset("""
about after against already also always another anything because before behind
being between both cannot could during either enough every everything first from
given going having however inside instead itself least longer making might mostly
myself neither never nothing nowhere often only other others ought outside rather
really should since something sometimes still their there therefore these things
those though through under unless until using where whether which while whose
without would tonight session party record campaign
""".split())


def _distinctive_terms(text: str) -> List[str]:
    """A fact's rare words: its proper-noun runs, its hard tokens, and its long
    content words. Deliberately crude — this row never claims to know whether two
    sentences say the same thing, only whether they share the words nothing else
    on the page would use."""
    terms = list(_proper_noun_runs(text)) + _hard_tokens(text)
    for word in re.findall(r"\b[A-Za-z][a-z]{5,}\b", text):
        low = word.lower()
        if low in _CANON_STOPWORDS:
            continue
        if low not in [t.lower() for t in terms]:
            terms.append(word)
    return terms


_DECLARES_NONE_RE = re.compile(r"^\s*(?:\*\*)?none\b", re.IGNORECASE)


def _canon_facts(value: str) -> List[str]:
    """The facts an `Introduced canon` field lists — its indented sub-bullets, or
    the whole value where it wrote none.

    A field that opens by declaring none is an **answer**, not a fact — the
    template offers exactly that wording
    (`skills/to-session-brief/SKILL.md` — "none; all derived"). The field is
    filled, so the row runs, and it finds nothing to require, which is a different
    thing from the row not running at all."""
    if _DECLARES_NONE_RE.match(value):
        return []
    facts = [
        line.strip().lstrip("-*").strip()
        for line in value.splitlines()
        if line.strip().startswith(("-", "*"))
    ]
    facts = [f for f in facts if f]
    return facts or ([value.strip()] if value.strip() else [])


@register_check("build-session/brief-introduced-canon", "build-session", takes_context=True)
def check_brief_introduced_canon(artifact: str, context: Context) -> List[Finding]:
    """Every fact the brief licensed as introduced canon is new against the
    campaign canon record extract, and lands on the page
    (`skills/to-session-brief/SKILL.md` — "checked as a diff against the campaign
    canon record, which the checker is handed").

    This is the row **defined as** a diff against the **record extract**, and it
    refuses to run without it rather than grading half its own definition;
    `build-session/brief-locked-subject-canon` consumes the same extract on the
    same terms, which is what makes that row a row rather than a second channel.
    The extract is a named input on the party roster's precedent — the checker has
    no filesystem reach into the campaign record, and a durable extract handed in
    is the only way past that wall.

    **Conservative in both directions, on purpose.** The diff fires only when
    *every* distinctive term of a fact is already in the extract, so a genuinely
    new fact about an existing subject — which shares that subject's name with the
    record and nothing else — never fires. The landed half fires only when *none*
    of a fact's terms appears on the page, so a fact the page reworded passes and
    only a fact the page never touched is caught. A false finding against a
    contract the DM wrote costs more here than a missed one, and *is this the same
    fact, said differently?* is judgement."""
    check_id = "build-session/brief-introduced-canon"
    value = _brief_value(context, "introduced canon", check_id)
    if value is None:
        return []
    record = (context or {}).get("canon_record")
    if not isinstance(record, str) or not record.strip():
        raise ValueError(
            f"{check_id} is defined as a diff against the campaign canon record "
            "and was handed none; pass the record extract as "
            "context['canon_record']. It is a named input like the party roster, "
            "not something this check can go and read."
        )
    findings: List[Finding] = []
    for fact in _canon_facts(value):
        terms = _distinctive_terms(fact)
        if not terms:
            continue
        if all(_contains(record, term) for term in terms):
            findings.append(
                Finding(
                    check_id=check_id,
                    expected="every fact the brief calls introduced canon is absent from the record extract",
                    actual="the record extract already carries every distinctive term of: "
                    + fact[:90],
                    output_location="the brief's `Introduced canon` field, against the campaign canon record",
                )
            )
        if not any(_contains(artifact, term) for term in terms):
            findings.append(
                Finding(
                    check_id=check_id,
                    expected="every fact the brief licensed as introduced canon is asserted on the page",
                    actual="no term of this fact appears anywhere on the page: " + fact[:90],
                    output_location="the page, against the brief's `Introduced canon` field",
                )
            )
    return findings


# --- Environmental ground rules: the rule as stated, and where it is stated. --- #

@register_check("build-session/brief-ground-rules-stated", "build-session", takes_context=True)
def check_brief_ground_rules_stated(artifact: str, context: Context) -> List[Finding]:
    """The brief's ground rules of tonight's place are stated on the page, and
    stated before any room is keyed (`skills/to-session-brief/SKILL.md` — "The
    named ground rules of tonight's place, stated before any room or NPC is
    keyed") — the format's Features slot
    (`skills/build-session/session-page-format.md` — "a **Features** preamble for
    what holds everywhere").

    **The rule as stated, and nothing about routes.** Whether the page's own edges
    are consistent with a claim that guards interpose is
    `build-session/guarded-approach-holds`, a Standards row that needs no
    brief; the overlap between these two fields dissolved into that row instead of
    being split between them.

    The boundary is the first **keyed area** of the section the rules land in, not
    the Key NPCs table. The format mandates that table as an early skeleton
    section, so a boundary drawn there is one no format-conformant page could
    clear — and a row no correct page can satisfy is a broken row, not a strict
    one. Scoping the boundary to the rules' own section is what keeps an unrelated
    key elsewhere on the page (a tavern before the dungeon) from failing a page
    that stated its rules exactly where the format asks.

    Hard tokens are the currency because they are the part of a prose rule that
    survives rewording intact. A ground-rules block written with no DC, die or
    distance in it carries no token and goes ungraded; the row says so rather than
    guessing. The field's declared **home** is the brief's own declaration and is
    carried into the finding, never graded as a page-visible marker — the format
    has no provenance slot and minting one would be a promise this row is not
    entitled to make."""
    check_id = "build-session/brief-ground-rules-stated"
    value = _brief_value(context, "environmental ground rules", check_id)
    if value is None:
        return []
    tokens = _hard_tokens(value)
    if not tokens:
        return []
    home = "unstated"
    for candidate in ("introduced here", "node canon", "campaign reference"):
        if _contains(value, candidate):
            home = candidate
            break
    location = f"the page's Features preamble (the brief declares this rule's home: {home})"
    findings: List[Finding] = []
    missing = [t for t in tokens if not _token_present(artifact, t)]
    for token in missing:
        findings.append(
            Finding(
                check_id=check_id,
                expected=f"the brief's ground rule `{token}` stated on the page",
                actual="no such rule anywhere on the page",
                output_location=location,
            )
        )
    stated = [t for t in tokens if t not in missing]
    if not stated:
        return findings
    sections = [m.start() for m in re.finditer(r"^##\s", artifact, re.MULTILINE)]
    keys = [m.start() for m in _KEYED_HEADING_RE.finditer(artifact)]
    late = []
    for token in stated:
        m = re.search(_token_pattern(token), artifact, re.IGNORECASE)
        at = m.start() if m else len(artifact)
        # Each rule is judged against the first room keyed in the section IT is
        # stated in — per token, never against one boundary drawn from whichever
        # token happened to appear earliest. A page states some of its rules in
        # the Preparation section and the rest in the Features preamble, and one
        # early mention must not drag every later rule's boundary back to an
        # unrelated key in a different section.
        owning = max([s for s in sections if s <= at], default=0)
        after = [k for k in keys if k > owning]
        if after and at > after[0]:
            late.append(token)
    late = sorted(late)
    if late:
        findings.append(
            Finding(
                check_id=check_id,
                expected="the brief's ground rules stated before the first keyed area of their section",
                actual="stated only after a room is keyed: " + " · ".join(late),
                output_location=location,
            )
        )
    return findings


# --- NPC commitments: per named NPC, a roster row. ---------------------------- #

_BRIEF_SUBITEM_NAME_RE = re.compile(r"^[ \t]*[-*]\s+\*\*(?P<name>[^*]+?)\*\*", re.MULTILINE)


def _brief_npc_names(value: str) -> List[str]:
    """The NPCs an `NPC commitments` field names — the bold lead-in of each
    indented sub-item, falling back to the field's proper nouns where it wrote
    prose. Reading the lead-in specifically is what keeps a bolded *commitment*
    ("**neutral evil**", "**she survives the night**") from being read as a
    name."""
    names = [m.group("name").strip() for m in _BRIEF_SUBITEM_NAME_RE.finditer(value)]
    return names or _proper_noun_runs(value)


def _name_keys(name: str) -> List[str]:
    """The capitalised words in a name that could carry it on their own — how
    "Dr. Isolde Fenwick" in a brief matches "Isolde Fenwick" in a roster."""
    return [w for w in re.findall(r"\b[A-Z][A-Za-z]{3,}\b", name)]


@register_check("build-session/brief-npc-commitments", "build-session", takes_context=True)
def check_brief_npc_commitments(artifact: str, context: Context) -> List[Finding]:
    """Every NPC the brief names has a row of their own in the Key NPCs table
    (`skills/to-session-brief/SKILL.md` — "Per named NPC: identity, allegiance,
    and whether they survive").

    **Identity only.** The roster's five columns carry no allegiance and no
    survival, so a page that lists a locked NPC and then reverses their allegiance
    passes this row — that reversal is the judgement half's to catch. Adding a
    column to carry them would re-decide the shipped page format and mint a new
    promise, which is the wrong trade for a row that already catches the drop.

    **It ships precautionary and says so.** The field's ablation *leaked* — the
    withheld arm's `Exit edge` still named the curator's syndicate, so the roster
    kept her — which means the field's absence was never actually tested. It is
    retained on the precautionary reading, not on evidence.

    The *"name only those an edit could not route around"* qualifier belongs to
    the brief's own preamble and is never a criterion here: this row grades the
    names it was given and does not second-guess which of them earned a line."""
    check_id = "build-session/brief-npc-commitments"
    value = _brief_value(context, "npc commitments", check_id)
    if value is None:
        return []
    names = _brief_npc_names(value)
    if not names:
        return []
    location = "the Key NPCs table, against the brief's `NPC commitments`"
    rows = _key_npcs_table(artifact)
    if not rows:
        return [
            Finding(
                check_id=check_id,
                expected="a Key NPCs row for each NPC the brief names: " + " · ".join(names),
                actual="the page carries no Key NPCs table",
                output_location=location,
            )
        ]
    header = rows[0]
    idx = _col_index(header, "Name")
    cells = [row[idx] for row in rows[1:] if idx is not None and idx < len(row)]
    findings: List[Finding] = []
    for name in names:
        keys = _name_keys(name) or [name]
        if any(any(_contains(cell, key) for key in keys) for cell in cells):
            continue
        findings.append(
            Finding(
                check_id=check_id,
                expected=f"a Key NPCs row for {name}, whom the brief commits the night to",
                actual="no roster row names them",
                output_location=location,
            )
        )
    return findings


# --- Timeline commitments: the schedule half. --------------------------------- #

_HOUR_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
}
_NAMED_HOURS = ("midnight", "noon", "midday", "dawn", "dusk", "sunrise", "sunset", "nightfall", "daybreak")
_CLOCK_RE = re.compile(r"\b(?P<h>\d{1,2}):\d{2}")
_HOUR_RANGE_RE = re.compile(r"\b(?P<a>\d{1,2})\s*[–—-]\s*(?P<b>\d{1,2})\s*[ap]\.?\s?m\.?", re.IGNORECASE)
_BARE_HOUR_RE = re.compile(r"\b(?P<h>\d{1,2})\s*(?:o'clock|[ap]\.?\s?m\.?)", re.IGNORECASE)


def _hours(text: str) -> set:
    """Every hour a piece of text names, as ints 1–12 plus the named hours.

    Both notations count on both sides: a page writing *half past ten* has kept a
    10:30 p.m. commitment, and a check that fires on that is a check about
    punctuation rather than about the contract."""
    found = set()
    for pattern, groups in ((_CLOCK_RE, ("h",)), (_HOUR_RANGE_RE, ("a", "b")), (_BARE_HOUR_RE, ("h",))):
        for m in pattern.finditer(text):
            for g in groups:
                value = int(m.group(g))
                if 1 <= value <= 12:
                    found.add(value)
    lowered = text.lower()
    for named in _NAMED_HOURS:
        if re.search(rf"\b{named}\b", lowered):
            found.add(named)
    for value, word in _HOUR_WORDS.items():
        if re.search(rf"\b{word}\b", lowered):
            found.add(value)
    return found


def _hour_requirements(text: str) -> List[set]:
    """What a brief's timeline actually demands of a page: one requirement per
    fixed hour, and **a range as a single requirement either endpoint satisfies.**

    A range names a window, not two independent commitments — the gala that runs
    *6–8 p.m.* is one fact, and a page that says the doors close at eight has
    carried it. Splitting the range into two would fail a page for dropping the
    colour half of a window whose operative half it kept."""
    ranges = []
    consumed = set()
    for m in _HOUR_RANGE_RE.finditer(text):
        pair = {int(m.group("a")), int(m.group("b"))}
        if all(1 <= h <= 12 for h in pair):
            ranges.append(pair)
            consumed |= pair
    singles = [{h} for h in sorted(_hours(text) - consumed, key=str)]
    return ranges + singles


@register_check("build-session/brief-timeline-commitments", "build-session", takes_context=True)
def check_brief_timeline_commitments(artifact: str, context: Context) -> List[Finding]:
    """Every hour the brief's timeline fixes is named on the page too
    (`skills/to-session-brief/SKILL.md` — "The question that resolves tonight,
    either way — with the schedule as optional fill where one exists").

    **The schedule half only.** *The question resolves tonight, either way* is not
    a mechanical property and is not attempted here. A field carrying no clock at
    all yields no hour and this row stays silent on it — three of the four ablated
    situations carry none, which is the field being kind-conditional rather than
    the field failing.

    Two blind spots, named rather than smoothed: an hour word that doubles as a
    count (*one*, *two*) is cheap for a page to satisfy; and the row asserts the
    hour is *named*, never that the page hangs the right event on it."""
    check_id = "build-session/brief-timeline-commitments"
    value = _brief_value(context, "timeline commitments", check_id)
    if value is None:
        return []
    wanted = _hour_requirements(value)
    if not wanted:
        return []
    have = _hours(artifact)
    def _show(hour):
        return hour if isinstance(hour, str) else f"{hour} o'clock ({_HOUR_WORDS[hour]})"
    missing = [req for req in wanted if not (req & have)]
    if not missing:
        return []
    return [
        Finding(
            check_id=check_id,
            expected="every hour the brief's timeline fixes is named on the page",
            actual="the page names no hour for: "
            + " · ".join(" or ".join(_show(h) for h in sorted(req, key=str)) for req in missing),
            output_location="the page's schedule, against the brief's `Timeline commitments`",
        )
    ]


# --- Revelation paid down: the named state transition, read off the clue web. -- #

_TRANSITION_RE = re.compile(
    r"from\s+(?P<start>\d+)\s+of\s+(?P<n>\d+).{0,80}?to\s+(?P<end>\d+)\s+of\s+(?P=n)",
    re.IGNORECASE | re.DOTALL,
)


def _revelation_names(value: str) -> List[str]:
    """The revelation(s) the field names — its emphasis or quotation spans, minus
    the ones that are plainly a *state* rather than a name, falling back to the
    field's proper nouns. A brief that names its revelation in bare unpunctuated
    prose is therefore graded on the weaker key, and the row says so."""
    spans = [
        s for s in _emphasis_spans(value)
        if len(s.split()) >= 2
        and not re.search(r"\b\d+\s+of\s+\d+\b", s, re.IGNORECASE)
    ]
    return spans or _proper_noun_runs(value)


@register_check("build-session/brief-revelation-paid-down", "build-session", takes_context=True)
def check_brief_revelation_paid_down(artifact: str, context: Context) -> List[Finding]:
    """The revelation the brief names is paid down **through the clue web**: named
    inside at least one clue payload block
    (`skills/build-session/session-page-format.md` — "**Points at** *(behind the
    screen)* — the node or revelation the clue targets"), and where the field
    states both endpoints of its transition — *from j of n to k of n* — carried by
    at least `k − j` distinct payloads
    (`skills/to-session-brief/SKILL.md` — "Which one tonight advances, and to what
    state").

    **This grades the named state transition, not that the page is about the
    revelation.** That is what makes it independently failable from the
    rubric-graded `Premise` row, and the split is enforced by *where* it reads: a
    payload block is a structured clue, so the prose sentence that enacts the
    premise cannot also satisfy this row. A page can run the night the premise
    describes in full and leave the revelation exactly where it was — that is the
    independent failure the split buys.

    What it cannot reach is the **ledger**: whether the campaign's revelation
    tracker really stood at *j* going in is a fact about the record, not about the
    page, and the tracker is not an input."""
    check_id = "build-session/brief-revelation-paid-down"
    value = _brief_value(context, "revelation paid down", check_id)
    if value is None:
        return []
    names = _revelation_names(value)
    if not names:
        return []
    blocks = _clue_payload_blocks(artifact)
    location = "the page's clue payloads, against the brief's `Revelation paid down`"
    transition = _TRANSITION_RE.search(re.sub(r"\s+", " ", value))
    required = 1
    if transition:
        required = max(1, int(transition.group("end")) - int(transition.group("start")))
    findings: List[Finding] = []
    for name in names:
        # A payload carries the revelation when it names it, or when it says the
        # same thing in its own words — every distinctive term of the revelation
        # inside one block. Pages rephrase a revelation's title routinely ("the
        # papering revelation"); insisting on the brief's exact string would make
        # this a check about wording rather than about the transition.
        terms = _distinctive_terms(name)
        carrying = [
            b for b in blocks
            if _contains(b, name) or (terms and all(_contains(b, t) for t in terms))
        ]
        if len(carrying) >= required:
            continue
        findings.append(
            Finding(
                check_id=check_id,
                expected=f"{required} clue payload(s) naming the revelation the brief pays down: " + name[:70],
                actual=f"{len(carrying)} payload(s) name it — the page does not move it to the state the brief fixed",
                output_location=location,
            )
        )
    return findings


# --- Destination node(s): a place the page builds, not a place it mentions. ---- #

_LINK_TARGET_RE = re.compile(r"\]\(\s*(?P<target>[^)\s]+)")


def _link_basenames(text: str) -> List[str]:
    names = []
    for m in _LINK_TARGET_RE.finditer(text):
        target = m.group("target").split("#")[0]
        if not target:
            continue
        base = target.rsplit("/", 1)[-1]
        base = re.sub(r"\.(md|markdown|html)$", "", base, flags=re.IGNORECASE)
        if base and base not in names:
            names.append(base)
    return names


@register_check("build-session/brief-destination-nodes", "build-session", takes_context=True)
def check_brief_destination_nodes(artifact: str, context: Context) -> List[Finding]:
    """Every destination the brief aims the session at is **named on the page**
    (`skills/to-session-brief/SKILL.md` — "Where the session is aimed. Earlier
    leads already point into these").

    **This row reads the whole page, and that is a deliberate weakening made
    against evidence.** It was written to read the page's structural slots —
    headings, keyed index, link targets — and three of the five frozen Gloamfen
    arms failed it while building exactly the right place: they title the section
    *"Inside the Museum After Dark"* and carry the node's full name only in the
    prose and the node diagram. A row that fires on three correct pages is a row
    about naming conventions, not about aim, so it reads the page instead. What it
    still catches is the failure the brief exists for: a page that re-anchored on a
    different conceit does not name the destination anywhere.

    The cost is stated rather than hidden: a premise sentence that names the
    destination satisfies this row too. That overlap is not one of the two pairs
    Implementation Decision 5 rules on, and the page it lets through — one that
    names the node in its premise and builds somewhere else — is a page the
    rubric-graded `Premise` row is already positioned to fail.

    **A destination is one name, and its proper-noun runs are alternatives rather
    than requirements.** "The Grayharbour Museum of Natural History" breaks into
    two runs on the lowercase *of*; demanding both would fail a page that named
    the place perfectly well. Where the brief links the node's own page, that
    link's basename is a further key.

    `Node cluster in reach` is **not** a row here: the field was cut from the
    template outright, so there is no field to grade."""
    check_id = "build-session/brief-destination-nodes"
    value = _brief_value(context, "destination node(s)", check_id)
    if value is None:
        return []
    named: List[tuple] = []
    for m in _LINK_RE.finditer(value):
        text = m.group(0)
        label = re.match(r"\[(?P<t>[^\]]*)\]", text)
        target = _link_basenames(text)
        named.append(((label.group("t") if label else text), target[0] if target else None))
    for span in _emphasis_spans(value):
        named.append((span, None))
    if not named:
        named = [(run, None) for run in _proper_noun_runs(value)]
    page_links = _link_basenames(artifact)
    findings: List[Finding] = []
    for name, basename in named:
        keys = _proper_noun_runs(name) or [name.strip()]
        if any(_contains(artifact, key) for key in keys):
            continue
        if basename and any(_contains(link, basename) for link in page_links):
            continue
        findings.append(
            Finding(
                check_id=check_id,
                expected=f"the destination `{name.strip()[:60]}` named on the page — it is where the session is aimed",
                actual="the page names it nowhere, and links to no node page carrying it",
                output_location="the page, against the brief's `Destination node(s)`",
            )
        )
    return findings


# --- Exit edge: which node a lead actually reaches. --------------------------- #

@register_check("build-session/brief-exit-edge", "build-session", takes_context=True)
def check_brief_exit_edge(artifact: str, context: Context) -> List[Finding]:
    """At least one `Lead →` in the Conclusion names something the brief's `Exit
    edge` field names (`skills/to-session-brief/SKILL.md` — "Where the party can
    leave toward, per `seed-clues` Step 5";
    `skills/build-session/session-page-format.md` — "at least two live leads into
    the clue web toward other nodes, with no steer").

    This is the half the library has never had. `build-session/conclusion-leads`
    counts the exits and never asks **which node any of them reaches**, and
    `seed-clues` Step 5's cluster-level exit check exists as prose and is
    implemented nowhere — so an exit edge has been *counted but never named* since
    the checker was written.

    It asserts the named target is reachable from the page — that a lead points at
    it — never that the lead leaves the cluster, which needs the clue web and
    belongs to `seed-clues/cluster-has-exit-edge`. A field naming no proper noun at
    all ("any progression lead out") leaves nothing to look for and the row stays
    silent."""
    check_id = "build-session/brief-exit-edge"
    value = _brief_value(context, "exit edge", check_id)
    if value is None:
        return []
    wanted = _proper_noun_runs(value)
    if not wanted:
        return []
    body = _section_body(artifact, "Conclusion")
    location = "the Conclusion's `Lead →` lines, against the brief's `Exit edge`"
    if body is None:
        return [
            Finding(
                check_id=check_id,
                expected="a Conclusion lead naming the exit the brief fixed: " + " · ".join(wanted),
                actual="the page carries no Conclusion",
                output_location=location,
            )
        ]
    leads = [line for line in body.splitlines() if _LEAD_RE.search(line)]
    joined = " ".join(leads)
    if any(_contains(joined, run) for run in wanted):
        return []
    return [
        Finding(
            check_id=check_id,
            expected="a Conclusion `Lead →` naming where the brief fixed the exit: " + " · ".join(wanted),
            actual=f"{len(leads)} lead(s) in the Conclusion, none of them naming it",
            output_location=location,
        )
    ]


# --- Map topology: the shape, in the page's own edge table. ------------------- #

# The brief side's twin of `_EDGES_SECTION_RE`, at any heading level, and it
# READS RAW MARKDOWN for the same deliberate reason: a session page files
# its edge table inside an HTML comment so no DM ever reads it, and this pattern
# matches inside the comment because it is applied to source text. Never narrow it
# to skip commented-out regions. `check_brief_map_topology` returns [] when this
# finds no section, so that change would take the topology check dark — a passing
# verdict on every page, indistinguishable from a page that genuinely has no shape
# to check, with no test or error anywhere reporting the loss.
_ANY_LEVEL_EDGES_RE = re.compile(
    r"^\s*#{2,6}\s+Edges\b.*?$(?P<body>.*?)(?=^\s*#{1,6}\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
_COUNT_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_ENTRANCE_COUNT_RE = re.compile(
    r"\b(?P<n>\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(?:\w+\s+){0,2}?(?:entrances?|entries|ways?\s+in)\b",
    re.IGNORECASE,
)
_VERTICAL_WORDS = re.compile(
    r"\b(floors?|levels?|storeys?|stories|basements?|cellars?|attics?|"
    r"vertical|upper|lower|below|above|shafts?|stairs?|towers?)\b",
    re.IGNORECASE,
)


@register_check("build-session/brief-map-topology", "build-session", takes_context=True)
def check_brief_map_topology(artifact: str, context: Context) -> List[Finding]:
    """The shape the brief commits the geography to holds in the page's own edge
    table (`skills/to-session-brief/SKILL.md` — "**Map topology.** The shape"): a
    stated count of entrances equals the count of boundary edges, and a topology
    naming any vertical structure is carried by at least one `vertical` edge.

    **Shape only.** Whether the shape *fits* established geography is the brief's
    separate rubric-graded field and is not touched here.

    The vertical half is the one the ablation earned: both withheld arms
    **flattened a vertical site into a walled yard**, which is exactly this
    assertion. The table is located at any heading level, because a session page
    nests one under its location section rather than at the top level as a dungeon
    package does. A page with no edge table — a night with no keyed site — carries
    no shape to check and the row stays silent, as does a topology sentence
    stating neither a count nor a vertical.

    **It reads the page's raw markdown on purpose.** The edge table is
    machine state rather than DM-facing content, so a session page may carry it
    wrapped in an HTML comment; this check keeps working because it searches the
    source text and matches inside the comment, and a concealed table therefore
    earns the same verdict as a visible one. Do not make the section search skip
    commented-out regions. Both no-section and no-edges fall through to the empty
    list above, which is the silent-failure mode: the check would report clean on
    every page forever, looking exactly like a night with no keyed site, and no
    test, error, or finding anywhere would register that it had stopped
    checking."""
    check_id = "build-session/brief-map-topology"
    value = _brief_value(context, "map topology", check_id)
    if value is None:
        return []
    section = _ANY_LEVEL_EDGES_RE.search(artifact)
    if section is None:
        return []
    edges = _parse_edge_rows(section.group("body"))
    if not edges:
        return []
    location = "the page's edge table, against the brief's `Map topology`"
    findings: List[Finding] = []
    stated = _ENTRANCE_COUNT_RE.search(value)
    if stated:
        raw = stated.group("n").lower()
        wanted = _COUNT_WORDS.get(raw, int(raw) if raw.isdigit() else None)
        actual = len([e for e in edges if e.boundary])
        if wanted is not None and actual != wanted:
            findings.append(
                Finding(
                    check_id=check_id,
                    expected=f"{wanted} entrance(s), the shape the brief locks",
                    actual=f"{actual} boundary edge(s) in the page's edge table",
                    output_location=location,
                )
            )
    if _VERTICAL_WORDS.search(value):
        # Read the type cell's pre-em-dash region as text rather than requiring a
        # `·`-separated token: the ablation arms wrote "vertical, stairs, up" with
        # commas, and a check that goes dark on the notation the defect arrived in
        # buys nothing. Typing the token strictly is `type-column-token-strictness`.
        if not any("vertical" in e.raw_type.split("—", 1)[0].lower() for e in edges):
            findings.append(
                Finding(
                    check_id=check_id,
                    expected="at least one `vertical` edge — the brief's topology is not flat",
                    actual="every edge in the table is on one level",
                    output_location=location,
                )
            )
    return findings


# --- Not tonight: what the page must not stage. ------------------------------- #

def _excluded_items(value: str) -> List[str]:
    """One entry per `Not tonight` bullet — its bold lead-in where it has one,
    else the whole bullet."""
    items = []
    for line in value.splitlines():
        stripped = line.strip().lstrip("-*").strip()
        if not stripped:
            continue
        bold = re.match(r"\*\*(?P<t>[^*]+?)\*\*", stripped)
        items.append(bold.group("t").strip() if bold else stripped)
    return items


_EXCLUSION_TAIL_RE = re.compile(r"^\s+(?P<word>[a-z][a-z'’-]{2,})\b")


def _exclusion_keys(item: str) -> List[str]:
    """What one `Not tonight` entry is looked for by: its proper-noun run **plus
    the common noun that follows it**, where one does.

    The bare run is not enough, and a frozen arm proves it. *"The university's
    administration and Fenwick's reinstatement"* yields the run `Fenwick` — who is
    also the night's client, named in the brief's own `NPC commitments` — and a
    page keying a clue called *"Fenwick's ledger of nights"* would be reported as
    staging an excluded thread it never touched. `Fenwick's reinstatement` is the
    thing excluded, and it is the key. Where no common noun follows, the run
    stands alone (`Old Town`, `Harrow`)."""
    keys: List[str] = []
    for run, end in _proper_noun_spans(item):
        tail = _EXCLUSION_TAIL_RE.match(item[end:])
        key = f"{run} {tail.group('word')}" if tail else run
        if key not in keys:
            keys.append(key)
    return keys


def _depossess(text: str) -> str:
    """Drop possessive endings, so a key built off a stripped run still matches the
    page's own possessive phrasing — `Fenwick reinstatement` against *Fenwick's
    reinstatement hearing*."""
    return re.sub(r"['’]s\b", "", text)


@register_check("build-session/brief-not-tonight", "build-session", takes_context=True)
def check_brief_not_tonight(artifact: str, context: Context) -> List[Finding]:
    """Nothing the brief deliberately excluded is **staged** by the page — no `Not
    tonight` item appears as a heading, in the keyed index, or in a Potential
    Scenes entry (`skills/to-session-brief/SKILL.md` — "Named and deliberately
    excluded, so their absence reads as a decision rather than an oversight").

    The slot list is the whole design, and it excludes the Key NPCs table and the
    clue slate **deliberately**. The Gloamfen brief locks the curator as an NPC,
    aims its exit edge at her syndicate, and excludes *confronting* that syndicate
    — three lines at once and all three correct — so a row reading roster rows or
    lead targets would fire on a page that kept the contract perfectly. An
    excluded thread the page merely mentions, or points a lead toward, is not
    staged and is not a finding."""
    check_id = "build-session/brief-not-tonight"
    value = _brief_value(context, "not tonight", check_id)
    if value is None:
        return []
    slots = _staging_slots(artifact, include_title=False)
    findings: List[Finding] = []
    for item in _excluded_items(value):
        for run in _exclusion_keys(item):
            hit = next(
                (slot for slot in slots if _contains(_depossess(slot), _depossess(run))),
                None,
            )
            if hit is None:
                continue
            findings.append(
                Finding(
                    check_id=check_id,
                    expected=f"nothing staged for `{item[:60]}` — the brief excludes it",
                    actual=f"the page stages it: {hit[:70]}",
                    output_location="the page's headings, keyed index and scenes, against the brief's `Not tonight`",
                )
            )
            break
    return findings


# --- Unlicensed additive canon on a locked subject. --------------------------- #
#
# The one Spec-axis row that is NOT a field row. It grades the Locked lines as a
# SET — every subject any of them names — because the failure it exists for is
# invisible to every field row: one frozen ablation arm scored 11 of 11 while
# minting seven new facts about objects its brief locked, and nothing caught it,
# since every other row asks whether the LICENSED facts landed and none asks
# whether unlicensed ones were added.
#
# **This is not a general no-new-canon rule.** A subject the brief never locks is
# silence, and inventing there is exactly what the generator is for
# (`skills/build-session/SKILL.md` — "invent where both are silent"). A finding
# against new content about an unlocked subject would be this row doing the one
# thing it was scoped not to do.

# The Locked half of the template, which is the whole subject set. `Not tonight`
# is deliberately absent: its subjects are EXCLUDED, not locked, and a page is
# free to say new things about a thread it correctly kept off the board.
_LOCKED_SUBJECT_FIELDS = tuple(name for name, _ in _BRIEF_FIELD_CHECKS if name != "not tonight") + (
    "premise",
    "fit to established geography",
)

# System vocabulary a brief writes as part of a rule, never as a subject: the
# ability a save is made against reads exactly like a proper noun.
_SYSTEM_WORDS = frozenset("""
strength dexterity constitution intelligence wisdom charisma perception insight
investigation athletics acrobatics arcana history nature religion survival stealth
persuasion deception intimidation medicine performance initiative
""".split())

_SENTENCE_OPENERS = frozenset(".:;!?-*>|—–")


def _opens_a_sentence(text: str, start: int) -> bool:
    """Did this run start a sentence, a bullet or a line? A single capitalised
    word in that position is the writing, not a name — *Twelve* guards, *Interior*
    doors, *Alarm* spells, *Eldritch* eggs. Mid-sentence, the same capital is a
    reference."""
    i = start - 1
    while i >= 0 and (text[i].isspace() or text[i] in "*_\"'“‘("):
        if text[i] == "\n":
            return True
        i -= 1
    return i < 0 or text[i] in _SENTENCE_OPENERS


def locked_subjects(brief: str) -> List[str]:
    """Every subject the brief's **Locked** lines name.

    Read out of the enumerated Locked fields rather than off the raw `## Locked`
    section, which is what keeps the template's own preamble ("Each line is a
    proposition…") out of the set. Two filters earn their place: a single
    capitalised word that **opened** a sentence is prose, not a subject, and a
    bare ability name is system vocabulary. Both were fitted against the worked
    brief — without them the set carries `Twelve`, `Interior`, `Alarm` and
    `Wisdom`, and a junk subject matches page prose everywhere, which turns this
    row into the general no-new-canon rule it must not be."""
    fields = brief_fields(brief)
    subjects: List[str] = []
    for field in _LOCKED_SUBJECT_FIELDS:
        value = fields.get(field)
        if not value:
            continue
        for run, start, _ in _proper_noun_offsets(value):
            if run.lower() in _SYSTEM_WORDS:
                continue
            if " " not in run and _opens_a_sentence(value, start):
                continue
            if run not in subjects:
                subjects.append(run)
    return subjects


# The heading line is matched with `[^\n]*` rather than `.*`: DOTALL is needed for
# the body and would let a `.*` heading swallow the section it is anchoring.
_ADVENTURE_BACKGROUND_RE = re.compile(
    r"^#{1,6}[ \t]+[^\n]*Adventure Background[^\n]*\n(?P<body>.*?)(?=^#{1,6}\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_QUANTITY_WORDS = {word: n for n, word in _NUMBER_WORDS.items() if " " not in word}
_QUANTITY_RE = re.compile(
    r"(?<![\w-])(?P<n>\d+)(?![\w-])|\b(?P<word>" + "|".join(_QUANTITY_WORDS) + r")\b",
    re.IGNORECASE,
)


def _quantities(sentence: str) -> List[tuple]:
    """Every quantity in a sentence as ``(value, as_written)``. A numeral must
    stand alone — `T1`, `1d4` and `21st` are keys, dice and ordinals, not counts."""
    found: List[tuple] = []
    for m in _QUANTITY_RE.finditer(sentence):
        raw = m.group("n") or m.group("word")
        value = int(m.group("n")) if m.group("n") else _QUANTITY_WORDS[raw.lower()]
        if (value, raw.lower()) not in [(v, w.lower()) for v, w in found]:
            found.append((value, raw))
    return found


def _quantity_licensed(value: int, sources: List[str]) -> bool:
    """Is this quantity supplied by the brief or the record extract, in either
    notation? A page writing *thirty feet* has been given `30 feet`, and a check
    that fires on that is a check about spelling."""
    forms = [rf"(?<![\w-]){value}(?![\w-])"]
    word = _NUMBER_WORDS.get(value)
    if word:
        forms.append(rf"\b{re.escape(word)}\b")
    pattern = "|".join(forms)
    return any(re.search(pattern, source, re.IGNORECASE) for source in sources)


@register_check("build-session/brief-locked-subject-canon", "build-session", takes_context=True)
def check_brief_locked_subject_canon(artifact: str, context: Context) -> List[Finding]:
    """For each subject a Locked line names, the page asserts no fact about that
    subject which neither the brief nor the campaign canon record extract supplies
    (`skills/build-session/SKILL.md` — "A subject a Locked line names is not
    silence").

    **The executable half of a two-half row**, and the halves are split where the
    evidence is. It reads the page's **Adventure Background** — the section the
    format defines as the page's own voice on what is true
    (`skills/build-session/session-page-format.md` — "**Adventure Background** —
    what is actually going on, written for the DM") — and fires where a sentence
    naming a locked subject carries a **quantity** neither source supplies. The
    judgement half, graded by build-session's one-round fresh check, covers what a
    number does not mark: the frozen arm's sharpest invention carried one (*"made
    it himself, forty years ago"*) and its next one carried none (*"and he made it
    badly on purpose"*).

    **Two scope decisions, both deliberate.** The Adventure Background *only*,
    because a keyed area rendering a locked place in fresh words is the page doing
    its job — a whole-page read would fire on every correct page and the axis
    already names that as the failure a structural slot exists to prevent. And the
    subject set comes from the **Locked** fields only, never from `Not tonight`.

    It consumes the record extract on the same terms as
    `build-session/brief-introduced-canon` and refuses to run without it: grading
    "neither the brief nor the record supplies" against the brief alone would
    report the record's own facts as inventions."""
    check_id = "build-session/brief-locked-subject-canon"
    brief = _brief_or_raise(context, check_id)
    record = (context or {}).get("canon_record")
    if not isinstance(record, str) or not record.strip():
        raise ValueError(
            f"{check_id} asks what the brief and the campaign canon record "
            "already supply and was handed no record; pass the record extract as "
            "context['canon_record']. It is a named input like the party roster, "
            "not something this check can go and read."
        )
    subjects = locked_subjects(brief)
    if not subjects:
        return []
    section = _ADVENTURE_BACKGROUND_RE.search(artifact)
    if not section:
        return []
    sources = [brief, record]
    findings: List[Finding] = []
    for sentence in re.split(r"(?<=[.!?])\s+", section.group("body")):
        if not sentence.strip():
            continue
        named = [s for s in subjects if _contains(_depossess(sentence), _depossess(s))]
        if not named:
            continue
        unlicensed = [
            written for value, written in _quantities(sentence)
            if not _quantity_licensed(value, sources)
        ]
        if not unlicensed:
            continue
        findings.append(
            Finding(
                check_id=check_id,
                expected=f"nothing asserted about `{named[0]}` that the brief and the record do not supply",
                actual="new about `%s`: %s in — %s"
                % (named[0], ", ".join(f"*{w}*" for w in unlicensed),
                   re.sub(r"\s+", " ", sentence.strip())[:90]),
                output_location="the page's Adventure Background, against the brief's Locked lines",
            )
        )
    return findings
