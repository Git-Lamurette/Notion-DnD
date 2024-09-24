# from Experiement.test import add_bulleted_list
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
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
        add_divider,
        add_paragraph_with_mentions,
        add_expandable_toggle,
        add_bulleted_list,
    )

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
    features_data = load_data(logger, data_directory, "5e-SRD-Features.json")
    level_data = load_data(logger, data_directory, "5e-SRD-Levels.json")

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
                        "text": {"content": class_json["name"].capitalize()},
                    }
                ]
            },
            "5E Category": {"select": {"name": "Classes"}},
            "Hit Die": {
                "rich_text": [
                    {"type": "text", "text": {"content": f"d {class_json['hit_die']}"}}
                ]
            },
            "Subclass": {
                "multi_select": [
                    {
                        "name": clas["name"].capitalize()
                        for clas in class_json["subclasses"]
                    }
                ]
            },
        }

        # == Ensure children_properties list is empty
        children_properties = []

        # == Building markdown for classes
        children_properties = build_classes_markdown(
            logger, notion, class_json, features_data, level_data
        )

        # == Sending api call
        # ==========
        created_page = create_page(
            logger, notion, database_id, markdown_properties, children_properties
        )

        """
        list_of_desc = features_data["desc"].split("\n")
        temp = []

        for desc in list_of_desc:
            add_paragraph(temp, desc)
            if len(temp) >= 100:
                notion.blocks.children.append(block_id=created_page, children=temp)
                temp = []

        # Append any remaining elements in temp

        """
        # == Class Features
        # ==========================================================

        feature_list = (
            [
                feat
                for feat in features_data
                if feat["class"]["name"].lower() == class_json["name"].lower()
            ]
            if features_data
            else []
        )

        temp_markdown = []

        for feat in feature_list:
            add_section_heading(temp_markdown, feat["name"], level=2)
            add_paragraph(temp_markdown, f"Level: {feat['level']}")
            add_divider(temp_markdown)
            if feat["desc"]:
                for f in feat["desc"]:
                    add_paragraph(temp_markdown, f)
            if len(temp_markdown) >= 90:
                notion.blocks.children.append(
                    block_id=created_page, children=temp_markdown
                )
                temp_markdown = []

        if temp_markdown:
            notion.blocks.children.append(block_id=created_page, children=temp_markdown)

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
    database_classes_properties = {
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
                    {"name": "Thief", "color": "yellow"},
                ]
            }
        },
    }

    return create_database(
        logger, notion, database_id, database_name, database_classes_properties
    )


