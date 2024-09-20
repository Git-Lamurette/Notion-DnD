from src.utils.load_json import load_data
from src.api.notion_call import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def languages_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    database_id: str,
    start: int,
    end: Union[None, int],
    json_file: str,
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each languages in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get languages Data
    languages_data = load_data(logger, data_directory, json_file)

    # == Apply range to languages data
    if end is None or end > len(languages_data):
        end = len(languages_data)

    # == Iterates through the specified range of the languages JSON
    for index in range(start, end):
        selected_language = languages_data[index]

        logger.info(
            f"Building Markdown for languages -- {selected_language['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _languages class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_language["name"]},
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "".join(mn for mn in selected_language["desc"])
                        },
                    }
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for languages
        children_properties = build_languages_markdown(selected_language)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def languages_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "languages"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_languages_markdown(languages_data: object) -> list:
    from src.markdown.children_md import (
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
    add_section_heading(markdown_children, f"{languages_data['name']}", level=1)
    add_divider(markdown_children)
    add_paragraph(markdown_children, "".join(desc for desc in languages_data["desc"]))

    return markdown_children
