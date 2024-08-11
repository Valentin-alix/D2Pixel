from logging import Logger

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QWidget

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.bots.modules.bot import Bot
from src.gui.components.loaders import Loading
from src.gui.components.organization import VerticalLayout

from src.gui.pages.craft.craft_automatic_tab import CraftAutomaticTab
from src.gui.pages.craft.craft_manual_tab import CraftManualTab
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class CraftPage(QWidget):
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
        self.app_signals = app_signals
        self.service = service
        self.bot = bot
        self.is_loading: bool = False
        self.logger = logger

        self.setLayout(VerticalLayout())

        self.tabs = QTabWidget()

        self.loading_widget = Loading(self)
        self.loading_widget.start()
        self.layout().addWidget(self.loading_widget)

        self.rec_thread, self.rec_worker = run_in_background(
            lambda: RecipeService.get_available_recipes(
                self.service, self.bot.character_state.character.id
            )
        )
        self.rec_worker.signals.function_result.connect(
            self.on_fetched_available_recipes
        )

    @pyqtSlot(object)
    def on_fetched_available_recipes(self, recipes: list[RecipeSchema]):
        self.loading_widget.stop()
        self.automatic_tab = CraftAutomaticTab(
            self.service,
            self.bot.character_state.character,
            self.logger,
            recipes,
        )
        self.tabs.addTab(self.automatic_tab, "Automatique")
        self.layout().addWidget(self.tabs)

        self.manual_tab = CraftManualTab(
            self.app_signals, self.service, self.bot, self.logger, recipes
        )
        self.tabs.addTab(self.manual_tab, "Manuel")
