from src.consts import BACKEND_URL
from src.services.session import ServiceSession

LOGIN_URL = BACKEND_URL + "/login/"


class LoginService:
    @staticmethod
    def is_login(service: ServiceSession) -> bool:
        with service.logged_session() as session:
            resp = session.get(f"{LOGIN_URL}")
            if resp.status_code != 200:
                return False
            return True
