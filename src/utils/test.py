from notion_client import Client
import sys


from notion_client import Client
import logging

def query_notion(
    notion: Client,
    query: str,
    filter: dict = None,
    sort: dict = None,
    page_size: int = 100,
    logger: logging.Logger = None
) -> list:
    """Query the Notion API and return results.

    Args:
        notion (Client): The Notion client.
        query (str): The search query.
        filter (dict, optional): The filter for the search. Defaults to None.
        sort (dict, optional): The sort order for the search. Defaults to None.
        page_size (int, optional): The number of results per page. Defaults to 100.
        logger (logging.Logger, optional): Logger for logging errors. Defaults to None.

    Returns:
        list: The search results.

    Example:
        query = "Backpack"
        filter = {
            "property": "object",
            "value": "page"
        }
        sort = {
            "direction": "ascending",
            "timestamp": "last_edited_time"
        }
        results = query_notion(notion, query, filter, sort)
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

    return results

notion = Client(auth="secret_8fDt3EJbAlcH0tWh6u26x5RfTBVkfHZYW9nUUN6K1gU")


query = "Backpack"
filter = {
    "property": "object",
    "value": "page"
}
sort = {
    "direction": "ascending",
    "timestamp": "last_edited_time"
}

results = query_notion(notion, query, filter, sort)
print(results[0]['id'])