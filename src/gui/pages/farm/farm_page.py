from logging import Logger

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
)

from src.bots.modules.bot import DEFAULT_MODULES, Bot
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.organization import (
    VerticalLayout,
)
from src.gui.components.play_stop import PlayStopWidget
from src.gui.signals.app_signals import AppSignals
from src.gui.workers.worker_farm import (
    WorkerFarm,
)
from src.gui.workers.worker_stop import WorkerStop


class FarmPage(QWidget):
    def __init__(self, logger: Logger, app_signals: AppSignals, bot: Bot):
        super().__init__()
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.bot = bot
        self.is_loading = False
        self.app_signals = app_signals
        self.logger = logger

        self.main_layout = VerticalLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_action_btns()

        self._setup_module_combobox()

        self._setup_info_action()

        self._setup_content()

        bot.bot_signals.playing_action.connect(self.on_playing_action)
        self.play_stop_widget.signals.played.connect(lambda: self.on_play(bot))
        self.play_stop_widget.signals.stopped.connect(lambda: self.on_stop(bot))

    def _setup_module_combobox(self):
        self.combo_modules = CheckableComboBox[str](parent=self)
        for module_name in DEFAULT_MODULES:
            self.combo_modules.addItem(module_name, checked=True)
        self.layout().addWidget(self.combo_modules)

    def _setup_info_action(self):
        self.name_action = QLabel()
        self.layout().addWidget(self.name_action)

    def _setup_content(self): ...

    def _setup_action_btns(self):
        self.play_stop_widget = PlayStopWidget(self.app_signals, self.bot.bot_signals)
        self.layout().addWidget(self.play_stop_widget)

    @pyqtSlot(str)
    def on_playing_action(self, name: str):
        self.name_action.setText(name)

    @pyqtSlot(object)
    def on_play(self, bot: Bot):
        name_modules = self.combo_modules.currentData()
        if len(name_modules) == 0:
            self.play_stop_widget.on_click_stop()
            self.logger.warning("Veuillez sélectionner au moins une action.")
            return

        if self.thread_run is not None:
            self.thread_run.quit()
            self.thread_run.wait()

        self.worker_run = WorkerFarm(bot, name_modules=self.combo_modules.currentData())
        self.thread_run = QThread()

        self.worker_run.moveToThread(self.thread_run)
        self.thread_run.started.connect(self.worker_run.run)
        self.thread_run.finished.connect(self.worker_run.deleteLater)
        self.thread_run.start()

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

        self.name_action.setText("")
