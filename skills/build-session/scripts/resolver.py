"""DDB reference resolver.

Finds {type:Name} references in text and resolves to D&D Beyond URLs.
Unknown references return None (caller renders as plain styled text).
"""

import re
import sys

_REF_PATTERN = re.compile(r"\{(monster|item|spell|skill|condition|action):([^}]+)\}")

_URL_BASES = {
    "monster": "https://www.dndbeyond.com/monsters/",
    "item": "https://www.dndbeyond.com/magic-items/",
    "spell": "https://www.dndbeyond.com/spells/2024/",
}

# Skills have no individual glossary anchors on DDB — they all share the
# Skills section of Playing the Game. Conditions and actions have 2024
# rules-glossary entries anchored <PascalName>Condition / <PascalName>Action.
# Names outside these sets (house rules like Dazed) resolve to None so the
# caller renders a styled term rather than a broken anchor.
_RULES_GLOSSARY = "https://www.dndbeyond.com/sources/dnd/br-2024/rules-glossary#"
_SKILLS_URL = "https://www.dndbeyond.com/sources/dnd/free-rules/playing-the-game#Skills"

_SKILLS = {
    "acrobatics", "animal handling", "arcana", "athletics", "deception",
    "history", "insight", "intimidation", "investigation", "medicine",
    "nature", "perception", "performance", "persuasion", "religion",
    "sleight of hand", "stealth", "survival",
}
_CONDITIONS = {
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned",
    "prone", "restrained", "stunned", "unconscious",
}
_ACTIONS = {
    "attack", "dash", "disengage", "dodge", "help", "hide", "influence",
    "magic", "ready", "search", "study", "utilize",
}


def find_references(text: str) -> list[dict]:
    """Find all {type:Name} references in text."""
    return [
        {"type": m.group(1), "name": m.group(2)}
        for m in _REF_PATTERN.finditer(text)
    ]


def _slugify(name: str) -> str:
    """Kebab-case slug for monster/item/spell URLs."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _pascal(name: str) -> str:
    """PascalCase for rules-glossary anchors ("sleight of hand" -> "SleightOfHand")."""
    return "".join(w.capitalize() for w in name.split())


def resolve_reference(ref_type: str, name: str) -> str | None:
    """Resolve a reference to a DDB URL. Returns None if unresolvable."""
    if ref_type == "skill":
        return _SKILLS_URL if name.lower() in _SKILLS else None
    if ref_type == "condition":
        if name.lower() in _CONDITIONS:
            return f"{_RULES_GLOSSARY}{_pascal(name)}Condition"
        return None
    if ref_type == "action":
        if name.lower() in _ACTIONS:
            return f"{_RULES_GLOSSARY}{_pascal(name)}Action"
        return None
    base = _URL_BASES.get(ref_type)
    if not base:
        print(f"Warning: unknown reference type '{ref_type}'", file=sys.stderr)
        return None
    return f"{base}{_slugify(name)}"


def resolve_references_in_text(text: str) -> str:
    """Replace all {type:Name} references with HTML links.

    Unknown references render as styled spans without links.
    Broken DDB links (404) are acceptable — they never block rendering.
    """
    def _replace(match):
        ref_type = match.group(1)
        name = match.group(2)
        url = resolve_reference(ref_type, name)
        css_class = f"ref-{ref_type}"
        if url:
            return f'<a href="{url}" class="{css_class}">{name}</a>'
        print(f"Warning: could not resolve {{{ref_type}:{name}}}", file=sys.stderr)
        return f'<span class="{css_class}">{name}</span>'

    return _REF_PATTERN.sub(_replace, text)
