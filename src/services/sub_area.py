import requests
from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.sub_area import SubAreaSchema

from src.consts import BACKEND_URL

SUBAREA_URL = BACKEND_URL + "/sub_area/"


class SubAreaService:
    @staticmethod
    def get_random_grouped_sub_area(
        sub_area_ids_farming: list[int],
        weight_by_map: dict[int, float],
        valid_sub_area_ids: list[int],
        is_sub: bool,
    ) -> list[SubAreaSchema]:
        resp = requests.get(
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
        server_id: int,
        sub_area_ids: list[int],
        lvl: int,
    ) -> dict[int, float]:
        resp = requests.get(
            f"{SUBAREA_URL}weights_fight_map",
            params={"server_id": server_id, "lvl": lvl},
            json=sub_area_ids,
        )
        return {int(key): value for key, value in resp.json().items()}

    @staticmethod
    def get_max_time_fighter(
        sub_area_ids: list[int],
    ) -> int:
        resp = requests.get(
            f"{SUBAREA_URL}max_time_fighter",
            json=sub_area_ids,
        )
        return int(resp.json())

    @staticmethod
    def get_valid_sub_areas_fighter(
        character_id: str,
    ) -> list[SubAreaSchema]:
        resp = requests.get(
            f"{SUBAREA_URL}valid_sub_areas_fighter/",
            params={"character_id": character_id},
        )
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_weights_harvest_map(
        server_id: int,
        possible_collectable_ids: list[int],
        valid_sub_area_ids: list[int],
    ) -> dict[int, float]:
        resp = requests.get(
            f"{SUBAREA_URL}weights_harvest_map",
            params={"server_id": server_id},
            json={
                "possible_collectable_ids": possible_collectable_ids,
                "valid_sub_area_ids": valid_sub_area_ids,
            },
        )
        return {int(key): value for key, value in resp.json().items()}

    @staticmethod
    def get_max_time_harvester(
        sub_area_ids: list[int],
    ) -> int:
        resp = requests.get(
            f"{SUBAREA_URL}max_time_harvester",
            json=sub_area_ids,
        )
        return int(resp.json())

    @staticmethod
    def get_valid_sub_areas_harvester(
        character_id: str,
    ) -> list[SubAreaSchema]:
        resp = requests.get(
            f"{SUBAREA_URL}valid_sub_areas_harvester/",
            params={"character_id": character_id},
        )
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_dropable_items(
        sub_area_id: int,
    ) -> list[ItemSchema]:
        resp = requests.get(
            f"{SUBAREA_URL}{sub_area_id}/dropable_items",
        )
        return [ItemSchema(**elem) for elem in resp.json()]
