from dataclasses import dataclass

import numpy

from D2Shared.shared.enums import FromDirection
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


class MapState:
    def __init__(self) -> None:
        self.curr_map_info: CurrentMapInfo | None = None
        self.curr_direction: FromDirection | None = None
        self.building: BuildingInfo | None = None
        self.is_first_move: bool = True

    def reset_state(self):
        self.curr_map_info = None
        self.curr_direction = None
        self.building = None
        self.is_first_move = True
