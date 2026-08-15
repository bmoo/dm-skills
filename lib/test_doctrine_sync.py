"""The doctrine-duplication guard, run two ways.

Unit tests drive ``doctrine_sync`` against a synthetic pair of skills, so each
kind of drift is *proven* to fail — a clause deleted from one copy, a sentence
added to one copy, a re-wrap that must **not** fail. The tree tests then run the
real declaration over the real skills: ``pytest lib/`` is the gate, the same one
the anchor and retired-phrase checks use.

Two tests guard the **declaration** rather than the tree. A closed-diff check
degrades quietly in one direction: a permitted variation that no longer occurs
is dead weight that will silently absorb a future span, and a required clause
that appears in neither copy asserts nothing. Both are checked against the real
files.

Like ``test_citation_anchors.py`` beside it, this lives at the ``lib/`` top
level rather than inside ``lib/mechanical-checker/`` — that directory
materialises into every consumer through a symlink, and a check over *this
repo's* skill text must not ship with it.
"""

import pytest

from doctrine_sync import (
    BLOCKS,
    RULES_SOURCING,
    DuplicatedBlock,
    Variation,
    drifted,
    extract_block,
    variations,
)

HEADING = "Rules sourcing — non-negotiable"

LEFT = """---
name: left
---

## Rules sourcing — non-negotiable

- **MUST** source all rules content from the tools, never from memory.
- If the shelf is empty, **flag the gap and halt**.

## Step 1

Prose that is not part of the block.
"""

RIGHT = LEFT.replace("name: left", "name: right").replace(
    "all rules content from", "all rules content — item text — from"
)


@pytest.fixture
def tree(tmp_path):
    """A miniature pair of skills carrying the same block."""
    for name, text in (("left", LEFT), ("right", RIGHT)):
        skill = tmp_path / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(text, encoding="utf-8")
    return tmp_path


def _block(**overrides) -> DuplicatedBlock:
    fields = dict(
        name="fixture",
        heading=HEADING,
        left="skills/left/SKILL.md",
        right="skills/right/SKILL.md",
        required=("If the shelf is empty, **flag the gap and halt**.",),
        permitted=(Variation("", "— item text —", "the right skill places items"),),
    )
    fields.update(overrides)
    return DuplicatedBlock(**fields)


def _rewrite(tree, name, old, new):
    path = tree / "skills" / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


# --- the shape being compared -------------------------------------------------


def test_extract_block_stops_at_the_next_heading():
    body = extract_block(LEFT, HEADING)
    assert "flag the gap and halt" in body
    assert "not part of the block" not in body


def test_extract_block_returns_none_when_the_heading_is_gone():
    assert extract_block(LEFT.replace("## Rules sourcing", "## Rules"), HEADING) is None


# --- copies that agree --------------------------------------------------------


def test_declared_variation_passes(tree):
    assert drifted(repo_root=tree, blocks=(_block(),)) == []


def test_a_rewrap_is_not_a_difference(tree):
    """Both files are hard-wrapped; re-flowing one copy must not fail the check,
    or the guard would fire on every unrelated edit near the block."""
    _rewrite(tree, "left", "- **MUST** source all rules content from the tools, never from memory.",
             "- **MUST** source all rules content from the tools, never from\n  memory.")
    assert drifted(repo_root=tree, blocks=(_block(),)) == []


def test_the_same_edit_in_both_copies_passes(tree):
    """The point of the guard: doctrine may change, it may just not change in
    one copy only."""
    for name in ("left", "right"):
        _rewrite(tree, name, "never from memory", "never from training-data memory")
    assert drifted(repo_root=tree, blocks=(_block(),)) == []


# --- the failure modes the guard exists for -----------------------------------


def test_a_clause_deleted_from_one_copy_fails(tree):
    _rewrite(tree, "left", ", never from memory", "")
    findings = drifted(repo_root=tree, blocks=(_block(),))
    assert any("undeclared difference" in str(finding) for finding in findings)
    assert any("never from memory" in str(finding) for finding in findings)


def test_a_sentence_added_to_one_copy_fails(tree):
    """The case a required-phrase list cannot see, and the reason this check is a
    closed diff instead."""
    _rewrite(tree, "right", "**flag the gap and halt**.", "**flag the gap and halt**. Never guess a stat block.")
    findings = drifted(repo_root=tree, blocks=(_block(),))
    assert any("undeclared difference" in str(finding) for finding in findings)
    assert any("Never guess a stat block." in str(finding) for finding in findings)


def test_the_failure_prints_a_pasteable_declaration(tree):
    """A maintainer must be able to copy the span straight into PERMITTED."""
    _rewrite(tree, "right", "**flag the gap and halt**.", "**flag the gap and halt** — do not answer from memory.")
    report = "\n".join(str(finding) for finding in drifted(repo_root=tree, blocks=(_block(),)))
    assert "Variation(" in report
    assert "PERMITTED" in report


def test_an_obligation_dropped_from_both_copies_fails(tree):
    """A closed diff alone stays green when both copies are gutted in step; the
    required clauses are what catch that."""
    for name in ("left", "right"):
        _rewrite(tree, name, "- If the shelf is empty, **flag the gap and halt**.\n", "")
    findings = drifted(repo_root=tree, blocks=(_block(),))
    assert len(findings) == 2
    assert all("no longer states a required clause" in str(finding) for finding in findings)


def test_a_missing_block_fails(tree):
    _rewrite(tree, "right", "## Rules sourcing — non-negotiable", "## Sourcing")
    findings = drifted(repo_root=tree, blocks=(_block(),))
    assert len(findings) == 1
    assert "no `## Rules sourcing — non-negotiable` section" in str(findings[0])


# --- guards on the declaration, not the tree ----------------------------------


def test_every_permitted_variation_still_occurs():
    """A stale entry is worse than a missing one: it sits there ready to absorb a
    future span that happens to land on the same words."""
    live = {variation.span for variation in variations(RULES_SOURCING)}
    for permitted in RULES_SOURCING.permitted:
        assert permitted.span in live, f"declared but no longer a difference: {permitted}"
        assert permitted.why, f"{permitted} carries no reason"


def test_every_required_clause_is_specific_enough_to_be_a_claim():
    for block in BLOCKS:
        assert block.required, f"{block.name} declares no obligations"
        for clause in block.required:
            assert len(clause) >= 20, clause


# --- the gate: the real declaration over the real skills -----------------------


def test_the_duplicated_doctrine_is_in_sync():
    findings = drifted()
    assert not findings, "\n".join(str(finding) for finding in findings)
