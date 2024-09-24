from src.utils.load_json import load_data
from src.api.notion_api import create_page, create_database
from typing import TYPE_CHECKING, Union
from time import sleep

if TYPE_CHECKING:
    import logging
    from notion_client import client


def build_classes_database(logger, notion, data_directory, json_file, args):
    classes_db_id = classes_db(logger, notion, args.database_id)
    classes_page(
        logger,
        notion,
        data_directory,
        json_file,
        classes_db_id,
        args.start_range,
        args.end_range,
    )


def classes_page(
    logger: "logging.Logger",
    notion: "client",
    data_directory: str,
    json_file: str,
    database_id: str,
    start: int,
    end: Union[None, int],
) -> None:
    """This generates the api calls needed for Notion. This parses the JSON and build the markdown body for the API call.
    It iterates through each classes in the json depending on params.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client objext
        data_directory (str): Path to the json you are parsing
        database_id (str): Your database ID - This must be a page cannot be another database
        start (int): If you want to only capture a range specify the start
        end (Union[None, int]): If you want to only capture a range specify the end
    """
    # == Get classes Data
    classes_data = load_data(logger, data_directory, json_file)

    # == Apply range to classes data
    if end is None or end > len(classes_data):
        end = len(classes_data)

    # == Iterates through the specified range of the classes JSON
    for index in range(start, end):
        class_json = classes_data[index]

        logger.info(
            f"Building Markdown for classes -- {class_json['name']} -- Index -- {index} --"
        )

        # == Building markdown properties from _classes class
        markdown_properties = {
            "Class": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": class_json['name'].capitalize()},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Classes"}},
            "Hit Die": {
                "rich_text": [
                    {"type": "text", "text": {"content": f"d {class_json['hit_die']}"}}
                ]
            },
            "Subclass": {"multi_select": [{"name": clas['name'].capitalize() for clas in class_json['subclasses']}]},
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for classes
        #children_properties = build_weapon_markdown(logger, notion, classes)

        # == Sending api call
        # ==========
        create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        sleep(0.5)


def classes_db(logger: "logging.Logger", notion: "client", database_id: str) -> str:
    """This generates the api calls needed for Notion. This just builds the empty database page with the required options.

    Args:
        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID

    Returns:
        str: Database ID
    """

    # == Database Name
    database_name = "Classes"

    # == Building markdown database properties
    database_weapon_properties = {
        "Class": {"title": {}},
        "Hit Die": {"rich_text": {}},
        "5E Category": {"select": {"options": [{"name": "Classes", "color": "green"}]}},
        "Subclass": {
            "multi_select": {
                "options": [
                    {"name": "Berserker", "color": "gray"},
                    {"name": "Champion", "color": "green"},
                    {"name": "Devotion", "color": "yellow"},
                    {"name": "Draconic", "color": "blue"},
                    {"name": "Evocation", "color": "red"},
                    {"name": "Fiend", "color": "orange"},
                    {"name": "Hunter", "color": "pink"},
                    {"name": "Land", "color": "purple"},
                    {"name": "Life", "color": "brown"},
                    {"name": "Lore", "color": "gray"},
                    {"name": "Open Hand", "color": "green"},
                    {"name": "Thief", "color": "yellow"}
                ]
            }
        }
    }

    return create_database(
        logger, notion, database_id, database_name, database_weapon_properties
    )


def build_weapon_markdown(
    logger: "logging.Logger", notion: "client", classes_prop: object
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
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
    add_section_heading(markdown_children, f"{classes_prop['name']}", level=1)
    add_divider(markdown_children)
    headers = [
        f"Type: {classes_prop.category_range}",
        f"Cost: {classes_prop.cost['quantity']} {classes_prop.cost['unit']}",
        f"Weight: {classes_prop.get_weight()}",
    ]
    add_table(markdown_children, headers)
    add_divider(markdown_children)

    if classes_prop.special:
        for special in classes_prop.special:
            add_paragraph(markdown_children, special)
        add_divider(markdown_children)

    # == Attributes
    # ==========

    # == Need to capture the rich text to then add into the table structure
    stats_table_headers = ["Name", "Cost", "Damage", "Weight", "Properties", "Range"]

    # == Make the string for the values
    text_string = f"{" ".join(prop for prop in classes.get_properties())}"

    rich_text = add_paragraph_with_mentions(
        logger,
        notion,
        markdown_children,
        text_string,
        [text_string],
        "Weapon Properties",
        ret=True,
    )

    stats_table_row = [
        f"{classes.name}",
        f"{classes.cost['quantity']} {classes.cost['unit']}",
        f"{classes.get_damage_dice()}",
        f"{classes.weight} lbs",
        rich_text,
        f"{classes.get_range()}",
    ]

    add_table(markdown_children, stats_table_headers, [stats_table_row])

    return markdown_children
