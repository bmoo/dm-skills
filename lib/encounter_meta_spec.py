"""Maintainer guard: the encounter-meta block has **one** spec, and both
code paths that read the block are checked against it.

The block's field list used to be asserted in three independent places — prose
in the fight procedure (now `build-session/combat.md`), the wire-format parser
(`build-session/scripts/session_parser.py`), and the deterministic checker
(`lib/mechanical-checker/checker.py`, the
`build-session/encounter-meta-required-lines` row). Three copies, no
mechanism: a label added to one was a label missing from the other two, and
nothing said so.

 moved the spec to the format doc the block travels on —
`build-session/session-page-format.md`, *The encounter-meta block* — and
the fight procedure (`build-session/combat.md`) now cites it. This module is what makes that a **single
source** rather than a relocation:

``spec_required_labels`` / ``spec_optional_labels``
    read out of the shipped section itself, two ways that must agree — the
    fenced template's ``> **<label>:**`` lines, and the prose sentence naming
    which are required. A section that disagrees with itself fails here first.

``checker_required_labels``
    the shipped checker's ``_ENCOUNTER_META_REQUIRED`` literal, loaded by path.
    It stays a literal — ``lib/mechanical-checker/`` materialises into every
    consumer through a symlink and must not read this repo's docs at run time —
    and the test asserts it equals the spec's list. Pinned, not duplicated.

``parse_spec_example``
    the parser's own reading of the spec's example block. The parser keeps a
    callout body as an opaque string, so it carries no field list to compare
    (`lint/encounter-meta-fields-match-parser` recorded exactly that); what it
    *can* be held to is that the spec's own block parses as an `encounter-meta`
    callout with every spec label intact. That is the parser half, checked
    against the prose rather than against a copy of it.

``restatements``
    every *other* place in the tree that writes the template's placeholder form
    (``> **Party:** <…>``). The spec file is the only legal home; a fixture is a
    filled instance, not a restatement, so the placeholder form is what is
    searched for. This is the guard that keeps the fourth copy from growing
    back.

Like ``citation_anchors`` and ``doctrine_sync`` beside it, this lives at the
``lib/`` top level and never ships.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

from tree_scan import iter_tree

REPO_ROOT = Path(__file__).resolve().parent.parent

SPEC_FILE = "skills/build-session/session-page-format.md"
SPEC_HEADING = "## The encounter-meta block"
SPEC_ANCHOR = "#the-encounter-meta-block"

CHECKER = "lib/mechanical-checker/checker.py"
PARSER = "skills/build-session/scripts/session_parser.py"

# The file that cites the spec instead of restating it.
CITING_SKILL = "skills/build-session/combat.md"

# A template line: `> **Party:** <size and level …>`. The angle-bracket
# placeholder is what distinguishes a template from a filled example block.
_TEMPLATE_LINE = re.compile(r"^>\s*\*\*(?P<label>[A-Za-z][A-Za-z ]*):\*\*\s*<")

# "Party, Enemies, Budget, Terrain, Spotlight, and Objective are required;
#  Note is optional."
_REQUIREMENT_SENTENCE = re.compile(
    r"(?P<required>[A-Z][A-Za-z, ]*?)\s+are required;\s*(?P<optional>[A-Za-z, ]+?)\s+is optional"
)

# Files that legitimately carry filled encounter-meta blocks (fixtures, corpus
# instances) — they are instances, never the template.
_RESTATEMENT_SKIP = (SPEC_FILE,)


def spec_section(repo_root: Path = REPO_ROOT) -> str:
    """The shipped spec section, heading through the line before the next H2."""
    text = (repo_root / SPEC_FILE).read_text(encoding="utf-8")
    start = text.find(SPEC_HEADING + "\n")
    if start == -1:
        raise AssertionError(
            f"{SPEC_FILE} carries no {SPEC_HEADING!r} section — the encounter-meta "
            "spec has no home, and the parser and checker have nothing to be pinned to"
        )
    rest = text[start + len(SPEC_HEADING) :]
    end = rest.find("\n## ")
    return SPEC_HEADING + (rest if end == -1 else rest[:end])


def spec_template(repo_root: Path = REPO_ROOT) -> str:
    """The fenced example block inside the spec section, fences stripped."""
    section = spec_section(repo_root)
    match = re.search(r"```markdown\n(?P<body>.*?)\n```", section, re.DOTALL)
    if match is None:
        raise AssertionError(f"{SPEC_HEADING} carries no ```markdown template fence")
    return match.group("body")


def template_labels(repo_root: Path = REPO_ROOT) -> list[str]:
    """Labels in the template, in the order the block writes them."""
    return [
        match.group("label").strip()
        for line in spec_template(repo_root).splitlines()
        if (match := _TEMPLATE_LINE.match(line.strip()))
    ]


def _requirement_sentence(repo_root: Path = REPO_ROOT) -> re.Match[str]:
    prose = re.sub(r"\s+", " ", spec_section(repo_root))
    match = _REQUIREMENT_SENTENCE.search(prose)
    if match is None:
        raise AssertionError(
            f"{SPEC_HEADING} no longer states which lines are required — the "
            "template alone cannot say which fields are optional"
        )
    return match


def _split_labels(clause: str) -> list[str]:
    parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", clause.strip())
    return [part.strip() for part in parts if part.strip()]


def spec_required_labels(repo_root: Path = REPO_ROOT) -> list[str]:
    """The required labels, as the spec's prose names them."""
    return _split_labels(_requirement_sentence(repo_root).group("required"))


