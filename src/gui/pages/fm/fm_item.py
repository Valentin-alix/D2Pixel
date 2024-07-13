import traceback
from logging import Logger
from typing import TypeVar

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QFormLayout, QLabel, QLineEdit, QWidget

from D2Shared.shared.enums import ExoStatEnum
from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, StatSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import (
    AlignDelegate,
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.components.table import TableWidget
from src.services.equipment import EquipmentService
from src.services.session import ServiceSession
from src.services.stat import StatService


class FmItemSignals(QObject):
    saved_item = pyqtSignal()
    deleted_item = pyqtSignal()


T = TypeVar("T", bound=BaseLineSchema)


class FmItem(QWidget):
    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        lines: list[T],
        equipment: ReadEquipmentSchema | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.signals = FmItemSignals()
        self.service = service
        self.equipment = equipment
        self.lines = lines
        self.lines_edit: list[tuple[QLineEdit, BaseLineSchema]] = []
        self.item_table: TableWidget | None = None

        self.main_layout = VerticalLayout()
        self.setLayout(self.main_layout)

        self.set_item_content()
        self.set_action_buttons()

    def set_item_content(self):
        self.label_equip_widget = QWidget()
        self.label_equip_layout = QFormLayout()
        self.label_equip_widget.setLayout(self.label_equip_layout)
        self.label_edit = QLineEdit()
        if self.equipment:
            self.label_edit.setText(self.equipment.label)
        self.label_equip_layout.addRow("Label", self.label_edit)
        self.main_layout.addWidget(self.label_equip_widget)

        if self.equipment:
            self.set_item_from_equipment(self.equipment)
        else:
            self.set_item_from_lines(self.lines)

    def set_item_from_equipment(self, equipment: ReadEquipmentSchema):
        if self.item_table:
            self.main_layout.removeWidget(self.item_table)
            self.item_table.deleteLater()

        print(equipment)
        columns = ["Stat", "Valeur", "Tentative"]

        self.item_table = TableWidget(columns)
        self.main_layout.addWidget(self.item_table)

        self.lines_edit.clear()
        for line in equipment.lines:
            table_index = self.item_table.table.rowCount()
            self.item_table.table.setRowCount(table_index + 1)

            line_label = QLabel()
            line_label.setText(line.stat.name)
            self.item_table.table.setCellWidget(table_index, 0, line_label)

            line_edit = QLineEdit()
            line_edit.setText(str(line.value))
            self.lines_edit.append((line_edit, line))
            self.item_table.table.setCellWidget(table_index, 1, line_edit)

            line_spent = QLabel()
            line_spent.setText(str(line.spent_quantity))
            self.item_table.table.setCellWidget(table_index, 2, line_spent)

        table_index = self.item_table.table.rowCount()
        self.item_table.table.setRowCount(table_index + 1)
        self.exo_combo = QComboBox()
        delegate = AlignDelegate(self.exo_combo)
        self.exo_combo.setItemDelegate(delegate)
        self.exo_combo.addItem("", None)
        for stat in StatService.get_stats(self.service):
            if stat.name not in ExoStatEnum:
                continue
            self.exo_combo.addItem(stat.name, stat)

        if equipment.exo_line:
            exo_index = self.exo_combo.findData(equipment.exo_line.stat)
            self.exo_combo.setCurrentIndex(exo_index)

        self.item_table.table.setCellWidget(table_index, 0, self.exo_combo)

        self.exo_attempt_label = QLabel()
        if equipment.exo_line:
            self.exo_attempt_label.setText(str(equipment.exo_line.spent_quantity))
        self.item_table.table.setCellWidget(table_index, 2, self.exo_attempt_label)

    def set_item_from_lines(self, lines: list[T]):
        if self.item_table:
            self.main_layout.removeWidget(self.item_table)
            self.item_table.deleteLater()

        columns = ["Stat", "Valeur"]

        self.item_table = TableWidget(columns)
        self.main_layout.addWidget(self.item_table)

        self.lines_edit.clear()
        for line in lines:
            table_index = self.item_table.table.rowCount()
            self.item_table.table.setRowCount(table_index + 1)

            line_label = QLabel()
            line_label.setText(line.stat.name)
            self.item_table.table.setCellWidget(table_index, 0, line_label)

            line_edit = QLineEdit()
            line_edit.setText(str(line.value))
            self.lines_edit.append((line_edit, line))
            self.item_table.table.setCellWidget(table_index, 1, line_edit)

        table_index = self.item_table.table.rowCount()
        self.item_table.table.setRowCount(table_index + 1)

        self.exo_combo = QComboBox()
        delegate = AlignDelegate(self.exo_combo)
        self.exo_combo.setItemDelegate(delegate)
        self.exo_combo.addItem("", None)
        for stat in StatService.get_stats(self.service):
            if stat.name not in ExoStatEnum:
                continue
            self.exo_combo.addItem(stat.name, stat)
        self.item_table.table.setCellWidget(table_index, 0, self.exo_combo)

    def set_action_buttons(self):
        action_buttons = QWidget()
        self.main_layout.addWidget(action_buttons)
        self.action_buttons_layout = HorizontalLayout()
        action_buttons.setLayout(self.action_buttons_layout)

        self.button_save = PushButtonIcon(
            "save.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_save.setCheckable(False)
        self.button_save.clicked.connect(self.on_save)
        self.action_buttons_layout.addWidget(self.button_save)

        self.set_btn_delete()

    def set_btn_delete(self):
        if self.equipment is not None:
            self.button_delete = PushButtonIcon(
                "delete.svg", width=80, height=40, icon_size=20, parent=self
            )
            self.button_delete.setCheckable(False)
            self.button_delete.clicked.connect(self.on_delete)
            self.action_buttons_layout.addWidget(self.button_delete)

    @pyqtSlot()
    def on_delete(self):
        assert self.equipment is not None
        EquipmentService.delete_equipment(self.service, self.equipment.id)
        self.signals.deleted_item.emit()

    @pyqtSlot()
    def on_save(self):
        updated_equipment = UpdateEquipmentSchema(
            label=self.get_edited_label(),
            lines=self.get_edited_lines(),
            exo_line=self.get_exo_line(),
        )
        try:
            if self.equipment is not None:
                EquipmentService.update_equipment(
                    self.service, self.equipment.id, updated_equipment
                )
            else:
                equipment = EquipmentService.create_equipment(
                    self.service, updated_equipment
                )
                self.equipment = equipment
                self.set_btn_delete()
                self.set_item_from_equipment(self.equipment)
        except Exception:
            self.logger.error(traceback.format_exc())
            return

        self.signals.saved_item.emit()

    def get_exo_line(self) -> BaseLineSchema | None:
        stat: StatSchema | None = self.exo_combo.currentData()
        if stat is None:
            return None
        return BaseLineSchema(value=1, stat=stat, stat_id=stat.id)

    def get_edited_label(self) -> str:
        return self.label_edit.text()

    def get_edited_lines(self) -> list[BaseLineSchema]:
        edited_lines: list[BaseLineSchema] = []
        for line_edit, line_schema in self.lines_edit:
            line_schema.value = int(line_edit.text())
            edited_lines.append(line_schema)
        return edited_lines
