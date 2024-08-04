from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit

from D2Shared.shared.consts.stats import BIG_STATS_NAMES
from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, LineSchema, StatSchema
from src.gui.components.organization import AlignDelegate
from src.gui.components.table import BaseTableWidget
from src.services.session import ServiceSession
from src.services.stat import StatService


class FmItemTable(BaseTableWidget):
    def __init__(self, service: ServiceSession, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.labels_spent_by_stat_id: dict[int, tuple[QLabel, QLabel]] = {}
        self.edits_with_line: list[tuple[QLineEdit, BaseLineSchema]] = []
        self.stats = StatService.get_stats(self.service)
        self.sorted_exo_stats: list[StatSchema] = sorted(
            self.stats, key=lambda _stat: _stat.name in BIG_STATS_NAMES, reverse=True
        )
        self.count_lines_achieved: int | None = None

    def set_table_from_equipment(self, equipment: ReadEquipmentSchema):
        self.count_lines_achieved = equipment.count_lines_achieved
        self.clear_table()
        columns = ["Stat", "Valeur", "Tentatives", "Tentatives Moyenne"]
        self.set_columns(columns)

        for line in equipment.lines:
            table_index = self.table.rowCount()
            self.table.setRowCount(table_index + 1)
            self._add_line(table_index, line)

        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)
        if equipment.exo_stat:
            self._add_exo_line(
                table_index,
                equipment.exo_stat,
                [_elem.stat for _elem in equipment.lines],
            )
        else:
            self._add_empty_exo_line(
                table_index, [_elem.stat for _elem in equipment.lines]
            )

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
        self._add_empty_exo_line(table_index, [_elem.stat for _elem in base_lines])

    def clear_table(self):
        self.edits_with_line.clear()
        self.table.setRowCount(0)

    def _add_empty_exo_line(self, table_index: int, base_stats: list[StatSchema]):
        self.exo_combo = QComboBox()
        self.exo_combo.setItemDelegate(AlignDelegate(self.exo_combo))

        self.exo_combo.setEditable(True)

        self.exo_combo.addItem("", None)

        for stat in self.sorted_exo_stats:
            if stat in base_stats:
                continue
            self.exo_combo.addItem(stat.name, stat.id)

        exo_combo_edit = self.exo_combo.lineEdit()
        exo_combo_edit.setAlignment(Qt.AlignCenter)
        exo_combo_edit.setReadOnly(True)

        self.table.setCellWidget(table_index, 0, self.exo_combo)

        self.exo_attempt_label = QLabel()
        self.table.setCellWidget(table_index, 2, self.exo_attempt_label)

    def _add_exo_line(
        self, table_index: int, exo_stat: StatSchema, base_stats: list[StatSchema]
    ):
        self._add_empty_exo_line(table_index, base_stats)

        exo_index = self.exo_combo.findData(exo_stat.id)
        self.exo_combo.setCurrentIndex(exo_index)

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

        assert self.count_lines_achieved is not None
        line_spent_coeff = QLabel()
        if self.count_lines_achieved != 0:
            line_spent_coeff.setText(
                str(line.spent_quantity / self.count_lines_achieved)
            )
        self.table.setCellWidget(table_index, 3, line_spent_coeff)
        self.labels_spent_by_stat_id[line.stat_id] = (line_spent, line_spent_coeff)

    def _on_new_equipment_datas(self, equipment: ReadEquipmentSchema):
        self.count_lines_achieved = equipment.count_lines_achieved
        for line in equipment.lines:
            related_label_spent, label_coeff = self.labels_spent_by_stat_id[
                line.stat_id
            ]
            related_label_spent.setText(str(line.spent_quantity))
            if self.count_lines_achieved != 0:
                label_coeff.setText(
                    str(line.spent_quantity / self.count_lines_achieved)
                )
