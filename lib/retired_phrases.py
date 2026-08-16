"""Maintainer guard: a retired contract phrase must not survive
anywhere in the tree.

`docs/campaign-contract.md` carries a *"Must move in the same commit"* table —
the right mechanism for the library's cross-skill couplings, and hand-maintained
prose that nothing consults. `d1a08f9` is the proof: it changed a fact in
`build-session/SKILL.md` and left six other locations asserting the old one.
The contract table didn't help, because reading it is a step a human has
to remember.

This is the dumb half of that problem, and dumb on purpose. A real dependency
graph over prose skills isn't worth building; a denylist of **strings that used
to be true and are not any more** costs almost nothing and catches the failure
that actually occurs — the half-applied change. Both seed phrases below
(`"the spotlight plan is on the page, not in chat"`, `"files one onto the
session page"`) would have failed `d1a08f9`'s successor commit on the spot.

It shares its matching with ``citation_anchors`` — literal, whitespace-normalised
— because both guards are the same question asked in opposite directions: *this
string must still appear in this file* / *this string must appear nowhere*.
Normalising matters as much here: `"the spotlight plan is on the page, not in
chat"` lived wrapped across two lines of a checklist box, so a byte-literal grep
would have missed the very phrase this list is seeded from.

Retiring a phrase
-----------------

When a commit changes what the library asserts — not a reword, a **reversal** —
add the sentence it retires to ``RETIRED`` below, with the commit that retired it
in the comment beside it. Two rules, both enforced by the tests:

1. The phrase must be **gone from the whole tree** when you add it. The entry is
   a claim about the present, so it fails on arrival otherwise — which is the
   point: adding the entry is how you find the copy you missed.
2. It must be a phrase that genuinely **used to be there**. Quote the retiring
   commit's own ``-`` side rather than paraphrasing from memory; a phrase that
   was never in the tree guards nothing and will never fire.

Name the commit **as it lands on `main`**, not the branch commit you wrote it
on. This repo squash-merges, so the branch commit is unreachable in a fresh
clone even though it still resolves in the working copy that created it — both
commit-side tests shell out to git and would pass for you and fail in CI. That
means an entry retired by your own commit lands one commit *after* it: merge
first, then add the entry naming the squash. The assertion was added after the
same failure surfaced, and repointed the two pre-existing commit references —
seven entries between them — that were already naming vanished branch commits.

Keep entries long enough to be unambiguous and short enough to survive an
unrelated reword nearby — one clause of the retired claim, not a paragraph.

This guard lives at the ``lib/`` top level, outside ``lib/mechanical-checker/``,
for the same reason the anchor check does: that directory materialises into every
consumer, and this is a check over *this repo's* history. It runs here
(``pytest lib/``) and never ships.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from citation_anchors import REPO_ROOT, normalise

# File types the sweep reads. Everything else in the tree is an image or a
# binary fixture and holds no prose.
TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".css", ".yml", ".yaml"}

# The two files that *quote* retired phrases as data. Scanning them would make
# every entry fail against itself.
SELF_REFERENTIAL = {
    "lib/retired_phrases.py",
    "lib/test_retired_phrases.py",
}


# Commits named by entries that predate the public cut. This repo was released
# as a single orphan commit, so these hashes resolve only in the private
# predecessor's history: the tree-absence sweep still enforces every entry
# below, but the provenance tests (commit exists, on main, quotable from its
# removed side) skip commits in this frozen set. The set is sealed at the cut —
# a NEW entry must name the squash commit as it lands on this repo's `main`
# and never joins this list.
PRE_PUBLIC_CUT = frozenset({
    "ab0d0cb", "d1a08f9", "2c2ab3a", "8be33ec", "2b49772", "d88dc13",
    "3aeaa2f", "93cdb6d", "37aa169", "a9f688e", "f961822", "024b1f7",
    "dd75d5b", "c6757b8",
})


@dataclass(frozen=True)
class RetiredPhrase:
    text: str
    retired_by: str  # the commit that removed it
    why: str


# Seeded from the two commits of the motivating half-applied change, plus the
# delegate-interface refactor — the other coupling change the contract table
# records. Every entry was verified present in the tree at the retiring commit's
# parent and absent from it afterwards; the tests re-assert the absent half on
# every run.
RETIRED = [
    # --- ab0d0cb: the session spotlight plan became transient, never filed.
    # The half-applied version of this change is this guard's motivating failure:
    # d1a08f9 fixed build-session and left six other locations asserting the old
    # fact. These two are the seed phrases the module docstring quotes.
    RetiredPhrase(
        "the spotlight plan is on the page, not in chat",
        "ab0d0cb",
        "The plan is transient prep-run state; only its per-beat effects reach the page.",
    ),
    RetiredPhrase(
        "files one onto the session page",
        "ab0d0cb",
        "build-session files no plan; a delegate is handed the beat in-run.",
    ),
    RetiredPhrase(
        "The filed **session spotlight plan**",
        "ab0d0cb",
        "The contract table's own name for the coupling, back when the plan was filed.",
    ),
    RetiredPhrase(
        "which both read it before allocating texture",
        "ab0d0cb",
        "Delegates are handed the beat now; they never read a filed plan.",
    ),
    RetiredPhrase(
        "the plan is durable bookkeeping, not chat state",
        "ab0d0cb",
        "Exactly inverted: the plan is chat state, and dies with the run.",
    ),
    RetiredPhrase(
        "reconcile the prep's spotlight plan against the table",
        "ab0d0cb",
        "catch-up reconciles from the page's annotations — the plan is gone by then.",
    ),
    RetiredPhrase(
        "record which planned spotlights **fired**",
        "ab0d0cb",
        "The ledger is the page's staged beats, not the plan's allocations.",
    ),
    # --- d1a08f9: the same fact, one commit earlier and one skill only. These
    # are the sentences that commit removed from build-session/SKILL.md.
    RetiredPhrase(
        "The spotlight plan is durable, unlike a lean sheet",
        "d1a08f9",
        "The plan is transient on every run, lean sheet or full page.",
    ),
    RetiredPhrase(
        "only its two durable products",
        "d1a08f9",
        "A lean-sheet run has one durable product: the Key NPCs roster.",
    ),
    RetiredPhrase(
        "Like the spotlight plan, the roster is durable",
        "d1a08f9",
        "The roster is durable; the plan is not, so the comparison is backwards.",
    ),
    # --- 2c2ab3a: callers stopped loading combat-generator's internals and
    # started invoking its delegate interface. The contract table records the
    # retirement in prose ("Nobody loads these across a skill boundary any more").
    RetiredPhrase(
        "dungeon-generator, which loads both in its Step 5",
        "2c2ab3a",
        "dungeon-generator invokes the delegate interface; it loads no internals.",
    ),
    RetiredPhrase(
        "which loads them for its per-fight budgets and complications",
        "2c2ab3a",
        "Same retirement, stated from combat-generator's side.",
    ),
    # --- 8be33ec: build-session stopped allocating the session spotlight
    # plan inline and started invoking spotlight's delegate interface. The same
    # load→delegate reversal already made for combat-generator, one edge over — and
    # the last `../spotlight/` path in build-session went with it.
    RetiredPhrase(
        "this step also owns the **session spotlight plan**: load that skill's",
        "8be33ec",
        "build-session invokes spotlight's delegate interface; the step owns no allocation.",
    ),
    RetiredPhrase(
        "read the profiles via its data ladder and the recent ledger, and allocate the",
        "8be33ec",
        "The ladder and the allocation live behind the delegate boundary now.",
    ),
    RetiredPhrase(
        "and only then loads `doctrine.md` and its Legibility section",
        "8be33ec",
        "The contract row is a delegate edge: build-session opens none of spotlight's files.",
    ),
    RetiredPhrase(
        "Consumers load them directly: combat-generator and dungeon-generator (texturing fights), build-session (the session spotlight plan)",
        "8be33ec",
        "build-session is a delegate caller, not a file loader; catch-up dropped off the list in the spotlight-transience sweep.",
    ),
    # --- 2b49772: build-session started reading a session brief, and its
    # flat no-invention rule inverted into a fallback ladder — derive from the
    # record, draw on the wider corpus, invent where both are silent. The one
    # reversal in that body of work. Only the prohibition is retired: the
    # sentence's "say so" half survives, demoted into Step 7's report.
    RetiredPhrase(
        "Do not invent content at any step",
        "2b49772",
        "Silence in the brief falls back to derive · corpus · invent; the run never halts on a gap.",
    ),
    # --- d88dc13: dungeon-generator's Step 8 now restates the
    # `Spotlight (scene):` template inline, so the cross-skill pointer beside it
    # became a citation and the contract row was retyped to match.
    RetiredPhrase(
        "which dungeon-generator does not restate",
        "d88dc13",
        "Step 8 restates the line's template inline; the pointer is a citation now, not a load.",
    ),
    # --- 3aeaa2f: dungeon-generator took ownership of the artifact it
    # hands back. The edge table ships already concealed instead of being left to
    # the caller, and the key files onto the session page pre-play instead of onto
    # the anchor node's — a node page is canon and takes no session-scoped content
    # while the session is unplayed.
    RetiredPhrase(
        "whether it files onto the session page is the caller's call",
        "3aeaa2f",
        "The producer decides: the table ships concealed, and the caller embeds it as-is.",
    ),
    RetiredPhrase(
        "Dungeon key onto the anchor node's page",
        "3aeaa2f",
        "The key files onto the session page pre-play; a node page takes no unplayed session content.",
    ),
    # --- 93cdb6d: the map render stopped assuming the node page. Its
    # input contract reads the edge list off whichever page carries it, and the
    # rendered map files with the session it was purpose-built for. (The rule
    # that the render never runs before filing is *not* reversed — only the
    # filing's location moved — so it stays true and stays unretired.)
    RetiredPhrase(
        "Embed on the node page via the `[!map]` callout",
        "93cdb6d",
        "The map is session-scoped output; it embeds on the session page as its keyed hotspot map.",
    ),
    # --- 37aa169: the producer stopped asking each keyed room for an exits
    # list. `d155428` abolished the per-key enumeration on the page format's side
    # and this is the producer side finally agreeing — the typed edge data lives
    # once, in the concealed `## Edges (render-ready)` section, and the room's own
    # prose carries the connections that matter with their types and DCs.
    RetiredPhrase(
        "its typed exits (the full edge list, render-ready)",
        "37aa169",
        "Typed edge data lives once in the concealed edge section; the room's prose carries the connections that matter.",
    ),
    # --- a9f688e: the map render's *invocation* narrowed to a session page. The
    # filing step has exactly one target, so a render read off a node page
    # terminated nowhere. Two entries because the admission was stated twice —
    # in the step and again in the pointer to it — and the second copy is the one
    # a single-site edit would have left behind. The input contract is **not**
    # reversed: the render still reads the edge list off whichever page carries
    # it. Only where you may invoke it moved.
    RetiredPhrase(
        "against any page that already carries an `## Edges (render-ready)` section",
        "a9f688e",
        "Standalone runs only against a session page; the filing step files there and nowhere else.",
    ),
    RetiredPhrase(
        "against any page that already has an `## Edges (render-ready)` section",
        "a9f688e",
        "Step 9's pointer narrows with the step it points at — the copy a one-file edit misses.",
    ),
    # --- f961822: rules sourcing went tool-agnostic. The doctrine's hard
    # stop existed for the tools-not-installed case; with the SRD as the chain's
    # floor that case no longer halts a run — only an unreachable *chain* does,
    # and then the obligation is to name the gap, never to stop cold. Two entries
    # because the claim lived in two wordings: the doctrine's own sentence and
    # the shorthand the contract and doctrine_sync docstring used for it.
    RetiredPhrase(
        "If the tools are unavailable, **say so and stop**",
        "f961822",
        "No tool is required any more; the chain falls back to the SRD, and only a dry chain ends a lookup.",
    ),
    RetiredPhrase(
        "stop if the tools are unavailable",
        "f961822",
        "The third obligation is now name-the-gap at the chain's tail, not a stop on missing tools.",
    ),
    # --- 024b1f7: party-sync dropped D&D Beyond scraping for the
    # tool-agnostic intake chain — any environment character tool first, the DM
    # in chat as the floor. Three reversals: the skill always has a fetch path
    # now (the interview), a refresh makes no API calls at all, and freshness is
    # session-boundary ("confirmed since your last session"), not calendar
    # arithmetic.
    RetiredPhrase(
        "this skill has no other fetch path",
        "024b1f7",
        "The interview rung is the floor; a missing tool falls back to the DM in chat, never a stop.",
    ),
    RetiredPhrase(
        "A refresh is one GET per character",
        "024b1f7",
        "A refresh walks the intake chain — tool reads or chat answers — and makes no HTTP calls of its own.",
    ),
    RetiredPhrase(
        "**more than 7 days old**, warn the DM and offer to re-sync",
        "024b1f7",
        "Freshness is session-boundary: unconfirmed since the last played session prompts the offer, not a calendar age.",
    ),
    # --- dd75d5b: the wiki scaffold gained inventory rows. The scaffold work
    # shipped the template assets while the setup skill did not yet exist, so its
    # README correctly recorded that no skill promised anything about the scaffold
    # and left the question open. The setup-skill build then gave the bootstrap
    # phase two promises
    # about this very template — starts green, preflight names every landed path
    # — and the standing "no row" claim survived that commit, which is the
    # half-applied shape this list exists to catch.
    RetiredPhrase(
        "no skill gained or changed a checkable promise",
        "dd75d5b",
        "The setup skill's bootstrap phase promises the fresh copy checks clean and the preflight names every shipped top-level path.",
    ),
    RetiredPhrase(
        "Whether scaffold templates warrant their own rows is an open question",
        "dd75d5b",
        "Settled: they warrant static-lint rows, and lib/wiki_scaffold_lint.py is derived from them.",
    ),
    # --- c6757b8: the setup skill's content-tool phase got built. Phase 1
    # now surveys the environment for content tools, smoke-tests each, and offers
    # to connect more — so the README's "stubbed" caveat and the stub's own
    # one-line deferral both reversed in the same commit.
    RetiredPhrase(
        "a content-tool phase is stubbed and not built yet",
        "c6757b8",
        "The phase is built: it surveys, smoke-tests, and offers to connect content tools.",
    ),
    RetiredPhrase(
        "content-tool setup is coming",
        "c6757b8",
        "It arrived: phase 1 runs the content-tool survey instead of deferring to a future build.",
    ),
    # --- ee88018: the never-executed trace and diff inventory rows were
    # deleted rather than given the harness they waited on. The inventory's
    # harness section had claimed the trace tier as the library's coverage of
    # its hard prohibitions and as feasibility-confirmed; with the rows gone,
    # both claims are reversed — the promises live only in the skill text's
    # own MUSTs now, and no trace assertion covers anything.
    RetiredPhrase(
        'and "**MUST**" in the library is one of these',
        "ee88018",
        "No trace rows exist any more; a never/MUST is skill-text doctrine, not a trace assertion.",
    ),
    RetiredPhrase(
        "the headless which-skill-fired research spike",
        "ee88018",
        "The spike's feasibility claim died with the trace class; nothing cites it as grounds any more.",
    ),
    # --- 7940851: the verification-chain cut — one one-round fresh check
    # replaces the dual-axis, multi-round judgement loop; findings_log gains
    # the judgement tier's real code path.
    RetiredPhrase(
        "Two axes, two checkers.",
        "7940851",
        "The Spec and Standards bars are graded by one fresh check in one pass; "
        "the parallel second checker with an unmerged verdict is gone.",
    ),
    RetiredPhrase(
        "Three rounds, then the loop exhausts.",
        "7940851",
        "The check is one round with one fix pass and no re-grade; there is no "
        "loop left to exhaust.",
    ),
    RetiredPhrase(
        "writes this record by hand",
        "7940851",
        "The judgement tier now logs through findings_log's own parameters "
        "(verdict, quoted_span, reason); no checker restates the schema by hand.",
    ),
    RetiredPhrase(
        "capped at three rounds",
        "7940851",
        "Back-pressure as a capped multi-round loop is retired; the fresh check "
        "grades once.",
    ),
    # --- 7467a0d: the generator merge — dungeon-generator and combat-generator
    # became build-session's internal `combat.md` / `dungeon.md` procedures.
    # Every skill installs alone now, so the README's install clusters, the
    # contract's hard-edge accounting, and the two-copy rules-sourcing doctrine
    # (with the `doctrine_sync` guard over it) reversed in the same commit.
    RetiredPhrase(
        "three skills are not standalone",
        "7467a0d",
        "Every skill installs alone; the generators are build-session's internal "
        "procedures, not cluster members.",
    ),
    RetiredPhrase(
        "The duplication is the accepted answer",
        "7467a0d",
        "The rules-sourcing doctrine lives once, inside build-session; "
        "doctrine_sync retired with the second copy.",
    ),
    RetiredPhrase(
        "Every hard edge points at `spotlight` or `combat-generator`",
        "7467a0d",
        "No hard edge remains: the generator edges became internal loads and the "
        "spotlight edge is one guarded, degradable load.",
    ),
    RetiredPhrase(
        "Editing the rules-sourcing doctrine: edit both copies",
        "7467a0d",
        "There is one copy; the contract section demanding the paired edit died "
        "with the second.",
    ),
    RetiredPhrase(
        "an edit to one copy is an edit to both, in the same commit",
        "7467a0d",
        "Same reversal, stated as the rule that section enforced.",
    ),
]


@dataclass(frozen=True)
class Survivor:
    phrase: RetiredPhrase
    path: str
    line: int

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.line}: retired phrase survives — "
            f'"{self.phrase.text}"\n'
            f"    retired by {self.phrase.retired_by}: {self.phrase.why}"
        )


def tracked_text_files(repo_root: Path = REPO_ROOT) -> list[str]:
    """Every tracked prose/source file, minus the two that quote the list."""
    listing = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [
        name
        for name in listing.split("\0")
        if name
        and Path(name).suffix in TEXT_SUFFIXES
        and name not in SELF_REFERENTIAL
    ]


def surviving_phrases(
    repo_root: Path = REPO_ROOT,
    phrases: list[RetiredPhrase] | None = None,
    files: list[str] | None = None,
) -> list[Survivor]:
    """Every retired phrase still present in the tree, with where it survives.

    Matched per line-window rather than per line, so a phrase that wraps — which
    the seeded ones do — is still found. The window is the line plus the two
    after it; retired claims are sentences, not paragraphs.
    """
    wanted = RETIRED if phrases is None else phrases
    needles = [(phrase, normalise(phrase.text)) for phrase in wanted]
    survivors: list[Survivor] = []
    for name in tracked_text_files(repo_root) if files is None else files:
        path = repo_root / name
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for index in range(len(lines)):
            window = normalise(" ".join(lines[index : index + 3]))
            for phrase, needle in needles:
                if needle in window and not any(
                    survivor.phrase is phrase and survivor.path == name
                    for survivor in survivors
                ):
                    survivors.append(Survivor(phrase, name, index + 1))
    return survivors


def main() -> int:
    survivors = surviving_phrases()
    for survivor in survivors:
        print(survivor)
    print(
        f"{'FAIL' if survivors else 'ok'}: {len(survivors)} surviving retired "
        f"phrase(s) of {len(RETIRED)} on the list"
    )
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
