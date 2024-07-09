import logging
import sys
from typing import Any

import coloredlogs

from src.common.loggers.utils import get_file_handler
from src.gui.signals.app_signals import AppSignals


class AppLogger(logging.Logger):
    def __init__(self, app_signals: AppSignals) -> None:
        super().__init__(name="root")
        self.app_signals = app_signals
        self.setLevel(logging.DEBUG)
        coloredlogs.install(
            level=logging.DEBUG,
            logger=self,
            isatty=True,
            stream=sys.stdout,
            fmt="%(asctime)s %(levelname)-8s %(message)s",
        )
        self.addHandler(get_file_handler("root"))

    def debug(self, msg: Any, *args, **kwargs):
        self.app_signals.lvl_with_title_and_msg.emit((logging.DEBUG, str(msg)))
        super().debug(msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        self.app_signals.lvl_with_title_and_msg.emit((logging.INFO, str(msg)))
        super().info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        self.app_signals.lvl_with_title_and_msg.emit((logging.WARNING, str(msg)))
        super().warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        self.app_signals.lvl_with_title_and_msg.emit((logging.ERROR, str(msg)))
        super().error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        self.app_signals.lvl_with_title_and_msg.emit((logging.CRITICAL, str(msg)))
        super().critical(msg, *args, **kwargs)
