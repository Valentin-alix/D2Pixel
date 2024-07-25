from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.server import ServerSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

SERVER_URL = BACKEND_URL + "/server/"


class ServerService:
    @staticmethod
    @cached(cache={}, key=lambda _: hashkey())
    async def get_servers(service: ClientService) -> list[ServerSchema]:
        resp = await service.session.get(
            f"{SERVER_URL}",
        )
        return [ServerSchema(**elem) for elem in resp.json()]
