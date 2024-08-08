from typing import override
from D2Shared.shared.schemas.item import ItemSchema
from src.gui.components.group_list import GroupList


class SellGroup(GroupList[ItemSchema]):
    def __init__(self, items: list[ItemSchema], *args, **kwargs) -> None:
        super().__init__(elems=items, *args, **kwargs)

    @override
    def get_id_elem(self, elem: ItemSchema) -> str | int:
        return elem.id

    @override
    def get_name_elem(self, elem: ItemSchema) -> str:
        return elem.name
