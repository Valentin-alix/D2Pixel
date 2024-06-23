from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.module_manager import ModuleManager
from src.gui.components.organization import HorizontalLayout
from src.gui.pages.modules.module_page import ModulesPage
from src.gui.pages.stats.stats_page import StatsPage
from src.services.session import ServiceSession


class SubHeader(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        module_manager: ModuleManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service = service
        self.main_layout = HorizontalLayout()
        self.setLayout(self.main_layout)

        self.setup_tabs(module_manager)

    def setup_tabs(self, module_manager: ModuleManager):
        self.tabs = QTabWidget()
        self.module_tab = ModulesPage(module_manager=module_manager)
        self.tabs.addTab(self.module_tab, "Modules")

        self.stats_frame = StatsPage(self.service, module_manager=module_manager)
        self.tabs.addTab(self.stats_frame, "Stats")
        self.main_layout.addWidget(self.tabs)
