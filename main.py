"""
D&D 5E Notion Database Builder

Converts a JSON file contianing the entirety of DND 5E SRD into a notion database via API calls.
Allowing for easy integration into world building or running campaigns.

Written by:
    Trent.L.Odell@gmail.com

Python: 3.12.6
Formatter: Ruff
Linter: Ruff
"""

from notion_client import Client
from notion_client.errors import APIResponseError
from src.utils.load_json import load_data
from src.utils.logger import configure_logging
from src.classes.creatures import _Creature
from src.markdown.creature_md import build_creature_markdown

NAME = "D&D 5E Notion Database Builder"
VERSION = "0.0.1"
DATA_DIRECTORY = "src/data"
LOGGING_DIRECTORY = "logs"


def main():
    # == Configure logging
    logger = configure_logging(LOGGING_DIRECTORY)

    # == This is personal to my notion, will have kwargs to handle this eventually
    database_id = "03f59b41-0f8f-4ec2-8941-e8aba10190bf"
    auth_key = "secret_8fDt3EJbAlcH0tWh6u26x5RfTBVkfHZYW9nUUN6K1gU"

    logger.info(f"Fed user database: {database_id}")
    logger.info(f"Fed user auth key: {auth_key}")

    # == Using your auth key we access your notion
    notion = Client(auth=auth_key)

    # == Get Monster Data
    creature_data = load_data(logger, DATA_DIRECTORY, "5e-SRD-Monsters.json")

    # == Iterates through the monster JSON
    for x in creature_data:
        # == Makes the creature as a data class
        monster = _Creature(**x)

        # == For development I want to focus on one monster
        if monster.name == "Acolyte":
            logger.info(f"Building {monster.name} MD File")

            try:
                children = build_creature_markdown(monster)
                response = notion.pages.create(
                    parent={"database_id": database_id},
                    properties={
                        "Name": {
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": monster.name.capitalize()},
                                }
                            ]
                        },
                        "Size": {"select": {"name": monster.size.capitalize()}},
                        "Type": {"select": {"name": monster.type.capitalize()}},
                        "CR": {"number": monster.challenge_rating},
                        "Hit Points": {"number": monster.hit_points},
                        "Movement Type": {
                            "multi_select": [
                                {"name": mt.capitalize()} for mt in monster.speed
                            ]
                        },
                    },
                    children=children,
                )
                logger.info(
                    f"Page created for {monster.name} with ID: {response['id']}"
                )  # type: ignore
            except APIResponseError as e:
                logger.error(f"An API error occurred: {e}")


if __name__ == "__main__":
    main()
