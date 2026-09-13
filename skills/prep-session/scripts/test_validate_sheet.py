"""Fixture-driven units for the prep-sheet format lint."""

import subprocess
import sys
from pathlib import Path

from validate_sheet import lint

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def _run(fixture):
    return subprocess.run(
        [sys.executable, str(HERE / "validate_sheet.py"), str(FIXTURES / fixture)],
        capture_output=True, text=True,
    )


def test_good_sheet_passes():
    result = _run("sheet_good.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().endswith("OK")


def test_bad_sheet_reports_each_shape_break():
    result = _run("sheet_bad.md")
    assert result.returncode == 1
    out = result.stdout
    assert "content before the Strong Start" in out
    assert "numbered H2" in out
    assert "first H2 must be '## Strong Start'" in out
    assert "whole-line italic note" in out


def test_lint_is_silent_on_the_good_sheet():
    assert lint(FIXTURES / "sheet_good.md") == []


def test_nested_encounter_block_is_not_a_finding():
    # Callout lines (including nested `> >` blocks) are never read as italics
    # or as body before the Strong Start.
    errors = lint(FIXTURES / "sheet_good.md")
    assert not any("encounter" in e for e in errors)


def test_missing_contents_line_is_a_finding(tmp_path):
    sheet = tmp_path / "s.md"
    sheet.write_text("# T\n\n## Strong Start\n\nGo.\n", encoding="utf-8")
    errors = lint(sheet)
    assert any("no *Contents:* jump bar" in e for e in errors)
