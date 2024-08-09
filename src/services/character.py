from typing import Sequence
from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.item import SellItemInfo
from D2Shared.shared.schemas.spell import SpellSchema, UpdateSpellSchema
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

CHARACTER_URL = BACKEND_URL + "/character/"


class CharacterService:
    @staticmethod
    def update_character(
        service: ServiceSession, character: UpdateCharacterSchema
    ) -> CharacterSchema:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character.id}", json=character.model_dump()
            ).json()
            return CharacterSchema(**resp)

    @staticmethod
    def update_job_infos(
        service: ServiceSession,
        character_id: str,
        job_infos: list[CharacterJobInfoSchema],
    ):
        with service.logged_session() as session:
            session.put(
                f"{CHARACTER_URL}{character_id}/job_infos",
                json=[elem.model_dump() for elem in job_infos],
            ).json()

    @staticmethod
    def update_waypoints(
        service: ServiceSession,
        character_id: str,
        waypoint_ids: list[int],
    ):
        with service.logged_session() as session:
            session.put(
                f"{CHARACTER_URL}{character_id}/waypoints",
                params={"character_id": character_id},
                json=waypoint_ids,
            )

    @staticmethod
    def update_recipes(
        service: ServiceSession,
        character_id: str,
        recipe_ids: list[int],
    ):
        with service.logged_session() as session:
            session.put(
                f"{CHARACTER_URL}{character_id}/recipes",
                params={"character_id": character_id},
                json=recipe_ids,
            )

    @staticmethod
    def update_sell_items(
        service: ServiceSession,
        character_id: str,
        items_info: Sequence[SellItemInfo],
    ):
        with service.logged_session() as session:
            session.put(
                f"{CHARACTER_URL}{character_id}/sell_items/",
                params={"character_id": character_id},
                json=[_elem.model_dump() for _elem in items_info],
            )

    @staticmethod
    def update_spells(
        service: ServiceSession,
        character_id: str,
        spells: list[UpdateSpellSchema],
    ) -> list[SpellSchema]:
        with service.logged_session() as session:
            resp = session.put(
                f"{CHARACTER_URL}{character_id}/spells/",
                json=[elem.model_dump() for elem in spells],
            )
            return [SpellSchema(**elem) for elem in resp.json()]

    @staticmethod
    def update_sub_areas(
        service: ServiceSession,
        character_id: str,
        sub_area_ids: list[int],
    ):
        with service.logged_session() as session:
            session.put(
                f"{CHARACTER_URL}{character_id}/sub_areas",
                params={"character_id": character_id},
                json=sub_area_ids,
            )

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
