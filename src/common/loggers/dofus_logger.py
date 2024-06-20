import logging
from typing import Any

from src.common.loggers.common_logger import CommonLogger
from src.gui.signals.dofus_signals import DofusSignals


class DofusLogger(CommonLogger):
    def __init__(self, bot_signals: DofusSignals, *args, **kwargs) -> None:
        self.bot_signals = bot_signals
        super().__init__(*args, **kwargs)

    def log_debug(self, msg: Any):
        self.bot_signals.log_msg_by_type.emit((logging.DEBUG, str(msg)))
        self._logger.debug(self._get_log_msg(msg))

    def log_info(self, msg: Any):
        self.bot_signals.log_msg_by_type.emit((logging.INFO, str(msg)))
        self._logger.info(self._get_log_msg(msg))

    def log_warning(self, msg: Any):
        self.bot_signals.log_msg_by_type.emit((logging.WARNING, str(msg)))
        self._logger.warning(self._get_log_msg(msg))

    def log_error(self, msg: Any):
        self.bot_signals.log_msg_by_type.emit((logging.ERROR, str(msg)))
        self._logger.error(self._get_log_msg(msg))

    def log_critical(self, msg: Any):
        self.bot_signals.log_msg_by_type.emit((logging.CRITICAL, str(msg)))
        self._logger.critical(self._get_log_msg(msg))
