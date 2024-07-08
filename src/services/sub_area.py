from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

SUBAREA_URL = BACKEND_URL + "/sub_area/"


class SubAreaService:
    @staticmethod
    def get_random_grouped_sub_area(
        service: ServiceSession,
        sub_area_ids_farming: list[int],
        weight_by_map: dict[int, float],
        valid_sub_area_ids: list[int],
        is_sub: bool,
    ) -> list[SubAreaSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}random_grouped_sub_area/",
                params={"is_sub": is_sub},
                json={
                    "sub_area_ids_farming": sub_area_ids_farming,
                    "weight_by_map": weight_by_map,
                    "valid_sub_area_ids": valid_sub_area_ids,
                },
            )
            return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_weights_fight_map(
        service: ServiceSession,
        server_id: int,
        sub_area_ids: list[int],
        lvl: int,
    ) -> dict[int, float]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}weights_fight_map",
                params={"server_id": server_id, "lvl": lvl},
                json=sub_area_ids,
            )
            return {int(key): value for key, value in resp.json().items()}

    @staticmethod
    @cached(cache={}, key=lambda _, sub_area_ids: hashkey(tuple(sub_area_ids)))
    def get_max_time_fighter(
        service: ServiceSession,
        sub_area_ids: list[int],
    ) -> int:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}max_time_fighter",
                json=sub_area_ids,
            )
            return int(resp.json())

    @staticmethod
    def get_valid_sub_areas_fighter(
        service: ServiceSession,
        character_id: str,
    ) -> list[SubAreaSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}valid_sub_areas_fighter/",
                params={"character_id": character_id},
            )
            return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(
        cache={},
        key=lambda _, server_id, possible_collectable_ids, valid_sub_area_ids: hashkey(
            server_id, tuple(possible_collectable_ids), tuple(valid_sub_area_ids)
        ),
    )
    def get_weights_harvest_map(
        service: ServiceSession,
        character_id: str,
        server_id: int,
        possible_collectable_ids: list[int],
        valid_sub_area_ids: list[int],
    ) -> dict[int, float]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}weights_harvest_map",
                params={"server_id": server_id, "character_id": character_id},
                json={
                    "possible_collectable_ids": possible_collectable_ids,
                    "valid_sub_area_ids": valid_sub_area_ids,
                },
            )
            return {int(key): value for key, value in resp.json().items()}

    @staticmethod
    @cached(cache={}, key=lambda _, sub_area_ids: hashkey(tuple(sub_area_ids)))
    def get_max_time_harvester(
        service: ServiceSession,
        sub_area_ids: list[int],
    ) -> int:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}max_time_harvester",
                json=sub_area_ids,
            )
            return int(resp.json())

    @staticmethod
    def get_valid_sub_areas_harvester(
        service: ServiceSession,
        character_id: str,
    ) -> list[SubAreaSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}valid_sub_areas_harvester/",
                params={"character_id": character_id},
            )
            return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(cache={}, key=lambda _, sub_area_id: hashkey(sub_area_id))
    def get_dropable_items(
        service: ServiceSession,
        sub_area_id: int,
    ) -> list[ItemSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SUBAREA_URL}{sub_area_id}/dropable_items",
            )
            return [ItemSchema(**elem) for elem in resp.json()]
