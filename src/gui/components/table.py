from PyQt5.QtWidgets import (
    QHeaderView,
    QScrollArea,
    QTableWidget,
)

from src.gui.components.organization import (
    AlignDelegate,
)


class BaseTableWidget(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = QTableWidget(parent=self)
        self.delegate_type = AlignDelegate

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().hide()

        self.setWidget(self.table)
        self.setWidgetResizable(True)

    def set_columns(self, columns_name: list[str]):
        self.table.setColumnCount(len(columns_name))
        delegate = self.delegate_type(self.table)
        for index in range(len(columns_name)):
            self.table.setItemDelegateForColumn(index, delegate)
        self.table.setHorizontalHeaderLabels(columns_name)


class TableWidget(BaseTableWidget):
    def __init__(self, columns_name: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_columns(columns_name)
