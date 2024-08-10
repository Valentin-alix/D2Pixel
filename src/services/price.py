from D2Shared.shared.schemas.price import PriceSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

PRICE_URL = BACKEND_URL + "/price/"


class PriceService:
    @staticmethod
    def update_or_create_price(
        service: ServiceSession, item_id: int, server_id: int, average: float
    ) -> PriceSchema:
        with service.logged_session() as session:
            resp = session.post(
                f"{PRICE_URL}update_or_create/",
                params={
                    "item_id": item_id,
                    "server_id": server_id,
                    "price_average": average,
                },
            )
            return PriceSchema(**resp.json())

    @staticmethod
    def get_price_items(
        service: ServiceSession, item_ids: list[int], server_id: int
    ) -> list[PriceSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{PRICE_URL}",
                params={
                    "server_id": server_id,
                },
                json=item_ids,
            )
            return [PriceSchema(**_elem) for _elem in resp.json()]
