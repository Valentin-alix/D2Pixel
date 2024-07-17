from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
)

from src.bots.modules.bot import DEFAULT_MODULES, Bot
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.loaders import Loading
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.pages.bot_logs import LogBox
from src.gui.workers.worker_farm import (
    WorkerFarm,
)
from src.gui.workers.worker_stop import WorkerStop


class FarmPage(QWidget):
    def __init__(self, bot: Bot):
        super().__init__()
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.bot = bot
        self.is_loading = False

        self.main_layout = VerticalLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_action_btns()

        self._setup_module_combobox()

        self._setup_info_action()

        self._setup_content()

        bot.bot_signals.is_stopping_bot.connect(self.on_new_is_stopping_bot)
        bot.bot_signals.log_info.connect(self.log_box.add_log_msg)
        bot.bot_signals.playing_action.connect(self.on_playing_action)
        self.button_play.clicked.connect(lambda: self.on_play(bot))
        self.button_stop.clicked.connect(lambda: self.on_stop(bot))

        self.bot.bot_signals.connected_bot.connect(self.on_connected_bot)
        self.bot.bot_signals.disconnected_bot.connect(self.on_disconnected_bot)

    @pyqtSlot()
    def on_connected_bot(self):
        self.button_play.setDisabled(False)

    @pyqtSlot()
    def on_disconnected_bot(self):
        self.button_play.setDisabled(True)

    def _setup_module_combobox(self):
        self.combo_modules = CheckableComboBox[str](parent=self)
        for module_name in DEFAULT_MODULES:
            self.combo_modules.addItem(module_name, checked=True)
        self.layout().addWidget(self.combo_modules)

    def _setup_info_action(self):
        self.name_action = QLabel()
        self.layout().addWidget(self.name_action)

    def _setup_content(self):
        self.log_box = LogBox()
        self.layout().addWidget(self.log_box)

    def _setup_action_btns(self):
        self.action_widget = QWidget()
        self.layout().addWidget(self.action_widget)
        self.action_widget.setLayout(HorizontalLayout())

        self.action_loading = Loading(parent=self.action_widget)
        self.action_widget.setFixedHeight(self.action_loading.height() + 5)

        self.action_widget.layout().addWidget(self.action_loading)

        self.action_content = QWidget()
        self.action_widget.layout().addWidget(self.action_content)

        self.action_content_layout = HorizontalLayout()
        self.action_content_layout.setAlignment(Qt.AlignCenter)
        self.action_content.setLayout(self.action_content_layout)

        self.button_play = PushButtonIcon(
            "play.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_play.setDisabled(True)
        self.button_play.setCheckable(False)
        self.action_content.layout().addWidget(self.button_play)

        self.button_stop = PushButtonIcon(
            "stop.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_stop.setCheckable(False)
        self.button_stop.hide()
        self.action_content.layout().addWidget(self.button_stop)

    @pyqtSlot(str)
    def on_playing_action(self, name: str):
        self.name_action.setText(name)

    @pyqtSlot(object)
    def on_play(self, bot: Bot):
        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerFarm(bot, name_modules=self.combo_modules.currentData())
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

        self.button_stop.show()
        self.button_play.hide()

    @pyqtSlot(object)
    def on_stop(self, bot: Bot):
        if self.thread_stop is not None:
            self.thread_stop.quit()
            self.thread_stop.wait()

        self.worker_stop = WorkerStop(bot)
        self.thread_stop = QThread()

        self.worker_stop.moveToThread(self.thread_stop)
        self.thread_stop.started.connect(self.worker_stop.run)
        self.thread_stop.finished.connect(self.worker_stop.deleteLater)
        self.thread_stop.start()

        self.button_stop.hide()
        self.button_play.show()

    @pyqtSlot(bool)
    def on_new_is_stopping_bot(self, value: bool):
        self.is_loading = value
        if value:
            self.action_loading.start()
            self.action_content.hide()
        else:
            self.action_content.show()
            self.action_loading.stop()
