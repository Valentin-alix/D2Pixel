from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QWidget

from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.server import ServerSchema
from src.gui.components.organization import VerticalLayout
from src.services.client_service import ClientService
from src.services.server import ServerService
from src.services.type_item import TypeItemService


class BenefitCraftFilters(QWidget):
    class FilterSignals(QObject):
        changed_filters = pyqtSignal()

    def __init__(self, service: ClientService):
        super().__init__()
        self.service = service
        self.filter_signals = self.FilterSignals()

        self.main_layout = VerticalLayout()
        self.setLayout(self.main_layout)

        self.setup_filters_server_id()
        self.setup_filters_category()

        self.setup_filters_type()

    def setup_filters_server_id(self) -> None:
        self.servers: list[ServerSchema] = ServerService.get_servers(self.service)
        self.combo_servers = QComboBox(parent=self)
        for server in self.servers:
            self.combo_servers.addItem(server.name, server.id)
        self.combo_servers.currentIndexChanged.connect(self.on_select_server)
        self.main_layout.addWidget(self.combo_servers)

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

    @pyqtSlot()
    def on_select_server(self):
        self.emit_change()

    def on_select_category(self, index: int):
        category = self.categories[index][0]
        self.combo_type_item.clear()
        self.combo_type_item.addItem("")
        if category is not None:
            for type_item in sorted(
                TypeItemService.get_type_items(self.service, category),
                key=lambda elem: elem.name,
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
