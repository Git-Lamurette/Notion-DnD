from notion_client import client
import logging
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


def build_items_markdown(
    equipment: object, notion: client, logger: logging.Logger, database_id: str
) -> list:
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
        f"Type: {equipment.equipment_category['name']}",
        f"Cost: {equipment.cost['quantity']} {equipment.cost['unit']}",
        f"Weight: {equipment.get_weight()}",
    ]

    if equipment.speed:
        speed: str = f"Speed: {equipment.speed['quantity']} {equipment.speed['unit']}"
        headers.append(speed)

    if equipment.capacity:
        cap: str = f"Carry Weight: {equipment.capacity}"
        headers.append(cap)

    add_table(markdown_children, headers)

    if equipment.desc:
        add_divider(markdown_children)
        for desc in equipment.desc:
            add_paragraph(markdown_children, desc)

    if equipment.contents:
        add_divider(markdown_children)
        for content in equipment.contents:
            add_paragraph(
                markdown_children, f"{content["quantity"]} x {content["item"]["name"]}"
            )

    return markdown_children
