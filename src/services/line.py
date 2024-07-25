from D2Shared.shared.schemas.stat import LineSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

LINE_URL = BACKEND_URL + "/line/"


class LineService:
    @staticmethod
    async def add_spent_quantity(
        service: ClientService, line_id: int, spent_quantity: int
    ) -> LineSchema:
        resp = await service.session.put(
            f"{LINE_URL}{line_id}/", params={"spent_quantity": spent_quantity}
        )
        return LineSchema(**resp.json())
