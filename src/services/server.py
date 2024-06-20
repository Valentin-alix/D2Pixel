from functools import cache

import requests
from EzreD2Shared.shared.schemas.server import ServerSchema

from src.consts import BACKEND_URL

SERVER_URL = BACKEND_URL + "/server/"


class ServerService:
    @staticmethod
    @cache
    def get_servers() -> list[ServerSchema]:
        resp = requests.get(
            f"{SERVER_URL}",
        )
        return [ServerSchema(**elem) for elem in resp.json()]
