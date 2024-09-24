from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_magic_schools_database(logger, notion, data_directory, json_file, args):
    magic_schools_db_id = magic_schools_db(logger, notion, args.reference_page_id)
    magic_schools_page(
        logger,
        notion,
        data_directory,
        json_file,
        magic_schools_db_id,
        args.start_range,
        args.end_range,
    )


def magic_schools_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each magic_schools in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get magic_schools Data
    magic_schools_data = load_data(logger, data_directory, json_file)

    # == Apply range to magic_schools data
    if end is None or end > len(magic_schools_data):
        end = len(magic_schools_data)

    # == Iterates through the specified range of the magic_schools JSON
    for index in range(start, end):
        schools = magic_schools_data[index]

        logger.info(
            f"Building Markdown for magic_schools -- {schools['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _magic_schools class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": schools["name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Magic Schools"}},
            "Description": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": schools["desc"]},
                    }
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for magic_schools
        children_properties = build_magic_schools_markdown(schools)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def magic_schools_db(
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
    database_name = "Magic Schools"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "5E Category": {
            "select": {"options": [{"name": "Magic Schools", "color": "green"}]}
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_magic_schools_markdown(magic_schools_data: object) -> list:
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
    add_section_heading(markdown_children, f"{magic_schools_data['name']}", level=1)
    add_divider(markdown_children)
    add_paragraph(markdown_children, magic_schools_data["desc"])

    return markdown_children
