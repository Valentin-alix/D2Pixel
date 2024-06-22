from functools import cache

from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from src.consts import BACKEND_URL
from src.services.session import logged_session

WORLD_URL = BACKEND_URL + "/world/"


class WorldService:
    @staticmethod
    @cache
    def get_waypoints(world_id: int) -> list[WaypointSchema]:
        with logged_session() as session:
            resp = session.get(f"{WORLD_URL}{world_id}/waypoints")
            return [WaypointSchema(**elem) for elem in resp.json()]