def build_classes_markdown(
    logger: "logging.Logger",
    notion: "client",
    classes_prop: object,
    features_data: list,
    levels_data: list,
) -> list:
    from src.builds.children_md import (
        add_paragraph,
        add_section_heading,
        add_table,
        add_divider,
        add_paragraph_with_mentions,
        add_expandable_toggle,
        add_bulleted_list,
    )
    from pprint import pprint
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(markdown_children, f"{classes_prop['name']}", level=1)
    add_paragraph(markdown_children, f"Hit Die - d{classes_prop['hit_die']}")
    add_divider(markdown_children)
    add_section_heading(markdown_children, "Class Features", level=2)
    add_paragraph(
        markdown_children,
        f"As a {classes_prop['name']}, you gain the following class features.",
    )
    # == Adding class features
    add_section_heading(markdown_children, "Proficiencies", level=3)

    prop = []
    for prof in classes_prop["proficiencies"]:
        prop.append(
            add_paragraph_with_mentions(
                logger,
                notion,
                markdown_children,
                prof["name"],
                [prof["name"]],
                ret=True,
            )
        )

    if prop:
        add_expandable_toggle(
            markdown_children,
            "Click to Expand...",
            prop,
            color="default",
        )

    for prof in classes_prop["proficiency_choices"]:
        all_thing = []
        add_section_heading(markdown_children, f"{prof['desc']}", level=3)

        for sub in prof["from"]["options"]:
            if sub.get("item"):
                all_thing.append(
                    add_paragraph_with_mentions(
                        logger,
                        notion,
                        markdown_children,
                        sub["item"]["name"],
                        [sub["item"]["name"]],
                        ret=True,
                    )
                )

            if sub.get("choice"):
                for op in sub["choice"]["from"]["options"]:
                    all_thing.append(
                        add_paragraph_with_mentions(
                            logger,
                            notion,
                            markdown_children,
                            op["item"]["name"],
                            [op["item"]["name"]],
                            ret=True,
                        )
                    )

        if all_thing:
            add_expandable_toggle(
                markdown_children,
                "Click to Expand...",
                all_thing,
                color="default",
            )

    # == Equipment Section
    # ==========================================================
    add_section_heading(markdown_children, "Equipment", level=3)
    add_paragraph(
        markdown_children,
        "You start with the following equipment, in addition to the equipment granted by your background:",
    )

    starting_equp = [
        " - ".join(
            [
                f"{equip['equipment']['name']} (Quantity: {equip['quantity']})"
                for equip in classes_prop["starting_equipment"]
            ]
        )
    ]

    optional_equp = [
        f"{equip['desc']}" for equip in classes_prop["starting_equipment_options"]
    ]

    starting_equp.extend(optional_equp)
    add_bulleted_list(markdown_children, starting_equp)

    # == Class Tables - Might be hardcoded for all classes
    # ==========================================================
    feature_list = (
        [
            feat
            for feat in levels_data
            if feat["class"]["name"].lower() == classes_prop["name"].lower()
        ]
        if features_data
        else []
    )

    add_section_heading(markdown_children, f"The {classes_prop['name']}", level=3)
    add_divider(markdown_children)

    # == Fighter Table
    if feature_list[0]["class"]["name"].lower() == "fighter":
        header = ["Level", "Proficiency Bonus", "Features"]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            body.append(
                [
                    f"{ordinal(feat.get('level', ' '))}",
                    f"+{feat.get('prof_bonus', ' ')}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                ]
            )

    # == Barbarian Table
    if feature_list[0]["class"]["name"].lower() == "barbarian":
        header = ["Level", "Proficiency Bonus", "Features", "Rages", "Rage Damage"]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            body.append(
                [
                    f"{ordinal(feat.get('level', ' '))}",
                    f"+{feat.get('prof_bonus', ' ')}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                    f"{feat['class_specific']['rage_count']}",
                    f"+{feat['class_specific']['rage_damage_bonus']}",
                ]
            )

    # == Rogue Table
    if feature_list[0]["class"]["name"].lower() == "rogue":
        header = ["Level", "Proficiency Bonus", "Sneak Attack", "Features"]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue

            class_specific = feat.get("class_specific", {})
            features = ", ".join(feature["name"] for feature in feat["features"])
            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{class_specific['sneak_attack']['dice_count']}d{class_specific['sneak_attack']['dice_value']}",
                    features,
                ]
            )

    # == Monk Table
    if feature_list[0]["class"]["name"].lower() == "monk":
        header = [
            "Level",
            "Proficiency Bonus",
            "Martial Arts",
            "Ki Points",
            "Unarmored Movement",
            "Features",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            class_specific = feat.get("class_specific", {})
            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{class_specific['martial_arts'].get('dice_count')}d{class_specific['martial_arts'].get('dice_value')} ",
                    f"{format_spell_slot(class_specific.get('ki_points'))}",
                    f"+{class_specific.get('unarmored_movement', ' ')} ft.",
                    ", ".join(feature["name"] for feature in feat["features"]),
                ]
            )

    # == Bard
    if feature_list[0]["class"]["name"].lower() == "bard":
        header = [
            "Level",
            "Proficiency Bonus",
            "Features",
            "Cantrips Known",
            "Spells Known",
            "Spell Slots 1st",
            "Spell Slots 2nd",
            "Spell Slots 3rd",
            "Spell Slots 4th",
            "Spell Slots 5th",
            "Spell Slots 6th",
            "Spell Slots 7th",
            "Spell Slots 8th",
            "Spell Slots 9th",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})

            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                    f"{spellcasting.get('cantrips_known', ' - ')}",
                    f"{spellcasting.get('spells_known', ' - ')}",
                    format_spell_slot(spellcasting.get("spell_slots_level_1", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_2", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_3", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_4", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_5", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_6", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_7", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_8", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_9", " - ")),
                ]
            )

    # == Cleric + Druid
    table_list1 = ["cleric", "druid", "wizard"]
    if feature_list[0]["class"]["name"].lower() in table_list1:
        header = [
            "Level",
            "Proficiency Bonus",
            "Features",
            "Cantrips Known",
            "Spell Slots 1st",
            "Spell Slots 2nd",
            "Spell Slots 3rd",
            "Spell Slots 4th",
            "Spell Slots 5th",
            "Spell Slots 6th",
            "Spell Slots 7th",
            "Spell Slots 8th",
            "Spell Slots 9th",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})

            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                    f"{spellcasting.get('cantrips_known', ' - ')}",
                    format_spell_slot(spellcasting.get("spell_slots_level_1", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_2", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_3", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_4", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_5", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_6", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_7", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_8", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_9", " - ")),
                ]
            )

    # == Paladin
    if feature_list[0]["class"]["name"].lower() == "paladin":
        header = [
            "Level",
            "Proficiency Bonus",
            "Features",
            "Spell Slots 1st",
            "Spell Slots 2nd",
            "Spell Slots 3rd",
            "Spell Slots 4th",
            "Spell Slots 5th",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})

            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                    format_spell_slot(spellcasting.get("spell_slots_level_1", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_2", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_3", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_4", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_5", " - ")),
                ]
            )

    # == Ranger
    if feature_list[0]["class"]["name"].lower() == "ranger":
        header = [
            "Level",
            "Proficiency Bonus",
            "Features",
            "Spells Known",
            "Spell Slots 1st",
            "Spell Slots 2nd",
            "Spell Slots 3rd",
            "Spell Slots 4th",
            "Spell Slots 5th",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})

            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    f"{' '.join(feat['name'] for feat in feat['features'])}",
                    format_spell_slot(spellcasting.get("spells_known", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_1", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_2", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_3", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_4", " - ")),
                    format_spell_slot(spellcasting.get("spell_slots_level_5", " - ")),
                ]
            )

    # == Sorcerer
    if feature_list[0]["class"]["name"].lower() == "sorcerer":
        header = [
            "Level",
            "Proficiency Bonus",
            "Sorcery Points",
            "Features",
            "Cantrips Known",
            "Spells Known",
            "Spell Slots 1st",
            "Spell Slots 2nd",
            "Spell Slots 3rd",
            "Spell Slots 4th",
            "Spell Slots 5th",
            "Spell Slots 6th",
            "Spell Slots 7th",
            "Spell Slots 8th",
            "Spell Slots 9th",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})
            class_specific = feat.get("class_specific", {})

            body.append(
                [
                    f"{ordinal(feat['level'])}",
                    f"+{feat['prof_bonus']}",
                    format_spell_slot(class_specific.get("sorcery_points", " - ")),
                    ", ".join(feature["name"] for feature in feat["features"]),
                    f"{spellcasting.get('cantrips_known', ' - ')}",
                    f"{spellcasting.get('spells_known', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_1', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_2', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_3', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_4', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_5', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_6', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_7', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_8', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_9', ' - ')}",
                ]
            )

    # == Warlock
    if feature_list[0]["class"]["name"].lower() == "warlock":
        header = [
            "Level",
            "Proficiency Bonus",
            "Features",
            "Cantrips Known",
            "Spells Known",
            "Spell Slots",
            "Slot Level",
            "Invocations Known",
        ]
        body = []
        for feat in feature_list:
            if feat.get("subclass"):
                continue
            spellcasting = feat.get("spellcasting", {})
            class_specific = feat.get("class_specific", {})

            body.append(
                [
                    f"{feat['level']}",
                    f"+{feat['prof_bonus']}",
                    ", ".join(feature["name"] for feature in feat["features"]),
                    f"{spellcasting.get('cantrips_known', ' - ')}",
                    f"{spellcasting.get('spells_known', ' - ')}",
                    f"{spellcasting.get('spell_slots_level_1', ' - ')}",
                    f"{class_specific.get('spell_slot_level', ' - ')}",
                    format_spell_slot(class_specific.get("invocations_known", " - ")),
                ]
            )

    add_table(markdown_children, header, body)

    # == Spellcasting
    # ==========================================================
    if classes_prop.get("spellcasting"):
        add_section_heading(markdown_children, "Spellcasting", level=1)
        add_divider(markdown_children)
        for info in classes_prop["spellcasting"]["info"]:
            add_section_heading(markdown_children, info["name"], level=3)
            for des in info["desc"]:
                add_paragraph(markdown_children, des)

    return markdown_children


def ordinal(n):
    """Convert an integer to its ordinal representation."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_spell_slot(value):
    """Format spell slot value, replacing 0 with ' - '."""
    return " - " if value == 0 else str(value)
