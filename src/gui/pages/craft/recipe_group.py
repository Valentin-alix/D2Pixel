from typing import override

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.group_list import GroupList


class RecipeGroup(GroupList[RecipeSchema]):
    def __init__(self, recipes: list[RecipeSchema], *args, **kwargs) -> None:
        super().__init__(elems=recipes, *args, **kwargs)
        self.setTitle("Craft")

    @override
    def get_id_elem(self, elem: RecipeSchema) -> str | int:
        return elem.id

    @override
    def get_name_elem(self, elem: RecipeSchema) -> str:
        return elem.result_item.name
