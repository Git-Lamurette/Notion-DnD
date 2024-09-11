"""Just a placeholder as a temp database creation tool for creatures"""

from notion_client import Client

database_id = "daa7c3005621476ca0e48b420bbb8b1f"
auth_key = "secret_8fDt3EJbAlcH0tWh6u26x5RfTBVkfHZYW9nUUN6K1gU"

notion = Client(auth=auth_key)


parent_page_id = database_id

database_properties = {
    "Name": {"title": {}},
    "Size": {
        "select": {
            "options": [
                {"name": "Tiny", "color": "pink"},
                {"name": "Small", "color": "purple"},
                {"name": "Medium", "color": "blue"},
                {"name": "Large", "color": "green"},
                {"name": "Huge", "color": "yellow"},
                {"name": "Gargantuan", "color": "red"},
            ]
        }
    },
    "Type": {
        "select": {
            "options": [
                {"name": "Aberration", "color": "gray"},
                {"name": "Beast", "color": "green"},
                {"name": "Celestial", "color": "yellow"},
                {"name": "Construct", "color": "blue"},
                {"name": "Dragon", "color": "red"},
                {"name": "Elemental", "color": "orange"},
                {"name": "Fey", "color": "pink"},
                {"name": "Fiend", "color": "purple"},
                {"name": "Giant", "color": "brown"},
                {"name": "Humanoid", "color": "blue"},
                {"name": "Monstrosity", "color": "red"},
                {"name": "Ooze", "color": "gray"},
                {"name": "Plant", "color": "green"},
                {"name": "Undead", "color": "gray"},  # Fixed color
            ]
        }
    },
    "CR": {"number": {}},
    "Hit Points": {"number": {}},
    "Movement Type": {
        "multi_select": {
            "options": [
                {"name": "Walk", "color": "blue"},
                {"name": "Fly", "color": "purple"},
                {"name": "Swim", "color": "green"},
                {"name": "Climb", "color": "yellow"},
                {"name": "Burrow", "color": "brown"},
                {"name": "Hover", "color": "pink"},
            ]
        }
    },
}


response = notion.databases.create(
    parent={"type": "page_id", "page_id": parent_page_id},
    title=[{"type": "text", "text": {"content": "Monsters Database"}}],
    properties=database_properties,
)

print(response)
print(response["id"])
