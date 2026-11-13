import ast
import copy
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import report
from engine import play
from scenario import apply_variant, auto_variants, check, load, unmodelled
from simulate import review_text, scenario_problems

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
UNBEATABLE_DC = 99
GOOD = sorted(p for p in FIXTURES.glob("*.scenario.json") if p.name != "bad_shape.scenario.json")


def _cli(*args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / "simulate.py"), *map(str, args)],
                          capture_output=True, text=True, cwd=cwd)


def _sure_hit(dice="10", kind=None, **extra):
    return {"id": "strike", "reach": extra.pop("reach", "melee"), **extra, "effects": [
        {"kind": "save", "ability": "con", "dc": UNBEATABLE_DC,
         "fail": [{"kind": "damage", "dice": dice, **({"type": kind} if kind else {})}]}]}


def _creature(cid, side, actions=(), **fields):
    return {"id": cid, "side": side, "zone": "yard", "ac": 10, "hp": 100, "actions": list(actions), **fields}


def _scenario(*combatants, **fields):
    return {
        "format": "encounter-scenario/1", "name": "test", "round_limit": 3,
        "zones": [{"id": "yard"}, {"id": "gate"}], "links": [{"between": ["yard", "gate"], "feet": 30}],
        "combatants": list(combatants),
        "objectives": {"party": {"wins": [{"kind": "defeat", "side": "enemies"}]},
                       "enemies": {"wins": [{"kind": "defeat", "side": "party"}]}},
        **fields,
    }


def _play(sc, seed=1, log=False):
    assert check(sc) == []
    return play(sc, random.Random(seed), log=log)


def _by_id(result, cid):
    return next(c for c in result["creatures"] if c["id"] == cid)


@pytest.mark.parametrize("path", GOOD, ids=lambda p: p.name)
def test_shipped_fixtures_pass_the_shape_check(path):
    assert check(load(path)) == []


def test_shape_check_names_every_break():
    result = _cli("check", FIXTURES / "bad_shape.scenario.json")
    assert result.returncode == 1
    for needle in ("'format' must be", "'cover' must be", "unknown key 'armour'", "not a dice expression",
                   "missing 'enemies'"):
        assert needle in result.stdout


def test_same_seed_gives_the_same_report_and_a_new_seed_does_not():
    path = FIXTURES / "the_countdown.scenario.json"
    first = _cli("run", path, "--runs", "60", "--seed", "5")
    again = _cli("run", path, "--runs", "60", "--seed", "5")
    other = _cli("run", path, "--runs", "60", "--seed", "6")
    assert first.returncode == 0, first.stderr
    assert first.stdout == again.stdout
    assert first.stdout != other.stdout


