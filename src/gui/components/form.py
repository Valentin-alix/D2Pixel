from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget

from src.gui.components.organization import HorizontalLayout


class Form(QWidget):
    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.h_layout = HorizontalLayout()
        self.setLayout(self.h_layout)

        self.label = QLabel(name)
        self.h_layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        self.h_layout.addWidget(self.line_edit)

        self.h_layout.setAlignment(QtCore.Qt.AlignCenter)
