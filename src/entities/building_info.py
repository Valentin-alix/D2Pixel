from dataclasses import dataclass
from typing import Callable

from src.bots.dofus.walker.entities_map.entity_map import EntityMap


@dataclass
class BuildingInfo(EntityMap):
    go_in: Callable
    go_out: Callable
