from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_ability_scores_database(logger, notion, data_directory, json_file, args):
    ability_scores_db_id = ability_scores_db(logger, notion, args.database_id)
    ability_scores_page(
        logger,
        notion,
        data_directory,
        json_file,
        ability_scores_db_id,
        args.start_range,
        args.end_range,
    )


def ability_scores_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each ability_scores in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get ability_scores Data
    ability_scores_data = load_data(logger, data_directory, json_file)

    # == Apply range to ability_scores data
    if end is None or end > len(ability_scores_data):
        end = len(ability_scores_data)

    # == Iterates through the specified range of the ability_scores JSON
    for index in range(start, end):
        selected_skill = ability_scores_data[index]

        logger.info(
            f"Building Markdown for ability_scores -- {selected_skill['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _ability_scores class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_skill["full_name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Ability Scores"}},
            "Skills": {
                "multi_select": [
                    {"name": f"{x['name']}"} for x in selected_skill["skills"]
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "".join(mn for mn in selected_skill["desc"])
                        },
                    }
                ]
            },
        }
        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for ability_scores
        children_properties = build_ability_scores_markdown(
            logger, notion, selected_skill
        )

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def ability_scores_db(
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
    database_name = "Ability Scores"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "Skills": {
            "multi_select": {
                "options": [
                    {"name": "Strength", "color": "gray"},
                    {"name": "Dexterity", "color": "blue"},
                    {"name": "Constitution", "color": "red"},
                    {"name": "Intelligence", "color": "pink"},
                    {"name": "Wisdom", "color": "purple"},
                    {"name": "Charisma", "color": "brown"},
                ]
            }
        },
        "5E Category": {
            "select": {"options": [{"name": "Ability Scores", "color": "green"}]}
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_ability_scores_markdown(
    logger: "logging.Logger", notion: "client", ability_scores_data: object
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_divider,
        add_paragraph_with_mentions,
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
        markdown_children, f"{ability_scores_data['full_name']}", level=1
    )
    add_divider(markdown_children)
    for desc in ability_scores_data["desc"]:
        add_paragraph(markdown_children, desc)

    if ability_scores_data["skills"]:
        add_section_heading(markdown_children, "Skills", level=2)
        add_divider(markdown_children)
        for abil in ability_scores_data["skills"]:
            text_string = f"{abil['name']}"
            add_paragraph_with_mentions(
                logger,
                notion,
                markdown_children,
                text_string,
                [text_string],
                "Skills",
            )

    return markdown_children
