#!/usr/bin/env python3
"""Read-only OKF conformance and campaign convention checks.

Every concept has a parseable YAML frontmatter block.
Only malformed frontmatter, missing type, and reserved-file shape are errors.
All other findings are warnings; --strict makes warnings fail the exit status.
Link targets and the meaning of body content belong to the groomer.

    python3 scripts/okf-check.py [--warnings] [--strict]
"""

import argparse
from datetime import date, datetime
from pathlib import Path, PurePosixPath
import re
import sys

# The checker does not create __pycache__ in a consumer's bundle.
sys.dont_write_bytecode = True
import okf_bundle as wiki
from okf_config import DIRECTORY_TYPES, SUGGESTED_TAGS, TAG_STOPWORDS


def finding(check_id, path, message):
    return f"[{check_id}] {path}: {message}"


def timestamp_has_offset(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
    except ValueError:
        return False


def actor_has_shape(value):
    return isinstance(value, str) and re.fullmatch(
        r"(?:human:[^\s:/]+|process:[^\s:/]+|[^\s:/]+/[^\s/]+)", value
    ) is not None


def setting_tags(paths):
    """Tags a concept basename exempts: the whole stem, each hyphen-delimited
    word, and each hyphen-delimited prefix, skipping bare stopwords."""
    tags = set()
    for path in paths:
        words = PurePosixPath(path).stem.split("-")
        candidates = set(words) | {"-".join(words[:n]) for n in range(1, len(words) + 1)}
        tags.update(candidate for candidate in candidates if candidate not in TAG_STOPWORDS)
    return tags


def check_pages():
    errors, warnings = [], []
    paths = sorted(set(wiki.page_paths()))
    slugs = setting_tags(paths)
    for path in paths:
        try:
            fm, body = wiki.load(path)
        except (UnicodeError, OSError) as exc:
            errors.append(finding("okf/frontmatter-parses", path, f"cannot read UTF-8 concept: {exc}"))
            continue
        if fm is None:
            errors.append(finding("okf/frontmatter-parses", path, "no parseable YAML frontmatter block"))
            continue
        kind = fm.get("type", "")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(finding("okf/type-present", path, "frontmatter has no non-empty string `type`"))
        missing = [key for key in ("title", "description", "tags", "status", "generated") if key not in fm]
        if missing:
            warnings.append(finding("okf/expected-keys", path, "recommended keys absent: " + ", ".join(missing)))
        generated = fm.get("generated")
        if "generated" in fm and (not isinstance(generated, dict) or not generated.get("by")):
            warnings.append(finding("okf/generated-by", path, "`generated` should carry `by`"))
        actors, timestamps = [], []
        if isinstance(generated, dict):
            if generated.get("by"):
                actors.append(("generated.by", generated["by"]))
            if "at" in generated:
                timestamps.append(("generated.at", generated["at"]))
        verified = fm.get("verified", [])
        # OKF explicitly treats a bare verification mapping as a one-item list.
        if isinstance(verified, dict):
            verified = [verified]
        if isinstance(verified, list):
            for i, event in enumerate(verified):
                if isinstance(event, dict):
                    if "by" in event:
                        actors.append((f"verified[{i}].by", event["by"]))
                    if "at" in event:
                        timestamps.append((f"verified[{i}].at", event["at"]))
        if "stale_after" in fm:
            timestamps.append(("stale_after", fm["stale_after"]))
        for key, value in actors:
            if not actor_has_shape(value):
                warnings.append(finding("okf/actor-shape", path, f"`{key}` should be human:<id>, process:<id>, or <producer>/<version>"))
        for key, value in timestamps:
            if not timestamp_has_offset(value):
                warnings.append(finding("okf/timestamp-offset", path, f"`{key}` should be an ISO 8601 datetime with UTC offset"))
        if "status" in fm and fm["status"] not in ("draft", "stable", "deprecated"):
            warnings.append(finding("okf/status-enum", path, "`status` should be draft, stable, or deprecated"))
        if "timestamp" in fm:
            warnings.append(finding("okf/legacy-timestamp", path, "legacy `timestamp`; use `generated.at`"))
        expected = DIRECTORY_TYPES.get(str(PurePosixPath(path).parent))
        if kind and kind not in ("schema", "readme", "seed-ideas") and expected and kind != expected:
            warnings.append(finding("wiki/type-matches-directory", path, f"directory convention expects type `{expected}`"))
        if "tags" in fm:
            tags = fm["tags"]
            if not isinstance(tags, list) or any(
                not isinstance(tag, str) or tag not in SUGGESTED_TAGS and tag not in slugs for tag in tags
            ):
                warnings.append(finding("wiki/tags-suggested", path, "tags should be a list from SUGGESTED_TAGS or words of existing concept basenames"))
        description = fm.get("description", "")
        if isinstance(description, str) and any(wiki.markdown_links(description)):
            warnings.append(finding("wiki/description-plain", path, "description should use plain text without Markdown links"))
        for link in wiki.markdown_links(body):
            if wiki.is_relative_link(link.destination):
                warnings.append(finding("wiki/link-form", path, f"prefer bundle-relative `/` form: {link.destination}"))
    return errors, warnings


def check_index(path, body, raw):
    """Only root index metadata may declare a version; unknown versions remain readable."""
    problems = []
    if raw is not None:
        fm = wiki.parse_frontmatter(raw)
        if not (path == "index.md" and isinstance(fm, dict)
                and set(fm) == {"okf_version"} and isinstance(fm["okf_version"], str)):
            problems.append("index frontmatter permits only `okf_version` at the bundle root")
    elif body.startswith("---\n"):
        problems.append("unclosed index frontmatter")
    visible = wiki.markdown_prose(body)
    if not re.search(r"^#{1,6}\s+\S", visible, re.M):
        problems.append("no section headings")
    if not any(re.match(r"^\s*[*-]\s+\[", line) and any(wiki.markdown_links(line))
               for line in visible.splitlines()):
        problems.append("no linked entries")
    return [finding("okf/reserved-file-shape", path, problem) for problem in problems]


def check_log(path, body):
    """Logs may be empty; actual H2 headings are valid ISO dates, newest first."""
    problems, dates = [], []
    for heading in re.findall(r"^##\s+(.+?)\s*#*\s*$", wiki.markdown_prose(body), re.M):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", heading):
                raise ValueError
            dates.append(date.fromisoformat(heading))
        except ValueError:
            problems.append(f"heading '{heading}' is not ISO 8601 YYYY-MM-DD")
    if dates != sorted(dates, reverse=True):
        problems.append("date headings should be newest first")
    return [finding("okf/reserved-file-shape", path, problem) for problem in problems]


def check_reserved():
    errors = []
    for path in sorted(set(wiki.reserved_paths())):
        try:
            with open(Path(wiki.bundle_root()) / path, encoding="utf-8") as stream:
                raw, body = wiki.split_frontmatter(stream.read())
        except (UnicodeError, OSError) as exc:
            errors.append(finding("okf/reserved-file-shape", path, f"cannot read UTF-8 reserved file: {exc}"))
            continue
        if PurePosixPath(path).name == "index.md":
            errors += check_index(path, body, raw)
        else:
            errors += check_log(path, body)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warnings", action="store_true", help="print advisory findings")
    parser.add_argument("--strict", action="store_true", help="print warnings and fail if any occur")
    args = parser.parse_args()
    errors, warnings = check_pages()
    errors += check_reserved()
    for error in errors:
        print(f"FAIL  {error}")
    if args.warnings or args.strict:
        for warning in warnings:
            print(f"warn  {warning}")
    print(f"\n{len(set(wiki.page_paths()))} concepts, {len(set(wiki.reserved_paths()))} reserved files checked.")
    failed = bool(errors or args.strict and warnings)
    print(f"{'CHECK FAILED' if failed else 'Wiki checks pass'} — {len(errors)} error(s), {len(warnings)} warning(s).")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
