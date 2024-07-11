from PyQt5.QtCore import QObject, pyqtSlot

from src.bots.modules.module_manager import ModuleManager


class WorkerRunFarming(QObject):
    def __init__(
        self, module_manager: ModuleManager, name_modules: list[str], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.module_manager = module_manager
        self.name_modules = name_modules

    @pyqtSlot()
    def run(self):
        self.module_manager.run_bot(self.name_modules)