import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication


sys.path.append(os.path.join(Path(__file__).parent.parent.parent))
from D2Shared.shared.schemas.item import ItemSchema, SellItemInfo
from src.gui.pages.sell.sell_info_table import SellInfoTable
from D2Shared.shared.enums import CategoryEnum, SaleHotelQuantity
from D2Shared.shared.schemas.type_item import TypeItemSchema


def show_sell_info_table(app: QApplication):
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
    app.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show_sell_info_table(app)
