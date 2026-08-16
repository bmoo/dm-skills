"""Maintainer guard: the declared dependency clusters match the tree.

The CLI installs one skill at a time, but some skills reach across a skill
boundary — `build-session`'s fight and keyed-site procedures open
`../spotlight/doctrine.md` mid-step. A selective
install of the dependent alone leaves a dangling load or a missing delegate, so
the library **declares** the edges: the master table lives under
*Dependency clusters* in ``docs/campaign-contract.md`` (maintainer-side, never
shipped). While any declared edge is **hard**, the consumer-facing statement
with the install command per cluster lives in ``README.md``; with every edge
degrading (the state since the generator merge) the README carries no cluster
section and none is demanded.

A hand-maintained dependency list is exactly the prose that goes stale — the
failure this repo keeps designing against. Three assertions, all over the real
tree:

``undeclared_edges``
    every ``../<other-skill>/`` path under ``skills/`` has a row in the table,
    typed **load** or **citation**. A path on a row typed *delegate* fails here
    too: a delegate edge invokes a skill and touches none of its files, so a
    relative path on one means the row is mis-typed or the skill text changed.

``stale_declarations``
    every declared **load** row still has at least one such path in the tree.
    Without this half, a load that was removed (or converted to a delegate, as
    interface refactors have done before) would sit in the table
    forever, telling installers to install a skill they no longer need.

``install_command_gaps``
    for every skill with a **hard** dependency, the README's cluster block
    carries an install command whose ``--skill`` set covers that skill plus the
    transitive closure of its hard dependencies. This is what keeps the
    consumer-facing half honest when an edge is added: declaring a new hard
    dependency and leaving the README's command short fails here.

**Deliberately dumb**, in the spirit of ``retired_phrases.py``. It pins the
*presence* of an edge and the README's agreement with it. It cannot tell a load
from a citation, and it cannot tell hard from degrades — those columns are prose,
and they are only as true as the last person to read the surrounding step. What
it does catch is the failure that actually occurs: a new `../other-skill/` load
added to a skill and never declared anywhere.

Lives at the ``lib/`` top level beside ``citation_anchors.py``, outside
``lib/mechanical-checker/`` — that directory materialises into every consumer
through a symlink, and this check is about *this repo's* install-time docs. It
runs under ``pytest lib/`` and never ships.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tree_scan import iter_tree

REPO_ROOT = Path(__file__).resolve().parent.parent

CONTRACT = "docs/campaign-contract.md"
README = "README.md"

CONTRACT_HEADING = "## Dependency clusters"
README_HEADING = "### Dependency clusters"

KINDS = ("load", "delegate", "citation")
STRENGTHS = ("hard", "degrades", "none")

# `build-session` | `spotlight` | load — degrades | …
_CELL_SKILL_RE = re.compile(r"^`([a-z][a-z0-9-]*)`$")
_COUPLING_RE = re.compile(r"^\**([a-z]+)\**\s*—\s*\**([a-z]+)\**$")

# ../<name>/ inside a shipped skill file. The `<name>` is filtered to real skill
# directories afterwards, which drops `../../docs/` and `../../scripts/`.
_CROSS_SKILL_RE = re.compile(r"\.\./([a-z][a-z0-9-]*)/")

# --skill <name>, as written in a fenced install command.
_SKILL_FLAG_RE = re.compile(r"--skill\s+([a-z][a-z0-9-]*)")

SHIPPED_SUFFIXES = (".md", ".py")


@dataclass(frozen=True)
class Declaration:
    """One row of the master table."""

    skill: str
    needs: str
    kind: str
    strength: str
    line: int

    @property
    def edge(self) -> tuple[str, str]:
        return (self.skill, self.needs)

    def __str__(self) -> str:
        return f"{CONTRACT}:{self.line}: `{self.skill}` needs `{self.needs}` ({self.kind} — {self.strength})"


def skill_names(repo_root: Path = REPO_ROOT) -> set[str]:
    """Every installable skill — a directory under ``skills/`` with a SKILL.md."""
    return {
        child.name
        for child in (repo_root / "skills").iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }


def _section(text: str, heading: str) -> list[tuple[int, str]]:
    """The ``(line number, text)`` body of the section that starts with
    ``heading``, up to the next heading at that level or above.

    A subsection *below* that level is therefore part of the body, and any table
    in it is parsed as declarations — so a nested `###` under the cluster section
    would surface as a row that doesn't parse rather than as a placement
    mistake. Fenced blocks are skipped over: a ``# comment`` inside an install
    command is not a heading."""
    lines = text.splitlines()
    level = heading.split(" ")[0]
    stops = tuple(level[:depth] + " " for depth in range(1, len(level) + 1))
    for index, line in enumerate(lines):
        if line.startswith(heading):
            body: list[tuple[int, str]] = []
            fenced = False
            for number, following in enumerate(lines[index + 1 :], index + 2):
                if following.startswith("```"):
                    fenced = not fenced
                # A `# comment` inside a fenced install command is not a heading.
                if not fenced and following.startswith(stops):
                    break
                body.append((number, following))
            return body
    raise LookupError(f"no section starting {heading!r} — the declaration moved or was deleted")


def declarations(repo_root: Path = REPO_ROOT) -> list[Declaration]:
    """The master table, parsed. Raises on a row that doesn't parse rather than
    skipping it — a silently-dropped row is a silently-undeclared edge."""
    text = (repo_root / CONTRACT).read_text(encoding="utf-8")

    rows: list[Declaration] = []
    for number, line in _section(text, CONTRACT_HEADING):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        skill_cell, needs_cell, coupling_cell = cells[0], cells[1], cells[2]
        if skill_cell == "Skill" or set(skill_cell) <= {"-", " ", ":"}:
            continue
        skill = _CELL_SKILL_RE.match(skill_cell)
        needs = _CELL_SKILL_RE.match(needs_cell)
        coupling = _COUPLING_RE.match(coupling_cell)
        if not (skill and needs and coupling):
            raise ValueError(
                f"{CONTRACT}:{number}: row does not parse — expected "
                "| `skill` | `needs` | <kind> — <strength> | prose | , got "
                f"{stripped[:90]!r}"
            )
        kind, strength = coupling.group(1), coupling.group(2)
        if kind not in KINDS:
            raise ValueError(f"{CONTRACT}:{number}: unknown coupling {kind!r} — one of {KINDS}")
        if strength not in STRENGTHS:
            raise ValueError(f"{CONTRACT}:{number}: unknown strength {strength!r} — one of {STRENGTHS}")
        rows.append(Declaration(skill.group(1), needs.group(1), kind, strength, number))
    return rows


def tree_edges(repo_root: Path = REPO_ROOT) -> dict[tuple[str, str], list[str]]:
    """Every ``../<other-skill>/`` reference in the shipped tree, keyed by edge,
    valued by the ``path:line`` sites that wrote it."""
    skills = skill_names(repo_root)
    found: dict[tuple[str, str], list[str]] = {}
    for skill in sorted(skills):
        root = repo_root / "skills" / skill
        for path in iter_tree(root):
            if path.suffix not in SHIPPED_SUFFIXES:
                continue
            for number, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                for target in _CROSS_SKILL_RE.findall(line):
                    if target not in skills or target == skill:
                        continue
                    site = f"{path.relative_to(repo_root)}:{number}"
                    found.setdefault((skill, target), []).append(site)
    return found


def unknown_skills(repo_root: Path = REPO_ROOT) -> list[str]:
    """Declared rows naming a skill that isn't installable."""
    skills = skill_names(repo_root)
    return [
        f"{row}: names a skill that is not in skills/"
        for row in declarations(repo_root)
        if row.skill not in skills or row.needs not in skills
    ]


