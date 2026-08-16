"""The encounter-meta single-source guard, run over the real tree.

Each test names the failure it exists to catch: the spec disagreeing with
itself, the checker's literal drifting off the spec, the parser no longer
reading the spec's own block, the citing skill growing its own copy back.

Like ``test_citation_anchors.py`` and ``test_doctrine_sync.py`` beside it, this
lives at the ``lib/`` top level rather than inside the shipped checker at
``skills/build-session/scripts/mechanical_checker/`` —
that directory materialises into every consumer, and a check
over *this repo's* skill text must not ship with it.
"""

from encounter_meta_spec import (
    SPEC_FILE,
    SPEC_HEADING,
    checker_required_labels,
    cites_spec,
    parse_spec_example,
    restatements,
    spec_optional_labels,
    spec_required_labels,
    spec_section,
    spec_template,
    template_labels,
)

SIX = ["Party", "Enemies", "Budget", "Terrain", "Spotlight", "Objective"]


def test_the_spec_has_a_home():
    assert SPEC_HEADING in spec_section()
    assert "> [!encounter-meta]" in spec_template()


def test_template_and_prose_agree():
    """The section states the field list twice — the template and the sentence
    naming which are required. They must be the same list."""
    assert template_labels() == spec_required_labels() + spec_optional_labels()


def test_the_six_required_lines_are_unchanged():
    """This is a citation move, not a promise change."""
    assert spec_required_labels() == SIX
    assert spec_optional_labels() == ["Note"]


def test_checker_is_pinned_to_the_spec():
    """The shipped checker keeps a literal (it must not read this repo's docs at
    run time); this is what holds the literal to the spec."""
    assert checker_required_labels() == spec_required_labels()


def test_the_parser_reads_the_specs_own_block():
    """The parser half: the spec's example parses as an encounter-meta callout
    whose body carries every label the spec declares."""
    blocks = [element for element in parse_spec_example() if element["type"] == "encounter-meta"]
    assert len(blocks) == 1, "the spec's own template must parse as exactly one callout"
    body = blocks[0]["content"]
    for label in template_labels():
        assert f"**{label}:**" in body, f"the parser lost the {label} line"


def test_nothing_restates_the_template():
    """The failure arose from a fourth independent copy of the field
    list. The spec file is the only legal home for the placeholder form."""
    assert restatements() == [], (
        "the encounter-meta template is restated outside "
        f"{SPEC_FILE} — cite the spec section instead:\n" + "\n".join(restatements())
    )


def test_combat_generator_cites_the_spec():
    assert cites_spec()


# --------------------------------------------------------------------------- #
# The guards proven against synthetic trees — a green tree alone cannot show
# that either check would fire.
# --------------------------------------------------------------------------- #


def _synthetic(root, template_lines, sentence):
    spec = root / SPEC_FILE
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(
        f"{SPEC_HEADING}\n\n```markdown\n> [!encounter-meta]\n"
        + "".join(f"> **{label}:** <a placeholder>\n" for label in template_lines)
        + f"```\n\n{sentence}\n\n## Next\n",
        encoding="utf-8",
    )
    return root


def test_a_spec_that_disagrees_with_itself_is_caught(tmp_path):
    """A label added to the template and not to the sentence — the drift the
    three-copy arrangement used to hide."""
    root = _synthetic(
        tmp_path,
        SIX + ["Morale", "Note"],
        "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required; "
        "Note is optional.",
    )
    assert template_labels(root) != spec_required_labels(root) + spec_optional_labels(root)


def test_a_restated_template_is_caught(tmp_path):
    """The fourth copy growing back."""
    root = _synthetic(
        tmp_path,
        SIX + ["Note"],
        "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required; "
        "Note is optional.",
    )
    assert restatements(root) == []
    (root / "some-other-skill.md").write_text(
        "> [!encounter-meta]\n> **Party:** <size and level sized for>\n", encoding="utf-8"
    )
    assert [hit for hit in restatements(root) if "some-other-skill.md" in hit]
