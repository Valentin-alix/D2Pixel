from cachetools import cached
from cachetools.keys import hashkey

from EzreD2Shared.shared.schemas.breed import BreedSchema

from src.consts import BACKEND_URL
from src.services.session import ServiceSession

BREED_URL = BACKEND_URL + "/breed/"


class BreedService:
    @staticmethod
    @cached(cache={}, key=lambda _: hashkey())
    def get_breeds(service: ServiceSession) -> list[BreedSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{BREED_URL}")
            return [BreedSchema(**elem) for elem in resp.json()]