def test_run_needs_nothing_but_the_scenario_file(tmp_path):
    shutil.copy(FIXTURES / "toll_road_ambush.scenario.json", tmp_path / "fight.scenario.json")
    result = _cli("run", "fight.scenario.json", "--runs", "20", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "## Outcome" in result.stdout


def test_engine_imports_only_the_standard_library():
    local = {p.stem for p in HERE.glob("*.py")}
    for name in ("scenario", "engine", "report", "simulate"):
        tree = ast.parse((HERE / f"{name}.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = ([a.name for a in node.names] if isinstance(node, ast.Import)
                       else [node.module] if isinstance(node, ast.ImportFrom) else [])
            for module in modules:
                root = module.split(".")[0]
                assert root in local or root in sys.stdlib_module_names, f"{name}.py imports {module}"


def test_report_carries_every_section_the_dm_reads():
    out = _cli("run", FIXTURES / "toll_road_ambush.scenario.json", "--runs", "80").stdout
    for heading in ("## Outcome", "## Player characters", "## Limited resources spent",
                    "## What moves the result", "## A typical run", "## A bad run", "## Not modelled"):
        assert heading in out
    assert "Parry reaction" in out.split("## Not modelled")[1]


def test_action_outside_the_closed_set_is_reported_and_never_played():
    summon = {"id": "summon", "name": "Summon Swarm", "effects": [{"kind": "summon", "creature": "rats"}]}
    sc = _scenario(_creature("hero", "party", [_sure_hit()], pc=True),
                   _creature("witch", "enemies", [summon, _sure_hit()]))
    assert [g["item"] for g in unmodelled(sc)] == ["Summon Swarm"]
    result = _play(sc, log=True)
    assert not any("Summon Swarm" in line for line in result["log"])
    assert _by_id(result, "hero")["taken"] > 0
    rendered = report.render(sc, report.summarize([result]), [], {}, "1")
    assert "Summon Swarm" in rendered.split("## Not modelled")[1]


def test_unknown_condition_makes_its_action_unmodelled():
    hex_ = {"id": "hex", "effects": [{"kind": "condition", "name": "cursed", "duration": {"rounds": 1}}]}
    sc = _scenario(_creature("hero", "party", [_sure_hit()], pc=True), _creature("witch", "enemies", [hex_]))
    assert check(sc) == []
    assert "cursed" in unmodelled(sc)[0]["reason"]


def test_resistance_halves_immunity_stops_and_vulnerability_doubles():
    def taken(**defence):
        sc = _scenario(_creature("hero", "party", [_sure_hit("10", "fire")], pc=True),
                       _creature("dummy", "enemies", [], **defence), round_limit=1)
        return _by_id(_play(sc), "dummy")["taken"]
    assert taken() == 10
    assert taken(resistances=["fire"]) == 5
    assert taken(immunities=["fire"]) == 0
    assert taken(vulnerabilities=["fire"]) == 20


def test_a_paralyzed_creature_takes_no_turn_and_fails_dex_saves():
    hold = {"id": "hold", "effects": [
        {"kind": "save", "ability": "wis", "dc": UNBEATABLE_DC,
         "fail": [{"kind": "condition", "name": "paralyzed", "duration": {"rounds": 5}}]},
        {"kind": "save", "ability": "dex", "dc": 1, "fail": [{"kind": "damage", "dice": "7"}]}]}
    sc = _scenario(_creature("hero", "party", [hold], pc=True, initiative=50),
                   _creature("ogre", "enemies", [_sure_hit()], saves={"dex": 20}))
    result = _play(sc)
    assert _by_id(result, "hero")["taken"] == 0
    assert _by_id(result, "ogre")["taken"] == 7 * 3


def test_condition_immunity_blocks_the_condition():
    stun = {"id": "stun", "effects": [{"kind": "save", "ability": "con", "dc": UNBEATABLE_DC, "fail": [
        {"kind": "condition", "name": "stunned", "duration": {"rounds": 5}}]}]}
    sc = _scenario(_creature("hero", "party", [stun], pc=True, initiative=50),
                   _creature("golem", "enemies", [_sure_hit()], condition_immunities=["stunned"]))
    assert _by_id(_play(sc), "hero")["taken"] == 30


def test_a_downed_pc_returns_when_healed_and_a_monster_does_not():
    heal = {"id": "heal", "target": "ally", "reach": {"range": 60}, "effects": [{"kind": "heal", "dice": "5"}]}
    sc = _scenario(
        _creature("tank", "party", [], pc=True, hp=5, initiative=10),
        _creature("medic", "party", [heal], pc=True, zone="gate", initiative=5,
                  tactics={"position": "hold", "plan": [{"use": "heal", "when": {"ally_hp_below": 0.5}}]}),
        _creature("brute", "enemies", [_sure_hit()], initiative=20, tactics={"position": "hold"}),
        round_limit=2)
    result = _play(sc, log=True)
    assert _by_id(result, "tank")["drops"] == 2
    assert any("Tank regains" in line or "tank regains" in line for line in result["log"])


def test_half_cover_and_three_quarters_cover_raise_armor_class_from_another_zone():
    def hits(cover):
        shot = {"id": "shot", "reach": {"range": 60}, "effects": [
            {"kind": "attack", "to_hit": 0, "hit": [{"kind": "damage", "dice": "1"}]}]}
        zones = [{"id": "yard", **({"cover": cover} if cover else {})}, {"id": "gate"}]
        sc = _scenario(_creature("archer", "party", [shot], pc=True, zone="gate", tactics={"position": "hold"}),
                       _creature("target", "enemies", [], ac=14), zones=zones, round_limit=20)
        return sum(_by_id(_play(sc, seed), "target")["taken"] for seed in range(40))
    assert hits(None) > hits("half") > hits("three-quarters") > 0


def test_a_melee_fighter_must_cross_the_link_before_it_can_sure_hit():
    sc = _scenario(_creature("hero", "party", [_sure_hit()], pc=True, speed=30, initiative=50),
                   _creature("far", "enemies", [], zone="gate"),
                   links=[{"between": ["yard", "gate"], "feet": 60}], round_limit=2)
    assert _by_id(_play(sc), "far")["taken"] == 10


@pytest.mark.parametrize("position, expected", [("close", 10), ("keep range", 0), ("hold", 0), ({"go": "yard"}, 0)])
def test_only_the_close_position_walks_into_melee(position, expected):
    sc = _scenario(_creature("hero", "party", [_sure_hit()], pc=True, tactics={"position": position}),
                   _creature("far", "enemies", [], zone="gate"), round_limit=1)
    assert _by_id(_play(sc), "far")["taken"] == expected


def test_a_choke_limits_how_many_of_one_side_stand_in_it():
    zones = [{"id": "yard"}, {"id": "gate", "capacity": 1}]
    sc = _scenario(_creature("mob", "party", [_sure_hit("1")], pc=True, count=4, initiative=50),
                   _creature("warden", "enemies", [], zone="gate"), zones=zones, round_limit=1)
    assert _by_id(_play(sc), "warden")["taken"] == 1


def test_reinforcements_enter_on_their_round_unless_the_guard_is_down():
    def late_damage(lookout_hp):
        sc = _scenario(
            _creature("hero", "party", [_sure_hit("50")], pc=True, initiative=50, tactics={"focus": ["lookout"]}),
            _creature("lookout", "enemies", [], hp=lookout_hp),
            _creature("wall", "enemies", [], hp=1000),
            _creature("late", "enemies", [_sure_hit("3")], zone=None),
            events=[{"round": 2, "kind": "enter", "combatant": "late", "zone": "yard", "unless_down": "lookout"}],
            round_limit=3)
        return _by_id(_play(sc), "late")["dealt"]
    assert late_damage(lookout_hp=1000) == 6
    assert late_damage(lookout_hp=10) == 0


def test_a_clock_objective_ends_the_fight_for_the_side_it_favours():
    sc = _scenario(_creature("hero", "party", [_sure_hit("1")], pc=True),
                   _creature("cult", "enemies", [], hp=1000), round_limit=10)
    sc["objectives"]["enemies"]["wins"] = [{"kind": "rounds", "round": 4}]
    result = _play(sc)
    assert (result["rounds"], result["met"]) == (4, ["enemies"])


def test_defeating_the_named_target_wins_while_its_screen_still_stands():
    sc = _scenario(_creature("hero", "party", [_sure_hit("50")], pc=True, tactics={"focus": ["leader"]}),
                   _creature("leader", "enemies", [], hp=40), _creature("screen", "enemies", [], count=3))
    sc["objectives"]["party"]["wins"] = [{"kind": "defeat", "combatant": "leader"}]
    result = _play(sc)
    assert (result["rounds"], result["met"]) == (1, ["party"])


def test_a_creature_that_flees_counts_as_defeated():
    sc = _scenario(_creature("hero", "party", [_sure_hit("60")], pc=True, initiative=50),
                   _creature("coward", "enemies", [_sure_hit()], tactics={"flee": {"hp_below": 0.5}}))
    result = _play(sc)
    assert _by_id(result, "coward")["status"] == "fled"
    assert result["met"] == ["party"]


def test_limited_uses_run_out_and_the_report_counts_what_was_spent():
    blast = _sure_hit("5", uses={"resource": "slot", "cost": 1})
    blast["id"] = "blast"
    sc = _scenario(_creature("mage", "party", [blast, _sure_hit("1")], pc=True, resources={"slot": 2},
                             tactics={"plan": [{"use": "blast"}, {"use": "strike"}]}),
                   _creature("dummy", "enemies", [], hp=1000), round_limit=5)
    result = _play(sc)
    assert _by_id(result, "mage")["spent"] == {"slot": 2}
    assert _by_id(result, "dummy")["taken"] == 5 + 5 + 1 + 1 + 1


def test_a_variant_changes_a_copy_and_leaves_the_scenario_alone():
    sc = load(FIXTURES / "toll_road_ambush.scenario.json")
    before = copy.deepcopy(sc)
    changed = apply_variant(sc, {"name": "more", "counts": {"bandit": 5}, "first": "party"})
    assert sc == before
    assert next(c for c in changed["combatants"] if c["id"] == "bandit")["count"] == 5
    names = [v["name"] for v in auto_variants(sc)]
    assert "the party acts first" in names and "the enemies act first" in names


def test_the_side_that_acts_first_takes_every_turn_before_the_other():
    sc = _scenario(_creature("hero", "party", [_sure_hit("100")], pc=True, initiative=-50),
                   _creature("ogre", "enemies", [_sure_hit("100")], initiative=50))
    assert _play(apply_variant(sc, {"name": "p", "first": "party"}))["met"] == ["party"]
    assert _play(apply_variant(sc, {"name": "e", "first": "enemies"}))["met"] == ["enemies"]


def test_replay_reports_where_the_record_sits_in_the_spread(tmp_path):
    sc = load(FIXTURES / "the_countdown.scenario.json")
    results = report.run_many(sc, 200, "9")
    median = report.percentile([r["rounds"] for r in results], 50)
    outcome = report.replay(results, {"rounds": median, "damage_dealt": {"rogue": 10_000},
                                      "party_met_objective": True, "dropped": ["fighter"]})
    rounds, rogue = outcome["rows"]
    assert not rounds["outside"]
    assert rogue["outside"] and rogue["position"] == 1.0
    assert len(outcome["facts"]) == 2
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"rounds": median}), encoding="utf-8")
    shown = _cli("replay", FIXTURES / "the_countdown.scenario.json", "--record", record, "--runs", "50")
    assert shown.returncode == 0 and "Position in the spread" in shown.stdout


