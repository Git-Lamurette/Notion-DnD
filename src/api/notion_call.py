from notion_client.errors import APIResponseError
import sys
from time import sleep
import logging
from notion_client import client


def create_page(
    logger: logging.Logger,
    notion: client,
    database_id: str,
    markdown_properties: list,
    children_properties: list,
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
