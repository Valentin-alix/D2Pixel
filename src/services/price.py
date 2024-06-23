from EzreD2Shared.shared.schemas.price import PriceSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

PRICE_URL = BACKEND_URL + "/price/"


class PriceService(ServiceSession):
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
