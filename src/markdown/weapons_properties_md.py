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


def build_weapons_properties_markdown(weapons_properties_data: object) -> list:
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(
        markdown_children, f"{weapons_properties_data['name']}", level=1
    )
    add_divider(markdown_children)
    add_paragraph(
        markdown_children, "".join(desc for desc in weapons_properties_data["desc"])
    )

    return markdown_children
