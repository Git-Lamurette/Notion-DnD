from notion_client.errors import APIResponseError
import sys
from time import sleep
import logging
from notion_client import Client

def query_notion(
    logger: logging.Logger,
    notion: Client,
    query: str,
    filter: dict = None,
    sort: dict = None,
    page_size: int = 100,
    exact_case: bool = True,
    
) -> list:
    """Query the Notion API and return results.
    Example:

        results = query_notion(logger, notion, query, filter, sort)
    """
    results = []
    start_cursor = None
    while True:
        try:
            response = notion.search(
                query=query,
                filter=filter,
                sort=sort,
                start_cursor=start_cursor,
                page_size=page_size
            )
            results.extend(response.get("results", []))
            start_cursor = response.get("next_cursor")

            if not start_cursor:
                break

        except Exception as e:
            if logger:
                logger.error(f"Error querying Notion API: {e}")
            else:
                print(f"Error querying Notion API: {e}")
            break
    """
    if exact_case:
        # Use a generator expression to find the first result that matches the exact case
        result = next((result for result in results if result.get("title", "").strip() == query), None)
        return [result] if result else []
    """
    return results

def create_page_under_page(
    logger: logging.Logger,
    notion: Client,
    database_id: str,
    title,
):
    try:
        response = notion.pages.create(
            parent={"page_id": database_id},
            properties={"title": [{"type": "text", "text": {"content": title}}]},
        )

        logger.info(f"Page created with ID: {response['id']}")
        return response["id"]

    except APIResponseError as e:
        logger.error(f"Response status: {e.status}")
        logger.error(f"An API error occurred: {e}")
        sys.exit(1)


def create_page(
    logger: logging.Logger,
    notion: Client,
    database_id: str,
    markdown_properties: dict,
    children_properties: list,
) -> None:
    """This function creates a page in Notion. It is used to create the pages for the creatures and equipment.

    Args:

        logger (logging.Logger): Logging object
        notion (client): Notion Client object
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
    notion: Client,
    database_id: str,
    database_name: str,
    database_properties: dict,
) -> str:
    """This function creates a database in Notion. It is used to create the database for the creatures and equipment.

    Args:

        logger (logging.Logger): Logging object
        notion (client): Notion Client object
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
