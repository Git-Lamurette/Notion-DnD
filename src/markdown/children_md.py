def add_paragraph(markdown_children: list, text: str, bold=False) -> None:
    """Make a markdown paragraph

    Args:
        markdown_children (list): You markdown list that contain all elements so far
        text (str): The content for the paragraph
    """
    import re

    # == Regular expression to find bold text
    bold_pattern = re.compile(r"\*\*\*(.*?)\*\*\*")

    # Split the text by the bold pattern
    split_text = bold_pattern.split(text)

    # Initialize the rich_text list
    rich_text = []

    for index, part in enumerate(split_text):
        if index % 2 == 0:
            # Regular text
            rich_text.append(
                {
                    "type": "text",
                    "text": {"content": part},
                    "annotations": {
                        "bold": bold,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                }
            )
        else:
            # Bold text
            rich_text.append(
                {
                    "type": "text",
                    "text": {"content": part},
                    "annotations": {
                        "bold": True,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                }
            )

    # Append the paragraph block with the rich_text list
    markdown_children.append(
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text}}
    )


def add_section_heading(markdown_children: list, text: str, level: int = 2) -> None:
    """Add a heading

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        text (str): The content for the heading
        level (int, optional): The heading style can do 1-3. Defaults to 2.
    """
    heading = {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }
    markdown_children.append(heading)


def add_bulleted_list(markdown_children: list, items: list) -> None:
    """Add a bullet list to your markdown

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        items (list): The list of your bulleted items, if you only send a single item it is supported but must have []
    """
    list_items = [
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": item}}]
            },
        }
        for item in items
    ]
    markdown_children.extend(list_items)


def add_numbered_list(markdown_children: list, items: list) -> None:
    """Add a numbered list to your markdown

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        items (list): The list of your numbered items, if you only send a single item it is supported but must have []
    """
    list_items = [
        {
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": item}}]
            },
        }
        for item in items
    ]
    markdown_children.extend(list_items)


def add_table(markdown_children: list, headers: list, rows: list = None) -> None:
    """Add a table to your markdown

    Example:
        Headers = ["Item 1", "Item 2", "Item 3"]
        Rows = [
            ["Data 1", "Data 2", "Data 3"],
            ["Data 4", "Data 5", "Data 6"],
        ]

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        headers (list): The headers for your table
        rows (list, optional): The rows for your table. Defaults to None.
    """
    table_width = len(headers)

    # Construct header row
    header_row = {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [
                [{"type": "text", "text": {"content": header}}] for header in headers
            ]
        },
    }

    # Construct data rows if provided
    data_rows = []
    if rows:
        data_rows = [
            {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [
                        [{"type": "text", "text": {"content": cell}}] for cell in row
                    ]
                },
            }
            for row in rows
        ]

    # Construct the full table block
    table = {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": True,
            "children": [header_row] + data_rows,
        },
    }

    # Append the table to markdown_children list
    markdown_children.append(table)


def add_divider(markdown_children: list) -> None:
    """Generates a simple divider line

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
    """
    divider = {"object": "block", "type": "divider", "divider": {}}
    markdown_children.append(divider)


def add_quote(markdown_children: list, text: str) -> None:
    """Added a quoted block of text

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        text (str): The text for the quote
    """
    quote = {
        "object": "block",
        "type": "quote",
        "quote": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }
    markdown_children.append(quote)


def add_callout(
    markdown_children: list,
    text: str,
    color: str = "blue_background",
    icon: str = None,
) -> None:
    """Add a callout box

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        text (str): The text for the callout
        color (str, optional): The color for the callout, there is a verified list. Defaults to "blue_background".
        icon (str, optional): An emoji icon. Defaults to None.

    Raises:
        ValueError: If the color is not supported
    """

    supported_colors = [
        "blue",
        "blue_background",
        "brown",
        "brown_background",
        "default",
        "gray",
        "gray_background",
        "green",
        "green_background",
        "orange",
        "orange_background",
        "yellow",
        "pink",
        "pink_background",
        "purple",
        "purple_background",
        "red",
        "red_background",
        "yellow_background",
    ]

    if color not in supported_colors:
        raise ValueError(
            f"Color '{color}' is not supported. Supported colors are: {', '.join(supported_colors)}"
        )

    callout = {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "color": color,
        },
    }

    if icon is not None:
        callout["callout"]["icon"] = {"emoji": icon}

    markdown_children.append(callout)
