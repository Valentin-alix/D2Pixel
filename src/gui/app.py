import ctypes
import os
import sys
from logging import Logger
from time import sleep
from typing import cast

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import (
    QObject,
    Qt,
    QThread,
    pyqtSlot,
)
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QStackedWidget,
    QWidget,
)
from qt_material import apply_stylesheet

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.bots_manager import BotsManager
from src.bots.modules.module_manager import ModuleManager
from src.consts import ASSET_FOLDER_PATH, RESOURCE_FOLDER_PATH
from src.gui.components.loaders import Loading
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.components.toastr import show_message
from src.gui.fragments.sidebar.sidebar import SideBar
from src.gui.fragments.sub_header.sub_header import SubHeader
from src.gui.pages.farm.farm_page import ModulesPage
from src.gui.pages.login.login_page import LoginModal
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from src.services.user import UserService

TITLE = "D2SafeBot"


class WorkerSetupBots(QObject):
    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        app_signals: AppSignals,
        stacked_frames: QStackedWidget,
        user: ReadUserSchema,
        *args,
        **kwargs,
    ) -> None:
        self.logger = logger
        self.service = service
        self.app_signals = app_signals
        self.stacked_frames = stacked_frames
        self.user = user
        super().__init__(*args, **kwargs)

    @pyqtSlot()
    def run(self) -> None:
        module_tabs: list[ModulesPage] = []
        for index in range(self.stacked_frames.count()):
            widget = self.stacked_frames.widget(index)
            widget = cast(SubHeader, widget)
            widget.module_tab.on_stop()
            module_tabs.append(widget.module_tab)

        for elem in module_tabs:
            while elem.is_loading:
                sleep(0.5)
            if elem.thread_stop:
                elem.thread_stop.quit()
                elem.thread_stop.wait()
            if elem.thread_run:
                elem.thread_run.quit()
                elem.thread_run.wait()

        bots_manager = BotsManager(
            self.logger, self.service, self.app_signals, self.user
        )
        self.app_signals.bots_initialized.emit(bots_manager.module_managers)


class Application(QApplication):
    def __init__(self, argv) -> None:
        # authorize app to change icon of application
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "dofus.evoker_bot"
        )

        super().__init__(argv)
        self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.setApplicationName(TITLE)
        apply_stylesheet(
            self,
            theme="dark_pink.xml",
            css_file=os.path.join(RESOURCE_FOLDER_PATH, "styles.qss"),
        )


class MainWindow(QMainWindow):
    BASE_WIDTH = 1280
    BASE_HEIGHT = 720
    sidebar: SideBar

    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        app_signals: AppSignals,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.thread_setup_bots: QThread | None = None
        self.module_managers: list[ModuleManager] = []

        icon_bot = QtGui.QIcon(
            os.path.join(ASSET_FOLDER_PATH, "icons", "logo_evoker_bot.png")
        )
        self.setWindowIcon(icon_bot)
        # self.setWindowFlag(Qt.FramelessWindowHint)  # to hide topbar
        self.app_signals = app_signals

        self.setWindowTitle(TITLE)
        self.resize(self.BASE_WIDTH, self.BASE_HEIGHT)
        self.show()

        self.all_content = QWidget(parent=self)
        self.setCentralWidget(self.all_content)
        self.all_content_layout = VerticalLayout()
        self.all_content_layout.setAlignment(Qt.AlignTop)
        self.all_content.setLayout(self.all_content_layout)

        # content
        self.main_content = QWidget(parent=self)
        self.all_content_layout.addWidget(self.main_content)
        self.main_content_layout = HorizontalLayout()
        self.main_content_layout.setAlignment(Qt.AlignLeft)
        self.main_content.setLayout(self.main_content_layout)

        self.app_signals.bots_initialized.connect(self.on_bot_initialized)
        self.app_signals.is_connecting_bots.connect(self.on_connecting_bots)
        self.app_signals.login_failed.connect(self.on_login_failed)
        self.app_signals.lvl_with_title_and_msg.connect(self.on_log_app)

        self.user = UserService.get_current_user(self.service)

        # sidebar
        self.sidebar = SideBar(self.service, self.app_signals, self.user)
        self.sidebar.side_bar_menu.button_refresh.clicked.connect(self.setup_bots)
        self.main_content_layout.addWidget(self.sidebar)

        self.stacked_frames = QStackedWidget(parent=self.main_content)
        self.main_content_layout.addWidget(self.stacked_frames)
        self.sidebar.side_bar_signals.clicked_bot.connect(
            self.stacked_frames.setCurrentIndex
        )
        self.loading = Loading(parent=self.main_content)
        self.main_content_layout.addWidget(self.loading)

        self.setup_bots()

    def setup_bots(self):
        self.app_signals.is_connecting_bots.emit(True)

        if self.thread_setup_bots is not None:
            self.thread_setup_bots.quit()
            self.thread_setup_bots.wait()

        self.worker_setup_bots = WorkerSetupBots(
            self.logger,
            self.service,
            self.app_signals,
            stacked_frames=self.stacked_frames,
            user=self.user,
        )
        self.thread_setup_bots = QThread()

        self.worker_setup_bots.moveToThread(self.thread_setup_bots)
        self.thread_setup_bots.started.connect(self.worker_setup_bots.run)
        self.thread_setup_bots.finished.connect(self.worker_setup_bots.deleteLater)
        self.thread_setup_bots.start()

    def on_log_app(self, lvl_with_title_and_msg: tuple[int, str]):
        log_lvl, msg = lvl_with_title_and_msg
        show_message(
            self,
            msg,
            log_lvl,
            corner=QtCore.Qt.Corner.BottomRightCorner,
        )

    def on_login_failed(self):
        input_dialog = LoginModal(app_signals=self.app_signals, service=self.service)
        if input_dialog.exec_() != QDialog.Accepted:
            sys.exit()

    @pyqtSlot(bool)
    def on_connecting_bots(self, is_loading: bool):
        if is_loading:
            self.loading.start()
            self.stacked_frames.hide()
        else:
            self.loading.stop()
            self.stacked_frames.show()

    @pyqtSlot(object)
    def on_bot_initialized(self, module_managers: list[ModuleManager]):
        self.module_managers = module_managers
        # clear pages
        count_frames = self.stacked_frames.count()
        for _ in range(count_frames):
            widget = self.stacked_frames.widget(0)
            if widget is not None:
                widget.deleteLater()
            self.stacked_frames.removeWidget(widget)

        for module_manager in module_managers:
            sub_header = SubHeader(self.service, module_manager, self.logger)
            self.stacked_frames.addWidget(sub_header)

    def closeEvent(self, _: QCloseEvent):
        self.app_signals.on_close.emit()
