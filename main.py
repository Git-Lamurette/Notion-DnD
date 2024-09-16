"""

D&D 5E Notion Database Builder

Converts a JSON file contianing the entirety of DND 5E SRD into a notion database via API calls.
Allowing for easy integration into world building or running campaigns.

Written by:
    Trent.L.Odell@gmail.com

Version: 0.0.1
Python: 3.12.6
Formatter: Ruff
Linter: Ruff

SUPPORTED DATABASES:

    All
    Creature
    Weapons

EXAMLPES:

This will build a creatures database
    py .\\main.py -b "creatures" -db "database_key" -k "notion_api_key"

This wil build all databases
    py .\\main.py -b "all" -db "database_key" -k "notion_api_key"

"""

from notion_client import Client
from src.utils.logger import configure_logging
from src.api.creature import creature_page, creature_db
from src.api.weapons import weapons_page, weapons_db
from src.api.armors import armor_page, armor_db

import argparse


NAME = "D&D 5E Notion Database Builder"
VERSION = "0.0.1"
DATA_DIRECTORY = "src/data"
LOGGING_DIRECTORY = "logs"


def main(args):
    # == Configure logging
    logger = configure_logging(LOGGING_DIRECTORY)

    # == Logging passed through info
    logger.info("=========================================================")
    logger.info("==             D&D 5E Notion Database Builder          ==")
    logger.info(f"==                   Version {VERSION}                     ==")
    logger.info("=========================================================")
    logger.info("==")
    logger.info(f"==  Database ID         : {args.database_id}")
    logger.info(f"==  Authentication Key  : {args.auth_key}")
    logger.info(f"==  Build Database      : {args.build}")
    logger.info(f"==  Start Range         : {args.start_range}")
    logger.info(f"==  End Range           : {args.end_range}")
    logger.info("==")
    logger.info("=========================================================")

    # == Using your auth key we access your Notion account
    notion = Client(auth=args.auth_key)

    # == This enables the selection of the specified databases you want build
    # ========================
    # == This is creating everything needed for the creature database
    # ========================
    if args.build.lower() in {"creatures", "all"}:
        # == Creating the database itself
        creature_db_id = creature_db(logger, notion, args.database_id)
        # == Populating the database with all the markdown files
        creature_page(
            logger,
            notion,
            DATA_DIRECTORY,
            creature_db_id,
            args.start_range,
            args.end_range,
        )

    if args.build.lower() in {"weapons", "all"}:
        equipment_db_id = weapons_db(logger, notion, args.database_id)

        weapons_page(
            logger,
            notion,
            DATA_DIRECTORY,
            equipment_db_id,
            args.start_range,
            args.end_range,
        )

    if args.build.lower() in {"armor", "all"}:
        equipment_db_id = armor_db(logger, notion, args.database_id)
        
        armor_page(
            logger,
            notion,
            DATA_DIRECTORY,
            equipment_db_id,
            args.start_range,
            args.end_range,
        )

if __name__ == "__main__":
    # Argument parsing block
    parser = argparse.ArgumentParser(
        description="A tool for building a D&D 5E Notion Database from a JSON source file."
    )

    parser.add_argument(
        "-b",
        "--build",
        type=str,
        required=True,
        help="Select your database you want to build",
    )

    # Define the command-line arguments
    parser.add_argument(
        "-db",
        "--database_id",
        type=str,
        required=True,
        help="The Notion database ID where data will be stored.",
    )

    parser.add_argument(
        "-k",
        "--auth_key",
        type=str,
        required=True,
        help="Your Notion API authentication key (starts with 'secret_').",
    )

    parser.add_argument(
        "-s",
        "--start_range",
        type=int,
        required=False,
        default=0,
        help="The start of the range you want to import",
    )

    parser.add_argument(
        "-e",
        "--end_range",
        type=int,
        required=False,
        default=None,
        help="The end of the range you want to import",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call main() with the parsed arguments
    main(args)
