from functools import cache
from EzreD2Shared.shared.schemas.server import ServerSchema

from src.consts import BACKEND_URL
from src.services.session import ServiceSession

SERVER_URL = BACKEND_URL + "/server/"


class ServerService(ServiceSession):
    @staticmethod
    @cache
    def get_servers(service: ServiceSession) -> list[ServerSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SERVER_URL}",
            )
            return [ServerSchema(**elem) for elem in resp.json()]
