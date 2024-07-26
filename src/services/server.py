from cachetools import cached
from cachetools.keys import hashkey
from D2Shared.shared.schemas.server import ServerSchema

from src.consts import BACKEND_URL
from src.services.session import ServiceSession

SERVER_URL = BACKEND_URL + "/server/"


class ServerService:
    @staticmethod
    @cached(cache={}, key=lambda _: hashkey())
    def get_servers(service: ServiceSession) -> list[ServerSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SERVER_URL}",
            )
            return [ServerSchema(**elem) for elem in resp.json()]
