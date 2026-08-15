#!/usr/bin/env python3
"""Check the wiki against its schema (wiki-schema.md).

The wiki passes if:
  1. Every wiki page parses a YAML frontmatter block.
  2. Every frontmatter block carries a non-empty `type`.
  3. Every reserved file (index.md, log.md) follows its conventions.

Missing recommended fields (`title`, `description`) are reported as warnings,
never failures.

    python3 scripts/wiki-check.py [--warnings]
"""

import re
import sys

import wiki_bundle as wiki


def check_pages():
    errors, warnings = [], []
    for path in wiki.page_paths():
        fm, _ = wiki.load(path)
        if fm is None:
            errors.append(f"{path}: no parseable YAML frontmatter block")
            continue
        if not str(fm.get("type", "")).strip():
            errors.append(f"{path}: frontmatter has no non-empty `type`")
        for field in ("title", "description"):
            if not str(fm.get(field, "")).strip():
                warnings.append(f"{path}: no `{field}` (recommended)")
    return errors, warnings


def check_index(path, body, fm):
    """Index files list their directory's contents, with no frontmatter."""
    errors = []
    if fm is not None:
        errors.append(f"{path}: index files carry no frontmatter")
    if not re.search(r"^#+ .+$", body, re.M):
        errors.append(f"{path}: no section headings")
    if not re.search(r"^\s*[*-] \[.+\]\(.+\)", body, re.M):
        errors.append(f"{path}: no linked entries")
    return errors


def check_log(path, body, fm):
    """Date-grouped entries under ISO 8601 `## YYYY-MM-DD` headings.

    A log with no entries yet is fine; every heading it does have must be a
    date."""
    errors = []
    if fm is not None:
        errors.append(f"{path}: log files carry no frontmatter")
    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.M)
    for h in headings:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", h):
            errors.append(f"{path}: heading '{h}' is not ISO 8601 YYYY-MM-DD")
    return errors


def check_reserved():
    errors = []
    for path in wiki.reserved_paths():
        fm, body = wiki.load(path)
        if path.endswith("index.md"):
            errors += check_index(path, body, fm)
        else:
            errors += check_log(path, body, fm)
    return errors


def main():
    show_warnings = "--warnings" in sys.argv
    errors, warnings = check_pages()
    errors += check_reserved()

    pages = len(wiki.page_paths())
    reserved = len(wiki.reserved_paths())

    for e in errors:
        print(f"FAIL  {e}")
    if show_warnings:
        for w in warnings:
            print(f"warn  {w}")

    print(f"\n{pages} wiki pages, {reserved} reserved files checked.")
    if errors:
        print(f"CHECK FAILED — {len(errors)} error(s).")
        return 1
    suffix = "" if show_warnings else f" ({len(warnings)} warnings; --warnings)"
    print(f"Wiki checks pass{suffix}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
