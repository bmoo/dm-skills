"""Maintainer guard: no session fixture in this repo's corpus encodes a keyed page
the session-page format forbids.

`fbfe586` added this sweep, and it initially lived inside the checker's own
directory — which *materialises into every consumer*. Two things
put it here instead.
It needs the sanctioned tree walker
(`lib/test_tree_scan.py` — "walk the tree through tree_scan.iter_tree"), and that
walker does not ship, so the shipped test module importing it broke collection in
every vendored copy. And what it asserts is about *this repo's fixture corpus*: a
consumer has no session fixtures to sweep, so the check has nothing to say there.
Same reasoning that already puts `citation_anchors` at the
`lib/` top level rather than inside a shipping directory.

Depending on the shipped checker from up here is the allowed direction — maintainer
code may import shipped code; shipped code importing maintainer code is the
violation `test_tree_scan.py` now guards against.
"""

from pathlib import Path
import sys

from tree_scan import iter_tree

REPO_ROOT = Path(__file__).resolve().parent.parent
MECHANICAL_CHECKER = (
    REPO_ROOT / "skills" / "build-session" / "scripts" / "mechanical_checker"
)
FIXTURES = MECHANICAL_CHECKER / "fixtures"

# The shipped checker is reached by path: it lives under a skill directory, which
# is not importable by name, and it is not a package.
sys.path.insert(0, str(MECHANICAL_CHECKER))

from checker import run_checks  # noqa: E402  (needs the path above)

# The two rows that say what a keyed page owes: a map, and an edge list the DM's
# page does not show.
KEYED_PAGE_ROWS = [
    "build-session/keyed-site-carries-map",
    "build-session/edges-not-dm-visible",
]


def test_no_session_fixture_encodes_a_keyed_page_the_format_forbids():
    # Those two rows run against ONE fixture in `test_checker.py`'s page-owned
    # subset, so a fixture that violates either is invisible to the gate — which is
    # how five keyed pages carrying no map survived being wired into the documented
    # run. Sweeping every session fixture is the pin: a new fixture written to the
    # old shape fails here rather than shipping as known-good.
    forbidden = {
        path.name: [
            f.check_id
            for f in run_checks(
                path.read_text(encoding="utf-8"), "build-session", KEYED_PAGE_ROWS, context={}
            )
        ]
        for path in sorted(iter_tree(FIXTURES, "session*.md"), key=lambda p: p.name)
    }
    assert {name: ids for name, ids in forbidden.items() if ids} == {}


def test_the_sweep_actually_reaches_the_corpus():
    # A sweep that walks nothing passes vacuously. The corpus is many fixtures; pin
    # that the walk finds them, so a renamed fixture dir cannot quietly empty it.
    assert len(list(iter_tree(FIXTURES, "session*.md"))) > 5
