from EzreD2Shared.shared.enums import CategoryEnum
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QWidget

from src.gui.components.organization import VerticalLayout
from src.services.type_item import TypeItemService


class BenefitCraftFilters(QWidget):
    class FilterSignals(QObject):
        changed_filters = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.filter_signals = self.FilterSignals()

        self.main_layout = VerticalLayout()
        self.setLayout(self.main_layout)

        self.setup_filters_category()

        self.setup_filters_type()

    def setup_filters_category(self) -> None:
        self.categories: list[tuple[CategoryEnum | None, str]] = [
            (None, ""),
            (CategoryEnum.CONSUMABLES, "Consommables"),
            (CategoryEnum.EQUIPMENT, "Equipements"),
            (CategoryEnum.RESOURCES, "Ressources"),
        ]
        self.combo_category = QComboBox(parent=self)
        for category, name in self.categories:
            self.combo_category.addItem(name, category)
        self.combo_category.currentIndexChanged.connect(self.on_select_category)
        self.main_layout.addWidget(self.combo_category)

    def on_select_category(self, index: int):
        category = self.categories[index][0]
        self.combo_type_item.clear()
        self.combo_type_item.addItem("")
        if category is not None:
            for type_item in sorted(
                TypeItemService.get_type_items(category), key=lambda elem: elem.name
            ):
                self.combo_type_item.addItem(type_item.name, type_item.id)
        self.emit_change()

    def setup_filters_type(self):
        self.combo_type_item = QComboBox(parent=self)
        self.main_layout.addWidget(self.combo_type_item)
        self.combo_type_item.currentTextChanged.connect(self.emit_change)

    def emit_change(self):
        """for refresh"""
        self.filter_signals.changed_filters.emit()
