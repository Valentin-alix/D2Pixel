from PyQt5.QtWidgets import QDialog, QLabel, QWidget

from src.gui.components.buttons import PushButton
from src.gui.components.organization import (
    HorizontalLayout,
    VerticalLayout,
)


class Dialog(QDialog):
    def open(self):
        self.exec_()


class ConfirmationDialog(Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumSize(200, 100)
        self.setWindowTitle("Confirmation")

        self.buttons = QWidget()
        self.buttons_layout = HorizontalLayout(space=8, margins=(8, 8, 8, 8))
        self.buttons.setLayout(self.buttons_layout)
        self.yes_btn = PushButton(text="Oui")
        self.buttons_layout.addWidget(self.yes_btn)
        self.no_btn = PushButton(text="Non")
        self.buttons_layout.addWidget(self.no_btn)

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)

        self.v_layout = VerticalLayout(space=8, margins=(8, 8, 8, 8))
        msg = QLabel("Êtes vous sur ?!")
        self.v_layout.addWidget(msg)
        self.v_layout.addWidget(self.buttons)
        self.setLayout(self.v_layout)
