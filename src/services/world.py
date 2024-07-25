from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.waypoint import WaypointSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

WORLD_URL = BACKEND_URL + "/world/"


class WorldService:
    @staticmethod
    @cached(cache={}, key=lambda _, world_id: hashkey(world_id))
    async def get_waypoints(
        service: ClientService, world_id: int
    ) -> list[WaypointSchema]:
        resp = await service.session.get(f"{WORLD_URL}{world_id}/waypoints")
        return [WaypointSchema(**elem) for elem in resp.json()]
