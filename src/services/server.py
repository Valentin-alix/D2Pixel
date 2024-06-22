from functools import cache
from EzreD2Shared.shared.schemas.server import ServerSchema
from src.services.session import logged_session
from src.consts import BACKEND_URL

SERVER_URL = BACKEND_URL + "/server/"


class ServerService:
    @staticmethod
    @cache
    def get_servers() -> list[ServerSchema]:
        with logged_session() as session:
            resp = session.get(
                f"{SERVER_URL}",
            )
            return [ServerSchema(**elem) for elem in resp.json()]
