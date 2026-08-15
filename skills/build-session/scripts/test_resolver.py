from resolver import find_references, resolve_reference, resolve_references_in_text


def test_find_monster_reference():
    text = "A {monster:Frost Giant} blocks the path."
    refs = find_references(text)
    assert len(refs) == 1
    assert refs[0] == {"type": "monster", "name": "Frost Giant"}


def test_find_multiple_references():
    text = "DC 15 {skill:Persuasion} check to calm the {monster:Goblin Boss}."
    refs = find_references(text)
    assert len(refs) == 2
    types = {r["type"] for r in refs}
    assert types == {"skill", "monster"}


def test_find_all_reference_types():
    text = "{monster:Goblin} {item:Potion of Healing} {spell:Fireball} {skill:Stealth} {condition:Poisoned}"
    refs = find_references(text)
    assert len(refs) == 5


def test_resolve_monster_url():
    url = resolve_reference("monster", "Frost Giant")
    assert "dndbeyond.com/monsters/" in url
    assert "frost-giant" in url


def test_resolve_item_url():
    url = resolve_reference("item", "Potion of Healing")
    assert "dndbeyond.com/magic-items/" in url


def test_resolve_spell_url():
    url = resolve_reference("spell", "Fireball")
    assert "dndbeyond.com/spells/" in url


def test_resolve_unknown_returns_url():
    # resolve_reference always constructs a URL — no database to validate against.
    # DDB will 404 for invalid names, but broken links never block rendering.
    url = resolve_reference("monster", "Xyzzy the Unknowable")
    assert url is not None
    assert "dndbeyond.com/monsters/" in url
    assert "xyzzy-the-unknowable" in url


def test_resolve_references_in_text_produces_html():
    result = resolve_references_in_text("A {monster:Goblin} attacks.")
    assert '<a href=' in result
    assert 'class="ref-monster"' in result
    assert "Goblin" in result


def test_resolve_references_in_text_unknown_produces_link():
    # Since resolve_reference always returns a URL, even unknown names get <a> tags.
    result = resolve_references_in_text("A {monster:Xyzzy the Unknowable} lurks.")
    assert '<a href=' in result
    assert 'class="ref-monster"' in result
    assert "Xyzzy the Unknowable" in result


def test_resolve_skill_goes_to_playing_the_game():
    url = resolve_reference("skill", "Sleight of Hand")
    assert url == "https://www.dndbeyond.com/sources/dnd/free-rules/playing-the-game#Skills"


def test_resolve_condition_carries_condition_suffix():
    url = resolve_reference("condition", "prone")
    assert url == "https://www.dndbeyond.com/sources/dnd/br-2024/rules-glossary#ProneCondition"


def test_resolve_action_carries_action_suffix():
    url = resolve_reference("action", "Influence")
    assert url == "https://www.dndbeyond.com/sources/dnd/br-2024/rules-glossary#InfluenceAction"


def test_house_condition_resolves_to_styled_span():
    # Dazed is a house condition — no DDB anchor exists, so it must render
    # as a styled term, never a broken anchor.
    assert resolve_reference("condition", "Dazed") is None
    result = resolve_references_in_text("The goblin is {condition:Dazed}.")
    assert '<span class="ref-condition">Dazed</span>' in result
