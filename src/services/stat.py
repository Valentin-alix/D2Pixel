from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.stat import StatSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

STAT_URL = BACKEND_URL + "/stat/"


class StatService:
    @staticmethod
    @cached(cache={}, key=lambda _: hashkey())
    async def get_stats(service: ClientService) -> list[StatSchema]:
        resp = await service.session.get(f"{STAT_URL}")
        return [StatSchema(**elem) for elem in resp.json()]
