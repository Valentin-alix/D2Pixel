from logging import Logger

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from src.gui.components.organization import VerticalLayout
from src.gui.pages.hdv.craft.craft_group import CraftGroup
from src.gui.pages.hdv.craft.craft_table import CraftTable
from src.services.session import ServiceSession


class HdvPage(QWidget):
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

        self.craft_table = CraftTable(self.character, self.service)
        self.craft_group = CraftGroup(self.character, self.service)

        self.craft_group.signals.added_recipe_queue.connect(self.craft_table.add_recipe)
        self.craft_table.signals.removed_recipe.connect(self.craft_group.add_recipe)

        self.layout().addWidget(self.craft_table)
        self.layout().addWidget(self.craft_group)
