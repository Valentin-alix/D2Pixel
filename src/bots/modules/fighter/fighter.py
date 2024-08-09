import traceback
from dataclasses import dataclass
from logging import Logger
from threading import Lock
from time import perf_counter, sleep
from typing import Iterator

import numpy
import tesserocr

from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.region import RegionSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from D2Shared.shared.schemas.user import ReadUserSchema
from D2Shared.shared.utils.randomizer import (
    multiply_offset,
)
from D2Shared.shared.utils.text_similarity import are_similar_text
from src.bots.dofus.deblocker.deblock_system import DeblockSystem
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.hud.info_bar import is_full_pods
from src.bots.dofus.hud.infobulle import iter_infobulles_contours
from src.bots.dofus.sub_area_farming.sub_area_farming_system import (
    SubAreaFarming,
    SubAreaFarmingSystem,
)
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)
from src.image_manager.masks import get_white_masked
from src.image_manager.ocr import BASE_CONFIG, get_text_from_image
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService
from src.states.character_state import CharacterState
from src.utils.time import convert_time_to_seconds
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


def get_group_lvl(img: numpy.ndarray, region: RegionSchema) -> int | None:
    lvl_line_img = crop_image(img, region)
    lvl_line_img = get_white_masked(lvl_line_img)

    with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
        tes_api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
        tes_api.SetVariable("tessedit_char_whitelist", "Niveau123456789 ")
        lvl_text = get_text_from_image(lvl_line_img).split(" ")

    if are_similar_text(lvl_text[0], "Niveau") and len(lvl_text) >= 1:
        try:
            return int(lvl_text[1])
        except ValueError:
            return None

    return None


MULTIPLIER_LVL = 1.5
OFFSET_LVL = 5

fighter_choose_sub_area_lock = Lock()


