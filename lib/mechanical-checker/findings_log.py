"""Append-only findings log — the durable write path for validator telemetry.

Five places in the
shipped library named *telemetry* as the destination for a verifier finding and
none of them defined a sink, so "it is telemetry" meant "it is discarded" — and
the discarded class is the valuable one. A mechanical check that heals on *every*
run is a generator systematically emitting the wrong thing while the checker
silently corrects it and nobody is told. This module is where those records land.

Two record kinds, one line of JSON each, distinguished by ``record``:

  - ``"finding"`` — one broken promise, keyed by ``inventory_row``. That key is
    the whole point: recurrence ranking becomes a ``GROUP BY`` instead of an
    excavation through a campaign's git history.
  - ``"run"`` — one per verification pass, carrying its ``tier`` and its
    ``checks_evaluated``. It supplies **the denominator**: "this row fired 12
    times" is unreadable without knowing whether that is 12 of 12 runs (a broken
    skill) or 12 of 400 (noise). It is also **the entry condition**: a pass
    that raised nothing writes this row and nothing else, so a tier that ran
    clean stays distinguishable from a tier that never ran. Both tiers write one
    — the judgement checker by hand, from its launch protocol — which is why the
    row names its tier.

Design constraints this module is built to:

  - **Stdlib only.** The loop fires at the table mid-prep and the whole library
    ships to consumers by folder-copy. No SDK, no service, no network, no
    ``pip install``.
  - **The check functions stay pure.** ``checker.py`` has zero file I/O and keeps
    it. All I/O lives here, in one module the loop calls after a verdict — never
    inside a check.
  - **The path is injectable.** Tests never touch the real log, and the placement
    stays cheap to revisit.
  - **No filtering at write time.** Weight is a property of the *group*, not the
    individual finding: one healed arithmetic slip carries none, forty are the
    top-ranked defect class. Log everything; rank at read time.

This is not a violation of the read-only law the two tiers ship under. That law
guarantees verification never alters what gets filed and never files anything
itself — the DM's yes stays the sole trigger that writes a page. An append-only,
out-of-band telemetry line is not filing, and nothing here feeds back into a
verdict.

Two safeguards close the silences exposed after a full prep session's telemetry went missing and
nothing anywhere said so:

  - **A lost line is announced.** The append stays best-effort — see ``_append``
    — but it now says so on ``stderr`` rather than only returning ``False``. A
    caller that never wrote and a caller whose write failed were otherwise
    indistinguishable from every angle, downstream and at the call site both.
  - **The default path does not invent a campaign repo.** ``.claude/`` must
    already exist for the default path to be written, because sitting beside one
    is that path's whole rationale (below). A loop driven from the wrong working
    directory used to create the tree wherever it stood and report success.

Neither closes the third property the run-record design names, and no code here can: a run that
bypasses this module entirely calls nothing that could notice. That one is closed
by the run record above being written *at all*, and at read time by
comparing runs on record against the pages a campaign actually filed.

Reading the log is deliberately out of scope — it is the maintainer-side, offline
half, reserved for the campaign reporting workflow.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Where the log lives.
# --------------------------------------------------------------------------- #
#
# Consumer-side and tracked in git, as a sibling of the campaign repo's existing
# ``.claude/agent-memory/`` (durable per-agent state) rather than inside it —
# same placement instinct, different category. ``agent-memory`` holds prose an
# agent reads back to recall things; this is append-only machine-grouped events
# for later analysis, and keeping them apart stops one being mistaken for the
# other.
#
# **Relative on purpose.** It resolves against the *current working directory* —
# the campaign repo where the loop runs — never against this module's own
# location. This file materialises inside each installed skill folder, so a
# ``__file__``-relative path would write the campaign's telemetry into the
# installed skill.
DEFAULT_LOG_PATH = Path(".claude/validator-findings/findings.jsonl")

_TIERS = {"mechanical", "judgement"}

# Which dispositions each tier may record. Mechanical findings end up healed (the
# silent class) or unhealable (the terminal escalation to the DM). A judgement
# finding only ever records that it was *raised*, once per round: whether it was
# resolved (present round 1, absent round 2) or survived to the DM (present in the
# final round) is inferred at read time from the sequence. Observed behaviour beats
# a generator's own account of whether it fixed something.
_DISPOSITIONS_BY_TIER = {
    "mechanical": {"healed", "unhealable"},
    "judgement": {"raised"},
}


# --------------------------------------------------------------------------- #
# The append — the single I/O primitive.
# --------------------------------------------------------------------------- #

def _warn(message: str) -> None:
    """Announce a lost telemetry line on ``stderr``.

    Before this stderr warning existed, swallowing the failure and returning ``False`` left a write that failed
    byte-identical to a write nobody attempted — an absent log read as a clean run
    either way. The swallow stays, because a lost line still beats a dead prep
    session. The silence does not.

    A bare ``stderr`` write rather than ``warnings.warn`` on purpose: the warnings
    module dedups per call site, so the second through Nth loss of a session — the
    ones that say *this is systematic, not a blip* — would be filtered out at
    exactly the moment they start to matter.
    """
    sys.stderr.write(f"findings-log: {message}\n")


def _now_iso() -> str:
    """UTC ISO-8601, seconds resolution. UTC so lexicographic sort is
    chronological — the analysis side defers ``run_id`` and leans on timestamp
    clustering to group findings into prep sessions."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append(record: Dict[str, Any], path: Optional[Path]) -> bool:
    """Append one JSON record as a line. Returns whether the write landed.

    **Best-effort by design, against this repo's house style.** Elsewhere the
    library fails loudly (an unknown check id raises) because that norm protects
    *verification correctness*. This is out-of-band telemetry firing at the table
    mid-prep: a read-only log directory, a full disk, or a missing parent must not
    abort a DM's prep session. A lost line beats a dead run, so I/O failures are
    swallowed and reported through the return value.

    Caller mistakes are a different class and still raise — see ``log_finding``.

    Every failure is **announced on stderr** as well as returned, and an
    announcement carries the record it lost, so an operator who sees one can
    re-append the line by hand instead of reconstructing a session from memory.
    """
    if path is None:
        # The default-path rule is intentional: the path is cwd-relative, and the repo it is meant to
        # resolve against is identified by the very ``.claude/`` this log is placed
        # beside (see DEFAULT_LOG_PATH). Absent, the loop is being driven from
        # somewhere that is not the campaign repo, and ``parents=True`` below would
        # cheerfully build the tree there, write a session's telemetry to a path
        # nobody reads, and return True. Decline, and say which directory it was.
        #
        # Only the *default* path is second-guessed. An explicit ``path=`` is a
        # caller stating where it wants the log — a test's ``tmp_path``, a reader
        # pointing at another campaign — and is taken at its word.
        campaign_dir = DEFAULT_LOG_PATH.parent.parent
        if not campaign_dir.is_dir():
            _warn(
                f"no {campaign_dir}/ in the working directory ({Path.cwd()}), "
                f"so this is not a campaign repo and {DEFAULT_LOG_PATH} was not "
                f"written. Drive the loop from the campaign root, or pass an "
                f"explicit path=. The record is lost: "
                f"{json.dumps(record, ensure_ascii=False, sort_keys=True)}"
            )
            return False
    target = Path(path) if path is not None else DEFAULT_LOG_PATH
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        # One ``write`` of one newline-terminated line in append mode, so
        # concurrent appenders interleave whole lines rather than shredding one.
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        _warn(f"could not append to {target}: {exc}. The record is lost: {line}")
        return False
    return True


