from notion_client import Client
import re
from typing import Union


def add_paragraph_with_mentions(
    logger,
    notion: Client,
    markdown_children: list,
    text: str,
    mention_keywords: list,
    exclude_tag: str = "",
    include_tags: str = "",
    ret=False,
) -> Union[None, list]:
    from pprint import pprint

    """Add a paragraph with mentions of specific keywords

    Args:
        logger (logging.Logger): Logging object
        notion (Client): The Notion client
        markdown_children (list): Your markdown list that contains all elements so far
        text (str): The text content for the paragraph
        mention_keywords (list): List of keywords to mention
        ret (bool): Whether to return the rich_text list

    Returns:
        Union[None, list]: The rich_text list if ret is True, otherwise None
    """

    # Create a regex pattern that matches any of the keywords
    pattern = "|".join(map(re.escape, mention_keywords))

    # Split the text and keep the keywords using parentheses
    split_text = re.split(f"({pattern})", text)

    rich_text = []

    for word in split_text:
        if word in mention_keywords:
            # Define the filter for the search query

            filt = {
                "value": "page",
                "property": "object",
            }

            # logger.info(f"Filter: {filt}")
            # Search for the page to mention
            results = notion.search(query=word, filter=filt).get("results")
            # pprint(f"results: {results}")

            if include_tags or exclude_tag:
                filtered_results = [
                    res
                    for res in results
                    if (
                        include_tags == ""
                        or res["properties"]
                        .get("5E Category", {})
                        .get("select", {})
                        .get("name")
                        == include_tags
                    )
                    and (
                        exclude_tag == ""
                        or res["properties"]
                        .get("5E Category", {})
                        .get("select", {})
                        .get("name")
                        != exclude_tag
                    )
                ]
            else:
                filtered_results = results

            if len(filtered_results) == 0:
                rich_text.append({"type": "text", "text": {"content": word}})
            else:
                for res in filtered_results:
                    if res["properties"].get("Name"):
                        captured_word = res["properties"]["Name"]["title"][0]["text"][
                            "content"
                        ]
                        if word.lower() == captured_word.lower():
                            mentioned_page_id = res["id"]
                            rich_text.append(
                                {
                                    "type": "mention",
                                    "mention": {"page": {"id": mentioned_page_id}},
                                }
                            )

        else:
            rich_text.append({"type": "text", "text": {"content": word}})

    paragraph_content = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text},
    }

    if ret:
        return rich_text

    markdown_children.append(paragraph_content)

    return None


def add_paragraph(markdown_children: list, text: str) -> None:
    """Add a paragraph to the markdown children list with formatting checks.

    Args:
        markdown_children (list): The list of markdown elements.
        text (str): The text content for the paragraph.
    """
    # Check for headings with ## this is a title
    heading_pattern_4 = re.compile(r"##### (.*)")
    heading_pattern_3 = re.compile(r"#### (.*)")
    heading_pattern_2 = re.compile(r"### (.*)")
    heading_pattern_1 = re.compile(r"## (.*)")

    if heading_pattern_3.match(text) or heading_pattern_4.match(text):
        heading_text = heading_pattern_3.sub(r"\1", text)
        markdown_children.append(
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                },
            }
        )
        return

    if heading_pattern_2.match(text):
        heading_text = heading_pattern_2.sub(r"\1", text)
        markdown_children.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                },
            }
        )
        return

    if heading_pattern_1.match(text):
        heading_text = heading_pattern_1.sub(r"\1", text)
        markdown_children.append(
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": heading_text}}]
                },
            }
        )
        return

    # Check for bold italic formatting with ***word***
    bold_italic_pattern = re.compile(r"\*\*\*(.*?)\*\*\*")
    text = bold_italic_pattern.sub(r"<strong><em>\1</em></strong>", text)

    # Check for bold formatting with **word**
    bold_pattern = re.compile(r"\*\*(.*?)\*\*")
    text = bold_pattern.sub(r"<strong>\1</strong>", text)

    # Split text into parts to handle formatting
    parts = re.split(r"(<strong><em>.*?</em></strong>|<strong>.*?</strong>)", text)

    rich_text = []

    for part in parts:
        if part.startswith("<strong><em>") and part.endswith("</em></strong>"):
            content = part[13:-14]
            rich_text.append(
                {
                    "type": "text",
                    "text": {"content": content},
                    "annotations": {"bold": True, "italic": True},
                }
            )
        elif part.startswith("<strong>") and part.endswith("</strong>"):
            content = part[8:-9]
            rich_text.append(
                {
                    "type": "text",
                    "text": {"content": content},
                    "annotations": {"bold": True},
                }
            )
        else:
            rich_text.append({"type": "text", "text": {"content": part}})

    markdown_children.append(
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text}}
    )


def add_expandable_toggle(markdown_children, title, content, color: str = "default"):
    """Add an expandable toggle block to the children blocks.

    Args:
        markdown_children (list): Your markdown list that contains all elements so far
        title (str): The title of the toggle block
        content (list): The list of text strings or rich text objects to be included as content inside the toggle block
        color (str, optional): The color of the toggle block. Defaults to "default".

    Example:
            toggle_content_texts = [
        "This is the first paragraph inside the toggle.",
        "This is the second paragraph inside the toggle.",
        ]

        # Adding the expandable toggle block with basic text content
        add_expandable_toggle(
            markdown_children,
            "Click to Expand (Basic Text)",
            toggle_content_texts,
            color="blue",
        )

        # Adding the expandable toggle block with rich text content
        add_expandable_toggle(
            markdown_children,
            "Click to Expand (Rich Text)",
            all_thing,
            color="green_background",
        )
    """
    # Create the rich text for the toggle title
    rich_text_title = [
        {
            "type": "text",
            "text": {"content": title},
        }
    ]

    # Determine if the content is basic text or rich text
    if all(isinstance(item, str) for item in content):
        # Convert basic text strings to rich text objects
        content_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                },
            }
            for text in content
        ]
    else:
        # Use the rich text objects directly
        content_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": rich_text},
            }
            for rich_text in content
        ]

    # Create the toggle block
    toggle_block = {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": rich_text_title,
            "color": color,
            "children": content_blocks,
        },
    }

    # Append the toggle block to the markdown children
    markdown_children.append(toggle_block)


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


def add_table(markdown_children: list, headers: list, rows: list = []) -> None:
    """Add a table to your markdown

    Example:
        Headers = ["Item 1", "Item 2", "Item 3"]
        Rows = [
            ["Data 1", "Data 2", "Data 3"],
            [["type": "text", "text": {"content": "Data 4"}], ...],
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
        for row in rows:
            data_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": []},
            }
            for cell in row:
                if isinstance(cell, str):
                    # Handle plain string
                    data_row["table_row"]["cells"].append(
                        [{"type": "text", "text": {"content": cell}}]
                    )
                elif isinstance(cell, list):
                    # Handle rich text object
                    data_row["table_row"]["cells"].append(cell)
                else:
                    raise ValueError("Unsupported cell content type")
            data_rows.append(data_row)

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
    icon: str = "",
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
