from logging import Logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.item import ItemSchema
from src.gui.components.organization import VerticalLayout
from src.gui.pages.sell.sell_group import SellGroup
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

        self.sell_group = SellGroup(
            [
                _elem
                for _elem in ItemService.get_items(self.service)
                if _elem not in self.character.sell_items
            ]
        )
        self.char_sell_group = SellGroup(items=self.character.sell_items)

        self.sell_group.signals.clicked_elem_queue.connect(self.on_added_item_queue)
        self.char_sell_group.signals.clicked_elem_queue.connect(
            self.on_removed_item_queue
        )

        self.layout().addWidget(self.char_sell_group)
        self.layout().addWidget(self.sell_group)

    @pyqtSlot(object)
    def on_removed_item_queue(self, item: ItemSchema):
        if item in self.character.sell_items:
            self.character.sell_items.remove(item)
            CharacterService.update_sell_items(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.sell_items],
            )
        self.sell_group.add_elem(item)

    @pyqtSlot(object)
    def on_added_item_queue(self, item: ItemSchema):
        if item not in self.character.sell_items:
            self.character.sell_items.append(item)
            CharacterService.update_sell_items(
                self.service,
                self.character.id,
                [_elem.id for _elem in self.character.sell_items],
            )
        self.char_sell_group.add_elem(item)