def test_review_lists_every_action_and_marks_what_is_not_modelled():
    sc = load(FIXTURES / "the_countdown.scenario.json")
    text = review_text(sc)
    for c in sc["combatants"]:
        for a in c["actions"]:
            assert a["name"] in text
    assert "Spiritual Weapon [bonus, melee] NOT MODELLED" in text


def _swing(to_hit=5, dice="1d6"):
    return {"id": "swing", "effects": [{"kind": "attack", "to_hit": to_hit, "hit": [{"kind": "damage", "dice": dice}]}]}


def _set(path, value):
    def change(sc):
        target = sc
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return change


HERO, OGRE = ("combatants", 0), ("combatants", 1)
BREAKS = [
    (_set((*OGRE, "count"), 0), "'count' must be a whole number of 1 or more"),
    (_set((*OGRE, "count"), "3"), "'count' must be a whole number of 1 or more"),
    (_set((*OGRE, "initiative"), "fast"), "'initiative' must be a whole number"),
    (_set((*OGRE, "resources"), {"rage": "2"}), "'rage' must be a whole number of 0 or more"),
    (_set((*HERO, "actions", 0, "effects", 0, "to_hit"), "5"), "'to_hit' must be a whole number"),
    (_set((*HERO, "actions", 0, "effects", 0, "hit", 0, "dice"), "1d0"), "at least one side"),
    (_set((*HERO, "actions", 0, "uses"), {"recharge": "5"}), "'recharge' must be a whole number of 2 or more"),
    (_set((*HERO, "actions", 0, "reach"), {"range": 30, "long": "far"}), "'long' must be a number"),
    (_set((*HERO, "actions"), "swing"), "'actions' must be a list"),
    (_set((*HERO, "tactics"), {"flee": {"hp_below": "half"}}), "'hp_below' must be a number"),
    (_set(("round_limit",), "ten"), "'round_limit' must be a whole number of 1 or more"),
    (_set((*HERO, "side"), "enemies"), "the party side needs a combatant on the field"),
    (_set((*OGRE, "zone"), None), "the enemies side needs a combatant on the field"),
    (_set(("links",), []), "'gate' is not linked to the rest of the ground"),
    (_set(("zones", 0, "hazard"), [{"kind": "lava"}]), "A hazard must use the closed set"),
    (_set(("zones", 0, "capacity"), 1), "has a capacity of 1 and the party side starts 2 there"),
    (_set((*HERO, "actions"), [_swing(), {"id": "twice", "steps": ["swing"]}, {"id": "thrice", "steps": ["twice"]}]),
     "step 'twice' has steps of its own"),
]


