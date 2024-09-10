from notion_client import Client
from notion_client.errors import APIResponseError
from src.util.load_json import load_data, _Creature
from src.util.children_func import (
    add_columns,
    add_bulleted_list,
    add_numbered_list,
    add_paragraph,
    add_section_heading,
    add_table,
    add_divider,
)

# py-dm-tk call main program window.
NAME = "Notion 5E Database Builder"
DESCRIPTION = "Convert json data into a Notion CSV and MD files"
VERSION = "0.0.1"
DATA_DIRECTORY = "src/data"
notion = Client(auth="secret_8fDt3EJbAlcH0tWh6u26x5RfTBVkfHZYW9nUUN6K1gU")
database_id = "997bb9bb0bc048ecb6c06523c4af66aa"  # type: ignore
print("Database created with ID:", database_id)


def ability_modifier(number):
    # Calculating abilit score modifiers
    ability_table = [
        ("1", "-5"),
        ("2-3", "-4"),
        ("4-5", "-3"),
        ("6-7", "-2"),
        ("8-9", "-1"),
        ("10-11", "0"),
        ("12-13", "+1"),
        ("14-15", "+2"),
        ("16-17", "+3"),
        ("18-19", "+4"),
        ("20-21", "+5"),
        ("22-23", "+6"),
        ("24-25", "+7"),
        ("26-27", "+8"),
        ("28-29", "+9"),
        ("30", "+10"),
    ]

    for range, value in ability_table:
        if "-" in range:
            start, end = map(int, range.split("-"))
            if start <= number <= end:
                return value
        elif int(range) == number:
            return value


def build_children_blocks(monster):
    # =======================================================
    # ==  All of the pre work is here for string manipulation
    # =======================================================

    # monster = _Creature(**x)

    # ==  Parsing speed
    parsed_speed = [
        f"{Movement}: {Distance}" for Movement, Distance in monster.speed.items()
    ]
    parsed_speed = " - ".join([x.capitalize() for x in parsed_speed])

    # ==  Armor parsing
    parsed_armor = []
    for armor in monster.armor_class:
        if "spell" in armor:
            parsed_armor.append(
                f"{armor['type'].capitalize()} {armor['value']} : {armor['spell']['name']}"
            )
        elif "condition" in armor:
            parsed_armor.append(
                f"{armor['type'].capitalize()} {armor['value']} : {armor['condition']['name']}"
            )
        elif "armor" in armor:
            for x in armor["armor"]:
                parsed_armor.append(
                    f"{armor['type'].capitalize()} {armor['value']} : {x['name']}"
                )
        else:
            parsed_armor.append(f"{armor['type'].capitalize()} {armor['value']}")
    parsed_armor = " - ".join(parsed_armor)

    # ==  Building list for basic info
    basic_info_list = [
        f"Armor Class : {parsed_armor}",
        f"Hit Points : {monster.hit_points} ( {monster.hit_points_roll} )",
        f"Speed : {parsed_speed}",
    ]
    # =======================================================
    # ==  End of pre work
    # =======================================================
    # ==
    # =======================================================
    # ==  This is all of the building of the api call for
    # ==  the markdown body
    # =======================================================

    # ==  Initializing all the blank list
    left_column_content = []
    right_column_content = []
    children = []

    # ==  Adding header at the top
    add_section_heading(children, f"{monster.name}", level=1)
    add_paragraph(
        children,
        f"{monster.size.capitalize()} {monster.type.capitalize()} , {monster.alignment}",
    )
    add_divider(children)

    # ==  Adding basic info
    add_bulleted_list(right_column_content, basic_info_list)
    add_divider(children)

    # == Stats Section
    add_section_heading(left_column_content, "Stats", level=2)
    stats_table_headers = ["STR", "Value"]
    stats_table_rows = [
        ["Strength", (f"{monster.strength}")],
        ["Dexterity", (f"{monster.dexterity}")],
        ["Constitution", (f"{monster.constitution}")],
        ["Intelligence", (f"{monster.intelligence}")],
        ["Wisdom", (f"{monster.wisdom}")],
        ["Charisma", (f"{monster.charisma}")],
    ]
    add_table(left_column_content, stats_table_headers, stats_table_rows)
    add_divider(children)

    # Add columns to the children
    add_columns(children, left_column_content, right_column_content)

    return children


def main():
    # Get Monster Data
    creature_data = load_data(DATA_DIRECTORY)

    # Iterates through the monster JSON
    for x in creature_data:

        # Makes the creature as a data class
        monster = _Creature(**x)
        if monster.name == "Aboleth":
            try:

                children = build_children_blocks(monster)

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
                        "Hit Points": {"number": monster.hit_points},
                        "Movement Type": {
                            "multi_select": [
                                {"name": mt.capitalize()} for mt in monster.speed
                            ]
                        },
                    },
                    children=children,
                )
                print(f"Page created for {monster.name} with ID: {response['id']}")  # type: ignore
            except APIResponseError as e:
                print(f"An API error occurred: {e}")


if __name__ == "__main__":
    main()
