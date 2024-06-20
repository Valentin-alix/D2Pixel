from dotenv import get_key, set_key
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QLabel, QWidget

from src.consts import ENV_PATH
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.dialog import Dialog
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.signals.app_signals import AppSignals


class PcSettingsModal(Dialog):
    def __init__(
        self,
        app_signals: AppSignals,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Paramètres")
        self.app_signals = app_signals

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.setLayout(self.main_layout)

        self.launcher_settings = QWidget()
        self.main_layout.addWidget(self.launcher_settings)
        self.launcher_settings_layout = HorizontalLayout(space=4)
        self.launcher_settings.setLayout(self.launcher_settings_layout)

        self.set_ankama_launcher_settings()

    def set_ankama_launcher_settings(self):
        curr_path_ankama = get_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER") or "Vide"

        widget = QWidget()
        self.launcher_settings_layout.addWidget(widget)
        widget_layout = HorizontalLayout()
        widget.setLayout(widget_layout)

        text = QWidget()
        widget_layout.addWidget(text)
        text_layout = VerticalLayout()
        text.setLayout(text_layout)
        path_ankama_title_label = QLabel(text="Chemin de l'ankama launcher :")
        self.path_ankama_value_label = QLabel(text=curr_path_ankama)
        font = QFont()
        font.setItalic(True)
        self.path_ankama_value_label.setFont(font)
        text_layout.addWidget(path_ankama_title_label)
        text_layout.addWidget(self.path_ankama_value_label)

        folder_open = PushButtonIcon(
            filename="folder_open.svg", height=35, width=45, icon_size=25
        )
        folder_open.clicked.connect(self.open_search_launcher)
        widget_layout.addWidget(folder_open)

    def open_search_launcher(self):
        filename = QFileDialog.getOpenFileName(
            self, "Open file", "c:\\", "Executable (*.exe)"
        )[0]
        if filename == "":
            return
        set_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER", filename)
        self.path_ankama_value_label.setText(filename)
