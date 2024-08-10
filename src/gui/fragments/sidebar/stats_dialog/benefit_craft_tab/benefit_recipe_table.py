from D2Shared.shared.enums import CategoryEnum
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QWidget

from src.gui.components.organization import VerticalLayout
from src.gui.components.table import BaseTableWidget, ColumnInfo
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class BenefitRecipeTable(QWidget):
    def __init__(self, service: ServiceSession):
        super().__init__()
        self.service = service
        v_layout = VerticalLayout(space=8)
        self.setLayout(v_layout)

        title = QLabel(parent=self, text="Meilleur bénéfice sur les crafts")
        v_layout.addWidget(title)

        columns: list[ColumnInfo] = [
            ColumnInfo(name="Nom"),
            ColumnInfo(name="Bénéfice"),
        ]

        table_benefit_recipe_scroll = BaseTableWidget()
        table_benefit_recipe_scroll.set_columns(columns)
        self.table_benefit_recipe = table_benefit_recipe_scroll.table
        v_layout.addWidget(table_benefit_recipe_scroll)

    def get_benefit_recipe(
        self,
        server_id: int,
        category: CategoryEnum | None = None,
        type_item_id: int | None = None,
    ):
        self.table_benefit_recipe.clearContents()
        self.table_benefit_recipe.setRowCount(0)

        rows = 100
        benefit_recipe = RecipeService.get_best_recipe_benefits(
            self.service, server_id, category, type_item_id, rows
        )
        self.table_benefit_recipe.setRowCount(len(benefit_recipe))
        for index, (name, benefit) in enumerate(benefit_recipe):
            name_col = QTableWidgetItem(name)
            benefit_col = QTableWidgetItem(str(benefit))

            self.table_benefit_recipe.setItem(index, 0, name_col)
            self.table_benefit_recipe.setItem(index, 1, benefit_col)
