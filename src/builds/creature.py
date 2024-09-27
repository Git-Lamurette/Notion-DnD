from src.classes.creature_class import _Creature
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_creature_database(logger, notion, data_directory, json_file, args):
    creature_db_id = creature_db(logger, notion, args.database_id)
    creature_page(
        logger,
        notion,
        data_directory,
        json_file,
        creature_db_id,
        args.start_range,
        args.end_range,
    )


def creature_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each creature in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get Monster Data
    creature_data = load_data(logger, data_directory, json_file)

    # == Apply range to creature data
    if end is None or end > len(creature_data):
        end = len(creature_data)

    # == Iterates through the specified range of the monster JSON
    for index in range(start, end):
        x = creature_data[index]

        # == Makes the creature as a data class
        monster = _Creature(**x)

        logger.info(
            f"Building Markdown for Creature -- {monster.name} -- Index -- {index} --"
        )

        # == Building markdown properties from _Creature class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": monster.name},
                    }
                ]
            },
            "URL": {"url": f"https://www.dndbeyond.com/monsters/{monster.index}"},
            "Size": {"select": {"name": monster.size.capitalize()}},
            "Type": {"select": {"name": monster.type.capitalize()}},
            "CR": {"number": monster.challenge_rating},
            "Hit Points": {"number": monster.hit_points},
            "Movement Type": {
                "multi_select": [{"name": mt.capitalize()} for mt in monster.speed]
            },
            "5E Category": {"select": {"name": "Creatures"}},
        }

        # == Ensure children list is empty
        children_properties = []

        # == Building markdown for creature
        children_properties = build_creature_markdown(monster)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def creature_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just bulds the empty database page with the required options.

    Args:
        logger (logging.Logger): _description_
        notion (client): _description_
        database_id (str): _description_

    Returns:
        str: _description_
    """
    # == Database Name
    database_name = "Creatures"

    # == Building markdown database properties
    database_properties = {
        "Name": {"title": {}},
        "URL": {"url": {}},
        "5E Category": {
            "select": {"options": [{"name": "Creatures", "color": "green"}]}
        },
        "Size": {
            "select": {
                "options": [
                    {"name": "Tiny", "color": "pink"},
                    {"name": "Small", "color": "purple"},
                    {"name": "Medium", "color": "blue"},
                    {"name": "Large", "color": "green"},
                    {"name": "Huge", "color": "yellow"},
                    {"name": "Gargantuan", "color": "red"},
                ]
            }
        },
        "Type": {
            "select": {
                "options": [
                    {"name": "Aberration", "color": "gray"},
                    {"name": "Beast", "color": "green"},
                    {"name": "Celestial", "color": "yellow"},
                    {"name": "Construct", "color": "blue"},
                    {"name": "Dragon", "color": "red"},
                    {"name": "Elemental", "color": "orange"},
                    {"name": "Fey", "color": "pink"},
                    {"name": "Fiend", "color": "purple"},
                    {"name": "Giant", "color": "brown"},
                    {"name": "Humanoid", "color": "blue"},
                    {"name": "Monstrosity", "color": "red"},
                    {"name": "Ooze", "color": "gray"},
                    {"name": "Plant", "color": "green"},
                    {"name": "Undead", "color": "gray"},  # Fixed color
                ]
            }
        },
        "CR": {"number": {}},
        "Hit Points": {"number": {}},
        "Movement Type": {
            "multi_select": {
                "options": [
                    {"name": "Walk", "color": "blue"},
                    {"name": "Fly", "color": "purple"},
                    {"name": "Swim", "color": "green"},
                    {"name": "Climb", "color": "yellow"},
                    {"name": "Burrow", "color": "brown"},
                    {"name": "Hover", "color": "pink"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_properties
    )


def build_creature_markdown(creature: object) -> list:
    from src.utils.ability_modifier import ability_modifier
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
        add_divider,
    )

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
    add_paragraph(markdown_children, f"Armor Class : {creature.get_armor()}")
    add_paragraph(markdown_children, f"Speed : {creature.get_speed()}")

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

    # == Proficiencies
    # ==========
    saving_profs, skill_prof = creature.get_proficencies()

    if saving_profs:
        add_paragraph(markdown_children, f"Saving proficiencies: {saving_profs}")

    if skill_prof:
        add_paragraph(markdown_children, f"Skill proficiencies: {skill_prof}")

    # == Resistances
    # ==========
    parsed_dam_res = creature.get_damage_resistances()
    if parsed_dam_res:
        add_paragraph(markdown_children, f"Damage Resistances: {parsed_dam_res}")

    # == Vulnerabilities
    # ==========
    parsed_dam_vul = creature.get_damage_vulnerabilities()
    if parsed_dam_vul:
        add_paragraph(markdown_children, f"Damage Vulnerabilities: {parsed_dam_vul}")

    # == Immunities
    # ==========
    parsed_dam_imun = creature.get_damage_immunities()
    if parsed_dam_imun:
        add_paragraph(markdown_children, f"Damage Immunity: {parsed_dam_imun}")

    parsed_con_imun = creature.get_condition_immunities()
    if parsed_con_imun:
        add_paragraph(markdown_children, f"Condition Immunity: {parsed_con_imun}")

    # == Language and Senses
    # ==========
    parsed_senses = creature.get_senses()
    if parsed_senses:
        add_paragraph(markdown_children, f"Senses: {parsed_senses}")

    add_paragraph(markdown_children, f"Language(s) : {creature.languages}")

    # == CR (XP) -- Prof Bonus
    # ==========
    add_paragraph(
        markdown_children,
        f"Challenge Rating: {creature.challenge_rating} ({creature.xp})    Proficiency Bonus: +{creature.proficiency_bonus}",
    )

    # == Special Abilities
    # ==========
    special_ability = creature.get_special_abilities()
    if special_ability:
        add_section_heading(markdown_children, "Abilities", level=3)
        add_divider(markdown_children)
        for x in special_ability:
            add_paragraph(markdown_children, f"{x}")

    # == Spellcasting
    # ==========
    spell_ability = creature.get_spellcasting()
    if spell_ability:
        add_section_heading(markdown_children, "Spellcasting", level=3)
        add_divider(markdown_children)
        add_paragraph(markdown_children, spell_ability)

    # == Actions
    # ==========
    actions = creature.get_actions()
    if actions:
        add_section_heading(markdown_children, "Actions", level=3)
        add_divider(markdown_children)
        for x in actions:
            add_paragraph(markdown_children, f"{x}")

    # == Legendary Actions
    # ==========
    legendary_action = creature.get_legendary_actions()
    if legendary_action:
        add_section_heading(markdown_children, "Legendary Actions", level=3)
        add_divider(markdown_children)
        for x in legendary_action:
            add_paragraph(markdown_children, f"{x}")

    # == Description
    # ==========
    if creature.desc:
        add_section_heading(markdown_children, "Description", level=3)
        add_divider(markdown_children)
        add_paragraph(markdown_children, f"{creature.desc}")

    return markdown_children
