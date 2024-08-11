from logging import Logger

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QWidget

from D2Shared.shared.schemas.item import ItemSchema
from src.bots.modules.bot import Bot
from src.gui.components.loaders import Loading
from src.gui.components.organization import VerticalLayout
from src.gui.pages.sell.sell_automatic_tab import SellAutomaticTab
from src.gui.pages.sell.sell_manual_tab import SellManualTab
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.item import ItemService
from src.services.session import ServiceSession


class SellPage(QWidget):
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

        self.loading_widget = Loading(self)
        self.loading_widget.start()
        self.layout().addWidget(self.loading_widget)

        self.tabs = QTabWidget()

        self.items_thread, self.items_worker = run_in_background(
            lambda: ItemService.get_items(self.service)
        )
        self.items_worker.signals.function_result.connect(self.on_items_fetched)

    @pyqtSlot(object)
    def on_items_fetched(self, items: list[ItemSchema]):
        self.loading_widget.stop()
        self.automatic_tab = SellAutomaticTab(
            service=self.service,
            character=self.bot.character_state.character,
            logger=self.logger,
            items=items,
        )
        self.tabs.addTab(self.automatic_tab, "Automatique")
        self.layout().addWidget(self.tabs)

        self.manual_tab = SellManualTab(
            app_signals=self.app_signals,
            bot=self.bot,
            service=self.service,
            character=self.bot.character_state.character,
            logger=self.logger,
            items=items,
        )
        self.tabs.addTab(self.manual_tab, "Manuel")
        self.layout().addWidget(self.tabs)
