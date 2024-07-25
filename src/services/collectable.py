from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

COLLECTABLE_URL = BACKEND_URL + "/collectable/"


class CollectableService:
    @staticmethod
    @cached(
        cache={},
        key=lambda _, map_id, possible_collectable_ids: hashkey(
            map_id, tuple(possible_collectable_ids)
        ),
    )
    async def get_possible_config_on_map(
        service: ClientService,
        map_id: int,
        possible_collectable_ids: list[int],
    ) -> list[ObjectSearchConfig]:
        resp = await service.session.post(
            f"{COLLECTABLE_URL}possible_on_map/",
            params={"map_id": map_id},
            json=possible_collectable_ids,
        )
        return [ObjectSearchConfig(**elem) for elem in resp.json()]
