from src.consts import BACKEND_URL
from src.services.client_service import ClientService

LOGIN_URL = BACKEND_URL + "/login/"


class LoginService:
    @staticmethod
    async def is_login(service: ClientService) -> bool:
        resp = await service.session.get(f"{LOGIN_URL}")
        if resp.status_code != 200:
            return False
        return True
