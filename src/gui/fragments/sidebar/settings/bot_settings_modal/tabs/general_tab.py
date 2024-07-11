from PyQt5.QtCore import Qt
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
from D2Shared.shared.schemas.character import CharacterJobInfoSchema, CharacterSchema
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.organization import HorizontalLayout, VerticalLayout
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

        self.set_base_infos()
        self.set_bot_job_infos()

    def set_base_infos(self):
        base_info_wid = QWidget()
        self.layout().addWidget(base_info_wid)
        form = QFormLayout()
        form.setAlignment(Qt.AlignCenter)
        base_info_wid.setLayout(form)

        self.sub_checkbox = QCheckBox()
        self.sub_checkbox.setChecked(self.character.is_sub)
        form.addRow("Est Abonné", self.sub_checkbox)

        self.server_combo = QComboBox()
        servers = ServerService.get_servers(self.service)
        for server in servers:
            self.server_combo.addItem(server.name, server.id)
        index = self.server_combo.findData(self.character.server_id)
        self.server_combo.setCurrentIndex(index)
        form.addRow("Serveur", self.server_combo)

        self.bot_lvl_form = QLineEdit()
        self.bot_lvl_form.setValidator(self.valid_lvl)
        self.bot_lvl_form.setText(str(self.character.lvl))
        form.addRow("Niveau", self.bot_lvl_form)

        self.combo_waypoints = CheckableComboBox(parent=self)
        self.origin_waypoints = self.character.waypoints
        character_waypoints = self.origin_waypoints
        for waypoint in sorted(
            WorldService.get_waypoints(self.service, 1),
            key=lambda elem: elem.map.sub_area.name,
        ):
            checked = waypoint in character_waypoints
            self.combo_waypoints.addItem(
                waypoint.map.sub_area.name, waypoint, checked=checked
            )
        form.addRow("Zaaps", self.combo_waypoints)

    def set_bot_job_infos(self):
        self.box_job_lvl = QGroupBox()
        box_job_lvl_layout = HorizontalLayout()
        self.box_job_lvl.setLayout(box_job_lvl_layout)
        self.layout().addWidget(self.box_job_lvl)

        self.job_info_edits: list[
            tuple[CharacterJobInfoSchema, QLineEdit, QLineEdit | None]
        ] = []
        job_infos = sorted(
            self.character.character_job_info,
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
