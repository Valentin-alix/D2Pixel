import math
import random
from dataclasses import dataclass
from logging import Logger
from time import perf_counter

import numpy

from D2Shared.shared.schemas.map import MapSchema

from D2Shared.shared.schemas.map_direction import MapDirectionSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.services.map import MapService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService
from src.states.character_state import CharacterState


@dataclass
class SubAreaFarming:
    service: ServiceSession
    character_state: CharacterState

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

    def get_neighbors_time_sub_area(
        self,
        map: MapSchema,
        sub_areas: list[SubAreaSchema],
        maps_time: dict[int, float],
    ) -> list[tuple[MapDirectionSchema, float]]:
        neighbors_time: list[tuple[MapDirectionSchema, float]] = [
            (map_direction, maps_time[map_direction.to_map_id])
            for map_direction in MapService.get_map_directions(self.service, map.id)
            if map_direction.to_map.sub_area in sub_areas
        ]
        self.logger.info(f"Map voisines avec leur temps: {neighbors_time}")
        return neighbors_time

    def get_next_direction_sub_area(
        self,
        sub_areas: list[SubAreaSchema],
        maps_time: dict[int, float],
        weights_by_map: dict[int, float],
    ) -> MapDirectionSchema | None:
        neighbors_with_times = self.get_neighbors_time_sub_area(
            self.core_walker_sys.get_curr_map_info().map, sub_areas, maps_time
        )
        if len(neighbors_with_times) == 0:
            return None

        return random.choices(
            neighbors_with_times,
            weights=[
                math.pow(perf_counter() - time, 1)
                * weights_by_map.get(map_direction.to_map_id, 1)
                for map_direction, time in neighbors_with_times
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

        limit_maps = MapService.get_limit_maps_sub_area(self.service, sub_area_ids)
        return self.core_walker_sys.travel_to_map(limit_maps)
