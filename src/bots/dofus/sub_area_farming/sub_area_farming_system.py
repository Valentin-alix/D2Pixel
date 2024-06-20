import math
import random
from time import perf_counter

import numpy
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.map_direction import MapDirectionSchema
from EzreD2Shared.shared.schemas.sub_area import SubAreaSchema
from EzreD2Shared.shared.utils.debugger import log_caller, timeit

from src.bots.dofus.dofus_bot import DofusBot
from src.bots.dofus.elements.bank import BankSystem
from src.services.map import MapService
from src.services.sub_area import SubAreaService


class SubAreaFarming(DofusBot):
    @timeit
    def get_random_grouped_sub_area(
        self,
        sub_area_ids_farming: list[int],
        weights_by_map: dict[int, float],
        valid_sub_areas: list[SubAreaSchema],
    ) -> list[SubAreaSchema]:
        return SubAreaService.get_random_grouped_sub_area(
            sub_area_ids_farming,
            weights_by_map,
            [elem.id for elem in valid_sub_areas],
            self.character.is_sub,
        )


class SubAreaFarmingSystem(BankSystem, SubAreaFarming):
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
                map.id, self.get_curr_direction()
            )
            if map_direction.to_map.sub_area in sub_areas
        ]
        self.log_info(f"found neighbors in sub_area with time: {neighbors_time}")
        return neighbors_time

    def get_next_direction_sub_area(
        self,
        sub_areas: list[SubAreaSchema],
        maps_time: dict[MapSchema, float],
        weights_by_map: dict[int, float],
    ) -> MapDirectionSchema | None:
        neighbors_with_times = self.__get_neighbors_time_sub_area(
            self.get_curr_map_info().map, sub_areas, maps_time
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

        if self.get_curr_map_info().map.sub_area_id in sub_area_ids:
            return self.travel_to_map([self.get_curr_map_info().map])

        limit_maps = MapService.get_limit_maps_sub_area(
            sub_area_ids, self.character.is_sub
        )
        return self.travel_to_map(limit_maps)