# --------------------------------------------------------------------------- #
# The two public writers.
# --------------------------------------------------------------------------- #

def log_finding(
    skill: str,
    inventory_row: str,
    tier: str,
    disposition: str,
    heal_attempts: Optional[int] = None,
    output_anchor: str = "",
    path: Optional[Path] = None,
) -> bool:
    """Append one finding record. Returns whether the write landed.

    All three verification channels come through here — healed mechanical findings,
    terminal mechanical escalations, and judgement findings — because the silent
    class is precisely the one worth recording.

    - ``skill`` — which generator produced the output (``"combat-generator"``,
      ``"dungeon-generator"``, ``"build-session"``). One prep session emits
      findings from up to three skills, interleaved, because delegation is a
      chain.
    - ``inventory_row`` — the promise-pointer: the eval-inventory row this
      finding broke, which for a mechanical finding is the ``Finding``'s
      ``check_id`` verbatim. **The grouping key**, and a row id rather than a line
      citation because a line citation inherits the rot problem.
    - ``tier`` — ``"mechanical"`` or ``"judgement"``.
    - ``disposition`` — ``"healed"`` / ``"unhealable"`` for mechanical,
      ``"raised"`` for judgement (one record per round it appears).
    - ``heal_attempts`` — how many tries before the disposition stuck (the loop
      caps at 3). Left ``None`` for a judgement finding: the checker is stateless
      across rounds by design, and handing it its own round number would tell it
      that prior fix attempts happened — exactly the leak the independence rule
      forbids. Round order is recovered at read time from ``timestamp``, which is
      the same read-time inference that already distinguishes a finding the
      generator resolved from one that survived to the DM.
    - ``output_anchor`` — where in the output it broke (a ``Finding``'s
      ``output_location``, or the judgement finding's anchor).

    Raises ``ValueError`` on an unknown tier or a disposition that tier cannot
    produce. That is a caller bug, caught at authoring time, not a runtime I/O
    condition — unlike the I/O itself, which is best-effort (see ``_append``).
    """
    if tier not in _TIERS:
        raise ValueError(f"unknown tier {tier!r}; expected one of {sorted(_TIERS)}")
    allowed = _DISPOSITIONS_BY_TIER[tier]
    if disposition not in allowed:
        raise ValueError(
            f"disposition {disposition!r} is not one the {tier} tier can produce; "
            f"expected one of {sorted(allowed)}"
        )

    return _append(
        {
            "record": "finding",
            "timestamp": _now_iso(),
            "skill": skill,
            "inventory_row": inventory_row,
            "tier": tier,
            "disposition": disposition,
            "heal_attempts": heal_attempts,
            "output_anchor": output_anchor,
        },
        path,
    )


