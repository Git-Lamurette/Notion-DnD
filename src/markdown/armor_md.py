from src.utils.ability_modifier import ability_modifier
from src.markdown.children_md import (
    add_bulleted_list,
    add_paragraph,
    add_section_heading,
    add_table,
    add_divider,
    add_callout,
    add_numbered_list,
    add_quote,
)


def build_armor_markdown(equipment: object) -> list:
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(markdown_children, f"{equipment.name}", level=1)

    headers = [
        f"Type: {equipment.armor_category}",
        f"Cost: {equipment.cost['quantity']} {equipment.cost['unit']}",
        f"Weight: {equipment.get_weight()}",
    ]
    add_table(markdown_children, headers)
    add_divider(markdown_children)

    # == Attributes
    # ==========
    stats_table_headers = [
        "Name",
        "Cost",
        "Armor Class",
        "Strength",
        "Stealth",
        "Weight",
    ]
    stats_table_row = [
        f"{equipment.name}",
        f"{equipment.cost['quantity']} {equipment.cost['unit']}",
        f"{equipment.get_armor_class()}",
        f"{' -- ' if equipment.get_strength_requirement() == 0 else equipment.get_strength_requirement()}",
        f"{' -- ' if not equipment.stealth_disadvantage else "Disadvantage"}",
        f"{equipment.weight} lbs",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])

    return markdown_children
