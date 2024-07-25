from logging import Logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import VerticalLayout
from src.gui.pages.craft.recipe_group import RecipeGroup
from src.gui.pages.craft.recipe_table import RecipeTable
from src.services.character import CharacterService
from src.services.client_service import ClientService
from src.services.recipe import RecipeService


class AutomaticTab(QWidget):
    def __init__(
        self,
        service: ClientService,
        character: CharacterSchema,
        logger: Logger,
        available_recipes: list[RecipeSchema],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service = service
        self.character = character
        self.is_loading: bool = False
        self.logger = logger

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.craft_table = RecipeTable(self.character.recipes)
        self.craft_group = RecipeGroup(
            [
                _elem
                for _elem in available_recipes
                if _elem not in self.character.recipes
            ]
        )

        self.craft_group.signals.added_recipe_queue.connect(self.on_added_recipe_queue)
        self.craft_table.signals.removed_recipe.connect(self.on_removed_recipe_queue)

        refresh_btn = PushButtonIcon("restart.svg")
        refresh_btn.clicked.connect(self._on_refresh_recipes)
        self.layout().addWidget(refresh_btn)

        self.layout().addWidget(self.craft_table)
        self.layout().addWidget(self.craft_group)

    @pyqtSlot(object)
    def on_removed_recipe_queue(self, recipe: RecipeSchema):
        if recipe in self.character.recipes:
            self.character.recipes.remove(recipe)
            CharacterService.update_recipes(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.recipes],
            )
        self.craft_group.add_recipe(recipe)

    @pyqtSlot(object)
    def on_added_recipe_queue(self, recipe: RecipeSchema):
        if recipe not in self.character.recipes:
            self.character.recipes.append(recipe)
            CharacterService.update_recipes(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.recipes],
            )
        self.craft_table.add_recipe(recipe)

    @pyqtSlot()
    def _on_refresh_recipes(self) -> None:
        recipes = self.get_not_in_queue_available_recipes()
        self.craft_group._on_refresh_recipes(recipes)

    def get_not_in_queue_available_recipes(self) -> list[RecipeSchema]:
        recipes = RecipeService.get_available_recipes(self.service, self.character.id)
        return [_elem for _elem in recipes if _elem not in self.character.recipes]
