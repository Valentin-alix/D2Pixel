from cachetools import cached
from cachetools.keys import hashkey
from pydantic import BaseModel

from D2Shared.shared.schemas.map import CoordinatesMapSchema, MapSchema
from src.services.map import MapService
from src.services.session import ServiceSession


class EntityMap(BaseModel):
    map_info: MapSchema


@cached(cache={}, key=lambda _: hashkey())
def get_phenixs_entity_map(service: ServiceSession) -> list[EntityMap]:
    maps_coordinates: list[CoordinatesMapSchema] = [
        CoordinatesMapSchema(x=2, y=-14, world_id=1),
        CoordinatesMapSchema(x=12, y=12, world_id=1),
        CoordinatesMapSchema(x=-10, y=13, world_id=1),
        CoordinatesMapSchema(x=-10, y=-54, world_id=1),
        CoordinatesMapSchema(x=-16, y=36, world_id=1),
        CoordinatesMapSchema(x=2, y=-1, world_id=2),
    ]
    return [
        EntityMap(map_info=MapService.get_related_map(service, map_coordinates))
        for map_coordinates in maps_coordinates
    ]
