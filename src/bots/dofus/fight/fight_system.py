from logging import Logger
from threading import Event
from time import sleep

import numpy

from D2Shared.shared.consts.adaptative.positions import END_TURN_POSITION
from D2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.schemas.region import RegionSchema
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.path_grid import AstarGrid
from src.bots.dofus.fight.ias.brute import IaBruteFightSystem
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.hud.info_bar import get_percentage_info_bar_fight
from src.bots.dofus.hud.pa import get_pa
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.entities_map.entity_map import (
    get_phenixs_entity_map,
)
from src.common.randomizer import wait
from src.common.retry import RetryTimeArgs
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.client_service import ClientService
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


def is_ur_turn(img: numpy.ndarray) -> bool:
    return get_percentage_info_bar_fight(img) > 0


class FightSystem:
    def __init__(
        self,
        ia_brute_sys: IaBruteFightSystem,
        core_walker_system: CoreWalkerSystem,
        animation_manager: AnimationManager,
        hud_sys: HudSystem,
        astar_grid: AstarGrid,
        spell_manager: SpellManager,
        logger: Logger,
        capturer: Capturer,
        object_searcher: ObjectSearcher,
        image_manager: ImageManager,
        controller: Controller,
        grid: Grid,
        is_dead: Event,
        service: ClientService,
        not_in_fight: Event,
    ) -> None:
        self.capturer = capturer
        self.object_searcher = object_searcher
        self.is_dead = is_dead
        self.animation_manager = animation_manager
        self.ia_brute_sys = ia_brute_sys
        self.core_walker_system = core_walker_system
        self.hud_sys = hud_sys
        self.astar_grid = astar_grid
        self.spell_manager = spell_manager
        self.logger = logger
        self.image_manager = image_manager
        self.controller = controller
        self.grid = grid
        self.service = service
        self.not_in_fight = not_in_fight

    def play_fight(self) -> tuple[numpy.ndarray, bool]:
        """Return True if was teleported"""
        self.not_in_fight.clear()
        wait((0.1, 3))

        self.logger.info("Playing fight")

        img = self.init_fight(self.capturer.capture())

        while True:
            if (
                self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight)
                is None
            ):
                break
            if is_ur_turn(img):
                in_fight = self.play_turn(img)
                if not in_fight:
                    break
            sleep(0.5)
            img = self.capturer.capture()

        img, was_teleported = self.handle_post_fight()

        self.not_in_fight.set()

        return img, was_teleported

    def init_fight(self, img: numpy.ndarray) -> numpy.ndarray:
        img = self.animation_manager.wait_animation_end(img, CONTENT_REGION)

        mode_crea_info = self.object_searcher.get_position(
            img, ObjectConfigs.Fight.mode_crea
        )
        if mode_crea_info is not None:
            self.controller.click(mode_crea_info[0])
            self.controller.void_click()
            wait((0.3, 0.5))
            img = self.capturer.capture()

        self.spell_manager.on_start_fight_spells()
        self.grid.init_grid(img)

        if (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.in_prep)
            is not None
        ):
            img = self.handle_fight_preparation(img)

        self.logger.info("Fight initialized")

        return img

    def handle_fight_preparation(self, img: numpy.ndarray) -> numpy.ndarray:
        if (
            pos_info_lock := self.object_searcher.get_position(
                img, ObjectConfigs.Fight.lock
            )
        ) is not None:
            self.controller.click(pos_info_lock[0])

        self.grid.parse_grid_prep(img)

        near_mov_cell = self.astar_grid.get_near_movable_to_reach_enemy()
        assert near_mov_cell is not None

        self.controller.click(near_mov_cell.center_pos)
        self.controller.void_click()
        self.character_cell = near_mov_cell

        pos_chall_info = self.object_searcher.get_position(
            img, ObjectConfigs.Fight.choose_chall
        )
        if pos_chall_info is not None:
            self.controller.click(pos_chall_info[0])

        pos_info_ready = self.image_manager.wait_on_screen(
            ObjectConfigs.Fight.ready,
            RetryTimeArgs(offset_start=0.3, repeat_time=0.2, timeout=3),
        )
        if pos_info_ready is not None:
            self.controller.click(pos_info_ready[0])

        return self.image_manager.wait_not_on_screen(
            ObjectConfigs.Fight.in_prep, force=True
        )

    def revive_character(self) -> numpy.ndarray:
        self.core_walker_system.go_near_entity_map(
            get_phenixs_entity_map(self.service), use_transport=False
        )
        img = self.capturer.capture()
        phenix_pos_info = self.object_searcher.get_position(
            img,
            ObjectConfigs.Fight.phenix,
            self.core_walker_system.get_curr_map_info().map.id,
            force=True,
        )
        self.controller.click(phenix_pos_info[0])
        self.image_manager.wait_on_screen(ObjectConfigs.Fight.ressuscite_text)
        self.is_dead.clear()
        return img

    def handle_post_fight(self) -> tuple[numpy.ndarray, bool]:
        """Return True if was teleported"""
        self.logger.info("Handling post fight")
        pos, template_found, config, img = self.image_manager.wait_multiple_or_template(
            [
                ObjectConfigs.Cross.info_win_fight,
                ObjectConfigs.Cross.info_lose_fight,
                ObjectConfigs.Text.level_up,
            ],
            force=True,
        )
        if config == ObjectConfigs.Text.level_up:
            img = self.hud_sys.handle_level_up(
                img, pos, RegionSchema.model_validate(template_found.region)
            )

        if (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.grave)
            is not None
        ):
            self.is_dead.set()
            self.logger.warning("Character is dead.")
            img = self.on_dead_character(img)
            self.not_in_fight.set()
            return img, True

        if config == ObjectConfigs.Cross.info_lose_fight:
            self.logger.warning("Loosed Fight")
            self.core_walker_system.wait_for_new_map()
            return (
                self.hud_sys.close_modals(
                    img,
                    ordered_configs_to_check=[
                        ObjectConfigs.Cross.info_lose_fight,
                        ObjectConfigs.Cross.popup_info,  # in case energy is low
                    ],
                ),
                True,
            )

        return (
            self.hud_sys.close_modals(
                img,
                ordered_configs_to_check=[
                    ObjectConfigs.Cross.map,
                    ObjectConfigs.Cross.info_win_fight,
                    ObjectConfigs.Cross.popup_info,
                ],
            ),
            False,
        )

    def on_dead_character(self, img: numpy.ndarray) -> numpy.ndarray:
        ok_info = self.object_searcher.get_position(img, ObjectConfigs.Button.yes)
        if ok_info is not None:
            self.controller.click(ok_info[0])
        sleep(0.6)

        img = self.hud_sys.close_modals(
            self.capturer.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.info_lose_fight],
        )
        self.core_walker_system.wait_for_new_map(force=False)

        img = self.revive_character()
        return img

    def play_turn(self, img: numpy.ndarray) -> bool:
        img = self.animation_manager.wait_animation_end(
            self.capturer.capture(),
            CONTENT_REGION,
            retry_time_args=RetryTimeArgs(repeat_time=0.75, wait_end=(0.1, 2)),
        )

        self.spell_manager.on_new_turn_spells()
        self.grid.parse_grid(img)
        self.logger.info(f"Character cell : {self.character_cell}")

        self.spell_manager._pa = get_pa(img)
        self.logger.info(f"Character has {self.spell_manager._pa} pa")

        if self.ia_brute_sys.play_turn(img) is False:
            return False

        if is_ur_turn(img):
            self.controller.click(END_TURN_POSITION)
            self.controller.void_click()
        wait()
        return True