@pytest.mark.parametrize("break_it, needle", BREAKS, ids=[needle for _, needle in BREAKS])
def test_check_rejects_a_scenario_that_would_crash_or_cannot_be_fought(break_it, needle):
    sc = _scenario(_creature("hero", "party", [_swing()], pc=True, count=2), _creature("ogre", "enemies", [_swing()]))
    assert check(sc) == []
    break_it(sc)
    assert any(needle in e for e in check(sc)), check(sc)


WRONG_VALUES = [None, "x", "", 0, -1, 2.5, True, [], {}, [1], ["x"], {"x": 1}, float("nan"), "0d0", 10**9]


def _paths(node, prefix=()):
    if prefix:
        yield prefix
    children = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, child in children:
        yield from _paths(child, (*prefix, key))


@pytest.mark.parametrize("path", GOOD, ids=lambda p: p.name)
def test_any_scenario_that_passes_the_check_can_be_reviewed_and_played(path):
    base = load(path)
    paths = list(_paths(base))
    rng = random.Random(102)
    passed = 0
    for _ in range(300):
        sc = copy.deepcopy(base)
        where, value = rng.choice(paths), copy.deepcopy(rng.choice(WRONG_VALUES))
        _set(where, value)(sc)
        try:
            if scenario_problems(sc):
                continue
            passed += 1
            review_text(sc)
            report.sensitivity(sc, report.run_many(sc, 2, "fuzz"), 2, "fuzz")
        except Exception as e:
            pytest.fail(f"{'/'.join(map(str, where))} = {value!r}: {type(e).__name__}: {e}")
    assert passed > 0


