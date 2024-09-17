import logging
import pprint


def get_first_level_keys(data):
    if isinstance(data, dict):
        return set(data.keys())
    return set()


def get_keys(
    logger: logging.Logger, DATA_DIRECTORY: str, json_file: str, key_val: str
) -> None:
    """Getting the unique keys and values from the JSON file

    Args:
        logger (logging.Logger): Logging object
        DATA_DIRECTORY (str): Path to the json you are parsing
        json_file (str): JSON file you are parsing
        key_val (str): Key value you want to get the unique keys and values from

    """
    # == Importing required modules
    # ==========
    from src.utils.load_json import load_data

    # == Loading data
    # ==========
    data_list = load_data(logger, DATA_DIRECTORY, json_file)

    unique_key = set()
    unique_values = set()

    # Iterate over each key_val in the data list
    for data in data_list:
        for key in data.keys():
            unique_key.add(key)

        # Check if "equipment_category" exists in the nested key_val
        if data[f"{key_val}"]:
            if isinstance(data[f"{key_val}"], dict):
                for key, value in data[f"{key_val}"].items():
                    unique_values.add(value)

            elif isinstance(data[f"{key_val}"], str):
                unique_values.add(data[f"{key_val}"])

            elif isinstance(data[f"{key_val}"], int):
                unique_values.add(data[f"{key_val}"])

            elif isinstance(data[f"{key_val}"], list):
                for item in data[f"{key_val}"]:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            unique_values.add(value)
                    else:
                        unique_values.add(item)

    # Print the unique keys and values
    print("Unique Keys:")
    pprint.pprint(unique_key)

    print("\nUnique Values:")
    pprint.pprint(unique_values)

    input("Press Enter to continue...")
