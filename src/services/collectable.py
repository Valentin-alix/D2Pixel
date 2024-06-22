from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig
from src.services.session import logged_session
from src.consts import BACKEND_URL

COLLECTABLE_URL = BACKEND_URL + "/collectable/"


class CollectableService:
    @staticmethod
    def get_possible_config_on_map(
        map_id: int,
        possible_collectable_ids: list[int],
    ) -> list[ObjectSearchConfig]:
        with logged_session() as session:
            resp = session.get(
                f"{COLLECTABLE_URL}possible_on_map/",
                params={"map_id": map_id},
                json=possible_collectable_ids,
            )
            return [ObjectSearchConfig(**elem) for elem in resp.json()]
