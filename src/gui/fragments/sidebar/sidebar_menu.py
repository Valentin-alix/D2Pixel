from collections import OrderedDict
from logging import Logger

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QSizePolicy, QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.modules.bot import Bot
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.loaders import Loading
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.fragments.sidebar.settings.user_settings_modal import (
    UserSettingsModal,
)
from src.gui.fragments.sidebar.sidebar_menu_item import SideBarMenuItem
from src.gui.fragments.sidebar.stats_dialog.stats_dialog import StatsDialog
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


class SideBarMenuSignals(QObject):
    clicked_bot = pyqtSignal(object)
    clicked_restart = pyqtSignal()


class SideBarMenu(QWidget):
    WIDTH: int = 240

    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        app_signals: AppSignals,
        user: ReadUserSchema,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.signals = SideBarMenuSignals()
        self.service = service
        self.logger = logger
        self.app_signals = app_signals
        self.user = user
        self.menu_item_by_char: OrderedDict[CharacterSchema, SideBarMenuItem] = (
            OrderedDict()
        )
        self.selected_menu_item: SideBarMenuItem | None = None

        self.setProperty("class", "border-right-slim")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(self.WIDTH)
        main_layout = VerticalLayout(margins=(4, 4, 4, 4))
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        self._setup_list_character()

        main_layout.addStretch(1)

        self.stat_dialog: StatsDialog | None = None
        self.user_settings_dialog: UserSettingsModal | None = None

        self._setup_footer()

        self.app_signals.is_connecting.connect(self.on_connection_loading)

    def _setup_list_character(self):
        self.list_character_widget = QWidget(parent=self)
        self.list_character_widget.setLayout(VerticalLayout(space=0))
        self.layout().addWidget(self.list_character_widget)
        self.list_char_widget_loading = Loading(parent=self)
        self.layout().addWidget(self.list_char_widget_loading)

    def _setup_footer(self) -> None:
        footer = QWidget()
        footer.setLayout(HorizontalLayout(space=4))
        self.layout().addWidget(footer)

        self.refresh_btn = PushButtonIcon("restart.svg", parent=self)
        self.refresh_btn.clicked.connect(self.signals.clicked_restart)
        footer.layout().addWidget(self.refresh_btn)

        self.stats_btn = PushButtonIcon("stats.svg", parent=self)
        self.stats_btn.clicked.connect(self.on_clicked_stats)
        footer.layout().addWidget(self.stats_btn)

        self.settings_btn = PushButtonIcon("settings.svg", parent=self)
        self.settings_btn.clicked.connect(self.on_clicked_settings)
        footer.layout().addWidget(self.settings_btn)

    def add_bot(self, bot: Bot) -> None:
        side_bar_menu_item = SideBarMenuItem(
            self.logger, self.service, bot=bot, parent=self
        )
        self.menu_item_by_char[bot.character_state.character] = side_bar_menu_item
        side_bar_menu_item.btn_char.clicked.connect(
            lambda: self.on_clicked_character(bot.character_state.character)
        )
        self.list_character_widget.layout().addWidget(side_bar_menu_item)
        if self.selected_menu_item is None:
            self.selected_menu_item = side_bar_menu_item
            side_bar_menu_item.btn_char.setChecked(True)
            side_bar_menu_item.btn_char.setEnabled(False)

    def remove_character(self, character: CharacterSchema) -> None:
        related_widget = self.menu_item_by_char.pop(character, None)
        if related_widget is None:
            return
        self.list_character_widget.layout().removeWidget(related_widget)
        related_widget.deleteLater()
        if self.selected_menu_item == related_widget:
            next_character = next(iter(self.menu_item_by_char.keys()), None)
            if next_character is not None:
                self.on_clicked_character(next_character)
            else:
                self.selected_menu_item = None

    def on_characters_connected(self, bots_by_id: dict[str, Bot]) -> None:
        untreated_chars: list[CharacterSchema] = list(self.menu_item_by_char.keys())
        for bot in bots_by_id.values():
            if bot.character_state.character not in self.menu_item_by_char.keys():
                self.add_bot(bot)
            if bot.character_state.character in untreated_chars:
                untreated_chars.remove(bot.character_state.character)

        for char in untreated_chars:
            self.remove_character(char)

    @pyqtSlot(bool)
    def on_connection_loading(self, is_loading: bool):
        self.refresh_btn.setEnabled(not is_loading)
        if is_loading:
            self.list_char_widget_loading.start()
        else:
            self.list_char_widget_loading.stop()

    def on_clicked_character(self, character: CharacterSchema):
        if self.selected_menu_item is not None:
            self.selected_menu_item.btn_char.setEnabled(True)
            self.selected_menu_item.btn_char.setChecked(False)

        related_item = self.menu_item_by_char[character]
        self.selected_menu_item = related_item

        related_item.btn_char.setEnabled(False)
        related_item.btn_char.setChecked(True)

        self.signals.clicked_bot.emit(character)

    @pyqtSlot()
    def on_clicked_settings(self):
        if self.user_settings_dialog is None:
            self.user_settings_dialog = UserSettingsModal(
                self.logger, self.app_signals, self.user, self.service
            )
        self.user_settings_dialog.open()

    @pyqtSlot()
    def on_clicked_stats(self):
        if self.stat_dialog is None:
            self.stat_dialog = StatsDialog(self.service, 1)
        self.stat_dialog.open()
