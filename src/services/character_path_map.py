from D2Shared.shared.schemas.character_path_map import (
    CreateUpdateCharacterPathMapSchema,
    ReadCharacterPathMapSchema,
)
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

CHARACTER_PATH_MAP_URL = BACKEND_URL + "/path_map/"


class PathMapService:
    @staticmethod
    def create_path_map(
        service: ServiceSession,
        path_map: CreateUpdateCharacterPathMapSchema,
    ) -> ReadCharacterPathMapSchema:
        with service.logged_session() as session:
            resp = session.post(
                f"{CHARACTER_PATH_MAP_URL}", json=path_map.model_dump()
            ).json()
            return ReadCharacterPathMapSchema(**resp)

    @staticmethod
    def update_character_path_map(
        service: ServiceSession,
        path_map_id: int,
        path_map: CreateUpdateCharacterPathMapSchema,
    ) -> ReadCharacterPathMapSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_PATH_MAP_URL}{path_map_id}", json=path_map.model_dump()
            ).json()
            return ReadCharacterPathMapSchema(**resp)

    @staticmethod
    def delete_character_path_map(service: ServiceSession, path_map_id: int):
        with service.logged_session() as session:
            session.delete(f"{CHARACTER_PATH_MAP_URL}{path_map_id}")
