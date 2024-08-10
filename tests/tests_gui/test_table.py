import os
import sys
import unittest
from logging import Logger
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from D2Shared.shared.enums import CategoryEnum, SaleHotelQuantity
from D2Shared.shared.schemas.type_item import TypeItemSchema


sys.path.append(os.path.join(Path(__file__).parent.parent.parent))
from D2Shared.shared.schemas.item import ItemSchema, SellItemInfo
from src.gui.pages.sell.sell_info_table import SellInfoTable
from src.gui.signals.app_signals import AppSignals
from src.services.character import CharacterService
from src.services.session import ServiceSession


class TestTable(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ServiceSession(Logger("Xeloreeuu"), AppSignals())
        self.character = CharacterService.get_or_create_character(
            self.service, "Tema-la-ratte"
        )
        self.app = QApplication(sys.argv)

        return super().setUp()

    def test_sell_info_table(self):
        item = ItemSchema(
            id=1,
            name="Poudre",
            type_item_id=1,
            type_item=TypeItemSchema(
                id=1, name="Ressource diverse", category=CategoryEnum.RESOURCES
            ),
            icon_id=1,
            is_saleable=True,
            level=1,
            weight=10,
        )
        widget = SellInfoTable(
            [
                SellItemInfo(
                    item_id=1,
                    item=item,
                    sale_hotel_quantities=[SaleHotelQuantity.HUNDRED],
                )
            ]
        )
        widget.show()
        self.app.exec()
