import logging
import os

from src.consts import LOGS_FOLDER
from src.loggers.formatters import BASE_FORMATTER


def get_file_handler(header: str) -> logging.FileHandler:
    file_handler = logging.FileHandler(os.path.join(LOGS_FOLDER, f"{header}.log"), "w+")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(BASE_FORMATTER)
    return file_handler
