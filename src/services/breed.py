from functools import cache

from EzreD2Shared.shared.schemas.breed import BreedSchema

from src.consts import BACKEND_URL
from src.services.session import ServiceSession

BREED_URL = BACKEND_URL + "/breed/"


class BreedService:
    @staticmethod
    @cache
    def get_breeds(service: ServiceSession) -> list[BreedSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{BREED_URL}")
            return [BreedSchema(**elem) for elem in resp.json()]
