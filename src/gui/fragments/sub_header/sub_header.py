from logging import Logger

from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.bot import Bot
from src.gui.components.organization import HorizontalLayout
from src.gui.pages.craft.craft_page import CraftPage
from src.gui.pages.farm.farm_page import FarmPage
from src.gui.pages.fm.fm_page import FmPage
from src.gui.pages.stats.stats_page import StatsPage
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


class SubHeader(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        app_signals: AppSignals,
        bot: Bot,
        logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.bot = bot
        self.app_signals = app_signals

        self.setLayout(HorizontalLayout())
        self._setup_tabs(self.bot)

    def _setup_tabs(self, bot: Bot):
        self.tabs = QTabWidget()

        self.bot_page = FarmPage(self.logger, self.app_signals, bot=bot)
        self.tabs.addTab(self.bot_page, "Farming")

        self.craft_frame = CraftPage(
            self.app_signals,
            self.service,
            bot=bot,
            logger=self.logger,
        )
        self.tabs.addTab(self.craft_frame, "Crafting")
        self.fm_frame = FmPage(
            self.service, self.app_signals, bot=bot, logger=self.logger
        )
        self.tabs.addTab(self.fm_frame, "Forgemagie")

        self.stats_frame = StatsPage(
            self.service, character=bot.character_state.character
        )
        self.tabs.addTab(self.stats_frame, "Statistique")

        self.layout().addWidget(self.tabs)
