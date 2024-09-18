from dotenv import set_key
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QLineEdit

from D2Shared.shared.schemas.user import CreateUserSchema
from src.consts import ENV_PATH
from src.gui.components.dialog import Dialog
from src.gui.signals.app_signals import AppSignals
from src.services.login import LoginService
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
        self.setWindowTitle("Connexion ou inscription")
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
        UserService.create_user(
            self.service, CreateUserSchema(email=username, password=password)
        )
        set_key(ENV_PATH, "USERNAME", username)
        set_key(ENV_PATH, "PASSWORD", password)
        if not LoginService.is_login(self.service):
            return
        self.app_signals.login_success.emit()
        self.accept()

    def get_inputs(self) -> tuple[str, str]:
        return self.username.text(), self.password.text()
