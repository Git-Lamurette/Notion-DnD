from src.classes.spells_class import _spell
from src.markdown.spells_md import build_spells_markdown
from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def spells_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
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
    spells_data = load_data(logger, data_directory, "5e-SRD-Spells.json")

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
            "URL": {"url": f"https://www.dndbeyond.com/spells/{spells.index}"},
            "Level": {
                "select": {
                    "name": str(spells.level) if spells.level != 0 else "Cantrip"
                }
            },
            "School": {"select": {"name": spells.school.get("name", "Unknown School")}},
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
                    {"name": component.capitalize()} for component in spells.components
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


def spells_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
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
