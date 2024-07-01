from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
)

from src.bots.modules.module_manager import DEFAULT_MODULES, ModuleManager
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.loaders import Loading
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.pages.modules.logs import LogBox
from src.gui.pages.modules.workers_action import (
    WorkerRunActions,
    WorkerStopActions,
)


class ModulesPage(QWidget):
    thread_run: QThread | None = None
    thread_stop: QThread | None = None

    def __init__(self, module_manager: ModuleManager):
        super().__init__()
        self.module_manager = module_manager
        self.is_loading = False

        self.main_layout = VerticalLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.set_action_widget()

        self.set_module_combobox()

        self.setup_info_action()

        self.set_content()

        self.module_manager.bot_signals.is_stopping_bot.connect(
            self.on_new_is_stopping_bot
        )

    def set_module_combobox(self):
        self.combo_modules = CheckableComboBox(parent=self)
        for name in DEFAULT_MODULES:
            self.combo_modules.addItem(name, checked=True)
        self.main_layout.addWidget(self.combo_modules)

    def set_content(self):
        self.log_box = LogBox(bot_signals=self.module_manager.bot_signals)
        self.main_layout.addWidget(self.log_box)

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

    def setup_info_action(self):
        self.info_action = QWidget()
        self.main_layout.addWidget(self.info_action)
        self.info_action.hide()
        self.info_action_layout = HorizontalLayout()
        self.info_action.setLayout(self.info_action_layout)

        self.name_action = QLabel()
        self.info_action_layout.addWidget(self.name_action)
        self.module_manager.bot_signals.playing_action.connect(self.on_playing_action)

    @pyqtSlot(str)
    def on_playing_action(self, name: str):
        self.name_action.setText(name)
        self.info_action.show()

    def refresh_state_play_stop_btn(self):
        if self.module_manager.is_playing.is_set():
            self.button_play.hide()
            self.button_stop.show()
        else:
            self.button_stop.hide()
            self.button_play.show()

    def on_play(self):
        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerRunActions(
            self.module_manager, name_modules=self.combo_modules.currentData()
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

    @pyqtSlot(bool)
    def on_new_is_stopping_bot(self, value: bool):
        self.is_loading = value
        if value:
            self.loading.start()
            self.action_content.hide()
            self.info_action.hide()
        else:
            self.refresh_state_play_stop_btn()
            self.action_content.show()
            self.info_action.show()
            self.loading.stop()
