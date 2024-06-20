import traceback
from threading import Lock
from time import perf_counter, sleep
from typing import Iterator

import numpy
import tesserocr
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.region import RegionSchema
from EzreD2Shared.shared.schemas.sub_area import SubAreaSchema
from EzreD2Shared.shared.utils.randomizer import (
    RANGE_DURATION_ACTIVITY,
    multiply_offset,
)
from EzreD2Shared.shared.utils.text_similarity import are_similar_text

from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.bots.dofus.hud.info_bar import is_full_pods
from src.bots.dofus.hud.infobulle import iter_infobulles_contours
from src.bots.dofus.sub_area_farming.sub_area_farming_system import (
    SubAreaFarmingSystem,
)
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)
from src.image_manager.masks import get_white_masked
from src.image_manager.ocr import BASE_CONFIG, get_text_from_image
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService
from src.services.sub_area import SubAreaService


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


MULTIPLIER_LVL = 1.5
OFFSET_LVL = 5

TIME_FIGHTER = 60 * 60 * 1.5

fighter_choose_sub_area_lock = Lock()


class Fighter(SubAreaFarmingSystem, ConnectionSystem):
    def __init__(
        self,
        fighter_maps_time: dict[MapSchema, float],
        fighter_sub_areas_farming_ids: list[int],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fighter_maps_time = fighter_maps_time
        self.fighter_sub_areas_farming_ids = fighter_sub_areas_farming_ids

    def run_fighter(self) -> None:
        limit_time = TIME_FIGHTER * multiply_offset(RANGE_DURATION_ACTIVITY)

        initial_time = perf_counter()
        sub_areas_farmed_history: set[SubAreaSchema] = set()

        valid_sub_area_ids = SubAreaService.get_valid_sub_areas_fighter(
            self.character.id
        )
        self.weight_by_map_fighter = SubAreaService.get_weights_fight_map(
            self.character.server_id,
            [elem.id for elem in valid_sub_area_ids],
            self.character.lvl,
        )

        while perf_counter() - initial_time < limit_time:
            with fighter_choose_sub_area_lock:
                sub_areas = self.get_random_grouped_sub_area(
                    self.fighter_sub_areas_farming_ids,
                    self.weight_by_map_fighter,
                    valid_sub_area_ids,
                )
                self.fighter_sub_areas_farming_ids.extend(
                    (elem.id for elem in sub_areas)
                )

            try:
                self.log_info(f"Gonna farm {sub_areas}")
                self._fight_sub_area(sub_areas)
            except StoppedException:
                raise
            except (UnknowStateException, CharacterIsStuckException):
                self.log_error(traceback.format_exc())
                self.deblock_character()
            finally:
                sub_areas_farmed_history.update(sub_areas)
                for sub_area in sub_areas:
                    self.fighter_sub_areas_farming_ids.remove(sub_area.id)

        dropped_item_ids: set[int] = set()
        for sub_area in sub_areas_farmed_history:
            for item in SubAreaService.get_dropable_items(sub_area.id):
                dropped_item_ids.add(item.id)
        CharacterService.add_bank_items(self.character.id, list(dropped_item_ids))

    def __get_valid_group_infobul_on_img(
        self, img: numpy.ndarray
    ) -> Iterator[RegionSchema]:
        for infobull_info in iter_infobulles_contours(img):
            _, x, y, width, height = infobull_info
            area = RegionSchema(left=x, right=x + width, top=y, bot=y + height)
            lvl = get_group_lvl(img, area)
            self.log_info(f"lvl : {lvl}")
            if lvl and (lvl / MULTIPLIER_LVL) - OFFSET_LVL < self.character.lvl:
                yield area

    def __get_area_group_enemy(self) -> Iterator[RegionSchema]:
        with self.hold("z"):
            sleep(0.3)
            img = self.capture()

        yield from self.__get_valid_group_infobul_on_img(img)

    def __attack_enemy_in_group(self, infobul_area: RegionSchema) -> bool:
        center = (infobul_area.left + infobul_area.right) // 2
        with self.set_focus():
            for y in range(infobul_area.bot + 15, infobul_area.bot + 50, 5):
                curr_pos = Position(x_pos=center, y_pos=y)
                self.move(curr_pos)
                if (
                    next((self.__get_valid_group_infobul_on_img(self.capture())), None)
                    is None
                ):
                    continue
                self.click(curr_pos)
                return True
        return False

    def _attack_enemy(self) -> bool:
        for area_group in self.__get_area_group_enemy():
            attacked = self.__attack_enemy_in_group(area_group)
            if attacked:
                break
        else:
            return False

        in_fight_info = self.wait_on_screen(ObjectConfigs.Fight.in_fight)
        if in_fight_info is None:
            return self._attack_enemy()

        return True

    def _attack_map(self, sub_areas: list[SubAreaSchema]) -> bool:
        while True:
            in_fight = self._attack_enemy()
            if not in_fight:
                return False
            img, was_teleported = self.play_fight()
            if is_full_pods(img):
                new_img = self.bank_clear_inventory()
                self.close_modals(
                    new_img,
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                self.go_inside_grouped_sub_area(sub_areas)
                return True
            elif was_teleported:
                self.go_inside_grouped_sub_area(sub_areas)
                return True

    def _fight_sub_area(self, sub_areas: list[SubAreaSchema]):
        max_time = SubAreaService.get_max_time_fighter([elem.id for elem in sub_areas])

        self.go_inside_grouped_sub_area(sub_areas)

        initial_time: float = perf_counter()
        self.fighter_maps_time[self.get_curr_map_info().map] = perf_counter()

        is_new_map: bool = True

        while perf_counter() - initial_time < max_time:
            if is_new_map:
                did_moved = self._attack_map(sub_areas)
                if did_moved:
                    continue

            map_direction = self.get_next_direction_sub_area(
                sub_areas, self.fighter_maps_time, self.weight_by_map_fighter
            )
            if map_direction is None:
                self.log_info("Did not found neighbor in sub_area")
                if self.get_curr_map_info().map.sub_area not in sub_areas:
                    self.go_inside_grouped_sub_area(sub_areas)
                    continue
                raise CharacterIsStuckException()

            new_img, was_teleported = self.go_to_neighbor(
                map_direction, do_trust=True, use_shift=False
            )
            if was_teleported:
                new_img = self.go_inside_grouped_sub_area(sub_areas)

            if new_img is None:
                is_new_map = False
                continue

            self.fighter_maps_time[map_direction.to_map] = perf_counter()
            is_new_map = True
