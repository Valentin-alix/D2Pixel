from typing import override

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.gui.components.group_list import GroupList


class RecipeGroup(GroupList[RecipeSchema]):
    def __init__(self, recipes: list[RecipeSchema], *args, **kwargs) -> None:
        super().__init__(elems=recipes, is_lazy_loaded=True, *args, **kwargs)
        self.setTitle("Craft")

    @override
    def get_name_elem(self, elem: RecipeSchema) -> str:
        return elem.result_item.name

    @override
    def get_widget_elem(self, elem: RecipeSchema) -> QWidget:
        label = QLabel(self.get_name_elem(elem))
        label.setAlignment(Qt.AlignLeft)
        return label
