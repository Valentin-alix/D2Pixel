from D2Shared.shared.schemas.price import PriceSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

PRICE_URL = BACKEND_URL + "/price/"


class PriceService:
    @staticmethod
    async def update_or_create_price(
        service: ClientService, item_id: int, server_id: int, average: float
    ) -> PriceSchema:
        resp = await service.session.post(
            f"{PRICE_URL}update_or_create/",
            params={
                "item_id": item_id,
                "server_id": server_id,
                "price_average": average,
            },
        )
        return PriceSchema(**resp.json())
