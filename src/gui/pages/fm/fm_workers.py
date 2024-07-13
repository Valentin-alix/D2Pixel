from PyQt5.QtCore import QObject, pyqtSlot

from D2Shared.shared.schemas.stat import BaseLineSchema
from src.bots.modules.module_manager import ModuleManager


class WorkerRunFm(QObject):
    def __init__(
        self,
        module_manager: ModuleManager,
        lines: list[BaseLineSchema],
        exo_line: BaseLineSchema | None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.module_manager = module_manager
        self.lines = lines
        self.exo = exo_line

    @pyqtSlot()
    def run(self):
        self.module_manager.run_fm(self.lines, self.exo)
