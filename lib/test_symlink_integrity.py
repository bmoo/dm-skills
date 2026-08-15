"""Build/CI guard: each skill's materialised ``lib/`` assets are
byte-identical to their canonical sources.

Three libraries ship this way — the deterministic ``mechanical-checker``,
the judgement-tier ``judgement-checker``, and the ``wiki-scaffold``
template assets the setup skill copies into a consumer repo. In-repo each
consuming skill reaches its library through a *relative symlink*. At the consumer
the ``skills`` CLI dereferences that symlink on install into a real, independent
copy (see the README beside each canonical library). We cannot test the
post-install dereference from here, so this in-repo integrity/byte-identity
assertion is the real guard against the silently-skipped broken symlink: it
actively resolves each symlink and compares the bytes reached through it to the
canonical files — it does not trust the symlink silently.

This test lives OUTSIDE the canonical library dirs on purpose: those directories
are what materialise into every consumer, and a symlink-integrity test's
``assert is_symlink()`` premise is structurally false at the consumer (where the
copy is a real directory). Keeping the guard one level up means it runs in this
repo (``pytest lib/``) but never ships.
"""

from pathlib import Path

import pytest

from tree_scan import iter_tree

REPO_ROOT = Path(__file__).resolve().parent.parent

# The checker libraries every generator links inside its scripts/ dir:
# (symlink name, canonical source dir under lib/).
LIBRARIES = [
    ("mechanical_checker", "mechanical-checker"),  # deterministic tier
    ("judgement_checker", "judgement-checker"),    # judgement tier
]

GENERATORS = ["combat-generator", "dungeon-generator", "build-session"]

# Every (skill, symlink path relative to the skill dir, canonical dir under
# lib/) the guard covers. Each new symlinked library adds a row here and
# inherits the same resolve-and-byte-identity guard.
_CASES = [
    (generator, f"scripts/{link_name}", canonical_dir)
    for generator in GENERATORS
    for link_name, canonical_dir in LIBRARIES
] + [
    # The wiki-bootstrap template assets, linked at the skill root.
    ("setup", "wiki-scaffold", "wiki-scaffold"),
]
_IDS = [f"{skill}:{Path(link).name}" for skill, link, _ in _CASES]


def _symlink_path(skill: str, link_rel: str) -> Path:
    return REPO_ROOT / "skills" / skill / link_rel


def _canonical_path(canonical_dir: str) -> Path:
    return REPO_ROOT / "lib" / canonical_dir


def _source_files(root: Path) -> list[Path]:
    """Every real file under ``root``, skipping build artifacts and dot-directories
    (``tree_scan`` owns that exclusion for every tree-walking test here),
    sorted by path relative to ``root`` for a stable comparison."""
    return sorted(iter_tree(root), key=lambda p: p.relative_to(root).as_posix())


@pytest.mark.parametrize("skill,link_rel,canonical_dir", _CASES, ids=_IDS)
def test_symlink_exists_and_is_a_symlink(skill, link_rel, canonical_dir):
    link = _symlink_path(skill, link_rel)
    assert link.is_symlink(), f"{link} is missing or not a symlink"


@pytest.mark.parametrize("skill,link_rel,canonical_dir", _CASES, ids=_IDS)
def test_symlink_resolves_inside_repo_to_canonical_lib(skill, link_rel, canonical_dir):
    link = _symlink_path(skill, link_rel)
    canonical = _canonical_path(canonical_dir)
    resolved = link.resolve()
    # inside the repo…
    assert REPO_ROOT in resolved.parents or resolved == REPO_ROOT, (
        f"{link} resolves to {resolved}, outside the repo"
    )
    # …and to exactly the canonical library.
    assert resolved == canonical.resolve(), (
        f"{link} resolves to {resolved}, not the canonical {canonical}"
    )


@pytest.mark.parametrize("skill,link_rel,canonical_dir", _CASES, ids=_IDS)
def test_files_reached_through_symlink_are_byte_identical(skill, link_rel, canonical_dir):
    link = _symlink_path(skill, link_rel)
    canonical_files = _source_files(_canonical_path(canonical_dir))
    assert canonical_files, "canonical library has no files to compare"

    canonical = _canonical_path(canonical_dir)
    for source in canonical_files:
        rel = source.relative_to(canonical)
        through_link = link / rel  # reached *through* the symlink, not the canonical path
        assert through_link.exists(), f"{rel} missing through {skill}'s {link_rel} symlink"
        assert through_link.read_bytes() == source.read_bytes(), (
            f"{rel} differs between {skill}'s {link_rel} symlink and the canonical lib"
        )
