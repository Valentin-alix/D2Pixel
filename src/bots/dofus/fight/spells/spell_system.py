from logging import Logger
from time import sleep

import numpy

from D2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.cell import CellSchema
from D2Shared.shared.schemas.spell import CurrentBoostSchema, SpellSchema
from D2Shared.shared.utils.randomizer import wait
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.hud.info_bar import get_percentage_info_bar_fight
from src.bots.dofus.hud.pa import get_pa
from src.exceptions import UnknowStateException
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.utils.retry import RetryTimeArgs, retry_time
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


class SpellSystem:
    def __init__(
        self,
        service: ServiceSession,
        spell_manager: SpellManager,
        controller: Controller,
        capturer: Capturer,
        object_searcher: ObjectSearcher,
        image_manager: ImageManager,
        animation_manager: AnimationManager,
        grid: Grid,
        logger: Logger,
    ) -> None:
        self.service = service
        self.capturer = capturer
        self.animation_manager = animation_manager
        self.object_searcher = object_searcher
        self.spell_manager = spell_manager
        self.controller = controller
        self.image_manager = image_manager
        self.grid = grid
        self.logger = logger

    def on_launched_spell(self, spell: SpellSchema) -> numpy.ndarray:
        sleep(0.3)
        self.controller.void_click()
        self.spell_manager._pa -= spell.ap_cost
        self.spell_manager._spell_used_ids_with_count[spell.id] += 1
        wait((0.3, 0.4))
        return self.capturer.capture()

    def launch_spell_at_self(self, spell: SpellSchema) -> numpy.ndarray:
        self.logger.info(f"Gonna launch spell : {spell} for self")
        assert not spell.is_for_enemy
        assert (charact_cell := self.grid.character_cell) is not None
        self.controller.click(spell.get_pos_spell())
        self.controller.click(charact_cell.center_pos)

        if spell.boost_char:
            # refresh buff
            curr_buff = CurrentBoostSchema(
                spell_level_id=spell.id,
                expire_turn=self.spell_manager._turn + spell.duration_boost,
            )
            self.spell_manager._current_boosts.discard(curr_buff)
            self.spell_manager._current_boosts.add(curr_buff)
        if spell.is_disenchantment:
            self.logger.info(f"{spell} is disenchantment")
            self.spell_manager._current_boosts.clear()

        img = self.on_launched_spell(spell)
        img = self.animation_manager.wait_animation_end(img, CONTENT_REGION)

        if spell.boost_char == CharacteristicEnum.PM:
            self.grid.parse_grid(img)
        if spell.boost_char:
            self.spell_manager._pa = get_pa(img)

        return img

    def launch_spell_at_enemy(
        self, spell: SpellSchema, enemy_cell: CellSchema
    ) -> tuple[numpy.ndarray, bool]:
        self.logger.info(f"Gonna launch spell : {spell} for enemy at {enemy_cell}")
        self.controller.click(spell.get_pos_spell())
        self.controller.click(enemy_cell.center_pos)
        img = self.on_launched_spell(spell)
        img = self.wait_end_animation_launch_spell_enemy(img)
        if self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight) is None:
            return img, False
        self.grid.parse_grid(img, self.grid.character_cell)
        return img, True

    def wait_end_animation_launch_spell_enemy(
        self, img: numpy.ndarray
    ) -> numpy.ndarray:
        def is_end_animation_launch_spell() -> numpy.ndarray | None:
            _img = self.capturer.capture()
            if (
                self.animation_manager._is_end_animation(CONTENT_REGION, _img)
                is not None
            ):
                return _img
            if (
                self.image_manager._is_not_found_template(
                    ObjectConfigs.Fight.in_fight, img=_img
                )
                is not None
            ):
                return _img
            if get_percentage_info_bar_fight(_img) > 0:
                return _img
            return None

        self.animation_manager._prev_img = img

        res = retry_time(RetryTimeArgs(repeat_time=0.3, wait_end=(0.1, 0.2)))(
            is_end_animation_launch_spell
        )()
        if res is None:
            raise UnknowStateException(
                self.animation_manager._prev_img, "animation_launch_spell"
            )
        return res
