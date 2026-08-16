"""Units for the append-only findings log.

Every test writes to a pytest ``tmp_path`` handed in through the module's
injectable ``path`` argument — the real consumer-side log at
``.claude/validator-findings/findings.jsonl`` is never touched, and a guard test
below asserts that default stays relative so it can never resolve into the
installed skill folder.

Same shape as ``test_checker.py``: flat imports, plain ``def test_...()``
functions, assertions over external behavior only.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

import findings_log
from findings_log import DEFAULT_LOG_PATH, log_finding, log_run


def _lines(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    """A log under a directory that does not exist yet — the first append must
    create it, as it will on a fresh campaign clone."""
    return tmp_path / "validator-findings" / "findings.jsonl"


# --------------------------------------------------------------------------- #
# The append itself.
# --------------------------------------------------------------------------- #

def test_first_append_creates_the_parent_directory(log_path):
    assert not log_path.parent.exists()
    assert log_finding("combat-generator", "combat-generator/enemies-line-arithmetic", "mechanical", "healed",
                       heal_attempts=1, output_anchor="> [!encounter-meta] block",
                       path=log_path) is True
    assert log_path.exists()


def test_appends_accumulate_one_json_object_per_line(log_path):
    log_run("build-session", ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header"], path=log_path)
    log_finding("build-session", "build-session/skeleton-sections-in-order", "mechanical", "healed", heal_attempts=1, path=log_path)
    log_finding("build-session", "build-session/key-npcs-header", "mechanical", "unhealable", heal_attempts=3, path=log_path)

    records = _lines(log_path)
    assert [r["record"] for r in records] == ["run", "finding", "finding"]
    assert [r.get("inventory_row") for r in records] == [None, "build-session/skeleton-sections-in-order", "build-session/key-npcs-header"]


def test_appending_never_rewrites_earlier_lines(log_path):
    log_finding("dungeon-generator", "dungeon-generator/two-entrances", "mechanical", "healed", heal_attempts=2, path=log_path)
    first = log_path.read_text(encoding="utf-8")
    log_finding("dungeon-generator", "dungeon-generator/objective-two-routes", "mechanical", "healed", heal_attempts=1, path=log_path)
    assert log_path.read_text(encoding="utf-8").startswith(first)


# --------------------------------------------------------------------------- #
# The finding record — the grouping key and the three channels.
# --------------------------------------------------------------------------- #

def test_finding_record_carries_every_schema_field(log_path):
    log_finding("combat-generator", "combat-generator/stat-block-refs-on-enemies-line", "mechanical", "unhealable",
                heal_attempts=3, output_anchor="the Enemies line", path=log_path)
    record, = _lines(log_path)
    assert record == {
        "record": "finding",
        "timestamp": record["timestamp"],
        "skill": "combat-generator",
        "inventory_row": "combat-generator/stat-block-refs-on-enemies-line",
        "tier": "mechanical",
        "disposition": "unhealable",
        "heal_attempts": 3,
        "output_anchor": "the Enemies line",
        "quoted_span": "",
        "reason": "",
    }


def test_healed_findings_are_logged_not_filtered(log_path):
    """The silent class is the valuable one — weight is a property of the group,
    so nothing is filtered at write time."""
    for _ in range(4):
        log_finding("combat-generator", "combat-generator/enemies-line-arithmetic", "mechanical", "healed", heal_attempts=1, path=log_path)
    rows = [r["inventory_row"] for r in _lines(log_path) if r["disposition"] == "healed"]
    assert rows == ["combat-generator/enemies-line-arithmetic"] * 4


def test_judgement_finding_carries_its_evidence(log_path):
    """The evidence contract: a judgement finding records the quoted span it
    fired on and a one-line reason, so a wrong verdict is distinguishable from
    a right one at read time."""
    log_finding("build-session", "build-session/spotlight-coverage", "judgement", "raised",
                output_anchor="the roster table",
                quoted_span="Nyla is named nowhere on the page",
                reason="the staged rite is an unused obvious carrier", path=log_path)
    record, = _lines(log_path)
    assert record["disposition"] == "raised"
    assert record["heal_attempts"] is None
    assert record["tier"] == "judgement"
    assert record["quoted_span"] == "Nyla is named nowhere on the page"
    assert record["reason"] == "the staged rite is an unused obvious carrier"


def test_judgement_finding_without_evidence_raises(log_path):
    """A verdict with nothing behind it cannot be audited — both halves of the
    evidence are required, and the refusal is a caller bug, not I/O."""
    with pytest.raises(ValueError, match="quoted_span and reason"):
        log_finding("build-session", "build-session/plain-language", "judgement", "raised",
                    quoted_span="thread the needle", path=log_path)
    with pytest.raises(ValueError, match="quoted_span and reason"):
        log_finding("build-session", "build-session/plain-language", "judgement", "raised",
                    reason="undefined metaphor in a spotlight line", path=log_path)
    assert not log_path.exists()


def test_mechanical_finding_needs_no_evidence_fields(log_path):
    """The evidence contract is judgement-only: a deterministic finding states
    expected-vs-actual through the checker, so the fields default empty."""
    log_finding("combat-generator", "combat-generator/budget-line-arithmetic", "mechanical", "healed",
                heal_attempts=2, path=log_path)
    record, = _lines(log_path)
    assert record["quoted_span"] == ""
    assert record["reason"] == ""


def test_heal_attempts_and_anchor_default_when_unknown(log_path):
    log_finding("dungeon-generator", "dungeon-generator/every-flagged-pc-staged", "mechanical", "healed", path=log_path)
    record, = _lines(log_path)
    assert record["heal_attempts"] is None
    assert record["output_anchor"] == ""


def test_timestamp_is_utc_iso8601(log_path):
    log_finding("build-session", "build-session/skeleton-sections-in-order", "mechanical", "healed", heal_attempts=1, path=log_path)
    record, = _lines(log_path)
    parsed = datetime.fromisoformat(record["timestamp"])
    assert parsed.utcoffset().total_seconds() == 0


# --------------------------------------------------------------------------- #
# The run record — the denominator.
# --------------------------------------------------------------------------- #

def test_run_record_carries_the_check_id_list_not_a_count(log_path):
    log_run("build-session", ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header", "build-session/role-word-count"], path=log_path)
    record, = _lines(log_path)
    assert record["record"] == "run"
    assert record["checks_evaluated"] == ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header", "build-session/role-word-count"]
    assert record["skill"] == "build-session"


def test_run_record_copies_the_check_list(log_path):
    checks = ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header"]
    log_run("build-session", checks, path=log_path)
    checks.append("build-session/role-word-count")
    record, = _lines(log_path)
    assert record["checks_evaluated"] == ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header"]


# --------------------------------------------------------------------------- #
# The run record as the entry condition — clean is not absent.
# --------------------------------------------------------------------------- #

def test_a_clean_pass_is_distinguishable_from_a_pass_that_never_ran(log_path):
    """The whole run-record design in one assertion. A tier that ran and found nothing leaves
    a run row; a tier that was bypassed leaves no file. Before the run record
    carried a tier, both tiers' silence looked the same as each other's *and* as a
    clean run."""
    log_run("build-session", ["build-session/skeleton-sections-in-order"], path=log_path)
    clean = _lines(log_path)
    assert [r["record"] for r in clean] == ["run"]
    assert not [r for r in clean if r["record"] == "finding"]


def test_run_record_names_its_tier_and_defaults_to_mechanical(log_path):
    """The two-argument call shipped in ``self-heal-loop.md`` is the mechanical
    one, so it stays correct rather than becoming unlabelled."""
    log_run("build-session", ["build-session/key-npcs-header"], path=log_path)
    record, = _lines(log_path)
    assert record["tier"] == "mechanical"


def test_judgement_run_record_is_distinguishable_from_a_mechanical_one(log_path):
    """Both tiers write a run row over the same skill; without the tier field a
    reader could not tell which tier's denominator it was holding. A judgement
    run also carries its verdict — an approve run with zero findings and a run
    that never happened must stay distinguishable."""
    log_run("build-session", ["build-session/skeleton-sections-in-order"], path=log_path)
    log_run("build-session", ["build-session/npc-rows-named", "build-session/clue-interpretability"],
            tier="judgement", verdict="approve", path=log_path)
    mechanical, judgement = _lines(log_path)
    assert mechanical["tier"] == "mechanical"
    assert "verdict" not in mechanical
    assert judgement["tier"] == "judgement"
    assert judgement["verdict"] == "approve"
    assert judgement["checks_evaluated"] == ["build-session/npc-rows-named", "build-session/clue-interpretability"]


def test_judgement_run_without_a_verdict_raises(log_path):
    """The verdict is the property of the pass; a judgement run row that omits
    it is the retired multi-round shape and is refused."""
    with pytest.raises(ValueError, match="judgement run requires verdict"):
        log_run("build-session", ["build-session/npc-rows-named"], tier="judgement", path=log_path)
    assert not log_path.exists()


def test_mechanical_run_with_a_verdict_raises(log_path):
    """Deterministic findings are their own verdict; a labelled one is a
    mislabelled caller."""
    with pytest.raises(ValueError, match="mechanical run carries no verdict"):
        log_run("build-session", ["build-session/key-npcs-header"], verdict="approve", path=log_path)
    assert not log_path.exists()


def test_unknown_tier_on_a_run_raises(log_path):
    """Same caller-bug class as ``log_finding``'s tier check, and the same refusal
    — a mislabelled denominator silently corrupts every rate computed from it."""
    with pytest.raises(ValueError, match="unknown tier"):
        log_run("build-session", ["build-session/key-npcs-header"], tier="spec", path=log_path)
    assert not log_path.exists()


# --------------------------------------------------------------------------- #
# A lost line says so — the swallow stays, the silence does not.
# --------------------------------------------------------------------------- #

def test_io_failure_is_announced_on_stderr(tmp_path, capsys):
    blocked = tmp_path / "a-file-not-a-dir"
    blocked.write_text("", encoding="utf-8")
    assert log_finding("build-session", "build-session/key-npcs-header", "mechanical", "healed",
                       path=blocked / "findings.jsonl") is False
    assert "findings-log:" in capsys.readouterr().err


def test_the_announcement_carries_the_record_it_lost(tmp_path, capsys):
    """So an operator who sees one can re-append the line by hand, instead of
    reconstructing a prep session from memory the way  had to."""
    blocked = tmp_path / "a-file-not-a-dir"
    blocked.write_text("", encoding="utf-8")
    log_finding("combat-generator", "combat-generator/enemies-line-arithmetic", "mechanical", "unhealable",
                heal_attempts=3, output_anchor="the Enemies line", path=blocked / "findings.jsonl")

    err = capsys.readouterr().err
    quoted = json.loads(err[err.index("{"):err.rindex("}") + 1])
    assert quoted["inventory_row"] == "combat-generator/enemies-line-arithmetic"
    assert quoted["disposition"] == "unhealable"


def test_every_lost_line_is_announced_not_just_the_first(tmp_path, capsys):
    """Why this is a bare ``stderr`` write and not ``warnings.warn``: warnings dedup
    per call site, and the second through Nth loss are the ones that say *this is
    systematic*."""
    blocked = tmp_path / "a-file-not-a-dir"
    blocked.write_text("", encoding="utf-8")
    target = blocked / "findings.jsonl"
    for _ in range(3):
        log_finding("build-session", "build-session/key-npcs-header", "mechanical", "healed", path=target)

    assert capsys.readouterr().err.count("findings-log:") == 3


# --------------------------------------------------------------------------- #
# The default path does not invent a campaign repo.
# --------------------------------------------------------------------------- #

def test_default_path_declines_a_working_directory_with_no_campaign_dir(tmp_path, monkeypatch, capsys):
    """A loop driven from outside the campaign repo used to build the tree wherever
    it stood, write the session's telemetry to a path nobody reads, and return
    True."""
    monkeypatch.chdir(tmp_path)
    assert log_run("build-session", ["build-session/key-npcs-header"]) is False
    assert not (tmp_path / ".claude").exists()
    assert "not a campaign repo" in capsys.readouterr().err


def test_default_path_writes_when_the_campaign_dir_is_already_there(tmp_path, monkeypatch):
    """``.claude/`` pre-existing is the documented premise of the placement — the
    log sits beside the campaign repo's ``.claude/agent-memory/``. The leaf
    ``validator-findings/`` is still created on first append, as on a fresh clone."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".claude").mkdir()
    assert log_run("build-session", ["build-session/key-npcs-header"]) is True
    record, = _lines(tmp_path / DEFAULT_LOG_PATH)
    assert record["skill"] == "build-session"


