from time import sleep

import numpy
from EzreD2Shared.shared.consts.adaptative.positions import END_TURN_POSITION
from EzreD2Shared.shared.consts.adaptative.regions import CONTENT_REGION
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.schemas.region import RegionSchema
from EzreD2Shared.shared.utils.randomizer import wait

from src.bots.dofus.fight.ias.brute import IaBruteFightSystem
from src.bots.dofus.fight.ias.smart import IaSmartFightSystem
from src.bots.dofus.hud.info_bar import get_percentage_info_bar_fight
from src.bots.dofus.hud.pa import get_pa
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.entities_map.entity_map import (
    get_phenixs_entity_map,
)
from src.common.retry import RetryTimeArgs


def is_ur_turn(img: numpy.ndarray) -> bool:
    return get_percentage_info_bar_fight(img) > 0


class FightSystem(IaSmartFightSystem, IaBruteFightSystem, CoreWalkerSystem):
    def play_fight(self) -> tuple[numpy.ndarray, bool]:
        """Return True if was teleported"""
        self.in_fight = True
        wait((0.1, 3))

        self.log_info("Playing fight")

        img = self.init_fight(self.capture())

        while True:
            if self.get_position(img, ObjectConfigs.Fight.in_fight) is None:
                break
            if is_ur_turn(img):
                in_fight = self.play_turn(img)
                if not in_fight:
                    break
            sleep(0.5)
            img = self.capture()

        img, was_teleported = self.handle_post_fight()

        self.in_fight = False

        return img, was_teleported

    def init_fight(self, img: numpy.ndarray) -> numpy.ndarray:
        img = self.wait_animation_end(img, CONTENT_REGION)

        mode_crea_info = self.get_position(img, ObjectConfigs.Fight.mode_crea)
        if mode_crea_info is not None:
            self.click(mode_crea_info[0])
            self.void_click()
            wait((0.3, 0.5))
            img = self.capture()

        self.on_start_fight_spells()
        self.init_grid(img)

        if self.get_position(img, ObjectConfigs.Fight.in_prep) is not None:
            img = self.handle_fight_preparation(img)

        return img

    def handle_fight_preparation(self, img: numpy.ndarray) -> numpy.ndarray:
        if (
            pos_info_lock := self.get_position(img, ObjectConfigs.Fight.lock)
        ) is not None:
            self.click(pos_info_lock[0])

        self.parse_grid_prep(img)

        near_mov_cell = self.get_near_movable_to_reach_enemy()
        assert near_mov_cell is not None

        self.click(near_mov_cell.center_pos)
        self.void_click()
        self.character_cell = near_mov_cell

        pos_chall_info = self.get_position(img, ObjectConfigs.Fight.choose_chall)
        if pos_chall_info is not None:
            self.click(pos_chall_info[0])

        pos_info_ready = self.wait_on_screen(
            ObjectConfigs.Fight.ready,
            RetryTimeArgs(offset_start=0.3, repeat_time=0.2, timeout=3),
        )
        if pos_info_ready is not None:
            self.click(pos_info_ready[0])

        return self.wait_not_on_screen(ObjectConfigs.Fight.in_prep, force=True)

    def revive_character(self) -> numpy.ndarray:
        self.go_near_entity_map(get_phenixs_entity_map(), use_transport=False)
        img = self.capture()
        phenix_pos_info = self.get_position(
            img, ObjectConfigs.Fight.phenix, self.get_curr_map_info().map.id, force=True
        )
        self.click(phenix_pos_info[0])
        self.wait_on_screen(ObjectConfigs.Fight.ressuscite_text)
        self.is_dead = False
        return img

    def handle_post_fight(self) -> tuple[numpy.ndarray, bool]:
        """Return True if was teleported"""
        self.log_info("Handling post fight")
        pos, template_found, config, img = self.wait_multiple_or_template(
            [
                ObjectConfigs.Cross.info_win_fight,
                ObjectConfigs.Cross.info_lose_fight,
                ObjectConfigs.Text.level_up,
            ],
            force=True,
        )
        if config == ObjectConfigs.Text.level_up:
            img = self.handle_level_up(
                img, pos, RegionSchema.model_validate(template_found.region)
            )

        if self.get_position(img, ObjectConfigs.Fight.grave) is not None:
            self.is_dead = True
            self.log_warning("Character is dead.")
            img = self.on_dead_character(img)
            return img, True

        if config == ObjectConfigs.Cross.info_lose_fight:
            self.log_warning("Loosed Fight")
            self.wait_for_new_map()
            return (
                self.close_modals(
                    img,
                    ordered_configs_to_check=[
                        ObjectConfigs.Cross.info_lose_fight,
                        ObjectConfigs.Cross.popup_info,  # in case energy is low
                    ],
                ),
                True,
            )

        return (
            self.close_modals(
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
        ok_info = self.get_position(img, ObjectConfigs.Button.yes)
        if ok_info is not None:
            self.click(ok_info[0])
        sleep(0.6)

        img = self.close_modals(
            self.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.info_lose_fight],
        )
        self.wait_for_new_map(force=False)

        img = self.revive_character()
        return img

    def play_turn(self, img: numpy.ndarray) -> bool:
        img = self.wait_animation_end(
            self.capture(),
            CONTENT_REGION,
            retry_time_args=RetryTimeArgs(repeat_time=0.75, wait_end=(0.1, 2)),
        )

        self.on_new_turn_spells()
        self.parse_grid(img)
        self.log_info(f"Character cell : {self.character_cell}")

        self._pa = get_pa(img)
        self.log_info(f"Character has {self._pa} pa")

        if self.play_turn_brute(img) is False:
            return False

        if is_ur_turn(img):
            self.click(END_TURN_POSITION)
            self.void_click()
        wait()
        return True
