from PyQt5.QtCore import QObject, pyqtSlot

from src.bots.modules.bot import Bot


class WorkerFarm(QObject):
    def __init__(self, bot: Bot, name_modules: list[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.name_modules = name_modules

    @pyqtSlot()
    def run(self):
        self.bot.run_farming(self.name_modules)
