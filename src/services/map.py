from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.enums import FromDirection
from D2Shared.shared.schemas.map import CoordinatesMapSchema, MapSchema
from D2Shared.shared.schemas.map_direction import MapDirectionSchema
from D2Shared.shared.schemas.map_with_action import MapWithActionSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

MAP_URL = BACKEND_URL + "/map/"


class MapService:
    @staticmethod
    async def find_path(
        service: ClientService,
        use_transport: bool,
        map_id: int,
        from_direction: FromDirection,
        available_waypoints_ids: list[int],
        target_map_ids: list[int],
    ) -> list[MapWithActionSchema] | None:
        resp = await service.session.post(
            f"{MAP_URL}find_path/",
            params={
                "use_transport": use_transport,
                "map_id": map_id,
                "from_direction": from_direction.value,
            },
            json={
                "available_waypoints_ids": available_waypoints_ids,
                "target_map_ids": target_map_ids,
            },
        )
        if resp.json() is None:
            return None
        return [MapWithActionSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(cache={}, key=lambda _, map_id: hashkey(map_id))
    async def get_map(service: ClientService, map_id: int) -> MapSchema:
        resp = await service.session.get(f"{MAP_URL}{map_id}")
        return MapSchema(**resp.json())

    @staticmethod
    @cached(
        cache={}, key=lambda _, coordinate_map_schema: hashkey(coordinate_map_schema)
    )
    async def get_related_map(
        service: ClientService, coordinate_map_schema: CoordinatesMapSchema
    ) -> MapSchema:
        resp = await service.session.post(
            f"{MAP_URL}related/", json=coordinate_map_schema.model_dump()
        )
        return MapSchema(**resp.json())

    @staticmethod
    @cached(
        cache={},
        key=lambda _, zone_text, from_map_id, coordinates: hashkey(
            zone_text, from_map_id, tuple(coordinates)
        ),
    )
    async def get_map_from_hud(
        service: ClientService,
        zone_text: str,
        from_map_id: int | None,
        coordinates: list[str],
    ) -> MapSchema | None:
        resp = await service.session.post(
            f"{MAP_URL}from_coordinate/",
            params={
                "zone_text": zone_text,
                "from_map_id": from_map_id,
            },
            json=coordinates,
        )
        if resp.json() is None:
            return None
        return MapSchema(**resp.json())

    @staticmethod
    @cached(cache={}, key=lambda _, map_id: hashkey(map_id))
    async def get_near_map_allow_havre(
        service: ClientService,
        map_id: int,
    ) -> MapSchema:
        resp = await service.session.get(
            f"{MAP_URL}{map_id}/near_map_allowing_havre/",
        )
        return MapSchema(**resp.json())

    @staticmethod
    async def get_map_neighbors(
        service: ClientService,
        map_id: int,
        from_direction: FromDirection | None = None,
    ) -> list[MapDirectionSchema]:
        resp = await service.session.get(
            f"{MAP_URL}{map_id}/map_direction/",
            params={"from_direction": from_direction.value if from_direction else None},
        )
        return [MapDirectionSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(
        cache={},
        key=lambda _, sub_area_ids: hashkey(tuple(sub_area_ids)),
    )
    async def get_limit_maps_sub_area(
        service: ClientService,
        sub_area_ids: list[int],
    ) -> list[MapSchema]:
        resp = await service.session.post(
            f"{MAP_URL}limit_maps_sub_area/",
            json=sub_area_ids,
        )
        return [MapSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def confirm_map_direction(
        service: ClientService, map_direction_id: int, to_map_id: int
    ) -> MapDirectionSchema:
        resp = await service.session.put(
            f"{MAP_URL}map_direction/{map_direction_id}/confirm/",
            params={"to_map_id": to_map_id},
        )
        return MapDirectionSchema(**resp.json())

    @staticmethod
    async def delete_map_direction(service: ClientService, map_direction_id: int):
        await service.session.delete(
            f"{MAP_URL}map_direction/{map_direction_id}",
        )
