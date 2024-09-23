from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_languages_database(logger, notion, data_directory, json_file, args):
    languages_prop_db = languages_properties_db(logger, notion, args.reference_page_id)
    languages_properties_page(
        logger,
        notion,
        data_directory,
        json_file,
        languages_prop_db,
        args.start_range,
        args.end_range,
    )


def languages_properties_page(
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
    languages_data = load_data(logger, data_directory, json_file)

    # == Apply range to weapon properties data
    if end is None or end > len(languages_data):
        end = len(languages_data)

    # == Iterates through the specified range of the weapon properties JSON
    for index in range(start, end):
        selected_prop = languages_data[index]

        logger.info(
            f"Building Markdown for weapon properties -- {selected_prop['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from languages properties class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": selected_prop["name"]},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Languages"}},
            "Type": {"select": {"name": selected_prop.get("type", "")}},
            "Typical Speakers": {
                "multi_select": [
                    {"name": speaker.capitalize()}
                    for speaker in selected_prop["typical_speakers"]
                ]
            },
            "Script": {"select": {"name": selected_prop.get("script", " ")}},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for weapon properties
        children_properties = build_languages_properties_markdown(selected_prop)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def languages_properties_db(
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
    database_name = "Languages"

    # == Building markdown database properties
    database_languages = {
        "Name": {"title": {}},
        "5E Category": {
            "select": {"options": [{"name": "Languages", "color": "green"}]}
        },
        "Type": {
            "select": {
                "options": [
                    {"name": "Standard", "color": "green"},
                    {"name": "Exotic", "color": "purple"},
                ]
            }
        },
        "Typical Speakers": {
            "multi_select": {
                "options": [
                    {"name": "Humans", "color": "blue"},
                    {"name": "Dwarves", "color": "brown"},
                    {"name": "Elves", "color": "pink"},
                    {"name": "Ogres", "color": "orange"},
                    {"name": "Giants", "color": "red"},
                    {"name": "Gnomes", "color": "yellow"},
                    {"name": "Goblinoids", "color": "gray"},
                    {"name": "Halflings", "color": "purple"},
                    {"name": "Orcs", "color": "gray"},
                    {"name": "Demons", "color": "red"},
                    {"name": "Celestials", "color": "yellow"},
                    {"name": "Dragons", "color": "green"},
                    {"name": "Dragonborn", "color": "blue"},
                    {"name": "Aboleths", "color": "red"},
                    {"name": "Cloakers", "color": "gray"},
                    {"name": "Devils", "color": "red"},
                    {"name": "Elementals", "color": "orange"},
                    {"name": "Fey creatures", "color": "pink"},
                    {"name": "Underdark traders", "color": "gray"},
                ]
            }
        },
        "Script": {
            "select": {
                "options": [
                    {"name": "Common", "color": "blue"},
                    {"name": "Dwarvish", "color": "brown"},
                    {"name": "Elvish", "color": "pink"},
                    {"name": "Infernal", "color": "red"},
                    {"name": "Draconic", "color": "green"},
                    {"name": "Celestial", "color": "yellow"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_languages
    )


def build_languages_properties_markdown(languages_data: object) -> list:
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
    add_section_heading(markdown_children, f"{languages_data['name']}", level=1)
    add_divider(markdown_children)
    if languages_data.get("desc"):
        add_paragraph(markdown_children, f"{languages_data["desc"]}")
    else:
        add_paragraph(markdown_children, "No description available")

    return markdown_children
