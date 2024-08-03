from logging import Logger

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QWidget

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from src.bots.modules.bot import Bot
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import VerticalLayout
from src.gui.components.play_stop import PlayStopWidget
from src.gui.pages.fm.fm_item.fm_item import FmItem
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.equipment import EquipmentService
from src.services.session import ServiceSession


class FmPage(QWidget):
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
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.app_signals = app_signals
        self.bot = bot
        self.logger = logger
        self.fm_items: dict[ReadEquipmentSchema, FmItem] = {}
        self.curr_fm_item: FmItem | None = None

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_action_widget()
        self._setup_top_page()
        self._setup_content()

        self.bot.bot_signals.fm_new_equipment_datas.connect(
            self._on_new_equipment_datas
        )

        self.refresh_btn.clicked.connect(lambda: self._on_refresh(bot))
        self.play_stop_widget.signals.played.connect(lambda: self._on_play(bot))
        self.play_stop_widget.signals.stopped.connect(lambda: self._on_stop(bot))

    def _setup_top_page(self):
        self.refresh_btn = PushButtonIcon(
            "restart.svg", width=80, height=40, icon_size=20, parent=self
        )

        self.layout().addWidget(self.refresh_btn)

        self.equipment_combo = QComboBox()
        self.equipment_combo.addItem("", None)
        self.equipments = EquipmentService.get_equipments(self.service)
        for equipment in self.equipments:
            self.equipment_combo.addItem(equipment.label, equipment)
        self.equipment_combo.currentIndexChanged.connect(self._on_selected_item)
        self.layout().addWidget(self.equipment_combo)

    def _setup_action_widget(self):
        self.play_stop_widget = PlayStopWidget(self.app_signals, self.bot.bot_signals)
        self.layout().addWidget(self.play_stop_widget)

    def _setup_content(self) -> None:
        content_widget = QWidget()
        self.layout().addWidget(content_widget)
        self.content_widget_layout = VerticalLayout()
        content_widget.setLayout(self.content_widget_layout)

    @pyqtSlot(object)
    def _on_new_equipment_datas(self, equipment: ReadEquipmentSchema) -> None:
        related_fm_item = self.fm_items[equipment]
        related_fm_item._on_new_equipment_datas(equipment)

    def _insert_and_get_fm_item(self) -> FmItem:
        related_fm_item = FmItem(self.logger, self.service)
        related_fm_item.signals.saved_item.connect(self._on_saved_equipment)
        related_fm_item.signals.created_item.connect(self._on_created_equipment)
        related_fm_item.signals.deleted_item.connect(self._on_deleted_equipment)
        self.content_widget_layout.insertWidget(0, related_fm_item)
        return related_fm_item

    def _on_selected_item(self, index: int) -> None:
        if self.curr_fm_item:
            self.curr_fm_item.hide()
            self.curr_fm_item = None
        equipment: ReadEquipmentSchema | None = self.equipment_combo.itemData(index)
        if equipment is None:
            return
        related_fm_item = self.fm_items.get(equipment, None)
        if not related_fm_item:
            related_fm_item = self._insert_and_get_fm_item()
            self.fm_items[equipment] = related_fm_item

        related_fm_item.show()
        related_fm_item.set_item_from_equipment(equipment)

        curr_index = self.equipment_combo.findData(related_fm_item.equipment)
        self.equipment_combo.setCurrentIndex(curr_index)
        self.curr_fm_item = related_fm_item

    @pyqtSlot(object)
    def _on_deleted_equipment(self, equipment: ReadEquipmentSchema):
        self.equipment_combo.setCurrentIndex(0)
        related_index = self.equipment_combo.findData(equipment)
        self.equipment_combo.removeItem(related_index)

        del self.fm_items[equipment]
        assert self.curr_fm_item is not None
        self.curr_fm_item.deleteLater()
        self.curr_fm_item = None

    @pyqtSlot(object)
    def _on_saved_equipment(self, equipment: ReadEquipmentSchema):
        related_index = self.equipment_combo.findData(equipment)
        self.equipment_combo.setItemText(related_index, equipment.label)

    @pyqtSlot(object)
    def _on_created_equipment(self, equipment: ReadEquipmentSchema):
        self.equipment_combo.addItem(equipment.label, equipment)
        related_index = self.equipment_combo.findData(equipment)
        self.equipment_combo.setCurrentIndex(related_index)

    @pyqtSlot(object)
    def _on_refresh(self, bot: Bot):
        self.equipment_combo.setCurrentIndex(0)
        lines_item = bot.fm_analyser.get_stats_item_selected(bot.capturer.capture())
        if lines_item is None:
            return
        self.curr_fm_item = self._insert_and_get_fm_item()
        self.curr_fm_item.set_item_from_base_lines(lines_item)

    @pyqtSlot(object)
    def _on_play(self, bot: Bot):
        if self.curr_fm_item is None:
            self.play_stop_widget.on_click_stop()
            self.logger.warning("Veuillez sélectionner un item.")
            return
        lines = self.curr_fm_item.get_edited_lines()
        exo_stat = self.curr_fm_item.get_exo_stat()
        equipment = self.curr_fm_item.equipment

        self.thread_run, self.worker_run = run_in_background(
            lambda: bot.run_fm(
                lines,
                exo_stat,
                equipment,
            )
        )

    @pyqtSlot(object)
    def _on_stop(self, bot: Bot):
        self.thread_stop, self.worker_stop = run_in_background(bot.stop_bot)
