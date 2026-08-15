"""The retired-phrase denylist, run two ways.

Unit tests drive ``retired_phrases`` against a synthetic tree, so a surviving
phrase is *proven* to fail. The tree tests then run the list over the real repo —
``pytest lib/`` is the gate, the same one the anchor check uses.

Two of these guard the **list itself** rather than the tree, because a denylist
fails silently in both directions: an empty list passes vacuously forever, and an
entry for a phrase that was never in the tree guards nothing. So the list must be
non-empty, and every entry must be quotable from the diff of the commit it names
when that history is present. Entries sealed in ``PRE_PUBLIC_CUT`` predate this
repo's orphan release and name private predecessor commits; the tree-absence
sweep still enforces them, but the provenance tests apply only to entries added
since the cut.
"""

import re
import subprocess

import pytest

import retired_phrases
from retired_phrases import (
    PRE_PUBLIC_CUT,
    RETIRED,
    REPO_ROOT,
    RetiredPhrase,
    surviving_phrases,
    tracked_text_files,
)

# Entries added since the public cut — the only ones whose provenance this
# repo's history can vouch for.
POST_CUT = [phrase for phrase in RETIRED if phrase.retired_by not in PRE_PUBLIC_CUT]


def _post_cut_or_skip():
    if not POST_CUT:
        pytest.skip("every entry predates the public cut; no local provenance to check")
    return POST_CUT

GONE = RetiredPhrase("the spotlight plan is on the page, not in chat", "ab0d0cb", "why")


@pytest.fixture
def tree(tmp_path):
    """A miniature tracked repo — the sweep reads `git ls-files`, so the fixture
    has to be a real one."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def _commit(tree, name, text):
    (tree / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=tree, check=True)
    return name


# --- the failure mode the list exists for ------------------------------------


def test_surviving_retired_phrase_fails(tree):
    _commit(tree, "skill.md", "Every PC has a beat; the spotlight plan is on the page, not in chat.\n")
    survivors = surviving_phrases(repo_root=tree, phrases=[GONE])
    assert len(survivors) == 1
    assert survivors[0].path == "skill.md"
    assert "retired phrase survives" in str(survivors[0])
    assert "ab0d0cb" in str(survivors[0])


def test_tree_without_the_phrase_passes(tree):
    _commit(tree, "skill.md", "The plan is transient prep-run state.\n")
    assert surviving_phrases(repo_root=tree, phrases=[GONE]) == []


def test_wrapped_phrase_is_still_found(tree):
    """The seeded phrases are hard-wrapped in the source they came from — this one
    lived across two lines of a checklist box, so a byte-literal grep would miss
    the very phrase the list is seeded from."""
    _commit(
        tree,
        "skill.md",
        "- [ ] Every PC has a beat or is named resting; the spotlight plan is on\n"
        "      the page, not in chat.\n",
    )
    assert len(surviving_phrases(repo_root=tree, phrases=[GONE])) == 1


def test_a_phrase_surviving_in_two_files_reports_both(tree):
    _commit(tree, "one.md", "the spotlight plan is on the page, not in chat\n")
    _commit(tree, "two.md", "the spotlight plan is on the page, not in chat\n")
    assert {s.path for s in surviving_phrases(repo_root=tree, phrases=[GONE])} == {
        "one.md",
        "two.md",
    }


def test_untracked_and_binary_files_are_not_swept(tree):
    _commit(tree, "tracked.md", "clean\n")
    (tree / "untracked.md").write_text("the spotlight plan is on the page, not in chat\n")
    (tree / "art.png").write_bytes(b"\x89PNG the spotlight plan is on the page, not in chat")
    subprocess.run(["git", "add", "art.png"], cwd=tree, check=True)
    assert surviving_phrases(repo_root=tree, phrases=[GONE]) == []


def test_the_list_itself_is_not_swept():
    """The module and this test quote every retired phrase as data; sweeping them
    would make every entry fail against itself."""
    swept = tracked_text_files()
    assert "lib/retired_phrases.py" not in swept
    assert "lib/test_retired_phrases.py" not in swept
    assert "docs/campaign-contract.md" in swept  # the contract table is swept


# --- guards on the list, not the tree ----------------------------------------


def test_the_denylist_is_not_empty():
    """An empty denylist passes vacuously, forever, and looks exactly like a
    healthy one."""
    assert len(RETIRED) >= 2


def test_the_sealed_set_carries_no_dead_weight():
    """Every commit in PRE_PUBLIC_CUT is named by a live entry — a hash nothing
    references any more is clutter, and clutter in a sealed set invites edits."""
    assert set(PRE_PUBLIC_CUT) <= {phrase.retired_by for phrase in RETIRED}


def test_every_entry_names_a_commit_that_exists():
    for phrase in _post_cut_or_skip():
        assert subprocess.run(
            ["git", "cat-file", "-e", f"{phrase.retired_by}^{{commit}}"],
            cwd=REPO_ROOT,
            capture_output=True,
        ).returncode == 0, f"{phrase.retired_by} is not a commit in this repo"


def test_every_named_commit_is_reachable_from_main():
    """The squash-merge trap: a branch commit resolves fine in the working
    copy that wrote it and does not exist in a fresh clone, so the two tests
    around this one would pass for the author and fail in CI. Ancestry of `main`
    is the property that survives the clone — assert it directly rather than
    trusting the module docstring's instruction to name the squash."""
    post_cut = _post_cut_or_skip()
    main = subprocess.run(
        ["git", "rev-parse", "--verify", "main^{commit}"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    if main.returncode != 0:  # a checkout without the branch; nothing to compare
        pytest.skip("no local `main` to test ancestry against")
    for phrase in post_cut:
        assert subprocess.run(
            ["git", "merge-base", "--is-ancestor", phrase.retired_by, "main"],
            cwd=REPO_ROOT,
            capture_output=True,
        ).returncode == 0, (
            f"{phrase.retired_by} is not on main — name the squash commit as it "
            "landed, not the branch commit you wrote the change on"
        )


def test_every_entry_was_genuinely_removed_by_the_commit_it_names():
    """Rule 2 of the module docstring, enforced: a phrase that was never in the
    tree guards nothing and will never fire. Each entry has to be quotable from
    the removed side of its own commit's diff."""
    diffs: dict[str, str] = {}
    for phrase in _post_cut_or_skip():
        if phrase.retired_by not in diffs:
            raw = subprocess.run(
                ["git", "show", "--unified=0", "--format=", phrase.retired_by],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            removed = [
                line[1:]
                for line in raw.splitlines()
                if line.startswith("-") and not line.startswith("---")
            ]
            diffs[phrase.retired_by] = re.sub(r"\s+", " ", " ".join(removed))
        assert retired_phrases.normalise(phrase.text) in diffs[phrase.retired_by], (
            f'"{phrase.text}" is not on the removed side of {phrase.retired_by}'
        )


def test_entries_are_specific_enough_to_be_a_claim():
    """A two-word entry would fire on unrelated prose forever."""
    for phrase in RETIRED:
        assert len(phrase.text) >= 20, phrase.text
        assert phrase.why, f"{phrase.text} carries no reason"


# --- the gate: the list over the real tree ------------------------------------


def test_tree_carries_no_retired_contract_phrase():
    survivors = surviving_phrases()
    assert not survivors, "\n".join(str(survivor) for survivor in survivors)
