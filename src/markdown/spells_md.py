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


def build_spells_markdown(
    spell: object, notion: client, logger: logging.Logger, database_id: str
) -> list:
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(markdown_children, f"{spell.name}", level=1)

    stats_table_headers = [
        "Level",
        "Casting Time",
        "Range/Area",
        "Components",
    ]

    stats_table_row = [
        f"{str(spell.level) if spell.level != 0 else "Cantrip"}",
        f"{spell.casting_time}",
        f"{spell.range}",
        f"{', '.join(spell.components)}{'*' if spell.material else ''}",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])

    stats_table_headers = [
        "Duration",
        "School",
        "Attack/Save",
        "Damage/Effect",
    ]

    stats_table_row = [
        f"{spell.duration}",
        f"{spell.school['name']}",
        f"{spell.get_attack_spell_save()}",
        f"{spell.get_damage_effect()}",
    ]
    add_table(markdown_children, stats_table_headers, [stats_table_row])
    add_divider(markdown_children)

    """
    headers = [
        f"Type: {spell.spell_category['name']}",
        f"Cost: {spell.cost['quantity']} {spell.cost['unit']}",
        f"Weight: {spell.get_weight()}",
    ]

    if spell.speed:
        speed: str = f"Speed: {spell.speed['quantity']} {spell.speed['unit']}"
        headers.append(speed)

    if spell.capacity:
        cap: str = f"Carry Weight: {spell.capacity}"
        headers.append(cap)

    add_table(markdown_children, headers)

    if spell.desc:
        add_divider(markdown_children)
        for desc in spell.desc:
            add_paragraph(markdown_children, desc)

    if spell.contents:
        add_divider(markdown_children)
        for content in spell.contents:
            add_paragraph(
                markdown_children, f"{content["quantity"]} x {content["item"]["name"]}"
            )
    """
    return markdown_children
