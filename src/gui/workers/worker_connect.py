from PyQt5.QtCore import QObject, pyqtSlot

from src.bots.bots_manager import BotsManager
from src.gui.signals.app_signals import AppSignals


class WorkerConnect(QObject):
    def __init__(
        self,
        bots_manager: BotsManager,
        app_signals: AppSignals,
        *args,
        **kwargs,
    ) -> None:
        self.app_signals = app_signals
        self.bots_manager = bots_manager
        super().__init__(*args, **kwargs)

    @pyqtSlot()
    def run(self) -> None:
        self.bots_manager.connect_all()
        self.app_signals.connected_bots.emit(self.bots_manager.bots)
