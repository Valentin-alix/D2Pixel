from functools import cache

import requests
from EzreD2Shared.shared.schemas.breed import BreedSchema

from src.consts import BACKEND_URL

BREED_URL = BACKEND_URL + "/breed/"


class BreedService:
    @staticmethod
    @cache
    def get_breeds() -> list[BreedSchema]:
        resp = requests.get(f"{BREED_URL}")
        return [BreedSchema(**elem) for elem in resp.json()]
