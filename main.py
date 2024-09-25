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
from src.builds.rules_section import build_rules_database
from src.builds.languages import build_languages_database
from src.builds.damage_types import build_damage_types_database
from src.builds.conditions import build_conditions_database
from src.builds.alignments import build_alignments_database
from src.builds.ability_scores import build_ability_scores_database
from src.builds.proficiencies import build_proficiencies_database
from src.builds.classes import build_classes_database
from src.utils.get_keys import get_keys
from pprint import pprint

# from src.utils.get_keys import get_keys
import argparse


NAME = "D&D 5E Notion Database Builder"
VERSION = "0.0.1"
DATA_DIRECTORY = "data"
LOGGING_DIRECTORY = "logs"


def main(args):
    # == Configure the logger
    logger = configure_logging(LOGGING_DIRECTORY)
    # == Display the initial information
    log_initial_info(logger, args)
    # == Create the Notion client
    notion = Client(auth=args.auth_key)
    # ==
    #get_keys(logger, f"{DATA_DIRECTORY}", "5e-SRD-Classes.json", "subclasses")
    # == Create the reference page - Needed for nested databases
    args.reference_page_id = create_page_under_page(
        logger, notion, args.database_id, "Reference"
    )
    # Define a mapping of database names to their corresponding build functions and JSON files
    database_builders = {
        # == References first
        "weapon-properties": (
            build_weapon_properties_database,
            "5e-SRD-Weapon-Properties.json",
        ),
        "magic-schools": (build_magic_schools_database, "5e-SRD-Magic-Schools.json"),
        "rules": (build_rules_database, "5e-SRD-Rule-Sections.json"),
        "languages": (build_languages_database, "5e-SRD-Languages.json"),
        "damage-types": (build_damage_types_database, "5e-SRD-Damage-Types.json"),
        "conditions": (build_conditions_database, "5e-SRD-Conditions.json"),
        "alignments": (build_alignments_database, "5e-SRD-Alignments.json"),
        "proficiencies": (build_proficiencies_database, "5e-SRD-Proficiencies.json"),
        # == Ability score requires skills to be present to populate correctly
        "skills": (build_skills_database, "5e-SRD-Skills.json"),
        "ability-scores": (build_ability_scores_database, "5e-SRD-Ability-Scores.json"),
        # == Most of these rely on references for links
        "creatures": (build_creature_database, "5e-SRD-Monsters.json"),
        "classes": (build_classes_database, "5e-SRD-Classes.json"),
        "weapons": (build_weapons_database, "5e-SRD-Equipment.json"),
        "armors": (build_armors_database, "5e-SRD-Equipment.json"),
        "items": (build_items_database, "5e-SRD-Equipment.json"),
        "magic-items": (build_magic_items_database, "5e-SRD-Magic-Items.json"),
        "spells": (build_spells_database, "5e-SRD-Spells.json"),
    }

    # Iterate over the build list and call the corresponding build function
    for item in args.build:
        item_lower = item.lower()
        if item_lower.lower() == "all":
            # If "all" is specified, build all databases
            for builder, json_file in database_builders.values():
                log_db_build(logger, item, json_file)
                builder(logger, notion, DATA_DIRECTORY, json_file, args)
            break
        if item_lower in database_builders:
            builder, json_file = database_builders[item_lower]
            log_db_build(logger, item, json_file)
            builder(logger, notion, DATA_DIRECTORY, json_file, args)


def log_db_build(logger, item, json_file):
    logger.info("=========================================================")
    logger.info(f"==  Building {item} database")
    logger.info(f"==  Using {json_file} as the source file")
    logger.info("=========================================================")


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

    parser.add_argument(
        "-u",
        "--update",
        type=str,
        required=False,
        default=None,
        help="The database you want to update - only works with a single options at a time",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call main() with the parsed arguments
    main(args)
