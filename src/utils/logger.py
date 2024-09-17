import os
import logging
import datetime


def configure_logging(log_dir: str) -> logging.Logger:
    """Sets up logging for the tool

    Args:
        log_dir (str, optional): Path for your log

    Returns:
        logging.Logger: Returns the logging package configured
    """
    # == Get the datetime for logging file name
    current = datetime.datetime.now()
    formatted_datetime = current.strftime("%Y-%m-%d.%H.%M.%S")

    # == Init the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # == Setup logging to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    # == Ensure the directory for the log file exists
    log_file_path = f"{log_dir}/{formatted_datetime}-D&D-Notion.log"
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # == Create a file handler
    file_path = log_file_path
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s == %(levelname)s == %(message)s")
    )

    # == Add the handler to the logger
    logger.addHandler(file_handler)

    logger.info(f"Logging started: {file_path}")

    return logger
