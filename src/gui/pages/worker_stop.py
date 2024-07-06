from src.bots.modules.module_manager import ModuleManager


from PyQt5.QtCore import QObject, pyqtSlot


class WorkerStopActions(QObject):
    def __init__(self, module_manager: ModuleManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.module_manager = module_manager

    @pyqtSlot()
    def run(self):
        self.module_manager.stop_bot()
