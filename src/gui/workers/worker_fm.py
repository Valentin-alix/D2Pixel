from PyQt5.QtCore import QObject, pyqtSlot

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, StatSchema
from src.bots.modules.bot import Bot


class WorkerFm(QObject):
    def __init__(
        self,
        bot: Bot,
        lines: list[BaseLineSchema],
        exo_stat: StatSchema | None,
        equipment: ReadEquipmentSchema | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.lines = lines
        self.exo = exo_stat
        self.equipment = equipment

    @pyqtSlot()
    def run(self):
        self.bot.run_fm(self.lines, self.exo, self.equipment)