def test_an_explicit_path_is_taken_at_its_word(tmp_path, monkeypatch):
    """Only the *default* path is second-guessed. An explicit ``path=`` is a caller
    stating where it wants the log — a test's ``tmp_path``, a reader pointing at
    another campaign — and no ``.claude/`` is required for it."""
    monkeypatch.chdir(tmp_path)
    elsewhere = tmp_path / "somewhere-else" / "findings.jsonl"
    assert log_run("build-session", ["build-session/key-npcs-header"], path=elsewhere) is True
    assert elsewhere.exists()


# --------------------------------------------------------------------------- #
# Validation — caller bugs raise, I/O failures do not.
# --------------------------------------------------------------------------- #

def test_unknown_tier_raises(log_path):
    with pytest.raises(ValueError, match="unknown tier"):
        log_finding("build-session", "build-session/skeleton-sections-in-order", "deterministic", "healed", path=log_path)
    assert not log_path.exists()


def test_disposition_the_tier_cannot_produce_raises(log_path):
    with pytest.raises(ValueError, match="judgement tier"):
        log_finding("build-session", "build-session/spotlight-coverage", "judgement", "healed", path=log_path)
    with pytest.raises(ValueError, match="mechanical tier"):
        log_finding("build-session", "build-session/skeleton-sections-in-order", "mechanical", "raised", path=log_path)
    assert not log_path.exists()


