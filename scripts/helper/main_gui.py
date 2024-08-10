import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet


sys.path.append(os.path.join(Path(__file__).parent.parent.parent))
from D2Shared.shared.schemas.item import ItemSchema, SellItemInfo
from src.gui.pages.sell.sell_info_table import SellInfoTable
from D2Shared.shared.enums import CategoryEnum, SaleHotelQuantity
from D2Shared.shared.schemas.type_item import TypeItemSchema
from src.gui.pages.sell.item_group import ItemGroup
from src.consts import RESOURCE_FOLDER_PATH


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


def show_group(app: QApplication):
    widget = ItemGroup(
        [
            ItemSchema(
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
        ]
    )
    widget.show()
    app.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(
        app,
        theme="dark_yellow.xml",
        css_file=os.path.join(RESOURCE_FOLDER_PATH, "styles.qss"),
        invert_secondary=False,
    )
    show_group(app)
