from logging import Logger
import numpy
from EzreD2Shared.shared.enums import CharacteristicEnum

from EzreD2Shared.shared.schemas.cell import CellSchema
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.path_grid import AstarGrid
from src.bots.dofus.fight.ias.base import IaBaseFightSystem
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.fight.spells.spell_system import SpellSystem
from src.bots.dofus.hud.heart import is_full_life
from src.services.session import ServiceSession
from src.services.spell import SpellService
from src.states.character_state import CharacterState


class IaSmartFightSystem:
    def __init__(
        self,
        ia_base_fight_sys: IaBaseFightSystem,
        spell_system: SpellSystem,
        spell_manager: SpellManager,
        astar_grid: AstarGrid,
        grid: Grid,
        logger: Logger,
        service: ServiceSession,
        character_state: CharacterState,
    ) -> None:
        self.ia_base_fight_sys = ia_base_fight_sys
        self.spell_system = spell_system
        self.spell_manager = spell_manager
        self.astar_grid = astar_grid
        self.grid = grid
        self.logger = logger
        self.service = service
        self.character_state = character_state

    def play_turn_smart(self, img: numpy.ndarray) -> bool:
        is_full_hp = is_full_life(img)

        while True:
            img, enemy_cell = self.ia_base_fight_sys.reach_attackable_enemy(img)
            if enemy_cell is None:
                break
            img, in_focus, in_fight = self.hit_enemy_smart(img, is_full_hp, enemy_cell)
            if not in_fight:
                return False
            if in_focus:
                self.logger.info("Still focus on enemy")
                break

        self.logger.info("No more enemy attackable, boost character & reach enemy")

        is_contact_enemy: bool = (
            self.grid.character_cell is not None
            and enemy_cell is not None
            and self.grid.character_cell.get_dist_cell(enemy_cell) <= 1
        )
        self.logger.info(f"Character contact enemy : {is_contact_enemy}")
        spells_lvl = SpellService.get_best_combination(
            self.service,
            None,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.service,
                    self.character_state.character.lvl,
                    self.character_state.character.breed_id,
                )
            ],
            [
                CharacteristicEnum.PA,
                CharacteristicEnum.PM,
                CharacteristicEnum.PO,
                CharacteristicEnum.CHANCE,
            ],
            is_full_hp,
            self.character_state.character,
            self.spell_manager._pa,
            self.spell_manager._spell_used_ids_with_count,
            list(self.spell_manager._current_boosts),
        )

        if not is_contact_enemy:
            spells_lvl.sort(
                key=lambda spell_lvl: SpellService.check_if_boost_for_characteristic(
                    self.service, spell_lvl, CharacteristicEnum.PM
                ),
                reverse=True,
            )
        did_moved: bool = False
        for spell_lvl in spells_lvl:
            if not did_moved and not SpellService.check_if_boost_for_characteristic(
                self.service, spell_lvl, CharacteristicEnum.PM
            ):
                did_moved = True
                near_mov = self.astar_grid.get_near_movable_to_reach_enemy(enemy_cell)
                if near_mov is not None:
                    self.logger.info(f"Find near mov to reach enemy : {near_mov}")
                    img = self.ia_base_fight_sys.move_to_cell(near_mov, img)[0]

            img = self.spell_system.launch_spell_at_self(spell_lvl)

        if not did_moved:
            near_mov = self.astar_grid.get_near_movable_to_reach_enemy(enemy_cell)
            if near_mov is not None:
                self.logger.info(f"Find near mov to reach enemy : {near_mov}")
                img = self.ia_base_fight_sys.move_to_cell(near_mov, img)[0]

        return True

    def hit_enemy_smart(
        self, img: numpy.ndarray, is_full_hp: bool, enemy_cell: CellSchema
    ) -> tuple[numpy.ndarray, bool, bool]:
        """Hit single enemy

        Args:
            img (numpy.ndarray)
        Returns:
            tuple[numpy.ndarray, bool, bool]: the new img, is focus on enemy, is in fight
        """
        if self.grid.character_cell and enemy_cell:
            dist_from_enemy = self.grid.character_cell.get_dist_cell(enemy_cell)
        else:
            dist_from_enemy = None
        spells = SpellService.get_best_combination(
            self.service,
            dist_from_enemy,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.service,
                    self.character_state.character.lvl,
                    self.character_state.character.breed_id,
                )
            ],
            [
                CharacteristicEnum.PA,
                CharacteristicEnum(self.character_state.character.elem),
            ],
            is_full_hp,
            self.character_state.character,
            self.spell_manager._pa,
            self.spell_manager._spell_used_ids_with_count,
            list(self.spell_manager._current_boosts),
        )
        self.logger.info(f"Choosed spells : {spells}")
        for spell in spells:
            if spell.on_enemy:
                img, in_fight = self.spell_system.launch_spell_at_enemy(
                    spell, enemy_cell
                )
                if not in_fight:
                    return img, False, False
                if enemy_cell not in self.grid.enemy_cells:
                    return img, False, True
            else:
                img = self.spell_system.launch_spell_at_self(spell)
        return img, True, True
