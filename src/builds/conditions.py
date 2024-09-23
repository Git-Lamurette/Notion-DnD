from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_conditions_database(logger, notion, data_directory, json_file, args):
    conditions_prop_db = conditions_properties_db(
        logger, notion, args.reference_page_id
    )
    conditions_properties_page(
        logger,
        notion,
        data_directory,
        json_file,
        conditions_prop_db,
        args.start_range,
        args.end_range,
    )


def conditions_properties_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each conditions properties in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get conditions properties Data
    conditions_properties_data = load_data(logger, data_directory, json_file)

    # == Apply range to conditions properties data
    if end is None or end > len(conditions_properties_data):
        end = len(conditions_properties_data)

    # == Iterates through the specified range of the conditions properties JSON
    for index in range(start, end):
        selected_prop = conditions_properties_data[index]

        logger.info(
            f"Building Markdown for conditions properties -- {selected_prop['name']} -- Index -- {index} --"
        )

        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_prop["name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Conditions"}},
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

        # == Building markdown for conditions properties
        children_properties = build_conditions_properties_markdown(selected_prop)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def conditions_properties_db(
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
    database_name = "Conditions"

    # == Building markdown database properties
    database_conditions = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "5E Category": {
            "select": {
                "options": [
                    {"name": "Conditions", "color": "blue"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_conditions
    )


def build_conditions_properties_markdown(
    conditions_properties_data: object,
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
    add_section_heading(
        markdown_children, f"{conditions_properties_data['name']}", level=1
    )
    add_divider(markdown_children)
    add_paragraph(
        markdown_children,
        "".join(desc for desc in conditions_properties_data["desc"]),
    )

    return markdown_children
