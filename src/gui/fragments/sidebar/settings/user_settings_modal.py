import traceback
from datetime import time
from logging import Logger

from PyQt5.QtCore import Qt, QTime, pyqtSlot
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QTimeEdit, QWidget

from D2Shared.shared.schemas.config_user import (
    ReadConfigUserSchema,
    UpdateConfigUserSchema,
)
from D2Shared.shared.schemas.range_time import (
    UpdateRangeWaitSchema,
)
from D2Shared.shared.schemas.user import ReadUserSchema
from src.gui.components.buttons import PushButton
from src.gui.components.dialog import Dialog
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.gui.signals.app_signals import AppSignals
from src.services.config_user import ConfigService
from src.services.session import ServiceSession


class UserSettingsModal(Dialog):
    def __init__(
        self,
        logger: Logger,
        app_signals: AppSignals,
        user: ReadUserSchema,
        service: ServiceSession,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Paramètres")
        self.app_signals = app_signals
        self.logger = logger
        self.service = service
        self.user = user

        self.main_layout = VerticalLayout(margins=(8, 8, 8, 8))
        self.setLayout(self.main_layout)

        self.set_form(user.config_user)
        self.set_save_btn()

    def set_form(self, config_user: ReadConfigUserSchema):
        self.form_widget = QWidget()

        self.main_layout.addWidget(self.form_widget)
        form = QFormLayout()
        form.setAlignment(Qt.AlignCenter)
        self.form_widget.setLayout(form)

        self.time_between_sentence_edit = QTimeEdit()
        self.time_between_sentence_edit.setTime(
            QTime(
                config_user.time_between_sentence.hour,
                config_user.time_between_sentence.minute,
                config_user.time_between_sentence.second,
            )
        )
        form.addRow(
            "Temps entre les phrases aléatoires (HH-mm)",
            self.time_between_sentence_edit,
        )

        self.time_fighter_edit = QTimeEdit()
        self.time_fighter_edit.setTime(
            QTime(
                config_user.time_fighter.hour,
                config_user.time_fighter.minute,
                config_user.time_fighter.second,
            )
        )
        form.addRow("Temps module Combat (HH-mm)", self.time_fighter_edit)

        self.time_harvester_edit = QTimeEdit()
        self.time_harvester_edit.setTime(
            QTime(
                config_user.time_harvester.hour,
                config_user.time_harvester.minute,
                config_user.time_harvester.second,
            )
        )
        form.addRow("Temps module Récolte (HH-mm)", self.time_harvester_edit)

        range_new_map_widget = QWidget()
        range_new_map_widget_h_layout = HorizontalLayout()
        range_new_map_widget.setLayout(range_new_map_widget_h_layout)

        self.range_new_map_start_edit = QLineEdit()

        self.range_new_map_start_edit.setText(str(config_user.range_new_map.start))
        range_new_map_widget_h_layout.addWidget(self.range_new_map_start_edit)

        self.range_new_map_end_edit = QLineEdit()
        self.range_new_map_end_edit.setText(str(config_user.range_new_map.end))
        range_new_map_widget_h_layout.addWidget(self.range_new_map_end_edit)

        form.addRow("Attente en début de map (secondes)", range_new_map_widget)

        self.play_time_widget = QWidget()
        self.play_time_widget_layout = VerticalLayout()
        self.play_time_widget.setLayout(self.play_time_widget_layout)
        self.range_playtime_edits: list[tuple[QTimeEdit, QTimeEdit]] = []

    def set_save_btn(self):
        self.save_btn = PushButton(text="Enregistrer")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setShortcut("Return")
        self.main_layout.addWidget(self.save_btn)

    @pyqtSlot()
    def on_save(self):
        try:
            time_between_value = self.time_between_sentence_edit.time()
            time_between_sentence = time(
                time_between_value.hour(),
                time_between_value.minute(),
                time_between_value.second(),
            )

            time_fighter_value = self.time_fighter_edit.time()
            time_fighter = time(
                time_fighter_value.hour(),
                time_fighter_value.minute(),
                time_fighter_value.second(),
            )

            time_harvester_value = self.time_harvester_edit.time()
            time_harvester = time(
                time_harvester_value.hour(),
                time_harvester_value.minute(),
                time_harvester_value.second(),
            )

            range_new_map_start = float(self.range_new_map_start_edit.text())
            range_new_map_end = float(self.range_new_map_end_edit.text())
            range_new_map = UpdateRangeWaitSchema(
                start=range_new_map_start, end=range_new_map_end
            )

            update_config = UpdateConfigUserSchema(
                time_between_sentence=time_between_sentence,
                time_fighter=time_fighter,
                time_harvester=time_harvester,
                range_new_map=range_new_map,
            )
            self.user.config_user = ConfigService.update_config_user(
                self.service, self.user.config_user.id, update_config
            )
        except Exception:
            self.logger.error(traceback.format_exc())
            return

        self.close()
