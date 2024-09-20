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

    # == Speed
    # ==========
    def get_speed(self) -> str:
        parsed_speed = ", ".join(
            f"{movement.capitalize()}: {distance}"
            for movement, distance in self.speed.items()
        )
        return parsed_speed

    # == Armor parsing
    # ==========
    def get_armor(self) -> str:
        parsed_armor = []
        for armor in self.armor_class:
            if "spell" in armor:
                parsed_armor.append(
                    f"{armor['type'].capitalize()} {armor['value']} : {armor['spell']['name']}"
                )
            elif "condition" in armor:
                parsed_armor.append(
                    f"{armor['type'].capitalize()} {armor['value']} : {armor['condition']['name']}"
                )
            elif "armor" in armor:
                for x in armor["armor"]:
                    parsed_armor.append(
                        f"{armor['type'].capitalize()} {armor['value']} : {x['name']}"
                    )
            else:
                parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']}")

        parsed_armor = " - ".join(parsed_armor)
        return parsed_armor

    # == Proficencies
    # ==========
    def get_proficencies(self) -> tuple[str, str]:
        saving_prof = []
        skill_prof = []
        for x in self.proficiencies:
            name = x["proficiency"]["name"]
            if name.startswith("Skill"):
                name = name.removeprefix("Skill: ")
                skill_prof.append(f"{name} +{x["value"]}")
            if name.startswith("Saving Throw"):
                name = name.removeprefix("Saving Throw: ")
                saving_prof.append(f"{name} +{x["value"]}")

        if saving_prof:
            saving_prof = " , ".join(saving_prof)

        if skill_prof:
            skill_prof = " , ".join(skill_prof)

        return saving_prof, skill_prof

    # == Damage Resistances
    # ==========
    def get_damage_resistances(self) -> str:
        parsed_dam_res = []
        if parsed_dam_res := self.damage_resistances:
            parsed_dam_res = " , ".join([x.capitalize() for x in parsed_dam_res])
        return parsed_dam_res

    # == Damage Vulnerabilities
    # ==========
    def get_damage_vulnerabilities(self) -> str:
        parsed_dam_vul = []
        if parsed_dam_vul := self.damage_vulnerabilities:
            parsed_dam_vul = " , ".join([x.capitalize() for x in parsed_dam_vul])
        return parsed_dam_vul

    # == Damage Immunities
    # ==========
    def get_damage_immunities(self) -> list:
        parsed_dam_imun = []
        if parsed_dam_imun := self.damage_immunities:
            parsed_dam_imun = " , ".join([x.capitalize() for x in parsed_dam_imun])
        return parsed_dam_imun

    # == Condition Immunities
    # ===============
    def get_condition_immunities(self) -> str:
        parsed_con_imun = []
        if parsed_con_imun := [x["name"] for x in self.condition_immunities]:
            parsed_con_imun = " , ".join(parsed_con_imun)
        return parsed_con_imun

    # == Senses
    # ===============
    def get_senses(self) -> str:
        parsed_senses = [
            f"{key.replace("_", " ")}: {value}" for key, value in self.senses.items()
        ]
        parsed_senses = " , ".join([x.capitalize() for x in parsed_senses])
        return parsed_senses

    # == Special Abilities
    # ===============
    def get_special_abilities(self) -> list[str]:
        special_ability = []
        if self.special_abilities:
            for x in self.special_abilities:
                if x["name"].startswith("Spellcasting"):
                    continue
                if x["name"] != ("Spellcasting"):
                    special_ability.append(f'{x['name']} : {x["desc"]}')
        return special_ability

    # == Spellcasting Abilitites
    # ===============
    def get_spellcasting(self) -> list[str]:
        spell_ability = []
        for x in self.special_abilities or []:
            if x["name"].startswith("Spellcasting"):
                spell_ability = x["desc"]
        return spell_ability

    # == Actions
    # ===============
    def get_actions(self) -> list[str]:
        actions = []
        if self.actions:
            for x in self.actions:
                actions.append(f"{x['name']}: {x["desc"]}")
        return actions

    # == Legendary Actions
    # ===============
    def get_legendary_actions(self) -> list[str]:
        legendary_action = []
        if self.legendary_actions:
            for x in self.legendary_actions:
                legendary_action.append(f"{x['name']}: {x["desc"]}")
        return legendary_action
