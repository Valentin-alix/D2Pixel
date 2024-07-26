from D2Shared.shared.schemas.stat import LineSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

LINE_URL = BACKEND_URL + "/line/"


class LineService:
    @staticmethod
    def add_spent_quantity(
        service: ServiceSession, line_id: int, spent_quantity: int
    ) -> LineSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{LINE_URL}{line_id}/", params={"spent_quantity": spent_quantity}
            )
            return LineSchema(**resp.json())
