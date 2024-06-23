from functools import cache

from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.type_item import TypeItemSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession


TYPE_ITEM_URL = BACKEND_URL + "/type_item/"


class TypeItemService(ServiceSession):
    @staticmethod
    @cache
    def get_type_items(
        service: ServiceSession, category: CategoryEnum | None = None
    ) -> list[TypeItemSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{TYPE_ITEM_URL}", params={"category": category})
            return [TypeItemSchema(**elem) for elem in resp.json()]
