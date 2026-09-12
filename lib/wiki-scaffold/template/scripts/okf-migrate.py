#!/usr/bin/env python3
"""Migrate legacy bundle metadata and local Markdown links in place.

Configure the source key, actor, mappings, and backfills in okf_config.py.
All rewrites are planned before writing; malformed metadata leaves the bundle
untouched. Missing provenance and unknown statuses remain for checker review.
"""

import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

import okf_config as config
from okf_bundle import (
    bundle_root, edit_frontmatter, first_heading, inferred_type, page_paths,
    parse_frontmatter, reserved_paths, rewrite_local_links, split_frontmatter,
)

LOG_HEADER = """<!--
Format: date-grouped entries, newest first (conventions: wiki-schema.md — Log conventions).
  ## YYYY-MM-DD
  * **Label**: summary
Labels: Creation, Update, Deprecation, Session, Lint.
-->"""
LIFECYCLE_TAGS = {"stub", "prep", "canon"}


def source_datetime(value):
    """Retain an offset timestamp exactly; expand a valid date at midnight UTC."""
    if not isinstance(value, str):
        raise ValueError("source timestamp must be a string")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        date.fromisoformat(value)
        return value + "T00:00:00Z"
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("source timestamp needs an explicit UTC offset")
    return value


def migrate_metadata(path, text):
    block, body = split_frontmatter(text)
    if block is None and text.startswith(("---\n", "---\r\n")):
        raise ValueError("unterminated frontmatter")
    fields = parse_frontmatter(block) if block is not None else {}
    if fields is None:
        raise ValueError("unparseable frontmatter")
    updates, remove = {}, []
    source_key = config.MIGRATION_SOURCE_KEY
    if source_key in fields:
        # Existing provenance wins; a duplicate obsolete timestamp is removed.
        if "generated" not in fields:
            updates["generated"] = {"by": config.MIGRATION_ACTOR, "at": source_datetime(fields[source_key])}
        remove.append(source_key)
    status = fields.get("status")
    if isinstance(status, str):
        if status in config.MIGRATION_STATUS_MAP:
            updates["status"] = config.MIGRATION_STATUS_MAP[status]
        if status in config.MIGRATION_DECISION_MAP:
            decision = config.MIGRATION_DECISION_MAP[status]
            if "decision" in fields and fields["decision"] != decision:
                raise ValueError("existing decision conflicts with the legacy ADR status")
            if "decision" not in fields:
                updates["decision"] = decision
    if "tags" in fields:
        if not isinstance(fields["tags"], list) or not all(isinstance(tag, str) for tag in fields["tags"]):
            raise ValueError("tags must be a list of strings")
        tags = [tag for tag in fields["tags"] if tag not in LIFECYCLE_TAGS]
        if tags != fields["tags"]:
            updates["tags"] = tags
    if config.MIGRATION_BACKFILL_TYPE and not fields.get("type"):
        page_type = inferred_type(path)
        if page_type:
            updates["type"] = page_type
    if config.MIGRATION_BACKFILL_TITLE and not fields.get("title"):
        title = first_heading(body)
        if title:
            updates["title"] = title
    return edit_frontmatter(text, updates, remove)


def migrate_text(path, text, *, reserved=False):
    """Pure per-file migration; target existence is read from the configured bundle."""
    if not reserved:
        text = migrate_metadata(path, text)
    if Path(path).name == "log.md":
        header = re.match(r"\A<!--\s*Format:.*?-->", text, re.S)
        if header:
            newline = "\r\n" if "\r\n" in text else "\n"
            text = LOG_HEADER.replace("\n", newline) + text[header.end():]
    # Metadata may contain URLs or Markdown examples: only rewrite body links.
    block, body = split_frontmatter(text)
    prefix = text[:len(text) - len(body)] if block is not None else ""
    return prefix + rewrite_local_links(path, body)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    root = Path(bundle_root())
    reserved = set(reserved_paths())
    plan, errors = [], []
    for relative in sorted(set(page_paths()) | reserved):
        path = root / relative
        try:
            path.resolve().relative_to(root.resolve())
            old = path.read_bytes().decode("utf-8")
            new = migrate_text(relative, old, reserved=relative in reserved)
            if new != old:
                plan.append((path, new))
        except (ValueError, OSError) as exc:
            errors.append(f"{relative}: {exc}")
    if errors:
        print("Migration aborted; no files changed.", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    for path, text in plan:
        path.write_bytes(text.encode("utf-8"))
        print(f"migrated  {path.relative_to(root)}")
    print(f"Migrated {len(plan)} file(s). Run okf-index.py, then okf-check.py --strict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
