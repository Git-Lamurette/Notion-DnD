from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_backgrounds_database(logger, notion, data_directory, json_file, args):
    backgrounds_db_id = backgrounds_db(logger, notion, args.database_id)
    backgrounds_page(
        logger,
        notion,
        data_directory,
        json_file,
        backgrounds_db_id,
        args.start_range,
        args.end_range,
    )


def backgrounds_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each backgrounds in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get backgrounds Data
    backgrounds_data = load_data(logger, data_directory, json_file)

    # == Apply range to backgrounds data
    if end is None or end > len(backgrounds_data):
        end = len(backgrounds_data)

    # == Iterates through the specified range of the backgrounds JSON
    for index in range(start, end):
        backgrounds_data = backgrounds_data[index]

        logger.info(
            f"Building Markdown for backgrounds -- {backgrounds_data['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _backgrounds class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": backgrounds_data["name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Backgrounds"}},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for backgrounds
        children_properties = build_backgrounds_markdown(backgrounds_data)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def backgrounds_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Backgrounds"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "5E Category": {
            "select": {"options": [{"name": "Backgrounds", "color": "green"}]}
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_backgrounds_markdown(backgrounds_data: object) -> list:
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
    add_section_heading(markdown_children, f"{backgrounds_data['name']}", level=1)
    add_divider(markdown_children)

    return markdown_children
