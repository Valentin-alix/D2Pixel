import os
import sys
from logging import Logger

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QMainWindow, QStackedWidget, QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from src.bots.bots_manager import BotsManager
from src.bots.modules.bot import Bot
from src.consts import ASSET_FOLDER_PATH
from src.gui.components.loaders import Loading
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.components.toastr import show_message
from src.gui.fragments.sidebar.sidebar_menu import SideBarMenu
from src.gui.fragments.sub_header.sub_header import SubHeader
from src.gui.pages.login.login_page import LoginModal
from src.gui.signals.app_signals import AppSignals
from src.gui.workers.worker_connect import WorkerConnect
from src.services.session import ServiceSession
from src.services.user import UserService


class MainWindow(QMainWindow):
    BASE_WIDTH: int = 1600
    BASE_HEIGHT: int = 900

    def __init__(
        self,
        title: str,
        logger: Logger,
        service: ServiceSession,
        app_signals: AppSignals,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.thread_connect_bots: QThread | None = None
        self.sub_header_by_character: dict[CharacterSchema, SubHeader] = {}

        icon_bot = QtGui.QIcon(
            os.path.join(ASSET_FOLDER_PATH, "icons", "logo_safe_bot.png")
        )
        self.setWindowIcon(icon_bot)
        self.app_signals = app_signals

        self.setWindowTitle(title)
        self.resize(self.BASE_WIDTH, self.BASE_HEIGHT)
        self.show()

        self.all_content = QWidget(parent=self)
        self.setCentralWidget(self.all_content)
        all_content_layout = VerticalLayout()
        all_content_layout.setAlignment(Qt.AlignTop)
        self.all_content.setLayout(all_content_layout)

        # content
        self.main_content = QWidget(parent=self)
        self.all_content.layout().addWidget(self.main_content)
        main_content_layout = HorizontalLayout()
        main_content_layout.setAlignment(Qt.AlignLeft)
        self.main_content.setLayout(main_content_layout)

        self.app_signals.connected_bots.connect(self.on_connected_bots)
        self.app_signals.login_failed.connect(self.on_login_failed)
        self.app_signals.log_info.connect(self.on_log_app)

        self.user = UserService.get_current_user(self.service)

        # sidebar
        self.sidebar = SideBarMenu(
            self.logger, self.service, self.app_signals, self.user
        )
        self.sidebar.signals.clicked_restart.connect(self._setup_bots)
        self.sidebar.signals.clicked_bot.connect(self.on_clicked_sidebar_char)
        self.main_content.layout().addWidget(self.sidebar)

        self.stacked_frames = QStackedWidget(parent=self.main_content)
        self.frame_loading = Loading(parent=self.stacked_frames)
        self.stacked_frames.addWidget(self.frame_loading)

        self.main_content.layout().addWidget(self.stacked_frames)

        self.app_signals.is_connecting.connect(self.on_connecting)

        self.bots_manager: BotsManager = BotsManager(
            logger, service, app_signals, self.user
        )
        self._setup_bots()

    def _setup_bots(self):
        self.app_signals.is_connecting.emit(True)

        if self.thread_connect_bots is not None:
            self.thread_connect_bots.quit()
            self.thread_connect_bots.wait()

        self.worker_connect_bots = WorkerConnect(self.bots_manager, self.app_signals)
        self.thread_connect_bots = QThread()

        self.worker_connect_bots.moveToThread(self.thread_connect_bots)
        self.thread_connect_bots.started.connect(self.worker_connect_bots.run)
        self.thread_connect_bots.finished.connect(self.worker_connect_bots.deleteLater)
        self.thread_connect_bots.start()

    def add_bot(self, bot: Bot) -> None:
        character = bot.character_state.character
        related_menu_item = self.sub_header_by_character.get(character)
        if not related_menu_item:
            related_menu_item = SubHeader(
                self.service,
                self.app_signals,
                bot,
                self.logger,
                parent=self.stacked_frames,
            )
            self.sub_header_by_character[character] = related_menu_item
            self.stacked_frames.addWidget(related_menu_item)
        if len(self.sub_header_by_character) == 1:
            self.stacked_frames.setCurrentWidget(related_menu_item)

    def remove_character(self, character: CharacterSchema) -> None:
        related_menu_item = self.sub_header_by_character.pop(character, None)
        if related_menu_item is None:
            return
        self.stacked_frames.removeWidget(related_menu_item)
        related_menu_item.deleteLater()
        if len(self.sub_header_by_character) == 0:
            # otherwhise loading is not hidden
            self.frame_loading.stop()

    @pyqtSlot(object)
    def on_clicked_sidebar_char(self, character: CharacterSchema):
        related_width = self.sub_header_by_character[character]
        self.stacked_frames.setCurrentWidget(related_width)

    @pyqtSlot(object)
    def on_log_app(self, log_info: tuple[int, str]):
        log_lvl, msg = log_info
        show_message(
            self,
            msg,
            log_lvl,
            corner=QtCore.Qt.Corner.BottomRightCorner,
        )

    @pyqtSlot()
    def on_login_failed(self):
        input_dialog = LoginModal(app_signals=self.app_signals, service=self.service)
        if input_dialog.exec_() != QDialog.Accepted:
            sys.exit()

    @pyqtSlot(bool)
    def on_connecting(self, is_loading: bool):
        if is_loading:
            self.frame_loading.start()
        else:
            self.frame_loading.stop()

    @pyqtSlot(object)
    def on_connected_bots(self, bots_by_id: dict[str, Bot]):
        print(bots_by_id)
        self.sidebar.on_characters_connected(bots_by_id)
        untreated_character: list[CharacterSchema] = list(
            self.sub_header_by_character.keys()
        )
        for bot in bots_by_id.values():
            self.add_bot(bot)

            character = bot.character_state.character
            if character in untreated_character:
                untreated_character.remove(character)

        for character in untreated_character:
            self.remove_character(character)

        self.app_signals.is_connecting.emit(False)

    def closeEvent(self, _: QCloseEvent):
        self.app_signals.on_close.emit()
