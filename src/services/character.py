from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.waypoint import WaypointSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

CHARACTER_URL = BACKEND_URL + "/character/"


class CharacterService:
    @staticmethod
    def update_character(
        service: ServiceSession, character: CharacterSchema
    ) -> CharacterSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character.id}", json=character.model_dump()
            ).json()
            return CharacterSchema(**resp)

    @staticmethod
    def update_job_info(
        service: ServiceSession, character_id: str, job_id: int, lvl: int
    ) -> CharacterJobInfoSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character_id}/job_info",
                params={"job_id": job_id, "lvl": lvl},
            ).json()
            return CharacterJobInfoSchema(**resp)

    @staticmethod
    def add_waypoint(
        service: ServiceSession,
        character_id: str,
        waypoint_id: int,
    ):
        with service.logged_session() as session:
            session.post(
                f"{CHARACTER_URL}{character_id}/waypoint",
                params={"character_id": character_id, "waypoint_id": waypoint_id},
            )

    @staticmethod
    def get_waypoints(
        service: ServiceSession,
        character_id: str,
    ) -> list[WaypointSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/waypoints")
            return [WaypointSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_job_infos(
        service: ServiceSession,
        character_id: str,
    ) -> list[CharacterJobInfoSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/job_info")
            return [CharacterJobInfoSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_max_pods(service: ServiceSession, character_id: str) -> int:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/max_pods")
            return int(resp.json())

    @staticmethod
    def add_bank_items(
        service: ServiceSession,
        character_id: str,
        item_ids: list[int],
    ):
        with service.logged_session() as session:
            session.post(
                f"{CHARACTER_URL}{character_id}/bank_items",
                json=item_ids,
            )

    @staticmethod
    def remove_bank_items(
        service: ServiceSession,
        character_id: str,
        item_ids: list[int],
    ):
        with service.logged_session() as session:
            session.delete(
                f"{CHARACTER_URL}{character_id}/bank_items",
                json=item_ids,
            )

    @staticmethod
    def get_bank_items(
        service: ServiceSession,
        character_id: str,
    ) -> list[ItemSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/bank_items")
            return [ItemSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_possible_collectable(
        service: ServiceSession,
        character_id: str,
    ) -> list[CollectableSchema]:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/possible_collectable")
            return [CollectableSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_or_create_character(
        service: ServiceSession, character_id: str
    ) -> CharacterSchema:
        with service.logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/or_create/")
            return CharacterSchema(**resp.json())
