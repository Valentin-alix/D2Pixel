from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget

from src.gui.components.buttons import PushButtonIcon
from src.gui.components.loaders import Loading
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.signals.app_signals import AppSignals
from src.gui.signals.bot_signals import BotSignals


class PlayStopSignals(QObject):
    played = pyqtSignal()
    stopped = pyqtSignal()


class PlayStopWidget(QWidget):
    def __init__(
        self, app_signals: AppSignals, bot_signals: BotSignals, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setLayout(VerticalLayout())
        self.signals = PlayStopSignals()
        self._setup_btns()
        bot_signals.is_stopping_bot.connect(self.on_new_is_stopping_bot)
        app_signals.is_connecting.connect(self.on_connecting)

    def _setup_btns(self):
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
        self.button_play.clicked.connect(self.on_play)
        self.action_content.layout().addWidget(self.button_play)

        self.button_stop = PushButtonIcon(
            "stop.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_stop.hide()
        self.button_stop.clicked.connect(self.on_stop)
        self.action_content.layout().addWidget(self.button_stop)

    @pyqtSlot(bool)
    def on_connecting(self, is_loading: bool):
        if is_loading:
            self.button_play.setDisabled(True)
            self.button_stop.setDisabled(True)
        else:
            self.button_play.setDisabled(False)
            self.button_stop.setDisabled(False)

    @pyqtSlot()
    def on_play(self):
        self.button_play.hide()
        self.button_stop.show()
        self.signals.played.emit()

    @pyqtSlot()
    def on_stop(self):
        self.button_stop.hide()
        self.button_play.show()
        self.signals.stopped.emit()

    @pyqtSlot(bool)
    def on_new_is_stopping_bot(self, value: bool):
        self.is_loading = value
        if value:
            self.action_content.hide()
            self.action_loading.start()
        else:
            self.action_loading.stop()
            self.action_content.show()
