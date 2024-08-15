from PyQt5.QtCore import pyqtSlot
from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.character_path_info import BaseCharacterPathInfoSchema
from D2Shared.shared.schemas.character_path_map import ReadCharacterPathMapSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import HorizontalLayout
from src.gui.pages.farm.path_farm_tab.path_info_widget import PathInfoWidget
from src.services.session import ServiceSession


from PyQt5.QtWidgets import QScrollArea


class PathFarmTab(QScrollArea):
    def __init__(
        self, service: ServiceSession, character: CharacterSchema, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.setLayout(HorizontalLayout())
        self.service = service
        self.character = character

        add_path_info_btn = PushButtonIcon("add.svg")
        add_path_info_btn.clicked.connect(self.on_add_path_info)
        self.layout().addWidget(add_path_info_btn)

        for path_info in self.character.paths_infos:
            self.add_path_info(path_info, path_info.path_maps, path_info.id)

    def add_path_info(
        self,
        path_info: BaseCharacterPathInfoSchema,
        path_maps: list[ReadCharacterPathMapSchema] | None = None,
        path_info_id: int | None = None,
    ):
        path_info_widget = PathInfoWidget(
            self.character.id, self.service, path_info, path_maps, path_info_id
        )
        path_info_widget.signals.deleted_path_info.connect(
            lambda: self.on_remove_path_info(path_info_widget)
        )
        self.layout().addWidget(path_info_widget)

    @pyqtSlot(object)
    def on_remove_path_info(self, path_info_widget: PathInfoWidget):
        path_info_widget.deleteLater()
        self.layout().removeWidget(path_info_widget)

    @pyqtSlot()
    def on_add_path_info(self):
        self.add_path_info(BaseCharacterPathInfoSchema(name=""))
