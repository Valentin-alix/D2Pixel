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
from src.gui.workers.worker_craft import WorkerCraft
from src.gui.workers.worker_stop import WorkerStop
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class ManualTab(QWidget):
    def __init__(
        self,
        app_signals: AppSignals,
        service: ServiceSession,
        bot: Bot,
        logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.character = bot.character_state.character
        self.app_signals = app_signals
        self.is_loading: bool = False
        self.bot = bot
        self.logger = logger

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.craft_table = RecipeTable()
        self.craft_group = RecipeGroup(
            RecipeService.get_available_recipes(self.service, self.character.id)
        )

        self.craft_group.signals.added_recipe_queue.connect(self.on_added_recipe_queue)
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
        if not bot.character_state.character.is_sub:
            self.play_stop_widget.on_click_stop()
            self.logger.warning("Votre personnage doit être abonné.")
            return

        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerCraft(
            bot, recipes=list(self.craft_table.widget_item_by_recipe.keys())
        )
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

    @pyqtSlot(object)
    def on_stop(self, bot: Bot):
        if self.thread_stop is not None:
            self.thread_stop.quit()
            self.thread_stop.wait()

        self.worker_stop = WorkerStop(bot)
        self.thread_stop = QThread()

        self.worker_stop.moveToThread(self.thread_stop)
        self.thread_stop.started.connect(self.worker_stop.run)
        self.thread_stop.finished.connect(self.worker_stop.deleteLater)
        self.thread_stop.start()

    @pyqtSlot()
    def _on_refresh_recipes(self) -> None:
        recipes = RecipeService.get_available_recipes(self.service, self.character.id)
        not_in_queue_recipes = [
            _elem
            for _elem in recipes
            if _elem not in self.craft_table.widget_item_by_recipe.keys()
        ]
        self.craft_group._on_refresh_recipes(not_in_queue_recipes)

    @pyqtSlot(object)
    def on_removed_recipe_queue(self, recipe: RecipeSchema):
        self.craft_group.add_recipe(recipe)

    @pyqtSlot(object)
    def on_added_recipe_queue(self, recipe: RecipeSchema):
        self.craft_table.add_recipe(recipe)
