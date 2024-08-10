from typing import override

from PyQt5.QtWidgets import QLabel, QWidget
from D2Shared.shared.schemas.item import ItemSchema
from src.gui.components.group_list import GroupList


class ItemGroup(GroupList[ItemSchema]):
    def __init__(self, items: list[ItemSchema], *args, **kwargs) -> None:
        super().__init__(elems=items, is_lazy_loaded=True, *args, **kwargs)

    @override
    def get_name_elem(self, elem: ItemSchema) -> str:
        return elem.name

    @override
    def get_widget_elem(self, elem: ItemSchema) -> QWidget:
        label = QLabel(self.get_name_elem(elem))
        label.setStyleSheet("""qproperty-alignment: AlignLeft;""")
        return label
