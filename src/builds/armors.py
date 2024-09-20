from src.classes.equipment_class import _equipment
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import Union
from time import sleep
import logging
from notion_client import Client


async def build_armors_database(logger, notion, data_directory, json_file, args):
    armors_db_id = await armor_db(logger, notion, args.database_id)
    await armor_page(
        logger,
        notion,
        data_directory,
        json_file,
        armors_db_id,
        args.start_range,
        args.end_range,
    )


async def armor_page(
    logger: logging.Logger,
    notion: Client,
    data_directory: str,
    json_file: str,
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
    equipment_data = load_data(logger, data_directory, json_file)

    if not isinstance(equipment_data, (list, dict)):
        logger.error("Loaded data is not a list or dictionary")
        return

    # == Apply range to equipment data
    if end is None or end > len(equipment_data):
        end = len(equipment_data)

    # == Iterates through the specified range of the equipment JSON
    for index in range(start, end):
        x = equipment_data[index]

        # == Makes the equipment as a data class
        equipment = _equipment(**x)

        if equipment.equipment_category["index"] == "armor":
            logger.info(
                f"Building Markdown for equipment -- {equipment.name} -- Index -- {index} --"
            )

            # == Building markdown properties from _equipment class
            markdown_properties = {
                "Name": {"title": [{"text": {"content": equipment.name}}]},
                "URL": {
                    "url": f"https://www.dndbeyond.com/equipment/{equipment.index.strip("-armor")}"
                },
                "Category": {"select": {"name": equipment.equipment_category["name"]}},
                "Cost": {"rich_text": [{"text": {"content": equipment.get_cost()}}]},
                "Weight": {
                    "rich_text": [{"text": {"content": f"{equipment.weight} lbs"}}]
                },
                "Type": {"multi_select": [{"name": equipment.armor_category}]},
                "Armor Class": {
                    "rich_text": [{"text": {"content": equipment.get_armor_class()}}]
                },
                "Strength Requirement": {
                    "number": equipment.get_strength_requirement()
                },
                "Stealth Disadvantage": {"checkbox": equipment.stealth_disadvantage},
            }

            # == Ensure children_properties list is empty
            children_properties = []

            # == Building markdown for equipment
            children_properties = build_armor_markdown(equipment)

            # == Sending api call
            # ==========
            await create_page(
                logger,
                notion,
                database_id,
                markdown_properties,
                children_properties,
            )

            sleep(0.5)


async def armor_db(logger: "logging.Logger", notion: "Client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Armor"

    # == Building markdown database properties
    database_armor_properties = {
        "Name": {"title": {}},
        "URL": {"url": {}},
        "Category": {
            "select": {
                "options": [
                    {"name": "Armor", "color": "green"},
                ]
            }
        },
        "Cost": {"rich_text": {}},
        "Weight": {"rich_text": {}},
        "Type": {
            "multi_select": {
                "options": [
                    {"name": "Light Armor", "color": "gray"},
                    {"name": "Medium Armor", "color": "green"},
                    {"name": "Heavy Armor", "color": "yellow"},
                    {"name": "Shield", "color": "blue"},
                ]
            }
        },
        "Armor Class": {"rich_text": {}},
        "Strength Requirement": {"number": {}},
        "Stealth Disadvantage": {"checkbox": {}},
    }
    database_id = await create_database(
        logger, notion, database_id, database_name, database_armor_properties
    )

    return database_id


def build_armor_markdown(equipment: _equipment) -> list:
    from src.builds.children_md import (
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
    add_section_heading(markdown_children, f"{equipment.name}", level=1)

    headers = [
        f"Type: {equipment.armor_category}",
        f"Cost: {equipment.cost['quantity']} {equipment.cost['unit']}",
        f"Weight: {equipment.get_weight()}",
    ]
    add_table(markdown_children, headers)
    add_divider(markdown_children)

    # == Attributes
    # ==========
    stats_table_headers = [
        "Name",
        "Cost",
        "Armor Class",
        "Strength",
        "Stealth",
        "Weight",
    ]
    stats_table_row = [
        f"{equipment.name}",
        f"{equipment.cost['quantity']} {equipment.cost['unit']}",
        f"{equipment.get_armor_class()}",
        f"{' -- ' if equipment.get_strength_requirement() == 0 else equipment.get_strength_requirement()}",
        f"{' -- ' if not equipment.stealth_disadvantage else "Disadvantage"}",
        f"{equipment.weight} lbs",
    ]
    add_table(
        markdown_children,
        stats_table_headers,
        [stats_table_row],
    )

    return markdown_children
