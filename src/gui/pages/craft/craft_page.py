from logging import Logger

from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.bot import Bot
from src.gui.components.organization import VerticalLayout

from src.gui.pages.craft.craft_automatic_tab import CraftAutomaticTab
from src.gui.pages.craft.craft_manual_tab import CraftManualTab
from src.gui.signals.app_signals import AppSignals
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

        available_recipes = RecipeService.get_available_recipes(
            self.service, self.bot.character_state.character.id
        )

        self.automatic_tab = CraftAutomaticTab(
            self.service,
            self.bot.character_state.character,
            self.logger,
            available_recipes,
        )
        self.tabs.addTab(self.automatic_tab, "Automatique")
        self.layout().addWidget(self.tabs)

        self.manual_tab = CraftManualTab(
            self.app_signals, self.service, self.bot, self.logger, available_recipes
        )
        self.tabs.addTab(self.manual_tab, "Manuel")
