from typing import override

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLabel, QWidget
from D2Shared.shared.enums import SaleHotelQuantity
from D2Shared.shared.schemas.item import SellItemInfo
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.group_list import GroupList
from src.gui.components.organization import HorizontalLayout


class SellItemInfoGroupSignals(QObject):
    changed_item_info = pyqtSignal(object)
    removed_item = pyqtSignal(object)


class SellItemInfoGroup(GroupList[SellItemInfo]):
    def __init__(self, item_infos: list[SellItemInfo], *args, **kwargs) -> None:
        self.sell_signals = SellItemInfoGroupSignals()
        super().__init__(elems=item_infos, *args, **kwargs)

    @override
    def get_name_elem(self, elem: SellItemInfo) -> str:
        return elem.item.name

    @override
    def get_widget_elem(self, elem: SellItemInfo) -> QWidget:
        widget = QWidget()
        widget.setLayout(HorizontalLayout())
        widget.layout().addWidget(QLabel(self.get_name_elem(elem)))

        combo_quantities = CheckableComboBox[SaleHotelQuantity](parent=widget)
        for quantity in SaleHotelQuantity:
            combo_quantities.addItem(
                text=str(quantity),
                data=quantity,
                checked=quantity in elem.sale_hotel_quantities,
            )

        combo_quantities.signals.clicked_item.connect(
            lambda: self.on_new_sell_quantities(combo_quantities, elem)
        )
        widget.layout().addWidget(combo_quantities)

        delete_btn = PushButtonIcon("delete.svg")
        delete_btn.clicked.connect(lambda: self.on_clicked_delete_item(elem))
        widget.layout().addWidget(delete_btn)

        return widget

    @pyqtSlot()
    def on_clicked_delete_item(self, elem: SellItemInfo):
        self.remove_elem(elem)
        self.sell_signals.removed_item.emit(elem)

    @pyqtSlot(object)
    def on_new_sell_quantities(
        self,
        combo_quantities: CheckableComboBox[SaleHotelQuantity],
        item_info: SellItemInfo,
    ):
        item_info.sale_hotel_quantities = combo_quantities.currentData()
        self.sell_signals.changed_item_info.emit(item_info)
