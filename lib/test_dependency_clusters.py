"""The dependency-cluster guard, run two ways.

Unit tests drive ``dependency_clusters`` against a synthetic repo so each failure
mode is *proven* to fail — an undeclared cross-skill load, a declaration left
behind after the load went away, a README install command that no longer covers
a cluster. The tree tests then run it over the real repo, which is what gates a
commit: ``pytest lib/`` is the gate.

Like ``test_citation_anchors.py`` beside it, this lives at the ``lib/`` top level
rather than inside the shipped checker at
``skills/build-session/scripts/mechanical_checker/`` — that directory materialises
into every consumer, and a check over *this repo's* install-time
docs must not ship with it.
"""

from pathlib import Path

import pytest

from dependency_clusters import (
    declarations,
    hard_closure,
    install_command_gaps,
    install_commands,
    stale_declarations,
    tree_edges,
    undeclared_edges,
    unknown_skills,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# --- a synthetic repo, so every failure mode is exercised in isolation ---------

TABLE_HEADER = """## Dependency clusters — what a selective install needs

| Skill | Needs | Coupling | Without it |
|---|---|---|---|
"""

CONTRACT_TAIL = "\n## Sync obligations — maintainers only\n\nprose\n"

README_HEAD = "# repo\n\n### Dependency clusters — install these together\n\n```bash\n"
README_TAIL = "```\n\n## Roster\n\nprose\n"


def _repo(tmp_path, rows, commands, sources):
    """A miniature repo: three skills, a contract table, a README cluster block."""
    for name in ("alpha", "beta", "gamma"):
        skill = tmp_path / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(sources.get(name, "# skill\n"), encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "campaign-contract.md").write_text(
        TABLE_HEADER + "".join(rows) + CONTRACT_TAIL, encoding="utf-8"
    )
    (tmp_path / "README.md").write_text(
        README_HEAD
        + "".join(f"# a cluster\nnpx skills add repo {command}\n" for command in commands)
        + README_TAIL,
        encoding="utf-8",
    )
    return tmp_path


def _row(skill, needs, kind, strength):
    return f"| `{skill}` | `{needs}` | {kind} — {strength} | prose |\n"


LOADS_BETA = {"alpha": "Open beta's [`doctrine.md`](../beta/doctrine.md) now.\n"}


def test_declared_load_that_exists_passes(tmp_path):
    repo = _repo(
        tmp_path,
        [_row("alpha", "beta", "load", "hard")],
        ["--skill alpha --skill beta"],
        LOADS_BETA,
    )
    assert undeclared_edges(repo) == []
    assert stale_declarations(repo) == []
    assert install_command_gaps(repo) == []


def test_undeclared_cross_skill_load_is_reported(tmp_path):
    """The failure the guard exists for: a new sibling load nobody declared."""
    repo = _repo(tmp_path, [], ["--skill alpha"], LOADS_BETA)
    problems = undeclared_edges(repo)
    assert len(problems) == 1
    assert "no row in" in problems[0]
    assert "skills/alpha/SKILL.md:1" in problems[0]


def test_a_path_on_a_delegate_row_is_reported(tmp_path):
    """A delegate edge invokes a skill and touches no files, so a relative path
    into it means the row is mis-typed or the skill text changed under it."""
    repo = _repo(
        tmp_path,
        [_row("alpha", "beta", "delegate", "hard")],
        ["--skill alpha --skill beta"],
        LOADS_BETA,
    )
    problems = undeclared_edges(repo)
    assert len(problems) == 1
    assert "declared a delegate edge" in problems[0]


def test_declaration_left_behind_after_the_load_went_away(tmp_path):
    """A prior interface change converted a load into a delegate invocation; without this half the row
    would sit in the table forever, naming an install nobody needs."""
    repo = _repo(tmp_path, [_row("alpha", "beta", "load", "hard")], ["--skill alpha --skill beta"], {})
    problems = stale_declarations(repo)
    assert len(problems) == 1
    assert "no `../beta/` path survives" in problems[0]


def test_a_delegate_row_with_no_path_is_fine(tmp_path):
    """Delegate and citation edges are prose, not paths — the stale check must not
    demand a relative link they were never supposed to write."""
    repo = _repo(
        tmp_path,
        [_row("alpha", "beta", "delegate", "hard"), _row("alpha", "gamma", "citation", "none")],
        ["--skill alpha --skill beta"],
        {},
    )
    assert stale_declarations(repo) == []
    assert undeclared_edges(repo) == []


def test_install_command_missing_a_cluster_member_is_reported(tmp_path):
    repo = _repo(tmp_path, [_row("alpha", "beta", "load", "hard")], ["--skill alpha"], LOADS_BETA)
    problems = install_command_gaps(repo)
    assert len(problems) == 1
    assert "`alpha`" in problems[0] and "`beta`" in problems[0]


def test_hard_dependencies_close_transitively(tmp_path):
    """gamma → alpha → beta: installing gamma has to bring beta too, and the
    README command is held to the closure, not just the direct edge."""
    repo = _repo(
        tmp_path,
        [_row("alpha", "beta", "load", "hard"), _row("gamma", "alpha", "delegate", "hard")],
        ["--skill alpha --skill beta", "--skill gamma --skill alpha"],
        LOADS_BETA,
    )
    assert hard_closure(repo)["gamma"] == {"alpha", "beta"}
    problems = install_command_gaps(repo)
    assert len(problems) == 1 and "`gamma`" in problems[0]


def test_a_degrading_dependency_needs_no_install_command(tmp_path):
    """The honest half: a guarded edge is a real edge and still gets declared, but
    it must not force a cluster into the README."""
    repo = _repo(tmp_path, [_row("alpha", "beta", "load", "degrades")], [], LOADS_BETA)
    assert install_command_gaps(repo) == []
    assert undeclared_edges(repo) == []


def test_unknown_skill_in_a_row_is_reported(tmp_path):
    repo = _repo(tmp_path, [_row("alpha", "delta", "delegate", "hard")], ["--skill alpha --skill delta"], {})
    problems = unknown_skills(repo)
    assert len(problems) == 1 and "not in skills/" in problems[0]


def test_a_row_that_does_not_parse_raises(tmp_path):
    repo = _repo(tmp_path, ["| `alpha` | beta | load — hard | prose |\n"], [], {})
    with pytest.raises(ValueError, match="does not parse"):
        declarations(repo)


def test_an_unknown_coupling_raises(tmp_path):
    repo = _repo(tmp_path, [_row("alpha", "beta", "imports", "hard")], [], {})
    with pytest.raises(ValueError, match="unknown coupling"):
        declarations(repo)


def test_a_reference_to_a_non_skill_directory_is_ignored(tmp_path):
    """`../../docs/…` and `../../scripts/…` are everywhere in the rubrics and
    corpora; only sibling *skills* are install-time edges."""
    repo = _repo(tmp_path, [], [], {"alpha": "See [inventory](../../docs/eval.md).\n"})
    assert tree_edges(repo) == {}
    assert undeclared_edges(repo) == []


# --- the gate: the same guard over the real tree ------------------------------


def test_tree_every_cross_skill_reference_is_declared():
    problems = undeclared_edges()
    assert not problems, "\n".join(problems)


def test_tree_carries_no_stale_declarations():
    problems = stale_declarations()
    assert not problems, "\n".join(problems)


def test_tree_readme_install_commands_cover_every_cluster():
    problems = install_command_gaps()
    assert not problems, "\n".join(problems)


def test_tree_declarations_name_real_skills():
    problems = unknown_skills()
    assert not problems, "\n".join(problems)


def test_tree_declares_the_spotlight_edge():
    """A smoke test with teeth: the load edge the spotlight merge left. If
    this row vanishes, the table was replaced by something the parser silently
    accepts."""
    edges = {(row.skill, row.needs): row for row in declarations()}
    assert edges[("party-sync", "build-session")].kind == "load"
    assert edges[("party-sync", "build-session")].strength == "degrades"
    # The generator merge removed the last hard edge; the README's cluster
    # section went with it, and only a returning hard row may demand it back.
    assert hard_closure() == {}
