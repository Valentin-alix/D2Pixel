import requests
from EzreD2Shared.shared.schemas.price import PriceSchema

from src.consts import BACKEND_URL

PRICE_URL = BACKEND_URL + "/price/"


class PriceService:
    @staticmethod
    def update_or_create_price(
        item_id: int, server_id: int, average: float
    ) -> PriceSchema:
        resp = requests.post(
            f"{PRICE_URL}update_or_create/",
            params={
                "item_id": item_id,
                "server_id": server_id,
                "price_average": average,
            },
        )
        return PriceSchema(**resp.json())