def _crowd(sc):
    del sc["zones"][0]["capacity"]
    sc["combatants"][0]["count"] = sc["combatants"][1]["count"] = 30
    sc["combatants"].append(_creature("extra", "enemies", [_swing()]))


SECOND_ROUND_BREAKS = [
    (_set(("events",), [{"round": 1, "kind": "zone", "zone": "yard", "set": {"elevation": "high"}}]),
     "'elevation' must be a number"),
    (_set(("events",), [{"round": 1, "kind": "zone", "zone": "yard", "set": {"cover": "full"}}]), "'cover' must be"),
    (_set((*OGRE, "zone"), "cellar"), "unknown zone 'cellar'"),
    (_set((*HERO, "tactics"), {"plan": [{"use": "halberd"}]}), "'use' must name one of this combatant's actions"),
    (_set(("objectives", "enemies", "wins"), []), "'enemies' needs a non-empty 'wins' list"),
    (_set(("objectives", "neutral"), {"wins": []}), "unknown key 'neutral'"),
    (_set((*HERO, "actions", 0, "effects", 0, "hit"),
          [{"kind": "condition", "name": "prone", "duration": {"rounds": 1, "name": "doom"}}]), "'duration' must be"),
    (_set((*HERO, "tactics"), {"plan": [{"use": "swing", "when": {"target_has": ["x"]}}]}), "'target_has' must be text"),
    (_set(("name",), "\ud800"), "'name' must be plain text"),
    (_set((*OGRE, "hp"), 10**400), "'hp' must be a whole number"),
    (_set(("events",), [{"round": 0, "kind": "leave", "combatant": "ogre"}]), "'round' must be a whole number of 1"),
    (_set(("events",), [{"round": 2, "kind": "enter", "combatant": "ogre", "zone": "yard"}]),
     "'ogre' starts on the field"),
    (_set((*OGRE, "zone"), ["yard"]), "'zone' must be a zone id or null"),
    (_set((*OGRE, "id"), ["ogre"]), "'id' must be text"),
    (_set(("links", 0, "feet"), float("nan")), "'feet' must be a number"),
    (_set((*HERO, "actions"), [_swing(), _swing()]), "duplicate action id 'swing'"),
    (_set((*HERO, "actions", 0, "reach"), {"range": 60, "long": 30}), "'long' must not be shorter than 'range'"),
    (_set((*HERO, "actions", 0, "effects", 0, "hit", 0, "dice"), "0d0"), "at least one die"),
    (_set(("variants",), [{"name": "none", "drop_events": 0}]), "'drop_events' must be a list"),
    (_set((*OGRE, "count"), 10**6), "'count' must be 30 or less"),
    (_crowd, "a fight takes at most 60 creatures in all"),
    (_set(("round_limit",), 10**6), "'round_limit' must be 50 or less"),
    (_set((*HERO, "actions", 0, "effects", 0, "hit", 0, "dice"), "5000d6"), "at most 100 dice"),
    (_set(("assumptions",), "none"), "'assumptions' must be a list"),
    (_set((*HERO, "actions", 0, "effects", 0, "hit", 0, "type"), 2.5), "'type' must be text"),
    (_set(("variants",), [{"name": "crowd", "counts": {"hero": 9}}]), "variants[0] 'crowd': zones: 'yard' has a capacity"),
]


