from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QWidget,
)

from D2Shared.shared.consts.jobs import HARVEST_JOBS_ID
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from src.bots.modules.module_manager import ModuleManager
from src.gui.components.buttons import PushButton
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.dialog import Dialog
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.breed import BreedService
from src.services.character import CharacterService
from src.services.server import ServerService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService
from src.services.world import WorldService


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

        self.set_bot_job_infos(character)

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

        self.combo_waypoints = CheckableComboBox(parent=self)
        self.origin_waypoints = CharacterService.get_waypoints(
            self.service, character.id
        )
        character_waypoints = self.origin_waypoints
        for waypoint in sorted(
            WorldService.get_waypoints(self.service, 1),
            key=lambda elem: elem.map.sub_area.name,
        ):
            checked = waypoint in character_waypoints
            self.combo_waypoints.addItem(
                waypoint.map.sub_area.name, waypoint.id, checked=checked
            )
        form.addRow("Zaaps", self.combo_waypoints)

        self.combo_sub_areas = CheckableComboBox(parent=self)
        self.origin_sub_areas = CharacterService.get_sub_areas(
            self.service, character.id
        )
        character_sub_areas = self.origin_sub_areas
        for sub_area in sorted(
            SubAreaService.get_sub_areas(self.service),
            key=lambda elem: elem.name,
        ):
            checked = sub_area in character_sub_areas
            self.combo_sub_areas.addItem(sub_area.name, sub_area.id, checked=checked)
        form.addRow("Zones farmable", self.combo_sub_areas)

    def set_bot_job_infos(self, character: CharacterSchema):
        self.box_job_lvl = QGroupBox()
        box_job_lvl_layout = HorizontalLayout()
        self.box_job_lvl.setLayout(box_job_lvl_layout)
        self.main_layout.addWidget(self.box_job_lvl)

        self.job_info_edits: list[
            tuple[CharacterJobInfoSchema, QLineEdit, QLineEdit | None]
        ] = []
        job_infos = sorted(
            CharacterService.get_job_infos(self.service, character.id),
            key=lambda elem: (elem.job.id not in HARVEST_JOBS_ID, elem.job.name),
        )

        GROUP_COUNT: int = 4
        for index in range(0, len(job_infos), GROUP_COUNT):
            group_job = QWidget()
            box_job_lvl_layout.addWidget(group_job)
            group_form_layout = VerticalLayout()
            group_job.setLayout(group_form_layout)

            for job_info in job_infos[index : index + GROUP_COUNT]:
                job_widget = QGroupBox()
                job_widget.setStyleSheet(""" padding: 0px; """)
                group_form_layout.addWidget(job_widget)
                v_layout = VerticalLayout(space=0, margins=(0, 0, 0, 0))
                job_widget.setLayout(v_layout)

                job_label = QLabel()
                job_label.setStyleSheet(""" font-size: 16px; """)
                job_label.setText(job_info.job.name)
                v_layout.addWidget(job_label)

                job_info_widget = QWidget()
                h_layout = HorizontalLayout()
                job_info_widget.setLayout(h_layout)

                job_lvl_widget = QWidget()
                h_layout.addWidget(job_lvl_widget)
                job_lvl_layout = QFormLayout()
                job_lvl_widget.setLayout(job_lvl_layout)

                job_lvl_edit = QLineEdit()
                job_lvl_edit.setValidator(self.valid_lvl)
                job_lvl_edit.setText(str(job_info.lvl))
                job_lvl_layout.addRow("Niveau", job_lvl_edit)

                if job_info.job_id in HARVEST_JOBS_ID:
                    job_weight_widget = QWidget()
                    h_layout.addWidget(job_weight_widget)
                    job_weight_layout = QFormLayout()
                    job_weight_widget.setLayout(job_weight_layout)

                    job_weight_edit = QLineEdit()
                    job_weight_edit.setText(str(job_info.weight))
                    job_weight_layout.addRow("Poids", job_weight_edit)
                else:
                    job_weight_edit = None

                self.job_info_edits.append((job_info, job_lvl_edit, job_weight_edit))

                v_layout.addWidget(job_info_widget)

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

        waypoint_ids = self.combo_waypoints.currentData()
        if set((elem.id for elem in self.origin_waypoints)) != set(waypoint_ids):
            CharacterService.update_waypoints(self.service, character.id, waypoint_ids)

        sub_area_ids = self.combo_sub_areas.currentData()
        if set((elem.id for elem in self.origin_sub_areas)) != set(sub_area_ids):
            CharacterService.update_sub_areas(self.service, character.id, sub_area_ids)

        if (
            lvl != character.lvl
            or server_id != character.server_id
            or breed_id != character.breed_id
            or is_sub != character.is_sub
        ):
            character.lvl = lvl
            character.server_id = server_id
            character.breed_id = breed_id
            character.is_sub = is_sub
            CharacterService.update_character(self.service, character)

        for job_info, job_lvl_edit, job_weight_edit in self.job_info_edits:
            job_lvl = int(job_lvl_edit.text())
            if job_weight_edit is not None:
                job_weight = float(job_weight_edit.text())
            else:
                job_weight = 1
            if job_info.lvl == job_lvl and job_weight == job_info.weight:
                continue
            CharacterService.update_job_info(
                self.service, character.id, job_info.job_id, job_lvl, job_weight
            )

        self.close()
