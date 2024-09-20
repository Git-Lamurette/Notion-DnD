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
from src.api.notion_api import create_page_under_page
from src.utils.logger import configure_logging
from src.builds.creature import build_creature_database
from src.builds.weapons import build_weapons_database
from src.builds.armors import build_armors_database
from src.builds.items import build_items_database
from src.builds.magic_items import build_magic_items_database
from src.builds.spells import build_spells_database
from src.builds.weapons_properties import build_weapon_properties_database
from src.builds.skills import build_skills_database
from src.builds.magic_schools import build_magic_schools_database

# from src.utils.get_keys import get_keys
import argparse


NAME = "D&D 5E Notion Database Builder"
VERSION = "0.0.1"
DATA_DIRECTORY = "src/data"
LOGGING_DIRECTORY = "logs"


async def main(args):
    # == Configure the logger
    logger = configure_logging(LOGGING_DIRECTORY)
    # == Display the initial information
    log_initial_info(logger, args)
    # == Create the Notion client
    notion = Client(auth=args.auth_key)
    print(type(notion))
    input("Press Enter to continue...")
    # == Create the reference page - Needed for nested databases
    args.reference_page_id = create_page_under_page(
        logger, notion, args.database_id, "Reference"
    )

    # == Databases contained in the root
    # ==============================
    if any(item.lower() in ["creatures", "all"] for item in args.build):
        build_creature_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Monsters.json", args
        )

    if any(item.lower() in ["weapons", "all"] for item in args.build):
        build_weapons_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Equipment.json", args
        )

    if any(item.lower() in ["armors", "all"] for item in args.build):
        await build_armors_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Equipment.json", args
        )

    if any(item in ["items", "all"] for item in args.build):
        await build_items_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Equipment.json", args
        )

    if any(item in ["magic-items", "all"] for item in args.build):
        build_magic_items_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Magic-Items.json", args
        )

    if any(item in ["spells", "all"] for item in args.build):
        build_spells_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Spells.json", args
        )

    if any(item in ["weapon-properties", "all"] for item in args.build):
        build_weapon_properties_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Spells.json", args
        )

    if any(item in ["skills", "all"] for item in args.build):
        build_skills_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Spells.json", args
        )

    if any(item in ["magic-schools", "all"] for item in args.build):
        build_magic_schools_database(
            logger, notion, DATA_DIRECTORY, "5e-SRD-Spells.json", args
        )


def log_initial_info(logger, args):
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


if __name__ == "__main__":
    # Argument parsing block
    parser = argparse.ArgumentParser(
        description="A tool for building a D&D 5E Notion Database from a JSON source file."
    )

    parser.add_argument(
        "-b",
        "--build",
        nargs="+",
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
