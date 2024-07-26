from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.enums import FromDirection
from D2Shared.shared.schemas.map import CoordinatesMapSchema, MapSchema
from D2Shared.shared.schemas.map_direction import MapDirectionSchema
from D2Shared.shared.schemas.map_with_action import MapWithActionSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

MAP_URL = BACKEND_URL + "/map/"


class MapService:
    @staticmethod
    def find_path(
        service: ServiceSession,
        is_sub: bool,
        use_transport: bool,
        map_id: int,
        from_direction: FromDirection,
        available_waypoints_ids: list[int],
        target_map_ids: list[int],
    ) -> list[MapWithActionSchema] | None:
        with service.logged_session() as session:
            resp = session.get(
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
    @cached(cache={}, key=lambda _, map_id: hashkey(map_id))
    def get_map(service: ServiceSession, map_id: int) -> MapSchema:
        with service.logged_session() as session:
            resp = session.get(f"{MAP_URL}{map_id}")
            return MapSchema(**resp.json())

    @staticmethod
    @cached(
        cache={}, key=lambda _, coordinate_map_schema: hashkey(coordinate_map_schema)
    )
    def get_related_map(
        service: ServiceSession, coordinate_map_schema: CoordinatesMapSchema
    ) -> MapSchema:
        with service.logged_session() as session:
            resp = session.get(
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
    def get_map_from_hud(
        service: ServiceSession,
        zone_text: str,
        from_map_id: int | None,
        coordinates: list[str],
    ) -> MapSchema | None:
        with service.logged_session() as session:
            resp = session.get(
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
    def get_near_map_allow_havre(
        service: ServiceSession,
        map_id: int,
    ) -> MapSchema:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}{map_id}/near_map_allowing_havre/",
            )
            return MapSchema(**resp.json())

    @staticmethod
    def get_map_neighbors(
        service: ServiceSession,
        map_id: int,
        from_direction: FromDirection | None = None,
    ) -> list[MapDirectionSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}{map_id}/map_direction/",
                params={
                    "from_direction": from_direction.value if from_direction else None
                },
            )
            return [MapDirectionSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(
        cache={},
        key=lambda _, sub_area_ids, is_sub: hashkey(tuple(sub_area_ids), is_sub),
    )
    def get_limit_maps_sub_area(
        service: ServiceSession,
        sub_area_ids: list[int],
        is_sub: bool,
    ) -> list[MapSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}limit_maps_sub_area/",
                params={"is_sub": is_sub},
                json=sub_area_ids,
            )
            return [MapSchema(**elem) for elem in resp.json()]

    @staticmethod
    def confirm_map_direction(
        service: ServiceSession, map_direction_id: int, to_map_id: int
    ) -> MapDirectionSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{MAP_URL}map_direction/{map_direction_id}/confirm/",
                params={"to_map_id": to_map_id},
            )
            return MapDirectionSchema(**resp.json())

    @staticmethod
    def delete_map_direction(service: ServiceSession, map_direction_id: int):
        with service.logged_session() as session:
            session.delete(
                f"{MAP_URL}map_direction/{map_direction_id}",
            )
