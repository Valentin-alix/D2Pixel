from PyQt5.QtWidgets import QWidget

from src.gui.components.organization import VerticalLayout
from src.gui.fragments.sidebar.stats_dialog.benefit_craft_tab.benefit_craft_filters import (
    BenefitCraftFilters,
)
from src.gui.fragments.sidebar.stats_dialog.benefit_craft_tab.benefit_recipe_table import (
    BenefitRecipeTable,
)
from src.services.session import ServiceSession


class BenefitCraftTab(QWidget):
    def __init__(self, service: ServiceSession, server_id: int):
        super().__init__()
        self.server_id = server_id
        self.service = service
        v_layout = VerticalLayout(space=4)
        self.setLayout(v_layout)

        self.benefit_recipe_filters = BenefitCraftFilters(self.service)
        v_layout.addWidget(self.benefit_recipe_filters)

        self.benefit_recipe_table = BenefitRecipeTable(self.service)
        v_layout.addWidget(self.benefit_recipe_table)

        self.benefit_recipe_filters.filter_signals.changed_filters.connect(
            self.on_changed_filters
        )

        self.benefit_recipe_filters.emit_change()

    def on_changed_filters(self):
        self.server_id = self.benefit_recipe_filters.combo_servers.currentData()
        category = self.benefit_recipe_filters.combo_category.currentData()
        type_item = self.benefit_recipe_filters.combo_type_item.currentData()
        self.benefit_recipe_table.get_benefit_recipe(
            self.server_id, category, type_item
        )
