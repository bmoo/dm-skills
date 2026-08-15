"""Shared page discovery and frontmatter parsing for the wiki tooling.

The wiki is the set of directories `wiki_config.WIKI_DIRS` names, plus the
root files it lists. Everything else in the repo — tooling, media, working
docs — sits outside it and is never checked or indexed. Runs with no
dependencies; PyYAML is used when present.
"""

import os
import re

from wiki_config import EXCLUDED, WIKI_DIRS, WIKI_ROOT_FILES

# Reserved filenames — never wiki pages (see wiki-schema.md — Layout).
RESERVED = {"index.md", "log.md"}


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def page_paths():
    """Every wiki page, repo-relative, sorted."""
    root = repo_root()
    out = []
    for d in WIKI_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, d)):
            dirnames[:] = [n for n in dirnames if n not in EXCLUDED]
            for f in filenames:
                if f.endswith(".md") and f not in RESERVED:
                    out.append(os.path.relpath(os.path.join(dirpath, f), root))
    for f in WIKI_ROOT_FILES:
        if os.path.exists(os.path.join(root, f)):
            out.append(f)
    return sorted(out)


def reserved_paths():
    """Every index.md / log.md inside the wiki (plus the repo root's)."""
    root = repo_root()
    out = []
    for f in RESERVED:
        if os.path.exists(os.path.join(root, f)):
            out.append(f)
    for d in WIKI_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, d)):
            dirnames[:] = [n for n in dirnames if n not in EXCLUDED]
            for f in filenames:
                if f in RESERVED:
                    out.append(os.path.relpath(os.path.join(dirpath, f), root))
    return sorted(out)


def split_frontmatter(text):
    """Return (frontmatter_text, body) or (None, text) when absent."""
    if not text.startswith("---\n"):
        return None, text
    parts = text[4:].split("\n---\n", 1)
    if len(parts) != 2:
        return None, text
    return parts[0], parts[1]


def parse_frontmatter(text):
    """Parse frontmatter with PyYAML when available, else a flat-scalar reader.

    The fallback handles the shapes the schema asks for (scalars and inline
    `[a, b]` lists); it exists so the checker runs with no dependencies.
    """
    try:
        import yaml
    except ImportError:
        yaml = None
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            # Unparseable frontmatter is a check failure, not a crash — the
            # caller reports it as one.
            return None
        return data if isinstance(data, dict) else None
    data = {}
    for line in text.split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            data[key] = [v.strip() for v in raw[1:-1].split(",") if v.strip()]
        else:
            data[key] = raw.strip("'\"")
    return data


def load(path):
    """(frontmatter dict or None, body) for a repo-relative path."""
    with open(os.path.join(repo_root(), path), encoding="utf-8") as fh:
        text = fh.read()
    fm, body = split_frontmatter(text)
    return (parse_frontmatter(fm) if fm is not None else None), body
