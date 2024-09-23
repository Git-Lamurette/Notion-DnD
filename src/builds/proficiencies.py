from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_proficiencies_database(logger, notion, data_directory, json_file, args):
    proficiencies_db_id = proficiencies_db(logger, notion, args.reference_page_id)
    proficiencies_page(
        logger,
        notion,
        data_directory,
        json_file,
        proficiencies_db_id,
        args.start_range,
        args.end_range,
    )


def proficiencies_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each proficiencies in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get proficiencies Data
    proficiencies_data = load_data(logger, data_directory, json_file)

    # == Apply range to proficiencies data
    if end is None or end > len(proficiencies_data):
        end = len(proficiencies_data)

    # == Iterates through the specified range of the proficiencies JSON
    for index in range(start, end):
        selected_proficiencies = proficiencies_data[index]

        logger.info(
            f"Building Markdown for proficiencies -- {selected_proficiencies['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _proficiencies class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_proficiencies["name"]},
                    }
                ]
            },
            "Type": {"select": {"name": selected_proficiencies["type"]}},
            "Classes": {
                "multi_select": [
                    {"name": classes["name"]}
                    for classes in selected_proficiencies["classes"]
                ]
            },
            "Races": {
                "multi_select": [
                    {"name": race_name["name"]}
                    for race_name in selected_proficiencies["races"]
                ]
            },
            "5E Category": {"select": {"name": "Proficiencies"}},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for proficiencies
        # children_properties = build_proficiencies_markdown(
        #    logger, notion, selected_proficiencies
        # )

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def proficiencies_db(
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
    database_name = "Proficiencies"

    # == Building markdown database properties
    database_weapon_properties = {
        "Name": {"title": {}},
        "Type": {
            "select": {
                "options": [
                    {"name": "Armor", "color": "gray"},
                    {"name": "Artisan's Tools", "color": "blue"},
                    {"name": "Gaming Sets", "color": "red"},
                    {"name": "Musical Instruments", "color": "pink"},
                    {"name": "Other", "color": "purple"},
                    {"name": "Saving Throws", "color": "brown"},
                    {"name": "Skills", "color": "green"},
                    {"name": "Vehicles", "color": "yellow"},
                    {"name": "Weapons", "color": "orange"},
                ]
            }
        },
        "Classes": {
            "multi_select": {
                "options": [
                    {"name": "Barbarian", "color": "red"},
                    {"name": "Bard", "color": "pink"},
                    {"name": "Cleric", "color": "yellow"},
                    {"name": "Druid", "color": "green"},
                    {"name": "Fighter", "color": "gray"},
                    {"name": "Monk", "color": "blue"},
                    {"name": "Paladin", "color": "purple"},
                    {"name": "Ranger", "color": "orange"},
                    {"name": "Rogue", "color": "brown"},
                    {"name": "Sorcerer", "color": "red"},
                    {"name": "Warlock", "color": "purple"},
                    {"name": "Wizard", "color": "blue"},
                ]
            }
        },
        "Races": {
            "multi_select": {
                "options": [
                    {"name": "High Elf", "color": "red"},
                    {"name": "Dwarf", "color": "pink"},
                    {"name": "Elf", "color": "yellow"},
                ]
            }
        },
        "5E Category": {
            "select": {"options": [{"name": "Proficiencies", "color": "green"}]}
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_proficiencies_markdown(
    logger: "logging.Logger", notion: "client", proficiencies_data: object
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
    add_section_heading(markdown_children, f"{proficiencies_data['name']}", level=1)
    add_divider(markdown_children)

    return markdown_children
