from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

SUBAREA_URL = BACKEND_URL + "/sub_area/"


class SubAreaService:
    @staticmethod
    async def get_random_grouped_sub_area(
        service: ClientService,
        sub_area_ids_farming: list[int],
        weight_by_map: dict[int, float],
        valid_sub_area_ids: list[int],
    ) -> list[SubAreaSchema]:
        resp = await service.session.post(
            f"{SUBAREA_URL}random_grouped_sub_area/",
            json={
                "sub_area_ids_farming": sub_area_ids_farming,
                "weight_by_map": weight_by_map,
                "valid_sub_area_ids": valid_sub_area_ids,
            },
        )
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def get_weights_fight_map(
        service: ClientService,
        server_id: int,
        sub_area_ids: list[int],
        lvl: int,
    ) -> dict[int, float]:
        resp = await service.session.post(
            f"{SUBAREA_URL}weights_fight_map",
            params={"server_id": server_id, "lvl": lvl},
            json=sub_area_ids,
        )
        return {int(key): value for key, value in resp.json().items()}

    @staticmethod
    @cached(cache={}, key=lambda _, sub_area_ids: hashkey(tuple(sub_area_ids)))
    async def get_max_time_fighter(
        service: ClientService,
        sub_area_ids: list[int],
    ) -> int:
        resp = await service.session.post(
            f"{SUBAREA_URL}max_time_fighter",
            json=sub_area_ids,
        )
        return int(resp.json())

    @staticmethod
    async def get_valid_sub_areas_fighter(
        service: ClientService,
        character_id: str,
    ) -> list[SubAreaSchema]:
        resp = await service.session.get(
            f"{SUBAREA_URL}valid_sub_areas_fighter/",
            params={"character_id": character_id},
        )
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def get_weights_harvest_map(
        service: ClientService,
        character_id: str,
        server_id: int,
        possible_collectable_ids: list[int],
        valid_sub_area_ids: list[int],
    ) -> dict[int, float]:
        resp = await service.session.post(
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
    async def get_max_time_harvester(
        service: ClientService,
        sub_area_ids: list[int],
    ) -> int:
        resp = await service.session.post(
            f"{SUBAREA_URL}max_time_harvester",
            json=sub_area_ids,
        )
        return int(resp.json())

    @staticmethod
    @cached(cache={})
    async def get_sub_areas(
        service: ClientService,
    ) -> list[SubAreaSchema]:
        resp = await service.session.get(f"{SUBAREA_URL}")
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def get_valid_sub_areas_harvester(
        service: ClientService,
        character_id: str,
    ) -> list[SubAreaSchema]:
        resp = await service.session.get(
            f"{SUBAREA_URL}valid_sub_areas_harvester/",
            params={"character_id": character_id},
        )
        return [SubAreaSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(cache={}, key=lambda _, sub_area_id: hashkey(sub_area_id))
    async def get_dropable_items(
        service: ClientService,
        sub_area_id: int,
    ) -> list[ItemSchema]:
        resp = await service.session.get(
            f"{SUBAREA_URL}{sub_area_id}/dropable_items",
        )
        return [ItemSchema(**elem) for elem in resp.json()]
