from PyQt5.QtCore import QObject, pyqtSlot

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.bots.modules.bot import Bot


class WorkerCraft(QObject):
    def __init__(self, bot: Bot, recipes: list[RecipeSchema], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.recipes = recipes

    @pyqtSlot()
    def run(self):
        self.bot.run_craft(self.recipes)
