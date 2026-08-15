"""Structural lint over the `build-session/spotlight-coverage` corpus — NOT the verdict harness.

The verdict-match harness (run the checker over each instance, assert its verdict
equals the map's) is out of scope here and reserved for a future harness. This is the cheaper,
model-free guard the corpus needs anyway: an instance states a **pre-pass output**
in prose, and prose can drift out of agreement with the pre-pass that would
actually produce it. A wrong instance is worse than a missing one — it teaches the
checker a boundary the code cannot put it at.

So this asserts the two things a reader cannot reliably eyeball:

  1. every instance's stated `Uncovered` set is EXACTLY its PCs with beat share 0,
     which is `spotlight_coverage`'s own invariant (`covered ⟺ share > 0`);
  2. the instances on disk and the rows of the verdict map are the same set, in
     both directions.
"""

import ast
import re
from pathlib import Path

import pytest

CORPUS = Path(__file__).parent
INSTANCES = CORPUS / "instances"

_UNCOVERED_RE = re.compile(r"\*\*Uncovered:\*\*\s*`(\[[^`]*\])`")
_SHARE_RE = re.compile(r"\*\*Beat share:\*\*\s*`\{([^`]*)\}`")


def _instances():
    return sorted(INSTANCES.glob("*.md"))


def _parse(path: Path):
    text = path.read_text()
    um, sm = _UNCOVERED_RE.search(text), _SHARE_RE.search(text)
    assert um, f"{path.name}: no `**Uncovered:**` line — every instance states one"
    assert sm, f"{path.name}: no `**Beat share:**` line — every instance states one"
    uncovered = ast.literal_eval(um.group(1))
    share = {}
    for part in sm.group(1).split(","):
        pc, n = part.split(":")
        share[pc.strip()] = int(n)
    return uncovered, share


@pytest.mark.parametrize("path", _instances(), ids=lambda p: p.name)
def test_uncovered_set_matches_the_beat_share(path):
    # spotlight_coverage's invariant, restated over the corpus: a PC is uncovered iff
    # no annotation names them, i.e. iff their beat share is 0. An instance claiming a
    # covered PC with share 0 (or an uncovered PC with share > 0) describes output the
    # pre-pass cannot produce, and would pin the row's boundary in the wrong place.
    uncovered, share = _parse(path)
    assert sorted(uncovered) == sorted(pc for pc, n in share.items() if n == 0)


@pytest.mark.parametrize("path", _instances(), ids=lambda p: p.name)
def test_every_instance_is_listed_in_the_verdict_map(path):
    # The map is the manifest; an unlisted instance is unlabeled and ungradeable.
    assert path.name in (CORPUS / "verdict-map.md").read_text()


def test_the_verdict_map_lists_no_missing_instance():
    # The other direction: a map row pointing at a file that does not exist.
    listed = set(re.findall(r"instances/([a-z0-9-]+\.md)", (CORPUS / "verdict-map.md").read_text()))
    assert listed == {p.name for p in _instances()}
