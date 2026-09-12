"""Shared concept discovery and frontmatter parsing for the OKF tooling.

`BUNDLE_DIRS`, `ROOT_CONCEPTS`, and `EXCLUDED` configure the concept inventory
under `BUNDLE_ROOT`; reserved indexes and logs are traversed separately as
bundle members. Runs with no dependencies, using the OKF frontmatter YAML
subset below.
"""

import html
import json
import os
from pathlib import Path
import re
from typing import Any, NamedTuple
from urllib.parse import quote, unquote

from okf_config import BUNDLE_DIRS, BUNDLE_ROOT, EXCLUDED, ROOT_CONCEPTS

# Reserved filenames — bundle members, never concepts (see wiki-schema.md — Layout).
RESERVED = {"index.md", "log.md"}


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bundle_root():
    """The configured bundle root, resolved from the repository root."""
    return os.path.abspath(os.path.join(repo_root(), BUNDLE_ROOT))


def _configured_paths():
    """Files under configured directories, with exclusions and overlaps handled once."""
    root = bundle_root()
    paths = set()
    for directory in BUNDLE_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, directory)):
            dirnames[:] = [name for name in dirnames if name not in EXCLUDED]
            paths.update(os.path.relpath(os.path.join(dirpath, name), root)
                         for name in filenames)
    return paths


def page_paths():
    """Every candidate concept path in the configured bundle, sorted; reserved files excluded."""
    root = bundle_root()
    paths = _configured_paths()
    paths.update(path for path in ROOT_CONCEPTS if os.path.exists(os.path.join(root, path)))
    return sorted(path for path in paths
                  if path.endswith(".md") and Path(path).name not in RESERVED)


def reserved_paths():
    """Every reserved index.md / log.md bundle member, as a bundle-relative path."""
    root = bundle_root()
    paths = _configured_paths()
    paths.update(path for path in RESERVED if os.path.exists(os.path.join(root, path)))
    return sorted(path for path in paths if Path(path).name in RESERVED)


def split_frontmatter(text):
    """Return (frontmatter_text, body) or (None, text) when absent."""
    match = re.match(r"\A---\r?\n(?P<fields>.*?)(?m:^---(?:\r?\n|\Z))", text, re.S)
    if match is None:
        return None, text
    return match["fields"].rstrip("\r\n"), text[match.end():]


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


# --- Markdown destinations ---------------------------------------------------
# Keep offsets into the original text so callers can rewrite only destinations.
# These are Markdown links/images and reference definitions, not wikilinks or HTML.

class MarkdownLink(NamedTuple):
    destination: str
    start: int
    end: int


def markdown_prose(text):
    """Mask code and HTML comments with spaces, preserving source offsets."""
    def blank(match):
        value = match.group() if hasattr(match, "group") else match
        return re.sub(r"[^\r\n]", " ", value)

    text = re.sub(r"<!--.*?(?:-->|\Z)", blank, text, flags=re.S)
    lines, fence = [], None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            lines.append(blank(line))
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
            lines.append(blank(line))
        elif line.startswith(("    ", "\t")):
            lines.append(blank(line))
        else:
            lines.append(line)
    text = "".join(lines)
    return re.sub(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", blank, text, flags=re.S)


def _link_destination(text, start):
    """Parse a Markdown destination, allowing angle brackets and balanced ()."""
    if start >= len(text):
        return None
    if text[start] == "<":
        match = re.match(r"<((?:\\.|[^<>\n])*)>", text[start:])
        return (start + 1, start + 1 + len(match[1])) if match else None
    depth, end = 0, start
    while end < len(text):
        char = text[end]
        if char == "\\" and end + 1 < len(text):
            end += 2
            continue
        if char.isspace():
            break
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        end += 1
    return (start, end) if depth == 0 else None


def markdown_links(text):
    """Yield MarkdownLink(destination, start, end) outside code/examples.

    Offsets cover just the destination (inside <> when present), allowing
    reverse-order replacements while preserving titles and surrounding prose.
    Reference definitions are yielded once, including image definitions.
    """
    visible = markdown_prose(text)
    spans = set()
    # Inline links/images, including escaped or nested brackets in the label.
    for match in re.finditer(r"(?<!\\)\[(?:\\.|[^\]\\\n]|\[[^\]\n]*\])*\]\(\s*", visible):
        span = _link_destination(visible, match.end())
        if span is None:
            continue
        end = span[1] + (1 if visible[match.end():].startswith("<") else 0)
        # A link may include a quoted title between its destination and closing ).
        if re.match(r'''\s*(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\([^()]*\))?\s*\)''', visible[end:]):
            spans.add(span)
    for match in re.finditer(r"^ {0,3}\[(?!\^)[^\]\n]+\]:[ \t]*", visible, re.M):
        span = _link_destination(visible, match.end())
        if span:
            spans.add(span)
    for start, end in sorted(spans):
        yield MarkdownLink(text[start:end], start, end)


def is_relative_link(destination):
    """Local Markdown destinations (including #anchors) that lack leading /."""
    return not destination.startswith("/") and re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination) is None


