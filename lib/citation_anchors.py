"""Maintainer guard: every citation in the eval-assertion chain names a file
plus an **anchor phrase** that still appears verbatim in that file.

Citations used to be line numbers — ``(`SKILL.md:203-212`)``. They rot on every
edit: any insertion above a cited line silently invalidates every citation below
it, and nothing read them, so nobody noticed. The three artifact families had
already drifted into disagreeing with each other about the same rule. An anchor
phrase proves the same thing a line number was supposed to prove — *this row did
not invent its criterion* — and does not decay when the file is re-flowed.

The citation form, everywhere in the chain::

    (`SKILL.md` — "each creature × count")
    (`xp-budget.md` — "three distinct stat blocks", "CR 0 sparingly")
    (`SKILL.md` — "the DM's yes"; `build-session/spotlight-doctrine.md` — "flagged ability")

This module reads that form back out and asserts each phrase is still there. Two
guards, and both are needed:

``missing_anchors``
    every anchor phrase resolves to a file that exists and contains it. A literal
    substring test — no line arithmetic, no resolver, no auto-repair.

``line_number_citations``
    no ``file.md:123`` / `` `:123` `` residue survives anywhere in the swept set.
    A green anchor check alone cannot see an *unconverted* row (it carries no
    anchor to fail), and writing a fresh line number is exactly the failure mode
    being retired. This second guard is what makes the convention stick.

``malformed_citations``
    a citation that *starts* — a cited path followed by the em dash — but whose
    anchor never parses is invisible to both guards above, so it is caught here.
    The way this happens in practice is a wrapped citation inside a ``#`` comment
    or a ``>`` blockquote: the continuation line's prefix lands between the dash
    and the phrase, and the citation silently stops being one. The other shape
    (issue #21) is prose *before* the dash — ``the `complications.md` H2s —
    "## Terrain…"`` — which never even starts as a citation; a cited path within
    a short gap of a dash-quote pair is flagged the same way.

**Whitespace is normalised on both sides** before matching — runs of whitespace
collapse to a single space. The cited files are hard-wrapped at ~80 columns and
the citing prose is too, so a phrase of any useful length straddles a newline on
one side or the other. Normalising keeps the match literal (it is still "does
this string appear", never a pattern) while letting an anchor be long enough to
be distinctive. Everything else — ``×``, en vs em dash, curly quotes — must be
copied byte-exact.

Path resolution: a citation with a ``/`` is relative to ``skills/`` (falling back
to the repo root, for ``lib/…``); a bare filename is relative to the citing
context's own skill — the inventory section it sits under. Contexts with no
owning skill (``checker.py``, the non-skill inventory sections, the library
prose) must spell the skill out.

This guard lives at the ``lib/`` top level, beside ``test_symlink_integrity.py``
and outside ``lib/mechanical-checker/`` — that directory materialises into every
consumer through a symlink, and this check is about *this repo's* maintenance
docs. It runs here (``pytest lib/``) and never ships.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent

# The path half of every citation pattern below — one grammar, so a change to
# what counts as a citable path (a new extension, say) lands everywhere at once.
CITED_PATH_RE = r"`(?P<path>[A-Za-z0-9_.][A-Za-z0-9_./-]*\.(?:md|py))`"

# `path.md` — "anchor", "another anchor"
CITATION_RE = re.compile(
    CITED_PATH_RE + r"\s*—\s*"
    r"(?P<anchors>\"[^\"]+\"(?:\s*,\s*\"[^\"]+\")*)"
)
ANCHOR_RE = re.compile(r"\"([^\"]+)\"")

# A citation that starts but whose anchor never parses — see ``malformed_citations``.
CITATION_START_RE = re.compile(CITED_PATH_RE + r"\s*—")

# The escape CITATION_START_RE can't see (issue #21): prose between the path and
# the em dash — ``the `complications.md` H2s — "## Terrain…"`` — so the citation
# never parses and the dash no longer follows the path directly. The dash-quote
# pair is the citation signature; a cited path within a short prose gap of one,
# with no intervening backtick or quote (which would mean the pair belongs to a
# different, well-formed citation), is treated as a mis-phrased citation and must
# be rephrased. The gap bound keeps a path mentioned much earlier in a sentence
# from being implicated by an unrelated dash-quote pair further on.
NEAR_MISS_GAP = 60
CITATION_NEAR_MISS_RE = re.compile(
    CITED_PATH_RE + r"[^`\"—]{0,%d}—\s*\"" % NEAR_MISS_GAP
)

# The rot being retired: `SKILL.md:203-212`, `session-page-format.md:64`, and the
# bare continuation form `:104`. Deliberately not requiring backticks — checker.py
# carries bare-comment citations (`# SKILL.md:181`) too — and accepting an en dash
# in the range, which one comment used.
LINE_CITATION_RES = (
    re.compile(r"[A-Za-z0-9_.-]+\.(?:md|py):[0-9]+"),
    re.compile(r"`:[0-9]+"),
)

# Inventory H2 headings are prose, not directory names; the owning skill is
# explicit rather than derived. ``None`` = no owning skill, so every citation in
# that section must name one.
INVENTORY_SECTIONS = {
    "build-session — the fight procedure (`combat.md`)": "build-session",
    "build-session — the keyed-site procedure (`dungeon.md`)": "build-session",
    "seed-clues": "seed-clues",
    "build-session + session-page-format": "build-session",
    "build-session — `node-deepening.md`": "build-session",
    "build-session — the Spec axis (the session brief)": "build-session",
    "catch-up": "catch-up",
    "build-session — the spotlight procedure (`spotlight.md`)": "build-session",
    "party-sync": "party-sync",
    "campaign-art": "campaign-art",
    "review-rewards": "review-rewards",
    "Check methods": None,
    "Static lints — no model run required": None,
    "Unenforceable as written": None,
    "What this exposes about the harness": None,
}

INVENTORY = "docs/eval-assertion-inventory.md"

# Every artifact in the derivation chain that cites the skill text, with the skill
# a bare filename belongs to. A new citing file adds a row here and inherits both
# guards.
SWEPT_FILES: dict[str, str | None] = {
    INVENTORY: None,  # per-section; see INVENTORY_SECTIONS
    "lib/mechanical-checker/checker.py": None,
    "lib/mechanical-checker/README.md": None,
    "lib/mechanical-checker/test_checker.py": None,
    "lib/test_session_fixture_sweep.py": None,
    "CLAUDE.md": None,
    # Maintainer prose, not the derivation chain — but its scaffold-as-default
    # paragraph cites the wiki-scaffold assets by anchor phrase, so it
    # inherits both guards. No owning skill: every citation spells its path out.
    "docs/campaign-contract.md": None,
    # Not part of the derivation chain, but it cites skill text to justify each
    # candidate, and went unswept long enough for two of its line-number
    # citations to rot silently onto unrelated prose.
    "docs/backpressure-candidates.md": None,
}


@dataclass(frozen=True)
class Citation:
    """One `file` — "phrase" pair, and where it was written."""

    source: str  # repo-relative file the citation was written in
    line: int  # 1-indexed line the citation starts on
    context: str  # the inventory row slug / heading it sits under, for the report
    path: str  # the cited path, as written
    anchor: str  # the anchor phrase, as written
    skill: str | None  # owning skill for a bare filename, if any


@dataclass(frozen=True)
class Failure:
    citation: Citation
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.citation.source}:{self.citation.line}: "
            f"[{self.citation.context}] `{self.citation.path}` — "
            f'"{self.citation.anchor}": {self.reason}'
        )


def normalise(text: str) -> str:
    """Collapse whitespace runs to a single space. Applied to both the anchor and
    the file it is looked for in, so a hard-wrapped phrase still matches."""
    return re.sub(r"\s+", " ", text).strip()


def _row_slug(line: str) -> str | None:
    """The slug of an inventory table row, so a failure names the promise."""
    if not line.startswith("|"):
        return None
    first = line.strip().strip("|").split("|")[0].strip().strip("*")
    if not first or first == "Slug" or set(first) <= {"-", " "}:
        return None
    return first


def iter_citations(text: str, source: str, skill: str | None) -> Iterator[Citation]:
    """Every citation in one file, in order. ``skill`` is the default owner of a
    bare filename; the inventory overrides it per section."""
    section_skill = skill
    context = source
    line_starts = [0]
    for match in re.finditer(r"\n", text):
        line_starts.append(match.end())

    def line_of(offset: int) -> int:
        low, high = 0, len(line_starts) - 1
        while low < high:
            mid = (low + high + 1) // 2
            if line_starts[mid] <= offset:
                low = mid
            else:
                high = mid - 1
        return low + 1

    # Walk headings/rows and citations together so each citation knows its context.
    events: list[tuple[int, str, object]] = []
    for match in re.finditer(r"^.*$", text, re.MULTILINE):
        line = match.group(0)
        if source == INVENTORY and line.startswith("## "):
            heading = line[3:].strip()
            events.append((match.start(), "section", heading))
        slug = _row_slug(line) if source == INVENTORY else None
        if slug:
            events.append((match.start(), "context", slug))
    for match in CITATION_RE.finditer(text):
        events.append((match.start(), "citation", match))
    events.sort(key=lambda event: (event[0], {"section": 0, "context": 1, "citation": 2}[event[1]]))

    for offset, kind, payload in events:
        if kind == "section":
            heading = str(payload)
            if heading not in INVENTORY_SECTIONS:
                raise KeyError(
                    f"{source}: unknown section heading {heading!r} — add it to "
                    "INVENTORY_SECTIONS with the skill a bare filename belongs to"
                )
            section_skill = INVENTORY_SECTIONS[heading]
            context = heading
        elif kind == "context":
            context = str(payload)
        else:
            match = payload
            for anchor in ANCHOR_RE.findall(match.group("anchors")):
                yield Citation(
                    source=source,
                    line=line_of(offset),
                    context=context,
                    path=match.group("path"),
                    anchor=anchor,
                    skill=section_skill,
                )


def resolve(citation: Citation, repo_root: Path = REPO_ROOT) -> Path | None:
    """The file a citation names, or ``None`` when a bare filename has no owning
    skill to hang it on."""
    if "/" in citation.path:
        candidate = repo_root / "skills" / citation.path
        return candidate if candidate.exists() else repo_root / citation.path
    if citation.skill is None:
        return None
    return repo_root / "skills" / citation.skill / citation.path


def missing_anchors(repo_root: Path = REPO_ROOT, files: Iterable[str] | None = None) -> list[Failure]:
    """Every citation whose anchor phrase no longer appears in the file it names."""
    swept = SWEPT_FILES if files is None else {name: SWEPT_FILES[name] for name in files}
    failures: list[Failure] = []
    haystacks: dict[Path, str | None] = {}
    for source, skill in swept.items():
        text = (repo_root / source).read_text(encoding="utf-8")
        for citation in iter_citations(text, source, skill):
            target = resolve(citation, repo_root)
            if target is None:
                failures.append(
                    Failure(citation, "bare filename in a context with no owning skill — name the skill")
                )
                continue
            if target not in haystacks:
                haystacks[target] = (
                    normalise(target.read_text(encoding="utf-8")) if target.is_file() else None
                )
            haystack = haystacks[target]
            if haystack is None:
                failures.append(Failure(citation, f"no such file: {target.relative_to(repo_root)}"))
            elif normalise(citation.anchor) not in haystack:
                failures.append(
                    Failure(citation, f"phrase not found in {target.relative_to(repo_root)}")
                )
    return failures


def line_number_citations(repo_root: Path = REPO_ROOT, files: Iterable[str] | None = None) -> list[str]:
    """Surviving ``file.md:123`` / `` `:123`` residue in the swept set."""
    hits: list[str] = []
    for source in SWEPT_FILES if files is None else files:
        for number, line in enumerate((repo_root / source).read_text(encoding="utf-8").splitlines(), 1):
            for pattern in LINE_CITATION_RES:
                for match in pattern.finditer(line):
                    hits.append(f"{source}:{number}: {match.group(0)}  |  {line.strip()}")
    return hits


def malformed_citations(repo_root: Path = REPO_ROOT, files: Iterable[str] | None = None) -> list[str]:
    """Citations that begin — cited path, em dash — but whose anchor doesn't parse."""
    hits: list[str] = []
    for source in SWEPT_FILES if files is None else files:
        text = (repo_root / source).read_text(encoding="utf-8")
        starts = {match.start() for match in CITATION_START_RE.finditer(text)}
        starts.update(match.start() for match in CITATION_NEAR_MISS_RE.finditer(text))
        parsed = {match.start() for match in CITATION_RE.finditer(text)}
        for offset in sorted(starts - parsed):
            line = text.count("\n", 0, offset) + 1
            hits.append(f"{source}:{line}: {text[offset:offset + 90]!r}")
    return hits


def anchor_hit_counts(repo_root: Path = REPO_ROOT) -> list[tuple[Citation, int]]:
    """(citation, occurrences) for every resolvable anchor — the sweep aid for
    spotting an anchor so generic it points nowhere useful. Not asserted on: a
    hit-count *cap* would fail on legitimately repeated skill text."""
    counts = []
    for source, skill in SWEPT_FILES.items():
        text = (repo_root / source).read_text(encoding="utf-8")
        for citation in iter_citations(text, source, skill):
            target = resolve(citation, repo_root)
            if target is None or not target.is_file():
                continue
            haystack = normalise(target.read_text(encoding="utf-8"))
            counts.append((citation, haystack.count(normalise(citation.anchor))))
    return counts


def main() -> int:
    failures = missing_anchors()
    residue = line_number_citations()
    malformed = malformed_citations()
    for failure in failures:
        print(failure)
    for hit in residue:
        print(f"line-number citation (use an anchor phrase): {hit}")
    for hit in malformed:
        print(f"citation starts but its anchor does not parse: {hit}")
    total = len(failures) + len(residue) + len(malformed)
    print(f"{'FAIL' if total else 'ok'}: {total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
