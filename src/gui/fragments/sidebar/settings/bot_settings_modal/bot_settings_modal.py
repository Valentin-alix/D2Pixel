import traceback
from logging import Logger

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QTabWidget,
)

from D2Shared.shared.enums import ElemEnum
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.spell import UpdateSpellSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.bots.modules.module_manager import ModuleManager
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
        module_manager: ModuleManager,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.service = service
        self.logger = logger

        self.setWindowTitle(module_manager.character_state.character.id)
        self.module_manager = module_manager

        self.main_layout = VerticalLayout(margins=(16, 16, 16, 16))
        self.setLayout(self.main_layout)

        character = self.module_manager.character_state.character

        self.set_save_btn()

        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)

        self.general_tab = GeneralTab(service, character)
        self.tabs.addTab(self.general_tab, "Général")

        self.farm_tab = FarmTab(service, character)
        self.tabs.addTab(self.farm_tab, "Farm")

        self.gameplay_tab = GameplayTab(service, character)
        self.tabs.addTab(self.gameplay_tab, "Gameplay")

    def set_save_btn(self):
        self.save_btn = PushButton(text="Enregistrer")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setShortcut("Return")
        self.main_layout.addWidget(self.save_btn)

    @pyqtSlot()
    def on_save(self) -> None:
        try:
            server_id: int = self.general_tab.server_combo.currentData()
            lvl = int(self.general_tab.bot_lvl_form.text())
            is_sub = self.general_tab.sub_checkbox.isChecked()
            elem: ElemEnum = self.general_tab.elem_combo.currentData()

            character_state = self.module_manager.character_state

            waypoints = self.general_tab.combo_waypoints.currentData()
            if set((elem.id for elem in self.general_tab.origin_waypoints)) != set(
                waypoints
            ):
                character_state.character.waypoints = waypoints
                CharacterService.update_waypoints(
                    self.service,
                    character_state.character.id,
                    [elem.id for elem in character_state.character.waypoints],
                )

            sub_areas: list[SubAreaSchema] = [
                elem
                for combo in self.farm_tab.combo_sub_areas
                for elem in combo.currentData()
            ]
            if set((elem.id for elem in self.farm_tab.origin_sub_areas)) != set(
                sub_areas
            ):
                character_state.character.sub_areas = sub_areas
                CharacterService.update_sub_areas(
                    self.service,
                    character_state.character.id,
                    [elem.id for elem in character_state.character.sub_areas],
                )

            if (
                lvl != character_state.character.lvl
                or server_id != character_state.character.server_id
                or is_sub != character_state.character.is_sub
                or elem != character_state.character.elem
            ):
                character_state.character.lvl = lvl
                character_state.character.server_id = server_id
                character_state.character.is_sub = is_sub
                character_state.character.elem = elem
                CharacterService.update_character(
                    self.service,
                    UpdateCharacterSchema(
                        id=character_state.character.id,
                        lvl=character_state.character.lvl,
                        po_bonus=character_state.character.po_bonus,
                        is_sub=character_state.character.is_sub,
                        time_spent=character_state.character.time_spent,
                        elem=character_state.character.elem,
                        server_id=character_state.character.server_id,
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
                self.service, character_state.character.id, job_infos
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
                        character_id=character_state.character.id,
                    )
                )
            character_state.character.spells = CharacterService.update_spells(
                self.service, character_state.character.id, spells
            )
        except Exception:
            self.logger.error(traceback.format_exc())
            return

        self.close()
