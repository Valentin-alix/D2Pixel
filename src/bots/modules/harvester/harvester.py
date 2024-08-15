from enum import Enum, auto
import random
import traceback
from dataclasses import dataclass, field
from logging import Logger
from threading import Lock
from time import perf_counter, sleep

import numpy
import win32con

from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import Direction
from D2Shared.shared.schemas.character_path_info import ReadCharacterPathInfoSchema
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.map import MapSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from D2Shared.shared.schemas.template_found import InfoTemplateFoundPlacementSchema
from D2Shared.shared.schemas.user import ReadUserSchema
from D2Shared.shared.utils.randomizer import (
    multiply_offset,
)
from src.bots.dofus.deblocker.deblock_system import DeblockSystem
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.hud.highlight import remove_highlighted_zone
from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.hud.info_bar import is_full_pods
from src.bots.dofus.hud.info_popup.info_popup import (
    EventInfoPopup,
)
from src.bots.dofus.hud.infobulle import replace_infobulle
from src.bots.dofus.sub_area_farming.sub_area_farming_system import (
    SubAreaFarming,
    SubAreaFarmingSystem,
)
from src.bots.dofus.walker.core_walker_system import (
    GoToNeighborsExtraArgs,
    WaitForNewMapWalking,
)
from src.bots.dofus.walker.directions import (
    get_pos_to_direction,
)
from src.bots.dofus.walker.walker_system import WalkerSystem
from src.bots.modules.harvester.path_positions import (
    find_dumby_optimal_path_positions,
    find_optimal_path_positions,
)
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.character import CharacterService
from src.services.collectable import CollectableService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService
from src.states.character_state import CharacterState
from src.utils.retry import RetryTimeArgs
from src.utils.time import convert_time_to_seconds
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


def clean_image_after_collect(
    prev_img: numpy.ndarray, img: numpy.ndarray, pos: Position | None = None
):
    img = replace_infobulle(prev_img, img, pos)

    return remove_highlighted_zone(prev_img, img, pos)


harvester_choose_sub_area_lock = Lock()


class ActionHarvest(Enum):
    SUB_AREA = auto()
    CUSTOM_PATH = auto()