# --- Targeted rewrites --------------------------------------------------------

def resolve_local_link(source, destination):
    """Existing local target as a bundle-relative Path, or None.

    External URLs, broken targets, and paths escaping the bundle are untouched.
    Media and directories are valid targets even though discovery excludes them.
    """
    destination = html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", destination))
    if destination.startswith("//") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination):
        return None
    path = unquote(re.split(r"[?#]", destination, maxsplit=1)[0])
    root = Path(bundle_root()).resolve()
    target = root / path.lstrip("/") if path.startswith("/") else root / Path(source).parent / path
    if not path:
        target = root / source
    try:
        relative = target.resolve().relative_to(root)
        return relative if target.exists() else None
    except (ValueError, OSError):
        return None


def root_link(source, destination):
    """Rewrite a resolvable relative destination, retaining its query/anchor."""
    if not is_relative_link(destination):
        return destination
    target = resolve_local_link(source, destination)
    if target is None:
        return destination
    suffix = re.search(r"[?#].*", destination)
    path_part = re.split(r"[?#]", destination, maxsplit=1)[0]
    trailing = "/" if path_part.endswith("/") and target.as_posix() != "." else ""
    target_path = "" if target == Path(".") else quote(target.as_posix(), safe="/")
    return "/" + target_path + trailing + (suffix[0] if suffix else "")


def rewrite_local_links(source, text):
    """Pure destination-only rewrite; source is relative to the bundle root."""
    for link in reversed(list(markdown_links(text))):
        text = text[:link.start] + root_link(source, link.destination) + text[link.end:]
    return text


def first_heading(text):
    """First actual H1 outside code/comments, without optional closing hashes."""
    match = re.search(r"^ {0,3}#[ \t]+[^\r\n]*", markdown_prose(text), re.M)
    if match is None:
        return None
    raw = re.sub(r"^ {0,3}#[ \t]+", "", text[match.start():match.end()])
    return re.sub(r"[ \t]+#+[ \t]*$", "", raw).strip() or None


def inferred_type(path):
    """Configured directory/root type, with the scaffold's file conventions."""
    from okf_config import DIRECTORY_TYPES, ROOT_TYPE
    path = Path(path)
    if path.name == "wiki-schema.md":
        return "schema"
    if path.name.lower() == "readme.md":
        return "readme"
    if path.stem.endswith("-seed-ideas"):
        return "seed-ideas"
    return ROOT_TYPE if path.parent == Path(".") else DIRECTORY_TYPES.get(path.parent.as_posix())


def edit_frontmatter(text, updates, remove=()):
    """Update top-level fields without reserializing unrelated metadata.

    Values supplied in updates are serialized as JSON-compatible YAML. Unknown
    fields, their scalar spellings, comments, and body bytes remain intact.
    Invalid or unterminated frontmatter raises ValueError before any mutation.
    """
    match = re.match(r"\A---\r?\n(?P<fields>.*?)(?m:^---(?:\r?\n|\Z))", text, re.S)
    newline = "\r\n" if "\r\n" in text else "\n"
    def field(key, value):
        return key + ": " + json.dumps(value, ensure_ascii=False) + newline
    if match is None:
        if text.startswith(("---\n", "---\r\n")):
            raise ValueError("unterminated frontmatter")
        if not updates:
            return text
        return "---" + newline + "".join(field(k, v) for k, v in updates.items()) + "---" + newline + text
    raw = match["fields"]
    parsed = parse_frontmatter(raw)
    if parsed is None:
        raise ValueError("unparseable frontmatter")
    keys = list(re.finditer(r"^([A-Za-z_][\w.-]*):[^\r\n]*(?:\r?\n|$)", raw, re.M))
    replacements = []
    for index, key in enumerate(keys):
        name = key[1]
        if name not in updates and name not in remove:
            continue
        end = keys[index + 1].start() if index + 1 < len(keys) else len(raw)
        lines = raw[key.start():end].splitlines(keepends=True)
        # Preserve blank/comment lines, including comments around nested values.
        comments = "".join(line for line in lines[1:] if not line.strip() or line.lstrip().startswith("#"))
        replacement = field(name, updates[name]) if name in updates else ""
        replacements.append((key.start(), end, replacement + comments))
    for start, end, replacement in reversed(replacements):
        raw = raw[:start] + replacement + raw[end:]
    raw += "".join(field(k, v) for k, v in updates.items() if k not in parsed)
    if parse_frontmatter(raw) is None:
        raise ValueError("rewrite produced unparseable frontmatter")
    return text[:match.start("fields")] + raw + text[match.end("fields"):]
