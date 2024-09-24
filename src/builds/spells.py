from src.classes.spells_class import _spell
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import Client


def build_spells_database(logger, notion, data_directory, json_file, args):
    spells_db_id = spells_db(logger, notion, args.database_id)
    spells_page(
        logger,
        notion,
        data_directory,
        json_file,
        spells_db_id,
        args.start_range,
        args.end_range,
    )


def spells_page(
    logger: "logging.Logger",
    notion: "Client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each spells in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get spells Data
    spells_data = load_data(logger, data_directory, json_file)

    # == Apply range to spells data
    if end is None or end > len(spells_data):
        end = len(spells_data)

    # == Iterates through the specified range of the spells JSON
    for index in range(start, end):
        x = spells_data[index]

        # == Makes the spells as a data class
        spells = _spell(**x)

        logger.info(
            f"Building Markdown for spells -- {spells.name} -- Index -- {index} --"
        )

        # == Building markdown properties from _spells class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": spells.name},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Spells"}},
            "URL": {"url": f"https://www.dndbeyond.com/spells/{spells.index}"},
            "Level": {
                "select": {
                    "name": str(spells.level) if spells.level != 0 else "Cantrip"
                }
            },
            "School": {"select": {"name": spells.school.get("name").capitalize()}},
            "Casting Time": {"multi_select": [{"name": spells.casting_time}]},
            "Range": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": spells.range},
                    }
                ]
            },
            "Components": {
                "multi_select": [
                    {"name": component.capitalize()}
                    for component in spells.components or []
                ]
            },
            "Duration": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": spells.duration},
                    }
                ]
            },
            "Concentration": {"checkbox": spells.concentration},
            "Ritual": {"checkbox": spells.ritual},
            "Classes and Subclasses": {
                "multi_select": [
                    {"name": cls["name"].capitalize()}
                    for cls in spells.classes + spells.subclasses
                ]
            },
        }

        if spells.material:
            markdown_properties["Materials"] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": spells.material},
                    }
                ]
            }
        if spells.attack_type:
            markdown_properties["Attack Type"] = {
                "select": {
                    "name": spells.attack_type.capitalize()
                    if spells.attack_type
                    else ""
                }
            }

        if spells.damage and spells.damage.get("damage_type"):
            markdown_properties["Damage Type"] = {
                "select": {"name": spells.damage["damage_type"]["name"].capitalize()}
            }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for spells
        children_properties = build_spells_markdown(
            spells,
            notion,
            logger,
            database_id,
        )
        # == Sending api call
        # ==========
        create_page(
            logger,
            notion,
            database_id,
            markdown_properties,
            children_properties,
        )

        sleep(0.5)


