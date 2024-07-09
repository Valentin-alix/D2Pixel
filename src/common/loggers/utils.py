import logging
import os
from pathlib import Path

LOGS_FOLDER = os.path.join(Path(__file__).parent.parent.parent.parent, "logs")


os.makedirs(LOGS_FOLDER, exist_ok=True)

file_formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")


def get_file_handler(header: str) -> logging.FileHandler:
    file_handler = logging.FileHandler(os.path.join(LOGS_FOLDER, f"{header}.log"), "w+")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    return file_handler
