import numpy
from EzreD2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.enums import CharacteristicEnum
from EzreD2Shared.shared.schemas.spell_lvl import CurrentBoostSchema, SpellLevelSchema
from EzreD2Shared.shared.utils.randomizer import wait

from src.bots.dofus.fight.grid.cell import Cell
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.hud.pa import get_pa
from src.common.retry import RetryTimeArgs, retry_time
from src.exceptions import UnknowStateException
from src.services.spell import SpellService


class SpellSystem(SpellManager):
    def on_launched_spell(self, spell_lvl: SpellLevelSchema) -> numpy.ndarray:
        self.void_click()
        self._pa -= spell_lvl.ap_cost
        self._spell_used_ids_with_count[spell_lvl.id] += 1
        wait((0.3, 0.4))
        return self.capture()

    def launch_spell_at_self(self, spell_lvl: SpellLevelSchema) -> numpy.ndarray:
        self.log_info(f"Gonna launch spell : {spell_lvl} for self")
        assert not spell_lvl.on_enemy
        assert (charact_cell := self.character_cell) is not None
        self.click(spell_lvl.get_pos_spell())
        self.click(charact_cell.center_pos)

        if spell_lvl.is_boost:
            # refresh buff
            curr_buff = CurrentBoostSchema(
                spell_level_id=spell_lvl.id,
                expire_turn=self._turn + spell_lvl.duration_boost,
            )
            self._current_boosts.discard(curr_buff)
            self._current_boosts.add(curr_buff)
        if spell_lvl.is_disenchantment:
            self.log_info(f"{spell_lvl} is disenchantment")
            self._current_boosts.clear()

        img = self.on_launched_spell(spell_lvl)
        img = self.wait_animation_end(img, CONTENT_REGION)

        if SpellService.check_if_boost_for_characteristic(
            spell_lvl, CharacteristicEnum.PM
        ):
            self.parse_grid(img)
        if spell_lvl.is_boost:
            self._pa = get_pa(img)

        return img

    def launch_spell_at_enemy(
        self, spell_lvl: SpellLevelSchema, enemy_cell: Cell
    ) -> tuple[numpy.ndarray, bool]:
        self.log_info(f"Gonna launch spell : {spell_lvl} for enemy at {enemy_cell}")
        self.click(spell_lvl.get_pos_spell())
        self.click(enemy_cell.center_pos)
        img = self.on_launched_spell(spell_lvl)
        img = self.wait_end_animation_launch_spell_enemy(img)
        if self.get_position(img, ObjectConfigs.Fight.in_fight) is None:
            return img, False
        self.parse_grid(img, self.character_cell)
        return img, True

    def wait_end_animation_launch_spell_enemy(
        self, img: numpy.ndarray
    ) -> numpy.ndarray:
        self._prev_img = img

        res = retry_time(RetryTimeArgs(repeat_time=0.3, wait_end=(0.1, 0.2)))(
            [
                lambda: self._is_end_animation(CONTENT_REGION),
                lambda: self._not_found_template(ObjectConfigs.Fight.in_fight),
            ]
        )()
        if res is None:
            raise UnknowStateException(self._prev_img, "animation_launch_spell")
        return res
