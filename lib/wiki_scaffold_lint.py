"""Maintainer guard: the shipped wiki scaffold still bootstraps cleanly.

The `setup` skill's wiki-bootstrap phase copies ``lib/wiki-scaffold/template/``
verbatim into a consumer's fresh campaign repo, generates the catalog, and
declares the phase done only when conformance passes with zero errors and zero
warnings. That last clause is a promise about *committed content*, and it is the
one promise in the phase nobody can keep by asking the DM: every other step
either the agent performs or the DM answers, but "the template is internally
consistent with its own schema" is true or false the moment the template is
committed.

Two assertions, derived from the inventory rows of the same names — see
*Static lints* in ``docs/eval-assertion-inventory.md``
(``lint/wiki-scaffold-starts-green``, ``lint/wiki-scaffold-preflight-covers-template``):

``starts_green``
    copy the template to a scratch directory, run its own ``wiki-index.py``,
    then its own ``wiki-check.py --warnings``. Both must exit 0. This runs the
    shipped scripts rather than reimplementing their rules, so the schema and
    its checker can evolve together without this guard needing to learn them —
    it only pins that they still agree about the seed content.

``preflight_gaps``
    the skill's preflight names the top-level paths it refuses to overwrite
    (`setup/SKILL.md` — "The scaffold lands only on clean ground"). Every
    top-level entry the template actually ships must be on that list, or the
    copy step would write over a path the preflight promised to guard. The
    comparison is one-directional — ``index.md`` is named without shipping,
    since ``wiki-index.py`` generates it on the first run — so an *extra* named
    path is fine and a *missing* one is not.

**Deliberately dumb**, in the spirit of ``dependency_clusters`` and
``retired_phrases``. It does not read the schema, grade a page, or judge the
seed prose. It pins the two facts that go stale when someone edits the template
without rerunning the bootstrap by hand: the seed content stops conforming, or a
new top-level file slips past the preflight list.

Lives at the ``lib/`` top level, outside ``lib/wiki-scaffold/``, for the reason
``test_symlink_integrity`` spells out: that directory materialises into every
consumer, and this is a check over *this repo's* committed template. It runs
here (``pytest lib/``) and never ships.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "lib" / "wiki-scaffold" / "template"
SETUP_SKILL = REPO_ROOT / "skills" / "setup" / "SKILL.md"

# The preflight sentence runs from the clean-ground rule to the clause that says
# what happens when a path is already there. Everything in backticks between the
# two is a guarded path.
_PREFLIGHT_OPEN = "The scaffold lands only on clean ground"
_PREFLIGHT_CLOSE = "already exists at the"
_CODE_SPAN = re.compile(r"`([^`]+)`")


@dataclass(frozen=True)
class ScaffoldRun:
    """What the shipped scripts did to a scratch copy."""

    index: subprocess.CompletedProcess[str]
    check: subprocess.CompletedProcess[str]

    @property
    def clean(self) -> bool:
        return self.index.returncode == 0 and self.check.returncode == 0

    def report(self) -> str:
        lines = []
        for label, proc in (("wiki-index.py", self.index), ("wiki-check.py --warnings", self.check)):
            lines.append(f"  {label} → exit {proc.returncode}")
            for stream in (proc.stdout, proc.stderr):
                for line in (stream or "").splitlines():
                    if line.strip():
                        lines.append(f"    {line}")
        return "\n".join(lines)


def _run(script: str, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{script}", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def starts_green(template: Path = TEMPLATE) -> ScaffoldRun:
    """Bootstrap the template in a scratch dir exactly as the skill's phase does.

    The skill sets ``WIKI_TITLE`` between the copy and the index run; that edit is
    the DM's campaign name and changes no page's conformance, so the run here uses
    the committed default.
    """
    with tempfile.TemporaryDirectory(prefix="wiki-scaffold-lint-") as scratch:
        root = Path(scratch) / "campaign"
        # Dereferencing, not link-preserving: the skill copies the template's
        # *contents* and the CLI dereferences the skill's own symlink on install,
        # so what a consumer gets is always real files.
        shutil.copytree(template, root)
        index = _run("wiki-index.py", root)
        check = _run("wiki-check.py", root, "--warnings")
    return ScaffoldRun(index=index, check=check)


def preflight_paths(skill_text: str | None = None) -> set[str]:
    """The top-level paths the setup skill's preflight promises to refuse to overwrite."""
    text = skill_text if skill_text is not None else SETUP_SKILL.read_text(encoding="utf-8")
    start = text.find(_PREFLIGHT_OPEN)
    if start == -1:
        raise AssertionError(
            f"{SETUP_SKILL.relative_to(REPO_ROOT)} no longer says {_PREFLIGHT_OPEN!r} — "
            "the preflight was reworded; re-pick the anchor here and in the inventory row"
        )
    end = text.find(_PREFLIGHT_CLOSE, start)
    if end == -1:
        raise AssertionError(
            f"{SETUP_SKILL.relative_to(REPO_ROOT)}'s preflight no longer closes with "
            f"{_PREFLIGHT_CLOSE!r} — the guarded-path list can no longer be delimited"
        )
    return {span.rstrip("/") for span in _CODE_SPAN.findall(text[start:end])}


def shipped_top_level(template: Path = TEMPLATE) -> set[str]:
    """Every top-level entry the committed template lands in the consumer's root.

    Walks with ``iterdir`` rather than ``tree_scan.iter_tree``, which the other
    tree-walking guards here use. Two reasons, both specific to this question:
    ``iter_tree`` yields files only, and the scaffold's top level is mostly
    *directories* (`nodes/`, `story/`, `sessions/`, `players/`, `scripts/`) — so
    routing through it would drop the paths most worth guarding. And it skips
    dotfiles, which is the wrong exclusion here: a `.gitignore` added to the
    template would land in the consumer's root and silently overwrite theirs,
    which is precisely the clobber the preflight exists to refuse. A dotfile
    appearing here *should* fail until it is named.
    """
    return {child.name for child in template.iterdir()}


def preflight_gaps(template: Path = TEMPLATE, skill_text: str | None = None) -> set[str]:
    """Shipped top-level paths the preflight forgets to guard. Empty is the pass."""
    return shipped_top_level(template) - preflight_paths(skill_text)


def main() -> int:
    failures = 0

    run = starts_green()
    if run.clean:
        print("wiki-scaffold starts green: a fresh copy indexes and checks clean.")
    else:
        failures += 1
        print("wiki-scaffold does NOT start green:")
        print(run.report())

    gaps = preflight_gaps()
    if gaps:
        failures += 1
        print(
            "preflight list misses shipped top-level paths: "
            + ", ".join(sorted(gaps))
        )
    else:
        print(
            f"preflight guards every shipped top-level path ({len(shipped_top_level())} of them)."
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
