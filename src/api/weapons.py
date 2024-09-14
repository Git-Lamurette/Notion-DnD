from src.classes.equipment_class import _equipment
from src.markdown.weapons_md import build_weapon_markdown
from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def weapons_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each equipment in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get equipment Data
    equipment_data = load_data(logger, data_directory, "5e-SRD-Equipment.json")

    # == Apply range to equipment data
    if end is None or end > len(equipment_data):
        end = len(equipment_data)

    # == Iterates through the specified range of the equipment JSON
    for index in range(start, end):
        x = equipment_data[index]

        # == Makes the equipment as a data class
        equipment = _equipment(**x)

        if equipment.equipment_category["index"] == "weapon":
            logger.info(
                f"Building Markdown for equipment -- {equipment.name} -- Index -- {index} --"
            )

            # == Building markdown properties from _equipment class
            markdown_properties = {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": equipment.name},
                        }
                    ]
                },
                "URL": {
                    "url": f"https://www.dndbeyond.com/equipment/{equipment.index}"
                },
                "Category": {
                    "select": {
                        "name": equipment.equipment_category.get(
                            "name", "Unknown Category"
                        ).capitalize()
                    }
                },
                "Cost": {
                    "rich_text": [
                        {"type": "text", "text": {"content": equipment.get_cost()}}
                    ]
                },
                "Range": {
                    "rich_text": [
                        {"type": "text", "text": {"content": equipment.get_range()}}
                    ]
                },
                "Range - Thrown": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": equipment.get_range_thrown()},
                        }
                    ]
                },
                "Type": {"multi_select": [{"name": equipment.category_range}]},
                "Damage": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": equipment.get_damage_dice()},
                        }
                    ]
                },
                "Damage Type": {
                    "multi_select": [{"name": equipment.get_damage_type()}]
                },
                "Damage - Two Handed": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": equipment.get_two_handed_damage()},
                        }
                    ]
                },
                "Properties": {
                    "multi_select": [
                        {"name": prop} for prop in equipment.get_properties()
                    ]
                },
                "Weight": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"{equipment.weight} lbs"},
                        }
                    ]
                },
            }

            # == Ensure children_properties list is empty
            children_properties = []

            # == Building markdown for equipment
            children_properties = build_weapon_markdown(equipment)

            # == Sending api call
            # ==========
            create_page(
                logger, notion, database_id, markdown_properties, children_properties
            )

            sleep(0.5)


def weapons_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Weapons"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "URL": {"url": {}},
        "Category": {
            "select": {
                "options": [
                    {"name": "Adventuring Gear", "color": "gray"},
                    {"name": "Armor", "color": "green"},
                    {"name": "Weapons", "color": "yellow"},
                    {"name": "Tools", "color": "blue"},
                    {"name": "Mounts and Vehicles", "color": "red"},
                    {"name": "Magic Items", "color": "orange"},
                    {"name": "Food and Drink", "color": "pink"},
                    {"name": "Trade Goods", "color": "purple"},
                    {"name": "Special Gear", "color": "brown"},
                ]
            }
        },
        "Cost": {"rich_text": {}},
        "Range": {"rich_text": {}},
        "Range - Thrown": {"rich_text": {}},
        "Type": {
            "multi_select": {
                "options": [
                    {"name": "Simple Melee", "color": "blue"},
                    {"name": "Simple Ranged", "color": "green"},
                    {"name": "Martial Melee", "color": "yellow"},
                    {"name": "Martial Ranged", "color": "orange"},
                ]
            }
        },
        "Damage": {"rich_text": {}},
        "Damage Type": {
            "multi_select": {
                "options": [
                    {"name": "Bludgeoning", "color": "gray"},
                    {"name": "Piercing", "color": "red"},
                    {"name": "Slashing", "color": "blue"},
                    {"name": "Fire", "color": "orange"},
                    {"name": "Cold", "color": "blue"},
                    {"name": "Lightning", "color": "yellow"},
                    {"name": "Thunder", "color": "purple"},
                    {"name": "Poison", "color": "green"},
                    {"name": "Acid", "color": "brown"},
                    {"name": "Psychic", "color": "pink"},
                    {"name": "Radiant", "color": "yellow"},
                    {"name": "Necrotic", "color": "default"},
                ]
            }
        },
        "Damage - Two Handed": {"rich_text": {}},
        "Properties": {
            "multi_select": {
                "options": [
                    {"name": "Finesse", "color": "blue"},
                    {"name": "Heavy", "color": "green"},
                    {"name": "Light", "color": "yellow"},
                    {"name": "Thrown", "color": "orange"},
                    {"name": "Two-Handed", "color": "pink"},
                    {"name": "Versatile", "color": "purple"},
                ]
            }
        },
        "Weight": {"rich_text": {}},
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )