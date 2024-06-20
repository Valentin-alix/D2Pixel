from PyQt5.QtWidgets import QTabWidget, QWidget

from src.bots.modules.module_manager import ModuleManager
from src.gui.components.organization import VerticalLayout
from src.gui.pages.stats.benefit_craft_tab.benefit_craft_tab import (
    BenefitCraftTab,
)


class StatsPage(QWidget):
    def __init__(
        self,
        module_manager: ModuleManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.module_manager = module_manager

        self.v_layout = VerticalLayout()
        self.setLayout(self.v_layout)

        self.tabs = QTabWidget()
        self.scrapping_craft_tab = BenefitCraftTab(
            server_id=self.module_manager.character.server_id
        )
        self.tabs.addTab(self.scrapping_craft_tab, "Craft")
        self.v_layout.addWidget(self.tabs)
