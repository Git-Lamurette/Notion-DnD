def add_paragraph(children, text, column="both"):
    """Add a paragraph block to the children blocks."""
    paragraph = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }
    if column == "both":
        children.append(paragraph)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].append(paragraph)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].append(paragraph)


def add_section_heading(children, heading_text, column="both", level=2):
    """Add a heading block to the children blocks."""
    heading = {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": heading_text}}]
        },
    }
    if column == "both":
        children.append(heading)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].append(heading)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].append(heading)


def add_bulleted_list(children, items, column="both"):
    """Add a bulleted list block to the children blocks."""
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
    if column == "both":
        children.extend(list_items)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].extend(list_items)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].extend(list_items)


def add_numbered_list(children, items, column="both"):
    """Add a numbered list block to the children blocks."""
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
    if column == "both":
        children.extend(list_items)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].extend(list_items)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].extend(list_items)


def add_table(children, headers, rows, column="both"):
    """Add a table block to the children blocks."""
    table_width = len(headers)  # Define table width based on the number of headers

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

    # Ensure all rows have the correct number of cells
    formatted_rows = []
    for row in rows:
        if len(row) != table_width:
            raise ValueError(
                f"Row length {len(row)} does not match table width {table_width}"
            )

        formatted_rows.append(
            {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [
                        [{"type": "text", "text": {"content": cell}}] for cell in row
                    ]
                },
            }
        )

    # Construct the full table block
    table = {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": True,
            "children": [header_row] + formatted_rows,
        },
    }
    if column == "both":
        children.append(table)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].append(table)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].append(table)


def add_columns(children, left_column_content, right_column_content):
    """Add a two-column layout to the children blocks."""
    columns = {
        "object": "block",
        "type": "column_list",
        "column_list": {
            "children": [
                {
                    "object": "block",
                    "type": "column",
                    "column": {"children": left_column_content},
                },
                {
                    "object": "block",
                    "type": "column",
                    "column": {"children": right_column_content},
                },
            ]
        },
    }
    children.append(columns)


def add_divider(children, column="both"):
    """Add a divider block to the children blocks."""
    divider = {"object": "block", "type": "divider", "divider": {}}
    if column == "both":
        children.append(divider)
    else:
        if column == "left":
            if "left_column_content" not in children:
                children["left_column_content"] = []
            children["left_column_content"].append(divider)
        elif column == "right":
            if "right_column_content" not in children:
                children["right_column_content"] = []
            children["right_column_content"].append(divider)
