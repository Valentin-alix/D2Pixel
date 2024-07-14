from logging import Logger

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QWidget

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.loaders import Loading
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.pages.bot_logs import LogBox
from src.gui.pages.fm.fm_item.fm_item import FmItem
from src.gui.pages.fm.fm_workers import WorkerRunFm
from src.gui.pages.stop_worker import WorkerStop
from src.services.equipment import EquipmentService
from src.services.session import ServiceSession


class FmPage(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        module_manager: ModuleManager,
        logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.module_manager = module_manager
        self.is_loading: bool = False
        self.logger = logger

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_top_page()
        self._setup_action_widget()
        self._setup_content()

        self.module_manager.bot_signals.is_stopping_bot.connect(
            self._on_new_is_stopping_bot
        )

    def _setup_top_page(self):
        button_refr_wid = QWidget()
        self.main_layout.addWidget(button_refr_wid)
        refr_layout = HorizontalLayout()
        refr_layout.setAlignment(Qt.AlignCenter)
        button_refr_wid.setLayout(refr_layout)
        self.button_refresh = PushButtonIcon(
            "restart.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_refresh.setCheckable(False)
        self.button_refresh.clicked.connect(self._on_refresh)
        refr_layout.addWidget(self.button_refresh)

        self.equipment_combo = QComboBox()
        self.equipment_combo.addItem("", None)
        self.equipments = EquipmentService.get_equipments(self.service)
        for equipment in self.equipments:
            self.equipment_combo.addItem(equipment.label, equipment)
        self.equipment_combo.currentIndexChanged.connect(self._on_selected_item)
        self.main_layout.addWidget(self.equipment_combo)

    def _setup_action_widget(self):
        self.action = QWidget()
        self.main_layout.addWidget(self.action)
        self.action_layout = HorizontalLayout()
        self.action.setLayout(self.action_layout)

        self.loading = Loading(parent=self.action)
        self.action.setFixedHeight(self.loading.height() + 5)

        self.action_layout.addWidget(self.loading)

        self.action_content = QWidget()
        self.action_layout.addWidget(self.action_content)
        self.action_content_layout = HorizontalLayout()
        self.action_content_layout.setAlignment(Qt.AlignCenter)
        self.action_content.setLayout(self.action_content_layout)

        self.button_play = PushButtonIcon(
            "play.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_play.setCheckable(False)
        self.action_content_layout.addWidget(self.button_play)

        self.button_stop = PushButtonIcon(
            "stop.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_stop.setCheckable(False)
        self.action_content_layout.addWidget(self.button_stop)

        self.refresh_state_play_stop_btn()

        self.button_play.clicked.connect(self._on_play)
        self.button_stop.clicked.connect(self._on_stop)

    def _setup_content(self):
        content_widget = QWidget()
        self.main_layout.addWidget(content_widget)
        self.content_layout = VerticalLayout()
        content_widget.setLayout(self.content_layout)

        self.fm_item: FmItem = FmItem(self.logger, self.service)
        self.fm_item.hide()
        self.fm_item.signals.saved_item.connect(self._on_saved_equipment)
        self.fm_item.signals.created_item.connect(self._on_created_equipment)
        self.fm_item.signals.deleted_item.connect(self._on_deleted_equipment)
        self.content_layout.insertWidget(0, self.fm_item)

        self.log_box = LogBox(bot_signals=self.module_manager.bot_signals)
        self.content_layout.addWidget(self.log_box)

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

    @pyqtSlot()
    def _on_refresh(self):
        self.equipment_combo.setCurrentIndex(0)
        lines_item = self.module_manager.fm_analyser.get_stats_item_selected(
            self.module_manager.capturer.capture()
        )
        if lines_item is None:
            self.fm_item.hide()
            return
        self.fm_item.set_item_from_base_lines(lines_item)
        self.fm_item.show()

    def refresh_state_play_stop_btn(self):
        if self.module_manager.is_playing.is_set():
            self.button_play.hide()
            self.button_stop.show()
        else:
            self.button_stop.hide()
            self.button_play.show()

    @pyqtSlot()
    def _on_play(self):
        if self.fm_item.isHidden():
            self.logger.warning("Veuillez sélectionner un item.")
            return

        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerRunFm(
            self.module_manager,
            self.fm_item.get_edited_lines(),
            self.fm_item.get_exo_stat(),
        )
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

    @pyqtSlot()
    def _on_stop(self):
        if self.thread_stop is not None:
            self.thread_stop.quit()
            self.thread_stop.wait()

        self.worker_stop = WorkerStop(self.module_manager)
        self.thread_stop = QThread()

        self.worker_stop.moveToThread(self.thread_stop)
        self.thread_stop.started.connect(self.worker_stop.run)
        self.thread_stop.finished.connect(self.worker_stop.deleteLater)
        self.thread_stop.start()

    @pyqtSlot(bool)
    def _on_new_is_stopping_bot(self, value: bool):
        self.is_loading = value
        if value:
            self.loading.start()
            self.action_content.hide()
        else:
            self.refresh_state_play_stop_btn()
            self.action_content.show()
            self.loading.stop()
