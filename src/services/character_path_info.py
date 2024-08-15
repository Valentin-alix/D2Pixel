from D2Shared.shared.schemas.character_path_info import (
    CreateCharacterPathInfoSchema,
    ReadCharacterPathInfoSchema,
    UpdateCharacterPathInfoSchema,
)
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

CHARACTER_PATH_INFO_URL = BACKEND_URL + "/path_info/"


class PathInfoService:
    @staticmethod
    def create_character_path_info(
        service: ServiceSession,
        path_info: CreateCharacterPathInfoSchema,
    ) -> ReadCharacterPathInfoSchema:
        with service.logged_session() as session:
            resp = session.post(
                f"{CHARACTER_PATH_INFO_URL}", json=path_info.model_dump()
            ).json()
            return ReadCharacterPathInfoSchema(**resp)

    @staticmethod
    def update_character_path_info(
        service: ServiceSession,
        path_info_id: int,
        path_info: UpdateCharacterPathInfoSchema,
    ) -> ReadCharacterPathInfoSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_PATH_INFO_URL}{path_info_id}", json=path_info.model_dump()
            ).json()
            return ReadCharacterPathInfoSchema(**resp)

    @staticmethod
    def delete_character_path_info(service: ServiceSession, path_info_id: int):
        with service.logged_session() as session:
            session.delete(f"{CHARACTER_PATH_INFO_URL}{path_info_id}")
