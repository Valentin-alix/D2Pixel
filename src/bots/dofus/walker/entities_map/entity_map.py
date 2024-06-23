from cachetools import cached
from cachetools.keys import hashkey

from EzreD2Shared.shared.schemas.map import MapSchema
from pydantic import BaseModel

from src.services.map import MapService
from src.services.session import ServiceSession


class EntityMap(BaseModel):
    map_info: MapSchema


@cached(cache={}, key=lambda _: hashkey())
def get_phenixs_entity_map(service: ServiceSession) -> list[EntityMap]:
    map_ids: list[int] = [
        190843392,
        88086283,
        64489222,
        128059398,
        171442689,
        153879809,
    ]

    return [
        EntityMap(map_info=MapService.get_map(service, map_id)) for map_id in map_ids
    ]
