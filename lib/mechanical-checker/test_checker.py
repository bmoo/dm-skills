"""Fixture-driven units for the mechanical checker.

Mirrors the build-session/scripts pytest prior art: flat imports, pytest run from
within the scripts dir, plain ``def test_...()`` functions, fixtures in a
``fixtures/`` dir. Every test exercises external behavior — a labeled artifact in,
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
    assert run_checks("anything at all", "combat-generator", []) == []


def test_unknown_check_id_raises():
    with pytest.raises(ValueError, match="unknown check id"):
        run_checks("x", "combat-generator", ["combat-generator/no-such-check"])


def test_check_from_wrong_skill_raises():
    # The required-lines check is owned by combat-generator; a session build
    # may not request it.
    with pytest.raises(ValueError, match="owned by"):
        run_checks("x", "build-session", ["combat-generator/encounter-meta-required-lines"])


def test_findings_returned_in_requested_order():
    # Register two throwaway checks that always fire, assert order follows `checks`.
    @register_check("combat-generator/test-order-first", "combat-generator")
    def _a(artifact):
        return [Finding("combat-generator/test-order-first", "e", "a", "loc")]

    @register_check("combat-generator/test-order-second", "combat-generator")
    def _b(artifact):
        return [Finding("combat-generator/test-order-second", "e", "a", "loc")]

    ids = [f.check_id for f in run_checks(
        "x", "combat-generator",
        ["combat-generator/test-order-second", "combat-generator/test-order-first"])]
    assert ids == ["combat-generator/test-order-second", "combat-generator/test-order-first"]


def test_register_check_rejects_duplicate_check_id():
    # Two checks under one id is the silent-collision failure class the registry
    # exists to kill: the second registration raises at import time.
    @register_check("combat-generator/test-duplicate-id", "combat-generator")
    def _first(artifact):
        return []

    with pytest.raises(ValueError, match="already registered"):
        @register_check("combat-generator/test-duplicate-id", "combat-generator")
        def _second(artifact):
            return []


def test_register_check_rejects_qualifier_skill_mismatch():
    # The slug's qualifier IS the producing skill; a check filed under another
    # skill's qualifier is an import-time error, not a latent mis-routing.
    with pytest.raises(ValueError, match="qualified by 'build-session'"):
        @register_check("combat-generator/test-misfiled", "build-session")
        def _misfiled(artifact):
            return []


def test_register_check_rejects_an_unqualified_check_id():
    # An id carrying no `<skill>/` qualifier at all fails the same guard.
    with pytest.raises(ValueError, match="must be a '<producing skill>/<stem>' slug"):
        @register_check("test-unqualified", "combat-generator")
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
    @register_check("combat-generator/test-context", "combat-generator", takes_context=True)
    def _echo(artifact, context):
        return [Finding("combat-generator/test-context", "ctx", str((context or {}).get("k")), "loc")]

    findings = run_checks("x", "combat-generator", ["combat-generator/test-context"], context={"k": "v"})
    assert findings[0].actual == "v"


# --------------------------------------------------------------------------- #
# The dungeon subset. The good fixture is a full dungeon package
# that breaks no site-owned promise; each broken fixture isolates one defect.
# THE INHERITANCE SPLIT: dungeon does NOT register or run combat's checks — those
# arrive
# self-checked from combat-generator. These are the site-owned facets only.
# --------------------------------------------------------------------------- #

DUNGEON_GOOD = "dungeon_good.md"
DUNGEON_SUBSET = ["dungeon-generator/two-entrances", "dungeon-generator/at-least-one-loop", "dungeon-generator/no-secret-gated-spine", "dungeon-generator/objective-two-routes", "dungeon-generator/guarded-approach-holds", "dungeon-generator/edge-types-in-vocabulary", "dungeon-generator/type-column-token-strictness", "dungeon-generator/slate-picks-in-header", "dungeon-generator/one-signature-technique", "dungeon-generator/one-dungeon-mechanic", "dungeon-generator/mechanic-four-part-box", "dungeon-generator/default-scale", "dungeon-generator/fight-mix", "dungeon-generator/every-flagged-pc-staged", "dungeon-generator/aimed-slots-balanced"]
ROSTER = [
    {"pc": "Vex", "flagged": ["Sentinel reach"]},
    {"pc": "Bram", "flagged": ["Grapple"]},
    {"pc": "Sera", "flagged": ["Counterspell"]},
]
DUNGEON_CTX = {"roster": ROSTER, "scale_overridden": False}


def test_good_dungeon_passes_the_whole_site_owned_subset():
    # The clean site breaks no site-owned promise — the DoD's happy path.
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", DUNGEON_SUBSET, context=DUNGEON_CTX) == []


def test_dungeon_does_not_own_combat_checks():
    # The inheritance split at the registry: combat's checks are combat's, never
    # dungeon's.
    # Requesting one under dungeon-generator raises, exactly as a mis-scoped id.
    with pytest.raises(ValueError, match="owned by"):
        run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["combat-generator/encounter-meta-required-lines"], context=DUNGEON_CTX)


# ≥ 2 entrances.

def test_good_has_two_entrances():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/two-entrances"]) == []


def test_one_entrance_is_one_finding():
    findings = run_checks(_load("dungeon_one_entrance.md"), "dungeon-generator", ["dungeon-generator/two-entrances"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/two-entrances"
    assert "1 entrance" in findings[0].actual


def test_owns_edge_list_presence():
    # A missing/mis-formatted edge table must be a LOUD finding, not a silent pass
    # that lets the other graph/grammar checks return [] on unparseable output.
    # This check owns presence.
    findings = run_checks("# A dungeon with prose but no edge table\n", "dungeon-generator", ["dungeon-generator/two-entrances"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/two-entrances"
    assert "no parseable" in findings[0].actual


# ≥ 1 interior loop.

def test_good_has_a_loop():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/at-least-one-loop"]) == []


def test_tree_topology_is_one_finding():
    findings = run_checks(_load("dungeon_no_loop.md"), "dungeon-generator", ["dungeon-generator/at-least-one-loop"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/at-least-one-loop"
    assert "loop" in findings[0].actual.lower()


# No secret-gated spine.

def test_good_survives_secret_removal():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/no-secret-gated-spine"]) == []


def test_secret_gated_spine_is_one_finding():
    findings = run_checks(_load("dungeon_secret_gated_spine.md"), "dungeon-generator", ["dungeon-generator/no-secret-gated-spine"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/no-secret-gated-spine"
    assert "unreachable" in findings[0].actual


# Objective reachable by ≥ 2 edge-disjoint routes.

def test_good_has_two_routes():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/objective-two-routes"]) == []


def test_shared_bottleneck_is_one_finding():
    # Two approaches that funnel through one shared edge to the vault are one
    # route with a fork, not two — the discriminating case.
    findings = run_checks(_load("dungeon_shared_bottleneck.md"), "dungeon-generator", ["dungeon-generator/objective-two-routes"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/objective-two-routes"
    assert "1 independent route" in findings[0].actual


# A claimed guarded approach is not routed around.
#
# The three fixtures are ONE site with minimal diffs, deliberately: `bypass` and
# `unclaimed` carry byte-identical edge tables, so the silence on `unclaimed` can
# only be the missing claim and never the topology; `holds` differs from `bypass`
# in one endpoint of one edge.

GUARDED = "dungeon-generator/guarded-approach-holds"
DUNGEON_BYPASS = "dungeon_guarded_bypass.md"


def test_good_dungeon_claims_no_guarded_approach():
    # The flagship site names no guarded approach, so the check has nothing to
    # grade — it is in the DoD subset and stays silent there.
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", [GUARDED]) == []


def test_route_past_the_guards_is_one_finding():
    # The defect four of five ablation arms shipped: the page states a security
    # posture and its own edge table lists a route walking straight past it. Here
    # the skylight drops into the café corridor and the curator's private door
    # opens on the wing — three posts claimed, none of them met.
    findings = run_checks(_load(DUNGEON_BYPASS), "dungeon-generator", [GUARDED])
    assert len(findings) == 1
    assert findings[0].check_id == GUARDED
    assert "M8 → M9 → M7" in findings[0].actual


def test_guard_on_the_objective_room_is_not_interposition():
    # The claim names the objective room itself (a post on the wing's own doors,
    # as the arms wrote it). Removing the objective along with the posts would
    # make it unreachable from everywhere and pass the page vacuously, so the
    # objective is never removed — and the attic route still fires.
    assert "M7" in _load(DUNGEON_BYPASS).split("Guarded approach:")[1].splitlines()[0]
    assert len(run_checks(_load(DUNGEON_BYPASS), "dungeon-generator", [GUARDED])) == 1


def test_guarded_approach_that_holds_passes():
    # Same site, same claim; the private door now opens into the antechamber
    # instead of the wing, so every route meets a post.
    assert run_checks(_load("dungeon_guarded_holds.md"), "dungeon-generator", [GUARDED]) == []


def test_claim_reads_parenthesised_room_ids():
    # The notation every ablation arm actually wrote its posts in: "two on the
    # front desk (M1)". A tokenizer demanding bare `·`-separated IDs would find
    # no claim here and sit dark on the exact prose the defect arrived in.
    art = _load(DUNGEON_BYPASS).replace(
        "**Guarded approach:** M1 · M5 · M6 · M7",
        "**Guarded approach:** two on the desk (M1), four on the landing (M5), "
        "two in the antechamber (M6), two on the wing's own doors (M7)",
    )
    findings = run_checks(art, "dungeon-generator", [GUARDED])
    assert len(findings) == 1
    assert "M8 → M9 → M7" in findings[0].actual


def test_no_claim_no_finding_on_the_same_bypassing_graph():
    # The bypass fixture's edge table verbatim, with the claim removed. The site
    # still holds guard posts and still has an unguarded way in — which is legal
    # design until the page says otherwise, so silence is the right verdict. The
    # claim is read from the header, never inferred from where the guards stand.
    assert run_checks(_load("dungeon_guarded_unclaimed.md"), "dungeon-generator", [GUARDED]) == []


# Edge types from the closed vocabulary.

def test_good_all_in_vocabulary():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/edge-types-in-vocabulary"]) == []


def test_off_vocabulary_token_is_one_finding():
    findings = run_checks(_load("dungeon_bad_token.md"), "dungeon-generator", ["dungeon-generator/edge-types-in-vocabulary"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/edge-types-in-vocabulary"
    assert "doorr" in findings[0].actual


def test_ignores_prose_before_dash():
    # A prose fragment before the dash is the token-strictness defect, not a bad
    # enum value; the vocabulary check grades only the well-formed tokens, so it
    # stays silent on that fixture.
    assert run_checks(_load("dungeon_prose_before_dash.md"), "dungeon-generator", ["dungeon-generator/edge-types-in-vocabulary"]) == []


# Token strictness before the first em-dash.

def test_good_is_token_strict():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/type-column-token-strictness"]) == []


def test_prose_before_dash_is_one_finding():
    findings = run_checks(_load("dungeon_prose_before_dash.md"), "dungeon-generator", ["dungeon-generator/type-column-token-strictness"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/type-column-token-strictness"
    assert "prose" in findings[0].actual.lower()


def test_passes_a_bad_enum_token():
    # A well-formed but off-vocabulary token is the vocabulary defect; its
    # structure is fine, so the token-strictness check stays silent — the two
    # checks own disjoint failures.
    assert run_checks(_load("dungeon_bad_token.md"), "dungeon-generator", ["dungeon-generator/type-column-token-strictness"]) == []


# Exactly one signature technique.

def test_good_names_one_technique():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/one-signature-technique"]) == []


def test_two_techniques_is_one_finding():
    findings = run_checks(_load("dungeon_two_techniques.md"), "dungeon-generator", ["dungeon-generator/one-signature-technique"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/one-signature-technique"
    assert "2" in findings[0].actual


def test_fiction_prose_after_dash_is_not_a_second_technique():
    # xandering wants the technique grounded in the anchor's fiction, so the line
    # usually carries a description after the em-dash. Only the pre-dash clause
    # names the technique; prose mentioning another technique must not miscount.
    line = "**Signature technique:** Loops — the stairwells nest two sub-levels\n"
    assert run_checks(line, "dungeon-generator", ["dungeon-generator/one-signature-technique"]) == []


# Exactly one dungeon-wide mechanic (or a vanilla waiver).

def test_good_has_one_mechanic():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/one-dungeon-mechanic"]) == []


def test_two_mechanics_is_one_finding():
    findings = run_checks(_load("dungeon_two_mechanics.md"), "dungeon-generator", ["dungeon-generator/one-dungeon-mechanic"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/one-dungeon-mechanic"
    assert "2 mechanic" in findings[0].actual


def test_vanilla_waiver_is_allowed():
    # An explicit vanilla waiver with no mechanic box is fine — never a finding.
    vanilla = "**Dungeon mechanic:** vanilla — a plain site, no gimmick\n\n## Keyed areas\n- N1\n"
    assert run_checks(vanilla, "dungeon-generator", ["dungeon-generator/one-dungeon-mechanic"]) == []


# Both slate picks named in the header — the presence half, and the no-DM slate.

SLATE_PICKS = "dungeon-generator/slate-picks-in-header"
SLATE_NO_DM = "dungeon_slate_no_dm.md"
SLATE_DROPPED = "dungeon_slate_dropped_field.md"


def test_good_names_both_slate_picks():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", [SLATE_PICKS]) == []


def test_no_dm_package_passes_the_whole_site_owned_subset():
    # The defect four of four ablation arms hit: the slate stop had no legal path
    # with nobody there to answer it. With the stop's self-serve fallback the run
    # lands a package, and that package is graded exactly as an attended one —
    # same two header fields, same checks, no page-level trace of which mode
    # built it.
    assert run_checks(_load(SLATE_NO_DM), "dungeon-generator", DUNGEON_SUBSET, context=DUNGEON_CTX) == []


def test_dropped_signature_field_is_one_finding():
    # The silent escape an unanswered slate had before the fallback existed: the
    # pick never settles, so the field is simply left off.
    findings = run_checks(_load(SLATE_DROPPED), "dungeon-generator", [SLATE_PICKS])
    assert len(findings) == 1
    assert findings[0].check_id == SLATE_PICKS
    assert "Signature technique" in findings[0].actual


def test_one_technique_check_still_stays_silent_on_a_dropped_field():
    # The count check's strength is untouched by the presence row: it owns how
    # many techniques the field names, never whether the field is there. The two
    # own disjoint failures, as the vocabulary and token-strictness pair do.
    assert run_checks(_load(SLATE_DROPPED), "dungeon-generator", ["dungeon-generator/one-signature-technique"]) == []


def test_unresolved_slate_dumped_into_the_field_still_fires():
    # The other shape an unanswered slate takes: the candidate list goes into the
    # header instead of a pick. Three techniques named is three, whoever was —
    # or wasn't — there to choose between them.
    art = _load(SLATE_NO_DM).replace(
        "**Signature technique:** Redundant level links",
        "**Signature technique:** Redundant level links / Route loops / Pocket levels",
    )
    findings = run_checks(art, "dungeon-generator", ["dungeon-generator/one-signature-technique"])
    assert len(findings) == 1
    assert "3" in findings[0].actual


# The mechanic ships as a four-part box.

def test_good_box_has_four_parts():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/mechanic-four-part-box"]) == []


def test_box_missing_exploit_is_one_finding():
    findings = run_checks(_load("dungeon_box_missing_exploit.md"), "dungeon-generator", ["dungeon-generator/mechanic-four-part-box"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/mechanic-four-part-box"
    assert "Exploit" in findings[0].actual


# Default scale, only when the DM didn't override.

def test_good_is_default_scale():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/default-scale"], context=DUNGEON_CTX) == []


def test_too_many_combats_is_a_finding():
    findings = run_checks(_load("dungeon_too_many_combats.md"), "dungeon-generator", ["dungeon-generator/default-scale"], context=DUNGEON_CTX)
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/default-scale"
    assert "5 combats" in findings[0].actual


def test_override_suppresses_the_check():
    # When the DM chose a non-default scale, the check does not apply — even
    # off-range.
    findings = run_checks(
        _load("dungeon_too_many_combats.md"),
        "dungeon-generator",
        ["dungeon-generator/default-scale"],
        context={"scale_overridden": True},
    )
    assert findings == []


def test_no_context_assumes_default_and_runs():
    # With no context the check assumes an un-overridden run and grades it.
    findings = run_checks(_load("dungeon_too_many_combats.md"), "dungeon-generator", ["dungeon-generator/default-scale"])
    assert len(findings) == 1 and findings[0].check_id == "dungeon-generator/default-scale"


# Fight mix: one High set piece, the rest Low/Moderate.

def test_good_has_one_set_piece():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/fight-mix"]) == []


def test_two_high_fights_is_one_finding():
    findings = run_checks(_load("dungeon_two_high.md"), "dungeon-generator", ["dungeon-generator/fight-mix"])
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/fight-mix"
    assert "2 High" in findings[0].actual


# Every flagged PC staged somewhere (set cover vs roster).

def test_good_covers_the_roster():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/every-flagged-pc-staged"], context=DUNGEON_CTX) == []


def test_unstaged_pc_is_one_finding():
    findings = run_checks(_load("dungeon_pc_unstaged.md"), "dungeon-generator", ["dungeon-generator/every-flagged-pc-staged"], context=DUNGEON_CTX)
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/every-flagged-pc-staged"
    assert "Sera" in findings[0].actual


def test_staging_without_roster_raises():
    # A roster-dependent check handed no roster refuses to fake a verdict.
    with pytest.raises(ValueError, match="roster"):
        run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/every-flagged-pc-staged"])


# Aimed slots balanced across the flagging roster.

def test_good_is_balanced():
    assert run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/aimed-slots-balanced"], context=DUNGEON_CTX) == []


def test_unbalanced_slots_is_one_finding():
    findings = run_checks(_load("dungeon_unbalanced.md"), "dungeon-generator", ["dungeon-generator/aimed-slots-balanced"], context=DUNGEON_CTX)
    assert len(findings) == 1
    assert findings[0].check_id == "dungeon-generator/aimed-slots-balanced"
    assert "Sera:0" in findings[0].actual


def test_aimed_slot_balance_without_roster_raises():
    with pytest.raises(ValueError, match="roster"):
        run_checks(_load(DUNGEON_GOOD), "dungeon-generator", ["dungeon-generator/aimed-slots-balanced"])


# --------------------------------------------------------------------------- #
# The build-session subset. The good fixture is a full
# session page that breaks no page-owned promise; each broken fixture isolates one
# defect and is run only against its own check id (so it can be minimal).
#
# THE TWO-DELEGATE INHERITANCE SPLIT: build-session registers and runs no
# combat-generator or dungeon-generator row on the page. Fights arrive
# self-checked from combat-generator and
# keyed sites from dungeon-generator; these are the page/session-owned facets only.
# --------------------------------------------------------------------------- #

SESSION_GOOD = "session_good.md"
SESSION_SUBSET = [
    "build-session/skeleton-sections-in-order", "build-session/key-npcs-header", "build-session/role-word-count", "build-session/stat-block-resolvable", "build-session/location-uses-page-keys", "build-session/contents-index", "build-session/no-empty-scaffolding", "build-session/clue-payload-shape", "build-session/slate-indexes-only", "build-session/conclusion-leads", "build-session/foreshadow-not-a-lead",
    "build-session/fights-are-encounter-meta", "build-session/art-style-declared", "build-session/art-pieces", "build-session/float-before-prose", "build-session/art-style-differs-from-neighbors", "build-session/links-resolve", "build-session/hotspot-map", "build-session/keyed-site-carries-map", "build-session/edges-not-dm-visible", "build-session/spotlight-plan-not-filed", "build-session/spotlight-annotations-name-pc", "build-session/spotlight-shapes-separate",
]
SESSION_ROSTER = [
    {"pc": "Vex", "flagged": ["Sentinel reach"]},
    {"pc": "Bram", "flagged": ["Grapple"]},
    {"pc": "Sera", "flagged": ["Counterspell"]},
]
SESSION_CTX = {"roster": SESSION_ROSTER, "neighbor_art_styles": ["ink-and-wash", "photoreal noir"]}


def test_good_session_passes_the_whole_page_owned_subset():
    # The clean page breaks no page-owned mechanical promise — the DoD's happy path.
    assert run_checks(_load(SESSION_GOOD), "build-session", SESSION_SUBSET, context=SESSION_CTX) == []


# The sweep that holds every session fixture — not just SESSION_GOOD — against the
# two keyed-page rows lives maintainer-side, in `lib/test_session_fixture_sweep.py`.
# It walks this repo's fixture corpus, which a consumer does not have, and the walk
# it needs belongs to a module that deliberately does not ship.


def test_build_session_does_not_own_delegate_checks():
    # The two-delegate inheritance split at the registry: a `combat-generator/` row
    # is combat's and a `dungeon-generator/` row is dungeon's, never build-session's.
    # Requesting one raises, exactly as a mis-scoped id would — build-session cannot
    # re-verify what its delegates self-checked.
    with pytest.raises(ValueError, match="owned by"):
        run_checks(_load(SESSION_GOOD), "build-session", ["combat-generator/encounter-meta-required-lines"], context=SESSION_CTX)
    with pytest.raises(ValueError, match="owned by"):
        run_checks(_load(SESSION_GOOD), "build-session", ["dungeon-generator/two-entrances"], context=SESSION_CTX)


# The nine skeleton sections, present and in order.

def test_good_is_in_order():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/skeleton-sections-in-order"]) == []


def test_out_of_order_is_one_finding():
    findings = run_checks(_load("session_out_of_order.md"), "build-session", ["build-session/skeleton-sections-in-order"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/skeleton-sections-in-order"
    assert "out of order" in findings[0].actual


def test_owns_section_presence():
    # A page missing a skeleton section is the skeleton check's loud finding — and
    # the content checks (the Role word count here) stay silent on the absent
    # table, so the miss is singly fixable.
    prose = "# A page with no sections\n\nJust prose."
    skeleton = run_checks(prose, "build-session", ["build-session/skeleton-sections-in-order"])
    assert (len(skeleton) == 1
            and skeleton[0].check_id == "build-session/skeleton-sections-in-order"
            and "missing" in skeleton[0].actual)
    assert run_checks(prose, "build-session", ["build-session/role-word-count"]) == []


# Key NPCs header — enforced against the format file's 5 columns
# (unenforceable/npc-roster-column-contradiction).

def test_good_header_matches_five_columns():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/key-npcs-header"]) == []


def test_four_column_header_is_one_finding():
    # The four-column header (`build-session/SKILL.md` — "the roster table")
    # is the contradiction this check does NOT
    # enforce (unenforceable/npc-roster-column-contradiction); against the
    # format-file authority it reads as a defect.
    findings = run_checks(_load("session_four_col_header.md"), "build-session", ["build-session/key-npcs-header"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/key-npcs-header"
    assert "Personality" in findings[0].expected


# Role is 3–8 words.

def test_good_roles_in_range():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/role-word-count"]) == []


def test_long_role_is_one_finding():
    findings = run_checks(_load("session_long_role.md"), "build-session", ["build-session/role-word-count"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/role-word-count"
    assert "13 words" in findings[0].actual


# Stat Block resolvable; N/A (non-combat) is a defect.

def test_good_all_resolvable():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/stat-block-resolvable"]) == []


def test_na_non_combat_is_one_finding():
    findings = run_checks(_load("session_na_statblock.md"), "build-session", ["build-session/stat-block-resolvable"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/stat-block-resolvable"
    assert "N/A (non-combat)" in findings[0].actual


# Location uses page keys, not prose (proxy).

def test_good_uses_keys():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/location-uses-page-keys"]) == []


def test_prose_location_is_one_finding():
    findings = run_checks(_load("session_prose_location.md"), "build-session", ["build-session/location-uses-page-keys"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/location-uses-page-keys"
    assert "north of the well" in findings[0].actual


# Contents index: one line, 5–8 links.

def test_good_index_in_range():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/contents-index"]) == []


def test_too_few_links_is_one_finding():
    findings = run_checks(_load("session_too_few_links.md"), "build-session", ["build-session/contents-index"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/contents-index"
    assert "3 link" in findings[0].actual


# No empty Recap/Notes scaffolding.

def test_good_has_no_scaffolding():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/no-empty-scaffolding"]) == []


def test_empty_recap_is_one_finding():
    findings = run_checks(_load("session_empty_recap.md"), "build-session", ["build-session/no-empty-scaffolding"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/no-empty-scaffolding"
    assert "Recap" in findings[0].actual


# Clue payload carries Show / They learn / Points at.

def test_good_payloads_complete():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/clue-payload-shape"]) == []


def test_missing_part_is_one_finding():
    findings = run_checks(_load("session_missing_part.md"), "build-session", ["build-session/clue-payload-shape"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/clue-payload-shape"
    assert "Points at" in findings[0].actual


# The slate only indexes clues (every line links to a payload).

def test_good_slate_all_linked():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/slate-indexes-only"]) == []


def test_slate_line_without_link_is_one_finding():
    findings = run_checks(_load("session_slate_no_link.md"), "build-session", ["build-session/slate-indexes-only"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/slate-indexes-only"
    assert "no link" in findings[0].actual


# Conclusion carries ≥ 2 live leads.

def test_good_has_two_leads():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/conclusion-leads"]) == []


def test_one_lead_is_one_finding():
    findings = run_checks(_load("session_one_lead.md"), "build-session", ["build-session/conclusion-leads"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/conclusion-leads"
    assert "1 lead" in findings[0].actual


# Foreshadow never also tagged Lead.

def test_good_keeps_them_separate():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/foreshadow-not-a-lead"]) == []


def test_lead_and_foreshadow_on_one_line_is_a_finding():
    findings = run_checks(_load("session_lead_and_foreshadow.md"), "build-session", ["build-session/foreshadow-not-a-lead"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/foreshadow-not-a-lead"
    assert "both Lead and foreshadow" in findings[0].actual


# Every fight FILED as an encounter-meta callout (page-structural).

def test_good_fights_are_callouts():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/fights-are-encounter-meta"]) == []


def test_loose_fight_is_one_finding():
    findings = run_checks(_load("session_loose_fight.md"), "build-session", ["build-session/fights-are-encounter-meta"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/fights-are-encounter-meta"
    assert "outside any encounter-meta callout" in findings[0].actual


def test_is_structural_not_a_regrade():
    # A fight with BROKEN XP arithmetic but a well-formed callout is NOT this
    # check's concern — that arithmetic arrived self-checked from
    # combat-generator. This check owns only the filing shape, so it stays silent
    # here (inheritance split).
    bad_math = (
        "> [!encounter-meta]\n"
        "> **Party:** 3 PCs, Level 5\n"
        "> **Enemies:** {monster:Bandit} × 4 (25 XP) → **999 XP**\n"
        "> **Objective:** breach the gate\n"
    )
    assert run_checks(bad_math, "build-session", ["build-session/fights-are-encounter-meta"]) == []


# Art_style declared in frontmatter.

def test_good_declares_art_style():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/art-style-declared"]) == []


def test_missing_art_style_is_one_finding():
    findings = run_checks(_load("session_no_art_style.md"), "build-session", ["build-session/art-style-declared"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/art-style-declared"


# Four narrative art pieces (node diagram excluded).

def test_good_has_four_pieces_and_a_splash():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/art-pieces"]) == []


def test_three_pieces_is_a_count_finding():
    findings = run_checks(_load("session_three_pieces.md"), "build-session", ["build-session/art-pieces"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/art-pieces"
    assert "3 narrative" in findings[0].actual


# A float sits before prose, never adjacent to another callout.

def test_good_float_wraps_prose():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/float-before-prose"]) == []


def test_float_then_callout_is_one_finding():
    findings = run_checks(_load("session_float_then_callout.md"), "build-session", ["build-session/float-before-prose"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/float-before-prose"
    assert "another callout" in findings[0].actual


# Art_style differs from neighbors (context inequality).

def test_good_differs_from_neighbors():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/art-style-differs-from-neighbors"], context=SESSION_CTX) == []


def test_style_clash_is_one_finding():
    findings = run_checks(
        _load("session_style_clash.md"), "build-session", ["build-session/art-style-differs-from-neighbors"],
        context={"neighbor_art_styles": ["ink-and-wash", "photoreal noir"]},
    )
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/art-style-differs-from-neighbors"
    assert "ink-and-wash" in findings[0].actual


def test_no_neighbors_returns_empty_not_raise():
    # DIVERGENCE from the annotation check: neighbors legitimately may not exist
    # (first session), so
    # absent neighbor data is a vacuous pass, not a raise.
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/art-style-differs-from-neighbors"]) == []
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/art-style-differs-from-neighbors"], context={"roster": []}) == []


# Every on-page anchor link resolves (pure static).

def test_good_all_anchors_resolve():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/links-resolve"]) == []


def test_dangling_anchor_is_one_finding():
    findings = run_checks(_load("session_dangling_anchor.md"), "build-session", ["build-session/links-resolve"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/links-resolve"
    assert "#does-not-exist" in findings[0].actual


def test_spaced_dash_and_ampersand_headings_slug_as_the_renderers_do():
    # , the false-flag direction: the good page's keyed headings carry the
    # library's own prescribed ` — ` and its `Secrets & Clues`, so its anchors
    # double the hyphen exactly as GitHub and pandoc emit them. Collapsing the
    # whitespace run instead flagged all five of those correct links.
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/links-resolve"]) == []


def test_ascii_hyphen_keyed_heading_slugs_with_three_hyphens():
    # `_KEYED_INDEX_RE` accepts `[—–-]`, so an ASCII-hyphen key is house style too
    # — and it is the one keyed variant no fixture page carries. GitHub keeps the
    # hyphen (it is not punctuation) *and* both spaces: three in a row.
    page = "# P\n\n[Undercroft](#t2---the-undercroft)\n\n## T2 - The Undercroft\n"
    assert run_checks(page, "build-session", ["build-session/links-resolve"]) == []


def test_collapsed_run_anchor_is_a_dangling_link():
    # , the direction that mattered: a page whose anchors collapse ` — ` /
    # ` & ` to a single hyphen 404s on GitHub and in the site build. The old
    # slug agreed with the page and certified it; the finding is the fix.
    findings = run_checks(_load("session_collapsed_anchor.md"), "build-session", ["build-session/links-resolve"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/links-resolve"
    for a in ("#secrets-clues", "#t1-the-gate", "#n15-the-cold-cache"):
        assert a in findings[0].actual


# Where a hotspot map exists, one hotspot per key (conditional).

def test_good_plain_map_is_not_a_hotspot_treatment():
    # The good page's `> [!map]` carries no hotspot links → not a hotspot treatment,
    # so the check stays silent (the conditional).
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/hotspot-map"]) == []


def test_hotspot_count_mismatch_is_one_finding():
    findings = run_checks(_load("session_hotspot_mismatch.md"), "build-session", ["build-session/hotspot-map"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/hotspot-map"
    assert "2 hotspot link" in findings[0].actual and "3 keyed" in findings[0].actual


# A keyed site carries its map — a separate promise from the hotspot count above:
# that one fires where a treatment exists, this one where the map does not.

EDGES_PAGE = "session_edges_concealed_good.md"


def _carries_map(page: str) -> list:
    return run_checks(page, "build-session", ["build-session/keyed-site-carries-map"])


def test_a_keyed_page_with_its_map_embedded_passes():
    assert _carries_map(_load(EDGES_PAGE)) == []


def test_a_keyed_page_with_the_map_embed_removed_is_a_finding():
    page = _load(EDGES_PAGE).replace(
        "> [!map]\n> ![The Old Town Catacombs](old-town-night-map.png)\n"
        "> [N1](#n1) · [N2](#n2) · [N3](#n3)\n\n", "")
    assert "[!map]" not in page
    findings = _carries_map(page)
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/keyed-site-carries-map"
    # The finding names what it found keyed, so the fix needs no re-reading of the
    # rule: three areas, no map.
    assert "N1, N2, N3" in findings[0].actual


def test_a_page_with_no_keyed_areas_passes_silently():
    # A social session — nothing to navigate, so nothing to require.
    page = "# Session 3 — The Guildhall Vote\n\n## Beginning the Adventure\n\nTalk.\n"
    assert _carries_map(page) == []


def test_the_map_requirement_does_not_reach_into_the_hotspot_count():
    # The two rows are deliberately separate. A keyed page whose map carries
    # the WRONG number of badges satisfies this row — the map exists — and is the
    # hotspot row's to fail. Merging them would make one failure two.
    page = _load("session_hotspot_mismatch.md")
    assert _carries_map(page) == []
    assert len(run_checks(page, "build-session", ["build-session/hotspot-map"])) == 1


# The edge table is machine state: concealed, and its codes out of every line
# the DM reads (negative).


def _edges(page: str) -> list:
    return run_checks(page, "build-session", ["build-session/edges-not-dm-visible"])


def test_a_concealed_table_and_code_free_prose_pass():
    # The shape the format asks for: the table filed inside the comment so the map
    # can be re-rendered, and every connection the DM needs said in the room's own
    # prose — the locked gate's DC 15, the secret arch's DC 12, the well shaft.
    assert _edges(_load(EDGES_PAGE)) == []


def test_keyed_area_ids_are_not_edges():
    # `N1`/`N2`/`N3` are all over the good page's prose and index and stay there —
    # they resolve visually against the hotspot map. The exemption is real only if
    # nothing above fired on them, so pin it against a page that is nothing but.
    page = "# P\n\nThe stair from N1 reaches N2, and N12 lies past the arch.\n"
    assert _edges(page) == []


def test_the_shared_known_good_brief_page_stays_clean():
    # Its table was concealed by the prefactor; nothing outside the comment names
    # an edge.
    assert _edges(_load(BRIEF_PAGE)) == []


def test_a_page_with_no_keyed_site_passes_silently():
    assert _edges(_load(SESSION_GOOD)) == []


def test_a_visible_edges_heading_is_a_finding():
    page = _load(EDGES_PAGE).replace("<!--\n## Edges (render-ready)", "## Edges (render-ready)") \
                            .replace("| E4 | N1 — N3 | vertical · shaft · down — the dry well shaft |\n-->",
                                     "| E4 | N1 — N3 | vertical · shaft · down — the dry well shaft |")
    findings = _edges(page)
    assert findings, "an unconcealed edge table was not caught"
    assert any("Edges (render-ready)" in f.actual for f in findings)
    assert all(f.check_id == "build-session/edges-not-dm-visible" for f in findings)


def test_a_surviving_code_in_an_exit_line_is_a_finding():
    page = _load(EDGES_PAGE).replace(
        "## N1\n", "## N1\n\n**Exits.** E1 to the yard, E2 to the ossuary.\n")
    findings = _edges(page)
    assert [f.check_id for f in findings] == ["build-session/edges-not-dm-visible"] * 2
    assert "E1" in findings[0].actual and "E2" in findings[1].actual


def test_a_surviving_code_in_body_prose_is_a_finding():
    page = _load(EDGES_PAGE).replace(
        "The bricked arch back to the ossuary is obvious from this",
        "The bricked arch back to the ossuary (E3) is obvious from this")
    findings = _edges(page)
    assert len(findings) == 1
    assert "E3" in findings[0].actual


def test_a_surviving_code_in_a_sidebar_is_a_finding():
    page = _load(EDGES_PAGE).replace(
        "> **Spotlight (scene):** Vex — exploration; the gate's lock",
        "> **Spotlight (scene):** Vex — exploration; the lock on E2")
    findings = _edges(page)
    assert len(findings) == 1
    assert "E2" in findings[0].actual


def test_a_surviving_code_in_an_encounter_meta_terrain_block_is_a_finding():
    page = _load(EDGES_PAGE).replace(
        "> **Terrain:** the bone racks — heavy cover",
        "> **Terrain:** the bone racks and E3 — heavy cover")
    findings = _edges(page)
    assert len(findings) == 1
    assert "E3" in findings[0].actual


def test_an_unclosed_comment_opener_is_a_finding():
    # A `<!--` with no `-->` hides everything below it — the keyed areas, the
    # fights, the conclusion — and the page looks fine in the source. It is
    # reported alone: nothing under the opener can be judged visible or concealed
    # until it is closed.
    page = _load(EDGES_PAGE).replace(
        "| E4 | N1 — N3 | vertical · shaft · down — the dry well shaft |\n-->",
        "| E4 | N1 — N3 | vertical · shaft · down — the dry well shaft |")
    findings = _edges(page)
    assert len(findings) == 1
    assert "<!--" in findings[0].actual


# The spotlight plan is never filed on the page (negative).

def test_good_files_no_plan():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/spotlight-plan-not-filed"]) == []


def test_filed_plan_is_one_finding():
    findings = run_checks(_load("session_filed_plan.md"), "build-session", ["build-session/spotlight-plan-not-filed"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-plan-not-filed"
    assert "Spotlight plan" in findings[0].actual


def test_ignores_per_beat_annotations():
    # The per-beat Spotlight/Spotlight (scene) EFFECTS are allowed on the page —
    # this check flags only a filed PLAN, never the annotations (which are the
    # annotation check's concern).
    ann = "> **Spotlight:** aimed at Vex — a crate is shoved to bait Sentinel reach\n"
    assert run_checks(ann, "build-session", ["build-session/spotlight-plan-not-filed"]) == []


# The filed-plan anti-cheat paths — a plan can be filed without ever saying
# "plan".

def test_catches_a_plan_table_that_names_the_spotlight_nowhere():
    # The columns give it away: a who-column against a pillar/beat column. Neither
    # the heading nor any cell carries the word "spotlight" or "plan".
    src = _load("session_plan_table_untitled.md")
    assert "potlight" not in src and "plan" not in src.lower()
    findings = run_checks(src, "build-session", ["build-session/spotlight-plan-not-filed"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-plan-not-filed"
    assert "plan table" in findings[0].actual


def test_catches_annotations_filed_under_preparation():
    # Annotations are legal AT THE SCENE THAT STAGES THE BEAT; a nest of them under
    # Preparation is the plan re-filed as a bookmark list.
    findings = run_checks(_load("session_prep_annotation.md"), "build-session", ["build-session/spotlight-plan-not-filed"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-plan-not-filed"
    assert "under Preparation" in findings[0].actual


def test_catches_a_filed_resting_roster():
    # Resting is recorded by ABSENCE
    # (`build-session/session-page-format.md` — "**Absence is the record:**"),
    # so a filed
    # rest list is transient plan state that escaped the run.
    findings = run_checks(_load("session_resting_roster.md"), "build-session", ["build-session/spotlight-plan-not-filed"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-plan-not-filed"
    assert "Resting" in findings[0].actual


def test_catches_any_spotlight_heading_however_worded():
    # No skeleton section is headed for the spotlight, so any such heading is a plan —
    # the wording "plan"/"budget"/"allocation" is not required.
    findings = run_checks("## Tonight's Spotlight\n\nVex takes the gate.\n",
                          "build-session", ["build-session/spotlight-plan-not-filed"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-plan-not-filed"


def test_leaves_the_key_npcs_table_alone():
    # The strengthened table rule must not fire on the page's legitimate tables —
    # the good fixture's Key NPCs table has a name column and no beat column.
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/spotlight-plan-not-filed"]) == []


# The spotlight-coverage pre-pass — the uncovered set. Data, never a verdict.

def test_prepass_good_page_covers_every_pc():
    cov = checker.spotlight_coverage(_load(SESSION_GOOD), SESSION_ROSTER)
    assert cov.uncovered == []
    assert sorted(cov.covered) == ["Bram", "Sera", "Vex"]


def test_prepass_reports_the_uncovered_pc():
    cov = checker.spotlight_coverage(_load("session_pc_uncovered.md"), SESSION_ROSTER)
    assert cov.uncovered == ["Sera"]


def test_prepass_counts_a_secondary_mention_as_covered():
    # The stated rule: a PC named ANYWHERE in an annotation's value is covered,
    # including as a secondary inside another PC's beat. Bram appears only that way.
    cov = checker.spotlight_coverage(_load("session_pc_uncovered.md"), SESSION_ROSTER)
    assert "Bram" in cov.covered


def test_prepass_ignores_prose_mentions():
    # Only annotation lines count. The fixture's Conclusion prose names Sera; that is
    # not a staged beat and must not read as coverage.
    src = _load("session_pc_uncovered.md")
    assert "Sera" in src
    assert checker.spotlight_coverage(src, SESSION_ROSTER).uncovered == ["Sera"]


def test_prepass_reports_beat_share_for_the_judge():
    # beats_per_pc is the judge's "one PC absorbed a disproportionate share" signal.
    cov = checker.spotlight_coverage(_load("session_pc_uncovered.md"), SESSION_ROSTER)
    assert cov.beats_per_pc == {"Vex": 2, "Bram": 1, "Sera": 0}


def test_prepass_never_fails_a_page():
    # An uncovered PC is LEGAL — resting is recorded by absence. The pre-pass returns
    # data and emits no Finding, so it cannot fail a page on its own; the judgement
    # tier owns the verdict.
    cov = checker.spotlight_coverage(_load("session_pc_uncovered.md"), SESSION_ROSTER)
    assert not isinstance(cov, list)
    assert "build-session/spotlight-coverage" not in checker._REGISTRY


# Every Spotlight annotation names a roster PC — except a fight field declaring the
# `plain` texture, which stages no beat (context, raises).

def test_good_every_annotation_names_a_pc():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/spotlight-annotations-name-pc"], context=SESSION_CTX) == []


def test_annotation_without_pc_is_one_finding():
    findings = run_checks(
        _load("session_no_pc.md"), "build-session", ["build-session/spotlight-annotations-name-pc"], context={"roster": SESSION_ROSTER}
    )
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-annotations-name-pc"
    assert "naming no roster PC" in findings[0].actual


def test_plain_fight_and_pocket_beat_satisfy_the_row():
    # The absorbed exception. The encounter-meta `Spotlight:` label is required on
    # EVERY fight, so a fight that stages no beat still carries one and has nothing
    # to name; declaring the `plain` texture satisfies the row. The fixture carries
    # both doctrinally-required cases — a plain fight and a pocket beat in
    # Contingencies — beside two real staged beats that do name their PCs.
    assert run_checks(
        _load("session_plain_fight.md"), "build-session",
        ["build-session/spotlight-annotations-name-pc"], context=SESSION_CTX
    ) == []


def test_aimed_fight_naming_nobody_still_fires():
    # Only the affirmative `plain` declaration excuses a fight field. An `aimed`
    # fight is the paradigm beat that should carry a named PC.
    findings = run_checks(
        _load("session_aimed_no_pc.md"), "build-session",
        ["build-session/spotlight-annotations-name-pc"], context={"roster": SESSION_ROSTER}
    )
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-annotations-name-pc"


def test_relabelling_every_beat_plain_is_not_an_escape_hatch():
    # The exception is not universal: a `Spotlight (scene):` line exists only where a
    # beat was staged, so it is never excused and relabelling it `plain` does not
    # rescue it. The fixture marks EVERY annotation plain and the row still fires on
    # the scene line. (The plain fight fields pass by design — an unbeaten page is
    # spotlight-coverage's uncovered set to rule on, not this row's.)
    findings = run_checks(
        _load("session_beats_all_plain.md"), "build-session",
        ["build-session/spotlight-annotations-name-pc"], context={"roster": SESSION_ROSTER}
    )
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-annotations-name-pc"
    assert "naming no roster PC" in findings[0].actual


def test_annotations_without_roster_raises():
    # Mirrors dungeon's staging check: a roster-dependent check handed no roster
    # refuses to fake a verdict.
    with pytest.raises(ValueError, match="roster"):
        run_checks(_load(SESSION_GOOD), "build-session", ["build-session/spotlight-annotations-name-pc"])


# No Spotlight (scene) line inside an encounter-meta block (negative).

def test_good_keeps_shapes_separate():
    assert run_checks(_load(SESSION_GOOD), "build-session", ["build-session/spotlight-shapes-separate"]) == []


def test_scene_line_in_meta_is_one_finding():
    findings = run_checks(_load("session_scene_in_meta.md"), "build-session", ["build-session/spotlight-shapes-separate"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/spotlight-shapes-separate"
    assert "Spotlight (scene)" in findings[0].actual


# --------------------------------------------------------------------------- #
# The node-deepening rows — graded over the DEEPENED-NODE artifact, a
# different artifact from the session page the build-session rows grade.
# --------------------------------------------------------------------------- #

NODE_GOOD = "node_good.md"


def test_good_node_passes_the_deepening_subset():
    assert run_checks(_load(NODE_GOOD), "build-session", ["build-session/clue-web-section-present", "build-session/clue-web-indexes-only"]) == []


# Clue-web section present with its glance line.

def test_good_has_clue_web():
    assert run_checks(_load(NODE_GOOD), "build-session", ["build-session/clue-web-section-present"]) == []


def test_missing_clue_web_is_one_finding():
    findings = run_checks(_load("node_no_clue_web.md"), "build-session", ["build-session/clue-web-section-present"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/clue-web-section-present"
    assert "no clue-web section" in findings[0].actual


def test_owns_clue_web_presence():
    # The presence check owns the section's presence, so the indexes-only check
    # stays silent when it is absent — the miss is singly fixable (add the
    # section, then it can grade it).
    art = _load("node_no_clue_web.md")
    assert len(run_checks(art, "build-session", ["build-session/clue-web-section-present"])) == 1
    assert run_checks(art, "build-session", ["build-session/clue-web-indexes-only"]) == []


# Clue content lives in the body; the clue-web section only indexes.

def test_good_web_only_indexes():
    assert run_checks(_load(NODE_GOOD), "build-session", ["build-session/clue-web-indexes-only"]) == []


def test_content_in_web_is_one_finding():
    findings = run_checks(_load("node_content_in_web.md"), "build-session", ["build-session/clue-web-indexes-only"])
    assert len(findings) == 1
    assert findings[0].check_id == "build-session/clue-web-indexes-only"
    assert "index" in findings[0].actual.lower()


# --------------------------------------------------------------------------- #
# build-session — the Spec axis: the session brief.
# --------------------------------------------------------------------------- #
#
# One brief, one page that satisfies every row, and one targeted edit per row.
# The edits are inline `.replace()`s off the single good page for the same reason
# the guarded-approach fixtures are one site with minimal diffs: a variant that
# differs in one place can only fail for that one reason.

BRIEF = "session_brief_gloamfen.md"
BRIEF_PAGE = "session_brief_page_good.md"
BRIEF_RECORD = "session_brief_canon_record.md"

SPEC_AXIS = [
    "build-session/brief-introduced-canon",
    "build-session/brief-ground-rules-stated",
    "build-session/brief-npc-commitments",
    "build-session/brief-timeline-commitments",
    "build-session/brief-revelation-paid-down",
    "build-session/brief-destination-nodes",
    "build-session/brief-exit-edge",
    "build-session/brief-map-topology",
    "build-session/brief-not-tonight",
]

_FEATURES = """**Features.** Interior doors are locked after closing — DC 12 with thieves'
tools. Secret doors are DC 12 to spot. Ceilings run 30 feet through the public
halls and low through the service ways. Twelve guards hold fixed stations, and a
raised alarm draws 1d4 more guards per round from the nearest station. Alarm
spells sit on the marked interior thresholds and a staff pass card bypasses
them; while the museum is open to the public the alarms are unarmed, which is
why the gala is a way in.

