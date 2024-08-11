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
        use_transport: bool,
        map_id: int,
        available_waypoints_ids: list[int],
        target_map_ids: list[int],
    ) -> list[MapWithActionSchema] | None:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}find_path/",
                params={"use_transport": use_transport, "map_id": map_id},
                json={
                    "available_waypoints_ids": available_waypoints_ids,
                    "target_map_ids": target_map_ids,
                },
            )
            if resp.json() is None:
                return None
            return [MapWithActionSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_map(service: ServiceSession, map_id: int) -> MapSchema:
        with service.logged_session() as session:
            resp = session.get(f"{MAP_URL}{map_id}")
            return MapSchema(**resp.json())

    @staticmethod
    def update_can_havre_sac(
        service: ServiceSession, can_havre_sac: bool, map_id: int
    ) -> MapSchema:
        with service.logged_session() as session:
            resp = session.patch(
                f"{MAP_URL}{map_id}/can_havre_sac/",
                params={"can_havre_sac": can_havre_sac},
            )
            return MapSchema(**resp.json())

    @staticmethod
    def get_related_map(
        service: ServiceSession, coordinate_map_schema: CoordinatesMapSchema
    ) -> MapSchema:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}related/", json=coordinate_map_schema.model_dump()
            )
            return MapSchema(**resp.json())

    @staticmethod
    def get_map_from_hud(
        service: ServiceSession,
        zone_text: str,
        from_map_id: int | None,
        coordinates: list[str],
    ) -> MapSchema | None:
        with service.logged_session() as session:
            resp = session.get(
                f"{MAP_URL}from_hud/",
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
    def get_map_directions(
        service: ServiceSession, map_id: int
    ) -> list[MapDirectionSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{MAP_URL}{map_id}/map_direction/")
            return [MapDirectionSchema(**elem) for elem in resp.json()]

    @staticmethod
    def update_map_direction(
        service: ServiceSession, map_direction_id: int, to_map_id: int
    ):
        with service.logged_session() as session:
            session.patch(
                f"{MAP_URL}/map_direction/{map_direction_id}",
                params={"to_map_id": to_map_id},
            )

    @staticmethod
    def delete_map_direction(service: ServiceSession, map_direction_id: int):
        with service.logged_session() as session:
            session.delete(f"{MAP_URL}/map_direction/{map_direction_id}")

    @staticmethod
    def get_limit_maps_sub_area(service: ServiceSession, sub_area_ids: list[int]):
        with service.logged_session() as session:
            resp = session.get(f"{MAP_URL}/map_direction/", json=sub_area_ids)
            return [MapSchema(**_elem) for _elem in resp.json()]
