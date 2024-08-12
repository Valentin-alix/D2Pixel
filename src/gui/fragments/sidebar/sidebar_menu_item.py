from logging import Logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from src.bots.modules.bot import Bot
from src.gui.components.buttons import (
    LocalPushButtonIcon,
    LocalToolButtonIcon,
)
from src.gui.components.organization import HorizontalLayout
from src.gui.fragments.sidebar.bot_log_dialog import BotLogDialog
from src.gui.fragments.sidebar.settings.bot_settings_modal.bot_settings_modal import (
    BotSettingsModal,
)
from src.services.session import ServiceSession


class SideBarMenuItem(QWidget):
    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        bot: Bot,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.bot = bot
        self.setLayout(HorizontalLayout(space=0, margins=(0, 0, 0, 0)))

        self.bot_log_dialog = BotLogDialog(self.bot)
        self.bot_settings_dialog: BotSettingsModal | None = None
        self._setup_btns()

    def _setup_btns(self):
        self.btn_char = LocalToolButtonIcon(
            width=150, height=80, icon_size=32, filename="people.svg"
        )
        self.btn_char.setCheckable(True)
        self.btn_char.setAutoRaise(True)
        self.btn_char.setLayoutDirection(Qt.LeftToRight)
        self.btn_char.setText(self.bot.character_id)
        self.layout().addWidget(self.btn_char)

        self.logs_btn = LocalPushButtonIcon(
            "logs.svg", width=40, height=80, parent=self
        )
        self.logs_btn.setFlat(True)
        self.logs_btn.clicked.connect(self.on_clicked_logs)
        self.layout().addWidget(self.logs_btn)

        self.bot_settings_btn = LocalPushButtonIcon(
            filename="settings.svg", width=40, height=80
        )
        self.bot_settings_btn.setFlat(True)
        self.bot_settings_btn.clicked.connect(self.on_click_settings)
        self.layout().addWidget(self.bot_settings_btn)

    @pyqtSlot()
    def on_click_settings(self):
        if self.bot_settings_dialog is None:
            self.bot_settings_dialog = BotSettingsModal(
                self.logger, self.service, self.bot.character_state.character
            )
        self.bot_settings_dialog.set_default_values()
        self.bot_settings_dialog.open()

    @pyqtSlot()
    def on_clicked_logs(self):
        self.bot_log_dialog.open()
