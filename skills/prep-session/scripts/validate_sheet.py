#!/usr/bin/env python3
"""Format lint for prep-session sheets.

Checks the three shape rules the skill text states. It says nothing about
content — whether the cues are minimal, the secrets abstract, or the fights
worth costing is the DM's read, not this script's:

  1. The sheet opens title → *Contents:* line → `## Strong Start`; nothing
     else precedes the Strong Start.
  2. H2 headings are unnumbered.
  3. Whole-line italic paragraphs appear nowhere except the single
     *Contents:* jump bar (footnotes, coverage notes, epigraphs, and stray
     link lines are exactly the clutter this catches).

Usage: validate_sheet.py sessions/<slug>.md
Exit 0 when clean; exit 1 with one line per violation otherwise.
"""

import argparse
import re
import sys
from pathlib import Path


def strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def is_whole_line_italic(line):
    s = line.strip()
    # *...* or _..._ spanning the whole line, but not bold (**...**)
    # and not a list bullet ("* item").
    if re.fullmatch(r"\*[^*].*[^*]\*", s) and not s.startswith("* "):
        return True
    if re.fullmatch(r"_[^_].*[^_]_", s):
        return True
    return False


def lint(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = strip_frontmatter(lines)

    errors = []
    contents_seen = False
    first_h2 = None
    body_before_first_h2 = []

    for n, line in enumerate(lines[start:], start=start + 1):
        s = line.strip()
        in_callout = s.startswith(">")

        if s.startswith("## ") and first_h2 is None:
            first_h2 = (n, s)

        if not in_callout and is_whole_line_italic(line):
            if s.startswith("*Contents:") and not contents_seen:
                contents_seen = True
            else:
                errors.append(
                    f"{path}:{n}: whole-line italic note — sections carry "
                    f"only their step's content; delete it or fold the fact "
                    f"into a cue, a table row, or chat: {s[:80]}"
                )

        if re.match(r"^##\s+\d", s):
            errors.append(f"{path}:{n}: numbered H2 — headings are unnumbered: {s}")

        if first_h2 is None and s and not in_callout:
            if not (s.startswith("# ") or s.startswith("*Contents:")):
                body_before_first_h2.append((n, s))

    if not contents_seen:
        errors.append(f"{path}: no *Contents:* jump bar line found")
    if first_h2 is None:
        errors.append(f"{path}: no H2 sections found")
    elif first_h2[1] != "## Strong Start":
        errors.append(
            f"{path}:{first_h2[0]}: first H2 must be '## Strong Start', "
            f"found: {first_h2[1]}"
        )
    for n, s in body_before_first_h2:
        errors.append(
            f"{path}:{n}: content before the Strong Start — the sheet opens "
            f"title, Contents line, Strong Start: {s[:80]}"
        )
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    args = parser.parse_args()
    errors = lint(args.sheet)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"{args.sheet}: OK")


if __name__ == "__main__":
    main()
