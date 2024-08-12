from logging import Logger

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import (
    QLabel,
    QTabWidget,
    QWidget,
)

from src.bots.modules.bot import DEFAULT_FARMING_ACTIONS, Bot, FarmingAction
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.organization import (
    VerticalLayout,
)
from src.gui.components.play_stop import PlayStopWidget
from src.gui.pages.farm.path_farm_tab import PathFarmTab
from src.gui.pages.farm.sub_area_farm_tab import SubAreaFarmTab
from src.gui.signals.app_signals import AppSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.session import ServiceSession


class FarmPage(QWidget):
    def __init__(
        self, service: ServiceSession, logger: Logger, app_signals: AppSignals, bot: Bot
    ):
        super().__init__()
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.bot = bot
        self.is_loading = False
        self.app_signals = app_signals
        self.logger = logger
        self.service = service

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
        for action_name in FarmingAction:
            self.combo_modules.addItem(
                action_name, checked=action_name in DEFAULT_FARMING_ACTIONS
            )
        self.layout().addWidget(self.combo_modules)

    def _setup_info_action(self):
        self.name_action = QLabel()
        self.layout().addWidget(self.name_action)

    def _setup_content(self):
        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)
        self.sub_area_tabs = SubAreaFarmTab(
            self.service, self.bot.character_state.character
        )
        self.tabs.addTab(self.sub_area_tabs, "Zones")

        self.path_farm_tab = PathFarmTab(
            self.service, self.bot.character_state.character
        )
        self.tabs.addTab(self.path_farm_tab, "Chemins")

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

        self.thread_run, self.worker_run = run_in_background(
            lambda: bot.run_farming(self.combo_modules.currentData())
        )

    @pyqtSlot(object)
    def on_stop(self, bot: Bot):
        self.thread_stop, self.worker_stop = run_in_background(bot.stop_bot)
        self.name_action.setText("")
