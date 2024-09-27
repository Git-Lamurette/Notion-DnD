# from Experiement.test import add_bulleted_list
from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_races_database(logger, notion, data_directory, json_file, args):
    races_db_id = races_db(logger, notion, args.database_id)
    races_page(
        logger,
        notion,
        data_directory,
        json_file,
        races_db_id,
        args.start_range,
        args.end_range,
    )


def races_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_divider,
    )

    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each races in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get races Data
    races_data = load_data(logger, data_directory, json_file)
    traits_data = load_data(logger, data_directory, "5e-SRD-Traits.json")
    subraces_data = load_data(logger, data_directory, "5e-SRD-Subraces.json")

    # == Apply range to races data
    if end is None or end > len(races_data):
        end = len(races_data)

    # == Iterates through the specified range of the races JSON
    for index in range(start, end):
        races_json = races_data[index]

        logger.info(
            f"Building Markdown for races -- {races_json['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _races class
        markdown_properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": races_json["name"].capitalize()},
                    }
                ]
            },
            "Speed": {
                "rich_text": [
                    {"type": "text", "text": {"content": f"{races_json['speed']} ft."}}
                ]
            },
            "Ability Bonus": {
                "multi_select": [
                    {"name": f"+{bonus} {name}"}
                    for name, bonus in [
                        (abil["ability_score"]["name"], abil["bonus"])
                        for abil in races_json["ability_bonuses"]
                    ]
                ]
            },
            "5E Category": {"select": {"name": "Races"}},
            "Subrace": {
                "multi_select": [
                    {"name": subrace["name"].capitalize()}
                    for subrace in races_json["subraces"]
                ]
            },
            "Size": {"select": {"name": f"{races_json["size"].capitalize()}"}},
            "Languages": {
                "multi_select": [
                    {"name": language["name"].capitalize()}
                    for language in races_json["languages"]
                ]
            },
            "Traits": {
                "multi_select": [
                    {"name": trait["name"].capitalize()}
                    for trait in races_json["traits"]
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for races
        children_properties = build_races_markdown(
            logger, notion, races_json, traits_data, subraces_data
        )

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def races_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Races"

    # == Building markdown database properties
    database_races_properties = {
        "Name": {"title": {}},
        "Speed": {"rich_text": {}},
        "Ability Bonus": {
            "multi_select": {
                "options": [
                    {"name": "+1 INT", "color": "blue"},
                    {"name": "+1 CHA", "color": "red"},
                    {"name": "+1 DEX", "color": "yellow"},
                    {"name": "+1 CON", "color": "purple"},
                    {"name": "+1 STR", "color": "orange"},
                    {"name": "+1 WIS", "color": "pink"},
                    {"name": "+2 INT", "color": "brown"},
                    {"name": "+2 CHA", "color": "gray"},
                    {"name": "+2 DEX", "color": "blue"},
                    {"name": "+2 CON", "color": "red"},
                    {"name": "+2 STR", "color": "yellow"},
                    {"name": "+2 WIS", "color": "purple"},
                ]
            }
        },
        "5E Category": {
            "select": {
                "options": [
                    {"name": "Races", "color": "purple"},
                ]
            }
        },
        "Subrace": {
            "multi_select": {
                "options": [
                    {"name": "Small", "color": "blue"},
                    {"name": "Medium", "color": "green"},
                ]
            }
        },
        "Size": {
            "select": {
                "options": [
                    {"name": "Small", "color": "blue"},
                    {"name": "Medium", "color": "green"},
                ]
            }
        },
        "Languages": {
            "multi_select": {
                "options": [
                    {"name": "Common", "color": "gray"},
                    {"name": "Draconic", "color": "blue"},
                    {"name": "Dwarvish", "color": "brown"},
                    {"name": "Elvish", "color": "green"},
                    {"name": "Gnomish", "color": "purple"},
                    {"name": "Halfling", "color": "yellow"},
                    {"name": "Infernal", "color": "red"},
                    {"name": "Orc", "color": "orange"},
                ]
            }
        },
        "Traits": {
            "multi_select": {
                "options": [
                    {"name": "Brave", "color": "gray"},
                    {"name": "Breath Weapon", "color": "blue"},
                    {"name": "Damage Resistance", "color": "red"},
                    {"name": "Darkvision", "color": "default"},
                    {"name": "Draconic Ancestry", "color": "yellow"},
                    {"name": "Dwarven Combat Training", "color": "brown"},
                    {"name": "Dwarven Resilience", "color": "brown"},
                    {"name": "Fey Ancestry", "color": "green"},
                    {"name": "Gnome Cunning", "color": "purple"},
                    {"name": "Halfling Nimbleness", "color": "yellow"},
                    {"name": "Hellish Resistance", "color": "red"},
                    {"name": "Infernal Legacy", "color": "red"},
                    {"name": "Keen Senses", "color": "blue"},
                    {"name": "Lucky", "color": "green"},
                    {"name": "Menacing", "color": "default"},
                    {"name": "Relentless Endurance", "color": "gray"},
                    {"name": "Savage Attacks", "color": "red"},
                    {"name": "Skill Versatility", "color": "blue"},
                    {"name": "Stonecunning", "color": "gray"},
                    {"name": "Tool Proficiency", "color": "orange"},
                    {"name": "Trance", "color": "purple"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_races_properties
    )


def build_races_markdown(
    logger: "logging.Logger",
    notion: "client",
    races_json: object,
    traits_json: object,
    subraces_json: object,
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
        add_divider,
    )
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    ability_bonus = ", ".join(
        f"+{bonus} {name}"
        for name, bonus in [
            (abil["ability_score"]["name"], abil["bonus"])
            for abil in races_json["ability_bonuses"]
        ]
    )
    # == Adding header at the top
    # ==========

    add_section_heading(markdown_children, f"{races_json['name']}", level=1)
    add_section_heading(markdown_children, f"{races_json['name']} Traits", level=2)
    add_divider(markdown_children)
    add_paragraph(
        markdown_children,
        f"**Ability Score Increase.** {ability_bonus}",
    )
    add_paragraph(
        markdown_children,
        f"**Age.** {races_json['age']}",
    )
    add_paragraph(
        markdown_children,
        f"**Alignment.** {races_json['alignment']}",
    )
    add_paragraph(
        markdown_children,
        f"**Size.** {races_json['size_description']}",
    )
    add_paragraph(
        markdown_children,
        f"**Speed.** Your base walking speed is {races_json['speed']} feet.",
    )

    # == Draconic Ancestry Table
    # =============================
    draconic_header = ["Dragon", "Damage Type", "Breath Weapon"]
    draconic_body = []
    for trait in traits_json:
        if trait.get("parent"):
            if trait["parent"]["name"] == "Draconic Ancestry":
                draconic_body.append(
                    [
                        f"{trait["name"]}",
                        f"{trait["trait_specific"]['damage_type']['name']}",
                        f"{trait["trait_specific"]['breath_weapon']['area_of_effect']["size"]} ft. {trait["trait_specific"]['breath_weapon']['area_of_effect']["type"]} ({trait["trait_specific"]['breath_weapon']['dc']["dc_type"]["name"].capitalize()}. save) ",
                    ]
                )

    # == Rest of Traits
    # =============================
    for name in races_json["traits"]:
        for trait in traits_json:
            if name["name"] == trait["name"]:
                if name["name"] == "Draconic Ancestry":
                    add_table(markdown_children, draconic_header, draconic_body)
                add_paragraph(
                    markdown_children,
                    f"**{trait['name']}.** {" ".join(x for x in trait['desc'])}",
                )

    add_paragraph(
        markdown_children,
        f"**Languages.** {races_json['language_desc']} feet.",
    )

    if races_json["subraces"]:
        for sub in races_json["subraces"]:
            for subrace in subraces_json:
                if sub["name"] == subrace["name"]:
                    add_section_heading(
                        markdown_children, f"{subrace['name']}", level=3
                    )
                    add_paragraph(
                        markdown_children,
                        subrace["desc"],
                    )
                    add_divider(markdown_children)
                    if subrace.get("ability_bonuses"):
                        ability_bonus = ", ".join(
                            f"+{bonus} {name}"
                            for name, bonus in [
                                (abil["ability_score"]["name"], abil["bonus"])
                                for abil in subrace["ability_bonuses"]
                            ]
                        )
                        add_paragraph(
                            markdown_children,
                            f"**Ability Score Increase.** {ability_bonus}",
                        )

                    if subrace.get("racial_traits"):
                        for sub_trait in subrace["racial_traits"]:
                            for trait in traits_json:
                                if sub_trait["name"] == trait["name"]:
                                    add_paragraph(
                                        markdown_children,
                                        f"**{trait['name']}.** {" ".join(x for x in trait['desc'])}",
                                    )

    return markdown_children
