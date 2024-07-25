from D2Shared.shared.schemas.user import ReadUserSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

USER_URL = BACKEND_URL + "/users/"


class UserService:
    @staticmethod
    async def get_current_user(service: ClientService) -> ReadUserSchema:
        resp = await service.session.get(f"{USER_URL}me")
        return ReadUserSchema(**resp.json())
