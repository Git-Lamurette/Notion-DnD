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
            return self.damage.get("damage_dice", "")
        return "0"

    def get_two_handed_damage(self) -> str:
        if self.two_handed_damage:
            return self.two_handed_damage.get("damage_dice", "")
        return ""

    def get_cost(self) -> str:
        return f"{self.cost.get('quantity', '')} {self.cost.get('unit', '')}"

    def get_range(self) -> str:
        return "\n".join(
            f"{key.capitalize()} - {value}"
            for key, value in self.range.items()
            if key in ["normal", "long"]
        )

    def get_range_thrown(self) -> str:
        if self.throw_range:
            return " - ".join(
                f"{key.capitalize()} - {value}"
                for key, value in self.throw_range.items()
                if key in ["normal", "long"]
            )
        return ""

    def get_damage_type(self) -> str:
        if self.damage:
            return (
                self.damage.get("damage_type", {}).get("index", "Unknown").capitalize()
            )
        return "None"

    def get_properties(self) -> List[str]:
        return [prop["name"].capitalize() for prop in self.properties]

    def get_armor_class(self) -> str:
        if self.armor_class["dex_bonus"]:
            max_bonus = self.armor_class.get("max_bonus", None)
            if max_bonus:
                return f"{self.armor_class.get('base', 0)} + Dex Modifier (Max {self.armor_class['max_bonus']})"
            else:
                return f"{self.armor_class.get('base', 0)} + Dex Modifier"
        if self.armor_class:
            return f"{self.armor_class.get("base", 0)}"

        return "0"

    def get_strength_requirement(self) -> int:
        if self.str_minimum:
            return self.str_minimum
        return 0

    def get_equipment_category(self) -> str:
        if self.equipment_category["name"] == "Tools":
            return self.tool_category
        if self.equipment_category["name"] == "Mounts and Vehicles":
            return self.vehicle_category.replace(",", " -")
        if self.equipment_category["name"] == "Adventuring Gear":
            return self.gear_category["name"]
        return " -- "

    def get_weight(self) -> int:
        if self.weight:
            return f"{self.weight} lbs"
        return " -- "
