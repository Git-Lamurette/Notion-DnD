import logging
import pprint
def get_first_level_keys(data):
    if isinstance(data, dict):
        return set(data.keys())
    return set()

def get_keys(logger: logging.Logger, DATA_DIRECTORY, json_file) -> None:
    # == Importing required modules
    # ==========
    from src.utils.load_json import load_data

    # == Loading data
    # ==========
    data = load_data(logger, DATA_DIRECTORY, json_file)

    unique_keys = set()

    for item in data:
        if item['equipment_category']['name'] != "Armor" and item['equipment_category']['name'] != "Weapon":
            unique_keys = unique_keys.union(get_first_level_keys(item))

    pprint.pprint(unique_keys)

    input("Press Enter to continue...")
