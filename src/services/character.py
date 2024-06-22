from EzreD2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from EzreD2Shared.shared.schemas.collectable import CollectableSchema
from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from src.services.session import logged_session
from src.consts import BACKEND_URL

CHARACTER_URL = BACKEND_URL + "/character/"


class CharacterService:
    @staticmethod
    def update_character(character: CharacterSchema) -> CharacterSchema:
        with logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character.id}", json=character.model_dump()
            ).json()
            return CharacterSchema(**resp)

    @staticmethod
    def update_job_info(
        character_id: str, job_id: int, lvl: int
    ) -> CharacterJobInfoSchema:
        with logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character_id}/job_info",
                params={"job_id": job_id, "lvl": lvl},
            ).json()
            return CharacterJobInfoSchema(**resp)

    @staticmethod
    def add_waypoint(
        character_id: str,
        waypoint_id: int,
    ):
        with logged_session() as session:
            session.post(
                f"{CHARACTER_URL}{character_id}/waypoint",
                params={"character_id": character_id, "waypoint_id": waypoint_id},
            )

    @staticmethod
    def get_waypoints(
        character_id: str,
    ) -> list[WaypointSchema]:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/waypoints")
            return [WaypointSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_job_infos(
        character_id: str,
    ) -> list[CharacterJobInfoSchema]:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/job_info")
            return [CharacterJobInfoSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_max_pods(character_id: str) -> int:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/max_pods")
            return int(resp.json())

    @staticmethod
    def add_bank_items(
        character_id: str,
        item_ids: list[int],
    ):
        with logged_session() as session:
            session.post(
                f"{CHARACTER_URL}{character_id}/bank_items",
                json=item_ids,
            )

    @staticmethod
    def remove_bank_items(
        character_id: str,
        item_ids: list[int],
    ):
        with logged_session() as session:
            session.delete(
                f"{CHARACTER_URL}{character_id}/bank_items",
                json=item_ids,
            )

    @staticmethod
    def get_bank_items(
        character_id: str,
    ) -> list[ItemSchema]:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/bank_items")
            return [ItemSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_possible_collectable(
        character_id: str,
    ) -> list[CollectableSchema]:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/possible_collectable")
            return [CollectableSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_or_create_character(character_id: str) -> CharacterSchema:
        with logged_session() as session:
            resp = session.get(f"{CHARACTER_URL}{character_id}/or_create/")
            return CharacterSchema(**resp.json())
