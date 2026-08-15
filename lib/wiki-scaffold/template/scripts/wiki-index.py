#!/usr/bin/env python3
"""Generate the wiki's index layer from page frontmatter.

Writes the repo-root `index.md` (the full catalog) and one `index.md` per
wiki directory. Every entry's title/description/status comes from the target
page's own frontmatter, so the catalog cannot drift from the pages it
indexes — regenerate after any batch of wiki changes.

    python3 scripts/wiki-index.py [--check]

--check exits non-zero if the generated output differs from what is on disk.
"""

import os
import sys

import wiki_bundle as wiki
from wiki_config import GROUPS, WIKI_INTRO, WIKI_TITLE

LABEL = dict(GROUPS)


def pages_in(directory):
    """Wiki pages directly inside `directory` (not its subdirectories)."""
    out = []
    for path in wiki.page_paths():
        if os.path.dirname(path) == directory:
            fm, _ = wiki.load(path)
            out.append((path, fm or {}))
    # Seed-idea inboxes sort last; everything else by title.
    return sorted(out, key=lambda p: (p[1].get("type") == "seed-ideas",
                                      str(p[1].get("title", p[0])).lower()))


def subdirs_of(directory):
    return [d for d, _ in GROUPS
            if os.path.dirname(d) == directory and d != directory]


def entry(link, fm):
    title = str(fm.get("title") or os.path.basename(link)).strip()
    desc = str(fm.get("description", "")).strip()
    status = str(fm.get("status", "")).strip()
    line = f"* [{title}]({link})"
    if status:
        line += f" — *{status}*"
    if desc:
        line += f" - {desc}"
    return line


def dir_index(directory):
    """Index for one directory: subdirectories first, then its pages."""
    lines = [f"# {LABEL[directory]}", ""]
    subs = subdirs_of(directory)
    if subs:
        for sub in subs:
            count = len(pages_in(sub))
            name = os.path.basename(sub)
            noun = "page" if count == 1 else "pages"
            lines.append(f"* [{LABEL[sub]}]({name}/) - "
                         f"{count} {noun} in `{sub}/`.")
        lines.append("")
    pages = pages_in(directory)
    if pages:
        if subs:
            lines += [f"# {LABEL[directory]} — pages", ""]
        for path, fm in pages:
            lines.append(entry(os.path.basename(path), fm))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def root_index():
    """The root catalog — every page, grouped, newest metadata."""
    lines = [f"# {WIKI_TITLE}", "", WIKI_INTRO, ""]
    for directory, label in GROUPS:
        pages = pages_in(directory)
        if not pages:
            continue
        depth = directory.count("/") + 1
        lines += ["#" * min(depth, 6) + f" {label}", ""]
        for path, fm in pages:
            lines.append(entry(path, fm))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    check = "--check" in sys.argv
    root = wiki.repo_root()
    targets = {"index.md": root_index()}
    for directory, _ in GROUPS:
        if pages_in(directory) or subdirs_of(directory):
            targets[os.path.join(directory, "index.md")] = dir_index(directory)

    stale = []
    for rel, content in sorted(targets.items()):
        full = os.path.join(root, rel)
        current = open(full, encoding="utf-8").read() if os.path.exists(full) else None
        if current == content:
            continue
        stale.append(rel)
        if not check:
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(content)

    if check:
        for rel in stale:
            print(f"stale  {rel}")
        print(f"{len(targets)} index files checked, {len(stale)} stale.")
        return 1 if stale else 0
    print(f"Wrote {len(stale)} of {len(targets)} index files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
