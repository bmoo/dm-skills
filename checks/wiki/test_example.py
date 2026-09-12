"""Keep the populated example conformant and synchronized with its scaffold."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from wiki_scaffold_lint import REPO_ROOT, TEMPLATE

EXAMPLE = REPO_ROOT / "examples" / "emberwick-vale"
CONFIG = Path("scripts/okf_config.py")
# Spell out the shipped set so accidentally omitting an entire script or inbox
# from both sides cannot turn the copy contract into a vacuous comparison.
COPIED = (
    Path("wiki-schema.md"),
    *(Path("scripts") / name for name in (
        "okf-check.py", "okf-index.py", "okf-groom.py", "okf-migrate.py",
        "okf_bundle.py", "okf_config.py",
    )),
    *(Path(directory) / filename for directory, filename in (
        ("nodes/events", "events-seed-ideas.md"),
        ("nodes/factions", "factions-seed-ideas.md"),
        ("nodes/locations", "locations-seed-ideas.md"),
        ("nodes/npcs", "npcs-seed-ideas.md"),
        ("players", "players-seed-ideas.md"),
        ("sessions", "sessions-seed-ideas.md"),
        ("story", "story-seed-ideas.md"),
    )),
)


def scaffold_drift(template: Path, example: Path) -> list[Path]:
    drift = []
    for relative in COPIED:
        source, copy = template / relative, example / relative
        if not source.is_file() or not copy.is_file():
            drift.append(relative)
            continue
        expected = source.read_bytes()
        if relative == CONFIG:
            expected = expected.replace(
                b'WIKI_TITLE = "Campaign Wiki"\n',
                b'WIKI_TITLE = "The Emberwick Vale"\n',
            )
        if copy.read_bytes() != expected:
            drift.append(relative)
    return drift


def test_example_starts_green_over_the_real_tree():
    # Check committed catalogs before conformance; never regenerate away drift.
    for script, flag in (("okf-index.py", "--check"), ("okf-check.py", "--strict")):
        result = subprocess.run(
            [sys.executable, str(EXAMPLE / "scripts" / script), flag],
            cwd=EXAMPLE, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


def test_example_scaffold_matches_template_over_the_real_tree():
    assert not scaffold_drift(TEMPLATE, EXAMPLE)
    assert {p.name for p in (EXAMPLE / "scripts").glob("*.py")} == {
        p.name for p in COPIED if p.parent == Path("scripts")
    }


@pytest.mark.parametrize("relative", COPIED, ids=str)
def test_uncopied_template_edit_is_reported(tmp_path, relative):
    template, example = tmp_path / "template", tmp_path / "example"
    shutil.copytree(TEMPLATE, template)
    shutil.copytree(EXAMPLE, example)
    with (template / relative).open("ab") as target:
        target.write(b"\nUncopied template edit\n")
    assert scaffold_drift(template, example) == [relative]


def test_only_the_example_title_is_allowed_to_differ(tmp_path):
    example = tmp_path / "example"
    shutil.copytree(EXAMPLE, example)
    config = example / CONFIG
    config.write_text(config.read_text().replace('BUNDLE_ROOT = "."', 'BUNDLE_ROOT = "wiki"'))
    assert scaffold_drift(TEMPLATE, example) == [CONFIG]
