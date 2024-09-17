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


def build_magic_items_markdown(
    magic_item: object, notion: client, logger: logging.Logger, database_id: str
) -> list:
    # == This is all of the building of the api call for
    # == the markdown body
    # =======================================================

    # == Initializing the markdown children list
    # ==========
    markdown_children = []

    # == Adding header at the top
    # ==========
    add_section_heading(markdown_children, f"{magic_item.name}", level=1)

    for index, desc in enumerate(magic_item.desc):
        if index == 0:
            add_paragraph(markdown_children, desc)
            add_divider(markdown_children)
        else:
            add_paragraph(markdown_children, desc)

    return markdown_children
