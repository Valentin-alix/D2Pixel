from logging import Logger

from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.user import ReadUserSchema
from src.gui.components.organization import HorizontalLayout
from src.gui.fragments.sidebar.sidebar_menu import SideBarMenu
from src.gui.fragments.sidebar.sidebar_signals import SideBarSignals
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


class SideBar(QWidget):
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
        self.side_bar_signals = SideBarSignals()
        self.app_signals = app_signals
        self.service = service
        self.user = user
        self.logger = logger

        self.main_layout = HorizontalLayout()
        self.setLayout(self.main_layout)
        self.side_bar_menu = SideBarMenu(
            self.logger,
            service,
            side_bar_signals=self.side_bar_signals,
            app_signals=self.app_signals,
            user=self.user,
        )
        self.main_layout.addWidget(self.side_bar_menu)
