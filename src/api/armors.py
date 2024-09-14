from src.classes.equipment_class import _equipment
from src.markdown.armor_md import build_armor_markdown
from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def armor_page(
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

        if equipment.equipment_category["index"] == "armor":
            logger.info(
                f"Building Markdown for equipment -- {equipment.name} -- Index -- {index} --"
            )

            # == Building markdown properties from _equipment class
            markdown_properties = {
                "Name": {"title": [{"text": {"content": "Example Armor"}}]},
                "URL": {
                    "url": f"https://www.dndbeyond.com/equipment/{equipment.index}"
                },
                "Category": {"select": {"name": "Armor"}},
                "Cost": {"rich_text": [{"text": {"content": "50 gp"}}]},
                "Weight": {"number": 15},
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "This is an example description of the armor."
                            }
                        }
                    ]
                },
                "Type": {"multi_select": [{"name": "Medium Armor"}]},
                "Armor Class": {"number": 15},
                "Strength Requirement": {"number": 13},
                "Stealth Disadvantage": {"checkbox": False},
                "Special": {
                    "rich_text": [
                        {"text": {"content": "This armor has a special ability."}}
                    ]
                },
            }

            # == Ensure children_properties list is empty
            children_properties = []

            # == Building markdown for equipment
            children_properties = build_armor_markdown(equipment)

            # == Sending api call
            # ==========
            create_page(
                logger, notion, database_id, markdown_properties, children_properties
            )

            sleep(0.5)


def armor_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "armor"

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
        "Weight": {"number": {}},
        "Description": {"rich_text": {}},
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
        "Armor Class": {"number": {}},
        "Strength Requirement": {"number": {}},
        "Stealth Disadvantage": {"checkbox": {}},
        "Special": {"rich_text": {}},
    }
    return create_database(
        logger, notion, database_id, database_name, database_armor_properties
    )
