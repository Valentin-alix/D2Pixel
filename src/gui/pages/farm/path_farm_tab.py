from D2Shared.shared.schemas.character import CharacterSchema
from src.gui.components.organization import VerticalLayout
from src.services.session import ServiceSession


from PyQt5.QtWidgets import QWidget


class PathFarmTab(QWidget):
    def __init__(
        self, service: ServiceSession, character: CharacterSchema, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setLayout(VerticalLayout())
        self.service = service
        self.character = character
