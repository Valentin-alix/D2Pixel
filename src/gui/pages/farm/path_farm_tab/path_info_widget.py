from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit, QScrollArea, QWidget

from D2Shared.shared.schemas.character_path_info import (
    BaseCharacterPathInfoSchema,
    CreateCharacterPathInfoSchema,
    UpdateCharacterPathInfoSchema,
)
from D2Shared.shared.schemas.character_path_map import (
    BaseCharacterPathMapSchema,
    ReadCharacterPathMapSchema,
)
from D2Shared.shared.schemas.map import CoordinatesMapSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import VerticalLayout
from src.gui.pages.farm.path_farm_tab.path_map_widget import PathMapWidget
from src.services.character_path_info import PathInfoService
from src.services.session import ServiceSession


class PathInfoWidgetSignals(QObject):
    deleted_path_info = pyqtSignal()


class PathInfoWidget(QWidget):
    def __init__(
        self,
        character_id: str,
        service: ServiceSession,
        path_info: BaseCharacterPathInfoSchema,
        path_maps: list[ReadCharacterPathMapSchema] | None = None,
        id: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.signals = PathInfoWidgetSignals()
        self.character_id: str = character_id
        self.service: ServiceSession = service
        self.id: int | None = id
        self.path_info: BaseCharacterPathInfoSchema = path_info
        self.last_order_index = 0

        self.setLayout(VerticalLayout())
        self.layout().setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.paths_maps_widget = QWidget()
        paths_maps_area = QScrollArea()
        paths_maps_area.setWidget(self.paths_maps_widget)
        paths_maps_area.setWidgetResizable(True)
        self.layout().addWidget(paths_maps_area)

        self.setup_content(path_maps)

    def setup_content(
        self,
        path_maps: list[ReadCharacterPathMapSchema] | None = None,
    ):
        self.path_info_edit = QLineEdit()
        self.path_info_edit.setText(self.path_info.name)
        timer = QTimer()
        timer.setSingleShot(True)
        self.path_info_edit.textChanged.connect(lambda: timer.start(1000))
        self.layout().addWidget(self.path_info_edit)

        timer.timeout.connect(self.on_edited_name)

        if self.id:
            self.add_path_map_add_btn(self.id)
            self.add_path_info_remove_btn(self.id)

        if path_maps:
            for path_map in sorted(path_maps, key=lambda elem: elem.order_index):
                self.add_path_map(path_map, path_map.map, path_map.id)

    def add_path_map_add_btn(self, id: int):
        add_path_map_btn = PushButtonIcon("add.svg")
        add_path_map_btn.clicked.connect(lambda: self.on_add_path_map(id))
        self.layout().addWidget(add_path_map_btn)

    def add_path_info_remove_btn(self, id: int):
        btn_delete_path_info = PushButtonIcon("delete.svg")
        btn_delete_path_info.clicked.connect(lambda: self.on_delete_path_info(id))
        self.layout().addWidget(btn_delete_path_info)

    def add_path_map(
        self,
        path_map: BaseCharacterPathMapSchema,
        map: CoordinatesMapSchema | None = None,
        path_map_id: int | None = None,
    ):
        path_map_widget = PathMapWidget(self.service, path_map, map, path_map_id)
        path_map_widget.signals.deleted_path_map.connect(
            lambda: self.on_delete_path_map(path_map_widget)
        )
        self.last_order_index = path_map.order_index
        self.paths_maps_widget.layout().addWidget(path_map_widget)

    @pyqtSlot()
    def on_delete_path_map(self, path_map_widget: PathMapWidget):
        path_map_widget.deleteLater()
        self.paths_maps_widget.layout().removeWidget(path_map_widget)

    @pyqtSlot()
    def on_delete_path_info(self, path_info_id: int):
        PathInfoService.delete_character_path_info(self.service, path_info_id)
        self.signals.deleted_path_info.emit()

    @pyqtSlot(int)
    def on_add_path_map(self, id: int):
        self.last_order_index += 1
        self.add_path_map(
            BaseCharacterPathMapSchema(
                order_index=self.last_order_index, character_path_info_id=id
            )
        )

    @pyqtSlot()
    def on_edited_name(self):
        name = self.path_info_edit.text()
        if self.id is None:
            path_info = PathInfoService.create_character_path_info(
                self.service,
                CreateCharacterPathInfoSchema(
                    name=name, character_id=self.character_id
                ),
            )
            self.id = path_info.id
            self.add_path_map_add_btn(self.id)
            self.add_path_info_remove_btn(self.id)
        else:
            path_info = PathInfoService.update_character_path_info(
                self.service, self.id, UpdateCharacterPathInfoSchema(name=name)
            )
        self.path_info = path_info
