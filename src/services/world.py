from functools import cache

from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

WORLD_URL = BACKEND_URL + "/world/"


class WorldService:
    @staticmethod
    @cache
    def get_waypoints(service: ServiceSession, world_id: int) -> list[WaypointSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{WORLD_URL}{world_id}/waypoints")
            return [WaypointSchema(**elem) for elem in resp.json()]
