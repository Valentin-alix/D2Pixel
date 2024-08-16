from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from D2Shared.shared.schemas.character_path_map import (
    BaseCharacterPathMapSchema,
    CreateUpdateCharacterPathMapSchema,
)
from D2Shared.shared.schemas.map import CoordinatesMapSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import HorizontalLayout


from PyQt5.QtWidgets import QLineEdit, QWidget

from src.services.character_path_map import PathMapService
from src.services.session import ServiceSession


class PathMapWidgetSignals(QObject):
    deleted_path_map = pyqtSignal()


class PathMapWidget(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        path_map: BaseCharacterPathMapSchema,
        map: CoordinatesMapSchema | None = None,
        id: int | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service = service
        self.signals = PathMapWidgetSignals()
        self.path_map: BaseCharacterPathMapSchema = path_map
        self.id: int | None = id
        self.map = map

        self.setLayout(HorizontalLayout())

        self.setup_content()

    def setup_content(self):
        self.x_edit = QLineEdit()
        self.layout().addWidget(self.x_edit)

        self.y_edit = QLineEdit()
        self.layout().addWidget(self.y_edit)

        if self.map:
            self.x_edit.setText(str(self.map.x))
            self.y_edit.setText(str(self.map.y))

        self.add_remove_btn()

        x_timer = QTimer()
        x_timer.setSingleShot(True)
        self.x_edit.textChanged.connect(lambda: x_timer.start(1000))
        x_timer.timeout.connect(self.on_edited_path_map)

        y_timer = QTimer()
        y_timer.setSingleShot(True)
        self.y_edit.textChanged.connect(lambda: y_timer.start(1000))
        y_timer.timeout.connect(self.on_edited_path_map)

    def add_remove_btn(self):
        remove_btn_widget = PushButtonIcon("delete.svg")
        remove_btn_widget.clicked.connect(self.on_clicked_remove_btn)
        self.layout().addWidget(remove_btn_widget)

    def on_clicked_remove_btn(self):
        if self.id:
            PathMapService.delete_character_path_map(self.service, self.id)
        self.signals.deleted_path_map.emit()

    @pyqtSlot()
    def on_edited_path_map(self):
        try:
            path_map_datas = CreateUpdateCharacterPathMapSchema(
                order_index=self.path_map.order_index,
                character_path_info_id=self.path_map.character_path_info_id,
                map=CoordinatesMapSchema(
                    x=int(self.x_edit.text()), y=int(self.y_edit.text())
                ),
            )
        except ValueError:
            return
        try:
            if self.id is None:
                path_map = PathMapService.create_path_map(self.service, path_map_datas)
                self.path_map = path_map
                self.id = path_map.id
            else:
                self.path_map = PathMapService.update_character_path_map(
                    self.service, self.id, path_map_datas
                )
        except Exception:
            return
