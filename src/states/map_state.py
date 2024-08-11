from dataclasses import dataclass, field

import numpy


from D2Shared.shared.enums import Direction
from D2Shared.shared.schemas.map import MapSchema
from src.entities.building_info import BuildingInfo


@dataclass
class CurrentMapInfo:
    map: MapSchema
    img: numpy.ndarray
    zone_text: str

    def __str__(self) -> str:
        return f"Map : {self.map} | Zone text : {self.zone_text}"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class MapState:
    curr_map_info: CurrentMapInfo | None = field(default=None, init=False)
    curr_direction: Direction | None = None
    building: BuildingInfo | None = field(default=None, init=False)
    is_first_move: bool = field(default=True, init=False)

    def reset_state(self):
        self.curr_map_info = None
        self.building = None
        self.is_first_move = True
