from PyQt5.QtWidgets import QWidget

from src.gui.components.organization import VerticalLayout
from src.gui.pages.stats.benefit_craft_tab.benefit_craft_filters import (
    BenefitCraftFilters,
)
from src.gui.pages.stats.benefit_craft_tab.benefit_recipe_table import (
    BenefitRecipeTable,
)


class BenefitCraftTab(QWidget):
    def __init__(self, server_id: int):
        super().__init__()
        self.server_id = server_id
        v_layout = VerticalLayout(space=4)
        self.setLayout(v_layout)

        self.benefit_recipe_filters = BenefitCraftFilters()
        v_layout.addWidget(self.benefit_recipe_filters)

        self.benefit_recipe_table = BenefitRecipeTable()
        v_layout.addWidget(self.benefit_recipe_table)

        self.benefit_recipe_filters.filter_signals.changed_filters.connect(
            self.on_changed_filters
        )

        self.benefit_recipe_filters.emit_change()

    def on_changed_filters(self):
        category = self.benefit_recipe_filters.combo_category.currentData()
        type_item = self.benefit_recipe_filters.combo_type_item.currentData()
        self.benefit_recipe_table.get_benefit_recipe(
            self.server_id, category, type_item
        )
