from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_weapon_properties_database(logger, notion, data_directory, json_file, args):
    weapons_prop_db = weapons_properties_db(logger, notion, args.reference_page_id)
    weapons_properties_page(
        logger,
        notion,
        data_directory,
        json_file,
        weapons_prop_db,
        args.start_range,
        args.end_range,
    )


def weapons_properties_page(
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
    weapons_properties_data = load_data(logger, data_directory, json_file)

    # == Apply range to weapon properties data
    if end is None or end > len(weapons_properties_data):
        end = len(weapons_properties_data)

    # == Iterates through the specified range of the weapon properties JSON
    for index in range(start, end):
        selected_prop = weapons_properties_data[index]

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
            "Description": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "".join(mn for mn in selected_prop["desc"])
                        },
                    }
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for weapon properties
        children_properties = build_weapons_properties_markdown(selected_prop)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def weapons_properties_db(
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
    database_name = "Weapon Properties"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_weapons_properties_markdown(weapons_properties_data: object) -> list:
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
    add_section_heading(
        markdown_children, f"{weapons_properties_data['name']}", level=1
    )
    add_divider(markdown_children)
    add_paragraph(
        markdown_children, "".join(desc for desc in weapons_properties_data["desc"])
    )

    return markdown_children