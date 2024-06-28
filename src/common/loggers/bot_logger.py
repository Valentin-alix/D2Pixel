import logging
import os
import sys
from pathlib import Path
from typing import Any

import coloredlogs

from src.gui.signals.dofus_signals import BotSignals

LOGS_FOLDER = os.path.join(Path(__file__).parent.parent.parent.parent, "logs")

os.makedirs(LOGS_FOLDER, exist_ok=True)

file_formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")


def get_file_handler(header: str) -> logging.FileHandler:
    file_handler = logging.FileHandler(os.path.join(LOGS_FOLDER, f"{header}.log"), "w+")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    return file_handler


class BotLogger(logging.Logger):
    def __init__(self, title: str, bot_signals: BotSignals) -> None:
        super().__init__(name=title)
        self.title = title
        self.bot_signals = bot_signals
        self.setLevel(logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG, logger=self, isatty=True, stream=sys.stdout,
                            fmt="%(asctime)s %(levelname)-8s %(message)s")
        self.addHandler(get_file_handler(self.title))

    def _get_log_msg(self, msg: Any) -> str:
        return f"{self.title}: {msg}"

    def debug(self, msg: Any, *args, **kwargs):
        self.bot_signals.log_msg_by_type.emit((logging.DEBUG, str(msg)))
        super().debug(self._get_log_msg(msg), *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        self.bot_signals.log_msg_by_type.emit((logging.INFO, str(msg)))
        super().info(self._get_log_msg(msg), *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        self.bot_signals.log_msg_by_type.emit((logging.WARNING, str(msg)))
        super().warning(self._get_log_msg(msg), *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        self.bot_signals.log_msg_by_type.emit((logging.ERROR, str(msg)))
        super().error(self._get_log_msg(msg), *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        self.bot_signals.log_msg_by_type.emit((logging.CRITICAL, str(msg)))
        super().critical(self._get_log_msg(msg), *args, **kwargs)
