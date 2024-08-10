from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTableWidgetItem

from D2Shared.shared.enums import SaleHotelQuantity
from D2Shared.shared.schemas.item import SellItemInfo
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.table import TableWidget


class SellInfoTableSignals(QObject):
    removed_item_info = pyqtSignal(object)
    changed_item_info = pyqtSignal(object)


class SellInfoTable(TableWidget):
    def __init__(self, sell_items_infos: list[SellItemInfo], *args, **kwargs) -> None:
        column_names: list[str] = ["Nom", "Type", "Lvl", ""]
        super().__init__(column_names, *args, **kwargs)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.signals = SellInfoTableSignals()
        self.widget_item_by_item_info: dict[SellItemInfo, QTableWidgetItem] = {}
        for sell_item_info in sell_items_infos:
            self.add_item_info(sell_item_info)

    def add_item_info(self, sell_item_info: SellItemInfo) -> None:
        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)

        sell_info_widget_item = QTableWidgetItem(sell_item_info.item.name)
        self.widget_item_by_item_info[sell_item_info] = sell_info_widget_item

        self.table.setItem(table_index, 0, sell_info_widget_item)
        self.table.setItem(
            table_index, 1, QTableWidgetItem(sell_item_info.item.type_item.name)
        )
        self.table.setItem(
            table_index, 2, QTableWidgetItem(str(sell_item_info.item.level))
        )

        combo_quantities = CheckableComboBox[SaleHotelQuantity]()
        for quantity in SaleHotelQuantity:
            combo_quantities.addItem(
                text=str(quantity),
                data=quantity,
                checked=quantity in sell_item_info.sale_hotel_quantities,
            )
        combo_quantities.signals.clicked_item.connect(
            lambda: self.on_new_sell_quantities(combo_quantities, sell_item_info)
        )
        self.table.setCellWidget(table_index, 3, combo_quantities)

        delete_btn = PushButtonIcon("delete.svg")
        delete_btn.clicked.connect(lambda: self.remove_item_info(sell_item_info))
        self.table.setCellWidget(table_index, 4, delete_btn)

    def remove_item_info(self, item_info: SellItemInfo) -> None:
        related_widget_item = self.widget_item_by_item_info.pop(item_info)
        related_table_index = self.table.row(related_widget_item)
        self.table.removeRow(related_table_index)
        self.signals.removed_item_info.emit(item_info)

    @pyqtSlot(object)
    def on_new_sell_quantities(
        self,
        combo_quantities: CheckableComboBox[SaleHotelQuantity],
        item_info: SellItemInfo,
    ):
        item_info.sale_hotel_quantities = combo_quantities.currentData()
        self.signals.changed_item_info.emit(item_info)
