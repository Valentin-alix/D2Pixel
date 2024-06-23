import logging
from typing import Any
from src.common.loggers.utils import stdout_handler
from src.gui.signals.app_signals import AppSignals


class AppLogger(logging.Logger):
    def __init__(self, app_signals: AppSignals) -> None:
        super().__init__(name="root")
        self.app_signals = app_signals
        self.setLevel(logging.DEBUG)
        self.addHandler(stdout_handler)

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
