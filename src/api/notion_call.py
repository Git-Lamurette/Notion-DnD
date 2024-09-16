from notion_client.errors import APIResponseError
import sys
from time import sleep
import logging
from notion_client import client
from typing import Union


def create_page(
    logger: logging.Logger,
    notion: client,
    database_id: str,
    markdown_properties: list,
    children_properties: list,
    relations_to_create: list = None,
) -> None:
    """This function creates a page in Notion. It is used to create the pages for the creatures and equipment.

    Args:

        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID
        markdown_properties (list): List of properties for the page
        children_properties (list): List of children properties for the page

    """

    try:
        # == Sending response to notion API
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties=markdown_properties,
            children=children_properties,
        )
        logger.info(f"Page created with ID: {response['id']}")

        # Create the bidirectional relational connections
        if relations_to_create:
            for (
                item_page_id,
                parent_relation_name,
                item_relation_name,
            ) in relations_to_create:
                add_relation(
                    notion,
                    response["id"],
                    item_page_id,
                    parent_relation_name,
                    item_relation_name,
                )

            sleep(0.5)

    except APIResponseError as e:
        logger.error(f"Response status: {e.status}")
        logger.error(f"An API error occurred: {e}")
        sys.exit(1)


def create_database(
    logger: logging.Logger,
    notion: client,
    database_id: str,
    database_name: list,
    database_properties: list,
) -> None:
    """This function creates a database in Notion. It is used to create the database for the creatures and equipment.

    Args:

        logger (logging.Logger): Logging object
        notion (client): Notion client object
        database_id (str): Database ID
        database_name (list): Name of the database
        database_properties (list): Properties for the database

    """

    try:
        # == Sending response to notion API
        response = notion.databases.create(
            parent={"type": "page_id", "page_id": database_id},
            title=[{"type": "text", "text": {"content": f"{database_name}"}}],
            properties=database_properties,
        )
        logger.info(f"Page created for {database_name} with ID: {response['id']}")

        # == Returning
        return response["id"]

    except APIResponseError as e:
        logger.error(f"Response status: {e.status}")
        logger.error(f"An API error occurred: {e}")
        sys.exit(1)


# == Placeholder function, it works but do not know how I want to incorporate it.
def search_notion_page(
    notion: client, item_name: str, database_id: str
) -> Union[str, None]:
    response = notion.search(
        query=item_name,
        filter={"property": "object", "value": "page"},
        sort={"direction": "ascending", "timestamp": "last_edited_time"},
        page_size=100,
    )
    normalized_database_id = database_id.replace("-", "")
    for result in response.get("results", []):
        if (
            result["object"] == "page"
            and result["parent"].get("database_id", "").replace("-", "")
            == normalized_database_id
            and result["properties"]["Name"]["title"][0]["text"]["content"] == item_name
        ):
            print(
                f"I found page {result['properties']['Name']['title'][0]['text']['content']}: {result['id']}"
            )
            return result["id"]
    return None


def add_relation(
    notion: client,
    parent_page_id: str,
    item_page_id: str,
    parent_relation_name: str,
    item_relation_name: str,
):
    """This function adds bidirectional relational data between two pages in Notion.

    Args:
        notion (Client): Notion client object
        parent_page_id (str): ID of the parent page
        item_page_id (str): ID of the item page
        parent_relation_name (str): Name of the relation property in the parent page
        item_relation_name (str): Name of the relation property in the item page
    """
    # Add relation from parent page to item page
    notion.pages.update(
        page_id=parent_page_id,
        properties={
            parent_relation_name: {
                "type": "relation",
                "relation": [{"id": item_page_id}],
            }
        },
    )

    # Add relation from item page to parent page
    notion.pages.update(
        page_id=item_page_id,
        properties={
            item_relation_name: {
                "type": "relation",
                "relation": [{"id": parent_page_id}],
            }
        },
    )
