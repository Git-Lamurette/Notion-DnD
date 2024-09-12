from src.classes.creature_class import _Creature
from src.markdown.creature_md import build_creature_markdown
from notion_client.errors import APIResponseError
from src.utils.load_json import load_data
import sys
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def creature_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each creature in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get Monster Data
    creature_data = load_data(logger, data_directory, "5e-SRD-Monsters.json")

    # == Apply range to creature data
    if end is None or end > len(creature_data):
        end = len(creature_data)

    # == Iterates through the specified range of the monster JSON
    for index in range(start, end):
        x = creature_data[index]
        # == Makes the creature as a data class
        monster = _Creature(**x)

        # == Building markdown properties from _Creature class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": monster.name},
                    }
                ]
            },
            "Size": {"select": {"name": monster.size.capitalize()}},
            "Type": {"select": {"name": monster.type.capitalize()}},
            "CR": {"number": monster.challenge_rating},
            "Hit Points": {"number": monster.hit_points},
            "Movement Type": {
                "multi_select": [{"name": mt.capitalize()} for mt in monster.speed]
            },
        }

        try:
            # == Ensure children list is empty
            children = []
            logger.info(
                f"Building Markdown for Creature -- {monster.name} -- Index -- {index} --"
            )

            # == Building markdown for creature
            children = build_creature_markdown(monster)

            # == Sending response to notion API
            response = notion.pages.create(
                parent={"database_id": database_id},
                properties=markdown_properties,
                children=children,
            )
            logger.info(f"Page created for {monster.name} with ID: {response['id']}")
            sleep(0.5)

        except APIResponseError as e:
            logger.error(f"Response status: {e.status}")
            logger.error(f"An API error occurred: {e}")
            sys.exit(1)


def creature_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just bulds the empty database page with the required options.

    Args:
        logger (logging.Logger): _description_
        notion (client): _description_
        database_id (str): _description_

    Returns:
        str: _description_
    """
    # == Building markdown database properties
    database_properties = {
        "Name": {"title": {}},
        "Size": {
            "select": {
                "options": [
                    {"name": "Tiny", "color": "pink"},
                    {"name": "Small", "color": "purple"},
                    {"name": "Medium", "color": "blue"},
                    {"name": "Large", "color": "green"},
                    {"name": "Huge", "color": "yellow"},
                    {"name": "Gargantuan", "color": "red"},
                ]
            }
        },
        "Type": {
            "select": {
                "options": [
                    {"name": "Aberration", "color": "gray"},
                    {"name": "Beast", "color": "green"},
                    {"name": "Celestial", "color": "yellow"},
                    {"name": "Construct", "color": "blue"},
                    {"name": "Dragon", "color": "red"},
                    {"name": "Elemental", "color": "orange"},
                    {"name": "Fey", "color": "pink"},
                    {"name": "Fiend", "color": "purple"},
                    {"name": "Giant", "color": "brown"},
                    {"name": "Humanoid", "color": "blue"},
                    {"name": "Monstrosity", "color": "red"},
                    {"name": "Ooze", "color": "gray"},
                    {"name": "Plant", "color": "green"},
                    {"name": "Undead", "color": "gray"},  # Fixed color
                ]
            }
        },
        "CR": {"number": {}},
        "Hit Points": {"number": {}},
        "Movement Type": {
            "multi_select": {
                "options": [
                    {"name": "Walk", "color": "blue"},
                    {"name": "Fly", "color": "purple"},
                    {"name": "Swim", "color": "green"},
                    {"name": "Climb", "color": "yellow"},
                    {"name": "Burrow", "color": "brown"},
                    {"name": "Hover", "color": "pink"},
                ]
            }
        },
    }

    try:
        # == Sending response to notion API
        response = notion.databases.create(
            parent={"type": "page_id", "page_id": database_id},
            title=[{"type": "text", "text": {"content": "Creatures Database"}}],
            properties=database_properties,
        )
        logger.info(f"Page created for Creatures Database with ID: {response['id']}")

        # == Returning
        return response["id"]

    except APIResponseError as e:
        logger.error(f"Response status: {e.status}")
        logger.error(f"An API error occurred: {e}")
        sys.exit(1)
