from functools import cache

from EzreD2Shared.shared.schemas.breed import BreedSchema

from src.consts import BACKEND_URL
from src.services.session import logged_session

BREED_URL = BACKEND_URL + "/breed/"


class BreedService:
    @staticmethod
    @cache
    def get_breeds() -> list[BreedSchema]:
        with logged_session() as session:
            resp = session.get(f"{BREED_URL}")
            return [BreedSchema(**elem) for elem in resp.json()]
