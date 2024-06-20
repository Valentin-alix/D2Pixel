from functools import cache

import requests
from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.type_item import TypeItemSchema

from src.consts import BACKEND_URL

TYPE_ITEM_URL = BACKEND_URL + "/type_item/"


class TypeItemService:
    @staticmethod
    @cache
    def get_type_items(category: CategoryEnum | None = None) -> list[TypeItemSchema]:
        resp = requests.get(f"{TYPE_ITEM_URL}", params={"category": category})
        return [TypeItemSchema(**elem) for elem in resp.json()]
