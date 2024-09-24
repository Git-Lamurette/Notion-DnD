from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep
from src.builds.children_md import (
    add_paragraph,
)

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_rules_database(logger, notion, data_directory, json_file, args):
    rules_prop_db = rules_properties_db(logger, notion, args.reference_page_id)
    rules_properties_page(
        logger,
        notion,
        data_directory,
        json_file,
        rules_prop_db,
        args.start_range,
        args.end_range,
    )


def rules_properties_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each weapon properties in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get weapon properties Data
    rules_properties_data = load_data(logger, data_directory, json_file)

    # == Apply range to weapon properties data
    if end is None or end > len(rules_properties_data):
        end = len(rules_properties_data)

    # == Iterates through the specified range of the weapon properties JSON
    for index in range(start, end):
        selected_prop = rules_properties_data[index]

        logger.info(
            f"Building Markdown for weapon properties -- {selected_prop['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _weapon properties class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_prop["name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Rules"}},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Sending api call
        # ==========

        created_page = create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        list_of_desc = selected_prop["desc"].split("\n")
        temp = []

        for desc in list_of_desc:
            add_paragraph(temp, desc)
            if len(temp) >= 100:
                notion.blocks.children.append(block_id=created_page, children=temp)
                temp = []

        # Append any remaining elements in temp
        if temp:
            notion.blocks.children.append(block_id=created_page, children=temp)

        sleep(0.5)


def rules_properties_db(
    logger: "logging.Logger", notion: "client", database_id: str
) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Rules"

    # == Building markdown database properties
    database_rules = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "5E Category": {
            "select": {
                "options": [
                    {"name": "Rules", "color": "blue"},
                ]
            }
        },
    }

    return create_database(logger, notion, database_id, database_name, database_rules)