@pytest.mark.parametrize("break_it, needle", SECOND_ROUND_BREAKS, ids=[n for _, n in SECOND_ROUND_BREAKS])
def test_check_rejects_what_a_second_look_found(break_it, needle):
    sc = _scenario(_creature("hero", "party", [_swing()], pc=True, count=2), _creature("ogre", "enemies", [_swing()]))
    sc["zones"][0]["capacity"] = 4
    assert check(sc) == []
    break_it(sc)
    assert any(needle in e for e in check(sc)), check(sc)


def test_check_reports_a_file_that_is_not_json(tmp_path):
    broken = tmp_path / "fight.scenario.json"
    broken.write_text("{not json", encoding="utf-8")
    result = _cli("check", broken)
    assert result.returncode == 1 and "cannot read it as JSON" in result.stdout


def test_replay_rejects_a_record_that_names_nobody_in_the_fight(tmp_path):
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"rounds": 3, "dropped": ["wizzard"], "round": 3}), encoding="utf-8")
    result = _cli("replay", FIXTURES / "the_countdown.scenario.json", "--record", record, "--runs", "20")
    assert result.returncode == 1
    assert "unknown combatant 'wizzard'" in result.stdout and "unknown key 'round'" in result.stdout


def test_a_multiattack_that_loses_a_step_is_reported_as_playing_short():
    grab = {"id": "grab", "name": "Grab", "effects": [
        {"kind": "condition", "name": "swallowed", "duration": {"rounds": 1}}]}
    both = {"id": "both", "name": "Multiattack", "steps": ["swing", "grab"]}
    sc = _scenario(_creature("hero", "party", [_swing()], pc=True),
                   _creature("toad", "enemies", [_swing(), grab, both], tactics={"plan": [{"use": "both"}]}))
    assert check(sc) == []
    reasons = {g["item"]: g["reason"] for g in unmodelled(sc)}
    assert reasons["Multiattack"] == "plays without Grab, which is not modelled"
    assert "NOT MODELLED: plays without Grab" in review_text(sc)
    assert any("uses swing" in line for line in _play(sc, log=True)["log"])


