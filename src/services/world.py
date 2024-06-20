from functools import cache

import requests
from EzreD2Shared.shared.schemas.waypoint import WaypointSchema

from src.consts import BACKEND_URL

WORLD_URL = BACKEND_URL + "/world/"


class WorldService:
    @staticmethod
    @cache
    def get_waypoints(world_id: int) -> list[WaypointSchema]:
        resp = requests.get(f"{WORLD_URL}{world_id}/waypoints")
        return [WaypointSchema(**elem) for elem in resp.json()]
