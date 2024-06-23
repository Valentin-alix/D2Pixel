from logging import Logger
import math
import random
from time import perf_counter

import numpy
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.map_direction import MapDirectionSchema
from EzreD2Shared.shared.schemas.sub_area import SubAreaSchema
from EzreD2Shared.shared.utils.debugger import log_caller, timeit


from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.services.map import MapService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService
from src.states.character_state import CharacterState


class SubAreaFarming:
    def __init__(
        self, service: ServiceSession, character_state: CharacterState
    ) -> None:
        self.service = service
        self.character_state = character_state

    @timeit
    def get_random_grouped_sub_area(
        self,
        sub_area_ids_farming: list[int],
        weights_by_map: dict[int, float],
        valid_sub_areas: list[SubAreaSchema],
    ) -> list[SubAreaSchema]:
        return SubAreaService.get_random_grouped_sub_area(
            self.service,
            sub_area_ids_farming,
            weights_by_map,
            [elem.id for elem in valid_sub_areas],
            self.character_state.character.is_sub,
        )


class SubAreaFarmingSystem:
    def __init__(
        self,
        service: ServiceSession,
        core_walker_sys: CoreWalkerSystem,
        character_state: CharacterState,
        logger: Logger,
    ) -> None:
        self.service = service
        self.core_walker_sys = core_walker_sys
        self.logger = logger
        self.character_state = character_state

    @log_caller
    def __get_neighbors_time_sub_area(
        self,
        map: MapSchema,
        sub_areas: list[SubAreaSchema],
        maps_time: dict[MapSchema, float],
    ) -> list[tuple[MapDirectionSchema, float]]:
        neighbors_time: list[tuple[MapDirectionSchema, float]] = [
            (map_direction, maps_time[map_direction.to_map])
            for map_direction in MapService.get_map_neighbors(
                self.service, map.id, self.core_walker_sys.get_curr_direction()
            )
            if map_direction.to_map.sub_area in sub_areas
        ]
        self.logger.info(f"found neighbors in sub_area with time: {neighbors_time}")
        return neighbors_time

    def get_next_direction_sub_area(
        self,
        sub_areas: list[SubAreaSchema],
        maps_time: dict[MapSchema, float],
        weights_by_map: dict[int, float],
    ) -> MapDirectionSchema | None:
        neighbors_with_times = self.__get_neighbors_time_sub_area(
            self.core_walker_sys.get_curr_map_info().map, sub_areas, maps_time
        )
        if len(neighbors_with_times) == 0:
            return None

        return random.choices(
            neighbors_with_times,
            weights=[
                math.pow(perf_counter() - time, 1)
                * weights_by_map.get(map_direction.to_map.id, 1)
                for map_direction, time in neighbors_with_times
                if map_direction.to_map
            ],
        )[0][0]

    def go_inside_grouped_sub_area(
        self, sub_areas: list[SubAreaSchema]
    ) -> numpy.ndarray:
        sub_area_ids = [elem.id for elem in sub_areas]

        if self.core_walker_sys.get_curr_map_info().map.sub_area_id in sub_area_ids:
            return self.core_walker_sys.travel_to_map(
                [self.core_walker_sys.get_curr_map_info().map]
            )

        limit_maps = MapService.get_limit_maps_sub_area(
            self.service, sub_area_ids, self.character_state.character.is_sub
        )
        return self.core_walker_sys.travel_to_map(limit_maps)
