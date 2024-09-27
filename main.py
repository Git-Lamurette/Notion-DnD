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

    "all",
    "weapon-properties",
    "magic-schools",
    "rules",
    "languages",
    "damage-types",
    "conditions",
    "alignments",
    "proficiencies",
    "skills",
    "ability-scores",
    "creatures",
    "races",
    "classes",
    "weapons",
    "armors",
    "items",
    "magic-items",
    "spells",
    "backgrounds",
    "feats",

EXAMLPES:

This will build a creatures database
    py .\\main.py --build creatures weapons --database_id a674063b72a04deb8da26650db7294a5 -k secret_**********************

This wil build all databases
    py .\\main.py --build all --database_id a674063b72a04deb8da26650db7294a5 -k secret_**********************

"""

from notion_client import Client
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
from src.builds.races import build_races_database
from src.builds.backgrounds import build_backgrounds_database
from src.builds.feats import build_feats_database
import logging
import argparse


NAME = "D&D 5E Notion Database Builder"
VERSION = "0.0.1"
DATA_DIRECTORY = "data"
LOGGING_DIRECTORY = "logs"
VALID_BUILD_SET_1 = ["all"]
VALID_BUILD_SET_2 = [
    "weapon-properties",
    "magic-schools",
    "rules",
    "languages",
    "damage-types",
    "conditions",
    "alignments",
    "proficiencies",
    "skills",
    "ability-scores",
    "creatures",
    "races",
    "classes",
    "weapons",
    "armors",
    "items",
    "magic-items",
    "spells",
    "backgrounds",
    "feats",
]


def main(args: argparse.Namespace) -> None:
    """The main function for the D&D 5E Notion Database Builder
    Args:
        args (argparse.Namespace): The parsed command-line arguments
    """

    # == Configure the logger
    logger = configure_logging(LOGGING_DIRECTORY)

    # == Display the initial information
    log_initial_info(logger, args)

    # == Create the Notion client
    notion = Client(auth=args.auth_key)

    # == Define a mapping of database names to their corresponding build functions and JSON files
    # == Some of these are order dependent for example, you need to build the weapon properties before the weapons
    database_builders = {
        "weapon-properties": (
            build_weapon_properties_database,
            "5e-SRD-Weapon-Properties.json",
        ),
        "backgrounds": (build_backgrounds_database, "5e-SRD-Backgrounds.json"),
        "feats": (build_feats_database, "5e-SRD-Feats.json"),
        "magic-schools": (build_magic_schools_database, "5e-SRD-Magic-Schools.json"),
        "rules": (build_rules_database, "5e-SRD-Rule-Sections.json"),
        "languages": (build_languages_database, "5e-SRD-Languages.json"),
        "damage-types": (build_damage_types_database, "5e-SRD-Damage-Types.json"),
        "conditions": (build_conditions_database, "5e-SRD-Conditions.json"),
        "alignments": (build_alignments_database, "5e-SRD-Alignments.json"),
        "proficiencies": (build_proficiencies_database, "5e-SRD-Proficiencies.json"),
        "skills": (build_skills_database, "5e-SRD-Skills.json"),
        "ability-scores": (build_ability_scores_database, "5e-SRD-Ability-Scores.json"),
        "creatures": (build_creature_database, "5e-SRD-Monsters.json"),
        "races": (build_races_database, "5e-SRD-Races.json"),
        "classes": (build_classes_database, "5e-SRD-Classes.json"),
        "weapons": (build_weapons_database, "5e-SRD-Equipment.json"),
        "armors": (build_armors_database, "5e-SRD-Equipment.json"),
        "items": (build_items_database, "5e-SRD-Equipment.json"),
        "magic-items": (build_magic_items_database, "5e-SRD-Magic-Items.json"),
        "spells": (build_spells_database, "5e-SRD-Spells.json"),
    }

    # == Iterate over the database_builders dict and call the corresponding function to build the database
    for item in args.build:
        item_lower = item.lower()
        if item_lower == "all":
            for builder, json_file in database_builders.values():
                log_db_build(logger, item, json_file)
                builder(logger, notion, DATA_DIRECTORY, json_file, args)
            break
        # == Builds each item in the database args
        if item_lower in database_builders:
            builder, json_file = database_builders[item_lower]
            log_db_build(logger, item, json_file)
            builder(logger, notion, DATA_DIRECTORY, json_file, args)


def log_db_build(logger: logging.Logger, item: str, json_file: str) -> None:
    """Log the database build information
    Args:
        logger (logging.Logger): The logger object
        item (str): The database being built
        json_file (str): The JSON file being used as the source
    """
    logger.info("=========================================================")
    logger.info(f"==  Building {item} database")
    logger.info(f"==  Using {json_file} as the source file")
    logger.info("=========================================================")


def log_initial_info(logger: "logging.Logger", args: argparse.Namespace) -> None:
    """Log the initial configuration information
    Args:
        logger (logging.Logger): The logger object
        args (argparse.Namespace): The parsed command-line arguments
    """
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
    parser = argparse.ArgumentParser(
        description="""A tool for building a D&D 5E Notion Database from a JSON source file."""
    )

    parser.add_argument(
        "-b",
        "--build",
        nargs="+",
        type=str,
        required=True,
        help="""Select your database you want to build you can build selected databases or the whole package. 
        
        Example: 
            --build creatures weapon races
            --build all

        """,
    )

    # Define the command-line arguments
    parser.add_argument(
        "-db",
        "--database_id",
        type=str,
        required=True,
        help="""The Notion database ID where data will be stored. 
        
        Example: 
            --database_id "a674063b72a04deb8da26650db7294a5".""",
    )

    parser.add_argument(
        "-k",
        "--auth_key",
        type=str,
        required=True,
        help="""Your Notion API authentication key. 
        
        Example: 
            --auth_key "secret_**********************".""",
    )

    parser.add_argument(
        "-s",
        "--start_range",
        type=int,
        required=False,
        default=0,
        help="""The start of the range you want to build. 
        
        Example: 
            --start_range 3""",
    )

    parser.add_argument(
        "-e",
        "--end_range",
        type=int,
        required=False,
        default=None,
        help="""The end of the range you want to build. 
        
        Example: 
            --end_range 5""",
    )

    args = parser.parse_args()

    # == Check if "All" is by itself or with other options
    if "all" in args.build and len(args.build) > 1:
        raise argparse.ArgumentTypeError(
            'If "all" is specified, it must be the only build option.'
        )

    # == Check if the build options are valid
    if any(build not in VALID_BUILD_SET_1 + VALID_BUILD_SET_2 for build in args.build):
        raise argparse.ArgumentTypeError(
            f"\n\nInvalid build option(s):\n\nValid Set 1:\n\n{', '.join(VALID_BUILD_SET_1)}\n\nValid Set 2:\n\n{', '.join(VALID_BUILD_SET_2)}\n"
        )

    # == Call main() with the parsed arguments
    main(args)
