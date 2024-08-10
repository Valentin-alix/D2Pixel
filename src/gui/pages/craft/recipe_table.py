from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.table import TableWidget


class RecipeTableSignals(QObject):
    removed_recipe = pyqtSignal(object)


class RecipeTable(TableWidget):
    def __init__(self, recipes: list[RecipeSchema], *args, **kwargs) -> None:
        column_names: list[str] = ["Nom", "Métier", "LVL", ""]
        super().__init__(column_names, *args, **kwargs)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.signals = RecipeTableSignals()
        self.widget_item_by_recipe: dict[RecipeSchema, QTableWidgetItem] = {}
        for recipe in recipes:
            self.add_recipe(recipe)

    def add_recipe(self, recipe: RecipeSchema) -> None:
        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)

        recipe_widget_item = QTableWidgetItem(recipe.result_item.name)
        self.widget_item_by_recipe[recipe] = recipe_widget_item

        self.table.setItem(table_index, 0, recipe_widget_item)
        self.table.setItem(table_index, 1, QTableWidgetItem(recipe.job.name))
        self.table.setItem(
            table_index, 2, QTableWidgetItem(str(recipe.result_item.level))
        )

        delete_btn = PushButtonIcon("delete.svg")
        delete_btn.clicked.connect(lambda: self.remove_recipe(recipe))
        self.table.setCellWidget(table_index, 3, delete_btn)

    def remove_recipe(self, recipe: RecipeSchema) -> None:
        self.signals.removed_recipe.emit(recipe)
        related_widget_item = self.widget_item_by_recipe.pop(recipe)
        related_table_index = self.table.row(related_widget_item)
        self.table.removeRow(related_table_index)
