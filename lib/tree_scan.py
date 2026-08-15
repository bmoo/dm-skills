"""Shared guard for `pytest lib/` tests that walk the repo tree.

Worktree-isolated agents (`.claude/worktrees/agent-<id>/`) leave a full checkout
of the tree on disk that is not tracked by git but *is* visible to a plain
`Path.rglob`/`Path.glob`. A test that walks the tree without excluding dot-
directories picks up every worktree's own copy of whatever it's scanning for —
a spec violation or a stale declaration in the worktree's checkout reads as one
in the library itself. `.git/`, `.claude/`, and build artifacts like
`__pycache__` are never shipped content; no tree-walking test should see them.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

_IGNORE_PREFIXES = (".", "__pycache__")


def is_ignored(path: Path) -> bool:
    """True if any component of ``path`` is a dot-directory (`.git`, `.claude`, …)
    or a build artifact (`__pycache__`). Pass a path relative to the tree being
    walked: an absolute path under a dot-directory somewhere above the repo (a
    checkout inside `~/.local/`, say) reads as ignored when nothing in the repo
    is."""
    return any(part.startswith(_IGNORE_PREFIXES) for part in path.parts)


def iter_tree(root: Path, pattern: str = "**/*") -> Iterator[Path]:
    """Every file under ``root`` matching ``pattern``, skipping dot-directories
    and build artifacts. The one place tree-walking tests should walk from."""
    for path in sorted(root.glob(pattern)):
        if not path.is_file():
            continue
        if is_ignored(path.relative_to(root)):
            continue
        yield path