def test_a_save_based_area_rolls_its_damage_once_and_stops_at_its_maximum():
    blast = {"id": "blast", "reach": {"range": 60}, "effects": [{"kind": "area", "who": "enemies", "max": 3, "effects": [
        {"kind": "save", "ability": "dex", "dc": UNBEATABLE_DC, "fail": [{"kind": "damage", "dice": "1d100"}]}]}]}
    sc = _scenario(_creature("mage", "party", [blast], pc=True, zone="gate", tactics={"position": "hold"}),
                   _creature("mob", "enemies", [], count=5, hp=1000), round_limit=1)
    taken = sorted(c["taken"] for c in _play(sc)["creatures"] if c["id"] == "mob")
    assert taken[:2] == [0, 0]
    assert taken[2] > 0 and len(set(taken[2:])) == 1


def test_a_hazard_hurts_whoever_starts_a_turn_in_its_zone():
    zones = [{"id": "yard", "hazard": [{"kind": "damage", "dice": "3", "type": "fire"}]}, {"id": "gate"}]
    sc = _scenario(_creature("hero", "party", [], pc=True, tactics={"position": "hold"}),
                   _creature("archer", "enemies", [], zone="gate", tactics={"position": "hold"}),
                   zones=zones, round_limit=2)
    result = _play(sc)
    assert (_by_id(result, "hero")["taken"], _by_id(result, "archer")["taken"]) == (6, 0)


@pytest.mark.parametrize("movement, expected", [([], 0), (["climb"], 10), (["fly"], 10)])
def test_a_climb_costs_double_without_a_climb_or_fly_speed(movement, expected):
    zones = [{"id": "yard"}, {"id": "gate", "elevation": 15}]
    sc = _scenario(_creature("hero", "party", [_sure_hit()], pc=True, speed=30, movement=movement),
                   _creature("sniper", "enemies", [], zone="gate"), zones=zones,
                   links=[{"between": ["yard", "gate"], "feet": 20}], round_limit=1)
    assert _by_id(_play(sc), "sniper")["taken"] == expected


def test_darkness_hinders_an_attacker_who_cannot_see_in_it():
    def hits(senses):
        shot = {"id": "shot", "reach": {"range": 60}, "effects": [
            {"kind": "attack", "to_hit": 0, "hit": [{"kind": "damage", "dice": "1"}]}]}
        zones = [{"id": "yard", "light": "dark"}, {"id": "gate"}]
        sc = _scenario(_creature("archer", "party", [shot], pc=True, zone="gate", senses=senses,
                                 tactics={"position": "hold"}),
                       _creature("lurker", "enemies", [], ac=11, senses=["darkvision"], tactics={"position": "hold"}),
                       zones=zones, round_limit=20)
        return sum(_by_id(_play(sc, seed), "lurker")["taken"] for seed in range(40))
    assert hits(["darkvision"]) > hits([]) * 1.5 > 0


def test_a_concentration_effect_ends_when_its_caster_drops():
    def friend_taken(concentration):
        hold = {"id": "hold", "reach": {"range": 60}, "concentration": concentration, "effects": [
            {"kind": "save", "ability": "wis", "dc": UNBEATABLE_DC, "fail": [
                {"kind": "condition", "name": "paralyzed",
                 "duration": {"until": "save", "ability": "wis", "dc": UNBEATABLE_DC}}]}]}
        sc = _scenario(
            _creature("caster", "party", [hold], pc=True, hp=5, initiative=200, tactics={"focus": ["ogre"]}),
            _creature("friend", "party", [], pc=True, initiative=0),
            _creature("killer", "enemies", [_sure_hit()], initiative=100, tactics={"focus": ["caster"]}),
            _creature("ogre", "enemies", [_sure_hit("7")], initiative=50, tactics={"focus": ["friend"]}),
            round_limit=1)
        return _by_id(_play(sc), "friend")["taken"]
    assert (friend_taken(True), friend_taken(False)) == (7, 0)


def test_a_wider_critical_range_doubles_the_dice_more_often():
    def dealt(crit_from):
        swing = _swing(to_hit=100, dice="1d1")
        swing["effects"][0]["crit_from"] = crit_from
        sc = _scenario(_creature("hero", "party", [swing], pc=True),
                       _creature("dummy", "enemies", [], hp=1000), round_limit=20)
        return _by_id(_play(sc), "dummy")["taken"]
    assert dealt(2) > dealt(20) * 1.5
