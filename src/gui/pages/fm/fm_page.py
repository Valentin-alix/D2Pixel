from logging import Logger
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QWidget

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.stat import LineSchema, StatSchema
from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.loaders import Loading
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.pages.fm.fm_item import FmItem
from src.gui.pages.worker_stop import WorkerStopActions
from src.services.equipment import EquipmentService
from src.services.session import ServiceSession


class WorkerRunFm(QObject):
    def __init__(
        self,
        module_manager: ModuleManager,
        lines: list[LineSchema],
        exo: StatSchema | None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.module_manager = module_manager
        self.lines = lines
        self.exo = exo

    @pyqtSlot()
    def run(self):
        self.module_manager.run_fm(self.lines, self.exo)


class FmPage(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        module_manager: ModuleManager,
        app_logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.service = service
        self.module_manager = module_manager
        self.is_loading = False
        self.logger = app_logger

        self.current_item: FmItem | None = None
        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.set_top_page()
        self.set_action_widget()

        self.module_manager.bot_signals.is_stopping_bot.connect(
            self.on_new_is_stopping_bot
        )

    def set_top_page(self):
        button_refr_wid = QWidget()
        self.main_layout.addWidget(button_refr_wid)
        refr_layout = HorizontalLayout()
        refr_layout.setAlignment(Qt.AlignCenter)
        button_refr_wid.setLayout(refr_layout)
        self.button_refresh = PushButtonIcon(
            "restart.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_refresh.setCheckable(False)
        self.button_refresh.clicked.connect(self.on_refresh)
        refr_layout.addWidget(self.button_refresh)

        self.equipment_combo = QComboBox()
        self.refresh_equipments()
        self.equipment_combo.currentIndexChanged.connect(self.on_selected_item)
        self.main_layout.addWidget(self.equipment_combo)

    def set_action_widget(self):
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

        self.button_play.clicked.connect(self.on_play)
        self.button_stop.clicked.connect(self.on_stop)

    def refresh_state_play_stop_btn(self):
        if self.module_manager.is_playing.is_set():
            self.button_play.hide()
            self.button_stop.show()
        else:
            self.button_stop.hide()
            self.button_play.show()

    def on_play(self):
        if self.current_item is None:
            self.logger.warning("Veuillez sélectionner un item.")
            return

        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerRunFm(
            self.module_manager,
            self.current_item.get_edited_lines(),
            self.current_item.get_exo(),
        )
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

    def on_stop(self):
        if self.thread_stop is not None:
            self.thread_stop.quit()
            self.thread_stop.wait()

        self.worker_stop = WorkerStopActions(self.module_manager)
        self.thread_stop = QThread()

        self.worker_stop.moveToThread(self.thread_stop)
        self.thread_stop.started.connect(self.worker_stop.run)
        self.thread_stop.finished.connect(self.worker_stop.deleteLater)
        self.thread_stop.start()

    def refresh_equipments(self):
        equipments = EquipmentService.get_equipments(self.service)
        self.equipment_combo.clear()
        self.equipment_combo.addItem("", None)
        for equipment in equipments:
            self.equipment_combo.addItem(equipment.label, equipment)

    def on_selected_item(self):
        equipment: ReadEquipmentSchema | None = self.equipment_combo.currentData()
        if equipment is None:
            return
        if self.current_item is not None:
            self.main_layout.removeWidget(self.current_item)
            self.current_item.deleteLater()
            self.current_item = None

        self.current_item = FmItem(
            self.service, equipment.label, equipment.lines, equipment.id
        )
        self.current_item.signals.deleted_item.connect(self.clear_current_item)
        self.main_layout.addWidget(self.current_item)

    def clear_current_item(self):
        self.refresh_equipments()
        if self.current_item is not None:
            self.main_layout.removeWidget(self.current_item)
            self.current_item.deleteLater()
            self.current_item = None
            self.equipment_combo.setCurrentIndex(0)

    def on_refresh(self):
        self.clear_current_item()

        lines_item = self.module_manager.fm_analyser.get_stats_item_selected(
            self.module_manager.capturer.capture()
        )
        if lines_item is None:
            return
        self.current_item = FmItem(self.service, "", lines_item)
        self.current_item.signals.saved_item.connect(self.refresh_equipments)
        self.current_item.signals.deleted_item.connect(self.clear_current_item)
        self.main_layout.addWidget(self.current_item)

    @pyqtSlot(bool)
    def on_new_is_stopping_bot(self, value: bool):
        self.is_loading = value
        if value:
            self.loading.start()
            self.action_content.hide()
        else:
            self.refresh_state_play_stop_btn()
            self.action_content.show()
            self.loading.stop()
