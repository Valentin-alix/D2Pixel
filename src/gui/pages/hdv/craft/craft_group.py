from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.character import CharacterService
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class CraftGroupSignals(QObject):
    added_recipe_queue = pyqtSignal(object)


class CraftGroup(QGroupBox):
    def __init__(
        self, character: CharacterSchema, service: ServiceSession, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.character = character
        self.service = service
        self.signals = CraftGroupSignals()
        self.setTitle("Craft")
        self.setLayout(VerticalLayout())
        self.search_input_recipe: str = ""
        self.recipe_widget_by_name: dict[str, QListWidgetItem] = {}
        self.recipes: list[RecipeSchema] = []
        self.setup_list_recipe(self.get_not_in_queue_available_recipes())

    def get_not_in_queue_available_recipes(self) -> list[RecipeSchema]:
        recipes = RecipeService.get_available_recipes(self.service, self.character.id)
        return [_elem for _elem in recipes if _elem not in self.character.recipes]

    def setup_list_recipe(self, recipes: list[RecipeSchema]) -> None:
        self.list_wid_recipe = QListWidget()
        for recipe in recipes:
            self.add_recipe(recipe)
        self.list_wid_recipe.itemClicked.connect(self._on_click_recipe_widget)
        self.layout().addWidget(self.list_wid_recipe)

        bottom_widget = QWidget()
        bottom_widget.setLayout(HorizontalLayout())

        self.search_recipe_edit = QLineEdit()
        self.search_recipe_edit.textChanged.connect(self._on_search_recipes)
        bottom_widget.layout().addWidget(self.search_recipe_edit)
        refresh_btn = PushButtonIcon("restart.svg")
        refresh_btn.setCheckable(False)
        refresh_btn.clicked.connect(self._on_refresh_recipes)
        bottom_widget.layout().addWidget(refresh_btn)

        self.layout().addWidget(bottom_widget)

    def add_recipe(self, recipe: RecipeSchema):
        self.recipes.append(recipe)
        recipe_wid_item = QListWidgetItem(recipe.result_item.name)
        recipe_wid_item.setData(Qt.UserRole, recipe.id)
        self.recipe_widget_by_name[recipe.result_item.name] = recipe_wid_item
        self.list_wid_recipe.addItem(recipe_wid_item)

    def remove_recipe(self, recipe: RecipeSchema):
        self.recipes.remove(recipe)
        related_item = self.recipe_widget_by_name.pop(recipe.result_item.name)
        row_index = self.list_wid_recipe.row(related_item)
        self.list_wid_recipe.takeItem(row_index)

    def filter_recipes(self, search_input_recipe: str):
        for recipe in self.recipes:
            related_item = self.recipe_widget_by_name[recipe.result_item.name]
            if (
                search_input_recipe == ""
                or search_input_recipe.casefold() in related_item.text().casefold()
            ):
                related_item.setHidden(False)
            else:
                related_item.setHidden(True)

    def _on_click_recipe_widget(self, recipe_widget: QListWidgetItem):
        recipe_id = recipe_widget.data(Qt.UserRole)
        related_recipe: RecipeSchema = next(
            _elem for _elem in self.recipes if _elem.id == recipe_id
        )
        if related_recipe not in self.character.recipes:
            self.character.recipes.append(related_recipe)
            CharacterService.update_recipes(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.recipes],
            )
        self.remove_recipe(related_recipe)
        self.signals.added_recipe_queue.emit(related_recipe)

    @pyqtSlot()
    def _on_refresh_recipes(self) -> None:
        recipes = self.get_not_in_queue_available_recipes()
        untreated_recipe: dict[str, RecipeSchema] = {
            _recipe.result_item.name: _recipe for _recipe in recipes
        }
        for curr_recipe_name in self.recipe_widget_by_name.keys():
            related_untread_recipe = untreated_recipe.pop(curr_recipe_name, None)
            if not related_untread_recipe:
                related_curr_recipe = next(
                    _elem
                    for _elem in self.recipes
                    if _elem.result_item.name == curr_recipe_name
                )
                self.remove_recipe(related_curr_recipe)
                continue

        for recipe in untreated_recipe.values():
            self.add_recipe(recipe)

        self.filter_recipes(self.search_input_recipe)

    @pyqtSlot(str)
    def _on_search_recipes(self, recipe_name: str) -> None:
        self.search_input_recipe = recipe_name
        self.filter_recipes(self.search_input_recipe)
