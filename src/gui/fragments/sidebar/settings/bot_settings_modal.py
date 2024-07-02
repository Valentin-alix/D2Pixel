from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QWidget,
    QFormLayout,
    QLineEdit,
)

from D2Shared.shared.consts.jobs import HARVEST_JOBS_ID
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButton
from src.gui.components.dialog import Dialog
from src.gui.components.form import Form
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.breed import BreedService
from src.services.character import CharacterService
from src.services.server import ServerService
from src.services.session import ServiceSession


class BotSettingsModal(Dialog):
    def __init__(
        self,
        service: ServiceSession,
        module_manager: ModuleManager,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.valid_lvl = QIntValidator()
        self.valid_lvl.setRange(1, 200)

        self.setWindowTitle(module_manager.character_state.character.id)
        self.module_manager = module_manager

        self.main_layout = VerticalLayout(margins=(16, 16, 16, 16))
        self.setLayout(self.main_layout)

        character = self.module_manager.character_state.character

        self.set_top_form(character)

        self.set_bot_job_lvls(character)

        self.set_save_btn()

    def set_top_form(self, character: CharacterSchema):
        self.top_widget = QWidget()
        self.main_layout.addWidget(self.top_widget)
        form = QFormLayout()
        form.setAlignment(Qt.AlignCenter)
        self.top_widget.setLayout(form)

        self.sub_checkbox = QCheckBox()
        self.sub_checkbox.setChecked(character.is_sub)
        form.addRow("Est Abonné", self.sub_checkbox)

        self.server_combo = QComboBox()
        servers = ServerService.get_servers(self.service)
        for server in servers:
            self.server_combo.addItem(server.name, server.id)
        index = self.server_combo.findData(character.server_id)
        self.server_combo.setCurrentIndex(index)
        form.addRow("Serveur", self.server_combo)

        self.breed_combo = QComboBox()
        breeds = BreedService.get_breeds(self.service)
        for breed in sorted(breeds, key=lambda elem: elem.name):
            self.breed_combo.addItem(breed.name, breed.id)
        index = self.breed_combo.findData(character.breed_id)
        self.breed_combo.setCurrentIndex(index)
        form.addRow("Classe", self.breed_combo)

        self.bot_lvl_form = QLineEdit()
        self.bot_lvl_form.setValidator(self.valid_lvl)
        self.bot_lvl_form.setText(str(character.lvl))
        form.addRow("Niveau", self.bot_lvl_form)

    def set_bot_job_lvls(self, character: CharacterSchema):
        self.box_job_lvl = QGroupBox()
        box_job_lvl_layout = HorizontalLayout()
        self.box_job_lvl.setLayout(box_job_lvl_layout)
        self.main_layout.addWidget(self.box_job_lvl)

        self.form_job_infos: list[tuple[CharacterJobInfoSchema, Form]] = []
        job_infos = sorted(
            CharacterService.get_job_infos(self.service, character.id),
            key=lambda elem: (elem.job.id not in HARVEST_JOBS_ID, elem.job.name),
        )

        GROUP_COUNT: int = 4
        for index in range(0, len(job_infos), GROUP_COUNT):
            group_job = QWidget()
            box_job_lvl_layout.addWidget(group_job)
            group_job_layout = VerticalLayout()
            group_job.setLayout(group_job_layout)

            for job_info in job_infos[index : index + GROUP_COUNT]:
                form = Form(job_info.job.name)
                self.form_job_infos.append((job_info, form))
                form.line_edit.setValidator(self.valid_lvl)
                form.line_edit.setText(str(job_info.lvl))
                form.line_edit.setFixedWidth(50)
                group_job_layout.addWidget(form)

    def set_save_btn(self):
        self.save_btn = PushButton(text="Enregistrer")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setShortcut("Return")
        self.main_layout.addWidget(self.save_btn)

    @pyqtSlot()
    def on_save(self):
        server_id = self.server_combo.currentData()
        breed_id = self.breed_combo.currentData()
        lvl = int(self.bot_lvl_form.text())
        is_sub = self.sub_checkbox.isChecked()

        character = self.module_manager.character_state.character

        character.lvl = lvl
        character.server_id = server_id
        character.breed_id = breed_id
        character.is_sub = is_sub

        CharacterService.update_character(self.service, character)

        for job_info, form_job in self.form_job_infos:
            job_lvl = int(form_job.line_edit.text())
            if job_info.lvl == job_lvl:
                continue
            CharacterService.update_job_info(
                self.service, character.id, job_info.job_id, job_lvl
            )

        self.close()
