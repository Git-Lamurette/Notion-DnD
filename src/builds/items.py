from src.classes.equipment_class import _equipment
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import Union
from time import sleep
import logging
from notion_client import Client


def build_items_database(logger, notion, data_directory, json_file, args):
    items_db_id = items_db(logger, notion, args.database_id)
    items_page(
        logger,
        notion,
        data_directory,
        json_file,
        items_db_id,
        args.start_range,
        args.end_range,
    )


def items_page(
    logger: logging.Logger,
    notion: Client,
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each items in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get items Data
    items_data = load_data(logger, data_directory, json_file)

    # == Apply range to items data
    if end is None or end > len(items_data):
        end = len(items_data)

    # == Iterates through the specified range of the items JSON
    for index in range(start, end):
        x = items_data[index]

        # == Makes the items as a data class
        items = _equipment(**x)

        if (
            items.equipment_category["index"] != "armor"
            and items.equipment_category["index"] != "weapon"
        ):
            logger.info(
                f"Building Markdown for items -- {items.name} -- Index -- {index} --"
            )

            # == Building markdown properties from _items class
            markdown_properties = {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": items.name},
                        }
                    ]
                },
                "URL": {
                    "url": f"https://www.dndbeyond.com/equipment/{items.index.split("-")[0].strip()}"
                },
                "Category": {
                    "select": {
                        "name": items.equipment_category.get("name", "Unknown Category")
                    }
                },
                "Gear Category": {
                    "select": {"name": f"{items.get_equipment_category()}"}
                },
                "Cost": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"{items.cost.get('quantity', 'Unknown')} {items.cost.get('unit', 'Unknown Unit')}"
                            },
                        }
                    ]
                },
                "Weight": {"number": items.weight},
            }

            # == Ensure children_properties list is empty
            children_properties = []

            # == Building markdown for items
            children_properties = build_items_markdown(
                items,
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


def items_db(logger: logging.Logger, notion: Client, database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Items"

    # == Building markdown database properties
    database_items_properties = {
        "Name": {"title": {}},
        "URL": {"url": {}},
        "Category": {
            "select": {
                "options": [
                    {"name": "Adventuring Gear", "color": "gray"},
                    {"name": "Tools", "color": "blue"},
                    {"name": "Mounts and Vehicles", "color": "red"},
                    {"name": "Food and Drink", "color": "pink"},
                    {"name": "Trade Goods", "color": "purple"},
                    {"name": "Special Gear", "color": "brown"},
                ]
            }
        },
        "Gear Category": {
            "select": {
                "options": [
                    {"name": "Standard Gear", "color": "gray"},
                    {"name": "Kit", "color": "blue"},
                    {"name": "Container", "color": "green"},
                    {"name": "Tool", "color": "yellow"},
                    {"name": "Mount", "color": "red"},
                    {"name": "Vehicle", "color": "purple"},
                    {"name": "Food", "color": "pink"},
                    {"name": "Drink", "color": "brown"},
                    {"name": "Trade Good", "color": "orange"},
                    {"name": "Special", "color": "blue"},
                ]
            }
        },
        "Cost": {"rich_text": {}},
        "Weight": {"number": {}},
    }
    database_id = create_database(
        logger, notion, database_id, database_name, database_items_properties
    )
    return database_id


def build_items_markdown(
    equipment: _equipment, notion: Client, logger: logging.Logger, database_id: str
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
    add_section_heading(markdown_children, f"{equipment.name}", level=1)
    headers = [
        f"Type: {equipment.equipment_category['name']}",
        f"Cost: {equipment.cost['quantity']} {equipment.cost['unit']}",
        f"Weight: {equipment.get_weight()}",
    ]

    if equipment.speed:
        speed: str = f"Speed: {equipment.speed['quantity']} {equipment.speed['unit']}"
        headers.append(speed)

    if equipment.capacity:
        cap: str = f"Carry Weight: {equipment.capacity}"
        headers.append(cap)

    add_table(markdown_children, headers)

    if equipment.desc:
        add_divider(markdown_children)
        for desc in equipment.desc:
            add_paragraph(markdown_children, desc)

    if equipment.contents:
        add_divider(markdown_children)
        for content in equipment.contents:
            add_paragraph(
                markdown_children, f"{content["quantity"]} x {content["item"]["name"]}"
            )

    return markdown_children
