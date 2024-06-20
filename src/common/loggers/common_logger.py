import logging
import os
from pathlib import Path
from typing import Any

from src.common.environment import is_in_pyinstaller_bundle

LOGS_FOLDER = os.path.join(Path(__file__).parent.parent.parent.parent, "logs")

os.makedirs(LOGS_FOLDER, exist_ok=True)


class ColoredFormatter(logging.Formatter):
    GREY: str = "\x1b[38;20m"
    YELLOW: str = "\x1b[33;20m"
    RED: str = "\x1b[31;20m"
    BOLD_RED: str = "\x1b[31;1m"
    RESET: str = "\x1b[0m"
    _format: str = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + _format + RESET,
        logging.INFO: GREY + _format + RESET,
        logging.WARNING: YELLOW + _format + RESET,
        logging.ERROR: RED + _format + RESET,
        logging.CRITICAL: BOLD_RED + _format + RESET,
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(ColoredFormatter())

file_formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")


def get_file_handler(header: str) -> logging.FileHandler:
    file_handler = logging.FileHandler(os.path.join(LOGS_FOLDER, f"{header}.log"), "w+")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    return file_handler


class CommonLogger:
    _logger: logging.Logger
    __log_header: str

    def __init__(self, log_header: str, *args, **kwargs) -> None:
        self.__log_header = log_header
        self._logger = logging.getLogger(self.__log_header)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(stdout_handler)
        if not is_in_pyinstaller_bundle():
            self._logger.addHandler(get_file_handler(self.__log_header))
        super().__init__(*args, **kwargs)

    def _get_log_msg(self, msg: Any) -> str:
        return f"{self.__log_header}: {str(msg)}"

    def log_debug(self, msg: Any):
        self._logger.debug(self._get_log_msg(msg))

    def log_info(self, msg: Any):
        self._logger.info(self._get_log_msg(msg))

    def log_warning(self, msg: Any):
        self._logger.warning(self._get_log_msg(msg))

    def log_error(self, msg: Any):
        self._logger.error(self._get_log_msg(msg))

    def log_critical(self, msg: Any):
        self._logger.critical(self._get_log_msg(msg))
