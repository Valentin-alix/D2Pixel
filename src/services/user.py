from D2Shared.shared.schemas.user import ReadUserSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

USER_URL = BACKEND_URL + "/users/"


class UserService:
    @staticmethod
    def get_current_user(service: ServiceSession) -> ReadUserSchema:
        with service.logged_session() as session:
            resp = session.get(f"{USER_URL}me")
            return ReadUserSchema(**resp.json())
