from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit

from D2Shared.shared.enums import ExoStatEnum
from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, LineSchema, StatSchema
from src.gui.components.organization import AlignDelegate
from src.gui.components.table import BaseTableWidget
from src.gui.signals.bot_signals import BotSignals
from src.services.session import ServiceSession
from src.services.stat import StatService


class FmItemTable(BaseTableWidget):
    def __init__(
        self, bot_signals: BotSignals, service: ServiceSession, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bot_signals = bot_signals
        self.service = service
        self.label_spent_by_stat_id: dict[int, QLabel] = {}
        self.edits_with_line: list[tuple[QLineEdit, BaseLineSchema]] = []
        self.stats = StatService.get_stats(self.service)
        self.bot_signals.fm_new_line_value.connect(self.on_new_line_value)

    def set_table_from_equipment(self, equipment: ReadEquipmentSchema):
        self.clear_table()
        columns = ["Stat", "Valeur", "Tentative"]
        self.set_columns(columns)

        for line in equipment.lines:
            table_index = self.table.rowCount()
            self.table.setRowCount(table_index + 1)
            self._add_line(table_index, line)

        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)
        if equipment.exo_stat:
            self._add_exo_line(table_index, equipment.exo_stat, equipment.exo_attempt)
        else:
            self._add_empty_exo_line(table_index)

    def set_table_from_base_lines(self, base_lines: list[BaseLineSchema]):
        self.clear_table()
        columns = ["Stat", "Valeur"]
        self.set_columns(columns)

        for line in base_lines:
            table_index = self.table.rowCount()
            self.table.setRowCount(table_index + 1)
            self._add_base_line(table_index, line)

        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)
        self._add_empty_exo_line(table_index)

    def clear_table(self):
        self.edits_with_line.clear()
        self.table.setRowCount(0)

    def _add_empty_exo_line(self, table_index: int):
        self.exo_combo = QComboBox()
        self.exo_combo.setItemDelegate(AlignDelegate(self.exo_combo))

        self.exo_combo.setEditable(True)

        self.exo_combo.addItem("", None)
        for stat in self.stats:
            if stat.name not in ExoStatEnum:
                continue
            self.exo_combo.addItem(stat.name, stat.id)

        exo_combo_edit = self.exo_combo.lineEdit()
        exo_combo_edit.setAlignment(Qt.AlignCenter)
        exo_combo_edit.setReadOnly(True)

        self.table.setCellWidget(table_index, 0, self.exo_combo)

        self.exo_attempt_label = QLabel()
        self.table.setCellWidget(table_index, 2, self.exo_attempt_label)

    def _add_exo_line(self, table_index: int, exo_stat: StatSchema, exo_attempt: int):
        self._add_empty_exo_line(table_index)

        exo_index = self.exo_combo.findData(exo_stat.id)
        self.exo_combo.setCurrentIndex(exo_index)

        self.exo_attempt_label.setText(str(exo_attempt))
        self.label_spent_by_stat_id[exo_stat.id] = self.exo_attempt_label

    def _add_base_line(self, table_index: int, base_line: BaseLineSchema):
        line_label = QLabel()
        line_label.setText(base_line.stat.name)
        self.table.setCellWidget(table_index, 0, line_label)

        line_edit = QLineEdit()
        line_edit.setText(str(base_line.value))
        self.table.setCellWidget(table_index, 1, line_edit)
        self.edits_with_line.append((line_edit, base_line))

    def _add_line(self, table_index: int, line: LineSchema):
        self._add_base_line(table_index, line)
        line_spent = QLabel()
        line_spent.setText(str(line.spent_quantity))
        self.table.setCellWidget(table_index, 2, line_spent)
        self.label_spent_by_stat_id[line.stat_id] = line_spent

    @pyqtSlot(object)
    def on_new_line_value(self, spent_with_stat_id: tuple[int, int]):
        spent_quantity, stat_id = spent_with_stat_id
        related_label_spent = self.label_spent_by_stat_id[stat_id]
        related_label_spent.setText(str(spent_quantity))