def spec_optional_labels(repo_root: Path = REPO_ROOT) -> list[str]:
    """The optional labels, as the spec's prose names them."""
    return _split_labels(_requirement_sentence(repo_root).group("optional"))


def _load(relative: str, name: str, repo_root: Path = REPO_ROOT) -> ModuleType:
    """Import a module by path — ``lib/mechanical-checker`` has a hyphen, and the
    parser lives under a skill; neither is importable by name."""
    spec = importlib.util.spec_from_file_location(name, repo_root / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registered before execution: ``dataclasses`` resolves a class's own module
    # out of ``sys.modules`` while processing it, and checker.py is dataclasses.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def checker_required_labels(repo_root: Path = REPO_ROOT) -> list[str]:
    """``_ENCOUNTER_META_REQUIRED`` as the shipped checker declares it."""
    return list(_load(CHECKER, "_encounter_meta_checker", repo_root)._ENCOUNTER_META_REQUIRED)


def parse_spec_example(repo_root: Path = REPO_ROOT) -> list[dict]:
    """Run the session parser over the spec's own example block; return the
    elements it yields."""
    parser = _load(PARSER, "_encounter_meta_parser", repo_root)
    page = "# A page\n\n## A keyed area\n\n" + spec_template(repo_root) + "\n"
    tree = parser.parse_session_text(page)
    elements: list[dict] = []

    def walk(sections: list[dict]) -> None:
        for section in sections:
            elements.extend(section["elements"])
            walk(section["children"])

    walk(tree["sections"])
    return elements


def restatements(repo_root: Path = REPO_ROOT) -> list[str]:
    """Every place outside the spec that writes the template's placeholder form."""
    hits: list[str] = []
    labels = set(template_labels(repo_root))
    for path in iter_tree(repo_root, "**/*.md"):
        relative = path.relative_to(repo_root).as_posix()
        if relative in _RESTATEMENT_SKIP:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = _TEMPLATE_LINE.match(line.strip())
            if match and match.group("label").strip() in labels:
                hits.append(f"{relative}:{number}: {line.strip()}")
    return hits


def cites_spec(repo_root: Path = REPO_ROOT) -> bool:
    """True if the citing skill links the spec section rather than restating it."""
    text = (repo_root / CITING_SKILL).read_text(encoding="utf-8")
    return f"session-page-format.md{SPEC_ANCHOR}" in text


def main() -> int:
    problems: list[str] = []
    required, optional = spec_required_labels(), spec_optional_labels()
    if required + optional != template_labels():
        problems.append(
            f"spec disagrees with itself: template {template_labels()} vs "
            f"required {required} + optional {optional}"
        )
    if checker_required_labels() != required:
        problems.append(f"checker {checker_required_labels()} != spec {required}")
    if not any(element.get("type") == "encounter-meta" for element in parse_spec_example()):
        problems.append("the parser does not read the spec's own example as an encounter-meta callout")
    if not cites_spec():
        problems.append(f"{CITING_SKILL} no longer cites {SPEC_FILE}{SPEC_ANCHOR}")
    problems.extend(f"restated template: {hit}" for hit in restatements())
    for problem in problems:
        print(problem)
    print(f"{'FAIL' if problems else 'ok'}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
