import numpy
from EzreD2Shared.shared.enums import CharacteristicEnum

from src.bots.dofus.fight.grid.cell import Cell
from src.bots.dofus.fight.ias.base import IaBaseFightSystem
from src.bots.dofus.hud.heart import is_full_life
from src.services.spell import SpellService


class IaSmartFightSystem(IaBaseFightSystem):
    def play_turn_smart(self, img: numpy.ndarray) -> bool:
        is_full_hp = is_full_life(img)

        while True:
            img, enemy_cell = self.reach_attackable_enemy(img)
            if enemy_cell is None:
                break
            img, in_focus, in_fight = self.hit_enemy_smart(img, is_full_hp, enemy_cell)
            if not in_fight:
                return False
            if in_focus:
                self.log_info("Still focus on enemy")
                break

        self.log_info("No more enemy attackable, boost character & reach enemy")

        is_contact_enemy: bool = (
            self.character_cell is not None
            and enemy_cell is not None
            and self.character_cell.get_dist_cell(enemy_cell) <= 1
        )
        self.log_info(f"Character contact enemy : {is_contact_enemy}")
        spells_lvl = SpellService.get_best_combination(
            None,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.character.lvl, self.character.breed_id
                )
            ],
            [
                CharacteristicEnum.PA,
                CharacteristicEnum.PM,
                CharacteristicEnum.PO,
                CharacteristicEnum.CHANCE,
            ],
            is_full_hp,
            self.character,
            self._pa,
            self._spell_used_ids_with_count,
            list(self._current_boosts),
        )

        if not is_contact_enemy:
            spells_lvl.sort(
                key=lambda spell_lvl: SpellService.check_if_boost_for_characteristic(
                    spell_lvl, CharacteristicEnum.PM
                ),
                reverse=True,
            )
        did_moved: bool = False
        for spell_lvl in spells_lvl:
            if not did_moved and not SpellService.check_if_boost_for_characteristic(
                spell_lvl, CharacteristicEnum.PM
            ):
                did_moved = True
                near_mov = self.get_near_movable_to_reach_enemy(enemy_cell)
                if near_mov is not None:
                    self.log_info(f"Find near mov to reach enemy : {near_mov}")
                    img = self.move_to_cell(near_mov, img)[0]

            img = self.launch_spell_at_self(spell_lvl)

        if not did_moved:
            near_mov = self.get_near_movable_to_reach_enemy(enemy_cell)
            if near_mov is not None:
                self.log_info(f"Find near mov to reach enemy : {near_mov}")
                img = self.move_to_cell(near_mov, img)[0]

        return True

    def hit_enemy_smart(
        self, img: numpy.ndarray, is_full_hp: bool, enemy_cell: Cell
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
            [CharacteristicEnum.PA, CharacteristicEnum(self.character.elem)],
            is_full_hp,
            self.character,
            self._pa,
            self._spell_used_ids_with_count,
            list(self._current_boosts),
        )
        self.log_info(f"Choosed spells : {spells}")
        for spell in spells:
            if spell.on_enemy:
                img, in_fight = self.launch_spell_at_enemy(spell, enemy_cell)
                if not in_fight:
                    return img, False, False
                if enemy_cell not in self.enemy_cells:
                    return img, False, True
            else:
                img = self.launch_spell_at_self(spell)
        return img, True, True
