from PyQt5.QtWidgets import QTabWidget

from src.gui.components.dialog import Dialog
from src.gui.components.organization import VerticalLayout
from src.gui.fragments.sidebar.stats_dialog.benefit_craft_tab.benefit_craft_tab import (
    BenefitCraftTab,
)
from src.services.client_service import ClientService


class StatsDialog(Dialog):
    def __init__(
        self,
        service: ClientService,
        server_id: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.resize(800, 600)
        self.service = service
        self.server_id = server_id

        self.v_layout = VerticalLayout()
        self.setLayout(self.v_layout)

        self.tabs = QTabWidget()
        self.scrapping_craft_tab = BenefitCraftTab(
            self.service,
            server_id=self.server_id,
        )
        self.tabs.addTab(self.scrapping_craft_tab, "Craft")
        self.v_layout.addWidget(self.tabs)
