from PyQt5.QtWidgets import (
    QHeaderView,
    QScrollArea,
    QTableWidget,
)

from src.gui.components.organization import (
    AlignDelegate,
)


class TableWidget(QScrollArea):
    def __init__(
        self, columns_name: list[str], delegate_type=AlignDelegate, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.table = QTableWidget(parent=self)
        self.table.setColumnCount(len(columns_name))

        delegate = delegate_type(self.table)
        for index in range(len(columns_name)):
            self.table.setItemDelegateForColumn(index, delegate)

        self.table.setHorizontalHeaderLabels(columns_name)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().hide()

        self.setWidget(self.table)
        self.setWidgetResizable(True)
