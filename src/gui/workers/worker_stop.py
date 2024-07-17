from PyQt5.QtCore import QObject, pyqtSlot

from src.bots.modules.bot import Bot


class WorkerStop(QObject):
    def __init__(self, bot: Bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

    @pyqtSlot()
    def run(self):
        self.bot.stop_bot()
