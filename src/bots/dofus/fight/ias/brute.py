import numpy

from src.bots.dofus.fight.grid.cell import Cell
from src.bots.dofus.fight.ias.base import IaBaseFightSystem
from src.services.spell import SpellService


class IaBruteFightSystem(IaBaseFightSystem):
    def play_turn_brute(self, img: numpy.ndarray) -> bool:
        while True:
            img, enemy_cell = self.reach_attackable_enemy(img)
            if enemy_cell is None:
                break
            img, in_focus, in_fight = self.hit_enemy_brute(img, enemy_cell)
            if not in_fight:
                return False
            if in_focus:
                self.log_info("Still focus on enemy")
                break

        self.log_info("No more enemy attackable, reach enemy")
        near_mov = self.get_near_movable_to_reach_enemy(enemy_cell)
        if near_mov is not None:
            self.log_info(f"Find near mov to reach enemy : {near_mov}")
            img = self.move_to_cell(near_mov, img)[0]

        return True

    def hit_enemy_brute(
        self, img: numpy.ndarray, enemy_cell: Cell
    ) -> tuple[numpy.ndarray, bool, bool]:
        """Hit single enemy

        Args:
            img (numpy.ndarray)
        Returns:
            tuple[numpy.ndarray, bool, bool]: the new img, is focus on enemy, is in fight
        """
        if self.character_cell and enemy_cell:
            dist_from_enemy = self.character_cell.get_dist_cell(enemy_cell)
        else:
            dist_from_enemy = None

        spells = SpellService.get_best_combination(
            dist_from_enemy,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.character.lvl, self.character.breed_id
                )
            ],
            [],
            False,
            self.character,
            self._pa,
            self._spell_used_ids_with_count,
            list(self._current_boosts),
        )
        self.log_info(f"Choosed spells : {spells}")

        for spell in spells:
            assert spell.on_enemy is True
            img, in_fight = self.launch_spell_at_enemy(spell, enemy_cell)
            if not in_fight:
                return img, False, False
            if enemy_cell not in self.enemy_cells:
                return img, False, True
        return img, True, True
