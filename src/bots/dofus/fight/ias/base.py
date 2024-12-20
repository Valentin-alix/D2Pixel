from dataclasses import dataclass
from logging import Logger
from time import sleep

import numpy

from D2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.cell import CellSchema
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.fight.spells.spell_system import SpellSystem
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.utils.retry import RetryTimeArgs
from src.window_manager.controller import Controller


@dataclass
class IaBaseFightSystem:
    spell_sys: SpellSystem
    grid: Grid
    ldv_grid: LdvGrid
    controller: Controller
    animation_manager: AnimationManager
    service: ServiceSession
    character_state: CharacterState
    logger: Logger
    spell_manager: SpellManager
    object_searcher: ObjectSearcher

    def reach_attackable_enemy(
        self, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, CellSchema | None]:
        max_range_dmg_spell = self.spell_manager.get_max_range_valuable_dmg_spell()
        while (
            near_mov_ldv_enemy := self.ldv_grid.get_near_movable_for_ldv_enemy(
                max_range_dmg_spell
            )
        ) is None:
            # did not found ldv for enemy
            pm_buff_spell = self.spell_manager.get_spell_lvl_for_boost(
                CharacteristicEnum.PM
            )
            if (
                not pm_buff_spell
                or self.spell_manager._pa < pm_buff_spell.ap_cost
                or (
                    self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight)
                    is None
                )
            ):
                self.logger.info("Did not found PM Spell")
                return img, None
            self.logger.info("Launch PM Spell")
            img = self.spell_sys.launch_spell_at_self(pm_buff_spell)

        accessible_cell, enemy_cell = near_mov_ldv_enemy
        self.logger.info(
            f"Found ldv : cell : {accessible_cell}, enemy_cell: {enemy_cell}"
        )

        if accessible_cell in self.grid.movable_cells:
            # if accessible cell is not character cell, move
            img, is_accessible = self.move_to_cell(accessible_cell, img)
            if not is_accessible:
                self.logger.info(f"Cell at {accessible_cell} is inaccessible")
                return img, None

        return img, enemy_cell

    def move_to_cell(
        self, cell: CellSchema, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, bool]:
        """Move character to cell

        Args:
            cell (Cell): target cell
            img (numpy.ndarray)

        Returns:
            tuple[numpy.ndarray, bool]: new img, sucessfully moved
        """
        while True:
            self.logger.info(f"Moving to {cell}")
            if cell not in self.grid.movable_cells:
                return img, False

            old_curr_cell = self.grid.character_cell
            self.controller.click(cell.center_pos)
            sleep(0.3)
            self.controller.void_click()
            img = self.animation_manager.wait_animation_end(
                img,
                CONTENT_REGION,
                retry_time_args=RetryTimeArgs(
                    timeout=5, wait_end=(0.1, 0.2), repeat_time=0.3
                ),
            )
            self.grid.parse_grid(img, cell)
            self.logger.info(
                f"New character cell after moving : {self.grid.character_cell}"
            )
            if old_curr_cell == self.grid.character_cell:
                # cell is the same, fail to move
                return img, False

            if self.grid.character_cell == cell:
                # successful
                return img, True

            # character cell changed but still not at target, continue
