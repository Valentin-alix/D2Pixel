from time import sleep

import numpy
from EzreD2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from EzreD2Shared.shared.enums import CharacteristicEnum

from src.bots.dofus.fight.grid.cell import Cell
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.bots.dofus.fight.grid.path_grid import AstarGrid
from src.bots.dofus.fight.spells.spell_system import SpellSystem
from src.common.retry import RetryTimeArgs
from src.services.spell import SpellService


class IaBaseFightSystem(SpellSystem, LdvGrid, AstarGrid):
    def reach_attackable_enemy(
        self, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, Cell | None]:
        max_range_dmg_spell = SpellService.get_max_range_valuable_dmg_spell(
            self.character.elem,
            self.character.po_bonus,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.character.lvl, self.character.breed_id
                )
            ],
        )
        while (
            near_mov_ldv_enemy := self.get_near_movable_for_ldv_enemy(
                max_range_dmg_spell
            )
        ) is None:
            # did not found ldv for enemy
            pm_buff_spell = SpellService.get_spell_lvl_for_boost(
                self.character.lvl, self.character.breed_id, CharacteristicEnum.PM
            )
            if not pm_buff_spell:
                self.log_info("Did not found PM Spell")
                return img, None
            self.log_info("Launch PM Spell")
            img = self.launch_spell_at_self(pm_buff_spell)

        accessible_cell, enemy_cell = near_mov_ldv_enemy
        self.log_info(f"Found ldv : cell : {accessible_cell}, enemy_cell: {enemy_cell}")

        if accessible_cell in self.movable_cells:
            # if accessible cell is not character cell, move
            img, is_accessible = self.move_to_cell(accessible_cell, img)
            if not is_accessible:
                self.log_info(f"Cell at {accessible_cell} is inaccessible")
                return img, None

        return img, enemy_cell

    def move_to_cell(
        self, cell: Cell, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, bool]:
        """Move character to cell

        Args:
            cell (Cell): target cell
            img (numpy.ndarray)

        Returns:
            tuple[numpy.ndarray, bool]: new img, sucessfully moved
        """
        while True:
            if cell not in self.movable_cells:
                return img, False

            old_curr_cell = self.character_cell
            self.click(cell.center_pos)
            sleep(0.3)
            self.void_click()
            img = self.wait_animation_end(
                img,
                CONTENT_REGION,
                retry_time_args=RetryTimeArgs(
                    timeout=5, wait_end=(0.1, 0.2), repeat_time=0.3
                ),
            )
            self.parse_grid(img, cell)
            self.log_info(f"New character cell after moving : {self.character_cell}")
            if old_curr_cell == self.character_cell:
                # cell is the same, fail to move
                return img, False

            if self.character_cell == cell:
                # successful
                return img, True

            # character cell changed but still not at target, continue
