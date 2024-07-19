import os
from logging import Logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from src.bots.modules.bot import Bot
from src.gui.components.buttons import (
    PushButtonIcon,
    ToolButtonIcon,
)
from src.gui.components.organization import HorizontalLayout
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

        self._setup_btns()

        self.bot.bot_signals.connected_bot.connect(self.on_connected_bot)
        self.bot.bot_signals.disconnected_bot.connect(self.on_disconnected_bot)

    def alight_button(self):
        self.btn_char.setStyleSheet(
            f"border-right-color: {os.environ.get("QTMATERIAL_PRIMARYCOLOR")};"
        )

    def turn_off_button(self):
        self.btn_char.setStyleSheet(
            f"border-right-color: {os.environ.get("QTMATERIAL_SECONDARYLIGHTCOLOR")};"
        )

    @pyqtSlot()
    def on_connected_bot(self):
        self.alight_button()

    @pyqtSlot()
    def on_disconnected_bot(self):
        self.turn_off_button()

    def _setup_btns(self):
        self.btn_char = ToolButtonIcon(
            width=150, height=80, icon_size=32, checkable=True, filename="people.svg"
        )
        self.btn_char.setAutoRaise(True)
        self.btn_char.setLayoutDirection(Qt.LeftToRight)
        self.btn_char.setText(self.bot.character_id)
        self.layout().addWidget(self.btn_char)

        self.bot_settings_btn = PushButtonIcon(
            checkable=False, flat=True, filename="settings.svg", width=40, height=80
        )
        self.bot_settings_btn.clicked.connect(self.on_click_settings)
        self.layout().addWidget(self.bot_settings_btn)

        self.bot_delete_btn = PushButtonIcon(
            checkable=False, flat=True, filename="delete.svg", width=40, height=80
        )
        self.layout().addWidget(self.bot_delete_btn)

    @pyqtSlot()
    def on_click_settings(self):
        modal = BotSettingsModal(
            self.logger, self.service, self.bot.character_state.character
        )
        modal.open()
