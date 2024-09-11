import json
import logging


def load_data(logger: logging.Logger, json_dir: str, file: str) -> json:
    """_summary_

    Args:
        logger (logging.loger): Passing in the logger
        json_dir (str): path to json directory
        file (str): file name you want to access within the path

    Returns:
        json: returns the entirety of the raw json file
    """
    logger.info(f"Attempting to load: {json_dir}/{file}")
    with open(f"{json_dir}/{file}", "r") as f:
        return json.load(f)
