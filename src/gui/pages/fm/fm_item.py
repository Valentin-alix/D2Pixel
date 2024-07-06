from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QFormLayout, QLineEdit, QWidget

from D2Shared.shared.schemas.equipment import UpdateEquipmentSchema
from D2Shared.shared.schemas.stat import LineSchema, StatSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.equipment import EquipmentService
from src.services.session import ServiceSession
from src.services.stat import StatService


class FmItemSignals(QObject):
    saved_item = pyqtSignal()
    deleted_item = pyqtSignal()


class FmItem(QWidget):
    def __init__(
        self,
        service: ServiceSession,
        label: str,
        lines: list[LineSchema],
        equipment_id: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.signals = FmItemSignals()
        self.service = service
        self.equipment_id = equipment_id
        v_layout = VerticalLayout()
        v_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(v_layout)

        item = QWidget()
        f_layout = QFormLayout()
        item.setLayout(f_layout)
        v_layout.addWidget(item)

        self.label_edit = QLineEdit()
        self.label_edit.setText(label)
        f_layout.addRow("Label", self.label_edit)

        self.exo_combo = QComboBox()
        self.exo_combo.addItem("", None)
        for stat in StatService.get_stats(self.service):
            self.exo_combo.addItem(stat.name, stat)
        f_layout.addRow("Exo", self.exo_combo)

        self.lines_edit: list[tuple[QLineEdit, LineSchema]] = []
        for line in lines:
            line_edit = QLineEdit()
            line_edit.setText(str(line.value))
            self.lines_edit.append((line_edit, line))
            f_layout.addRow(line.stat.name, line_edit)

        action_buttons = QWidget()
        v_layout.addWidget(action_buttons)
        action_buttons_layout = HorizontalLayout()
        action_buttons.setLayout(action_buttons_layout)

        self.button_save = PushButtonIcon(
            "save.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_save.setCheckable(False)
        self.button_save.clicked.connect(self.on_save)
        action_buttons_layout.addWidget(self.button_save)

        if self.equipment_id is not None:
            self.button_delete = PushButtonIcon(
                "delete.svg", width=80, height=40, icon_size=20, parent=self
            )
            self.button_delete.setCheckable(False)
            self.button_delete.clicked.connect(self.on_delete)
            action_buttons_layout.addWidget(self.button_delete)

    def on_delete(self):
        assert self.equipment_id is not None
        EquipmentService.delete_equipment(self.service, self.equipment_id)
        self.signals.deleted_item.emit()

    def on_save(self):
        updated_equipment = UpdateEquipmentSchema(
            label=self.get_edited_label(), lines=self.get_edited_lines()
        )
        if self.equipment_id is not None:
            EquipmentService.update_equipment(
                self.service, self.equipment_id, updated_equipment
            )
        else:
            EquipmentService.create_equipment(self.service, updated_equipment)
        self.signals.saved_item.emit()

    def get_exo(self) -> StatSchema | None:
        return self.exo_combo.currentData()

    def get_edited_label(self) -> str:
        return self.label_edit.text()

    def get_edited_lines(self) -> list[LineSchema]:
        edited_lines: list[LineSchema] = []
        for line_edit, line_schema in self.lines_edit:
            line_schema.value = int(line_edit.text())
            edited_lines.append(line_schema)
        return edited_lines
