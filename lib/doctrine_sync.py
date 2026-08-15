"""Maintainer guard: the rules-sourcing doctrine is duplicated in two
skills, and the two copies must not drift apart silently.

``combat-generator`` and ``dungeon-generator`` each carry a *"Rules sourcing —
non-negotiable"* block. They are near-verbatim but deliberately **not**
identical: the dungeon copy enumerates the extra content types that skill
places, and points its browse rule at the step that shortlists. The duplication
is the accepted answer — the doctrine must live inside each generator's own
SKILL.md so a selective install carries it, while the sourcing *chain* the
blocks point at ships once (``lib/rules-sourcing.md``, materialised into each
skill by symlink like the mechanical checker). What hurts is not the copying;
it is a change landing in one copy only.

The check therefore asserts **the two copies differ only in ways declared
here**. Word-level diff, whitespace normalised on both sides (the same matching
``citation_anchors`` and ``retired_phrases`` use — both files are hard-wrapped,
so every clause of any length straddles a newline). Every differing span must
appear in ``PERMITTED`` with the reason it is per-skill; anything else fails.

Declaring the *variations* rather than the shared text is what makes this catch
drift in both directions. A list of required phrases catches a clause being
deleted or reworded in one copy; only a closed diff catches a sentence being
**added** to one copy, which is the likelier accident — a maintainer improving
the skill they happen to be editing. It also means this module holds no third
copy of the doctrine to keep in sync: it stores the deltas and the obligations,
never the block.

``REQUIRED`` carries the obligations on top, because a closed diff alone is
blind to a change applied to *both* copies at once — the doctrine could be
gutted in sync and stay perfectly consistent. Those three are the core
obligations: never from memory, browse the chosen source's catalog before
shortlisting, and name the gap when nothing in the sourcing chain answers.

(The block writes ``**MUST**`` twice, not three times; the third obligation is
carried by ``**say so and name the gap**``. The count is of obligations, not of
the markup.)

Adding a variation
------------------

When an edit to one copy is genuinely per-skill, the failure prints the exact
word spans; paste the pair into ``PERMITTED`` with why it belongs to only one
skill. When it is not per-skill — the usual case — make the same edit in the
other copy and the span disappears on its own.

Two things to expect while doing that. Editing a *shared* clause in both copies
can shift the word boundaries of a neighbouring variation, so an existing
``PERMITTED`` entry goes stale in the same edit that produces a new span:
``test_every_permitted_variation_still_occurs`` will name it — replace that
entry rather than adding beside it. And ``REQUIRED`` quotes the doctrine
verbatim, which makes this module a third copy of those clauses for
``retired_phrases`` purposes: it is swept like any other tracked file, so a
future retirement of rules-sourcing wording has to land here too. That is the
intended coupling, not an oversight.

This guard lives at the ``lib/`` top level, beside ``citation_anchors.py`` and
``retired_phrases.py`` and outside ``lib/mechanical-checker/``, for the same
reason: that directory materialises into every consumer through a symlink, and
this is a check over *this repo's* skill text. It runs here (``pytest lib/``)
and never ships.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path

from citation_anchors import REPO_ROOT, normalise

COMBAT = "skills/combat-generator/SKILL.md"
DUNGEON = "skills/dungeon-generator/SKILL.md"


@dataclass(frozen=True)
class Variation:
    """One declared per-skill difference between the two copies. ``left`` and
    ``right`` are the differing word spans, in the copies' declared order; an
    empty string means the span is absent from that copy."""

    left: str
    right: str
    why: str = ""

    @property
    def span(self) -> tuple[str, str]:
        return (self.left, self.right)


@dataclass(frozen=True)
class DuplicatedBlock:
    name: str
    heading: str
    left: str  # repo-relative path of the first copy
    right: str
    required: tuple[str, ...]  # obligations both copies must still state
    permitted: tuple[Variation, ...]


RULES_SOURCING = DuplicatedBlock(
    name="rules-sourcing",
    heading="Rules sourcing — non-negotiable",
    left=COMBAT,
    right=DUNGEON,
    required=(
        # The three core obligations, plus the two clauses that make them
        # operable — what to look up, and where the tool docs are.
        "never from training-data memory",
        "the sourcing chain in [`rules-sourcing.md`](rules-sourcing.md)",
        "**MUST** browse the chosen source's catalog (its listings, filtered by "
        "type/CR/etc.) *before* shortlisting",
        "If nothing in the chain answers, **say so and name the gap** — hand the "
        "DM what could not be sourced instead of filling it from memory.",
        "**MUST** source all rules content",
        "Look up every creature",
        "never shortlist from memory, which silently defaults to famous core-book "
        "entries and ignores what the table's sources actually offer.",
    ),
    permitted=(
        Variation(
            "",
            "item text, trap and door mechanics,",
            "A dungeon places items, traps and doors; a combat encounter places none.",
        ),
        Variation(
            "(2024 stat blocks and XP",
            "(the 2024 rules",
            "Combat's edition warning is about the two numbers it spends; the "
            "dungeon's covers every content type it places.",
        ),
        Variation(
            "",
            "and item",
            "Same reason: dungeon-generator looks up items as well as creatures.",
        ),
        Variation(
            "place; confirm its XP before you spend it.",
            "place.",
            "The XP-before-you-spend-it rule belongs to the skill that owns the "
            "budget arithmetic; dungeon-generator delegates fight sizing.",
        ),
        Variation(
            "",
            "in Step 5",
            "dungeon-generator shortlists in a numbered step; combat-generator "
            "shortlists inline, so it has no step to point at.",
        ),
    ),
)

BLOCKS = (RULES_SOURCING,)


@dataclass(frozen=True)
class Drift:
    block: DuplicatedBlock
    reason: str
    detail: str = ""

    def __str__(self) -> str:
        head = f"{self.block.name} ({self.block.left} / {self.block.right}): {self.reason}"
        return f"{head}\n{self.detail}" if self.detail else head


def extract_block(text: str, heading: str) -> str | None:
    """The body of one ``## <heading>`` section, up to the next H2 or EOF."""
    match = re.search(
        r"^##[ \t]+" + re.escape(heading) + r"[ \t]*$(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group("body") if match else None


def _bodies(block: DuplicatedBlock, repo_root: Path) -> tuple[str | None, str | None]:
    bodies = []
    for path in (block.left, block.right):
        file = repo_root / path
        text = file.read_text(encoding="utf-8") if file.is_file() else ""
        bodies.append(extract_block(text, block.heading))
    return bodies[0], bodies[1]


def variations(block: DuplicatedBlock, repo_root: Path = REPO_ROOT) -> list[Variation]:
    """Every word span where the two copies differ, in reading order. Both sides
    normalised first, so a re-wrap is not a difference."""
    left, right = _bodies(block, repo_root)
    if left is None or right is None:
        return []
    left_words, right_words = normalise(left).split(" "), normalise(right).split(" ")
    matcher = difflib.SequenceMatcher(None, left_words, right_words, autojunk=False)
    return [
        Variation(" ".join(left_words[i1:i2]), " ".join(right_words[j1:j2]))
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
        if tag != "equal"
    ]


def drifted(repo_root: Path = REPO_ROOT, blocks=BLOCKS) -> list[Drift]:
    """Every way the duplicated copies have come apart: a missing block, an
    obligation dropped from a copy, or an undeclared difference between them."""
    findings: list[Drift] = []
    for block in blocks:
        left, right = _bodies(block, repo_root)
        for path, body in ((block.left, left), (block.right, right)):
            if body is None:
                findings.append(
                    Drift(block, f"no `## {block.heading}` section in {path}")
                )
        if left is None or right is None:
            continue
        for path, body in ((block.left, left), (block.right, right)):
            haystack = normalise(body)
            for clause in block.required:
                if normalise(clause) not in haystack:
                    findings.append(
                        Drift(block, f"{path} no longer states a required clause", f'    "{clause}"')
                    )
        declared = {permitted.span for permitted in block.permitted}
        for variation in variations(block, repo_root):
            if variation.span not in declared:
                findings.append(
                    Drift(
                        block,
                        "undeclared difference between the copies",
                        f"    {block.left}: {variation.left!r}\n"
                        f"    {block.right}: {variation.right!r}\n"
                        "    → make the same edit in the other copy, or declare it "
                        "in PERMITTED with why it is per-skill:\n"
                        f"        Variation({variation.left!r}, {variation.right!r}, \"…\"),",
                    )
                )
    return findings


def main() -> int:
    findings = drifted()
    for finding in findings:
        print(finding)
    print(f"{'FAIL' if findings else 'ok'}: {len(findings)} drift(s) across {len(BLOCKS)} duplicated block(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
