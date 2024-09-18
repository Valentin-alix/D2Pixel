from D2Shared.shared.schemas.user import CreateUserSchema, ReadUserSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

USER_URL = BACKEND_URL + "/users/"


class UserService:
    @staticmethod
    def get_current_user(service: ServiceSession) -> ReadUserSchema:
        with service.logged_session() as session:
            resp = session.get(f"{USER_URL}me")
            return ReadUserSchema(**resp.json())

    @staticmethod
    def create_user(service: ServiceSession, user: CreateUserSchema) -> ReadUserSchema:
        with service.unlogged_session() as session:
            resp = session.post(f"{USER_URL}", json=user.model_dump())
            return ReadUserSchema(**resp.json())
