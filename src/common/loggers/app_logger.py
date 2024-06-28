import logging
import sys
from typing import Any

import coloredlogs

from src.gui.signals.app_signals import AppSignals


class AppLogger(logging.Logger):
    def __init__(self, app_signals: AppSignals) -> None:
        super().__init__(name="root")
        self.app_signals = app_signals
        self.setLevel(logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG, logger=self, isatty=True, stream=sys.stdout)

    def debug(self, msg: Any, *args, **kwargs):
        super().debug(msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        super().info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        super().warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        super().error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        super().critical(msg, *args, **kwargs)
