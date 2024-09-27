from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_feats_database(logger, notion, data_directory, json_file, args):
    feats_db_id = feats_db(logger, notion, args.database_id)
    feats_page(
        logger,
        notion,
        data_directory,
        json_file,
        feats_db_id,
        args.start_range,
        args.end_range,
    )


def feats_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each feats in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get feats Data
    feats_data = load_data(logger, data_directory, json_file)

    # == Apply range to feats data
    if end is None or end > len(feats_data):
        end = len(feats_data)

    # == Iterates through the specified range of the feats JSON
    for index in range(start, end):
        feats_data = feats_data[index]

        logger.info(
            f"Building Markdown for Feats -- {feats_data['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _feats class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": feats_data["name"]},
                    }
                ]
            },
            "Requirements": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"{feats_data['ability_score']['name']} {feats_data['minimum_score']}"
                            for feats_data in feats_data["prerequisites"]
                        },
                    }
                ]
            },
            "5E Category": {"select": {"name": "Feats"}},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for feats
        children_properties = build_feats_markdown(logger, notion, feats_data)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def feats_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Feats"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Requirements": {"rich_text": {}},
        "5E Category": {"select": {"options": [{"name": "Feats", "color": "green"}]}},
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_feats_markdown(
    logger: "logging.Logger",
    notion: "client",
    feats_data: object,
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
    add_section_heading(markdown_children, f"{feats_data['name']}", level=1)
    min = ", ".join(
        f"{feats_data['ability_score']['name']} {feats_data['minimum_score']}"
        for feats_data in feats_data["prerequisites"]
    )
    add_paragraph(
        markdown_children,
        (f"Minimum Requirements - {min}"),
    )
    add_divider(markdown_children)
    for d in feats_data["desc"]:
        add_paragraph(markdown_children, d)

    return markdown_children
