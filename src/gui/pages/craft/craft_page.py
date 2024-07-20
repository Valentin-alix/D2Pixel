from logging import Logger

from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.bot import Bot
from src.gui.components.organization import VerticalLayout
from src.gui.pages.craft.automatic_tab.automatic_tab import AutomaticTab
from src.gui.pages.craft.manual_tab.manual_tab import ManualTab
from src.gui.signals.app_signals import AppSignals
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

        self.automatic_tab = AutomaticTab(
            self.service, self.bot.character_state.character, self.logger
        )
        self.tabs.addTab(self.automatic_tab, "Automatique")
        self.layout().addWidget(self.tabs)

        self.manual_tab = ManualTab(
            self.app_signals, self.service, self.bot, self.logger
        )
        self.tabs.addTab(self.manual_tab, "Manuel")
