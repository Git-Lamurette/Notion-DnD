from dataclasses import dataclass
from typing import Optional, List, Dict, Union
from uuid import uuid4


@dataclass
class _equipment:
    index: str
    name: str
    equipment_category: dict
    url: str
    cost: Dict[str, Union[int, str]]
    uid: str = uuid4().hex
    capacity: Optional[str] = None
    quantity: Optional[int] = None
    stealth_disadvantage: Optional[bool] = None
    armor_class: Optional[dict[dict]] = None
    str_minimum: Optional[str] = None
    armor_category: Optional[str] = None
    two_handed_damage: Optional[dict[str, Union[str, int]]] = None
    special: Optional[list[str]] = None
    gear_category: Optional[dict] = None
    tool_category: Optional[str] = None
    vehicle_category: Optional[str] = None
    weapon_category: Optional[str] = None
    weapon_range: Optional[str] = None
    category_range: Optional[str] = None
    damage: Optional[dict] = None
    range: Optional[dict] = None
    weight: Optional[int] = None
    properties: Optional[List[dict]] = None
    throw_range: Optional[dict] = None
    contents: Optional[List[dict]] = None
    desc: Optional[List[str]] = None
    speed: Optional[Dict[str, Union[int, float, str]]] = None

    def get_damage_dice(self) -> str:
        if self.damage:
            return self.damage["damage_dice"]
        return "No Damage Info"