def undeclared_edges(repo_root: Path = REPO_ROOT) -> list[str]:
    """Cross-skill paths in the tree with no row, or a row typed *delegate*."""
    declared = {row.edge: row for row in declarations(repo_root)}
    problems: list[str] = []
    for edge, sites in sorted(tree_edges(repo_root).items()):
        row = declared.get(edge)
        where = ", ".join(sites[:3]) + (" …" if len(sites) > 3 else "")
        if row is None:
            problems.append(
                f"{where}: `{edge[0]}` loads from `{edge[1]}` with no row in "
                f"{CONTRACT}'s dependency-cluster table — declare it, and update "
                f"the {README} install commands if it is hard"
            )
        elif row.kind == "delegate":
            problems.append(
                f"{where}: `{edge[0]}` → `{edge[1]}` is declared a delegate edge, "
                "but the skill text writes a relative path into that skill — a "
                "delegate touches no files, so re-type the row or fix the text"
            )
    return problems


def stale_declarations(repo_root: Path = REPO_ROOT) -> list[str]:
    """Declared **load** rows whose path is no longer anywhere in the tree."""
    present = set(tree_edges(repo_root))
    return [
        f"{row}: declared a load, but no `../{row.needs}/` path survives in "
        f"skills/{row.skill}/ — retire the row or re-type it"
        for row in declarations(repo_root)
        if row.kind == "load" and row.edge not in present
    ]


def hard_closure(repo_root: Path = REPO_ROOT) -> dict[str, set[str]]:
    """Per skill, the transitive set of skills a working install must also carry."""
    hard: dict[str, set[str]] = {}
    for row in declarations(repo_root):
        if row.strength == "hard":
            hard.setdefault(row.skill, set()).add(row.needs)
    closure: dict[str, set[str]] = {}
    for skill in hard:
        seen: set[str] = set()
        frontier = list(hard[skill])
        while frontier:
            other = frontier.pop()
            if other in seen:
                continue
            seen.add(other)
            frontier.extend(hard.get(other, ()))
        closure[skill] = seen
    return closure


def install_commands(repo_root: Path = REPO_ROOT) -> list[set[str]]:
    """The ``--skill`` sets of the commands in the README's cluster block."""
    text = (repo_root / README).read_text(encoding="utf-8")
    fenced = False
    commands: list[set[str]] = []
    for _, line in _section(text, README_HEADING):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced and "--skill" in line:
            commands.append(set(_SKILL_FLAG_RE.findall(line)))
    return commands


def install_command_gaps(repo_root: Path = REPO_ROOT) -> list[str]:
    """Skills with a hard dependency that no README command installs whole.

    With no hard rows in the table there is nothing for the README to
    advertise, so the check passes without demanding the README carry a
    cluster section at all — the generator merge removed the last hard edge,
    and the section went with it. The day a hard edge returns, this reads the
    README again and fails until the section does too."""
    closure = hard_closure(repo_root)
    if not closure:
        return []
    commands = install_commands(repo_root)
    problems: list[str] = []
    for skill, needed in sorted(closure.items()):
        wanted = {skill} | needed
        if not any(wanted <= command for command in commands):
            problems.append(
                f"{README}: no install command under \"{README_HEADING[4:]}\" "
                f"covers `{skill}` and its hard dependencies "
                f"({', '.join('`' + name + '`' for name in sorted(needed))}) — "
                "add or extend one, or the README advertises a broken install"
            )
    return problems


def main() -> int:
    problems = (
        unknown_skills()
        + undeclared_edges()
        + stale_declarations()
        + install_command_gaps()
    )
    for problem in problems:
        print(problem)
    print(f"{'FAIL' if problems else 'ok'}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
