from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class _spell:
    area_of_effect: Optional[Dict[str, int]] = None
    attack_type: Optional[str] = None
    casting_time: Optional[str] = None
    classes: Optional[List[str]] = None
    components: Optional[List[str]] = None
    concentration: Optional[bool] = None
    damage: Optional[Dict[str, Dict[str, str]]] = None
    dc: Optional[Dict[str, str]] = None
    desc: Optional[List[str]] = None
    duration: Optional[str] = None
    heal_at_slot_level: Optional[Dict[str, str]] = None
    higher_level: Optional[List[str]] = None
    index: Optional[str] = None
    level: Optional[int] = None
    material: Optional[str] = None
    name: Optional[str] = None
    range: Optional[str] = None
    ritual: Optional[bool] = None
    school: Optional[str] = None
    subclasses: Optional[List[str]] = None
    url: Optional[str] = None

    def get_attack_spell_save(self) -> str:
        if self.attack_type:
            return self.attack_type.capitalize()
        if isinstance(self.dc, dict) and isinstance(self.dc.get("dc_type"), dict):
            dc_type = self.dc.get("dc_type", {})
            if isinstance(dc_type, dict):
                return f"{dc_type.get('name')} Save"
        return "None"

    def get_damage_effect(self) -> str:
        if self.damage and self.damage.get("damage_type"):
            return f"{self.damage["damage_type"]["name"].capitalize()}"
        else:
            return "None"

    def classes_and_subclasses(self) -> list:
        classes_and_subclasses = []
        for cls in (self.classes or []) + (self.subclasses or []):
            if isinstance(cls, dict) and isinstance(cls.get("name"), str):
                classes_and_subclasses.append(
                    {"name": cls.get("name", "").capitalize()}
                )
        return classes_and_subclasses