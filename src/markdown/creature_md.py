from src.utils.ability_modifier import ability_modifier
from src.markdown.children_md import (
    add_bulleted_list,
    add_paragraph,
    add_section_heading,
    add_table,
    add_divider,
    add_callout,
    add_numbered_list,
    add_quote,
)


def build_creature_markdown(creature: object) -> list:
    # ============================================
    # == Parse creature details
    # ============================================

    # == Speed
    # ==========
    parsed_speed = ", ".join(
        f"{movement.capitalize()}: {distance}"
        for movement, distance in creature.speed.items()
    )

    # == Armor parsing
    # ==========
    parsed_armor = []
    for armor in creature.armor_class:
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

    # == Proficencies
    # ==========
    saving_prof = []
    skill_prof = []
    for x in creature.proficiencies:
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

    # == Damage Resistances
    # ==========
    parsed_dam_res = []
    if parsed_dam_res := creature.damage_resistances:
        parsed_dam_res = " , ".join([x.capitalize() for x in parsed_dam_res])

    # == Damage Vulnerabilities
    # ==========
    parsed_dam_vul = []
    if parsed_dam_vul := list(creature.damage_vulnerabilities):
        parsed_dam_vul = " , ".join([x.capitalize() for x in parsed_dam_vul])

    # == Damage Immunities
    # ==========
    parsed_dam_imun = []
    if parsed_dam_imun := list(creature.damage_immunities):
        parsed_dam_imun = " , ".join([x.capitalize() for x in parsed_dam_imun])

    # == Condition Immunities
    # ===============
    parsed_con_imun = []
    if parsed_con_imun := [x["name"] for x in creature.condition_immunities]:
        parsed_con_imun = " , ".join(parsed_con_imun)

    # == Senses
    # ===============
    parsed_senses = [
        f"{key.replace("_", " ")}: {value}" for key, value in creature.senses.items()
    ]
    parsed_senses = " , ".join([x.capitalize() for x in parsed_senses])

    # == Special Abilities
    # ===============
    special_ability = []
    if creature.special_abilities:
        for x in creature.special_abilities:
            if x["name"].startswith("Spellcasting"):
                continue
            if x["name"] != ("Spellcasting"):
                special_ability.append(f'{x['name']} : {x["desc"]}')

    # == Spellcasting Abilitites
    # ===============
    spell_ability = []
    for x in creature.special_abilities or []:
        if x["name"].startswith("Spellcasting"):
            spell_ability = x["desc"]

    # == Actions
    # ===============
    actions = []
    if creature.actions:
        for x in creature.actions:
            actions.append(f"{x['name']}: {x["desc"]}")

    # == Legendary Actions
    # ===============
    legendary_action = []
    if creature.legendary_actions:
        for x in creature.legendary_actions:
            legendary_action.append(f"{x['name']}: {x["desc"]}")

    # =======================================================
    # == End of parse work
    # =======================================================
    # ==
    # =======================================================
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(markdown_children, f"{creature.name}", level=1)
    add_divider(markdown_children)
    add_paragraph(
        markdown_children,
        f"{creature.size.capitalize()} {creature.type.capitalize()} , {creature.alignment}",
    )
    add_divider(markdown_children)

    # == Basic info
    # ==========
    add_paragraph(
        markdown_children,
        f"Hit Points : {creature.hit_points} ( {creature.hit_points_roll} )",
    )
    add_paragraph(markdown_children, f"Armor Class : {parsed_armor}")
    add_paragraph(markdown_children, f"Speed : {parsed_speed}")
    add_divider(markdown_children)

    # == Attributes
    # ==========
    stats_table_headers = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    ]
    stats_table_row = [
        f"{(creature.strength)} ({ability_modifier(creature.strength)})",
        f"{str(creature.dexterity)} ({ability_modifier(creature.dexterity)})",
        f"{str(creature.constitution)} ({ability_modifier(creature.constitution)})",
        f"{str(creature.intelligence)} ({ability_modifier(creature.intelligence)})",
        f"{str(creature.wisdom)} ({ability_modifier(creature.wisdom)})",
        f"{str(creature.charisma)} ({ability_modifier(creature.charisma)})",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])
    add_divider(markdown_children)

    # == Proficiencies
    # ==========
    if saving_prof:
        add_paragraph(markdown_children, f"Saving proficiencies: {saving_prof}")

    if skill_prof:
        add_paragraph(markdown_children, f"Skill proficiencies: {skill_prof}")

    # == Resistances
    # ==========
    if parsed_dam_res:
        add_paragraph(markdown_children, f"Damage Resistances: {parsed_dam_res}")

    # == Vulnerabilities
    # ==========
    if parsed_dam_vul:
        add_paragraph(markdown_children, f"Damage Vulnerabilities: {parsed_dam_res}")

    # == Immunities
    # ==========
    if parsed_dam_imun:
        add_paragraph(markdown_children, f"Damage Immunity: {parsed_dam_imun}")

    if parsed_con_imun:
        add_paragraph(markdown_children, f"Condition Immunity: {parsed_con_imun}")

    # == Language and Senses
    # ==========
    if parsed_senses:
        add_paragraph(markdown_children, f"Senses: {parsed_senses}")
    add_paragraph(markdown_children, f"Language(s) : {creature.languages}")

    # == CR (XP) -- Prof Bonus
    # ==========
    add_paragraph(
        markdown_children,
        f"Challenge Rating: {creature.challenge_rating} ({creature.xp})    Proficiency Bonus: +{creature.proficiency_bonus}",
    )
    add_divider(markdown_children)

    # == Special Abilitites
    # ==========
    if special_ability:
        add_section_heading(markdown_children, "Abilitites", level=2)
        add_divider(markdown_children)
        for x in special_ability:
            add_paragraph(markdown_children, f"{x}")
        add_divider(markdown_children)

    # == Spellcasting
    # ==========
    if spell_ability:
        add_section_heading(markdown_children, "Spellcasting", level=2)
        add_divider(markdown_children)
        add_paragraph(markdown_children, spell_ability)
        add_divider(markdown_children)

    # == Actions
    # ==========
    if actions:
        add_section_heading(markdown_children, "Actions", level=2)
        add_divider(markdown_children)
        for x in actions:
            add_paragraph(markdown_children, f"{x}")
        add_divider(markdown_children)

    # == Legendary Actions
    # ==========
    if legendary_action:
        add_section_heading(markdown_children, "Legendary Actions", level=2)
        add_divider(markdown_children)
        for x in legendary_action:
            add_paragraph(markdown_children, f"{x}")
        add_divider(markdown_children)

    # == Description
    # ==========
    if creature.desc:
        add_section_heading(markdown_children, "Description", level=2)
        add_divider(markdown_children)
        add_paragraph(markdown_children, f"{creature.desc}")
        add_divider(markdown_children)

    return markdown_children
