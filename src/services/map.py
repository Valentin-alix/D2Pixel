from functools import cache

import requests
from EzreD2Shared.shared.enums import FromDirection
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.map_direction import MapDirectionSchema
from EzreD2Shared.shared.schemas.map_with_action import MapWithActionSchema

from src.consts import BACKEND_URL

MAP_URL = BACKEND_URL + "/map/"


class MapService:
    @staticmethod
    def find_path(
        is_sub: bool,
        use_transport: bool,
        map_id: int,
        from_direction: FromDirection,
        available_waypoints_ids: list[int],
        target_map_ids: list[int],
    ) -> list[MapWithActionSchema] | None:
        resp = requests.get(
            f"{MAP_URL}find_path/",
            params={
                "is_sub": is_sub,
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
    @cache
    def get_map(map_id: int) -> MapSchema:
        resp = requests.get(f"{MAP_URL}{map_id}")
        return MapSchema(**resp.json())

    @staticmethod
    @cache
    def get_related_map(x: int, y: int, world_id: int) -> MapSchema:
        resp = requests.get(
            f"{MAP_URL}related/", params={"x": x, "y": y, "world_id": world_id}
        )
        return MapSchema(**resp.json())

    @staticmethod
    def get_map_from_hud(
        zone_text: str,
        from_map_id: int | None,
        coordinates: list[str],
    ) -> MapSchema | None:
        resp = requests.get(
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
    @cache
    def get_near_map_allow_havre(
        map_id: int,
    ) -> MapSchema:
        resp = requests.get(
            f"{MAP_URL}{map_id}/near_map_allowing_havre/",
        )
        return MapSchema(**resp.json())

    @staticmethod
    def get_map_neighbors(
        map_id: int, from_direction: FromDirection | None = None
    ) -> list[MapDirectionSchema]:
        resp = requests.get(
            f"{MAP_URL}{map_id}/map_direction/",
            params={"from_direction": from_direction.value if from_direction else None},
        )
        return [MapDirectionSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_limit_maps_sub_area(
        sub_area_ids: list[int],
        is_sub: bool,
    ) -> list[MapSchema]:
        resp = requests.get(
            f"{MAP_URL}limit_maps_sub_area/",
            params={"is_sub": is_sub},
            json=sub_area_ids,
        )
        return [MapSchema(**elem) for elem in resp.json()]

    @staticmethod
    def confirm_map_direction(
        map_direction_id: int, to_map_id: int
    ) -> MapDirectionSchema:
        resp = requests.put(
            f"{MAP_URL}map_direction/{map_direction_id}/confirm/",
            params={"to_map_id": to_map_id},
        )
        return MapDirectionSchema(**resp.json())

    @staticmethod
    def delete_map_direction(map_direction_id: int):
        requests.delete(
            f"{MAP_URL}map_direction/{map_direction_id}",
        )
