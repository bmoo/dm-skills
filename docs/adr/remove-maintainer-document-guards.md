# Remove maintainer-document guards

Status: accepted.

## Context

This repository accumulated a second body of machinery that polices the first:
checks over its own maintenance documents. The runtime cost is negligible, but
the maintenance cost is not. A skill edit has to be reasoned about both for its
meaning and for every stable row id, citation, dependency declaration, fixture,
or symlink roster that it might falsify.

Those guards were built in response to a real failure: a commit changed a fact in
one skill and left several other locations asserting the old fact. They prevented
that class of stale restatement, but doing so made every skill edit pay the cost
of maintaining the verification documentation.

## Decision

Remove the maintainer-level guards and the maintenance paperwork they police.
The admission rule for checks is:

> A check earns a place in this repo only if it verifies shipped content or a
> consumer's repo. Checks over this repo's own maintenance documents do not get
> written.

The guards being removed are:

- `citation_anchors` caught a quoted phrase in a maintenance citation no longer
  appearing in the skill file named by that citation, as well as malformed or
  line-number citations.
- `dependency_clusters` caught a cross-skill relative load missing from the
  campaign contract's dependency table, a stale declared load, or an install
  command that omitted a hard dependency closure.
- `encounter_meta_spec` caught disagreement between the encounter-meta fields in
  the format document, the shipped checker's required-label literal, and the
  session parser's format example.
- `test_session_fixture_sweep` caught a session fixture in this repository's
  corpus encoding a keyed-page shape that the session-page format forbids.
- `test_symlink_integrity` caught a materialised asset under `skills/` that did
  not resolve to byte-identical content at its canonical `lib/` source.
- `tree_scan` and `test_tree_scan` caught a maintainer guard walking the tree
  independently instead of using the shared walker and its exclusions.

The shipped mechanical checker remains because it verifies skill output. The
wiki-scaffold lint remains because it verifies that a shipped template works in a
consumer's fresh repository. The coupled-shape sync table remains as prose: it
is not mechanically enforced and is a reminder to inspect related files when a
format changes.

## Consequences

The following defects will now go unnoticed by an automated repository guard:

- a quoted phrase becoming stale when the skill sentence it cites is reworded;
- an undeclared cross-skill load, a declaration left behind after the load is
  removed, or an install command that omits a hard dependency closure;
- an encounter-meta field list drifting across its format document, shipped
  checker, and parser;
- a session fixture encoding a page shape the format forbids;
- a symlinked skill asset resolving to content different from its canonical
  source; and
- a future maintainer guard independently walking the repository and thereby
  applying different exclusions.

The encounter-meta regression is the sharpest accepted cost. Removing its
single-source guard returns the block's field list to three unreconciled copies:
a label added to the format document is a label the shipped checker will not
require. This is accepted as one defect class in exchange for removing machinery
that taxes every skill edit.

The earlier stale-restatement failure can recur. The replacement is the surviving
sweep rule: when a commit reverses or changes a stated fact, read the change and
sweep the tree for the sentence it falsified. That human rule addresses the real
failure mode at a cost proportionate to how often it occurs, without permanently
maintaining a second system of documents and guards.
