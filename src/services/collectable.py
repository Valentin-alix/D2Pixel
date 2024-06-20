import requests
from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig

from src.consts import BACKEND_URL

COLLECTABLE_URL = BACKEND_URL + "/collectable/"


class CollectableService:
    @staticmethod
    def get_possible_config_on_map(
        map_id: int,
        possible_collectable_ids: list[int],
    ) -> list[ObjectSearchConfig]:
        resp = requests.get(
            f"{COLLECTABLE_URL}possible_on_map/",
            params={"map_id": map_id},
            json=possible_collectable_ids,
        )
        return [ObjectSearchConfig(**elem) for elem in resp.json()]