@dataclass
class Harvester:
    service: ServiceSession
    character_state: CharacterState
    sub_area_farming_sys: SubAreaFarmingSystem
    sub_area_farming: SubAreaFarming
    deblock_sys: DeblockSystem
    walker_sys: WalkerSystem
    hud_sys: HudSystem
    bank_sys: BankSystem
    controller: Controller
    object_searcher: ObjectSearcher
    capturer: Capturer
    image_manager: ImageManager
    logger: Logger
    harvest_sub_areas_farming_ids: list[int]
    harvest_map_time: dict[int, float]
    user: ReadUserSchema
    weight_by_map_harvest: dict[int, float] = field(
        default_factory=lambda: {}, init=False
    )
    possible_colls: list[CollectableSchema] = field(init=False)

    def __post_init__(self):
        self.possible_colls = CharacterService.get_possible_collectable(
            self.service, self.character_state.character.id
        )

    def run(self) -> None:
        if self.character_state.character.lvl < 10:
            self.logger.warning(
                "Character can't use module harvester because he can't access bank"
            )
            return None

        limit_time: float = convert_time_to_seconds(
            self.user.config_user.time_harvester
        ) * multiply_offset((0.6, 1.4))
        initial_time = perf_counter()

        possible_collectable_ids = [_elem.id for _elem in self.possible_colls]
        valid_sub_areas = SubAreaService.get_valid_sub_areas_harvester(
            self.service, self.character_state.character.id
        )
        valid_sub_area_ids = [_elem.id for _elem in valid_sub_areas]
        self.weight_by_map_harvest = SubAreaService.get_weights_harvest_map(
            self.service,
            self.character_state.character.id,
            self.character_state.character.server_id,
            possible_collectable_ids,
            valid_sub_area_ids,
        )

        while perf_counter() - initial_time < limit_time:
            harvest_action = random.choices(
                [ActionHarvest.CUSTOM_PATH, ActionHarvest.SUB_AREA],
                weights=[
                    len(self.character_state.character.paths_infos),
                    len(valid_sub_areas),
                ],
                k=1,
            )[0]
            try:
                if harvest_action == ActionHarvest.SUB_AREA:
                    self.run_action_sub_area(valid_sub_areas)
                else:
                    self.run_action_custom_path(
                        self.character_state.character.paths_infos
                    )
            except StoppedException:
                raise
            except (UnknowStateException, CharacterIsStuckException):
                self.logger.error(traceback.format_exc())
                self.deblock_sys.deblock_character()

        item_ids = [elem.item_id for elem in self.possible_colls]
        CharacterService.add_bank_items(
            self.service, self.character_state.character.id, item_ids
        )

    def run_action_custom_path(self, paths_infos: list[ReadCharacterPathInfoSchema]):
        path_info = random.choice(paths_infos)
        self.collect_path_info(path_info)

    def collect_path_info(self, path_info: ReadCharacterPathInfoSchema):
        collecting_count: int = 0

        ordered_path_maps = sorted(
            path_info.path_maps, key=lambda elem: elem.order_index
        )
        for index, path_map in enumerate(ordered_path_maps):
            if index > 0:
                first_go_to_neighbor_args = GoToNeighborsExtraArgs(
                    use_shift=True,
                    wait_for_new_map_args=self._get_wait_for_new_map_by_coll_count(
                        collecting_count
                    ),
                )
            else:
                first_go_to_neighbor_args = GoToNeighborsExtraArgs()

            img = self.walker_sys.travel_to_map(
                [path_map.map], extra_first_go_neighbors_args=first_go_to_neighbor_args
            )
            collecting_count = self.collect_map(
                img, self.walker_sys.get_curr_map_info().map
            )

        self.walker_sys.change_map(
            GoToNeighborsExtraArgs(
                True, self._get_wait_for_new_map_by_coll_count(collecting_count)
            )
        )

    def run_action_sub_area(self, valid_sub_areas: list[SubAreaSchema]):
        with harvester_choose_sub_area_lock:
            sub_areas = self.sub_area_farming.get_random_grouped_sub_area(
                self.harvest_sub_areas_farming_ids,
                self.weight_by_map_harvest,
                valid_sub_areas,
            )
        self.harvest_sub_areas_farming_ids.extend((elem.id for elem in sub_areas))
        try:
            self.logger.info(f"Harvest : gonna farm {sub_areas}")
            self.collect_sub_areas(sub_areas)
        finally:
            for sub_area in sub_areas:
                self.harvest_sub_areas_farming_ids.remove(sub_area.id)

    def on_info_modal(self, img: numpy.ndarray) -> numpy.ndarray:
        img, events = self.hud_sys.handle_info_modal(img)
        for event in events:
            if event == EventInfoPopup.LVL_UP_JOB:
                self.possible_colls = CharacterService.get_possible_collectable(
                    self.service, self.character_state.character.id
                )
                valid_sub_areas = SubAreaService.get_valid_sub_areas_harvester(
                    self.service, self.character_state.character.id
                )
                valid_sub_area_ids = [_elem.id for _elem in valid_sub_areas]
                self.weight_by_map_harvest = SubAreaService.get_weights_harvest_map(
                    self.service,
                    self.character_state.character.id,
                    self.character_state.character.server_id,
                    [_elem.id for _elem in self.possible_colls],
                    valid_sub_area_ids,
                )
        return img

    def collect_sub_areas(self, sub_areas: list[SubAreaSchema]):
        max_time = SubAreaService.get_max_time_harvester(
            self.service, [elem.id for elem in sub_areas]
        )

        img = self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)

        initial_time: float = perf_counter()
        self.harvest_map_time[self.walker_sys.get_curr_map_info().map.id] = (
            perf_counter()
        )

        is_new_map: bool = True

        while perf_counter() - initial_time < max_time:
            map_direction = self.sub_area_farming_sys.get_next_direction_sub_area(
                sub_areas, self.harvest_map_time, self.weight_by_map_harvest
            )
            if map_direction is None:
                self.logger.info("Did not found neighbor in sub_area")
                if self.walker_sys.get_curr_map_info().map.sub_area not in sub_areas:
                    img = self.sub_area_farming_sys.go_inside_grouped_sub_area(
                        sub_areas
                    )
                    continue
                raise CharacterIsStuckException

            if is_new_map:
                collecting_count = self.collect_map(
                    img,
                    self.walker_sys.get_curr_map_info().map,
                    map_direction.direction,
                )
                wait_args = self._get_wait_for_new_map_by_coll_count(collecting_count)
            else:
                wait_args = WaitForNewMapWalking()

            new_img, was_teleported = self.walker_sys.go_to_neighbor(
                True,
                map_direction,
                extra_args=GoToNeighborsExtraArgs(
                    use_shift=is_new_map, wait_for_new_map_args=wait_args
                ),
            )

            if was_teleported:
                new_img = self.sub_area_farming_sys.go_inside_grouped_sub_area(
                    sub_areas
                )

            if new_img is None:
                is_new_map = False
                continue

            self.harvest_map_time[self.walker_sys.get_curr_map_info().map.id] = (
                perf_counter()
            )
            img = new_img
            is_new_map = True

            if is_full_pods(img):
                img = self.bank_sys.bank_clear_inventory()
                img = self.hud_sys.close_modals(
                    img,
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                img = self.sub_area_farming_sys.go_inside_grouped_sub_area(sub_areas)

        self.logger.info("Zone finished")

    def get_pos_configs(
        self, img: numpy.ndarray, configs: set[ObjectSearchConfig]
    ) -> list[tuple[Position, InfoTemplateFoundPlacementSchema, ObjectSearchConfig]]:
        positions_infos: list[
            tuple[Position, InfoTemplateFoundPlacementSchema, ObjectSearchConfig]
        ] = []
        self.logger.info(f"Searching configs : {configs}")
        for config in configs:
            for pos_info in self.object_searcher.get_multiple_position(
                img, config, self.walker_sys.get_curr_map_info().map.id
            ):
                positions_infos.append((*pos_info, config))
        return positions_infos

    def collect_map(
        self,
        img: numpy.ndarray,
        map: MapSchema,
        next_direction: Direction | None = None,
    ) -> int:
        curr_direction = self.walker_sys.map_state.curr_direction
        start_pos = get_pos_to_direction(curr_direction) if curr_direction else None
        end_pos = get_pos_to_direction(next_direction) if next_direction else None

        collectable_configs = CollectableService.get_possible_config_on_map(
            self.service, map.id, [_elem.id for _elem in self.possible_colls]
        )
        self.logger.info(f"Searching for {collectable_configs}")

        positions_infos = self.get_pos_configs(img, set(collectable_configs))

        if len(positions_infos) == 0:
            return 0

        positions = [pos for pos, _, _ in positions_infos]
        optimal_path = (
            find_dumby_optimal_path_positions(positions, start_pos)
            if (len(positions) + (1 if start_pos else 0) + (1 if end_pos else 0)) > 13
            else find_optimal_path_positions(positions, start_pos, end_pos)[1]
        )
        self.logger.info(f"Collect path : {optimal_path}")

        positions_infos.sort(key=lambda pos_info: optimal_path.index(pos_info[0]))
        collected_count = 0
        with self.controller.hold(win32con.VK_SHIFT):
            for index, (pos, template_found_place, config) in enumerate(
                positions_infos
            ):
                if index != 0:
                    # not first pos, check if pos still valid
                    pos_info = next(
                        (
                            self.object_searcher.iter_position_from_template_info(
                                img, config, [template_found_place]
                            )
                        ),
                        None,
                    )
                    if pos_info is None:
                        continue
                self.controller.click(pos)
                sleep(0.3)
                collected_count += 1
                if len(positions_infos) <= index + 1:
                    # no more pos after
                    continue
                high_img = self.capturer.capture()
                img = clean_image_after_collect(img, high_img, pos)

        return collected_count

    def _get_wait_for_new_map_by_coll_count(
        self, collecting_count: int
    ) -> WaitForNewMapWalking:
        timeout = 15 + collecting_count * 5
        wait_default_args = WaitForNewMapWalking(
            extra_func=self.on_info_modal,
            retry_args=RetryTimeArgs(timeout=timeout),
        )
        return wait_default_args
