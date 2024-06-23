from functools import cache

import cv2
import numpy
from EzreD2Shared.shared.schemas.item import ItemSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

ITEM_URL = BACKEND_URL + "/item/"


class ItemService(ServiceSession):

    @staticmethod
    def get_default_sellable_items(
        service: ServiceSession, character_id: str, recipe_ids: list[int]
    ) -> list[ItemSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{ITEM_URL}default_sellable",
                params={"character_id": character_id},
                json=recipe_ids,
            )
            return [ItemSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cache
    def get_icon_img(service: ServiceSession, item_id: int) -> numpy.ndarray | None:
        with service.logged_session() as session:
            resp = session.get(f"{ITEM_URL}{item_id}/image/")
            img = resp.content
            if img is None:
                return None
            np_arr = numpy.fromstring(img, numpy.uint8)  # type: ignore
            img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return img_np
