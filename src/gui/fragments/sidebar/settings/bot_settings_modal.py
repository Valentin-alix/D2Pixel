from EzreD2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGroupBox, QLabel, QWidget

from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButton
from src.gui.components.dialog import Dialog
from src.gui.components.form import Form
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.breed import BreedService
from src.services.character import CharacterService
from src.services.server import ServerService


class BotSettingsModal(Dialog):
    def __init__(
        self,
        module_manager: ModuleManager,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.valid_lvl = QIntValidator()
        self.valid_lvl.setRange(1, 200)

        self.setWindowTitle(module_manager.character.id)
        self.module_manager = module_manager

        self.main_layout = VerticalLayout(margins=(16, 16, 16, 16))
        self.setLayout(self.main_layout)

        character = self.module_manager.character

        self.set_is_sub(character)
        self.set_server_choices(character)
        self.set_breed_choices(character)

        self.set_bot_lvl(character)

        self.set_bot_job_lvls(character)

        self.set_save_btn()

    def set_server_choices(self, character: CharacterSchema):
        self.server_widget = QWidget()
        self.main_layout.addWidget(self.server_widget)
        self.server_widget_layout = HorizontalLayout(8)
        self.server_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.server_widget.setLayout(self.server_widget_layout)

        title = QLabel("Serveur")
        self.server_widget_layout.addWidget(title)

        self.server_combo = QComboBox()
        self.server_combo.setFixedWidth(100)
        self.server_widget_layout.addWidget(self.server_combo)
        servers = ServerService.get_servers()
        for server in servers:
            self.server_combo.addItem(server.name, server.id)
        index = self.server_combo.findData(character.server_id)
        self.server_combo.setCurrentIndex(index)

    def set_breed_choices(self, character: CharacterSchema):
        self.breed_widget = QWidget()
        self.main_layout.addWidget(self.breed_widget)
        self.breed_widget_layout = HorizontalLayout(8)
        self.breed_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.breed_widget.setLayout(self.breed_widget_layout)

        title = QLabel("Classe")
        self.breed_widget_layout.addWidget(title)

        self.breed_combo = QComboBox()
        self.breed_combo.setFixedWidth(100)
        self.breed_widget_layout.addWidget(self.breed_combo)

        breeds = BreedService.get_breeds()
        for breed in sorted(breeds, key=lambda elem: elem.name):
            self.breed_combo.addItem(breed.name, breed.id)
        index = self.breed_combo.findData(character.breed_id)
        self.breed_combo.setCurrentIndex(index)

    def set_is_sub(self, character: CharacterSchema):
        self.is_sub_widget = QWidget()
        self.is_sub_widget_layout = HorizontalLayout(8)
        self.is_sub_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.is_sub_widget.setLayout(self.is_sub_widget_layout)

        label = QLabel("Est Abonné")
        self.is_sub_widget_layout.addWidget(label)
        self.sub_checkbox = QCheckBox()
        self.is_sub_widget_layout.addWidget(self.sub_checkbox)
        self.sub_checkbox.setChecked(character.is_sub)

        self.main_layout.addWidget(self.is_sub_widget)

    def set_bot_lvl(self, character: CharacterSchema):
        self.bot_lvl_form = Form("Niveau")
        self.bot_lvl_form.line_edit.setValidator(self.valid_lvl)
        self.bot_lvl_form.line_edit.setText(str(character.lvl))
        self.main_layout.addWidget(self.bot_lvl_form)

    def set_bot_job_lvls(self, character: CharacterSchema):
        self.box_job_lvl = QGroupBox()
        box_job_lvl_layout = HorizontalLayout()
        self.box_job_lvl.setLayout(box_job_lvl_layout)
        self.main_layout.addWidget(self.box_job_lvl)

        self.form_job_infos: list[tuple[CharacterJobInfoSchema, Form]] = []
        job_infos = sorted(
            CharacterService.get_job_infos(character.id), key=lambda elem: elem.job.name
        )

        GROUP_COUNT = 4
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
        lvl = int(self.bot_lvl_form.line_edit.text())
        is_sub = self.sub_checkbox.isChecked()

        character = self.module_manager.character

        character.lvl = lvl
        character.server_id = server_id
        character.breed_id = breed_id
        character.is_sub = is_sub

        CharacterService.update_character(character)

        for job_info, form_job in self.form_job_infos:
            job_lvl = int(form_job.line_edit.text())
            if job_info.lvl == job_lvl:
                continue
            CharacterService.update_job_info(character.id, job_info.job_id, job_lvl)

        self.close()
