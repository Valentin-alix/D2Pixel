from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.type_item import TypeItemSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession


TYPE_ITEM_URL = BACKEND_URL + "/type_item/"


class TypeItemService:
    @staticmethod
    @cached(cache={}, key=lambda _, category: hashkey(category))
    def get_type_items(
        service: ServiceSession, category: CategoryEnum | None = None
    ) -> list[TypeItemSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{TYPE_ITEM_URL}", params={"category": category})
            return [TypeItemSchema(**elem) for elem in resp.json()]
