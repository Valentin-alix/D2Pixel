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
from src.gui.workers.worker_fm import WorkerFm
from src.gui.workers.worker_stop import WorkerStop
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

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_action_widget()
        self._setup_top_page()
        self._setup_content()

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
        content_widget_layout = VerticalLayout()
        content_widget.setLayout(content_widget_layout)

        self.fm_item: FmItem = FmItem(self.logger, self.service)
        self.fm_item.hide()
        self.fm_item.signals.saved_item.connect(self._on_saved_equipment)
        self.fm_item.signals.created_item.connect(self._on_created_equipment)
        self.fm_item.signals.deleted_item.connect(self._on_deleted_equipment)
        content_widget_layout.insertWidget(0, self.fm_item)

    @pyqtSlot(int)
    def _on_selected_item(self, index: int) -> None:
        equipment: ReadEquipmentSchema | None = self.equipment_combo.itemData(index)
        if equipment is None:
            self.fm_item.hide()
            return
        self.fm_item.set_item_from_equipment(equipment)
        curr_index = self.equipment_combo.findData(self.fm_item.equipment)
        self.equipment_combo.setCurrentIndex(curr_index)
        self.fm_item.show()

    @pyqtSlot(object)
    def _on_deleted_equipment(self, equipment: ReadEquipmentSchema):
        self.equipment_combo.setCurrentIndex(0)
        related_index = self.equipment_combo.findData(equipment)
        self.equipment_combo.removeItem(related_index)
        self.fm_item.hide()

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
        bot.init_bot()
        lines_item = bot.fm_analyser.get_stats_item_selected(bot.capturer.capture())
        if lines_item is None:
            self.fm_item.hide()
            return
        self.fm_item.set_item_from_base_lines(lines_item)
        self.fm_item.show()

    @pyqtSlot(object)
    def _on_play(self, bot: Bot):
        if self.fm_item.isHidden():
            self.play_stop_widget.button_play.show()
            self.play_stop_widget.button_stop.hide()
            self.logger.warning("Veuillez sélectionner un item.")
            return

        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerFm(
            bot,
            self.fm_item.get_edited_lines(),
            self.fm_item.get_exo_stat(),
        )
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

    @pyqtSlot(object)
    def _on_stop(self, bot: Bot):
        if self.thread_stop is not None:
            self.thread_stop.quit()
            self.thread_stop.wait()

        self.worker_stop = WorkerStop(bot)
        self.thread_stop = QThread()

        self.worker_stop.moveToThread(self.thread_stop)
        self.thread_stop.started.connect(self.worker_stop.run)
        self.thread_stop.finished.connect(self.worker_stop.deleteLater)
        self.thread_stop.start()
