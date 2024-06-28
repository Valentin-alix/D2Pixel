from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QLineEdit
from dotenv import set_key

from src.consts import ENV_PATH
from src.gui.components.dialog import Dialog
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from src.services.user import UserService


class LoginModal(Dialog):
    def __init__(
        self,
        app_signals: AppSignals,
        service: ServiceSession,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.resize(QSize(400, 100))
        self.service = service
        self.app_signals = app_signals
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )

        layout = QFormLayout(self)
        layout.addRow("Nom d'utilisateur", self.username)
        layout.addRow("Mot de passe", self.password)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.set_login_info)
        button_box.rejected.connect(self.reject)

    def set_login_info(self):
        username, password = self.get_inputs()
        if username == "" or password == "":
            return
        set_key(ENV_PATH, "USERNAME", username)
        set_key(ENV_PATH, "PASSWORD", password)
        try:
            UserService.get_current_user(self.service)
        except Exception:
            return
        self.accept()
        self.app_signals.login_success.emit()

    def get_inputs(self) -> tuple[str, str]:
        return self.username.text(), self.password.text()