def test_io_failure_is_swallowed_and_reported(tmp_path):
    """A read-only log directory must not abort a DM's prep session — a lost line
    beats a dead run."""
    blocked = tmp_path / "a-file-not-a-dir"
    blocked.write_text("", encoding="utf-8")
    assert log_finding("build-session", "build-session/skeleton-sections-in-order", "mechanical", "healed",
                       path=blocked / "findings.jsonl") is False


# --------------------------------------------------------------------------- #
# Placement and purity guards.
# --------------------------------------------------------------------------- #

def test_default_path_is_relative_to_the_cwd_not_the_installed_skill():
    """This module materialises inside each installed skill folder; a
    ``__file__``-relative default would write the campaign's telemetry into the
    install instead of the campaign repo."""
    assert not DEFAULT_LOG_PATH.is_absolute()
    assert DEFAULT_LOG_PATH == Path(".claude/validator-findings/findings.jsonl")


def test_the_checker_library_still_does_no_io():
    """``checker.py``'s check functions stay pure — the write path lives here and
    only here."""
    source = (Path(findings_log.__file__).parent / "checker.py").read_text(encoding="utf-8")
    for forbidden in ("open(", "Path(", "import os", "read_text", "write_text"):
        assert forbidden not in source, f"checker.py gained file I/O: {forbidden}"