"""


def _spec_context(**over):
    ctx = {"brief": _load(BRIEF), "canon_record": _load(BRIEF_RECORD)}
    ctx.update(over)
    return ctx


def _spec_run(page, checks=None, **over):
    return run_checks(page, "build-session", checks or SPEC_AXIS, context=_spec_context(**over))


# The derivation: an enumerated field set in, the matching ids out.

def test_brief_checks_derives_one_id_per_filled_field():
    assert checker.brief_checks(_load(BRIEF)) == SPEC_AXIS


def test_a_blank_field_produces_no_row_at_all():
    # The axis's whole shape: a row exists only where the brief wrote a field, so
    # silence is never a constraint. Cutting `Exit edge` out of the brief must
    # remove its id from the derivation AND leave the check itself silent when a
    # caller runs it anyway.
    brief = _load(BRIEF)
    start = brief.index("- **Exit edge.**")
    end = brief.index("### Layout")
    without = brief[:start] + brief[end:]
    assert "build-session/brief-exit-edge" not in checker.brief_checks(without)
    assert checker.brief_checks(without) == [c for c in SPEC_AXIS if not c.endswith("exit-edge")]
    ctx = _spec_context(brief=without)
    assert run_checks(_load(BRIEF_PAGE), "build-session", SPEC_AXIS, context=ctx) == []


def test_an_emptied_field_is_blank_not_filled():
    # `- **Map topology.**` with nothing after it is a field the brief did not
    # fill, not a field it filled with nothing.
    brief = _load(BRIEF).replace(
        "- **Map topology.** The museum is a keyed interior on two floors plus a basement\n"
        "  and an attic, with four entrances connecting it to Museum Square; the Gemstone\n"
        "  Wing is the deep room and the guard stations sit between it and every entrance.",
        "- **Map topology.** <not decided>",
    )
    assert "build-session/brief-map-topology" not in checker.brief_checks(brief)


def test_an_explicit_none_is_a_filled_field():
    # "none; all derived" is the DM answering, not the DM staying silent — the row
    # runs and finds nothing named, which is different from not running.
    brief = _load(BRIEF)
    start = brief.index("- **Introduced canon.**")
    end = brief.index("- **Environmental ground rules.**")
    none_brief = brief[:start] + '- **Introduced canon.** none; all derived.\n' + brief[end:]
    assert "build-session/brief-introduced-canon" in checker.brief_checks(none_brief)
    assert run_checks(_load(BRIEF_PAGE), "build-session",
                      ["build-session/brief-introduced-canon"],
                      context=_spec_context(brief=none_brief)) == []


# A missing brief is a caller error; a blank field is silence.

def test_no_brief_raises_rather_than_faking_a_verdict():
    with pytest.raises(ValueError) as excinfo:
        run_checks(_load(BRIEF_PAGE), "build-session", ["build-session/brief-exit-edge"], context={})
    assert "brief" in str(excinfo.value).lower()


def test_introduced_canon_refuses_without_the_record_extract():
    # The row is DEFINED as a diff against the campaign canon record. Handed no
    # record, it stops rather than grading half its own definition — the same
    # refusal spotlight-annotations-name-pc makes without a roster.
    with pytest.raises(ValueError) as excinfo:
        run_checks(_load(BRIEF_PAGE), "build-session",
                   ["build-session/brief-introduced-canon"], context={"brief": _load(BRIEF)})
    assert "canon_record" in str(excinfo.value)


# The satisfied case: one page, all nine rows.

def test_the_good_page_satisfies_every_spec_row():
    assert _spec_run(_load(BRIEF_PAGE)) == []


def test_the_good_page_also_passes_the_whole_page_owned_subset():
    # The brief page was only ever asserted clean against the nine spec-axis rows
    # above, so the rows every session page owes went ungraded on it — and it was
    # missing its Preparation section and all four art pieces while being named
    # `_good` and used as the base for every variant in this section. Same shape
    # as the keyed-page defect f42cbb1/fbfe586 fixed: a fixture treated as
    # known-good while failing a shipped rule, invisible because nothing ran that
    # rule against it. A variant is only "one edit, one row" if the page under it
    # is clean everywhere, so this pins the base against the page-owned subset too.
    assert run_checks(_load(BRIEF_PAGE), "build-session", SESSION_SUBSET,
                      context=SESSION_CTX) == []


# One violated case per row, each firing exactly its own row.

def _drop_background(page):
    start = page.index("## Adventure Background")
    end = page.index("## Beginning the Adventure")
    return page[:start] + "## Adventure Background\n\nThe crate moved fast.\n\n" + page[end:]


def _features_after_the_first_key(page):
    page = page.replace(_FEATURES, "")
    return page.replace(
        "Museum Square and the front steps. Samira",
        _FEATURES + "Museum Square and the front steps. Samira",
    )


SPEC_VARIANTS = {
    # Three facts the brief licensed as introduced canon, and a page that asserts
    # none of them: the licence the night never used.
    "build-session/brief-introduced-canon": _drop_background,
    # The ground rules stated only once a room is already keyed.
    "build-session/brief-ground-rules-stated": _features_after_the_first_key,
    # A locked NPC with no roster row.
    "build-session/brief-npc-commitments": lambda p: p.replace(
        "| Orla Selke | Mrs. Iselin in *The Manchurian Candidate* | Curator; fences the museum's own acquisitions | {monster:Noble} | T5 |\n", ""),
    # The hour the brief fixed for the egg's effects, named nowhere.
    "build-session/brief-timeline-commitments": lambda p: p.replace(
        "begins to pulse at half past ten", "begins to pulse late in the evening"),
    # The premise still enacted, the revelation left exactly where it was.
    "build-session/brief-revelation-paid-down": lambda p: p.replace(
        "the revelation that the Gloamfen produced\n  something that is not an artifact — this lands it outright, because the party\n  are holding it.",
        "what the thing on the pedestal actually is."),
    # A page that re-anchored somewhere else entirely — the wayward conceit the
    # brief exists to prevent, and the one thing this row still catches after it
    # was widened off the structural slots (see its docstring).
    "build-session/brief-destination-nodes": lambda p: (
        p.replace("Grayharbour Museum", "Cold Halls").replace("Gemstone Wing", "Long Gallery")
         .replace("Museum Square", "Chandler Square").replace("museum", "gallery")
         .replace("Museum", "Gallery")),
    # Two live leads in the Conclusion, neither reaching where the brief fixed the exit.
    "build-session/brief-exit-edge": lambda p: p.replace(
        "points back at the Gloamfen\n  and the site that produced both", "points back at the flooded quarry"
    ).replace("Fenwick's account points at the university", "the porter's account points at the guild"),
    # Four entrances locked; three boundary edges drawn.
    "build-session/brief-map-topology": lambda p: p.replace(
        "| E8 | Chandler Row alley → T11 | open — the loading dock doors |\n", ""),
    # A keyed area for the one place the brief took off the board.
    "build-session/brief-not-tonight": lambda p: p.replace(
        "- [T11 — The basement loading dock](#t11)",
        "- [T11 — The basement loading dock](#t11)\n- [T12 — The Gloamfen dig, three days out](#t12)"),
}


@pytest.mark.parametrize("row", SPEC_AXIS)
def test_each_row_fires_on_its_own_violation(row):
    page = SPEC_VARIANTS[row](_load(BRIEF_PAGE))
    assert page != _load(BRIEF_PAGE), "the variant edit did not apply"
    findings = _spec_run(page)
    assert findings, f"{row} did not fire on its own violation"
    assert {f.check_id for f in findings} == {row}, (
        "one edit, one row: " + ", ".join(sorted({f.check_id for f in findings}))
    )


def test_the_diff_half_reads_the_record_extract():
    # The other direction of `Introduced canon`: a fact the brief calls new that
    # the record already carries in full. Nothing about the PAGE changes — only
    # the record extract — so this can only be the diff half firing.
    record = _load(BRIEF_RECORD) + (
        "\n- The hatchling is ravenous for raw meat and grows exponentially.\n")
    findings = run_checks(_load(BRIEF_PAGE), "build-session",
                          ["build-session/brief-introduced-canon"],
                          context=_spec_context(canon_record=record))
    assert len(findings) == 1
    assert "already carries" in findings[0].actual


# The residual scoping (spec Implementation Decision 5): two rows that must not
# be satisfiable by one sentence.

def test_premise_prose_cannot_pay_down_the_revelation():
    # The page enacts the premise in full and says the revelation's own words in
    # its narrative prose — and still has not moved it, because no clue payload
    # carries it. `brief-revelation-paid-down` reads payload blocks, so the
    # sentence that satisfies a premise row is structurally unable to satisfy it.
    page = SPEC_VARIANTS["build-session/brief-revelation-paid-down"](_load(BRIEF_PAGE))
    page = page.replace(
        "## Adventure Background\n",
        "## Adventure Background\n\nTonight the Gloamfen produced something that is not an\n"
        "artifact, and the party are the ones who find that out.\n",
    )
    findings = run_checks(page, "build-session",
                          ["build-session/brief-revelation-paid-down"], context=_spec_context())
    assert len(findings) == 1
    assert "does not move it" in findings[0].actual


def test_ground_rules_row_says_nothing_about_routes():
    # Route consistency against a guard claim is `dungeon-generator/guarded-approach-holds`,
    # a Standards row on another skill. Rewiring every route so the wing is
    # reachable without meeting a post changes nothing here: this row grades the
    # rule as stated and its position, and the edge table is not its business.
    page = _load(BRIEF_PAGE).replace(
        "| E4 | T7 — T9 | secret · door — a curtained pantry door into the wing |",
        "| E4 | T7 — T1 | open — the wing opens straight onto the front steps |")
    assert run_checks(page, "build-session",
                      ["build-session/brief-ground-rules-stated"], context=_spec_context()) == []


def test_the_curator_is_locked_aimed_at_and_excluded_at_once():
    # The three-way case the slot list exists for. The brief locks Selke as an
    # NPC, points its exit edge at her syndicate, and excludes CONFRONTING that
    # syndicate. A page that keeps all three — roster row, lead in the Conclusion,
    # no keyed area for her — must pass all three rows.
    page = _load(BRIEF_PAGE).replace(
        "- **Lead →** Fenwick's account points at the university",
        "- **Lead →** the private seal points at Orla Selke and the arrangement\n"
        "  behind her.\n- **Lead →** Fenwick's account points at the university")
    assert run_checks(page, "build-session", [
        "build-session/brief-npc-commitments",
        "build-session/brief-exit-edge",
        "build-session/brief-not-tonight",
    ], context=_spec_context()) == []


def test_a_page_with_no_edge_table_carries_no_shape_to_check():
    page = _load(BRIEF_PAGE)
    # Cut from the comment OPENER, not from the heading inside it: slicing at the
    # heading leaves the `<!--` behind with nothing to close it, and a page whose
    # comment never closes hides everything below it — a different defect from the
    # one this test is about, and one `build-session/edges-not-dm-visible` reports.
    start = page.index("<!--\n### Edges (render-ready)")
    end = page.index("### T1")
    variant = page[:start] + page[end:]
    assert "<!--" not in variant and "-->" not in variant
    assert run_checks(variant, "build-session",
                      ["build-session/brief-map-topology"], context=_spec_context()) == []


def test_concealing_the_table_does_not_change_the_topology_verdict():
    # The good page files its edge table inside an HTML comment, because the table
    # is machine state rather than something a DM reads. This row only keeps
    # working because its section search reads raw markdown and matches inside the
    # comment. Both arms below run the same page twice — once as filed, once with
    # the comment markers stripped so the table is visible — and the verdicts must
    # be identical.
    #
    # The firing arm is the one with teeth. A change that made the search skip
    # commented-out regions would take the check dark, and a dark check still
    # returns [] on the good page; only a violation that MUST be found proves the
    # concealed table is still being read.
    def visible(page):
        return page.replace("<!--\n### Edges (render-ready)", "### Edges (render-ready)").replace(
            "| E9 | The Quill's service alley → T11 | secret — the old tunnel out of the basement |\n-->",
            "| E9 | The Quill's service alley → T11 | secret — the old tunnel out of the basement |")

    concealed_page = _load(BRIEF_PAGE)
    visible_page = visible(concealed_page)
    assert visible_page != concealed_page, "the fixture's table is not concealed"
    assert "<!--" not in visible_page and "-->" not in visible_page, \
        "the visible arm is still concealed — both arms would read the same page"
    row = ["build-session/brief-map-topology"]

    # Clean arm: the shape holds either way.
    assert run_checks(concealed_page, "build-session", row, context=_spec_context()) == []
    assert run_checks(visible_page, "build-session", row, context=_spec_context()) == []

    # Firing arm: four entrances locked, one boundary edge deleted.
    violate = SPEC_VARIANTS["build-session/brief-map-topology"]
    concealed_findings = run_checks(violate(concealed_page), "build-session", row,
                                    context=_spec_context())
    visible_findings = run_checks(violate(visible_page), "build-session", row,
                                  context=_spec_context())
    assert concealed_findings, "the concealed table was not read — the check went dark"
    assert [(f.check_id, f.expected, f.actual) for f in concealed_findings] == \
           [(f.check_id, f.expected, f.actual) for f in visible_findings]


def test_the_vertical_half_reads_the_comma_notation_the_arms_wrote():
    # Every ablation arm typed its vertical edges with commas rather than the
    # grammar's `·`. A check that only saw `·`-separated tokens would sit dark on
    # the notation the flattening defect actually arrived in.
    page = _load(BRIEF_PAGE).replace(" · ", ", ")
    assert run_checks(page, "build-session",
                      ["build-session/brief-map-topology"], context=_spec_context()) == []


def test_an_hour_is_satisfied_in_either_notation():
    # A page writing "half past ten" has kept a 10:30 p.m. commitment; one writing
    # "10:30 p.m." has too. Firing on the difference would be a finding about
    # punctuation rather than about the contract.
    for spelling in ("at half past ten", "at 10:30 p.m.", "at ten o'clock"):
        page = _load(BRIEF_PAGE).replace("at half past ten", spelling)
        assert run_checks(page, "build-session",
                          ["build-session/brief-timeline-commitments"],
                          context=_spec_context()) == []


# Behaviours pinned deliberately after running every row over the seven worked
# Gloamfen pages in the ablation apparatus. Four were killed as false positives;
# the fifth is kept, and is pinned here so it cannot be lost by accident.

def test_a_stated_distance_is_satisfied_in_either_notation():
    # A frozen arm wrote "a thirty-foot ceiling" for the brief's `30 feet` rule.
    # Firing on that is a finding about notation, not about the contract.
    page = _load(BRIEF_PAGE).replace("Ceilings run 30 feet", "Ceilings run thirty feet")
    assert run_checks(page, "build-session",
                      ["build-session/brief-ground-rules-stated"], context=_spec_context()) == []


def test_an_hour_range_is_one_requirement_either_endpoint_satisfies():
    # The gala that runs 6–8 p.m. is one window. A frozen arm named only its
    # close ("before 8 p.m.") and had kept the commitment.
    page = _load(BRIEF_PAGE).replace("The gala runs 6–8 p.m. and the doors close",
                                     "The gala is over and the doors close at 8 p.m.")
    assert run_checks(page, "build-session",
                      ["build-session/brief-timeline-commitments"], context=_spec_context()) == []


def test_an_excluded_thread_is_keyed_by_more_than_its_proper_noun():
    # "Fenwick's reinstatement" is excluded and Fenwick is the night's client. A
    # clue keyed under her name is not the excluded thread, and reporting it would
    # fire on a page that kept the contract — the exact false positive a frozen
    # arm produced.
    page = _load(BRIEF_PAGE).replace(
        "- [T5 — The records room](#t5)",
        "- [T5 — The records room](#t5)\n- [T6 — Fenwick's ledger of nights](#t6)")
    assert run_checks(page, "build-session",
                      ["build-session/brief-not-tonight"], context=_spec_context()) == []
    # The thread itself, keyed, still fires.
    staged = _load(BRIEF_PAGE).replace(
        "- [T5 — The records room](#t5)",
        "- [T5 — The records room](#t5)\n- [T6 — Fenwick's reinstatement hearing](#t6)")
    assert len(run_checks(staged, "build-session",
                          ["build-session/brief-not-tonight"], context=_spec_context())) == 1


# The Potential Scenes slot, which sat inert from its introduction until this
# fix: the heading's `.*` ran under DOTALL and swallowed the section, so `body` was always empty and
# the slot silently never contributed. Pinned in both directions off inline
# variants rather than by extending the shared good page — one site, minimal diff,
# the same convention the rest of this section keeps.

_SCENES_ANCHOR = "## Adventure Background"


def _with_scenes(page, *bullets):
    section = "## Potential Scenes\n\n" + "".join(f"- {b}\n" for b in bullets) + "\n"
    return page.replace(_SCENES_ANCHOR, section + _SCENES_ANCHOR, 1)


def test_the_potential_scenes_body_is_the_entries_not_the_empty_string():
    sample = _with_scenes(_load(BRIEF_PAGE), "The vault corridor, after the alarm")
    body = checker._POTENTIAL_SCENES_RE.search(sample).group("body")
    assert "The vault corridor, after the alarm" in body
    # And it stops at the next heading rather than running to the end of the page.
    assert _SCENES_ANCHOR not in body


def test_an_excluded_thread_staged_as_a_scene_fires():
    page = _with_scenes(_load(BRIEF_PAGE), "The Gloamfen dig, three days out by cart")
    findings = run_checks(page, "build-session",
                          ["build-session/brief-not-tonight"], context=_spec_context())
    assert len(findings) == 1
    assert "Gloamfen dig" in findings[0].actual


def test_scenes_that_stage_nothing_excluded_stay_green():
    page = _with_scenes(
        _load(BRIEF_PAGE),
        "The gala floor, before the doors close",
        "The service stair, once the alarm is up",
    )
    assert run_checks(page, "build-session",
                      ["build-session/brief-not-tonight"], context=_spec_context()) == []


def test_the_page_title_is_not_a_staging_slot():
    # The session is named for its own subject and the brief takes that subject's
    # dig off the board. Both are correct at once.
    assert "# Session 3 — The Gloamfen Malevolence" in _load(BRIEF_PAGE)
    assert run_checks(_load(BRIEF_PAGE), "build-session",
                      ["build-session/brief-not-tonight"], context=_spec_context()) == []


def test_a_payload_that_says_the_revelation_in_its_own_words_carries_it():
    # Pages rephrase a revelation's title routinely. A payload carrying every
    # distinctive term of it has carried it, so this row is about the transition
    # rather than about wording.
    page = _load(BRIEF_PAGE).replace(
        "the revelation that the Gloamfen produced\n  something that is not an artifact",
        "what the Gloamfen produced, which was never an artifact at all")
    assert run_checks(page, "build-session",
                      ["build-session/brief-revelation-paid-down"], context=_spec_context()) == []


def test_payloads_pointing_only_at_nodes_do_not_pay_a_revelation_down():
    # RETAINED against a frozen arm, not a false positive. The page format permits
    # a Points-at naming "the node OR revelation", so a node-only payload is legal
    # in general — but a brief that locks a revelation transition makes naming it
    # the contract, and a page that pays clues down while recording nothing about
    # what they pay leaves the DM no way to tell the revelation moved.
    page = _load(BRIEF_PAGE)
    page = page.replace("the papering revelation, which this\n  completes",
                        "the museum's own paperwork in [T9](#t9)")
    page = page.replace("unprovenanced finds are being papered through legitimate\n  institutions",
                        "the books were dressed after the fact")
    page = page.replace(
        "the revelation that the Gloamfen produced\n  something that is not an artifact — this lands it outright, because the party\n  are holding it.",
        "the wing itself, and out of the museum entirely.")
    findings = run_checks(page, "build-session",
                          ["build-session/brief-revelation-paid-down"], context=_spec_context())
    assert len(findings) == 2


# --------------------------------------------------------------------------- #
# build-session — unlicensed additive canon on a locked subject.
# --------------------------------------------------------------------------- #
#
# The row the ablation proved was missing. One frozen arm scored **11 of 11**
# while minting seven new facts about objects its brief locked, and nothing in
# the proposition set caught it: every other row asks whether the LICENSED facts
# landed, and none asks whether unlicensed ones were added.
#
# `session_brief_page_unlicensed_canon.md` reproduces that case in this brief's
# own idiom — the satisfied page, plus seven new facts about locked subjects
# (four carrying a number, three carrying none) and one invention about a subject
# the brief never locks.

CANON_ROW = "build-session/brief-locked-subject-canon"
BRIEF_PAGE_UNLICENSED = "session_brief_page_unlicensed_canon.md"


def test_locked_subject_set_is_the_locked_lines_and_not_the_prose_around_them():
    # The scope IS the row. A junk subject matches page prose everywhere, and the
    # row would become the general no-new-canon rule it must not be.
    subjects = checker.locked_subjects(_load(BRIEF))
    for named in ("Isolde Fenwick", "Orla Selke", "Samira Romero", "Gloamfen",
                  "Grayharbour Museum", "Gemstone Wing", "Museum Square"):
        assert named in subjects
    # Sentence-opening capitals are the writing, not names; an ability is system
    # vocabulary; and `Not tonight` names the EXCLUDED, which is not the locked.
    for junk in ("Twelve", "Interior", "Alarm", "Eldritch", "Wisdom", "Home",
                 "Old Town", "Harrow"):
        assert junk not in subjects


def test_proper_noun_runs_keep_a_genuine_trailing_s():
    # rstrip("'s") strips a character SET, not a suffix — it ate the real tail
    # of any s-final name ("Reyes" → "Reye"). The strip may remove a
    # possessive "'s" or a bare plural-possessive apostrophe, nothing more.
    runs = [run for run, _, _ in checker._proper_noun_offsets(
        "Tomas Reyes holds the east gate. Reyes' orders come from Marlow's syndicate."
    )]
    assert "Tomas Reyes" in runs
    assert "Reyes" in runs
    assert "Marlow" in runs
    assert not any(r.endswith("Reye") for r in runs)


def test_the_eleven_of_eleven_page_passes_every_other_row_and_fails_this_one():
    # The reproduction, and the assertion that matters is the first one: the page
    # that mints seven facts about locked subjects satisfies every field row in
    # the axis, exactly as the frozen arm did.
    page = _load(BRIEF_PAGE_UNLICENSED)
    assert _spec_run(page) == []
    assert CANON_ROW not in checker.brief_checks(_load(BRIEF))  # a row, not a field row
    findings = run_checks(page, "build-session", [CANON_ROW], context=_spec_context())
    assert len(findings) == 4
    assert all(f.check_id == CANON_ROW for f in findings)
    subjects_reported = " ".join(f.actual for f in findings)
    for subject in ("Fenwick", "Orla Selke", "Gloamfen"):
        assert subject in subjects_reported


def test_the_satisfied_page_mints_nothing_and_draws_nothing():
    assert run_checks(_load(BRIEF_PAGE), "build-session", [CANON_ROW],
                      context=_spec_context()) == []


def test_the_row_does_not_fire_on_new_content_about_an_unlocked_subject():
    # The scoping, tested from the other side. The fixture invents a whole net
    # trap with its own DC — canon the brief never licensed, about a subject the
    # brief never locks. Silence is never a constraint, and inventing into it is
    # what the generator is for.
    findings = run_checks(_load(BRIEF_PAGE_UNLICENSED), "build-session", [CANON_ROW],
                          context=_spec_context())
    reported = " ".join(f.actual for f in findings)
    assert "net" not in reported and "14" not in reported
    # And on its own, with none of the locked-subject inventions beside it.
    page = _load(BRIEF_PAGE).replace(
        "built a crystal box that will hold the thing quiet",
        "built a crystal box that will hold the thing quiet. A weighted net hangs\n"
        "above the staff entrance and drops on the first person through it — DC 14\n"
        "Dexterity save, and the courier's cart outside carries seventeen crates")
    assert run_checks(page, "build-session", [CANON_ROW], context=_spec_context()) == []


def test_the_row_reads_the_adventure_background_and_not_the_keyed_areas():
    # A keyed area rendering a locked place in fresh words is the page doing its
    # job. A whole-page read would fire on every correct page — the failure the
    # axis's structural-slot rule exists to prevent.
    invention = ("Orla Selke has been fencing objects out of the Grayharbour "
                 "Museum for forty years.")
    page = _load(BRIEF_PAGE).replace(
        "The records room, off the service way.",
        "The records room, off the service way. " + invention)
    assert run_checks(page, "build-session", [CANON_ROW], context=_spec_context()) == []
    moved = _load(BRIEF_PAGE).replace(
        "Fenwick has\nbuilt a crystal box", invention + " Fenwick has\nbuilt a crystal box")
    assert len(run_checks(moved, "build-session", [CANON_ROW], context=_spec_context())) == 1


def test_a_quantity_the_brief_or_the_record_supplies_is_not_an_invention():
    # Either notation, and either source. A page writing *thirty feet* has been
    # given `30 feet`, and the record's own facts are not the page's inventions.
    page = _load(BRIEF_PAGE).replace(
        "Fenwick has\nbuilt a crystal box",
        "The Grayharbour Museum is a mile from the university and its halls run "
        "thirty feet to the ceiling, and twelve guards hold it. Fenwick has\n"
        "built a crystal box")
    assert run_checks(page, "build-session", [CANON_ROW], context=_spec_context()) == []


def test_locked_subject_canon_refuses_without_the_record_extract():
    # Same refusal as brief-introduced-canon: "neither the brief nor the record
    # supplies" graded against the brief alone would report the record's own facts
    # as inventions.
    with pytest.raises(ValueError) as excinfo:
        run_checks(_load(BRIEF_PAGE_UNLICENSED), "build-session", [CANON_ROW],
                   context={"brief": _load(BRIEF)})
    assert "canon_record" in str(excinfo.value)


def test_locked_subject_canon_needs_no_adventure_background_to_stay_silent():
    # A page with no such section carries no assertion in the page's own voice,
    # and the row says nothing rather than reaching for the rest of the page.
    page = _load(BRIEF_PAGE_UNLICENSED).replace("## Adventure Background", "## Notes")
    assert run_checks(page, "build-session", [CANON_ROW], context=_spec_context()) == []
