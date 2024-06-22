from PyQt5.QtWidgets import QWidget

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
