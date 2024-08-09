from logging import Logger

from PyQt5.QtCore import QThread, Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.item import ItemSchema, SellItemInfo
from src.bots.modules.bot import Bot
from src.gui.components.organization import VerticalLayout
from src.gui.components.play_stop import PlayStopWidget
from src.gui.pages.sell.groups.sell_item_info_group import SellItemInfoGroup
from src.gui.pages.sell.groups.item_group import ItemGroup
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.session import ServiceSession


class SellManualTab(QWidget):
    def __init__(
        self,
        app_signals: AppSignals,
        bot: Bot,
        service: ServiceSession,
        character: CharacterSchema,
        logger: Logger,
        items: list[ItemSchema],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.app_signals = app_signals
        self.bot = bot
        self.character = character
        self.is_loading: bool = False
        self.logger = logger

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.sell_group = ItemGroup(items)
        self.sell_info_group = SellItemInfoGroup(item_infos=[])

        self.sell_group.signals.clicked_elem_queue.connect(self.on_added_item_queue)
        self.sell_info_group.sell_signals.removed_item.connect(
            self.on_removed_item_queue
        )

        self._setup_play_stop()

        self.layout().addWidget(self.sell_info_group)
        self.layout().addWidget(self.sell_group)

    def _setup_play_stop(self):
        self.play_stop_widget = PlayStopWidget(self.app_signals, self.bot.bot_signals)
        self.play_stop_widget.signals.played.connect(lambda: self.on_play(self.bot))
        self.play_stop_widget.signals.stopped.connect(lambda: self.on_stop(self.bot))
        self.layout().addWidget(self.play_stop_widget)

    @pyqtSlot(object)
    def on_play(self, bot: Bot):
        self.thread_run, self.worker_run = run_in_background(
            lambda: bot.run_sell(list(self.sell_info_group.elems_by_name.values()))
        )

    @pyqtSlot(object)
    def on_stop(self, bot: Bot):
        self.thread_stop, self.worker_stop = run_in_background(bot.stop_bot)

    @pyqtSlot(object)
    def on_removed_item_queue(self, sell_item_info: SellItemInfo):
        self.sell_group.add_elem(sell_item_info.item)

    @pyqtSlot(object)
    def on_added_item_queue(self, item: ItemSchema):
        self.sell_group.remove_elem(item)
        sell_item_info = SellItemInfo(
            item_id=item.id, item=item, sale_hotel_quantities=[]
        )
        self.sell_info_group.add_elem(sell_item_info)
