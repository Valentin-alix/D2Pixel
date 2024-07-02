from cachetools import cached
from cachetools.keys import hashkey
from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from src.services.session import ServiceSession
from src.consts import BACKEND_URL

COLLECTABLE_URL = BACKEND_URL + "/collectable/"


class CollectableService:
    @staticmethod
    @cached(
        cache={},
        key=lambda _, map_id, possible_collectable_ids: hashkey(
            map_id, tuple(possible_collectable_ids)
        ),
    )
    def get_possible_config_on_map(
        service: ServiceSession,
        map_id: int,
        possible_collectable_ids: list[int],
    ) -> list[ObjectSearchConfig]:
        with service.logged_session() as session:
            resp = session.get(
                f"{COLLECTABLE_URL}possible_on_map/",
                params={"map_id": map_id},
                json=possible_collectable_ids,
            )
            return [ObjectSearchConfig(**elem) for elem in resp.json()]
