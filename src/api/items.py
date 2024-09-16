from src.classes.equipment_class import _equipment
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
    items_data = load_data(logger, data_directory, "5e-SRD-Equipment.json")

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
            children_properties, relations_to_create = build_items_markdown(
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
                relations_to_create,
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
    return create_database(
        logger, notion, database_id, database_name, database_items_properties
    )
