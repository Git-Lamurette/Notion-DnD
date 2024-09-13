from src.classes.equipment_class import _equipment
from src.markdown.equipment_md import build_equipment_markdown
from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def equipment_page(
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
            "Category": {
                "select": {
                    "name": equipment.equipment_category.get(
                        "name", "Unknown Category"
                    ).capitalize()
                }
            },
            "Cost Number": {"number": equipment.cost.get("quantity", None)},
            "Cost Unit": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": equipment.cost.get("unit", "Unknown Unit")},
                    }
                ]
            },
            "Weight": {"number": equipment.weight},
            "Damage": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": equipment.get_damage_dice()},
                    }
                ]
            },
            "Properties": {
                "multi_select": [
                    {"name": prop.get("name", "").capitalize()}
                    for prop in (equipment.properties or [])
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for equipment
        children_properties = build_equipment_markdown(equipment)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )
        logger.info(f"Page created for {equipment.name}")
        sleep(0.5)


def equipment_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just bulds the empty database page with the required options.

    Args:
        logger (logging.Logger): _description_
        notion (client): _description_
        database_id (str): _description_

    Returns:
        str: _description_
    """

    # == Database Name
    database_name = "Weapons"

    # == Building markdown database properties
    database_properties = {
        "Name": {"title": {}},
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
        "Cost Number": {"number": {}},
        "Cost Unit": {"rich_text": {}},
        "Weight": {"number": {}},
        "Damage": {"rich_text": {}},
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
    }

    create_database(logger, notion, database_id, database_name, database_properties)
