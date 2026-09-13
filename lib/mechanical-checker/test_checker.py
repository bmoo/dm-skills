"""Fixture-driven units for the mechanical checker.

Flat imports, pytest run from within this dir, plain ``def test_...()``
functions, fixtures in a ``fixtures/`` dir. Every test exercises external behavior — a labeled artifact in,
an expected findings list out — and asserts WHICH promise the checker reports
broken, never how it walks the artifact internally.
"""

from pathlib import Path

import pytest

import checker
from checker import Finding, run_checks, register_check

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _restore_registry():
    """Snapshot the check registry and restore it after each test, so a test that
    registers a throwaway check (e.g. the ordering test below) can't leak into
    another test or another collection of this same module. Downstream check
    suites inherit this pattern along with the file."""
    saved = dict(checker._REGISTRY)
    try:
        yield
    finally:
        checker._REGISTRY.clear()
        checker._REGISTRY.update(saved)


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


# --------------------------------------------------------------------------- #
# Encounter-meta required lines (the reference check).
# --------------------------------------------------------------------------- #

def test_valid_block_yields_no_findings():
    artifact = _load("encounter_meta_valid.md")
    findings = run_checks(artifact, "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    assert findings == []


def test_missing_required_line_yields_one_finding():
    artifact = _load("encounter_meta_missing_terrain.md")
    findings = run_checks(artifact, "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    assert len(findings) == 1
    finding = findings[0]
    assert finding.check_id == "combat-generator/encounter-meta-required-lines"
    assert "Terrain" in finding.actual
    assert "missing" in finding.actual.lower()
    assert finding.output_location == "> [!encounter-meta] block"
    # the five present labels are not reported missing
    for present in ("Party", "Enemies", "Budget", "Spotlight", "Objective"):
        assert present not in finding.actual.split("(present:")[0]


def test_note_is_optional():
    # The broken fixture omits Note as well as Terrain; only Terrain is reported.
    artifact = _load("encounter_meta_missing_terrain.md")
    findings = run_checks(artifact, "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    assert "Note" not in findings[0].actual


def test_absent_block_is_a_finding():
    findings = run_checks("# A page with no fight\n\nJust prose.", "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    assert len(findings) == 1
    assert findings[0].check_id == "combat-generator/encounter-meta-required-lines"
    assert "no `> [!encounter-meta]` block" in findings[0].actual


def test_finding_is_the_pinned_shape():
    findings = run_checks(_load("encounter_meta_missing_terrain.md"), "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    f = findings[0]
    assert isinstance(f, Finding)
    # exactly the four pinned fields, all strings
    assert set(vars(f)) == {"check_id", "expected", "actual", "output_location"}
    assert all(isinstance(v, str) for v in vars(f).values())


# --------------------------------------------------------------------------- #
# run_checks — the pinned contract the generator check suites inherit.
# --------------------------------------------------------------------------- #

def test_run_checks_is_pure_no_io():
    # Called twice with the same string, identical output; no file handed in.
    artifact = _load("encounter_meta_valid.md")
    assert run_checks(artifact, "combat-generator", ["combat-generator/encounter-meta-required-lines"]) == run_checks(
        artifact, "combat-generator", ["combat-generator/encounter-meta-required-lines"]
    )


def test_empty_check_list_runs_nothing():
    assert run_checks("anything at all", "test-skill", []) == []


def test_unknown_check_id_raises():
    with pytest.raises(ValueError, match="unknown check id"):
        run_checks("x", "test-skill", ["test-skill/no-such-check"])


def test_check_from_wrong_skill_raises():
    # A check registered under another skill's qualifier may not be requested
    # by test-skill — ownership is enforced at the call.
    @register_check("test-other-skill/test-foreign", "test-other-skill")
    def _foreign(artifact):
        return []

    with pytest.raises(ValueError, match="owned by"):
        run_checks("x", "test-skill", ["test-other-skill/test-foreign"])


def test_findings_returned_in_requested_order():
    # Register two throwaway checks that always fire, assert order follows `checks`.
    @register_check("test-skill/test-order-first", "test-skill")
    def _a(artifact):
        return [Finding("test-skill/test-order-first", "e", "a", "loc")]

    @register_check("test-skill/test-order-second", "test-skill")
    def _b(artifact):
        return [Finding("test-skill/test-order-second", "e", "a", "loc")]

    ids = [f.check_id for f in run_checks(
        "x", "test-skill",
        ["test-skill/test-order-second", "test-skill/test-order-first"])]
    assert ids == ["test-skill/test-order-second", "test-skill/test-order-first"]


def test_register_check_rejects_duplicate_check_id():
    # Two checks under one id is the silent-collision failure class the registry
    # exists to kill: the second registration raises at import time.
    @register_check("test-skill/test-duplicate-id", "test-skill")
    def _first(artifact):
        return []

    with pytest.raises(ValueError, match="already registered"):
        @register_check("test-skill/test-duplicate-id", "test-skill")
        def _second(artifact):
            return []


def test_register_check_rejects_qualifier_skill_mismatch():
    # The slug's qualifier IS the producing skill; a check filed under another
    # skill's qualifier is an import-time error, not a latent mis-routing.
    with pytest.raises(ValueError, match="qualified by 'test-skill'"):
        @register_check("test-other-skill/test-misfiled", "test-skill")
        def _misfiled(artifact):
            return []


def test_register_check_rejects_an_unqualified_check_id():
    # An id carrying no `<skill>/` qualifier at all fails the same guard.
    with pytest.raises(ValueError, match="must be a '<producing skill>/<stem>' slug"):
        @register_check("test-unqualified", "test-skill")
        def _unqualified(artifact):
            return []


# --------------------------------------------------------------------------- #
# The combat subset. Each check: the good fixture yields zero
# findings; its broken fixture yields exactly one, asserting WHICH promise broke.
# --------------------------------------------------------------------------- #

GOOD = "combat_meta_good.md"
COMBAT_SUBSET = ["combat-generator/encounter-meta-required-lines", "combat-generator/enemies-line-arithmetic", "combat-generator/budget-line-arithmetic", "combat-generator/per-char-matches-budget-table", "combat-generator/distinct-stat-block-cap", "combat-generator/stat-block-refs-on-enemies-line", "combat-generator/spotlight-texture-in-palette", "combat-generator/targeted-spotlight-names-target-and-staging"]


def test_good_fixture_passes_the_whole_combat_subset():
    # The clean block breaks no combat mechanical promise — the DoD's happy path.
    assert run_checks(_load(GOOD), "combat-generator", COMBAT_SUBSET) == []


# The floating form's role-terrain line.

def test_floating_good_passes_combat_subset_plus_roles_check():
    # A floating fight fills the same six labels, so the whole subset applies,
    # plus the role-form Terrain rule its form adds.
    art = _load("combat_meta_floating_good.md")
    assert run_checks(art, "combat-generator", COMBAT_SUBSET + ["combat-generator/floating-terrain-roles"]) == []


def test_floating_concrete_terrain_is_one_finding():
    findings = run_checks(_load("combat_meta_floating_bad_concrete.md"), "combat-generator", ["combat-generator/floating-terrain-roles"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/floating-terrain-roles"
    assert "needs:" in f.expected
    assert "boathouse" in f.actual
    assert "Terrain" in f.output_location


def test_pinned_fixture_never_sees_the_floating_check():
    # The pinned good fixture is graded by the subset alone; the floating rule
    # is requested only for floating fights, so its concrete terrain is legal.
    assert run_checks(_load(GOOD), "combat-generator", COMBAT_SUBSET) == []


# Enemies-line arithmetic.

def test_good_fixture_sums():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/enemies-line-arithmetic"]) == []


def test_wrong_total_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_total.md"), "combat-generator", ["combat-generator/enemies-line-arithmetic"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/enemies-line-arithmetic"
    assert "600" in f.expected   # 6×25 + 1×450
    assert "500" in f.actual     # the wrong stated total
    assert "Enemies" in f.output_location


# Budget-line arithmetic (two independent sub-assertions).

def test_good_fixture_holds():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/budget-line-arithmetic"]) == []


def test_spent_over_budget_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_spent.md"), "combat-generator", ["combat-generator/budget-line-arithmetic"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/budget-line-arithmetic"
    assert "spent" in f.expected.lower()
    assert "800" in f.actual
    assert "Budget" in f.output_location


# Per-char matches the budget table.

def test_good_fixture_matches_table():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/per-char-matches-budget-table"]) == []


def test_wrong_per_char_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_perchar.md"), "combat-generator", ["combat-generator/per-char-matches-budget-table"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/per-char-matches-budget-table"
    assert "150" in f.expected      # Moderate, level 2 → 150
    assert "100" in f.actual        # the stated wrong per-char
    assert "Budget" in f.output_location


def test_stray_band_is_flagged():
    # The reference fixture labels the band "Hard" (75 = Moderate's value):
    # a band with no DMG column is itself the defect this check owns.
    findings = run_checks(_load("encounter_meta_valid.md"), "combat-generator", ["combat-generator/per-char-matches-budget-table"])
    assert len(findings) == 1
    assert findings[0].check_id == "combat-generator/per-char-matches-budget-table"
    assert "Hard" in findings[0].actual


# No more than three distinct stat blocks.

def test_good_fixture_within_cap():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/distinct-stat-block-cap"]) == []


def test_four_stat_blocks_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_fourtypes.md"), "combat-generator", ["combat-generator/distinct-stat-block-cap"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/distinct-stat-block-cap"
    assert "4 distinct" in f.actual
    assert "Enemies" in f.output_location


# Every creature carries a stat-block reference.

def test_good_fixture_all_tagged():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/stat-block-refs-on-enemies-line"]) == []


def test_bare_name_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_barename.md"), "combat-generator", ["combat-generator/stat-block-refs-on-enemies-line"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/stat-block-refs-on-enemies-line"
    assert "Bandit Captain" in f.actual
    assert "bare" in f.actual.lower()
    assert "Enemies" in f.output_location


# Spotlight texture from the palette.

def test_good_fixture_in_palette():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/spotlight-texture-in-palette"]) == []


def test_off_palette_texture_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_texture.md"), "combat-generator", ["combat-generator/spotlight-texture-in-palette"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/spotlight-texture-in-palette"
    assert "ambush" in f.actual
    assert "Spotlight" in f.output_location


# An aimed/puzzle spotlight names a target and a staging clause.

def test_good_fixture_has_target_and_staging():
    assert run_checks(_load(GOOD), "combat-generator", ["combat-generator/targeted-spotlight-names-target-and-staging"]) == []


def test_missing_staging_is_one_finding():
    findings = run_checks(_load("combat_meta_bad_nostaging.md"), "combat-generator", ["combat-generator/targeted-spotlight-names-target-and-staging"])
    assert len(findings) == 1
    f = findings[0]
    assert f.check_id == "combat-generator/targeted-spotlight-names-target-and-staging"
    assert "staging" in f.actual.lower()
    assert "Spotlight" in f.output_location


def test_untargeted_texture_imposes_no_target_requirement():
    # A plain/steamroll/curveball fight need not name a target — the check stays
    # silent.
    plain = _load(GOOD).replace(
        "aimed at Vex — the captain shoves an ally off the gangway to bait Vex's Sentinel reach",
        "steamroll — the guards wade in and the party rolls over them",
    )
    assert run_checks(plain, "combat-generator", ["combat-generator/targeted-spotlight-names-target-and-staging"]) == []


# --------------------------------------------------------------------------- #
# The signature extension: run_checks grows an optional `context` arg,
# backward-compatibly. Combat's 3-arg calls above must keep working unchanged;
# these pin the new 4th argument and how a check declares it needs context.
# --------------------------------------------------------------------------- #

def test_run_checks_still_accepts_three_args():
    # Every  call is 3-arg; the new signature must not break them.
    assert run_checks(_load(GOOD), "combat-generator", COMBAT_SUBSET) == []


def test_context_free_check_ignores_context():
    # A context-free check runs identically whether or not context is handed in.
    with_ctx = run_checks(_load(GOOD), "combat-generator", ["combat-generator/encounter-meta-required-lines"], context={"roster": []})
    without = run_checks(_load(GOOD), "combat-generator", ["combat-generator/encounter-meta-required-lines"])
    assert with_ctx == without == []


def test_context_taking_check_receives_context():
    # A check registered takes_context=True is handed the context dict; register a
    # throwaway that echoes a context value into a finding to prove it flows.
    @register_check("test-skill/test-context", "test-skill", takes_context=True)
    def _echo(artifact, context):
        return [Finding("test-skill/test-context", "ctx", str((context or {}).get("k")), "loc")]

    findings = run_checks("x", "test-skill", ["test-skill/test-context"], context={"k": "v"})
    assert findings[0].actual == "v"
