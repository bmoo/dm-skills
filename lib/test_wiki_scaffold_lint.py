"""The gate half of ``wiki_scaffold_lint`` — see that module for why these two
facts are the ones worth pinning, and *Static lints* in
``docs/eval-assertion-inventory.md`` for the rows they derive from.

The two ``test_*_over_the_real_tree`` cases are the guard proper. The rest are
guard-the-guard: they feed the parser deliberately broken input to prove a gap
would actually be reported, since a lint whose extractor silently returns an
empty set passes forever.
"""

from __future__ import annotations

import pytest

from wiki_scaffold_lint import (
    preflight_gaps,
    preflight_paths,
    shipped_top_level,
    starts_green,
)


def test_scaffold_starts_green_over_the_real_tree():
    run = starts_green()
    assert run.clean, (
        "a fresh copy of the shipped wiki scaffold no longer bootstraps clean — "
        "the setup skill promises zero errors and zero warnings on a freshly "
        "generated catalog:\n" + run.report()
    )


def test_preflight_guards_every_shipped_path_over_the_real_tree():
    gaps = preflight_gaps()
    assert not gaps, (
        "the setup skill's preflight does not name these shipped top-level paths, "
        "so the bootstrap would write over them without stopping: "
        + ", ".join(sorted(gaps))
    )


def test_preflight_list_parses_to_the_paths_the_skill_names():
    named = preflight_paths()
    # index.md is named but never shipped — wiki-index.py generates it. Its
    # presence is what makes the shipped-subset-of-named direction the right one.
    assert "index.md" in named
    assert {"nodes", "story", "sessions", "players", "scripts"} <= named


def test_shipped_top_level_is_the_template_root():
    shipped = shipped_top_level()
    assert {"wiki-schema.md", "log.md", "scripts", "nodes"} <= shipped
    assert "index.md" not in shipped, "index files are generated; none should ship"


def test_a_forgotten_shipped_path_is_reported(tmp_path):
    """Guard-the-guard: add a top-level file the preflight never heard of."""
    (tmp_path / "campaign-secrets.md").write_text("", encoding="utf-8")
    assert preflight_gaps(template=tmp_path) == {"campaign-secrets.md"}


def test_a_dotfile_in_the_template_is_reported_too(tmp_path):
    """The repo's usual walker skips dotfiles; this check must not.

    A `.gitignore` shipped in the template would land in the consumer's root and
    overwrite theirs — the exact clobber the preflight refuses — so it has to be
    named there like any other path. Pins the deliberate choice of ``iterdir``
    over ``tree_scan.iter_tree`` against a well-meaning later "fix".
    """
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    assert preflight_gaps(template=tmp_path) == {".gitignore"}


def test_directories_are_reported_not_just_files(tmp_path):
    """The scaffold's top level is mostly directories; a file-only walker would
    make this check nearly vacuous."""
    (tmp_path / "vault").mkdir()
    assert preflight_gaps(template=tmp_path) == {"vault"}


def test_a_reworded_preflight_fails_loudly_rather_than_passing_empty():
    """An extractor that silently found nothing would make every gap invisible."""
    with pytest.raises(AssertionError, match="re-pick the anchor"):
        preflight_paths(skill_text="The setup skill no longer describes a preflight.")


def test_an_undelimited_preflight_fails_loudly():
    with pytest.raises(AssertionError, match="can no longer be delimited"):
        preflight_paths(
            skill_text="The scaffold lands only on clean ground: `nodes/`, `story/`."
        )
