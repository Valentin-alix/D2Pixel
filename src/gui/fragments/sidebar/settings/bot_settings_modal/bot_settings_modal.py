import traceback
from logging import Logger

from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtWidgets import (
    QTabWidget,
)

from D2Shared.shared.schemas.character import (
    CharacterSchema,
)
from src.gui.components.buttons import PushButton
from src.gui.components.dialog import Dialog
from src.gui.components.organization import VerticalLayout
from src.gui.fragments.sidebar.settings.bot_settings_modal.tabs.farm_tab import (
    FarmTab,
)
from src.gui.fragments.sidebar.settings.bot_settings_modal.tabs.gameplay_tab import (
    GameplayTab,
)
from src.gui.fragments.sidebar.settings.bot_settings_modal.tabs.general_tab import (
    GeneralTab,
)
from src.gui.utils.run_in_background import run_in_background
from src.services.session import ServiceSession


class BotSettingsModal(Dialog):
    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        character: CharacterSchema,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger
        self.character = character
        self.threads: list[QThread] = []

        self.setWindowTitle(self.character.id)
        self.setLayout(VerticalLayout(margins=(16, 16, 16, 16)))

        self._setup_save_btn()
        self._setup_tabs()

    def _setup_save_btn(self):
        self.save_btn = PushButton(text="Enregistrer")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setShortcut("Return")
        self.layout().addWidget(self.save_btn)

    def _setup_tabs(self) -> None:
        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)

        self.general_tab = GeneralTab(self.service, self.character)
        self.tabs.addTab(self.general_tab, "Général")

        self.farm_tab = FarmTab(self.service, self.character)
        self.tabs.addTab(self.farm_tab, "Farm")

        self.gameplay_tab = GameplayTab(self.service, self.character)
        self.tabs.addTab(self.gameplay_tab, "Gameplay")

    def set_default_values(self):
        self.general_tab.set_default_values()

    @pyqtSlot()
    def on_save(self) -> None:
        try:
            self.threads.append(
                run_in_background(lambda: self.general_tab.on_save())[0]
            )
            self.threads.append(run_in_background(lambda: self.farm_tab.on_save())[0])
            self.threads.append(
                run_in_background(lambda: self.gameplay_tab.on_save())[0]
            )
        except Exception:
            self.logger.error(traceback.format_exc())
            return

        self.close()
