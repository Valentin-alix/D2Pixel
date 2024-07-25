from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.type_item import TypeItemSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

TYPE_ITEM_URL = BACKEND_URL + "/type_item/"


class TypeItemService:
    @staticmethod
    @cached(cache={}, key=lambda _, category: hashkey(category))
    async def get_type_items(
        service: ClientService, category: CategoryEnum | None = None
    ) -> list[TypeItemSchema]:
        resp = await service.session.get(
            f"{TYPE_ITEM_URL}", params={"category": category}
        )
        return [TypeItemSchema(**elem) for elem in resp.json()]
