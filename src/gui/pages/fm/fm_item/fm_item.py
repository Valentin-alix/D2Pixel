import traceback
from logging import Logger

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, StatSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)
from src.gui.pages.fm.fm_item.fm_item_table import FmItemTable
from src.gui.signals.bot_signals import BotSignals
from src.services.client_service import ClientService
from src.services.equipment import EquipmentService


class FmItemSignals(QObject):
    saved_item = pyqtSignal(object)
    created_item = pyqtSignal(object)
    deleted_item = pyqtSignal(object)


class FmItem(QWidget):
    def __init__(
        self,
        bot_signals: BotSignals,
        logger: Logger,
        service: ClientService,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.bot_signals = bot_signals
        self.signals = FmItemSignals()
        self.service = service
        self.equipment: ReadEquipmentSchema | None = None

        self.main_layout = VerticalLayout()
        self.setLayout(self.main_layout)

        self._setup_count_achieved()
        self._setup_item_content()
        self._setup_action_buttons()

    def set_item_from_equipment(self, equipment: ReadEquipmentSchema):
        self.equipment = equipment
        self.label_edit.setText(equipment.label)
        self.fm_item_table.set_table_from_equipment(equipment)
        self.button_delete.show()

        self.label_count_achieved.setText(str(equipment.count_lines_achieved))
        self.bot_signals.fm_new_count_achieved.connect(self._on_new_count_achieved)
        self.count_achieved_widget.show()

    def set_item_from_base_lines(self, base_lines: list[BaseLineSchema]):
        self.equipment = None
        self.label_edit.setText("")
        self.fm_item_table.set_table_from_base_lines(base_lines)
        self.button_delete.hide()
        self.count_achieved_widget.hide()

    def get_exo_stat(self) -> StatSchema | None:
        stat_id: int | None = self.fm_item_table.exo_combo.currentData()
        if stat_id is None:
            return None
        related_stat: StatSchema = next(
            _elem for _elem in self.fm_item_table.stats if _elem.id == stat_id
        )
        return related_stat

    def get_edited_label(self) -> str:
        return self.label_edit.text()

    def get_edited_lines(self) -> list[BaseLineSchema]:
        edited_lines: list[BaseLineSchema] = []
        for line_edit, line_schema in self.fm_item_table.edits_with_line:
            line_schema.value = int(line_edit.text())
            edited_lines.append(line_schema)
        return edited_lines

    def _setup_item_content(self):
        self.label_equip_widget = QWidget()
        self.label_equip_layout = QFormLayout()
        self.label_equip_widget.setLayout(self.label_equip_layout)
        self.label_edit = QLineEdit()
        self.label_equip_layout.addRow("Label", self.label_edit)
        self.main_layout.addWidget(self.label_equip_widget)

        self.fm_item_table: FmItemTable = FmItemTable(self.bot_signals, self.service)
        self.main_layout.addWidget(self.fm_item_table)

    def _setup_count_achieved(self) -> None:
        self.count_achieved_widget = QWidget()
        count_layout = HorizontalLayout()
        count_layout.setAlignment(Qt.AlignCenter)
        self.count_achieved_widget.setLayout(count_layout)

        title = QLabel()
        title.setText("Nombre de passage aux lignes ciblés réussis : ")
        self.count_achieved_widget.layout().addWidget(title)

        self.label_count_achieved = QLabel()
        self.count_achieved_widget.layout().addWidget(self.label_count_achieved)

        self.count_achieved_widget.hide()
        self.layout().addWidget(self.count_achieved_widget)

    def _setup_action_buttons(self):
        action_buttons = QWidget()
        self.main_layout.addWidget(action_buttons)
        self.action_buttons_layout = HorizontalLayout()
        action_buttons.setLayout(self.action_buttons_layout)

        self.button_save = PushButtonIcon(
            "save.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_save.clicked.connect(self._on_save)
        self.action_buttons_layout.addWidget(self.button_save)

        self.button_delete = PushButtonIcon(
            "delete.svg", width=80, height=40, icon_size=20, parent=self
        )
        self.button_delete.hide()
        self.button_delete.clicked.connect(self._on_delete)
        self.action_buttons_layout.addWidget(self.button_delete)

    @pyqtSlot(int)
    def _on_new_count_achieved(self, count_achieved: int):
        self.label_count_achieved.setText(str(count_achieved))

    @pyqtSlot()
    def _on_delete(self):
        assert self.equipment is not None
        EquipmentService.delete_equipment(self.service, self.equipment.id)
        self.signals.deleted_item.emit(self.equipment)

    @pyqtSlot()
    def _on_save(self):
        updated_equipment = UpdateEquipmentSchema(
            label=self.get_edited_label(),
            lines=self.get_edited_lines(),
            exo_stat=self.get_exo_stat(),
        )
        try:
            if self.equipment is not None:
                self.equipment = EquipmentService.update_equipment(
                    self.service, self.equipment.id, updated_equipment
                )
                self.signals.saved_item.emit(self.equipment)
            else:
                self.equipment = EquipmentService.create_equipment(
                    self.service, updated_equipment
                )
                self.set_item_from_equipment(self.equipment)
                self.signals.created_item.emit(self.equipment)
        except Exception:
            self.logger.error(traceback.format_exc())
            return
