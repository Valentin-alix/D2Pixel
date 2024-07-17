import traceback
from logging import Logger

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QTabWidget,
)

from D2Shared.shared.enums import ElemEnum
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.spell import UpdateSpellSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
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
from src.services.character import CharacterService
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

    @pyqtSlot()
    def on_save(self) -> None:
        try:
            server_id: int = self.general_tab.server_combo.currentData()
            lvl = int(self.general_tab.bot_lvl_form.text())
            is_sub = self.general_tab.sub_checkbox.isChecked()
            elem: ElemEnum = self.general_tab.elem_combo.currentData()

            waypoints = self.general_tab.combo_waypoints.currentData()
            if set((elem.id for elem in self.general_tab.origin_waypoints)) != set(
                waypoints
            ):
                self.character.waypoints = waypoints
                CharacterService.update_waypoints(
                    self.service,
                    self.character.id,
                    [elem.id for elem in self.character.waypoints],
                )

            sub_areas: list[SubAreaSchema] = [
                _elem
                for combo in self.farm_tab.combo_sub_areas
                for _elem in combo.currentData()
            ]
            if set((elem.id for elem in self.farm_tab.origin_sub_areas)) != set(
                sub_areas
            ):
                self.character.sub_areas = sub_areas
                CharacterService.update_sub_areas(
                    self.service,
                    self.character.id,
                    [elem.id for elem in self.character.sub_areas],
                )

            if (
                lvl != self.character.lvl
                or server_id != self.character.server_id
                or is_sub != self.character.is_sub
                or elem != self.character.elem
            ):
                self.character.lvl = lvl
                self.character.server_id = server_id
                self.character.is_sub = is_sub
                self.character.elem = elem
                CharacterService.update_character(
                    self.service,
                    UpdateCharacterSchema(
                        id=self.character.id,
                        lvl=self.character.lvl,
                        po_bonus=self.character.po_bonus,
                        is_sub=self.character.is_sub,
                        time_spent=self.character.time_spent,
                        elem=self.character.elem,
                        server_id=self.character.server_id,
                    ),
                )

            job_infos: list[CharacterJobInfoSchema] = []
            for (
                job_info,
                job_lvl_edit,
                job_weight_edit,
            ) in self.general_tab.job_info_edits:
                job_lvl = int(job_lvl_edit.text())
                if job_weight_edit is not None:
                    job_weight = float(job_weight_edit.text())
                else:
                    job_weight = 1
                job_info.lvl = job_lvl
                job_info.weight = job_weight
                job_infos.append(job_info)

            CharacterService.update_job_infos(
                self.service, self.character.id, job_infos
            )

            spells: list[UpdateSpellSchema] = []
            for spell_info_edit in self.gameplay_tab.spell_edits.values():
                name = spell_info_edit.name_edit.text()
                index = int(spell_info_edit.index_edit.text())
                elem = spell_info_edit.elem_combo.currentData()
                is_disenchantement = spell_info_edit.disenchantment_checkbox.isChecked()

                if (data_boost_char := spell_info_edit.boost_combo.currentData()) != "":
                    boost_char = data_boost_char
                else:
                    boost_char = None

                is_healing = spell_info_edit.healing_checkbox.isChecked()
                is_for_enemy = spell_info_edit.for_enemy_checkbox.isChecked()
                ap_cost = int(spell_info_edit.ap_cost_edit.text())
                max_cast = int(spell_info_edit.max_cast_edit.text())
                min_range = int(spell_info_edit.min_range_edit.text())
                range = int(spell_info_edit.range_edit.text())
                if (
                    str_duration_boost := spell_info_edit.duration_boost_edit.text()
                ) != "":
                    duration_boost = int(str_duration_boost)
                else:
                    duration_boost = 0
                is_boostable_range = (
                    spell_info_edit.boostable_range_checkbox.isChecked()
                )
                level = int(spell_info_edit.level_edit.text())

                spells.append(
                    UpdateSpellSchema(
                        name=name,
                        boost_char=boost_char,
                        ap_cost=ap_cost,
                        boostable_range=is_boostable_range,
                        duration_boost=duration_boost,
                        elem=elem,
                        index=index,
                        is_disenchantment=is_disenchantement,
                        is_for_enemy=is_for_enemy,
                        is_healing=is_healing,
                        level=level,
                        max_cast=max_cast,
                        min_range=min_range,
                        range=range,
                        character_id=self.character.id,
                    )
                )
            self.character.spells = CharacterService.update_spells(
                self.service, self.character.id, spells
            )
        except Exception:
            self.logger.error(traceback.format_exc())
            return

        self.close()
