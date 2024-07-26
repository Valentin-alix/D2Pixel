from cachetools import cached
from cachetools.keys import hashkey


from D2Shared.shared.schemas.stat import StatSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

STAT_URL = BACKEND_URL + "/stat/"


class StatService:
    @staticmethod
    @cached(cache={}, key=lambda _: hashkey())
    def get_stats(service: ServiceSession) -> list[StatSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{STAT_URL}")
            return [StatSchema(**elem) for elem in resp.json()]
