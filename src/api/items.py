from src.classes.item_class import _items
from src.markdown.items_md import build_items_markdown
from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def items_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
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
    items_data = load_data(logger, data_directory, "5e-SRD-items.json")

    # == Apply range to items data
    if end is None or end > len(items_data):
        end = len(items_data)

    # == Iterates through the specified range of the items JSON
    for index in range(start, end):
        x = items_data[index]

        # == Makes the items as a data class
        items = _items(**x)

        if items.items_category["index"] == "items":
            logger.info(
                f"Building Markdown for items -- {items.name} -- Index -- {index} --"
            )

            # == Building markdown properties from _items class
            markdown_properties = {
                "Name": {"title": [{"text": {"content": items.name}}]},
                "URL": {
                    "url": f"https://www.dndbeyond.com/items/{items.index.strip("-items")}"
                },
                "Category": {"select": {"name": items.items_category["name"]}},
                "Cost": {"rich_text": [{"text": {"content": items.get_cost()}}]},
                "Weight": {"rich_text": [{"text": {"content": f"{items.weight} lbs"}}]},
                "Type": {"multi_select": [{"name": items.items_category}]},
                "items Class": {"rich_text": [{"text": {"content": items.get_items_class()}}]},
                "Strength Requirement": {"number": items.get_strength_requirement()},
                "Stealth Disadvantage": {"checkbox": items.stealth_disadvantage},
            }

            # == Ensure children_properties list is empty
            children_properties = []

            # == Building markdown for items
            children_properties = build_items_markdown(items)

            # == Sending api call
            # ==========
            create_page(
                logger, notion, database_id, markdown_properties, children_properties
            )
            
            sleep(0.5)


def items_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
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
                    {"name": "items", "color": "green"},
                ]
            }
        },
        "Cost": {"rich_text": {}},
        "Weight": {"rich_text": {}},
        "Type": {
            "multi_select": {
                "options": [
                    {"name": "Light items", "color": "gray"},
                    {"name": "Medium items", "color": "green"},
                    {"name": "Heavy items", "color": "yellow"},
                    {"name": "Shield", "color": "blue"},
                ]
            }
        },
        "items Class": {"rich_text": {}},
        "Strength Requirement": {"number": {}},
        "Stealth Disadvantage": {"checkbox": {}},
    }
    return create_database(
        logger, notion, database_id, database_name, database_items_properties
    )
