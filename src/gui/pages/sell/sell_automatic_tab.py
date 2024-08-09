from logging import Logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.item import ItemSchema, SellItemInfo
from src.gui.components.organization import VerticalLayout
from src.gui.pages.sell.groups.sell_item_info_group import SellItemInfoGroup
from src.gui.pages.sell.groups.item_group import ItemGroup
from src.services.character import CharacterService
from src.services.item import ItemService
from src.services.session import ServiceSession


class SellAutomaticTab(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        character: CharacterSchema,
        logger: Logger,
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

        character_sell_items: list[ItemSchema] = [
            _sell_item_info.item for _sell_item_info in self.character.sell_items_infos
        ]
        self.sell_group = ItemGroup(
            list(set(character_sell_items) ^ set(ItemService.get_items(self.service)))
        )
        self.sell_info_group = SellItemInfoGroup(
            item_infos=self.character.sell_items_infos
        )

        self.sell_group.signals.clicked_elem_queue.connect(self.on_added_item_queue)
        self.sell_info_group.signals.clicked_elem_queue.connect(
            self.on_removed_item_queue
        )
        self.sell_info_group.sell_signals.changed_item_info.connect(
            self.on_changed_item_info
        )

        self.layout().addWidget(self.sell_info_group)
        self.layout().addWidget(self.sell_group)

    @pyqtSlot(object)
    def on_changed_item_info(self, sell_item_info: SellItemInfo):
        print(sell_item_info)
        related_sell_info = next(
            _elem
            for _elem in self.character.sell_items_infos
            if _elem == sell_item_info
        )
        related_sell_info.sale_hotel_quantities = sell_item_info.sale_hotel_quantities
        CharacterService.update_sell_items(
            self.service,
            self.character.id,
            self.character.sell_items_infos,
        )

    @pyqtSlot(object)
    def on_removed_item_queue(self, sell_item_info: SellItemInfo):
        if sell_item_info in self.character.sell_items_infos:
            self.character.sell_items_infos.remove(sell_item_info)
            CharacterService.update_sell_items(
                self.service,
                self.character.id,
                self.character.sell_items_infos,
            )
        self.sell_group.add_elem(sell_item_info.item)

    @pyqtSlot(object)
    def on_added_item_queue(self, item: ItemSchema):
        sell_item_info = SellItemInfo(
            item_id=item.id, item=item, sale_hotel_quantities=[]
        )
        if sell_item_info not in self.character.sell_items_infos:
            self.character.sell_items_infos.append(sell_item_info)
            CharacterService.update_sell_items(
                self.service,
                self.character.id,
                self.character.sell_items_infos,
            )
        self.sell_info_group.add_elem(sell_item_info)
