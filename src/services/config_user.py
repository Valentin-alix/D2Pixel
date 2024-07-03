from D2Shared.shared.schemas.config_user import (
    ReadConfigUserSchema,
    UpdateConfigUserSchema,
)
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

CONFIG_URL = BACKEND_URL + "/config_user/"


class ConfigService:
    @staticmethod
    def update_config_user(
        service: ServiceSession,
        config_user_id: int,
        update_config_user: UpdateConfigUserSchema,
    ) -> ReadConfigUserSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CONFIG_URL}{config_user_id}/",
                json=update_config_user.model_dump_json(),
            )
            return ReadConfigUserSchema(**resp.json())
