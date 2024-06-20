from typing import Callable

from src.bots.dofus.walker.entities_map.entity_map import EntityMap


class BuildingInfo(EntityMap):
    go_in: Callable
    go_out: Callable
