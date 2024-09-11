"""Found from someone smarter than me online, idk if I want to keept it or not"""

from dataclasses import dataclass
from typing import Optional, Union
from uuid import uuid4


@dataclass(kw_only=True)
class _Creature:
    index: str
    uid: str = uuid4().hex
    type: str
    subtype: Optional[str] = None
    desc: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    url: str
    name: str
    size: str
    alignment: str
    armor_class: list[dict[str, Union[str, int]]]
    hit_points: int
    hit_dice: str
    hit_points_roll: str
    speed: dict[str, str]
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    proficiency_bonus: int
    proficiencies: list[dict[str, Union[str, dict[str, str]]]]
    damage_vulnerabilities: list[str]
    damage_resistances: list[str]
    damage_immunities: list[str]
    condition_immunities: list[dict[str, str]]
    senses: dict[str, Union[str, int]]
    languages: str
    challenge_rating: float
    xp: int
    special_abilities: Optional[list[dict[str, str]]] = None
    legendary_actions: Optional[list[dict[str, str]]] = None
    actions: Optional[list[dict]] = None
    reactions: Optional[list[dict]] = None
    forms: Optional[list[dict[str, str]]] = None
