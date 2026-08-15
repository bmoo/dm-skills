"""The citation-anchor guard, run two ways.

Unit tests drive ``citation_anchors`` against a synthetic tree so each failure
mode is *proven* to fail — including a fixture whose anchor phrase is absent,
which is the whole point of the guard. The three tree tests then run it over the
real repo, which is what gates a commit: ``pytest lib/`` is the gate; there is no
hook to install and nothing to remember.

Like ``test_symlink_integrity.py`` beside it, this lives at the ``lib/`` top
level rather than inside ``lib/mechanical-checker/`` — that directory
materialises into every consumer through a symlink, and a check over *this
repo's* maintenance docs must not ship with it.
"""

from pathlib import Path

import pytest

import citation_anchors
from citation_anchors import (
    Citation,
    iter_citations,
    line_number_citations,
    malformed_citations,
    missing_anchors,
    normalise,
    resolve,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# --- a synthetic tree, so every failure mode is exercised in isolation ---------

CITED_FILE = """# Combat Generator

- **MUST** browse the catalog across **all active sources** (the `list_*`
  tools) *before* shortlisting.

Party, Enemies, Budget, Terrain, Spotlight, and Objective are required;
Note is optional.
"""


@pytest.fixture
def tree(tmp_path):
    """A miniature repo: one skill with one cited file, and a citing doc whose
    content each test supplies."""
    skill = tmp_path / "skills" / "combat-generator"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(CITED_FILE, encoding="utf-8")
    return tmp_path


def _sweep(tree, text, name="doc.md", skill="combat-generator"):
    """Write one citing file into the miniature repo and make it the swept set."""
    (tree / name).write_text(text, encoding="utf-8")
    citation_anchors.SWEPT_FILES.clear()
    citation_anchors.SWEPT_FILES[name] = skill
    return name


@pytest.fixture(autouse=True)
def _restore_swept():
    """SWEPT_FILES is module state; a test that points it at tmp_path must not
    leak into the tree tests below."""
    saved = dict(citation_anchors.SWEPT_FILES)
    try:
        yield
    finally:
        citation_anchors.SWEPT_FILES.clear()
        citation_anchors.SWEPT_FILES.update(saved)


def _check(tree, text, skill="combat-generator"):
    _sweep(tree, text, skill=skill)
    return missing_anchors(repo_root=tree)


def test_present_anchor_passes(tree):
    assert _check(tree, 'A promise (`SKILL.md` — "*before* shortlisting").') == []


def test_missing_anchor_is_reported_with_row_and_phrase(tree):
    """The failure the whole guard exists for: a phrase that is no longer in the
    file it names."""
    failures = _check(tree, 'A promise (`SKILL.md` — "before you shortlist").')
    assert len(failures) == 1
    assert failures[0].citation.anchor == "before you shortlist"
    assert "phrase not found" in failures[0].reason
    assert "SKILL.md" in str(failures[0])


def test_one_citation_may_carry_several_anchors(tree):
    failures = _check(
        tree,
        'A promise (`SKILL.md` — "**all active sources**", "gone missing", "Note is optional").',
    )
    assert [failure.citation.anchor for failure in failures] == ["gone missing"]


def test_anchor_wrapped_across_lines_still_matches(tree):
    """Both sides are hard-wrapped, so normalisation is load-bearing — without it
    every anchor longer than a few words would fail spuriously."""
    assert _check(tree, 'A promise (`SKILL.md` — "browse the catalog\n  across **all active sources**").') == []


def test_missing_file_is_reported(tree):
    failures = _check(tree, 'A promise (`no-such-file.md` — "anything").')
    assert len(failures) == 1
    assert "no such file" in failures[0].reason


def test_bare_filename_without_an_owning_skill_is_reported(tree):
    failures = _check(tree, 'A promise (`SKILL.md` — "Note is optional").', skill=None)
    assert len(failures) == 1
    assert "name the skill" in failures[0].reason


def test_line_number_citation_is_reported(tree):
    _sweep(tree, "A promise (`SKILL.md:203-212`, `:104`).")
    hits = line_number_citations(repo_root=tree)
    assert len(hits) == 2
    assert "SKILL.md:203" in hits[0] and "`:104" in hits[1]


def test_a_swept_file_with_no_citations_is_not_a_pass_by_default(tree):
    """An *unconverted* citation carries no anchor to fail, which is why the
    residue guard exists — it is the half that sees what the anchor check can't."""
    _sweep(tree, "A promise, uncited, plus one at `SKILL.md:99`.")
    assert missing_anchors(repo_root=tree) == []
    assert line_number_citations(repo_root=tree)


def test_citation_broken_by_a_comment_prefix_is_reported(tree):
    """A wrapped citation inside a `#` comment: the dash ends one line and the
    prefix lands before the phrase, so it silently stops parsing."""
    _sweep(tree, '# A promise (`SKILL.md` —\n# "Note is optional").', name="doc.py")
    assert missing_anchors(repo_root=tree) == []  # invisible to the anchor check
    hits = malformed_citations(repo_root=tree)
    assert len(hits) == 1 and "SKILL.md" in hits[0]


def test_slash_path_resolves_under_skills(tree):
    citation = Citation("doc.md", 1, "row", "combat-generator/SKILL.md", "x", None)
    assert resolve(citation, tree) == tree / "skills" / "combat-generator" / "SKILL.md"


def test_normalise_collapses_whitespace_runs():
    assert normalise("  a\n   b\tc ") == "a b c"


def test_inventory_citations_carry_their_row_slug(tree):
    """A failure has to name the promise, not just the file — the row slug is the
    library's promise-pointer everywhere else."""
    text = (
        "## combat-generator\n\n"
        "| Slug | Promise (source) |\n|---|---|\n"
        '| combat-generator/catalog-browse-before-lookup | A promise (`SKILL.md` — "x") |\n'
    )
    citations = list(iter_citations(text, citation_anchors.INVENTORY, None))
    assert [citation.context for citation in citations] == [
        "combat-generator/catalog-browse-before-lookup"
    ]
    assert citations[0].skill == "combat-generator"


def test_unknown_inventory_section_raises_rather_than_guessing(tree):
    text = "## brand-new-skill\n\n| x | A promise (`SKILL.md` — \"y\") |\n"
    with pytest.raises(KeyError, match="INVENTORY_SECTIONS"):
        list(iter_citations(text, citation_anchors.INVENTORY, None))


# --- the gate: the same guard over the real tree ------------------------------


def test_tree_every_anchor_phrase_is_still_in_the_file_it_names():
    failures = missing_anchors()
    assert not failures, "\n".join(str(failure) for failure in failures)


def test_tree_carries_no_line_number_citations():
    hits = line_number_citations()
    assert not hits, "\n".join(hits)


def test_tree_carries_no_half_parsed_citations():
    hits = malformed_citations()
    assert not hits, "\n".join(hits)
