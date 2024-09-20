from src.classes.magic_items_class import _magic_item
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_magic_items_database(logger, notion, data_directory, json_file, args):
    items_db_id = magic_items_db(logger, notion, args.database_id)
    magic_items_page(
        logger,
        notion,
        data_directory,
        json_file,
        items_db_id,
        args.start_range,
        args.end_range,
    )


def magic_items_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each magic_items in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get magic_items Data
    magic_items_data = load_data(logger, data_directory, json_file)

    # == Apply range to magic_items data
    if end is None or end > len(magic_items_data):
        end = len(magic_items_data)

    # == Iterates through the specified range of the magic_items JSON
    for index in range(start, end):
        x = magic_items_data[index]

        # == Makes the magic_items as a data class
        magic_items = _magic_item(**x)

        logger.info(
            f"Building Markdown for magic_items -- {magic_items.name} -- Index -- {index} --"
        )

        # == Building markdown properties from _magic_items class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": magic_items.name},
                    }
                ]
            },
            "URL": {
                "url": f"https://www.dndbeyond.com/magic-items/{magic_items.index}"
            },
            "Rarity": {"select": {"name": magic_items.rarity.get("name", "Unknown")}},
            "Category": {
                "select": {
                    "name": magic_items.equipment_category.get(
                        "name", "Unknown Category"
                    )
                    .replace(",", " -")
                    .capitalize()
                }
            },
            "Variants": {
                "multi_select": [
                    {"name": mt.replace(",", " -").capitalize()}
                    for mt in magic_items.get_variants()
                ]
            },
            "Variant": {"checkbox": magic_items.variant},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for magic_items
        children_properties = build_magic_items_markdown(
            magic_items,
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


def magic_items_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Magic Items"

    # == Building markdown database properties
    database_magic_items_properties = {
        "Name": {"title": {}},
        "URL": {"url": {}},
        "Rarity": {
            "select": {
                "options": [
                    {"name": "Common", "color": "gray"},
                    {"name": "Varies", "color": "brown"},
                    {"name": "Uncommon", "color": "green"},
                    {"name": "Rare", "color": "blue"},
                    {"name": "Very Rare", "color": "purple"},
                    {"name": "Legendary", "color": "orange"},
                    {"name": "Artifact", "color": "red"},
                ]
            }
        },
        "Category": {
            "select": {
                "options": [
                    {"name": "Ammunition", "color": "gray"},
                    {"name": "Armor", "color": "blue"},
                    {"name": "Potion", "color": "green"},
                    {"name": "Ring", "color": "yellow"},
                    {"name": "Rod", "color": "red"},
                    {"name": "Scroll", "color": "purple"},
                    {"name": "Staff", "color": "pink"},
                    {"name": "Wand", "color": "brown"},
                    {"name": "Weapon", "color": "orange"},
                    {"name": "Wondrous Items", "color": "default"},
                    {"name": "Ammunition", "color": "gray"},
                    {"name": "Armor", "color": "blue"},
                    {"name": "Potion", "color": "green"},
                    {"name": "Ring", "color": "yellow"},
                    {"name": "Rod", "color": "red"},
                    {"name": "Scroll", "color": "purple"},
                    {"name": "Staff", "color": "pink"},
                    {"name": "Wand", "color": "brown"},
                    {"name": "Weapon", "color": "orange"},
                    {"name": "Wondrous-items", "color": "default"},
                ]
            }
        },
        "Variant": {"checkbox": {}},
        "Variants": {"multi_select": {}},
    }

    return create_database(
        logger, notion, database_id, database_name, database_magic_items_properties
    )


def build_magic_items_markdown(
    magic_item: object, notion: "client", logger: "logging.Logger", database_id: str
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
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
    add_section_heading(markdown_children, f"{magic_item.name}", level=1)

    for index, desc in enumerate(magic_item.desc):
        if index == 0:
            add_paragraph(markdown_children, desc)
            add_divider(markdown_children)
        else:
            add_paragraph(markdown_children, desc)

    return markdown_children
