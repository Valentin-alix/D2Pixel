from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.table import TableWidget
from src.services.character import CharacterService
from src.services.session import ServiceSession


class CraftTableSignals(QObject):
    removed_recipe = pyqtSignal(object)


class CraftTable(TableWidget):
    def __init__(
        self, character: CharacterSchema, service: ServiceSession, *args, **kwargs
    ) -> None:
        column_names: list[str] = ["Nom", "Métier", "LVL", ""]
        super().__init__(column_names, *args, **kwargs)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.service = service
        self.character = character

        self.signals = CraftTableSignals()
        self.widget_item_by_recipe_id: dict[int, QTableWidgetItem] = {}
        self.setup_recipes()

    def setup_recipes(self):
        for recipe in self.character.recipes:
            self.add_recipe(recipe)

    def add_recipe(self, recipe: RecipeSchema) -> None:
        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)

        recipe_widget_item = QTableWidgetItem(recipe.result_item.name)
        self.widget_item_by_recipe_id[recipe.id] = recipe_widget_item

        self.table.setItem(table_index, 0, recipe_widget_item)
        self.table.setItem(table_index, 1, QTableWidgetItem(recipe.job.name))
        self.table.setItem(
            table_index, 2, QTableWidgetItem(str(recipe.result_item.level))
        )

        delete_btn = PushButtonIcon("delete.svg")
        delete_btn.setCheckable(False)
        delete_btn.clicked.connect(lambda: self.remove_recipe(recipe))
        self.table.setCellWidget(table_index, 3, delete_btn)

    def remove_recipe(self, recipe: RecipeSchema) -> None:
        if recipe in self.character.recipes:
            self.character.recipes.remove(recipe)
            CharacterService.update_recipes(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.recipes],
            )
        related_widget_item = self.widget_item_by_recipe_id.pop(recipe.id)
        related_table_index = self.table.row(related_widget_item)
        self.table.removeRow(related_table_index)
        self.signals.removed_recipe.emit(recipe)
