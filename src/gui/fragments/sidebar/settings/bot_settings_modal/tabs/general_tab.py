from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QWidget,
)

from D2Shared.shared.consts.jobs import HARVEST_JOBS_NAME
from D2Shared.shared.enums import ElemEnum
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.waypoint import WaypointSchema
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.character import CharacterService
from src.services.server import ServerService
from src.services.session import ServiceSession
from src.services.world import WorldService


class GeneralTab(QWidget):
    def __init__(
        self, service: ServiceSession, character: CharacterSchema, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.character = character
        self.setLayout(VerticalLayout())

        self.valid_lvl = QIntValidator()
        self.valid_lvl.setRange(1, 200)

        self._set_base_infos()
        self._set_bot_job_infos()

        self.set_default_values()

    def set_default_values(self) -> None:
        self.bot_lvl_form.setText(str(self.character.lvl))
        self.combo_waypoints.clear()
        for waypoint in sorted(
            WorldService.get_waypoints(self.service, 1),
            key=lambda elem: elem.map.sub_area.name,
        ):
            checked = waypoint in self.character.waypoints
            self.combo_waypoints.addItem(
                waypoint.map.sub_area.name, waypoint, checked=checked
            )
        for char_job_info, job_lvl_edit, _ in self.job_info_edits:
            job_lvl_edit.setText(str(char_job_info.lvl))

    def _set_base_infos(self) -> None:
        base_info_wid = QWidget()
        self.layout().addWidget(base_info_wid)
        form = QFormLayout()
        form.setAlignment(Qt.AlignCenter)
        base_info_wid.setLayout(form)

        self.server_combo = QComboBox()
        servers = ServerService.get_servers(self.service)
        for server in servers:
            self.server_combo.addItem(server.name, server.id)
        server_index = self.server_combo.findData(self.character.server_id)
        self.server_combo.setCurrentIndex(server_index)
        form.addRow("Serveur", self.server_combo)

        self.bot_lvl_form = QLineEdit()
        self.bot_lvl_form.setValidator(self.valid_lvl)
        form.addRow("Niveau", self.bot_lvl_form)

        self.elem_combo = QComboBox()
        for elem_option in ElemEnum:
            self.elem_combo.addItem(elem_option, elem_option)
        elem_index = self.elem_combo.findData(self.character.elem)
        self.elem_combo.setCurrentIndex(elem_index)
        form.addRow("Élément", self.elem_combo)

        self.combo_waypoints = CheckableComboBox[WaypointSchema](parent=self)
        form.addRow("Zaaps", self.combo_waypoints)

    def _set_bot_job_infos(self) -> None:
        self.box_job_lvl = QGroupBox()
        box_job_lvl_layout = HorizontalLayout()
        self.box_job_lvl.setLayout(box_job_lvl_layout)
        self.layout().addWidget(self.box_job_lvl)

        self.job_info_edits: list[
            tuple[CharacterJobInfoSchema, QLineEdit, QLineEdit | None]
        ] = []
        job_infos = sorted(
            self.character.character_job_info,
            key=lambda elem: (elem.job.name not in HARVEST_JOBS_NAME, elem.job.name),
        )

        GROUP_COUNT: int = 4
        for index in range(0, len(job_infos), GROUP_COUNT):
            group_job = QWidget()
            box_job_lvl_layout.addWidget(group_job)
            group_form_layout = VerticalLayout()
            group_job.setLayout(group_form_layout)

            for job_info in job_infos[index : index + GROUP_COUNT]:
                job_widget = QGroupBox()
                job_widget.setProperty("class", "p-0")
                group_form_layout.addWidget(job_widget)
                v_layout = VerticalLayout(space=0, margins=(0, 0, 0, 0))
                job_widget.setLayout(v_layout)

                job_label = QLabel()
                job_label.setProperty("class", "fs-16")
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
                job_lvl_layout.addRow("Niveau", job_lvl_edit)

                if job_info.job.name in HARVEST_JOBS_NAME:
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

    def on_save(self) -> None:
        server_id: int = self.server_combo.currentData()
        lvl = int(self.bot_lvl_form.text())
        elem: ElemEnum = self.elem_combo.currentData()

        waypoints = self.combo_waypoints.currentData()
        if set(self.character.waypoints) != set(waypoints):
            self.character.waypoints = waypoints
            CharacterService.update_waypoints(
                self.service,
                self.character.id,
                [elem.id for elem in self.character.waypoints],
            )

        if (
            lvl != self.character.lvl
            or server_id != self.character.server_id
            or elem != self.character.elem
        ):
            self.character.lvl = lvl
            self.character.server_id = server_id
            self.character.elem = elem
            CharacterService.update_character(
                self.service,
                UpdateCharacterSchema(
                    id=self.character.id,
                    lvl=self.character.lvl,
                    po_bonus=self.character.po_bonus,
                    elem=self.character.elem,
                    server_id=self.character.server_id,
                ),
            )

        job_infos: list[CharacterJobInfoSchema] = []
        for (
            job_info,
            job_lvl_edit,
            job_weight_edit,
        ) in self.job_info_edits:
            job_lvl = int(job_lvl_edit.text())
            if job_weight_edit is not None:
                job_weight = float(job_weight_edit.text())
            else:
                job_weight = 1
            job_info.lvl = job_lvl
            job_info.weight = job_weight
            job_infos.append(job_info)

        CharacterService.update_job_infos(self.service, self.character.id, job_infos)
