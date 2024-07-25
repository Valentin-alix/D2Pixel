import cv2
import numpy
from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.item import ItemSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

ITEM_URL = BACKEND_URL + "/item/"


class ItemService:
    @staticmethod
    async def get_default_sellable_items(
        service: ClientService, character_id: str, recipe_ids: list[int]
    ) -> list[ItemSchema]:
        resp = await service.session.post(
            f"{ITEM_URL}default_sellable",
            params={"character_id": character_id},
            json=recipe_ids,
        )
        return [ItemSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(cache={}, key=lambda _, item_id: hashkey(item_id))
    async def get_icon_img(
        service: ClientService, item_id: int
    ) -> numpy.ndarray | None:
        resp = await service.session.get(f"{ITEM_URL}{item_id}/image/")
        img = resp.content
        if not img:
            return None
        np_arr = numpy.fromstring(img, numpy.uint8)  # type: ignore
        img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img_np