@dataclass
class Fighter:
    service: ServiceSession
    character_state: CharacterState
    sub_area_farming: SubAreaFarming
    sub_area_farming_sys: SubAreaFarmingSystem
    core_walker_sys: CoreWalkerSystem
    hud_sys: HudSystem
    fight_sys: FightSystem
    bank_sys: BankSystem
    deblock_sys: DeblockSystem
    controller: Controller
    object_searcher: ObjectSearcher
    capturer: Capturer
    image_manager: ImageManager
    logger: Logger
    fighter_maps_time: dict[int, float]
    fighter_sub_areas_farming_ids: list[int]
    user: ReadUserSchema

    def run(self) -> None:
        limit_time = convert_time_to_seconds(
            self.user.config_user.time_fighter
        ) * multiply_offset(
            (
                1 - self.user.config_user.randomizer_duration_activity,
                1 + self.user.config_user.randomizer_duration_activity,
            )
        )

        initial_time = perf_counter()
        sub_areas_farmed_history: set[SubAreaSchema] = set()

        valid_sub_area_ids = SubAreaService.get_valid_sub_areas_fighter(
            self.service, self.character_state.character.id
        )
        self.weight_by_map_fighter = SubAreaService.get_weights_fight_map(
            self.service,
            self.character_state.character.server_id,
            [elem.id for elem in valid_sub_area_ids],
            self.character_state.character.lvl,
        )

        while perf_counter() - initial_time < limit_time:
            with fighter_choose_sub_area_lock:
                sub_areas = self.sub_area_farming.get_random_grouped_sub_area(
                    self.fighter_sub_areas_farming_ids,
                    self.weight_by_map_fighter,
                    valid_sub_area_ids,
                )
                self.fighter_sub_areas_farming_ids.extend(
                    (elem.id for elem in sub_areas)
                )

            try:
                self.logger.info(f"Gonna farm {sub_areas}")
                self._fight_sub_area(sub_areas)
            except StoppedException:
                raise
            except (UnknowStateException, CharacterIsStuckException):
                self.logger.error(traceback.format_exc())
                self.deblock_sys.deblock_character()
            finally:
                sub_areas_farmed_history.update(sub_areas)
                for sub_area in sub_areas:
                    self.fighter_sub_areas_farming_ids.remove(sub_area.id)

        dropped_item_ids: set[int] = set()
        for sub_area in sub_areas_farmed_history:
            for item in SubAreaService.get_dropable_items(self.service, sub_area.id):
                dropped_item_ids.add(item.id)
        CharacterService.add_bank_items(
            self.service, self.character_state.character.id, list(dropped_item_ids)
        )

    def __get_valid_group_infobul_on_img(
        self, img: numpy.ndarray
    ) -> Iterator[RegionSchema]:
        for infobull_info in iter_infobulles_contours(img):
            _, x, y, width, height = infobull_info
            area = RegionSchema(left=x, right=x + width, top=y, bot=y + height)
            lvl = get_group_lvl(img, area)
            self.logger.info(f"lvl : {lvl}")
            if (
                lvl
                and (lvl / MULTIPLIER_LVL) - OFFSET_LVL
                < self.character_state.character.lvl
            ):
                yield area

    def __get_area_group_enemy(self) -> Iterator[RegionSchema]:
        with self.controller.hold("z"):
            sleep(0.6)
            img = self.capturer.capture()

        yield from self.__get_valid_group_infobul_on_img(img)

    def __attack_enemy_in_group(self, infobul_area: RegionSchema) -> bool:
        center = (infobul_area.left + infobul_area.right) // 2
        with self.controller.hold_focus():
            for y in range(infobul_area.bot + 15, infobul_area.bot + 50, 5):
                curr_pos = Position(x_pos=center, y_pos=y)
                self.controller.move(curr_pos)
                if (
                    next(
                        (
                            self.__get_valid_group_infobul_on_img(
                                self.capturer.capture()
                            )
                        ),
                        None,
                    )
                    is None
                ):
                    continue
                self.controller.click(curr_pos)
                return True
        return False

    def _attack_enemy(self, retry: int = 3) -> bool:
        if retry == 0:
            return False
        for area_group in self.__get_area_group_enemy():
            self.logger.info(area_group)
            attacked = self.__attack_enemy_in_group(area_group)
            if attacked:
                break
        else:
            return False

        in_fight_info = self.image_manager.wait_on_screen(ObjectConfigs.Fight.in_fight)
        if in_fight_info is None:
            return self._attack_enemy(retry - 1)

        return True

    def _attack_map(self, sub_areas: list[SubAreaSchema]) -> bool:
        while True:
            in_fight = self._attack_enemy()
            if not in_fight:
                return False
            img, was_teleported = self.fight_sys.play_fight()
            if is_full_pods(img):
                new_img = self.bank_sys.bank_clear_inventory()
                self.hud_sys.close_modals(
                    new_img,
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)
                return True
            elif was_teleported:
                self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)
                return True

    def _fight_sub_area(self, sub_areas: list[SubAreaSchema]):
        max_time = SubAreaService.get_max_time_fighter(
            self.service, [elem.id for elem in sub_areas]
        )

        self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)

        initial_time: float = perf_counter()
        self.fighter_maps_time[self.core_walker_sys.get_curr_map_info().map.id] = (
            perf_counter()
        )

        is_new_map: bool = True

        while perf_counter() - initial_time < max_time:
            if is_new_map:
                did_moved = self._attack_map(sub_areas)
                if did_moved:
                    continue

            map_direction = self.sub_area_farming_sys.get_next_direction_sub_area(
                sub_areas, self.fighter_maps_time, self.weight_by_map_fighter
            )
            if map_direction is None:
                self.logger.info("Did not found neighbor in sub_area")
                if (
                    self.core_walker_sys.get_curr_map_info().map.sub_area
                    not in sub_areas
                ):
                    self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)
                    continue
                raise CharacterIsStuckException

            new_img, was_teleported = self.core_walker_sys.go_to_neighbor(
                map_direction, do_trust=True, use_shift=False
            )
            if was_teleported:
                new_img = self.sub_area_farming_sys.go_inside_grouped_sub_area(
                    sub_areas
                )

            if new_img is None:
                is_new_map = False
                continue

            self.fighter_maps_time[map_direction.to_map_id] = perf_counter()
            is_new_map = True
