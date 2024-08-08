from logging import Logger

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.bots.modules.bot import Bot
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import VerticalLayout
from src.gui.components.play_stop import PlayStopWidget
from src.gui.pages.craft.recipe_group import RecipeGroup
from src.gui.pages.craft.recipe_table import RecipeTable
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class CraftManualTab(QWidget):
    def __init__(
        self,
        app_signals: AppSignals,
        service: ServiceSession,
        bot: Bot,
        logger: Logger,
        available_recipes: list[RecipeSchema],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.character = bot.character_state.character
        self.app_signals = app_signals
        self.available_recipes = available_recipes
        self.is_loading: bool = False
        self.bot = bot
        self.logger = logger

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.craft_table = RecipeTable()
        self.craft_group = RecipeGroup(recipes=available_recipes)

        self.craft_group.signals.clicked_elem_queue.connect(self.on_added_recipe_queue)
        self.craft_table.signals.removed_recipe.connect(self.on_removed_recipe_queue)

        self._setup_play_stop()

        refresh_btn = PushButtonIcon("restart.svg")
        refresh_btn.clicked.connect(self._on_refresh_recipes)
        self.layout().addWidget(refresh_btn)

        self.layout().addWidget(self.craft_table)
        self.layout().addWidget(self.craft_group)

    def _setup_play_stop(self):
        self.play_stop_widget = PlayStopWidget(self.app_signals, self.bot.bot_signals)
        self.play_stop_widget.signals.played.connect(lambda: self.on_play(self.bot))
        self.play_stop_widget.signals.stopped.connect(lambda: self.on_stop(self.bot))
        self.layout().addWidget(self.play_stop_widget)

    @pyqtSlot(object)
    def on_play(self, bot: Bot):
        self.thread_run, self.worker_run = run_in_background(
            lambda: bot.run_craft(list(self.craft_table.widget_item_by_recipe.keys()))
        )

    @pyqtSlot(object)
    def on_stop(self, bot: Bot):
        self.thread_stop, self.worker_stop = run_in_background(bot.stop_bot)

    @pyqtSlot()
    def _on_refresh_recipes(self) -> None:
        recipes = RecipeService.get_available_recipes(self.service, self.character.id)
        not_in_queue_recipes = [
            _elem
            for _elem in recipes
            if _elem not in self.craft_table.widget_item_by_recipe.keys()
        ]
        self.craft_group.on_refresh_elems(not_in_queue_recipes)

    @pyqtSlot(object)
    def on_removed_recipe_queue(self, recipe: RecipeSchema):
        self.craft_group.add_elem(recipe)

    @pyqtSlot(object)
    def on_added_recipe_queue(self, recipe: RecipeSchema):
        self.craft_table.add_recipe(recipe)
