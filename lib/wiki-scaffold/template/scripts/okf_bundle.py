"""Shared page discovery and frontmatter parsing for the wiki tooling.

The wiki is the set of directories `okf_config.BUNDLE_DIRS` names, plus the
root files it lists. Everything else in the repo — tooling, media, working
docs — sits outside it and is never checked or indexed. Runs with no
dependencies, using the OKF frontmatter YAML subset below.
"""

import json
import os
import re
from typing import Any

from okf_config import BUNDLE_DIRS, BUNDLE_ROOT, EXCLUDED, ROOT_CONCEPTS

# Reserved filenames — never wiki pages (see wiki-schema.md — Layout).
RESERVED = {"index.md", "log.md"}


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bundle_root():
    """The configured bundle root, resolved from the repository root."""
    return os.path.abspath(os.path.join(repo_root(), BUNDLE_ROOT))


def page_paths():
    """Every wiki page, bundle-relative, sorted."""
    root = bundle_root()
    out = []
    for d in BUNDLE_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, d)):
            dirnames[:] = [n for n in dirnames if n not in EXCLUDED]
            for f in filenames:
                if f.endswith(".md") and f not in RESERVED:
                    out.append(os.path.relpath(os.path.join(dirpath, f), root))
    for f in ROOT_CONCEPTS:
        if os.path.exists(os.path.join(root, f)):
            out.append(f)
    return sorted(out)


def reserved_paths():
    """Every index.md / log.md inside the wiki (plus the bundle root's)."""
    root = bundle_root()
    out = []
    for f in RESERVED:
        if os.path.exists(os.path.join(root, f)):
            out.append(f)
    for d in BUNDLE_DIRS:
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


# --- YAML subset -------------------------------------------------------------
# The stdlib has no YAML parser and the scaffold adds no dependencies, so this
# reads the subset OKF frontmatter actually uses: scalars, flow lists `[a, b]`,
# flow mappings `{ k: v }`, block mappings, and block lists whose items are
# scalars, flow mappings, or block mappings (`- id: x` followed by indented
# keys). Values stay strings except for nested containers.


class YamlError(ValueError):
    pass


def _unquote(s: str) -> str:
    s = s.strip()
    if s.startswith('"'):
        try:
            return json.loads(s)
        except (ValueError, TypeError) as exc:
            raise YamlError(f"invalid quoted scalar {s!r}") from exc
    if s.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", s):
            raise YamlError(f"invalid quoted scalar {s!r}")
        return s[1:-1].replace("''", "'")
    return s


def _split_flow(inner: str) -> list[str]:
    """Split on top-level commas, rejecting unfinished quotes and collections."""
    parts: list[str] = []
    stack: list[str] = []
    buf, quote = "", None
    i = 0
    while i < len(inner):
        ch = inner[i]
        if quote:
            buf += ch
            if ch == "\\" and quote == '"':
                i += 1
                if i >= len(inner):
                    raise YamlError("unfinished quoted escape")
                buf += inner[i]
            elif ch == quote:
                if quote == "'" and i + 1 < len(inner) and inner[i + 1] == "'":
                    i += 1
                    buf += inner[i]
                else:
                    quote = None
            i += 1
            continue
        # A quote inside a plain word (Mary's) does not open a quoted scalar.
        if ch in "\"'" and (not buf.strip() or buf.rstrip()[-1] in "[{,:"):
            quote = ch
        elif ch in "[{":
            stack.append(ch)
        elif ch in "]}":
            if not stack or stack.pop() != {"]": "[", "}": "{"}[ch]:
                raise YamlError("unbalanced flow collection")
        if ch == "," and not stack:
            if not buf.strip():
                raise YamlError("empty flow collection entry")
            parts.append(buf)
            buf = ""
        else:
            buf += ch
        i += 1
    if quote or stack:
        raise YamlError("unfinished flow collection or quoted scalar")
    if buf.strip():
        parts.append(buf)
    return parts


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith(("'", '"')):
        return _unquote(raw)
    if raw.startswith(("[", "{")) and not raw.endswith({"[": "]", "{": "}"}[raw[0]]):
        raise YamlError("unfinished flow collection")
    if raw.startswith("[") and raw.endswith("]"):
        return [_parse_scalar(p) for p in _split_flow(raw[1:-1])]
    if raw.startswith("{") and raw.endswith("}"):
        out: dict[str, Any] = {}
        for part in _split_flow(raw[1:-1]):
            if ":" not in part:
                raise YamlError(f"bad flow mapping entry {part.strip()!r}")
            k, v = part.split(":", 1)
            out[_unquote(k)] = _parse_scalar(v)
        return out
    return _unquote(raw)


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_block(lines: list[tuple[int, str]], i: int, indent: int) -> tuple[Any, int]:
    """Parse the block starting at lines[i] whose lines sit at `indent`."""
    if lines[i][1].lstrip().startswith("- "):
        return _parse_list(lines, i, indent)
    return _parse_map(lines, i, indent)


def _parse_map(lines: list[tuple[int, str]], i: int, indent: int) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while i < len(lines):
        lineno, line = lines[i]
        if _indent(line) < indent:
            break
        if _indent(line) > indent or line.lstrip().startswith("- "):
            raise YamlError(f"line {lineno}: unexpected indentation: {line.strip()!r}")
        m = re.match(r"^\s*([A-Za-z_][\w.-]*):\s*(.*)$", line)
        if not m:
            raise YamlError(f"line {lineno}: unparseable frontmatter line: {line.strip()!r}")
        key, value = m.group(1), m.group(2).strip()
        i += 1
        if value:
            out[key] = _parse_scalar(value)
        elif i < len(lines) and _indent(lines[i][1]) > indent:
            out[key], i = _parse_block(lines, i, _indent(lines[i][1]))
        elif i < len(lines) and lines[i][1].lstrip().startswith("- ") and _indent(lines[i][1]) == indent:
            out[key], i = _parse_list(lines, i, indent)  # list at the key's own indent
        else:
            out[key] = ""
    return out, i


def _parse_list(lines: list[tuple[int, str]], i: int, indent: int) -> tuple[list[Any], int]:
    out: list[Any] = []
    while i < len(lines):
        lineno, line = lines[i]
        if _indent(line) < indent or not line.lstrip().startswith("- "):
            break
        if _indent(line) != indent:
            raise YamlError(f"line {lineno}: unexpected indentation: {line.strip()!r}")
        rest = line.lstrip()[2:]
        item_indent = indent + 2
        if re.match(r"^[A-Za-z_][\w.-]*:(\s|$)", rest) and not rest.startswith(("{", "[")):
            # `- key: value` opens a block mapping whose further keys align with `key`.
            lines[i] = (lineno, " " * item_indent + rest)
            item, i = _parse_map(lines, i, item_indent)
            out.append(item)
        else:
            out.append(_parse_scalar(rest))
            i += 1
    return out, i


def parse_frontmatter(block: str) -> dict[str, Any] | None:
    lines = [
        (n, ln.rstrip())
        for n, ln in enumerate(block.splitlines(), start=2)
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    if not lines:
        return {}
    try:
        fields, end = _parse_map(lines, 0, 0)
        if end != len(lines):
            raise YamlError(f"line {lines[end][0]}: unparseable frontmatter line: {lines[end][1].strip()!r}")
    except YamlError:
        return None
    return fields



def load(path):
    """(frontmatter dict or None, body) for a bundle-relative path."""
    with open(os.path.join(bundle_root(), path), encoding="utf-8") as fh:
        text = fh.read()
    fm, body = split_frontmatter(text)
    return (parse_frontmatter(fm) if fm is not None else None), body
