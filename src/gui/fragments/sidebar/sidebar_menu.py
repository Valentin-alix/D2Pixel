from functools import partial

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QSizePolicy, QWidget

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButtonIcon, ToolButtonIcon
from src.gui.components.loaders import Loading
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.fragments.sidebar.settings.bot_settings_modal import (
    BotSettingsModal,
)
from src.gui.fragments.sidebar.settings.user_settings_modal import (
    UserSettingsModal,
)
from src.gui.fragments.sidebar.sidebar_signals import SideBarSignals
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


class SideBarMenuItem(QWidget):
    def __init__(
        self, service: ServiceSession, module_manager: ModuleManager, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.main_layout = HorizontalLayout()
        self.setLayout(self.main_layout)
        self.module_manager = module_manager

        self.btn_char = ToolButtonIcon(
            width=150, height=80, icon_size=32, checkable=True, filename="people.svg"
        )
        self.btn_char.setLayoutDirection(Qt.LeftToRight)
        self.btn_char.setText(module_manager.character_state.character.id)
        self.main_layout.addWidget(self.btn_char)

        self.bot_settings_btn = PushButtonIcon(
            checkable=False, flat=True, filename="settings.svg", width=30, height=80
        )
        self.bot_settings_btn.clicked.connect(self.on_click_settings)
        self.main_layout.addWidget(self.bot_settings_btn)

    @pyqtSlot()
    def on_click_settings(self):
        modal = BotSettingsModal(self.service, self.module_manager)
        modal.open()


class SideBarMenu(QWidget):
    WIDTH = 190

    def __init__(
        self,
        service: ServiceSession,
        side_bar_signals: SideBarSignals,
        app_signals: AppSignals,
        user: ReadUserSchema,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setProperty("class", "border-right-slim")
        self.service = service
        self.app_signals = app_signals
        self.side_bar_signals = side_bar_signals
        self.user = user
        self.current_index = 0
        self.bot_items: list[SideBarMenuItem] = []

        self.app_signals.bots_initialized.connect(self.on_bots_initialized)
        self.app_signals.is_connecting_bots.connect(
            self.on_new_is_connecting_bots_value
        )

        self.side_bar_signals = side_bar_signals
        self.app_signals = app_signals
        self.setAttribute(
            Qt.WA_StyledBackground, True
        )  # to apply style to whole widget
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(self.WIDTH)

        self.main_layout = VerticalLayout(margins=(4, 4, 4, 4))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.setup_menu()

        self.main_layout.addStretch(1)

        self.set_bottom()

    def set_bottom(self):
        self.bottom = QWidget()
        self.main_layout.addWidget(self.bottom)
        self.bottom_layout = HorizontalLayout(space=4)
        self.bottom.setLayout(self.bottom_layout)

        self.button_refresh = PushButtonIcon("restart.svg", parent=self)
        self.button_refresh.setCheckable(False)
        self.bottom_layout.addWidget(self.button_refresh)

        self.button_settings = PushButtonIcon("settings.svg", parent=self)
        self.button_settings.clicked.connect(self.on_clicked_settings)
        self.button_settings.setCheckable(False)
        self.bottom_layout.addWidget(self.button_settings)

    def setup_menu(self):
        self.bot_list = QWidget(parent=self)
        self.loading = Loading(parent=self)
        self.main_layout.addWidget(self.loading)
        self.main_layout.addWidget(self.bot_list)
        self.bot_list_layout = VerticalLayout(space=0)
        self.bot_list.setLayout(self.bot_list_layout)

    @pyqtSlot(object)
    def on_bots_initialized(self, module_managers: list[ModuleManager]):
        self.bot_list_layout.clear_list()
        self.bot_items = []
        self.current_index = 0
        for index, module_manager in enumerate(module_managers):
            bot_item = SideBarMenuItem(
                self.service, module_manager=module_manager, parent=self
            )
            bot_item.btn_char.clicked.connect(partial(self.on_clicked_bot, index))

            self.bot_list_layout.addWidget(bot_item)

            self.bot_items.append(bot_item)

            if index == 0:
                bot_item.btn_char.setChecked(True)
                bot_item.btn_char.setEnabled(False)

    @pyqtSlot(bool)
    def on_new_is_connecting_bots_value(self, is_loading: bool):
        if is_loading:
            self.bot_list.hide()
            self.loading.start()
            self.button_refresh.setEnabled(False)
        else:
            self.bot_list.show()
            self.loading.stop()
            self.button_refresh.setEnabled(True)

    def on_clicked_bot(self, index: int):
        related_item = self.bot_items[index]

        self.bot_items[self.current_index].btn_char.setEnabled(True)
        self.bot_items[self.current_index].btn_char.setChecked(False)
        self.current_index = index

        self.side_bar_signals.clicked_bot.emit(index)

        related_item.btn_char.setEnabled(False)

    @pyqtSlot()
    def on_clicked_settings(self):
        modal = UserSettingsModal(self.app_signals, self.user, self.service)
        modal.open()