def log_run(
    skill: str,
    checks_evaluated: List[str],
    tier: str = "mechanical",
    path: Optional[Path] = None,
) -> bool:
    """Append one run record — the denominator for every finding row, and the
    record that a tier ran at all. Returns whether the write landed.

    **This row is the entry condition**. A tier that ran and found nothing
    writes this row and no findings; a tier that never ran writes nothing. Without
    it those two are the same empty file — which is how a full prep session's
    verification came to leave no trace at all and read afterwards as a clean run.
    So it fires **once per pass, unconditionally, before the findings**: a pass
    that dies mid-loop is still on record as having started, and the difference
    between *clean* and *absent* survives into the reporting workflow's read.

    ``tier`` is which tier ran — ``"mechanical"`` or ``"judgement"``. It defaults
    to ``"mechanical"`` on the ``context=`` precedent that keeps a shipped
    signature backward-compatible: the two-argument call in ``self-heal-loop.md``
    is the mechanical one, so every pre-existing call site stays correct rather
    than becoming silently mislabelled. A judgement pass names itself — its
    checker writes this record by hand, from
    ``lib/judgement-checker/checker-launch-protocol.md``, having no import path to
    this module. Unknown tiers raise, exactly as in ``log_finding``.

    Recorded so it is not rediscovered at read time: a ``"run"`` row carrying **no**
    ``tier`` at all predates , and is **mechanical** — the mechanical tier was
    the only one that wrote run rows before this commit.

    For the judgement tier ``checks_evaluated`` is the **rubric rows it graded**,
    which is the same quantity by the same argument: a row's failure rate needs the
    count of passes where that row was in force.

    ``checks_evaluated`` is **the list of check ids actually evaluated, not a
    count**. Not every check applies to every output, so a run-level total would
    silently inflate the failure rate of conditional checks and deflate the
    unconditional ones. The list makes the per-row denominator correct: *this row
    fired 12 times out of the 12 runs where it was applicable.*

    Known limitation, recorded so it is not rediscovered at read time: this is the
    ``checks`` list handed to ``run_checks``, which is as precise as the purity
    constraint allows. Conditionality *inside* a check function — a fight check
    returning no finding on a page with no fights — is not observable from
    outside without adding signalling to the check functions, which is exactly the
    I/O they are forbidden. A check that ran and found its subject absent counts
    as evaluated here.
    """
    if tier not in _TIERS:
        raise ValueError(f"unknown tier {tier!r}; expected one of {sorted(_TIERS)}")

    return _append(
        {
            "record": "run",
            "timestamp": _now_iso(),
            "skill": skill,
            "tier": tier,
            "checks_evaluated": list(checks_evaluated),
        },
        path,
    )