def spells_db(logger: "logging.Logger", notion: "Client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Spells"

    # == Building markdown database properties
    database_spells_properties = {
        "Name": {"title": {}},
        "Range": {"rich_text": {}},
        "URL": {"url": {}},
        "5E Category": {"select": {"options": [{"name": "Spells", "color": "green"}]}},
        "Components": {
            "multi_select": {
                "options": [
                    {"name": "M", "color": "blue"},
                    {"name": "S", "color": "green"},
                    {"name": "V", "color": "red"},
                ]
            }
        },
        "Materials": {"rich_text": {}},
        "Ritual": {"checkbox": {}},
        "Duration": {"rich_text": {}},
        "Concentration": {"checkbox": {}},
        "Casting Time": {
            "multi_select": {
                "options": [
                    {"name": "1 action", "color": "yellow"},
                    {"name": "1 bonus action", "color": "purple"},
                    {"name": "1 hour", "color": "pink"},
                    {"name": "1 minute", "color": "orange"},
                    {"name": "1 reaction", "color": "brown"},
                    {"name": "10 minutes", "color": "gray"},
                    {"name": "12 hours", "color": "blue"},
                    {"name": "24 hours", "color": "green"},
                    {"name": "8 hours", "color": "red"},
                ]
            }
        },
        "Level": {
            "select": {
                "options": [
                    {"name": "Cantrip", "color": "blue"},
                    {"name": "1", "color": "green"},
                    {"name": "2", "color": "red"},
                    {"name": "3", "color": "yellow"},
                    {"name": "4", "color": "purple"},
                    {"name": "5", "color": "pink"},
                    {"name": "6", "color": "orange"},
                    {"name": "7", "color": "brown"},
                    {"name": "8", "color": "gray"},
                    {"name": "9", "color": "blue"},
                ]
            }
        },
        "Attack Type": {
            "select": {
                "options": [
                    {"name": "Melee", "color": "green"},
                    {"name": "Range", "color": "red"},
                ]
            }
        },
        "Damage Type": {
            "select": {
                "options": [
                    {"name": "Acid", "color": "blue"},
                    {"name": "Bludgeoning", "color": "green"},
                    {"name": "Cold", "color": "red"},
                    {"name": "Fire", "color": "yellow"},
                    {"name": "Force", "color": "purple"},
                    {"name": "Lightning", "color": "pink"},
                    {"name": "Necrotic", "color": "orange"},
                    {"name": "Piercing", "color": "brown"},
                    {"name": "Poison", "color": "gray"},
                    {"name": "Psychic", "color": "blue"},
                    {"name": "Radiant", "color": "green"},
                    {"name": "Slashing", "color": "red"},
                    {"name": "Thunder", "color": "yellow"},
                ]
            }
        },
        "School": {
            "select": {
                "options": [
                    {"name": "Abjuration", "color": "blue"},
                    {"name": "Conjuration", "color": "green"},
                    {"name": "Divination", "color": "red"},
                    {"name": "Enchantment", "color": "yellow"},
                    {"name": "Evocation", "color": "purple"},
                    {"name": "Illusion", "color": "pink"},
                    {"name": "Necromancy", "color": "orange"},
                    {"name": "Transmutation", "color": "brown"},
                ]
            }
        },
        "Classes and Subclasses": {
            "multi_select": {
                "options": [
                    {"name": "Bard", "color": "blue"},
                    {"name": "Cleric", "color": "green"},
                    {"name": "Druid", "color": "red"},
                    {"name": "Paladin", "color": "yellow"},
                    {"name": "Ranger", "color": "purple"},
                    {"name": "Sorcerer", "color": "pink"},
                    {"name": "Warlock", "color": "orange"},
                    {"name": "Wizard", "color": "brown"},
                    {"name": "Devotion", "color": "brown"},
                    {"name": "Fiend", "color": "gray"},
                    {"name": "Land", "color": "blue"},
                    {"name": "Life", "color": "green"},
                    {"name": "Lore", "color": "red"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_spells_properties
    )


def build_spells_markdown(
    spell: _spell, notion: "Client", logger: "logging.Logger", database_id: str
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
        add_divider,
    )
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(
        markdown_children,
        f"{spell.name}",
        level=1,
    )

    stats_table_headers = [
        "Level",
        "Casting Time",
        "Range/Area",
        "Components",
    ]

    stats_table_row = [
        f"{str(spell.level) if spell.level != 0 else "Cantrip"}",
        f"{spell.casting_time}",
        f"{spell.range}{f' ({spell.area_of_effect["size"]} ft. {spell.area_of_effect["type"].capitalize()})' if spell.area_of_effect else ''}",
        f"{', '.join(spell.components)}{' *' if spell.material else ''}",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])

    stats_table_headers = [
        "Duration",
        "School",
        "Attack/Save",
        "Damage/Effect",
    ]

    stats_table_row = [
        f"{spell.duration}",
        f"{spell.school['name']}",
        f"{spell.get_attack_spell_save()}",
        f"{spell.get_damage_effect()}",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])

    if spell.desc:
        add_section_heading(markdown_children, "Description", level=3)
        add_divider(markdown_children)
        for line in spell.desc:
            add_paragraph(markdown_children, f"{line}")

    if spell.higher_level:
        add_section_heading(markdown_children, "At Higher Levels", level=3)
        add_divider(markdown_children)
        for line in spell.higher_level:
            add_paragraph(markdown_children, f"{line}")

    if spell.material:
        add_divider(markdown_children)
        add_paragraph(markdown_children, f" * ({spell.material})")

    return markdown_children
