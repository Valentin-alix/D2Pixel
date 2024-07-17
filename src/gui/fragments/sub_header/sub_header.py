from logging import Logger

from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.bot import Bot
from src.gui.components.organization import HorizontalLayout
from src.gui.pages.farm.farm_page import FarmPage
from src.gui.pages.fm.fm_page import FmPage
from src.gui.pages.hdv.hdv_page import HdvPage
from src.gui.pages.stats.stats_page import StatsPage
from src.services.session import ServiceSession


class SubHeader(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        bot: Bot,
        logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.bot = bot

        self.setLayout(HorizontalLayout())
        self._setup_tabs(self.bot)

    def _setup_tabs(self, bot: Bot):
        self.tabs = QTabWidget()

        self.bot_page = FarmPage(bot=bot)
        self.tabs.addTab(self.bot_page, "Farm")

        self.hdv_frame = HdvPage(
            self.service,
            character=bot.character_state.character,
            logger=self.logger,
        )
        self.tabs.addTab(self.hdv_frame, "Hdv")

        self.fm_frame = FmPage(self.service, bot=bot, logger=self.logger)
        self.tabs.addTab(self.fm_frame, "FM")

        self.stats_frame = StatsPage(
            self.service, character=bot.character_state.character
        )
        self.tabs.addTab(self.stats_frame, "Stats")

        self.layout().addWidget(self.tabs)
