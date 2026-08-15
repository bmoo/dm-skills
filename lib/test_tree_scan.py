"""The shared tree-walking guard, and the check that nothing bypasses it.

Two halves: the behavioural half proves a
worktree checkout on disk is invisible to the scanning entry points — the
concrete failure the issue reported, rebuilt in a `tmp_path` repo. The source
half asserts no module under `lib/` walks the filesystem on its own again, which
is the part that actually keeps the fix from decaying: routing today's two
walkers through `tree_scan` does nothing about tomorrow's third one.
"""

from pathlib import Path

import pytest

from encounter_meta_spec import SPEC_FILE, restatements
from tree_scan import is_ignored, iter_tree

REPO_ROOT = Path(__file__).resolve().parent.parent

# `tree_scan` itself is where the walking lives; the guard below allows it there
# and nowhere else under `lib/`. Note the sweep also covers `lib/mechanical-checker/`
# and `lib/judgement-checker/`, which *ship* — `tree_scan` does not, so a walk that
# genuinely belongs in a shipped checker earns a row here rather than an import.
_WALKER_ALLOWLIST = {
    "tree_scan.py",
    # Shipped consumer tooling, not a maintainer test: it walks the consumer's
    # campaign repo (rooted at its own parent directory), never this repo's
    # tree, so the worktree phantom cannot reach it.
    "wiki_bundle.py",
}

# The calls that reach the filesystem directly, bypassing the shared exclusion.
# Assembled from parts rather than written whole so that this module — which has
# to name what it forbids — does not match its own guard, and stays covered by it.
_WALKER_CALLS = tuple(f"{name}(" for name in (".rglob", ".glob", "os.walk", "glob.glob"))

# The directories that *materialise* into every consumer repo: in this repo each
# generator's `scripts/` reaches them by symlink, at the consumer they are real
# copies with nothing above them. Nothing under here may import a module that
# stays behind.
_SHIPPED_DIRS = ("mechanical-checker", "judgement-checker")


def _fake_worktree(tree: Path) -> Path:
    """The thing an agent run with worktree isolation leaves behind: a full,
    untracked checkout of the library under a dot-directory."""
    worktree = tree / ".claude" / "worktrees" / "agent-deadbeef"
    worktree.mkdir(parents=True)
    return worktree


def test_iter_tree_skips_dot_directories_and_build_artifacts(tmp_path):
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "real.md").write_text("shipped", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "stale.pyc").write_text("junk", encoding="utf-8")
    worktree = _fake_worktree(tmp_path)
    (worktree / "copy.md").write_text("a worktree's own copy", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in iter_tree(tmp_path)]

    assert found == ["skills/real.md"]


def test_iter_tree_honours_the_pattern_and_yields_only_files(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("prose", encoding="utf-8")
    (tmp_path / "docs" / "script.py").write_text("code", encoding="utf-8")

    found = [p.relative_to(tmp_path).as_posix() for p in iter_tree(tmp_path, "**/*.md")]

    assert found == ["docs/note.md"]


@pytest.mark.parametrize(
    "relative",
    [".claude/worktrees/agent-1/skills/x.md", ".git/config", "a/__pycache__/x.pyc"],
)
def test_is_ignored_catches_every_excluded_shape(relative):
    assert is_ignored(Path(relative))


def test_is_ignored_passes_shipped_content():
    assert not is_ignored(Path("skills/build-session/session-page-format.md"))


def test_a_worktree_checkout_does_not_read_as_a_spec_violation(tmp_path):
    """A concrete failure: three finished agent worktrees on disk, and
    `test_nothing_restates_the_template` reports each worktree's own copy of the
    spec as a restatement of the template the spec legitimately carries."""
    spec = tmp_path / SPEC_FILE
    spec.parent.mkdir(parents=True)
    spec_text = (REPO_ROOT / SPEC_FILE).read_text(encoding="utf-8")
    spec.write_text(spec_text, encoding="utf-8")

    worktree_copy = _fake_worktree(tmp_path) / SPEC_FILE
    worktree_copy.parent.mkdir(parents=True)
    worktree_copy.write_text(spec_text, encoding="utf-8")

    assert restatements(tmp_path) == []


def test_no_module_under_lib_walks_the_tree_on_its_own():
    """The half that keeps the fix alive. A new test that reaches for `rglob`
    directly reintroduces the raw walk in a fresh place, silently — worktrees only exist
    on the machine that ran an isolated agent, so the phantom failure shows up
    for one person and nobody else can reproduce it."""
    offenders = []
    for path in iter_tree(REPO_ROOT / "lib", "**/*.py"):
        if path.name in _WALKER_ALLOWLIST:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            code = line.split("#", 1)[0]
            if any(call in code for call in _WALKER_CALLS):
                offenders.append(
                    f"{path.relative_to(REPO_ROOT).as_posix()}:{number}: {line.strip()}"
                )

    assert offenders == [], (
        "walk the tree through tree_scan.iter_tree, which excludes agent "
        "worktrees and build artifacts, rather than globbing directly:\n"
        + "\n".join(offenders)
    )


def _maintainer_side_modules() -> set[str]:
    """The importable names that live at the `lib/` top level and stay there.

    Derived from the directory rather than written out, so this module — which
    imports two of them itself — cannot match its own guard, and so a new
    maintainer module inherits the check the day it is added."""
    return {path.stem for path in iter_tree(REPO_ROOT / "lib", "*.py")}


def test_no_shipped_module_imports_a_maintainer_side_module():
    """This is the sibling gap to the walker check above. That one forbids a shipped
    file from *calling* a raw walker; this one forbids it from *importing* the
    walker that already exists, which is how `fbfe586` reached `tree_scan` from
    `lib/mechanical-checker/test_checker.py` and broke collection in every
    vendored copy while `pytest lib/` — where `lib/` is on the path — stayed green.

    Scope is the shipped dirs only: maintainer code importing maintainer code is
    ordinary, and maintainer code importing *shipped* code is the allowed
    direction. Only the upward reach out of a shipping directory is the fault."""
    maintainer = _maintainer_side_modules()
    offenders = []
    for shipped_dir in _SHIPPED_DIRS:
        for path in iter_tree(REPO_ROOT / "lib" / shipped_dir, "**/*.py"):
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                code = line.split("#", 1)[0]
                words = code.replace(",", " ").split()
                if not words or words[0] not in ("import", "from"):
                    continue
                imported = words[1].split(".", 1)[0] if len(words) > 1 else ""
                if imported in maintainer:
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT).as_posix()}:{number}: {line.strip()}"
                    )

    assert offenders == [], (
        "these directories materialise into every consumer repo, where the `lib/` "
        "top level does not exist — a module that stays behind cannot be imported "
        "from one that ships. Move the check that needs it up to `lib/` instead:\n"
        + "\n".join(offenders)
    )
